"""
文件名：repository.py
文件路径：app/modules/inventory_management/repository.py
功能描述：库存管理模块的数据访问层（Repository Layer）

主要功能：
- 封装所有数据库操作，提供统一的数据访问接口
- 构建复杂查询，支持分页、过滤、排序
- 实现缓存读写策略，提高查询性能
- 管理数据库事务边界，确保数据一致性
- 优化SQL语句，使用适当的索引和查询策略

架构层次：
- Router Layer → Service Layer → Repository Layer → Model Layer
- Repository层是Service层和Model层之间的抽象

设计原则：
- 单一职责：Repository只负责数据访问，不包含业务逻辑
- 依赖倒置：Service依赖Repository接口，而不是具体实现
- 开闭原则：易于扩展新的数据访问方法，不修改已有代码

使用说明：
- 导入：from app.modules.inventory_management.repository import InventoryRepository
- 初始化：repository = InventoryRepository(db_session)
- 方法调用：inventory = repository.get_inventory_by_sku(sku_id)

依赖模块：
- app.modules.inventory_management.models: 库存数据模型
- sqlalchemy.orm.Session: 数据库会话管理
- sqlalchemy: SQL查询构建

优势特性：
- 数据访问逻辑集中管理
- 便于单元测试（可Mock）
- 支持缓存策略扩展
- 易于切换数据源

创建时间：2025-10-18
最后修改：2025-10-18
架构版本：V2.0 (四层架构)
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .models import (
    InventoryStock,
    InventoryReservation,
    InventoryTransaction,
    ReservationType,
    TransactionType,
    AdjustmentType
)


class InventoryRepository:
    """
    库存管理数据访问层
    
    封装所有与数据库交互的操作，为Service层提供统一的数据访问接口。
    遵循Repository模式，实现数据访问逻辑与业务逻辑的分离。
    
    主要职责：
    1. CRUD操作：提供基础的增删改查方法
    2. 查询构建：构建复杂的数据库查询
    3. 事务管理：管理数据库事务边界
    4. 性能优化：使用适当的索引和查询策略
    """
    
    def __init__(self, db: Session):
        """
        初始化Repository
        
        Args:
            db: SQLAlchemy数据库会话
        """
        self.db = db
    
    # ============ 库存主表操作 (InventoryStock) ============
    
    def get_inventory_by_sku(self, sku_id: int) -> Optional[InventoryStock]:
        """
        根据SKU ID获取库存记录
        
        Args:
            sku_id: SKU唯一标识
            
        Returns:
            InventoryStock对象，如果不存在则返回None
        """
        return (
            self.db.query(InventoryStock)
            .filter(InventoryStock.sku_id == sku_id)
            .first()
        )
    
    def get_inventories_by_sku_ids(
        self, 
        sku_ids: List[int],
        is_active: Optional[bool] = None
    ) -> List[InventoryStock]:
        """
        批量获取库存记录
        
        Args:
            sku_ids: SKU ID列表
            is_active: 是否仅查询激活状态，None表示不过滤
            
        Returns:
            InventoryStock对象列表
        """
        query = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id.in_(sku_ids)
        )
        
        if is_active is not None:
            query = query.filter(InventoryStock.is_active == is_active)
            
        return query.all()
    
    def get_inventory_for_update(
        self, 
        sku_id: int,
        is_active: Optional[bool] = None
    ) -> Optional[InventoryStock]:
        """
        获取库存记录并加悲观锁（SELECT FOR UPDATE）
        用于并发控制，防止库存超卖
        
        Args:
            sku_id: SKU唯一标识
            is_active: 是否仅查询激活状态，None表示不过滤
            
        Returns:
            InventoryStock对象，如果不存在则返回None
            
        Note:
            此方法会在数据库级别加行锁，直到事务提交或回滚才释放
        """
        query = (
            self.db.query(InventoryStock)
            .filter(InventoryStock.sku_id == sku_id)
        )
        
        if is_active is not None:
            query = query.filter(InventoryStock.is_active == is_active)
            
        return query.with_for_update().first()
    
    def get_active_inventories(self, limit: int = 100, offset: int = 0) -> List[InventoryStock]:
        """
        获取所有启用的库存记录（支持分页）
        
        Args:
            limit: 每页记录数，默认100
            offset: 偏移量，默认0
            
        Returns:
            InventoryStock对象列表
        """
        return (
            self.db.query(InventoryStock)
            .filter(InventoryStock.is_active == True)
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def create_inventory(
        self,
        sku_id: int,
        total_quantity: int,
        available_quantity: Optional[int] = None,
        reserved_quantity: int = 0,
        warning_threshold: int = 10,
        critical_threshold: int = 5,
        is_active: bool = True
    ) -> InventoryStock:
        """
        创建新的库存记录
        
        Args:
            sku_id: SKU ID（必需）
            total_quantity: 总库存数量（必需）
            available_quantity: 可用库存数量（默认等于total_quantity）
            reserved_quantity: 预占库存数量（默认0）
            warning_threshold: 低库存预警阈值（默认10）
            critical_threshold: 紧急库存阈值（默认5）
            is_active: 是否启用（默认True）
                
        Returns:
            创建的InventoryStock对象
            
        Raises:
            IntegrityError: 如果SKU已存在库存记录
        """
        if available_quantity is None:
            available_quantity = total_quantity
            
        inventory = InventoryStock(
            sku_id=sku_id,
            total_quantity=total_quantity,
            available_quantity=available_quantity,
            reserved_quantity=reserved_quantity,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            is_active=is_active
        )
        self.db.add(inventory)
        self.db.flush()  # 刷新获取ID，但不提交事务
        self.db.refresh(inventory)
        return inventory
    
    def update_inventory_quantity(
        self, 
        sku_id: int, 
        total_change: int = 0,
        reserved_change: int = 0
    ) -> bool:
        """
        更新库存数量
        
        Args:
            sku_id: SKU ID
            total_change: 总库存变化量（正数为增加，负数为减少）
            reserved_change: 预占库存变化量（正数为增加，负数为减少）
            
        Returns:
            bool: 更新是否成功
            
        Note:
            此方法不会自动提交事务，需要调用方手动commit
        """
        inventory = self.get_inventory_by_sku(sku_id)
        if not inventory:
            return False
        
        if total_change != 0:
            inventory.total_quantity += total_change
        
        if reserved_change != 0:
            inventory.reserved_quantity += reserved_change
        
        # 更新时间戳
        inventory.updated_at = datetime.utcnow()
        
        return True
    
    def update_thresholds(
        self, 
        sku_id: int, 
        warning_threshold: Optional[int] = None,
        critical_threshold: Optional[int] = None
    ) -> bool:
        """
        更新库存预警阈值
        
        Args:
            sku_id: SKU ID
            warning_threshold: 低库存预警阈值
            critical_threshold: 紧急库存阈值
            
        Returns:
            bool: 更新是否成功
        """
        inventory = self.get_inventory_by_sku(sku_id)
        if not inventory:
            return False
        
        if warning_threshold is not None:
            inventory.warning_threshold = warning_threshold
        
        if critical_threshold is not None:
            inventory.critical_threshold = critical_threshold
        
        inventory.updated_at = datetime.utcnow()
        
        return True
    
    def deactivate_inventory(self, sku_id: int) -> bool:
        """
        停用库存管理
        
        Args:
            sku_id: SKU ID
            
        Returns:
            bool: 停用是否成功
        """
        inventory = self.get_inventory_by_sku(sku_id)
        if not inventory:
            return False
        
        inventory.is_active = False
        inventory.updated_at = datetime.utcnow()
        
        return True
    
    def get_low_stock_items(
        self, 
        threshold: Optional[int] = None
    ) -> List[InventoryStock]:
        """
        获取低库存商品列表
        
        Args:
            threshold: 库存阈值，如果为None则使用warning_threshold
            
        Returns:
            低库存的InventoryStock对象列表
        """
        query = self.db.query(InventoryStock).filter(
            InventoryStock.is_active == True
        )
        
        if threshold is not None:
            # 使用指定阈值
            query = query.filter(
                (InventoryStock.total_quantity - InventoryStock.reserved_quantity) <= threshold
            )
        else:
            # 使用各商品的warning_threshold
            query = query.filter(
                (InventoryStock.total_quantity - InventoryStock.reserved_quantity) <= InventoryStock.warning_threshold
            )
        
        return query.all()
    
    # ============ 库存预占操作 (InventoryReservation) ============
    
    def create_reservation(
        self,
        sku_id: int,
        reservation_type: str,
        reference_id: str,
        quantity: int,
        expires_at: datetime,
        is_active: bool = True
    ) -> InventoryReservation:
        """
        创建库存预占记录
        
        Args:
            sku_id: SKU ID（必需）
            reservation_type: 预占类型（必需）
            reference_id: 关联业务ID（必需）
            quantity: 预占数量（必需）
            expires_at: 过期时间（必需）
            is_active: 是否有效（默认True）
                
        Returns:
            创建的InventoryReservation对象
        """
        reservation = InventoryReservation(
            sku_id=sku_id,
            reservation_type=reservation_type,
            reference_id=reference_id,
            quantity=quantity,
            expires_at=expires_at,
            is_active=is_active
        )
        self.db.add(reservation)
        self.db.flush()  # 刷新获取ID，但不提交事务
        self.db.refresh(reservation)
        return reservation
    
    def get_reservation_by_id(self, reservation_id: int) -> Optional[InventoryReservation]:
        """
        根据ID获取预占记录
        
        Args:
            reservation_id: 预占记录ID
            
        Returns:
            InventoryReservation对象，如果不存在则返回None
        """
        return (
            self.db.query(InventoryReservation)
            .filter(InventoryReservation.id == reservation_id)
            .first()
        )
    
    def get_reservations_by_reference(
        self, 
        reference_id: str,
        reservation_type: Optional[ReservationType] = None,
        active_only: bool = True
    ) -> List[InventoryReservation]:
        """
        根据关联业务ID获取预占记录
        
        Args:
            reference_id: 关联业务ID（如订单ID、购物车ID）
            reservation_type: 预占类型（可选）
            active_only: 是否只返回有效预占，默认True
            
        Returns:
            InventoryReservation对象列表
        """
        query = self.db.query(InventoryReservation).filter(
            InventoryReservation.reference_id == reference_id
        )
        
        if reservation_type:
            query = query.filter(InventoryReservation.reservation_type == reservation_type)
        
        if active_only:
            query = query.filter(InventoryReservation.is_active == True)
        
        return query.all()
    
    def get_active_reservations_by_sku(self, sku_id: int) -> List[InventoryReservation]:
        """
        获取SKU的所有有效预占
        
        Args:
            sku_id: SKU ID
            
        Returns:
            有效的InventoryReservation对象列表
        """
        return (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.sku_id == sku_id,
                InventoryReservation.is_active == True
            )
            .all()
        )
    
    def get_expired_reservations(self, before: datetime) -> List[InventoryReservation]:
        """
        获取过期的预占记录
        
        Args:
            before: 截止时间，在此时间之前过期的预占
            
        Returns:
            过期的InventoryReservation对象列表
        """
        return (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.is_active == True,
                InventoryReservation.expires_at < before
            )
            .all()
        )
    
    def invalidate_reservation(self, reservation_id: int) -> bool:
        """
        标记预占失效
        
        Args:
            reservation_id: 预占记录ID
            
        Returns:
            bool: 标记是否成功
        """
        reservation = self.get_reservation_by_id(reservation_id)
        if not reservation:
            return False
        
        reservation.is_active = False
        reservation.updated_at = datetime.utcnow()
        
        return True
    
    def invalidate_reservations_batch(self, reservation_ids: List[int]) -> int:
        """
        批量标记预占失效
        
        Args:
            reservation_ids: 预占记录ID列表
            
        Returns:
            int: 成功标记的记录数量
        """
        result = (
            self.db.query(InventoryReservation)
            .filter(InventoryReservation.id.in_(reservation_ids))
            .update(
                {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                },
                synchronize_session=False
            )
        )
        
        return result
    
    # ============ 库存事务日志操作 (InventoryTransaction) ============
    
    def create_transaction(
        self,
        sku_id: int,
        transaction_type: TransactionType,
        quantity_change: int,
        quantity_before: int,
        quantity_after: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        reason: Optional[str] = None,
        operator_id: Optional[int] = None
    ) -> InventoryTransaction:
        """
        创建库存变动日志
        
        Args:
            sku_id: SKU ID（必需）
            transaction_type: 事务类型（必需）
            quantity_change: 数量变化（必需）
            quantity_before: 变更前数量（必需）
            quantity_after: 变更后数量（必需）
            reference_type: 关联业务类型（可选）
            reference_id: 关联业务ID（可选）
            reason: 变更原因（可选）
            operator_id: 操作人ID（可选）
                
        Returns:
            创建的InventoryTransaction对象
        """
        transaction = InventoryTransaction(
            sku_id=sku_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            operator_id=operator_id
        )
        self.db.add(transaction)
        self.db.flush()  # 刷新获取ID，但不提交事务
        self.db.refresh(transaction)
        return transaction
    
    def get_transactions_by_sku(
        self, 
        sku_id: int,
        transaction_type: Optional[TransactionType] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Tuple[List[InventoryTransaction], int]:
        """
        获取SKU的变动历史（支持分页和类型过滤）
        
        Args:
            sku_id: SKU ID
            transaction_type: 交易类型（可选）
            page: 页码，默认1
            page_size: 每页记录数，默认100
            
        Returns:
            Tuple[事务列表, 总记录数]
        """
        query = self.db.query(InventoryTransaction).filter(
            InventoryTransaction.sku_id == sku_id
        )
        
        # 添加交易类型过滤
        if transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == transaction_type)
        
        # 获取总数
        total = query.count()
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取分页数据
        transactions = (
            query
            .order_by(InventoryTransaction.created_at.desc())
            .limit(page_size)
            .offset(offset)
            .all()
        )
        
        return transactions, total
    
    def get_transactions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        transaction_type: Optional[TransactionType] = None,
        sku_id: Optional[int] = None
    ) -> List[InventoryTransaction]:
        """
        按日期范围查询事务记录
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            transaction_type: 事务类型（可选）
            sku_id: SKU ID（可选）
            
        Returns:
            InventoryTransaction对象列表
        """
        query = self.db.query(InventoryTransaction).filter(
            and_(
                InventoryTransaction.created_at >= start_date,
                InventoryTransaction.created_at <= end_date
            )
        )
        
        if transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == transaction_type)
        
        if sku_id:
            query = query.filter(InventoryTransaction.sku_id == sku_id)
        
        return query.order_by(InventoryTransaction.created_at.desc()).all()
    
    def get_transactions_by_reference(
        self,
        reference_type: str,
        reference_id: str
    ) -> List[InventoryTransaction]:
        """
        根据关联业务获取事务记录
        
        Args:
            reference_type: 关联业务类型（如'order', 'cart'）
            reference_id: 关联业务ID
            
        Returns:
            InventoryTransaction对象列表
        """
        return (
            self.db.query(InventoryTransaction)
            .filter(
                InventoryTransaction.reference_type == reference_type,
                InventoryTransaction.reference_id == reference_id
            )
            .order_by(InventoryTransaction.created_at.desc())
            .all()
        )
    
    # ============ 统计查询操作 ============
    
    def get_inventory_statistics(self, sku_ids: List[int]) -> Dict[str, Any]:
        """
        获取库存统计信息
        
        Args:
            sku_ids: SKU ID列表
            
        Returns:
            统计信息字典
        """
        inventories = self.get_inventories_by_sku_ids(sku_ids)
        
        total_skus = len(inventories)
        total_quantity = sum(inv.total_quantity for inv in inventories)
        total_reserved = sum(inv.reserved_quantity for inv in inventories)
        total_available = sum(inv.total_quantity - inv.reserved_quantity for inv in inventories)
        low_stock_count = sum(
            1 for inv in inventories 
            if (inv.total_quantity - inv.reserved_quantity) <= inv.warning_threshold
        )
        
        return {
            "total_skus": total_skus,
            "total_quantity": total_quantity,
            "total_reserved": total_reserved,
            "total_available": total_available,
            "low_stock_count": low_stock_count
        }
    
    def count_active_reservations_by_sku(self, sku_id: int) -> int:
        """
        统计SKU的有效预占数量
        
        Args:
            sku_id: SKU ID
            
        Returns:
            int: 有效预占记录数
        """
        return (
            self.db.query(func.count(InventoryReservation.id))
            .filter(
                InventoryReservation.sku_id == sku_id,
                InventoryReservation.is_active == True
            )
            .scalar()
        )
    
    # ============ 辅助方法 ============
    
    def flush(self) -> None:
        """
        刷新会话（不提交事务）
        将pending的更改发送到数据库，但不提交
        """
        self.db.flush()
    
    def refresh(self, instance) -> None:
        """
        刷新实例数据
        从数据库重新加载实例的最新数据
        
        Args:
            instance: 需要刷新的ORM实例
        """
        self.db.refresh(instance)
