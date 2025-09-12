"""
文件名：order.py
文件路径：app/models/order.py
功能描述：订单管理相关的数据模型定义
主要功能：
- Order订单模型：订单基础信息、状态管理、金额计算
- OrderItem订单项模型：订单商品明细、价格快照
- Cart购物车模型：购物车商品管理
使用说明：
- 导入：from app.models.order import Order, OrderItem, Cart
- 关系：Order与OrderItem的一对多关系，User与Order/Cart的一对多关系
依赖模块：
- app.models.base: 基础模型类和时间戳混合类
- sqlalchemy: 数据库字段定义和关系映射
"""

from sqlalchemy import Column, String, Text, DECIMAL, Integer, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, TimestampMixin


class Order(BaseModel, TimestampMixin):
    """订单模型"""
    __tablename__ = 'orders'
    
    order_no = Column(String(32), unique=True, nullable=False, index=True)  # 订单号
    
    # 用户关联
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 订单状态
    status = Column(String(20), nullable=False, default='pending')  # pending, paid, shipped, delivered, cancelled
    
    # 金额信息
    subtotal = Column(DECIMAL(10, 2), nullable=False, default=0.00)    # 小计
    shipping_fee = Column(DECIMAL(10, 2), nullable=False, default=0.00) # 运费
    discount_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00) # 优惠金额
    total_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)    # 总金额
    
    # 收货信息（JSON 存储）
    shipping_address = Column(Text, nullable=True)  # JSON string
    shipping_method = Column(String(50), default='standard', nullable=False)  # 配送方式
    
    # 备注和订单备注
    notes = Column(Text, nullable=True)  # 订单备注
    remark = Column(Text, nullable=True)  # 内部备注
    
    # 订单时间节点
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # 关系映射
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    
    # 索引优化
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_order_no', 'order_no'),
    )
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_no='{self.order_no}', status='{self.status}')>"


class OrderItem(BaseModel):
    """订单项模型"""
    __tablename__ = 'order_items'
    
    # 关联
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 商品快照信息（防止后续商品信息变更影响历史订单）
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100), nullable=False)
    
    # 数量和价格
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)  # 下单时价格快照
    subtotal = Column(DECIMAL(10, 2), nullable=False)    # quantity * unit_price
    
    # 关系映射
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    # 索引优化
    __table_args__ = (
        Index('idx_order_product', 'order_id', 'product_id'),
    )
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"


class Cart(BaseModel, TimestampMixin):
    """购物车模型"""
    __tablename__ = 'carts'
    
    # 用户和商品关联
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 数量
    quantity = Column(Integer, nullable=False, default=1)
    
    # 关系映射
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="cart_items")
    
    # 索引优化
    __table_args__ = (
        Index('idx_user_product', 'user_id', 'product_id'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})>"