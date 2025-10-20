"""
文件名：service.py
文件路径：app/modules/inventory_management/service.py
功能描述：库存管理模块的业务逻辑服务层

架构版本：V2.0 - 四层架构
架构层次：Service Layer (业务逻辑层)
职责范围：
- 实现库存业务逻辑和流程控制（预留、扣减、调整等）
- 协调Repository层完成数据操作
- 处理业务规则验证和权限检查
- 管理业务事务边界

主要功能：
- 实现库存查询、预留、扣减、调整等核心业务逻辑
- 基于SKU的库存管理，遵循Product-SKU分离原则
- 提供事务安全和数据一致性保证
- 支持高并发场景下的库存操作

使用说明：
- 导入：from app.modules.inventory_management.service import InventoryService
- 初始化：service = InventoryService(repository)
- 方法调用：inventory = await service.get_sku_inventory(sku_id)

依赖模块：
- app.modules.inventory_management.repository: 数据访问层
- app.modules.inventory_management.models: 库存数据模型
- app.core.redis_client: Redis缓存客户端

业务特性：
- 支持分布式锁确保并发安全
- 完整的库存变动日志记录
- 异步操作提升性能表现
- 完善的错误处理和异常管理

架构优势：
- Service层专注业务逻辑，不直接操作数据库
- Repository层可Mock，便于单元测试
- 数据访问逻辑集中管理，易于维护

创建时间：2025-09-15
最后修改：2025-10-18
版本：v2.0 (四层架构)
"""

# 标准库导入
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
# 第三方库导入
from sqlalchemy.orm import Session

# 本地应用导入
from .models import (AdjustmentType, InventoryReservation, InventoryStock,
                     InventoryTransaction, ReservationType, TransactionType)
from .repository import InventoryRepository
from .schemas import (AdjustmentResponse, CleanupResponse,
                      ConsistencyCheckItem, ConsistencyCheckResponse,
                      DeductItem, DeductItemResponse, DeductResponse,
                      InventoryTransactionRead, LowStockItem, ReservationItem,
                      ReservationItemResponse, ReservationResponse,
                      SKUInventoryRead, TransactionQuery,
                      TransactionSearchResponse)


