from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# 用户相关 Schema
class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None
    wx_openid: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class CategoryTreeRead(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    sort_order: int
    is_active: bool
    created_at: datetime
    children: List['CategoryTreeRead'] = []

    class Config:
        from_attributes = True


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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


# 订单相关 Schema
class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]
    shipping_address: Optional[str] = None  # JSON string
    remark: Optional[str] = None

    @validator('items')
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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True
