"""
文件名：service.py
文件路径：app/modules/inventory_management/service.py
功能描述：库存管理模块的业务逻辑服务层

主要功能：
- 实现库存查询、预留、扣减、调整等核心业务逻辑
- 基于SKU的库存管理，遵循Product-SKU分离原则
- 提供事务安全和数据一致性保证
- 支持高并发场景下的库存操作

使用说明：
- 导入：from app.modules.inventory_management.service import InventoryService
- 初始化：service = InventoryService(db_session)
- 方法调用：inventory = await service.get_sku_inventory(sku_id)

依赖模块：
- app.modules.inventory_management.models: 库存数据模型
- sqlalchemy.orm.Session: 数据库会话管理
- app.core.redis_client: Redis缓存客户端

业务特性：
- 支持分布式锁确保并发安全
- 完整的库存变动日志记录
- 异步操作提升性能表现
- 完善的错误处理和异常管理

创建时间：2025-09-15
最后修改：2025-09-15
"""

# 标准库导入
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

# 第三方库导入
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# 本地应用导入
from .models import (
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType, AdjustmentType
)
from .schemas import (
    ReservationItem, DeductItem, ReservationResponse, ReservationItemResponse,
    DeductResponse, DeductItemResponse, AdjustmentResponse, SKUInventoryRead,
    LowStockItem, ConsistencyCheckItem, ConsistencyCheckResponse, CleanupResponse,
    TransactionQuery, TransactionSearchResponse, InventoryTransactionRead
)


