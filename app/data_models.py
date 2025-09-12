from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, Text, DECIMAL, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    # 密码认证
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    # 用户角色权限 (V1.0 Mini-MVP)
    role = Column(String(20), default='user', nullable=False)  # 'user', 'admin', 'super_admin'
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
    payments = relationship("Payment", back_populates="user")
    carts = relationship("Cart", back_populates="user")


class Category(Base):
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
        Index('idx_category_status', 'category_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
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
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_order_no', 'order_no'),
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
        Index('idx_order_product', 'order_id', 'product_id'),
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
        Index('idx_payment_no', 'payment_no'),
        Index('idx_order_user', 'order_id', 'user_id'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_external_payment', 'external_payment_id'),
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
        Index('idx_payment_status', 'payment_id', 'status'),
        Index('idx_gateway_refund', 'gateway_refund_id'),
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
        Index('idx_user_status', 'user_id', 'status'),
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
        Index('idx_cart_product', 'cart_id', 'product_id'),
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
        Index('idx_available_quantity', 'available_quantity'),
        Index('idx_warning_threshold', 'warning_threshold'),
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
        Index('idx_product_transaction', 'product_id', 'created_at'),
        Index('idx_reference', 'reference_type', 'reference_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_transaction_type', 'transaction_type'),
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
