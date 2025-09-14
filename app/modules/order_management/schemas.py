"""
文件名：order.py
文件路径：app/schemas/order.py
功能描述：订单和购物车相关的Pydantic模式定义
主要功能：
- 订单创建、更新、展示模式
- 订单项管理模式
- 购物车操作和展示模式
- 订单状态流转和统计模式
使用说明：
- 导入：from app.schemas.order import OrderCreate, OrderRead, CartItemAdd
- 验证：order_data = OrderCreate(**input_data)
- 序列化：order_response = OrderRead.model_validate(order_obj)
依赖模块：
- app.schemas.base: 基础模式类
- pydantic: 数据验证和字段定义
- decimal: 金额字段类型
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

# 模块内独立定义基础schemas，遵循模块化单体架构原则
class BaseSchema(BaseModel):
    """订单管理模块基础模式类"""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class TimestampSchema(BaseSchema):
    """包含时间戳的基础模式"""
    created_at: datetime
    updated_at: datetime


# ============ 枚举定义 ============

class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


# ============ 订单项相关模式 ============

class OrderItemCreate(BaseSchema):
    """订单项创建模式"""
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., gt=0, le=999, description="购买数量")
    unit_price: Optional[Decimal] = Field(None, description="单价（可选，默认使用商品当前价格）")


class OrderItemRead(BaseSchema):
    """订单项展示模式"""
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    
    class Config:
        from_attributes = True


# ============ 订单相关模式 ============

class OrderCreate(BaseSchema):
    """订单创建模式"""
    items: List[OrderItemCreate] = Field(..., min_items=1, description="订单商品列表")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    shipping_method: Optional[str] = Field("standard", description="配送方式")
    notes: Optional[str] = Field(None, max_length=500, description="订单备注")
    
    @field_validator('items')
    @classmethod
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError('订单必须包含至少一个商品')
        return v


class OrderUpdate(BaseSchema):
    """订单更新模式"""
    shipping_address: Optional[str] = Field(None, description="收货地址")
    shipping_method: Optional[str] = Field(None, description="配送方式")
    notes: Optional[str] = Field(None, max_length=500, description="订单备注")


class OrderStatusUpdate(BaseSchema):
    """订单状态更新模式"""
    status: str = Field(..., pattern="^(pending|paid|shipped|delivered|cancelled|returned)$", description="订单状态")
    note: Optional[str] = Field(None, max_length=200, description="状态变更备注")


class OrderRead(TimestampSchema):
    """订单展示模式"""
    id: int
    order_no: str
    user_id: int
    status: str
    total_amount: Decimal
    shipping_address: Optional[str] = None
    shipping_method: str
    notes: Optional[str] = None
    
    # 时间节点
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    # 关联数据
    items: List[OrderItemRead] = []
    
    class Config:
        from_attributes = True


class OrderDetail(OrderRead):
    """订单详情模式（包含更多信息）"""
    subtotal: Decimal = Field(default=0, description="商品小计")
    shipping_fee: Decimal = Field(default=0, description="运费")
    discount_amount: Decimal = Field(default=0, description="优惠金额")
    remark: Optional[str] = None  # 内部备注


class OrderSearch(BaseSchema):
    """订单搜索模式"""
    order_no: Optional[str] = Field(None, description="订单号")
    user_id: Optional[int] = Field(None, description="用户ID")
    status: Optional[str] = Field(None, description="订单状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额")


class OrderStats(BaseSchema):
    """订单统计模式"""
    total_orders: int
    pending_orders: int
    completed_orders: int
    cancelled_orders: int
    total_amount: Decimal
    average_order_value: Decimal


# ============ 购物车相关模式 ============

class CartItemAdd(BaseSchema):
    """购物车添加商品模式"""
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., gt=0, le=99, description="添加数量（1-99）")


# 为了兼容性，创建别名
CartItemCreate = CartItemAdd


class CartItemUpdate(BaseSchema):
    """购物车商品更新模式"""
    quantity: int = Field(..., ge=0, le=99, description="更新数量（0表示删除）")


class CartItemRead(BaseSchema):
    """购物车商品展示模式"""
    product_id: int
    product_name: str
    product_sku: str
    price: Decimal
    quantity: int
    subtotal: Decimal  # 小计
    stock_quantity: int  # 库存数量
    image_url: Optional[str] = None
    is_available: bool = True  # 是否可购买
    
    class Config:
        from_attributes = True


class CartSummary(BaseSchema):
    """购物车摘要模式"""
    user_id: int
    items: List[CartItemRead]
    total_items: int  # 商品种类数
    total_quantity: int  # 总数量
    total_amount: Decimal  # 总金额


# 为了兼容性，创建别名
CartRead = CartSummary


class CartValidation(BaseSchema):
    """购物车验证结果模式"""
    can_checkout: bool
    errors: List[str] = []
    warnings: List[str] = []
    total_amount: Decimal
    available_items: int
    unavailable_items: int


class CartMerge(BaseSchema):
    """购物车合并模式（游客转用户）"""
    guest_cart_items: List[CartItemAdd] = Field(..., description="游客购物车商品列表")


# ============ 批量操作模式 ============

class OrderBatch(BaseSchema):
    """订单批量操作模式"""
    order_ids: List[int] = Field(..., min_items=1, description="订单ID列表")
    action: str = Field(..., pattern="^(export|print|update_status|cancel)$", description="操作类型")
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")


class OrderExport(BaseSchema):
    """订单导出模式"""
    format: str = Field("excel", pattern="^(excel|csv|pdf)$", description="导出格式")
    fields: Optional[List[str]] = Field(None, description="导出字段")
    filters: Optional[OrderSearch] = Field(None, description="筛选条件")


class OrderSummary(BaseSchema):
    """订单摘要模式"""
    id: int
    order_number: str
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    item_count: int
    customer_name: Optional[str] = None