class InventoryService:
    """
    库存管理服务类 - 基于SKU架构 (四层架构V2.0)

    提供完整的SKU库存管理业务逻辑
    
    架构说明：
    - 本类位于Service层（业务逻辑层）
    - 通过Repository层访问数据库，不直接使用db.query()
    - 专注于业务规则实现和流程控制
    """

    def __init__(self, db: Session):
        """
        初始化库存服务
        
        Args:
            db: SQLAlchemy数据库会话
        
        说明：
            - 创建Repository实例用于数据访问
            - Service层通过self.repository访问数据
        """
        self.db = db
        self.repository = InventoryRepository(db)

    # ============ 基础库存管理 ============

    def get_sku_inventory(self, sku_id: int) -> Optional[SKUInventoryRead]:
        """
        获取SKU库存信息
        
        Args:
            sku_id: SKU标识符
            
        Returns:
            SKU库存信息，不存在时返回None
        """
        inventory = self.repository.get_inventory_by_sku(sku_id)

        if not inventory:
            return None

        return SKUInventoryRead.model_validate(inventory)

    def get_batch_inventory(self, sku_ids: List[int]) -> List[SKUInventoryRead]:
        """
        批量获取SKU库存信息
        
        Args:
            sku_ids: SKU标识符列表
            
        Returns:
            SKU库存信息列表
        """
        inventories = self.repository.get_inventories_by_sku_ids(sku_ids, is_active=True)

        return [SKUInventoryRead.model_validate(inv) for inv in inventories]

    def create_sku_inventory(self, inventory_data) -> Dict:
        """
        创建SKU库存记录
        
        Args:
            inventory_data: 库存初始化数据
            
        Returns:
            创建的库存信息
            
        Raises:
            ValueError: 库存记录已存在或创建失败
        """
        # 检查是否已存在
        existing = self.repository.get_inventory_by_sku(inventory_data.sku_id)

        if existing:
            raise ValueError(f"SKU {inventory_data.sku_id} 的库存记录已存在")

        # 创建库存记录
        inventory = InventoryStock(
            sku_id=inventory_data.sku_id,
            total_quantity=inventory_data.initial_quantity,
            available_quantity=inventory_data.initial_quantity,
            reserved_quantity=0,
            warning_threshold=getattr(inventory_data, "warning_threshold", 10),
            critical_threshold=getattr(inventory_data, "critical_threshold", 5),
        )
        inventory = self.repository.create_inventory(inventory)

        # 记录初始库存事务
        transaction = InventoryTransaction(
            sku_id=inventory_data.sku_id,
            transaction_type=TransactionType.RESTOCK,
            quantity_change=inventory_data.initial_quantity,
            quantity_before=0,
            quantity_after=inventory_data.initial_quantity,
            reference_type="initial",
            reference_id="system_init",
            reason="初始库存创建",
        )
        self.repository.create_transaction(transaction)

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
        user_id: int,
    ) -> ReservationResponse:
        """
        预占库存
        
        Args:
            reservation_type: 预占类型
            reference_id: 关联业务ID
            items: 预占商品列表
            expires_minutes: 过期时间（分钟）
            user_id: 操作用户ID
            
        Returns:
            预占响应信息
            
        Raises:
            ValueError: 库存不足或预占失败
        """
        reservation_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        reserved_items = []

        try:
            for item in items:
                sku_id = item.sku_id
                quantity = item.quantity

                # 获取库存记录（加锁）
                inventory = self.repository.get_inventory_for_update(sku_id, is_active=True)

                if not inventory:
                    raise ValueError(f"SKU {sku_id} 不存在或未启用库存管理")

                # 检查库存是否足够
                if not inventory.can_reserve(quantity):
                    raise ValueError(
                        f"SKU {sku_id} 库存不足，可用: {inventory.available_quantity}, 需要: {quantity}"
                    )

                # 执行预占
                if not inventory.reserve_quantity(quantity):
                    raise ValueError(f"SKU {sku_id} 预占失败")

                # 创建预占记录
                reservation_obj = InventoryReservation(
                    sku_id=sku_id,
                    reservation_type=reservation_type,
                    reference_id=reference_id,
                    quantity=quantity,
                    expires_at=expires_at,
                )
                reservation = self.repository.create_reservation(reservation_obj)

                reserved_items.append(
                    ReservationItemResponse(
                        sku_id=sku_id,
                        reserved_quantity=quantity,
                        available_after_reserve=inventory.available_quantity,
                    )
                )

            self.db.commit()

            return ReservationResponse(
                reservation_id=reservation_id,
                expires_at=expires_at,
                reserved_items=reserved_items,
            )

        except Exception as e:
            self.db.rollback()
            raise

    async def release_reservation(self, reservation_id: str, user_id: int) -> bool:
        """
        释放指定预占
        
        Args:
            reservation_id: 预占关联业务ID
            user_id: 操作用户ID
            
        Returns:
            释放成功返回True，预占不存在返回False
        """
        reservations = self.repository.get_reservations_by_reference(
            reference_id=reservation_id, 
            active_only=True
        )

        if not reservations:
            return False

        try:
            for reservation in reservations:
                # 获取库存记录（加锁）
                inventory = self.repository.get_inventory_for_update(reservation.sku_id)

                if inventory:
                    # 释放预占
                    inventory.release_quantity(reservation.quantity)

                # 标记预占为无效
                self.repository.invalidate_reservation(reservation.id)

            self.db.commit()
            return True

        except Exception:
            self.db.rollback()
            raise

    async def release_user_reservations(self, user_id: str) -> Dict[str, Any]:
        """
        释放指定用户的所有库存预占
        
        Args:
            user_id: 用户ID（字符串格式）
            
        Returns:
            Dict包含释放的预占数量和总释放数量
            
        业务场景：
        - 用户清空购物车
        - 用户注销登录
        - 批量清理用户预占
        """
        try:
            # 查询用户的所有有效预占
            reservations = self.repository.get_reservations_by_reference(
                reference_id=user_id,
                active_only=True
            )
            
            if not reservations:
                return {
                    "released_reservations": 0,
                    "total_released_quantity": 0,
                    "message": "没有找到有效的预占记录"
                }
            
            released_count = 0
            total_quantity = 0
            
            for reservation in reservations:
                # 获取库存记录
                inventory = self.repository.get_by_sku_id(reservation.sku_id)
                if inventory:
                    # 释放预占数量
                    inventory.release_quantity(reservation.quantity)
                    total_quantity += reservation.quantity
                
                # 标记预占为无效
                self.repository.invalidate_reservation(reservation.id)
                released_count += 1
            
            self.db.commit()
            
            return {
                "released_reservations": released_count,
                "total_released_quantity": total_quantity,
                "message": f"成功释放{released_count}个预占，共{total_quantity}件商品"
            }
            
        except Exception:
            self.db.rollback()
            raise

    # ============ 库存操作管理 ============

    async def deduct_inventory(
        self, order_id: str, items: List[DeductItem], operator_id: int
    ) -> DeductResponse:
        """
        扣减库存（实际出库）
        
        Args:
            order_id: 订单ID
            items: 扣减商品列表
            operator_id: 操作员ID
            
        Returns:
            扣减响应信息
            
        Raises:
            ValueError: 库存不足或扣减失败
        """
        deducted_items = []

        try:
            for item in items:
                sku_id = item.sku_id
                quantity = item.quantity
                reservation_id = item.reservation_id

                # 获取库存记录（加锁）
                inventory = self.repository.get_inventory_for_update(sku_id, is_active=True)

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
                    reservations = self.repository.get_reservations_by_reference(
                        reference_id=reservation_id,
                        sku_id=sku_id,
                        is_active=True
                    )

                    reservation_ids = [r.id for r in reservations]
                    if reservation_ids:
                        self.repository.invalidate_reservations_batch(reservation_ids)

                deducted_items.append(
                    DeductItemResponse(
                        sku_id=sku_id,
                        deducted_quantity=quantity,
                        remaining_quantity=inventory.total_quantity,
                    )
                )

            self.db.commit()

            return DeductResponse(order_id=order_id, deducted_items=deducted_items)

        except Exception as e:
            self.db.rollback()
            raise

    # ============ 其他必要方法 ============

    async def update_thresholds(
        self, sku_id: str, warning_threshold: int, critical_threshold: int
    ) -> bool:
        """
        更新库存阈值
        
        Args:
            sku_id: SKU标识符
            warning_threshold: 预警阈值
            critical_threshold: 紧急阈值
            
        Returns:
            更新成功返回True，SKU不存在返回False
        """
        inventory = self.repository.get_inventory_by_sku(sku_id)

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

    async def update_sku_inventory_config(
        self, sku_id: str, update_data: Any
    ) -> bool:
        """
        更新SKU库存配置
        
        Args:
            sku_id: SKU标识符
            update_data: 更新数据（SKUInventoryUpdate对象）
            
        Returns:
            更新成功返回True，SKU不存在返回False
            
        功能：
        - 更新warning_threshold（预警阈值）
        - 更新critical_threshold（危险阈值）
        - 更新is_active（是否启用库存管理）
        """
        inventory = self.repository.get_inventory_by_sku(sku_id)
        
        if not inventory:
            return False
        
        # 应用更新（只更新提供的字段）
        if hasattr(update_data, 'warning_threshold') and update_data.warning_threshold is not None:
            inventory.warning_threshold = update_data.warning_threshold
        
        if hasattr(update_data, 'critical_threshold') and update_data.critical_threshold is not None:
            inventory.critical_threshold = update_data.critical_threshold
        
        if hasattr(update_data, 'is_active') and update_data.is_active is not None:
            inventory.is_active = update_data.is_active
        
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
        operator_id: int,
    ) -> Dict:
        """
        调整库存
        
        Args:
            sku_id: SKU标识符
            adjustment_type: 调整类型（增加/减少/设置）
            quantity: 调整数量
            reason: 调整原因
            reference: 关联业务引用
            operator_id: 操作员ID
            
        Returns:
            调整响应信息
            
        Raises:
            ValueError: 库存不足或调整失败
        """
        inventory = self.repository.get_inventory_for_update(sku_id, is_active=True)

        if not inventory:
            raise ValueError(f"SKU {sku_id} 不存在或未启用库存管理")

        try:
            # 根据调整类型更新库存
            old_quantity = inventory.total_quantity
            transaction_type = TransactionType.ADJUST  # 默认类型
            
            # 统一使用字符串值比较（兼容AdjustmentTypeEnum和AdjustmentType）
            adj_type_value = adjustment_type.value if hasattr(adjustment_type, 'value') else str(adjustment_type)
            
            if adj_type_value == "increase":
                inventory.total_quantity += quantity
                inventory.available_quantity += quantity
                transaction_type = TransactionType.RESTOCK
            elif adj_type_value == "decrease":
                if inventory.available_quantity < quantity:
                    raise ValueError(
                        f"可用库存不足，当前: {inventory.available_quantity}, 需要: {quantity}"
                    )
                inventory.total_quantity -= quantity
                inventory.available_quantity -= quantity
                transaction_type = TransactionType.ADJUST
            elif adj_type_value == "set":
                inventory.total_quantity = quantity
                inventory.available_quantity = quantity - inventory.reserved_quantity
                quantity = abs(quantity - old_quantity)  # 记录变化量
                transaction_type = TransactionType.ADJUST
            else:
                raise ValueError(f"不支持的调整类型: {adjustment_type}")

            # 创建变动记录
            transaction_obj = InventoryTransaction(
                sku_id=sku_id,
                transaction_type=transaction_type,
                quantity_change=quantity,
                reference_id=reference,
                operator_id=operator_id,
                reason=reason,
                quantity_before=inventory.total_quantity
                - (
                    quantity
                    if adjustment_type == AdjustmentType.INCREASE
                    else -quantity
                ),
                quantity_after=inventory.total_quantity,
            )
            transaction = self.repository.create_transaction(transaction_obj)

            self.db.commit()

            return AdjustmentResponse(
                sku_id=sku_id,
                old_quantity=old_quantity,
                new_quantity=inventory.total_quantity,
                adjustment_quantity=abs(quantity),
                transaction_id=str(transaction.id) if transaction.id else "pending",
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
                "reserved_quantity": 0,
            }

    def get_low_stock_skus(self, query_or_threshold=None) -> List[LowStockItem]:
        """
        获取低库存SKU列表
        
        Args:
            query_or_threshold: 查询对象或阈值数值
            
        Returns:
            低库存商品列表
        """
        # 检查参数类型并构建查询条件
        if query_or_threshold is not None:
            if hasattr(query_or_threshold, "level"):
                # 是LowStockQuery对象
                level = query_or_threshold.level
                if level == "critical":
                    # 使用critical_threshold - 传入None让Repository使用各SKU自己的critical_threshold
                    # TODO: Repository暂不支持threshold_type参数，使用默认逻辑
                    results = self.repository.get_low_stock_items(threshold=None)
                else:  # warning
                    # 使用warning_threshold - 传入None让Repository使用各SKU自己的warning_threshold
                    results = self.repository.get_low_stock_items(threshold=None)
            else:
                # 是数值阈值 - 使用自定义阈值
                results = self.repository.get_low_stock_items(threshold=query_or_threshold)
        else:
            # 默认使用预警阈值
            results = self.repository.get_low_stock_items(threshold=None)

        return [
            LowStockItem(
                sku_id=inv.sku_id,
                current_quantity=inv.available_quantity,
                warning_threshold=inv.warning_threshold,
                critical_threshold=inv.critical_threshold,
                level=(
                    "critical"
                    if inv.available_quantity < inv.critical_threshold
                    else "warning"
                ),
            )
            for inv in results
        ]

    def check_inventory_consistency(self) -> ConsistencyCheckResponse:
        """
        检查库存数据一致性
        
        Returns:
            一致性检查响应，包含不一致记录列表
        """
        inconsistent_records = []

        # 查询所有活跃库存
        inventories = self.repository.get_inventories_by_sku_ids([], is_active=True)

        # 如果参数为空列表，get_inventories_by_sku_ids可能返回空，改用直接查询
        if not inventories:
            stmt = select(InventoryStock).where(InventoryStock.is_active == True)
            inventories = self.db.execute(stmt).scalars().all()

        for inventory in inventories:
            issues = []

            # 检查数量一致性：total = available + reserved
            if inventory.total_quantity != (
                inventory.available_quantity + inventory.reserved_quantity
            ):
                issues.append("数量不一致")

            # 检查阈值合理性：critical <= warning
            if inventory.critical_threshold > inventory.warning_threshold:
                issues.append("阈值设置不合理")

            # 检查负数
            if inventory.available_quantity < 0 or inventory.reserved_quantity < 0:
                issues.append("存在负数")

            if issues:
                inconsistent_records.append(
                    ConsistencyCheckItem(
                        sku_id=inventory.sku_id,
                        issue="; ".join(issues),
                        suggested_action="检查库存数据并进行手动调整",
                    )
                )

        return ConsistencyCheckResponse(
            total_skus=len(inventories),
            inconsistent_skus=len(inconsistent_records),
            details=inconsistent_records,
        )

    def cleanup_expired_reservations(self) -> CleanupResponse:
        """
        清理过期预占
        
        Returns:
            清理响应，包含清理数量和释放库存量
        """
        now = datetime.now(timezone.utc)

        # 查询过期预占
        expired_reservations = self.repository.get_expired_reservations(now)

        cleaned_count = 0
        total_quantity_released = 0

        for reservation in expired_reservations:
            # 释放库存
            inventory = self.repository.get_inventory_by_sku(reservation.sku_id)

            if inventory:
                inventory.available_quantity += reservation.quantity
                inventory.reserved_quantity -= reservation.quantity
                total_quantity_released += reservation.quantity

            # 标记预占为非活跃
            self.repository.invalidate_reservation(reservation.id)
            cleaned_count += 1

        try:
            self.db.commit()
            return CleanupResponse(
                cleaned_reservations=cleaned_count,
                released_quantity=total_quantity_released,
            )
        except Exception:
            self.db.rollback()
            raise

    def get_transaction_logs(
        self, query: TransactionQuery
    ) -> TransactionSearchResponse:
        """
        获取库存变动记录
        
        Args:
            query: 交易查询条件
            
        Returns:
            交易搜索响应，包含总数和记录列表
        """
        # 应用查询条件
        sku_ids = query.sku_ids if query.sku_ids else None
        transaction_types = None
        if query.transaction_types:
            # 转换枚举值
            transaction_types = [
                getattr(TransactionType, t.name.upper())
                for t in query.transaction_types
            ]
        
        operator_id = query.operator_id if query.operator_id else None
        
        # 计算分页
        page = (query.offset // query.limit) + 1 if query.limit > 0 else 1
        page_size = query.limit

        # 使用Repository查询
        if sku_ids and len(sku_ids) == 1:
            # 单个SKU查询
            results, total = self.repository.get_transactions_by_sku(
                sku_id=sku_ids[0],
                transaction_type=transaction_types[0] if transaction_types else None,
                page=page,
                page_size=page_size
            )
            sku_id = sku_ids[0]
        else:
            # 多SKU或日期范围查询，使用通用方法
            # 这里简化处理，实际可能需要Repository增加更复杂的查询方法
            stmt = select(InventoryTransaction)
            
            if sku_ids:
                stmt = stmt.where(InventoryTransaction.sku_id.in_(sku_ids))
            if transaction_types:
                stmt = stmt.where(InventoryTransaction.transaction_type.in_(transaction_types))
            if operator_id:
                stmt = stmt.where(InventoryTransaction.operator_id == operator_id)
            
            stmt = stmt.order_by(InventoryTransaction.created_at.desc())
            
            # 计算总数
            count_stmt = select(InventoryTransaction).select_from(stmt.alias())
            total = len(self.db.execute(stmt).scalars().all())
            
            # 应用分页
            stmt = stmt.offset(query.offset).limit(query.limit)
            results = self.db.execute(stmt).scalars().all()
            
            sku_id = sku_ids[0] if sku_ids and len(sku_ids) == 1 else (results[0].sku_id if results else 0)

        # 转换为Response对象
        transaction_reads = [
            InventoryTransactionRead.model_validate(t) for t in results
        ]

        return TransactionSearchResponse(
            sku_id=sku_id, total=total, logs=transaction_reads
        )

    def search_transaction_logs(
        self, query: TransactionQuery
    ) -> List[TransactionSearchResponse]:
        """
        搜索库存变动记录（支持多SKU）
        
        Args:
            query: 交易查询条件
            
        Returns:
            交易搜索响应列表，每个SKU一个响应对象
            
        说明：
            与get_transaction_logs的区别：
            - get_transaction_logs: 单SKU查询，返回单个TransactionSearchResponse
            - search_transaction_logs: 多SKU查询，返回List[TransactionSearchResponse]
        """
        # 解析查询条件
        sku_ids = query.sku_ids if query.sku_ids else None
        transaction_types = None
        if query.transaction_types:
            # 转换为TransactionType枚举
            transaction_types = []
            for t in query.transaction_types:
                if isinstance(t, str):
                    transaction_types.append(TransactionType[t.upper()])
                else:
                    transaction_types.append(t)
        
        operator_id = query.operator_id if query.operator_id else None
        
        # 构建查询
        stmt = select(InventoryTransaction)
        
        if sku_ids:
            stmt = stmt.where(InventoryTransaction.sku_id.in_(sku_ids))
        if transaction_types:
            stmt = stmt.where(InventoryTransaction.transaction_type.in_(transaction_types))
        if operator_id:
            stmt = stmt.where(InventoryTransaction.operator_id == operator_id)
        
        stmt = stmt.order_by(InventoryTransaction.created_at.desc())
        
        # 应用分页
        stmt = stmt.offset(query.offset).limit(query.limit)
        
        # 执行查询
        results = self.db.execute(stmt).scalars().all()
        
        # 按SKU分组
        sku_groups = {}
        for transaction in results:
            sku_id = transaction.sku_id
            if sku_id not in sku_groups:
                sku_groups[sku_id] = []
            sku_groups[sku_id].append(transaction)
        
        # 构建响应列表
        response_list = []
        for sku_id, transactions in sku_groups.items():
            transaction_reads = [
                InventoryTransactionRead.model_validate(t) for t in transactions
            ]
            response_list.append(
                TransactionSearchResponse(
                    sku_id=sku_id,
                    total=len(transactions),
                    logs=transaction_reads
                )
            )
        
        return response_list

    # ============ 事件发布与集成 ============

    async def publish_inventory_event(
        self, 
        event_type: str, 
        event_data: Dict[str, Any],
        severity: str = "INFO"
    ) -> bool:
        """
        发布库存事件 - 用于系统集成和审计
        
        功能说明：
        1. **事件记录**：将事件写入日志系统，便于审计和追踪
        2. **时间戳**：自动添加事件发生时间（UTC时区）
        3. **事件ID**：生成唯一事件ID，用于事件去重和追踪
        4. **严重级别**：支持INFO/WARNING/ERROR级别分类
        5. **数据验证**：验证事件数据的完整性
        6. **异常捕获**：确保事件发布失败不影响业务流程
        
        Args:
            event_type: 事件类型，如"inventory.stock.reserved"
                - inventory.stock.reserved: 库存预占成功
                - inventory.stock.released: 库存释放成功
                - inventory.stock.deducted: 库存扣减成功
                - inventory.stock.adjusted: 库存调整完成
                - inventory.stock.low_warning: 库存低于警戒线
                - inventory.stock.critical: 库存低于危险线
            event_data: 事件数据字典，包含业务相关信息
            severity: 事件严重级别 (INFO/WARNING/ERROR)
            
        Returns:
            bool: 发布成功返回True，失败返回False
            
        事件数据标准格式：
            {
                "sku_id": int,              # SKU ID（必需）
                "user_id": int,             # 用户ID（可选）
                "operator_id": int,         # 操作员ID（可选）
                "quantity": int,            # 数量变化（可选）
                "old_value": int,           # 旧值（可选）
                "new_value": int,           # 新值（可选）
                "reason": str,              # 操作原因（可选）
                "reference_id": str,        # 业务引用ID（可选）
                "metadata": dict            # 额外元数据（可选）
            }
            
        使用示例：
            >>> await service.publish_inventory_event(
            ...     "inventory.stock.reserved",
            ...     {
            ...         "sku_id": 123,
            ...         "user_id": 456,
            ...         "quantity": 10,
            ...         "reference_id": "ORDER-001"
            ...     }
            ... )
            True
            
        TODO:
            - [ ] 集成消息队列（RabbitMQ/Kafka）实现异步事件分发
            - [ ] 添加事件重试机制，确保重要事件不丢失
            - [ ] 支持事件订阅者模式，允许其他模块订阅事件
            - [ ] 实现事件持久化到专门的事件存储（Event Store）
            - [ ] 添加事件版本控制，支持事件Schema演进
        """
        import logging
        import json
        
        logger = logging.getLogger(__name__)
        
        try:
            # 1. 生成事件唯一ID
            event_id = f"evt_{uuid.uuid4().hex[:16]}"
            
            # 2. 添加标准元数据
            event_payload = {
                "event_id": event_id,
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "severity": severity,
                "source": "inventory_management",
                "data": event_data
            }
            
            # 3. 数据验证
            required_fields = self._validate_event_data(event_type, event_data)
            if not required_fields:
                logger.warning(
                    f"[EVENT-VALIDATION-FAILED] {event_type}: 缺少必需字段",
                    extra={"event_payload": event_payload}
                )
                return False
            
            # 4. 根据严重级别选择日志级别
            log_message = f"[INVENTORY-EVENT] {event_type}"
            log_extra = {
                "event_id": event_id,
                "event_type": event_type,
                "event_data": event_data,
                "event_payload": json.dumps(event_payload, ensure_ascii=False)
            }
            
            if severity == "ERROR":
                logger.error(log_message, extra=log_extra)
            elif severity == "WARNING":
                logger.warning(log_message, extra=log_extra)
            else:
                logger.info(log_message, extra=log_extra)
            
            # 5. TODO: 发送到消息队列
            # 预留消息队列集成点
            # await self._send_to_message_queue(event_payload)
            
            # 6. 可选：记录到数据库事件表
            # 预留事件持久化点
            # await self._persist_event(event_payload)
            
            return True
            
        except Exception as e:
            # 确保事件发布失败不影响业务流程
            logger.error(
                f"[EVENT-PUBLISH-ERROR] 发布事件失败: {event_type}",
                exc_info=e,
                extra={
                    "event_type": event_type,
                    "event_data": event_data,
                    "error": str(e)
                }
            )
            return False
    
    def _validate_event_data(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        验证事件数据的完整性
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
            
        Returns:
            bool: 验证通过返回True，否则返回False
        """
        # 不同事件类型的必需字段
        required_fields_map = {
            "inventory.stock.reserved": ["sku_id", "user_id", "quantity"],
            "inventory.stock.released": ["reservation_id", "user_id"],  # reservation_id或reference_id都可以
            "inventory.stock.deducted": ["sku_id", "quantity", "operator_id"],
            "inventory.stock.adjusted": ["sku_id", "adjustment_type", "operator_id"],
            "inventory.stock.low_warning": ["sku_id", "current_quantity", "threshold"],
            "inventory.stock.critical": ["sku_id", "current_quantity", "threshold"],
        }
        
        # 获取必需字段列表（未定义的事件类型只要求sku_id）
        required_fields = required_fields_map.get(event_type, ["sku_id"])
        
        # 检查所有必需字段是否存在
        for field in required_fields:
            if field not in event_data:
                return False
        
        return True