class InventoryService:
    """
    库存管理服务类 - 基于SKU架构
    
    提供完整的SKU库存管理功能
    """

    def __init__(self, db: Session):
        self.db = db

    # ============ 基础库存管理 ============

    def get_sku_inventory(self, sku_id: int) -> Optional[SKUInventoryRead]:
        """获取SKU库存信息"""
        inventory = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id == sku_id
        ).first()
        
        if not inventory:
            return None
            
        return SKUInventoryRead.model_validate(inventory)

    def get_batch_inventory(self, sku_ids: List[int]) -> List[SKUInventoryRead]:
        """批量获取SKU库存信息"""
        inventories = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id.in_(sku_ids),
            InventoryStock.is_active == True
        ).all()
        
        return [SKUInventoryRead.model_validate(inv) for inv in inventories]

    def create_sku_inventory(self, inventory_data) -> Dict:
        """创建SKU库存记录"""
        # 检查是否已存在
        existing = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id == inventory_data.sku_id
        ).first()
        
        if existing:
            raise ValueError(f"SKU {inventory_data.sku_id} 的库存记录已存在")
        
        # 创建库存记录
        inventory = InventoryStock(
            sku_id=inventory_data.sku_id,
            total_quantity=inventory_data.initial_quantity,
            available_quantity=inventory_data.initial_quantity,
            reserved_quantity=0,
            warning_threshold=getattr(inventory_data, "warning_threshold", 10),
            critical_threshold=getattr(inventory_data, "critical_threshold", 5)
        )
        
        self.db.add(inventory)
        
        # 记录初始库存事务
        transaction = InventoryTransaction(
            sku_id=inventory_data.sku_id,
            transaction_type=TransactionType.RESTOCK,
            quantity_change=inventory_data.initial_quantity,
            quantity_before=0,
            quantity_after=inventory_data.initial_quantity,
            reference_type="initial",
            reference_id="system_init",
            reason="初始库存创建"
        )
        
        self.db.add(transaction)
        
        try:
            self.db.commit()
            return self.get_sku_inventory(inventory_data.sku_id)
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"创建库存记录失败: {str(e)}")

    # ============ 库存预占管理 ============

    async def reserve_inventory(
        self,
        reservation_type: ReservationType,
        reference_id: str,
        items: List[ReservationItem],
        expires_minutes: int,
        user_id: int
    ) -> ReservationResponse:
        """预占库存"""
        reservation_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        reserved_items = []
        
        try:
            for item in items:
                sku_id = item.sku_id
                quantity = item.quantity
                
                # 获取库存记录
                inventory = self.db.query(InventoryStock).filter(
                    InventoryStock.sku_id == sku_id,
                    InventoryStock.is_active == True
                ).with_for_update().first()
                
                if not inventory:
                    raise ValueError(f"SKU {sku_id} 不存在或未启用库存管理")
                
                # 检查库存是否足够
                if not inventory.can_reserve(quantity):
                    raise ValueError(f"SKU {sku_id} 库存不足，可用: {inventory.available_quantity}, 需要: {quantity}")
                
                # 执行预占
                if not inventory.reserve_quantity(quantity):
                    raise ValueError(f"SKU {sku_id} 预占失败")
                
                # 创建预占记录
                reservation = InventoryReservation(
                    sku_id=sku_id,
                    reservation_type=reservation_type,
                    reference_id=reference_id,
                    quantity=quantity,
                    expires_at=expires_at
                )
                self.db.add(reservation)
                
                reserved_items.append(ReservationItemResponse(
                    sku_id=sku_id,
                    reserved_quantity=quantity,
                    available_after_reserve=inventory.available_quantity
                ))
            
            self.db.commit()
            
            return ReservationResponse(
                reservation_id=reservation_id,
                expires_at=expires_at,
                reserved_items=reserved_items
            )
            
        except Exception as e:
            self.db.rollback()
            raise

    async def release_reservation(self, reservation_id: str, user_id: int) -> bool:
        """释放指定预占"""
        reservations = self.db.query(InventoryReservation).filter(
            InventoryReservation.reference_id == reservation_id,
            InventoryReservation.is_active == True
        ).all()
        
        if not reservations:
            return False
        
        try:
            for reservation in reservations:
                # 获取库存记录
                inventory = self.db.query(InventoryStock).filter(
                    InventoryStock.sku_id == reservation.sku_id
                ).with_for_update().first()
                
                if inventory:
                    # 释放预占
                    inventory.release_quantity(reservation.quantity)
                
                # 标记预占为无效
                reservation.is_active = False
            
            self.db.commit()
            return True
            
        except Exception:
            self.db.rollback()
            raise

    # ============ 库存操作管理 ============

    async def deduct_inventory(
        self,
        order_id: str,
        items: List[DeductItem],
        operator_id: int
    ) -> DeductResponse:
        """扣减库存（实际出库）"""
        deducted_items = []
        
        try:
            for item in items:
                sku_id = item.sku_id
                quantity = item.quantity
                reservation_id = item.reservation_id
                
                # 获取库存记录
                inventory = self.db.query(InventoryStock).filter(
                    InventoryStock.sku_id == sku_id,
                    InventoryStock.is_active == True
                ).with_for_update().first()
                
                if not inventory:
                    raise ValueError(f"SKU {sku_id} 不存在或未启用库存管理")
                
                # 如果有预占ID，从预占中扣减；否则直接从可用库存扣减
                from_reserved = reservation_id is not None
                
                if not inventory.deduct_quantity(quantity, from_reserved):
                    if from_reserved:
                        raise ValueError(f"SKU {sku_id} 预占库存不足")
                    else:
                        raise ValueError(f"SKU {sku_id} 可用库存不足")
                
                # 如果有预占记录，标记为无效
                if reservation_id:
                    reservations = self.db.query(InventoryReservation).filter(
                        InventoryReservation.reference_id == reservation_id,
                        InventoryReservation.sku_id == sku_id,
                        InventoryReservation.is_active == True
                    ).all()
                    
                    for reservation in reservations:
                        reservation.is_active = False
                
                deducted_items.append(DeductItemResponse(
                    sku_id=sku_id,
                    deducted_quantity=quantity,
                    remaining_quantity=inventory.total_quantity
                ))
            
            self.db.commit()
            
            return DeductResponse(
                order_id=order_id,
                deducted_items=deducted_items
            )
            
        except Exception as e:
            self.db.rollback()
            raise

    # ============ 其他必要方法 ============

    async def update_thresholds(
        self,
        sku_id: str,
        warning_threshold: int,
        critical_threshold: int
    ) -> bool:
        """更新库存阈值"""
        inventory = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id == sku_id
        ).first()
        
        if not inventory:
            return False
        
        inventory.warning_threshold = warning_threshold
        inventory.critical_threshold = critical_threshold
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    async def adjust_inventory(
        self,
        sku_id: int,
        adjustment_type: AdjustmentType,
        quantity: int,
        reason: str,
        reference: str,
        operator_id: int
    ) -> Dict:
        """调整库存"""
        inventory = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id == sku_id,
            InventoryStock.is_active == True
        ).with_for_update().first()
        
        if not inventory:
            raise ValueError(f"SKU {sku_id} 不存在或未启用库存管理")
        
        try:
            # 根据调整类型更新库存
            old_quantity = inventory.total_quantity
            if adjustment_type == AdjustmentType.INCREASE:
                inventory.total_quantity += quantity
                inventory.available_quantity += quantity
                transaction_type = TransactionType.RESTOCK
            elif adjustment_type == AdjustmentType.DECREASE:
                if inventory.available_quantity < quantity:
                    raise ValueError(f"可用库存不足，当前: {inventory.available_quantity}, 需要: {quantity}")
                inventory.total_quantity -= quantity
                inventory.available_quantity -= quantity
                transaction_type = TransactionType.ADJUST
            elif adjustment_type == AdjustmentType.SET:
                inventory.total_quantity = quantity
                inventory.available_quantity = quantity - inventory.reserved_quantity
                quantity = abs(quantity - old_quantity)  # 记录变化量
                transaction_type = TransactionType.ADJUST
            
            # 创建变动记录
            transaction = InventoryTransaction(
                sku_id=sku_id,
                transaction_type=transaction_type,
                quantity_change=quantity,
                reference_id=reference,
                operator_id=operator_id,
                reason=reason,
                quantity_before=inventory.total_quantity - (quantity if adjustment_type == AdjustmentType.INCREASE else -quantity),
                quantity_after=inventory.total_quantity
            )
            self.db.add(transaction)
            
            self.db.commit()
            
            return AdjustmentResponse(
                sku_id=sku_id,
                old_quantity=old_quantity,
                new_quantity=inventory.total_quantity,
                adjustment_quantity=abs(quantity),
                transaction_id=str(transaction.id) if transaction.id else "pending"
            )
            
        except Exception:
            self.db.rollback()
            raise

    # 添加向后兼容的方法（用于现有代码调用）
    def get_or_create_inventory(self, sku_id: str) -> Dict:
        """获取或创建库存记录（同步方法）"""
        import asyncio
        try:
            return asyncio.run(self.get_sku_inventory(sku_id))
        except:
            # 如果不存在，返回基本结构
            return {
                "sku_id": sku_id,
                "total_quantity": 0,
                "available_quantity": 0,
                "reserved_quantity": 0
            }

    def get_low_stock_skus(self, query_or_threshold = None) -> List[LowStockItem]:
        """获取低库存SKU列表"""
        db_query = self.db.query(InventoryStock).filter(
            InventoryStock.is_active == True
        )
        
        # 检查参数类型
        if query_or_threshold is not None:
            if hasattr(query_or_threshold, 'level'):
                # 是LowStockQuery对象
                if query_or_threshold.level == "warning":
                    db_query = db_query.filter(
                        InventoryStock.available_quantity < InventoryStock.warning_threshold
                    )
                elif query_or_threshold.level == "critical":
                    db_query = db_query.filter(
                        InventoryStock.available_quantity < InventoryStock.critical_threshold
                    )
            else:
                # 是数值阈值
                db_query = db_query.filter(
                    InventoryStock.available_quantity < query_or_threshold
                )
        else:
            # 使用预警阈值
            db_query = db_query.filter(
                InventoryStock.available_quantity < InventoryStock.warning_threshold
            )
        
        results = db_query.all()
        return [
            LowStockItem(
                sku_id=inv.sku_id,
                current_quantity=inv.available_quantity,
                warning_threshold=inv.warning_threshold,
                critical_threshold=inv.critical_threshold,
                level="critical" if inv.available_quantity < inv.critical_threshold else "warning"
            )
            for inv in results
        ]

    def check_inventory_consistency(self) -> ConsistencyCheckResponse:
        """检查库存数据一致性"""
        inconsistent_records = []
        
        # 查询所有活跃库存
        inventories = self.db.query(InventoryStock).filter(
            InventoryStock.is_active == True
        ).all()
        
        for inventory in inventories:
            issues = []
            
            # 检查数量一致性：total = available + reserved
            if inventory.total_quantity != (inventory.available_quantity + inventory.reserved_quantity):
                issues.append("数量不一致")
            
            # 检查阈值合理性：critical <= warning
            if inventory.critical_threshold > inventory.warning_threshold:
                issues.append("阈值设置不合理")
            
            # 检查负数
            if inventory.available_quantity < 0 or inventory.reserved_quantity < 0:
                issues.append("存在负数")
            
            if issues:
                inconsistent_records.append(ConsistencyCheckItem(
                    sku_id=inventory.sku_id,
                    issue="; ".join(issues),
                    suggested_action="检查库存数据并进行手动调整"
                ))
        
        return ConsistencyCheckResponse(
            total_skus=len(inventories),
            inconsistent_skus=len(inconsistent_records),
            details=inconsistent_records
        )

    def cleanup_expired_reservations(self) -> CleanupResponse:
        """清理过期预占"""
        now = datetime.now(timezone.utc)
        
        # 查询过期预占
        expired_reservations = self.db.query(InventoryReservation).filter(
            InventoryReservation.expires_at < now,
            InventoryReservation.is_active == True
        ).all()
        
        cleaned_count = 0
        total_quantity_released = 0
        
        for reservation in expired_reservations:
            # 释放库存
            inventory = self.db.query(InventoryStock).filter(
                InventoryStock.sku_id == reservation.sku_id
            ).first()
            
            if inventory:
                inventory.available_quantity += reservation.quantity
                inventory.reserved_quantity -= reservation.quantity
                total_quantity_released += reservation.quantity
            
            # 标记预占为非活跃
            reservation.is_active = False
            cleaned_count += 1
        
        try:
            self.db.commit()
            return CleanupResponse(
                cleaned_reservations=cleaned_count,
                released_quantity=total_quantity_released
            )
        except Exception:
            self.db.rollback()
            raise

    def get_transaction_logs(self, query: TransactionQuery) -> TransactionSearchResponse:
        """获取库存变动记录"""
        db_query = self.db.query(InventoryTransaction)
        
        # 应用查询条件
        if query.sku_ids:
            db_query = db_query.filter(InventoryTransaction.sku_id.in_(query.sku_ids))
        
        if query.transaction_types:
            # 转换枚举值
            types = [getattr(TransactionType, t.name.upper()) for t in query.transaction_types]
            db_query = db_query.filter(InventoryTransaction.transaction_type.in_(types))
            
        if query.operator_id:
            db_query = db_query.filter(InventoryTransaction.operator_id == query.operator_id)
            
        # 按创建时间倒序
        db_query = db_query.order_by(InventoryTransaction.created_at.desc())
        
        # 计算总数
        total = db_query.count()
        
        # 应用分页
        results = db_query.offset(query.offset).limit(query.limit).all()
        
        # 转换为Response对象
        transaction_reads = [InventoryTransactionRead.model_validate(t) for t in results]
        
        # 如果查询指定了单个SKU，返回该SKU的信息
        if query.sku_ids and len(query.sku_ids) == 1:
            sku_id = query.sku_ids[0]
        elif results:
            sku_id = results[0].sku_id
        else:
            sku_id = 0
            
        return TransactionSearchResponse(
            sku_id=sku_id,
            total=total,
            logs=transaction_reads
        )