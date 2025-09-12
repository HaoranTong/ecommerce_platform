"""
库存管理模块 Pydantic Schemas

此模块定义了库存管理相关的请求和响应数据模型，包括：
- 库存查询和修改的schemas
- 库存预占和释放的schemas  
- 库存变动记录的schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator
from enum import Enum


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


class AdjustmentType(str, Enum):
    """库存调整类型"""
    ADD = "ADD"         # 增加
    SUBTRACT = "SUBTRACT"  # 减少
    SET = "SET"         # 设置


# ============ 基础 Schemas ============

class InventoryBase(BaseModel):
    """库存基础信息"""
    available_quantity: int
    reserved_quantity: int
    total_quantity: int
    warning_threshold: int


class InventoryCreate(InventoryBase):
    """创建库存"""
    product_id: int


class InventoryUpdate(BaseModel):
    """更新库存"""
    available_quantity: Optional[int] = None
    reserved_quantity: Optional[int] = None
    warning_threshold: Optional[int] = None


class InventoryRead(InventoryBase):
    """库存读取"""
    id: int
    product_id: int
    is_low_stock: bool
    is_out_of_stock: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 库存查询 Schemas ============

class ProductInventoryQuery(BaseModel):
    """商品库存查询"""
    product_id: int


class BatchInventoryQuery(BaseModel):
    """批量库存查询"""
    product_ids: List[int]

    @validator('product_ids')
    def validate_product_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('product_ids不能为空')
        if len(v) > 100:
            raise ValueError('一次最多查询100个商品')
        return v


class InventorySimple(BaseModel):
    """简化的库存信息"""
    product_id: int
    available_quantity: int
    reserved_quantity: int
    total_quantity: int
    is_low_stock: bool

    class Config:
        from_attributes = True


# ============ 库存预占 Schemas ============

class ReservationItem(BaseModel):
    """预占商品项"""
    product_id: int
    quantity: int

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('数量必须大于0')
        return v


class CartReserveRequest(BaseModel):
    """购物车库存预占请求"""
    items: List[ReservationItem]
    expires_minutes: Optional[int] = 30

    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('预占商品不能为空')
        return v

    @validator('expires_minutes')
    def validate_expires_minutes(cls, v):
        if v is not None and (v < 1 or v > 120):
            raise ValueError('过期时间必须在1-120分钟之间')
        return v


class OrderReserveRequest(BaseModel):
    """订单库存预占请求"""
    order_id: int
    items: List[ReservationItem]

    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('预占商品不能为空')
        return v


class ReservedItem(BaseModel):
    """已预占商品信息"""
    product_id: int
    reserved_quantity: int
    available_after_reserve: int


class ReservationResponse(BaseModel):
    """预占响应"""
    reservation_id: str
    expires_at: datetime
    reserved_items: List[ReservedItem]


# ============ 库存扣减 Schemas ============

class DeductItem(BaseModel):
    """扣减商品项"""
    product_id: int
    quantity: int

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('扣减数量必须大于0')
        return v


class InventoryDeductRequest(BaseModel):
    """库存扣减请求"""
    order_id: int
    items: List[DeductItem]

    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError('扣减商品不能为空')
        return v


# ============ 库存调整 Schemas ============

class InventoryAdjustment(BaseModel):
    """库存调整"""
    adjustment_type: AdjustmentType
    quantity: int
    reason: Optional[str] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('调整数量必须大于0')
        return v

    @validator('reason')
    def validate_reason(cls, v):
        if v and len(v) > 500:
            raise ValueError('调整原因最多500个字符')
        return v


class ThresholdUpdate(BaseModel):
    """预警阈值更新"""
    warning_threshold: int

    @validator('warning_threshold')
    def validate_threshold(cls, v):
        if v < 0:
            raise ValueError('预警阈值不能为负数')
        return v


# ============ 库存变动记录 Schemas ============

class InventoryTransactionRead(BaseModel):
    """库存变动记录"""
    id: int
    product_id: int
    transaction_type: TransactionType
    quantity: int
    reference_type: Optional[ReferenceType]
    reference_id: Optional[int]
    reason: Optional[str]
    before_quantity: Optional[int]
    after_quantity: Optional[int]
    operator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionQuery(BaseModel):
    """变动记录查询参数"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    transaction_type: Optional[TransactionType] = None
    page: int = 1
    page_size: int = 20

    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('页码必须大于0')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('每页数量必须在1-100之间')
        return v


# ============ 购物车预占 Schemas ============

class CartReservationRead(BaseModel):
    """购物车预占记录"""
    id: int
    user_id: int
    product_id: int
    reserved_quantity: int
    expires_at: datetime
    created_at: datetime
    is_expired: bool
    remaining_minutes: int

    class Config:
        from_attributes = True


# ============ 管理员查询 Schemas ============

class LowStockQuery(BaseModel):
    """低库存查询参数"""
    page: int = 1
    page_size: int = 20

    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('页码必须大于0')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('每页数量必须在1-100之间')
        return v


class LowStockItem(BaseModel):
    """低库存商品"""
    product_id: int
    product_name: str
    product_sku: str
    available_quantity: int
    warning_threshold: int
    category_name: Optional[str]

    class Config:
        from_attributes = True


# ============ 通用响应 Schemas ============

class InventoryResponse(BaseModel):
    """库存操作响应"""
    code: int
    message: str
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int