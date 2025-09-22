"""
订单管理模块数据模式定义

根据 docs/design/modules/order-management/api-spec.md 规范实现
符合API设计标准和模块化架构原则

主要模式:
- API响应格式：统一的成功/失败响应结构
- 订单相关模式：创建、更新、查询、展示模式
- 订单项相关模式：Product+SKU双重关联模式
- 订单状态历史：状态变更审计模式
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union, Generic, TypeVar

T = TypeVar('T')
from datetime import datetime
from decimal import Decimal
from enum import Enum

# ============ 基础模式类 ============
# 模块内独立定义，遵循API设计标准避免跨模块依赖

class BaseSchema(BaseModel):
    """订单管理模块基础模式类"""
    model_config = ConfigDict(from_attributes=True)
        
class TimestampMixin(BaseModel):
    """时间戳混入类"""
    created_at: datetime
    updated_at: datetime


# ============ 统一API响应格式 ============

class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式，符合api-standards.md规范"""
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None
    metadata: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    items: List[T] = Field(default_factory=list, description="数据项列表")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    total_count: int = Field(default=0, ge=0, description="总数据量")
    
    @property
    def total_pages(self) -> int:
        """计算总页数"""
        if self.page_size <= 0:
            return 0
        return (self.total_count + self.page_size - 1) // self.page_size
    
    @property 
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages
        
    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1


# ============ 枚举定义 ============

class OrderStatus(str, Enum):
    """订单状态枚举，符合design.md状态流转设计"""
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    SHIPPED = "shipped"     # 已发货  
    DELIVERED = "delivered" # 已送达
    CANCELLED = "cancelled" # 已取消
    RETURNED = "returned"   # 已退货


# ============ 订单项相关模式 ============

class OrderItemRequest(BaseSchema):
    """订单项创建请求模式，支持Product+SKU双重关联"""
    product_id: int = Field(..., gt=0, description="商品ID")
    sku_id: int = Field(..., gt=0, description="SKU ID")
    quantity: int = Field(..., gt=0, le=999, description="购买数量")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('商品数量必须大于0')
        if v > 999:
            raise ValueError('单个商品数量不能超过999')
        return v

class OrderItemResponse(BaseSchema):
    """订单项响应模式，包含商品快照信息"""
    id: int
    order_id: int
    product_id: int
    sku_id: int
    
    # 商品快照信息
    sku_code: str
    product_name: str
    sku_name: str
    
    # 数量和价格
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ 收货地址相关模式 ============

class ShippingAddressRequest(BaseSchema):
    """收货地址请求模式"""
    recipient: str = Field(..., max_length=100, description="收货人")
    phone: str = Field(..., max_length=20, description="联系电话")
    address: str = Field(..., max_length=500, description="详细地址")

class ShippingAddressResponse(ShippingAddressRequest):
    """收货地址响应模式"""
    pass


# ============ 订单相关模式 ============

class OrderCreateRequest(BaseSchema):
    """订单创建请求模式，符合api-spec.md规范"""
    items: List[OrderItemRequest] = Field(..., min_length=1, max_length=50, description="订单商品列表")
    shipping_address: ShippingAddressRequest = Field(..., description="收货地址")
    notes: Optional[str] = Field(None, max_length=500, description="订单备注")
    
    @field_validator('items')
    @classmethod
    def validate_items_unique(cls, v):
        """验证订单不能包含重复的SKU"""
        sku_ids = [item.sku_id for item in v]
        if len(sku_ids) != len(set(sku_ids)):
            raise ValueError('订单不能包含重复的SKU')
        return v

class OrderStatusUpdateRequest(BaseSchema):
    """订单状态更新请求模式"""
    status: OrderStatus = Field(..., description="订单状态")
    remark: Optional[str] = Field(None, max_length=500, description="状态变更备注")

class OrderCancelRequest(BaseSchema):
    """订单取消请求模式"""
    reason: Optional[str] = Field(None, max_length=500, description="取消原因")


class OrderResponse(BaseSchema, TimestampMixin):
    """订单响应模式，符合design.md数据模型"""
    id: int
    order_number: str  # 统一使用order_number
    user_id: int
    status: OrderStatus
    
    # 金额信息
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    
    # 收货信息
    shipping_address: Optional[str] = None
    shipping_method: str = "standard"
    
    # 备注信息
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class OrderDetailResponse(OrderResponse):
    """订单详情响应模式，包含订单项和状态历史"""
    items: List[OrderItemResponse] = []
    status_history: List['OrderStatusHistoryResponse'] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderListQueryParams(BaseSchema):
    """订单列表查询参数"""
    status: Optional[OrderStatus] = Field(None, description="订单状态筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    start_date: Optional[str] = Field(None, description="开始日期(YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期(YYYY-MM-DD)")
# ============ 订单状态历史相关模式 ============

class OrderStatusHistoryResponse(BaseSchema):
    """订单状态历史响应模式"""
    id: int
    order_id: int
    old_status: Optional[str]
    new_status: str
    remark: Optional[str] = None
    operator_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ 错误响应模式 ============

class OrderErrorDetail(BaseSchema):
    """订单错误详情"""
    type: str
    details: List[Dict[str, Any]] = []

class OrderErrorResponse(BaseModel):
    """订单错误响应模式"""
    success: bool = False
    code: int
    message: str
    error: Optional[OrderErrorDetail] = None
    metadata: Optional[Dict[str, Any]] = None


# ============ 分页数据模式 ============

class PaginationInfo(BaseModel):
    """分页信息模式"""
    page: int
    page_size: int
    total_pages: int
    total_items: int
    has_next: bool
    has_prev: bool

class OrderListResponse(BaseModel):
    """订单列表响应模式"""
    success: bool = True
    code: int = 200
    message: str = "查询成功"
    data: Dict[str, Any] = Field(default_factory=lambda: {
        "items": [],
        "pagination": {}
    })
    metadata: Optional[Dict[str, Any]] = None


class OrderStatisticsResponse(BaseModel):
    """订单统计响应模式"""
    total_orders: int = Field(description="订单总数")
    pending_orders: int = Field(description="待支付订单数")
    paid_orders: int = Field(description="已支付订单数")
    shipped_orders: int = Field(description="已发货订单数")
    delivered_orders: int = Field(description="已送达订单数")
    cancelled_orders: int = Field(description="已取消订单数")
    returned_orders: int = Field(description="已退货订单数")
    total_amount: float = Field(description="订单总金额")
    completion_rate: float = Field(description="订单完成率（%）")
    cancellation_rate: float = Field(description="订单取消率（%）")


# 解决前向引用问题
OrderDetailResponse.model_rebuild()