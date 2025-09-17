"""
订单管理模块数据模型

根据 docs/modules/order-management/design.md 文档规范实现
符合数据库设计原则和字段命名标准

主要模型:
- Order: 订单主表，订单生命周期和状态管理
- OrderItem: 订单商品表，订单商品明细和价格快照记录
- OrderStatusHistory: 订单状态历史表，状态变更审计记录
"""

from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# 从架构标准的数据库层导入Base类
from app.core.database import Base


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    SHIPPED = "shipped"     # 已发货
    DELIVERED = "delivered" # 已送达
    CANCELLED = "cancelled" # 已取消
    RETURNED = "returned"   # 已退货


class Order(Base):
    """订单主表模型
    
    管理订单的完整生命周期，包括订单基础信息、金额信息、收货信息等
    符合 docs/modules/order-management/design.md 设计规范
    """
    __tablename__ = 'orders'
    
    # 主键 - 使用INTEGER符合database-standards.md规范
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 业务唯一标识
    order_number = Column(String(32), unique=True, nullable=False, index=True, comment='订单号')
    
    # 用户关联 - 外键关系
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    
    # 订单状态
    status = Column(String(20), nullable=False, default='pending', comment='订单状态')
    
    # 金额信息 - 使用Numeric符合database-standards.md规范
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.00, comment='小计金额')
    shipping_fee = Column(Numeric(10, 2), nullable=False, default=0.00, comment='运费')
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.00, comment='折扣金额')
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00, comment='总金额')
    
    # 收货信息
    shipping_address = Column(Text, nullable=True, comment='收货地址')
    shipping_method = Column(String(50), default='standard', comment='配送方式')
    
    # 备注信息
    notes = Column(Text, nullable=True, comment='订单备注')
    
    # 审计字段 - 统一时间戳字段
    created_at = Column(DateTime, default=func.now(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment='更新时间')
    
    # 关系映射 - 使用单向关系避免跨模块依赖问题
    user = relationship("User")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    # 支付关系 - 移除避免跨模块依赖问题
    # payments = relationship("Payment")  # 在单模块测试时不可用
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    """订单商品表模型
    
    存储订单中的商品明细信息，包含商品快照数据防止历史数据变更
    实现Product+SKU双重关联架构，符合table-module-mapping.md规范
    """
    __tablename__ = 'order_items'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联关系 - Product+SKU双重关联
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True, comment='订单ID')
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True, comment='商品ID')
    sku_id = Column(Integer, ForeignKey('skus.id'), nullable=False, index=True, comment='SKU ID')
    
    # 商品快照信息 - 防止后续商品信息变更影响历史订单
    sku_code = Column(String(100), nullable=False, comment='SKU编码快照')
    product_name = Column(String(200), nullable=False, comment='商品名称快照')
    sku_name = Column(String(200), nullable=False, comment='SKU名称快照')
    
    # 数量和价格信息
    quantity = Column(Integer, nullable=False, comment='商品数量')
    unit_price = Column(Numeric(10, 2), nullable=False, comment='单价快照')
    total_price = Column(Numeric(10, 2), nullable=False, comment='小计金额')
    
    # 审计字段
    created_at = Column(DateTime, default=func.now(), nullable=False, comment='创建时间')
    
    # 关系映射
    order = relationship("Order", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, sku_code='{self.sku_code}')>"


class OrderStatusHistory(Base):
    """订单状态历史表模型
    
    记录订单状态变更的完整审计轨迹，包括变更时间、操作人、备注等信息
    支持订单状态变更的可追溯性和审计要求
    """
    __tablename__ = 'order_status_history'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 订单关联
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True, comment='订单ID')
    
    # 状态变更信息
    old_status = Column(String(20), nullable=True, comment='原状态')
    new_status = Column(String(20), nullable=False, comment='新状态')
    remark = Column(Text, nullable=True, comment='状态变更备注')
    
    # 操作人信息
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment='操作人ID')
    
    # 审计字段
    created_at = Column(DateTime, default=func.now(), nullable=False, comment='变更时间')
    
    # 关系映射
    order = relationship("Order", back_populates="status_history")
    operator = relationship("User")
    
    def __repr__(self):
        return f"<OrderStatusHistory(id={self.id}, order_id={self.order_id}, {self.old_status}->{self.new_status})>"