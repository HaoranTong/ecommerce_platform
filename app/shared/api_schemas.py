from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# 用户认证相关 Schema
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    password: str = Field(..., min_length=6, max_length=128)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    real_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    username: str  # 可以是用户名或邮箱
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    real_name: Optional[str] = Field(None, max_length=100)


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: str  # V1.0 Mini-MVP: 用户角色
    is_active: bool
    wx_openid: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


# 购物车相关 Schema
class CartItemAdd(BaseModel):
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., gt=0, le=99, description="添加数量（1-99）")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0, le=99, description="更新数量（0表示删除）")


class CartItemRead(BaseModel):
    product_id: int
    product_name: str
    product_sku: str
    price: Decimal
    quantity: int
    subtotal: Decimal  # 小计
    stock_quantity: int  # 库存数量
    image_url: Optional[str] = None


class CartSummary(BaseModel):
    user_id: int
    items: List[CartItemRead]
    total_items: int  # 商品种类数
    total_quantity: int  # 总数量
    total_amount: Decimal  # 总金额
    
    model_config = ConfigDict(from_attributes=True)


class TokenRefresh(BaseModel):
    refresh_token: str


# 用户相关 Schema (保留兼容性)
class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None


# 分类相关 Schema
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    parent_id: Optional[int] = None
    sort_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    parent_id: Optional[int] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryRead(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    sort_order: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryTreeRead(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    sort_order: int
    is_active: bool
    created_at: datetime
    children: List['CategoryTreeRead'] = []

    model_config = ConfigDict(from_attributes=True)


# 商品相关 Schema
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=200)
    sku: str = Field(..., max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Decimal = Field(..., ge=0)
    stock_quantity: int = Field(..., ge=0)
    status: str = Field(default="active", pattern="^(active|inactive|out_of_stock)$")
    attributes: Optional[str] = None  # JSON string
    images: Optional[str] = None      # JSON string
    image_url: Optional[str] = Field(None, max_length=500, description="主图URL")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    sku: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive|out_of_stock)$")
    attributes: Optional[str] = None
    images: Optional[str] = None


class ProductStockUpdate(BaseModel):
    quantity_change: int = Field(..., description="库存变更量，正数为增加，负数为减少")
    reason: Optional[str] = Field(None, max_length=200, description="变更原因")


class ProductRead(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Decimal
    stock_quantity: int
    status: str
    attributes: Optional[str] = None
    images: Optional[str] = None
    image_url: Optional[str] = None  # 主图URL
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 订单项 Schema
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


# 订单相关 Schema
class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]
    shipping_address: Optional[str] = None  # JSON string
    remark: Optional[str] = None

    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError('订单必须包含至少一个商品')
        return v


class OrderRead(BaseModel):
    id: int
    order_no: str
    user_id: int
    status: str
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    shipping_address: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    # 包含订单项
    order_items: List[OrderItemRead] = []

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|paid|shipped|delivered|cancelled)$")


# 保留原有的 Certificate Schema（向后兼容）
class CertificateCreate(BaseModel):
    name: str
    issuer: Optional[str] = None
    serial: str
    description: Optional[str] = None


class CertificateRead(BaseModel):
    id: int
    name: str
    issuer: Optional[str] = None
    serial: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# 支付相关 Schema - V1.0 Mini-MVP
class PaymentCreate(BaseModel):
    order_id: int = Field(..., description="订单ID")
    payment_method: str = Field(..., description="支付方式", pattern=r'^(wechat|alipay|unionpay|paypal|balance)$')
    amount: Optional[Decimal] = Field(None, description="支付金额，为空时使用订单金额")
    currency: str = Field("CNY", description="货币类型")
    return_url: Optional[str] = Field(None, description="前端回调URL")
    notify_url: Optional[str] = Field(None, description="后端通知URL")
    description: Optional[str] = Field(None, description="支付描述")
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        allowed_methods = ['wechat', 'alipay', 'unionpay', 'paypal', 'balance']
        if v not in allowed_methods:
            raise ValueError(f'支付方式必须是: {", ".join(allowed_methods)}')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('支付金额必须大于0')
        return v


class PaymentRead(BaseModel):
    id: int
    order_id: int
    user_id: int
    payment_method: str
    amount: Decimal
    currency: str
    payment_no: str
    status: str
    external_payment_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    pay_url: Optional[str] = None
    qr_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentListResponse(BaseModel):
    items: List[PaymentRead]
    total: int
    page: int
    page_size: int
    pages: int


class RefundCreate(BaseModel):
    amount: Decimal = Field(..., description="退款金额")
    reason: str = Field(..., description="退款原因")
    operator_id: Optional[int] = Field(None, description="操作员ID")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('退款金额必须大于0')
        return v


class RefundRead(BaseModel):
    id: int
    payment_id: int
    amount: Decimal
    reason: str
    status: str
    gateway_refund_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    operator_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentStats(BaseModel):
    period: Dict[str, str]
    summary: Dict[str, Any]
    by_method: Dict[str, Dict[str, Any]]
    daily_trend: List[Dict[str, Any]]


class PaymentStatusUpdate(BaseModel):
    status: str = Field(..., description="支付状态")
    external_payment_id: Optional[str] = Field(None, description="第三方支付ID")
    external_transaction_id: Optional[str] = Field(None, description="第三方交易ID")
    callback_data: Optional[str] = Field(None, description="回调数据")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'paid', 'failed', 'refunded']
        if v not in allowed_statuses:
            raise ValueError(f'支付状态必须是: {", ".join(allowed_statuses)}')
        return v


class WechatPaymentCallback(BaseModel):
    """微信支付回调数据模型"""
    out_trade_no: str = Field(..., description="商户订单号")
    transaction_id: str = Field(..., description="微信支付订单号")
    trade_state: str = Field(..., description="交易状态")
    trade_state_desc: str = Field(..., description="交易状态描述")
    bank_type: Optional[str] = Field(None, description="银行类型")
    attach: Optional[str] = Field(None, description="附加数据")
    success_time: Optional[str] = Field(None, description="支付完成时间")


class RefundStatusUpdate(BaseModel):
    status: str = Field(..., description="退款状态")
    admin_note: Optional[str] = Field(None, description="管理员备注")
