"""
文件名：schemas.py
文件路径：app/modules/inventory_management/schemas.py
功能描述：库存管理模块的Pydantic Schema定义

主要功能：
- 定义API请求和响应的数据模型
- 提供数据验证和序列化功能
- 支持批量操作和复杂业务场景
- 基于SKU的库存管理接口设计

使用说明：
- 导入：from app.modules.inventory_management.schemas import InventoryRead, ReserveRequest
- API接口：用于FastAPI路由的请求/响应验证
- 数据验证：自动进行输入数据验证和格式化

依赖模块：
- pydantic.BaseModel: 基础Schema类
- typing: 类型注解支持
- datetime: 时间数据处理

Schema分类：
- Read Schemas: 用于API响应的数据输出
- Create/Update Schemas: 用于API请求的数据输入
- Query Schemas: 用于复杂查询和批量操作

创建时间：2025-09-15
最后修改：2025-09-15
"""

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class TransactionTypeEnum(str, Enum):
    """库存变动类型"""
    RESERVE = "reserve"
    RELEASE = "release"  
    DEDUCT = "deduct"
    ADJUST = "adjust"
    RESTOCK = "restock"


class ReservationTypeEnum(str, Enum):
    """预占类型"""
    CART = "cart"
    ORDER = "order"


class AdjustmentTypeEnum(str, Enum):
    """调整类型"""
    INCREASE = "increase"
    DECREASE = "decrease"
    SET = "set"


# ============ 基础 Schemas ============

class SKUInventoryBase(BaseModel):
    """SKU库存基础信息"""
    sku_id: str = Field(..., description="SKU唯一标识符")
    available_quantity: int = Field(ge=0, description="可用库存数量")
    reserved_quantity: int = Field(ge=0, description="预占库存数量") 
    total_quantity: int = Field(ge=0, description="总库存数量")
    warning_threshold: int = Field(ge=0, description="库存预警阈值")
    critical_threshold: int = Field(ge=0, description="库存严重不足阈值")


class SKUInventoryCreate(BaseModel):
    """创建SKU库存"""
    sku_id: str = Field(..., description="SKU ID")
    initial_quantity: int = Field(ge=0, description="初始库存数量")
    warning_threshold: int = Field(default=10, ge=0, description="库存预警阈值")
    critical_threshold: int = Field(default=5, ge=0, description="库存严重不足阈值")


class SKUInventoryUpdate(BaseModel):
    """更新SKU库存配置"""
    warning_threshold: Optional[int] = Field(None, ge=0, description="库存预警阈值")
    critical_threshold: Optional[int] = Field(None, ge=0, description="库存严重不足阈值")
    is_active: Optional[bool] = Field(None, description="是否启用库存管理")


class SKUInventoryRead(SKUInventoryBase):
    """SKU库存读取响应"""
    id: int
    is_low_stock: bool = Field(description="是否库存不足")
    is_critical_stock: bool = Field(description="是否库存严重不足")
    is_out_of_stock: bool = Field(description="是否缺货")
    is_active: bool = Field(description="是否启用库存管理")
    last_updated: datetime = Field(description="最后更新时间")

    class Config:
        from_attributes = True


# ============ 批量操作 Schemas ============

class BatchInventoryQuery(BaseModel):
    """批量库存查询"""
    sku_ids: List[str] = Field(..., description="SKU ID列表")

    @validator('sku_ids')
    def validate_sku_ids(cls, v):
        if not v:
            raise ValueError('sku_ids不能为空')
        if len(v) > 100:
            raise ValueError('一次最多查询100个SKU')
        return list(set(v))  # 去重


class SKUInventorySimple(BaseModel):
    """简化的SKU库存信息"""
    sku_id: str
    available_quantity: int
    reserved_quantity: int
    total_quantity: int
    is_low_stock: bool

    class Config:
        from_attributes = True


# ============ 库存预占 Schemas ============

class ReservationItem(BaseModel):
    """预占商品项"""
    sku_id: str = Field(..., description="SKU ID")
    quantity: int = Field(gt=0, description="预占数量")


class ReserveRequest(BaseModel):
    """库存预占请求"""
    reservation_type: ReservationTypeEnum = Field(..., description="预占类型")
    reference_id: str = Field(..., description="关联ID（用户ID或订单ID）")
    items: List[ReservationItem] = Field(..., description="预占商品列表")
    expires_minutes: int = Field(default=30, ge=1, le=1440, description="预占有效期（分钟）")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('items不能为空')
        if len(v) > 50:
            raise ValueError('一次最多预占50个SKU')
        return v


class ReservationItemResponse(BaseModel):
    """预占商品响应项"""
    sku_id: str
    reserved_quantity: int
    available_after_reserve: int


class ReservationResponse(BaseModel):
    """预占响应"""
    reservation_id: str
    expires_at: datetime
    reserved_items: List[ReservationItemResponse]


class ReleaseReservationRequest(BaseModel):
    """释放预占请求"""
    reservation_id: Optional[str] = Field(None, description="预占记录ID")
    user_id: Optional[str] = Field(None, description="用户ID（释放该用户所有预占）")


