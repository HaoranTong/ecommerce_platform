"""
文件名：models.py
文件路径：app/modules/inventory_management/models.py
功能描述：库存管理模块的数据模型定义

主要功能：
- 定义库存核心数据模型（Inventory、InventoryTransaction、InventoryReservation）
- 基于SKU的库存管理，严格遵循Product-SKU分离原则
- 支持库存预占、扣减、调整等业务操作
- 提供完整的库存变动审计追踪

使用说明：
- 导入：from app.modules.inventory_management.models import Inventory, InventoryTransaction
- 数据库表：inventory, inventory_transactions, inventory_reservations
- 关联关系：基于SKU进行库存管理，与product_catalog模块的SKU关联

依赖模块：
- app.shared.base_models.BaseModel: 基础模型类
- app.modules.product_catalog.models.SKU: SKU数据模型（外键关联）
- app.modules.user_auth.models.User: 用户模型（预占记录关联）

数据库设计：
- 遵循表模块映射架构设计标准
- 支持分布式环境下的数据一致性
- 包含完整的索引优化和性能设计

创建时间：2025-09-15
最后修改：2025-09-15
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SqlEnum, Index
from sqlalchemy.orm import relationship
import enum

from app.shared.base_models import BaseModel


class TransactionType(enum.Enum):
    """库存变动类型"""
    RESERVE = "reserve"      # 预占
    RELEASE = "release"      # 释放预占
    DEDUCT = "deduct"        # 扣减（实际出库）  
    ADJUST = "adjust"        # 手动调整
    RESTOCK = "restock"      # 入库


class ReservationType(enum.Enum):
    """预占类型"""
    CART = "cart"            # 购物车预占
    ORDER = "order"          # 订单预占


class AdjustmentType(enum.Enum):
    """调整类型"""
    INCREASE = "increase"    # 增加
    DECREASE = "decrease"    # 减少
    SET = "set"              # 直接设置


class InventoryStock(BaseModel):
    """
    SKU库存表
    
    核心设计原则：
    - 每个SKU独立管理库存
    - 支持可用数量、预占数量分离管理
    - 库存阈值配置支持自动预警
    """
    __tablename__ = "inventory_stocks"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String(50), ForeignKey("skus.id"), unique=True, index=True, nullable=False, comment="SKU ID")
    
    # 库存数量字段
    total_quantity = Column(Integer, nullable=False, default=0, comment="总库存数量")
    available_quantity = Column(Integer, nullable=False, default=0, comment="可用库存数量")
    reserved_quantity = Column(Integer, nullable=False, default=0, comment="预占库存数量")
    
    # 预警阈值
    warning_threshold = Column(Integer, nullable=False, default=10, comment="库存预警阈值")
    critical_threshold = Column(Integer, nullable=False, default=5, comment="库存严重不足阈值")
    
    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否启用库存管理")
    
    # 关系
    # sku = relationship("SKU", back_populates="inventory_stock")
    reservations = relationship("InventoryReservation", back_populates="stock", cascade="all, delete-orphan")
    transactions = relationship("InventoryTransaction", back_populates="stock", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_inventory_stocks_sku_id', 'sku_id'),
        Index('idx_inventory_stocks_available_quantity', 'available_quantity'),
        Index('idx_inventory_stocks_warning_threshold', 'warning_threshold'),
    )
    
    @property
    def is_low_stock(self) -> bool:
        """是否库存不足"""
        return self.available_quantity <= self.warning_threshold
    
    @property
    def is_critical_stock(self) -> bool:
        """是否库存严重不足"""
        return self.available_quantity <= self.critical_threshold
    
    @property
    def is_out_of_stock(self) -> bool:
        """是否缺货"""
        return self.available_quantity <= 0

    def can_reserve(self, quantity: int) -> bool:
        """检查是否可以预占指定数量"""
        return self.available_quantity >= quantity

    def reserve_quantity(self, quantity: int) -> bool:
        """预占库存"""
        if not self.can_reserve(quantity):
            return False
        
        self.available_quantity -= quantity
        self.reserved_quantity += quantity
        return True
    
    def release_quantity(self, quantity: int) -> bool:
        """释放预占库存"""
        if self.reserved_quantity < quantity:
            return False
            
        self.reserved_quantity -= quantity
        self.available_quantity += quantity
        return True
    
    def deduct_quantity(self, quantity: int, from_reserved: bool = True) -> bool:
        """扣减库存（实际出库）"""
        if from_reserved:
            # 从预占中扣减
            if self.reserved_quantity < quantity:
                return False
            self.reserved_quantity -= quantity
            self.total_quantity -= quantity
        else:
            # 直接从可用库存扣减
            if self.available_quantity < quantity:
                return False
            self.available_quantity -= quantity
            self.total_quantity -= quantity
        
        return True
    
    def adjust_quantity(self, adjustment_type: AdjustmentType, quantity: int) -> bool:
        """调整库存数量"""
        if adjustment_type == AdjustmentType.INCREASE:
            self.total_quantity += quantity
            self.available_quantity += quantity
        elif adjustment_type == AdjustmentType.DECREASE:
            if self.available_quantity < quantity:
                return False
            self.total_quantity -= quantity
            self.available_quantity -= quantity
        elif adjustment_type == AdjustmentType.SET:
            # 设置新的总库存，保持预占不变
            if quantity < self.reserved_quantity:
                return False
            self.total_quantity = quantity
            self.available_quantity = quantity - self.reserved_quantity
        
        return True


class InventoryReservation(BaseModel):
    """
    库存预占记录表
    
    支持购物车和订单的库存预占机制：
    - 购物车预占：临时锁定库存，防止其他用户购买
    - 订单预占：订单确认前的库存锁定
    - 自动过期机制：预占到期后自动释放
    """
    __tablename__ = "inventory_reservations"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String(50), ForeignKey("inventory_stocks.sku_id"), nullable=False, comment="SKU ID")
    
    # 预占信息
    reservation_type = Column(SqlEnum(ReservationType), nullable=False, comment="预占类型")
    reference_id = Column(String(100), nullable=False, comment="关联ID（用户ID或订单ID）")
    quantity = Column(Integer, nullable=False, comment="预占数量")
    
    # 时间控制
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否有效")
    
    # 关系
    stock = relationship("InventoryStock", back_populates="reservations")
    
    # 索引
    __table_args__ = (
        Index('idx_inventory_reservations_sku_id', 'sku_id'),
        Index('idx_inventory_reservations_reference_id', 'reference_id'),
        Index('idx_inventory_reservations_expires_at', 'expires_at'),
        Index('idx_inventory_reservations_reservation_type', 'reservation_type'),
        Index('idx_inventory_reservations_is_active', 'is_active'),
    )
    
    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        current_time = datetime.now(timezone.utc)
        expires_at = self.expires_at
        
        # 如果expires_at没有时区信息，假设它是UTC时间
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        return current_time > expires_at
    
    def extend_expiry(self, minutes: int):
        """延长过期时间"""
        from datetime import timedelta
        self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)


class InventoryTransaction(BaseModel):
    """
    库存变动记录表
    
    记录所有库存变动操作，支持：
    - 完整的操作审计跟踪  
    - 库存变动历史查询
    - 数据一致性验证
    """
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(String(50), ForeignKey("inventory_stocks.sku_id"), nullable=False, comment="SKU ID")
    
    # 变动信息
    transaction_type = Column(SqlEnum(TransactionType), nullable=False, comment="变动类型")
    quantity_change = Column(Integer, nullable=False, comment="变动数量（正数为增加，负数为减少）")
    
    # 变动前后状态
    quantity_before = Column(Integer, nullable=False, comment="变动前数量")
    quantity_after = Column(Integer, nullable=False, comment="变动后数量")
    
    # 关联信息
    reference_type = Column(String(50), comment="关联类型（order/cart/manual等）")
    reference_id = Column(String(100), comment="关联ID")
    
    # 操作信息
    operator_id = Column(Integer, comment="操作人ID")
    reason = Column(Text, comment="变动原因")
    notes = Column(Text, comment="备注信息")
    
    # 关系
    stock = relationship("InventoryStock", back_populates="transactions")
    
    # 索引
    __table_args__ = (
        Index('idx_inventory_transactions_sku_id', 'sku_id'),
        Index('idx_inventory_transactions_transaction_type', 'transaction_type'),
        Index('idx_inventory_transactions_reference_id', 'reference_id'),
        Index('idx_inventory_transactions_operator_id', 'operator_id'),
        Index('idx_inventory_transactions_created_at', 'created_at'),
    )
