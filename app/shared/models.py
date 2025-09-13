"""
共享数据模型和基础组件

提供跨模块共享的基础模型类和通用数据结构
"""

from sqlalchemy import Column, Integer, BigInteger, String, Text, DECIMAL, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# 从技术基础设施层导入统一的Base类
from app.core.database import Base


class TimestampMixin:
    """时间戳混合类 - 提供统一的时间戳字段"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base):
    """基础模型类 - 提供通用字段和方法"""
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


# ===== 业务通用模型（真正跨模块共享的数据） =====

class Category(Base):
    """商品分类表 - 跨产品和库存模块共享"""
    __tablename__ = 'categories'
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)    description = Column(Text, nullable=True)

    sort_order = Column(Integer, default=0)    parent_id = Column(BigInteger, ForeignKey('categories.id'), nullable=True)

    is_active = Column(Boolean, default=True)    level = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, server_default=func.now())    sort_order = Column(Integer, default=0, nullable=False)

        is_active = Column(Boolean, default=True, nullable=False)

    # 关系    

    products = relationship("Product", back_populates="category")    # 时间戳

    created_at = Column(DateTime, server_default=func.now())

class Product(Base):    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    """商品表 - 核心商品信息"""    

    __tablename__ = 'products'    # 自引用关系

        parent = relationship("Category", remote_side=[id], back_populates="children")

    id = Column(BigInteger, primary_key=True, index=True)    children = relationship("Category", back_populates="parent")

    name = Column(String(200), nullable=False)    

    sku = Column(String(100), unique=True, nullable=False)    # 跨模块关系

    description = Column(Text, nullable=True)    products = relationship("Product", back_populates="category")

    

    # 分类关联

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)class Product(Base):

        """商品表 - 跨多个模块共享的核心商品信息"""

    # 价格和库存    __tablename__ = 'products'

    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)    

    stock_quantity = Column(Integer, nullable=False, default=0)    id = Column(BigInteger, primary_key=True, index=True)

        name = Column(String(255), nullable=False)

    # 商品状态    description = Column(Text, nullable=True)

    status = Column(String(20), nullable=False, default='active')  # active, inactive, out_of_stock    sku = Column(String(100), unique=True, nullable=False, index=True)

        price = Column(DECIMAL(10, 2), nullable=False)

    # 商品图片    cost_price = Column(DECIMAL(10, 2), nullable=True)

    image_url = Column(String(500), nullable=True)  # 主图URL    weight = Column(DECIMAL(8, 3), nullable=True)  # 重量(kg)

        

    # 商品属性（JSON 存储，为后续扩展预留）    # 分类关联

    attributes = Column(Text, nullable=True)  # JSON string    category_id = Column(BigInteger, ForeignKey('categories.id'), nullable=True)

    images = Column(Text, nullable=True)      # JSON string of image URLs    

        # 状态字段

    # 时间字段    status = Column(String(20), default='active', nullable=False)

    created_at = Column(DateTime, server_default=func.now())    is_active = Column(Boolean, default=True, nullable=False)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())    

        # 库存字段

    # 关系    stock_quantity = Column(Integer, default=0, nullable=False)

    category = relationship("Category", back_populates="products")    min_stock_level = Column(Integer, default=0, nullable=False)

    order_items = relationship("OrderItem", back_populates="product")    max_stock_level = Column(Integer, nullable=True)

    cart_items = relationship("CartItem", back_populates="product")    

        # 销售信息

    # 索引    sales_count = Column(Integer, default=0, nullable=False)

    __table_args__ = (    view_count = Column(Integer, default=0, nullable=False)

        Index('idx_products_category_status', 'category_id', 'status'),    

        Index('idx_products_status_created', 'status', 'created_at'),    # 时间戳

    )    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Order(Base):    

    """订单表 - 核心订单信息"""    # 关系定义

    __tablename__ = 'orders'    category = relationship("Category", back_populates="products")

        order_items = relationship("OrderItem", back_populates="product")

    id = Column(BigInteger, primary_key=True, index=True)    cart_items = relationship("CartItem", back_populates="product")

    order_number = Column(String(50), unique=True, nullable=False, index=True)    payments = relationship("Payment", back_populates="product")

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)    

        # 索引

    # 订单状态    __table_args__ = (

    status = Column(String(20), default='pending', nullable=False)        Index('idx_products_category_status', 'category_id', 'status'),

    payment_status = Column(String(20), default='unpaid', nullable=False)        Index('idx_products_sku', 'sku'),

        )

    # 金额信息

    total_amount = Column(DECIMAL(10, 2), nullable=False)

    payment_amount = Column(DECIMAL(10, 2), default=0, nullable=False)class Order(Base):

    discount_amount = Column(DECIMAL(10, 2), default=0, nullable=False)    """订单表 - 跨订单管理和支付模块共享"""

        __tablename__ = 'orders'

    # 地址信息    

    shipping_address = Column(Text, nullable=True)    id = Column(BigInteger, primary_key=True, index=True)

    contact_phone = Column(String(20), nullable=True)    order_number = Column(String(50), unique=True, nullable=False, index=True)

    contact_name = Column(String(100), nullable=True)    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

        

    # 备注    # 订单状态

    remark = Column(Text, nullable=True)    status = Column(String(20), default='pending', nullable=False)

        payment_status = Column(String(20), default='unpaid', nullable=False)

    # 时间戳    

    created_at = Column(DateTime, server_default=func.now())    # 金额信息

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())    total_amount = Column(DECIMAL(10, 2), nullable=False)

        payment_amount = Column(DECIMAL(10, 2), default=0, nullable=False)

    # 关系定义    discount_amount = Column(DECIMAL(10, 2), default=0, nullable=False)

    order_items = relationship("OrderItem", back_populates="order")    

    payments = relationship("Payment", back_populates="order")    # 地址信息

    shipping_address = Column(Text, nullable=True)

class OrderItem(Base):    contact_phone = Column(String(20), nullable=True)

    """订单商品明细表"""    contact_name = Column(String(100), nullable=True)

    __tablename__ = 'order_items'    

        # 备注

    id = Column(BigInteger, primary_key=True, index=True)    remark = Column(Text, nullable=True)

    order_id = Column(BigInteger, ForeignKey('orders.id'), nullable=False)    

    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)    # 时间戳

        created_at = Column(DateTime, server_default=func.now())

    quantity = Column(Integer, nullable=False)    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    unit_price = Column(DECIMAL(10, 2), nullable=False)    

    total_price = Column(DECIMAL(10, 2), nullable=False)    # 关系定义

        order_items = relationship("OrderItem", back_populates="order")

    # 时间戳    payments = relationship("Payment", back_populates="order")

    created_at = Column(DateTime, server_default=func.now())    carts = relationship("Cart", back_populates="order")

    

    # 关系定义

    order = relationship("Order", back_populates="order_items")class OrderItem(Base):

    product = relationship("Product", back_populates="order_items")    """订单商品明细表"""

    __tablename__ = 'order_items'

class Payment(Base):    

    """支付记录表 - 跨支付和订单模块共享"""    id = Column(BigInteger, primary_key=True, index=True)

    __tablename__ = 'payments'    order_id = Column(BigInteger, ForeignKey('orders.id'), nullable=False)

        product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)

    id = Column(BigInteger, primary_key=True, index=True)    

    payment_number = Column(String(50), unique=True, nullable=False, index=True)    quantity = Column(Integer, nullable=False)

    order_id = Column(BigInteger, ForeignKey('orders.id'), nullable=False)    unit_price = Column(DECIMAL(10, 2), nullable=False)

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)    total_price = Column(DECIMAL(10, 2), nullable=False)

        

    # 支付信息    # 时间戳

    amount = Column(DECIMAL(10, 2), nullable=False)    created_at = Column(DateTime, server_default=func.now())

    payment_method = Column(String(20), nullable=False)    

    payment_status = Column(String(20), default='pending', nullable=False)    # 关系定义

        order = relationship("Order", back_populates="order_items")

    # 第三方支付信息    product = relationship("Product", back_populates="order_items")

    third_party_payment_id = Column(String(100), nullable=True)

    payment_gateway = Column(String(50), nullable=True)

    class Payment(Base):

    # 时间戳    """支付记录表 - 跨支付和订单模块共享"""

    created_at = Column(DateTime, server_default=func.now())    __tablename__ = 'payments'

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())    

        id = Column(BigInteger, primary_key=True, index=True)

    # 关系定义    payment_number = Column(String(50), unique=True, nullable=False, index=True)

    order = relationship("Order", back_populates="payments")    order_id = Column(BigInteger, ForeignKey('orders.id'), nullable=False)

    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=True)

class Cart(Base):    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    """购物车表"""    

    __tablename__ = 'carts'    # 支付信息

        amount = Column(DECIMAL(10, 2), nullable=False)

    id = Column(BigInteger, primary_key=True, index=True)    payment_method = Column(String(20), nullable=False)

    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)    payment_status = Column(String(20), default='pending', nullable=False)

        

    # 购物车状态    # 第三方支付信息

    status = Column(String(20), default='active', nullable=False)    third_party_payment_id = Column(String(100), nullable=True)

    total_amount = Column(DECIMAL(10, 2), default=0, nullable=False)    payment_gateway = Column(String(50), nullable=True)

        

    # 时间戳    # 时间戳

    created_at = Column(DateTime, server_default=func.now())    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

        

    # 关系定义    # 关系定义

    cart_items = relationship("CartItem", back_populates="cart")    order = relationship("Order", back_populates="payments")

    product = relationship("Product", back_populates="payments")

class CartItem(Base):

    """购物车商品明细表"""

    __tablename__ = 'cart_items'class Cart(Base):

        """购物车表"""

    id = Column(BigInteger, primary_key=True, index=True)    __tablename__ = 'carts'

    cart_id = Column(BigInteger, ForeignKey('carts.id'), nullable=False)    

    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)    id = Column(BigInteger, primary_key=True, index=True)

        user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    quantity = Column(Integer, nullable=False)    order_id = Column(BigInteger, ForeignKey('orders.id'), nullable=True)

    unit_price = Column(DECIMAL(10, 2), nullable=False)    

    total_price = Column(DECIMAL(10, 2), nullable=False)    # 购物车状态

        status = Column(String(20), default='active', nullable=False)

    # 时间戳    total_amount = Column(DECIMAL(10, 2), default=0, nullable=False)

    created_at = Column(DateTime, server_default=func.now())    

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())    # 时间戳

        created_at = Column(DateTime, server_default=func.now())

    # 关系定义    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cart = relationship("Cart", back_populates="cart_items")    

    product = relationship("Product", back_populates="cart_items")    # 关系定义

    cart_items = relationship("CartItem", back_populates="cart")

# ===== 质量控制模块模型 =====    order = relationship("Order", back_populates="carts")



class Certificate(Base):

    """质量认证证书表"""class CartItem(Base):

    __tablename__ = 'certificates'    """购物车商品明细表"""

        __tablename__ = 'cart_items'

    id = Column(BigInteger, primary_key=True, index=True)    

    name = Column(String(200), nullable=False)    id = Column(BigInteger, primary_key=True, index=True)

    issuer = Column(String(200), nullable=True)    cart_id = Column(BigInteger, ForeignKey('carts.id'), nullable=False)

    serial = Column(String(200), unique=True, nullable=False)    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系定义
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    __tablename__ = 'categories'
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(BigInteger, primary_key=True, index=True)
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
    
    # 商品图片
    image_url = Column(String(500), nullable=True)  # 主图URL
    
    # 商品属性（JSON 存储，为后续扩展预留）
    attributes = Column(Text, nullable=True)  # JSON string
    images = Column(Text, nullable=True)      # JSON string of image URLs
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    
    # 索引
    __table_args__ = (
        Index('idx_products_category_status', 'category_id', 'status'),
        Index('idx_products_status_created', 'status', 'created_at'),
    )


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(BigInteger, primary_key=True, index=True)
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
    payments = relationship("Payment", back_populates="order")  # V1.0: 支付关系
    
    # 索引
    __table_args__ = (
        Index('idx_orders_user_status', 'user_id', 'status'),
        Index('idx_orders_status_created', 'status', 'created_at'),
        Index('idx_orders_order_no', 'order_no'),
    )


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(BigInteger, primary_key=True, index=True)
    
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
        Index('idx_order_items_order_product', 'order_id', 'product_id'),
    )


# 保留现有的 Certificate 模型（暂时保留，后续可能重构为质量认证系统的一部分）
class Certificate(Base):
    __tablename__ = 'certificates'
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    issuer = Column(String(200), nullable=True)
    serial = Column(String(200), unique=True, nullable=False)


class Payment(Base):
    """支付单模型 - V1.0 Mini-MVP"""
    __tablename__ = 'payments'
    
    id = Column(BigInteger, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 所有权字段
    
    # 支付信息
    payment_method = Column(String(50), nullable=False)  # 'wechat', 'alipay', 'unionpay', 'paypal', 'balance'
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='CNY')
    
    # 支付单号
    payment_no = Column(String(100), unique=True, nullable=False)  # 内部支付单号
    
    # 状态字段  
    status = Column(String(20), default='pending')  # 'pending', 'paid', 'failed', 'cancelled', 'expired', 'refunding', 'refunded'
    
    # 第三方信息
    external_payment_id = Column(String(200), nullable=True)  # 支付网关订单号
    external_transaction_id = Column(String(200), nullable=True)  # 支付网关交易号
    
    # 支付页面信息
    pay_url = Column(String(1000), nullable=True)  # 支付页面URL
    qr_code = Column(Text, nullable=True)  # 二维码Base64数据
    expires_at = Column(DateTime, nullable=True)  # 支付过期时间
    
    # 回调信息
    callback_received_at = Column(DateTime, nullable=True)
    callback_data = Column(Text, nullable=True)  # 加密存储的回调数据
    
    # 描述信息
    description = Column(String(1000), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # 关系
    order = relationship("Order", back_populates="payments")
    user = relationship("User", back_populates="payments")
    refunds = relationship("Refund", back_populates="payment")
    
    # 索引
    __table_args__ = (
        Index('idx_payments_payment_no', 'payment_no'),
        Index('idx_payments_order_user', 'order_id', 'user_id'),
        Index('idx_payments_status_created', 'status', 'created_at'),
        Index('idx_payments_external_payment', 'external_payment_id'),
    )


class Refund(Base):
    """退款单模型 - V1.0 Mini-MVP"""
    __tablename__ = 'refunds'
    
    id = Column(BigInteger, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    
    # 退款信息
    amount = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(String(500), nullable=False)
    status = Column(String(20), default='processing')  # 'processing', 'success', 'failed', 'cancelled'
    
    # 第三方退款信息
    gateway_refund_id = Column(String(200), nullable=True)
    
    # 操作信息
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # 时间字段
    created_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # 关系
    payment = relationship("Payment", back_populates="refunds")
    operator = relationship("User", foreign_keys=[operator_id])
    
    # 索引
    __table_args__ = (
        Index('idx_refunds_payment_status', 'payment_id', 'status'),
        Index('idx_refunds_gateway_refund', 'gateway_refund_id'),
    )


class Cart(Base):
    """购物车模型"""
    __tablename__ = 'carts'
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='active', nullable=False)  # active, inactive, converted
    total_amount = Column(DECIMAL(10, 2), default=0.00)
    total_discount = Column(DECIMAL(10, 2), default=0.00)
    item_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)  # 购物车过期时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_cart_user_status', 'user_id', 'status'),
        Index('idx_cart_expires', 'expires_at'),
    )


class CartItem(Base):
    """购物车项目模型"""
    __tablename__ = 'cart_items'
    
    id = Column(BigInteger, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)  # 商品单价
    original_price = Column(DECIMAL(10, 2), nullable=False)  # 原始价格
    discount_amount = Column(DECIMAL(10, 2), default=0.00)  # 折扣金额
    total_price = Column(DECIMAL(10, 2), nullable=False)  # 小计
    added_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    
    # 约束和索引
    __table_args__ = (
        Index('idx_cart_items_cart_product', 'cart_id', 'product_id'),
        Index('idx_cart_items_cart', 'cart_id'),
        # 确保同一购物车中每个商品只有一条记录
        # UniqueConstraint('cart_id', 'product_id', name='uq_cart_product'),
    )


# ============ 库存管理模块模型 ============

from datetime import timedelta
from enum import Enum
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy import UniqueConstraint


class TransactionType(str, Enum):
    """库存变动类型"""
    IN = "IN"           # 入库
    OUT = "OUT"         # 出库
    RESERVE = "RESERVE" # 预占
    RELEASE = "RELEASE" # 释放
    ADJUST = "ADJUST"   # 调整


class ReferenceType(str, Enum):
    """变动关联类型"""
    ORDER = "ORDER"     # 订单
    CART = "CART"       # 购物车
    MANUAL = "MANUAL"   # 手动操作
    IMPORT = "IMPORT"   # 批量导入


class Inventory(Base):
    """库存主表"""
    __tablename__ = "inventory"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(
        Integer, 
        ForeignKey("products.id", ondelete="CASCADE"), 
        nullable=False,
        unique=True
    )
    available_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    total_quantity = Column(Integer, nullable=False, default=0)
    warning_threshold = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # 关系定义
    product = relationship("Product", back_populates="inventory")

    # 索引定义
    __table_args__ = (
        Index('idx_inventory_available_quantity', 'available_quantity'),
        Index('idx_inventory_warning_threshold', 'warning_threshold'),
    )

    @property
    def is_low_stock(self) -> bool:
        """是否低库存"""
        return self.available_quantity <= self.warning_threshold

    @property
    def is_out_of_stock(self) -> bool:
        """是否缺货"""
        return self.available_quantity <= 0

    def can_reserve(self, quantity: int) -> bool:
        """检查是否可以预占指定数量"""
        return self.available_quantity >= quantity

    def update_quantities(self, available_delta: int = 0, reserved_delta: int = 0):
        """更新库存数量"""
        self.available_quantity += available_delta
        self.reserved_quantity += reserved_delta
        self.total_quantity = self.available_quantity + self.reserved_quantity


class InventoryTransaction(Base):
    """库存变动记录表"""
    __tablename__ = "inventory_transactions"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(ENUM(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference_type = Column(ENUM(ReferenceType), nullable=True)
    reference_id = Column(Integer, nullable=True)
    reason = Column(String(500), nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    before_quantity = Column(Integer, nullable=True)
    after_quantity = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 关系定义
    operator = relationship("User")

    # 索引定义
    __table_args__ = (
        Index('idx_inventory_transactions_product_created', 'product_id', 'created_at'),
        Index('idx_inventory_transactions_reference', 'reference_type', 'reference_id'),
        Index('idx_inventory_transactions_created_at', 'created_at'),
        Index('idx_inventory_transactions_type', 'transaction_type'),
    )


class CartReservation(Base):
    """购物车库存预占表"""
    __tablename__ = "cart_reservations"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    reserved_quantity = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 关系定义
    user = relationship("User")
    product = relationship("Product")

    # 唯一约束和索引
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uk_user_product'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_user_id', 'user_id'),
    )

    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at

    @property
    def remaining_minutes(self) -> int:
        """剩余分钟数"""
        from datetime import datetime
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds() / 60))

    @classmethod
    def create_expiration_time(cls, minutes: int = 30):
        """创建过期时间"""
        from datetime import datetime, timedelta
        return datetime.utcnow() + timedelta(minutes=minutes)

    def extend_expiration(self, minutes: int = 30):
        """延长过期时间"""
        from datetime import datetime, timedelta
        self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
