from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    # 微信相关字段（为小程序对接预留）
    wx_openid = Column(String(100), unique=True, nullable=True)
    wx_unionid = Column(String(100), unique=True, nullable=True)
    # 基础用户信息
    phone = Column(String(20), nullable=True)
    real_name = Column(String(100), nullable=True)
    # 时间字段
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # 分类关联
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # 价格和库存
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # 商品状态
    status = Column(String(20), nullable=False, default='active')  # active, inactive, out_of_stock
    
    # 商品属性（JSON 存储，为后续扩展预留）
    attributes = Column(Text, nullable=True)  # JSON string
    images = Column(Text, nullable=True)      # JSON string of image URLs
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    
    # 索引
    __table_args__ = (
        Index('idx_category_status', 'category_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
    )


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False)  # 订单号
    
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
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    
    # 索引
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_order_no', 'order_no'),
    )


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 商品快照信息（防止后续商品信息变更影响历史订单）
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100), nullable=False)
    
    # 数量和价格
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)  # 下单时价格快照
    total_price = Column(DECIMAL(10, 2), nullable=False) # quantity * unit_price
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    # 索引
    __table_args__ = (
        Index('idx_order_product', 'order_id', 'product_id'),
    )


# 保留现有的 Certificate 模型（暂时保留，后续可能重构为质量认证系统的一部分）
class Certificate(Base):
    __tablename__ = 'certificates'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=True)
    serial = Column(String(200), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