# ============ 库存操作 Schemas ============

class DeductItem(BaseModel):
    """扣减商品项"""
    sku_id: str = Field(..., description="SKU ID")
    quantity: int = Field(gt=0, description="扣减数量")
    reservation_id: Optional[str] = Field(None, description="对应的预占记录ID")


class InventoryDeductRequest(BaseModel):
    """库存扣减请求"""
    order_id: str = Field(..., description="订单ID")
    items: List[DeductItem] = Field(..., description="扣减商品列表")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('items不能为空')
        return v


class DeductItemResponse(BaseModel):
    """扣减响应项"""
    sku_id: str
    deducted_quantity: int
    remaining_quantity: int


class DeductResponse(BaseModel):
    """扣减响应"""
    order_id: str
    deducted_items: List[DeductItemResponse]


class InventoryAdjustment(BaseModel):
    """库存调整请求"""
    sku_id: str = Field(..., description="SKU ID")
    adjustment_type: AdjustmentTypeEnum = Field(..., description="调整类型")
    quantity: int = Field(gt=0, description="调整数量")
    reason: str = Field(..., description="调整原因")
    reference: Optional[str] = Field(None, description="参考单号")


class AdjustmentResponse(BaseModel):
    """调整响应"""
    sku_id: str
    old_quantity: int
    new_quantity: int
    adjustment_quantity: int
    transaction_id: str


# ============ 库存管理 Schemas ============

class ThresholdUpdate(BaseModel):
    """阈值更新请求"""
    warning_threshold: int = Field(ge=0, description="库存预警阈值")
    critical_threshold: int = Field(ge=0, description="库存严重不足阈值")

    @validator('critical_threshold')
    def validate_thresholds(cls, v, values):
        if 'warning_threshold' in values and v > values['warning_threshold']:
            raise ValueError('critical_threshold不能大于warning_threshold')
        return v


class LowStockItem(BaseModel):
    """低库存商品项"""
    sku_id: str
    current_quantity: int
    warning_threshold: int
    critical_threshold: int
    level: str = Field(description="预警级别: warning/critical")

    class Config:
        from_attributes = True


class LowStockQuery(BaseModel):
    """低库存查询参数"""
    level: Optional[str] = Field("warning", description="预警级别")
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============ 历史记录 Schemas ============

class InventoryTransactionRead(BaseModel):
    """库存变动记录"""
    transaction_id: str
    sku_id: str
    transaction_type: TransactionTypeEnum
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reason: Optional[str]
    reference: Optional[str]
    operator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionQuery(BaseModel):
    """变动记录查询参数"""
    sku_ids: Optional[List[str]] = Field(None, description="SKU ID列表")
    transaction_types: Optional[List[TransactionTypeEnum]] = Field(None, description="变动类型列表")
    operator_id: Optional[int] = Field(None, description="操作人ID")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TransactionSearchResponse(BaseModel):
    """变动记录搜索响应"""
    sku_id: str
    total: int
    logs: List[InventoryTransactionRead]


# ============ 系统维护 Schemas ============

class CleanupResponse(BaseModel):
    """清理过期预占响应"""
    cleaned_reservations: int
    released_quantity: int


class ConsistencyCheckItem(BaseModel):
    """一致性检查项"""
    sku_id: str
    issue: str
    suggested_action: str


class ConsistencyCheckResponse(BaseModel):
    """一致性检查响应"""
    total_skus: int
    inconsistent_skus: int
    details: List[ConsistencyCheckItem]


# ============ 通用响应 Schemas ============

class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    items: List[Union[SKUInventoryRead, LowStockItem, InventoryTransactionRead]]
    page: int
    page_size: int
    total_pages: int


class APIResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(default=200)
    message: str = Field(default="成功")
    data: Optional[Union[dict, list]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ 错误响应 Schemas ============

class ErrorDetail(BaseModel):
    """错误详情"""
    sku_id: Optional[str] = None
    requested: Optional[int] = None
    available: Optional[int] = None
    message: str


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    error_code: str
    details: Optional[ErrorDetail] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============ 事件通知 Schemas ============

class InventoryEvent(BaseModel):
    """库存变动事件"""
    event_type: str = Field(description="事件类型")
    event_id: str = Field(description="事件ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    data: dict = Field(description="事件数据")


class StockReservedEvent(BaseModel):
    """库存预占事件"""
    sku_id: str
    quantity: int
    reservation_id: str
    user_id: Optional[str] = None


class StockReleasedEvent(BaseModel):
    """库存释放事件"""
    sku_id: str
    quantity: int
    reservation_id: str


class StockDeductedEvent(BaseModel):
    """库存扣减事件"""
    sku_id: str
    quantity: int
    order_id: str


class StockAdjustedEvent(BaseModel):
    """库存调整事件"""
    sku_id: str
    old_quantity: int
    new_quantity: int
    adjustment_type: AdjustmentTypeEnum
    operator_id: int


class LowStockWarningEvent(BaseModel):
    """库存不足预警事件"""
    sku_id: str
    current_quantity: int
    threshold: int
    level: str  # warning/critical