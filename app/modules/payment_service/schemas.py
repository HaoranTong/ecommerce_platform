"""
文件名：payment.py
文件路径：app/schemas/payment.py
功能描述：支付和退款相关的Pydantic模式定义
主要功能：
- 支付创建、状态更新、展示模式
- 退款申请、处理、展示模式
- 支付回调和通知处理模式
- 支付统计和分析模式
使用说明：
- 导入：from app.schemas.payment import PaymentCreate, PaymentRead, RefundCreate
- 验证：payment_data = PaymentCreate(**input_data)
- 序列化：payment_response = PaymentRead.model_validate(payment_obj)
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
from app.schemas.base import BaseSchema, TimestampSchema


# ============ 枚举定义 ============

class PaymentStatus(str, Enum):
    """支付状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class RefundStatus(str, Enum):
    """退款状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    ALIPAY = "alipay"
    WECHAT = "wechat"
    BANK_CARD = "bank_card"
    PAYPAL = "paypal"
    CASH = "cash"


# ============ 支付相关模式 ============

class PaymentCreate(BaseSchema):
    """支付创建模式"""
    order_id: int = Field(..., description="订单ID")
    payment_method: str = Field(..., description="支付方式")
    amount: Optional[Decimal] = Field(None, description="支付金额，为空时使用订单金额")
    currency: str = Field("CNY", description="货币类型")
    return_url: Optional[str] = Field(None, description="前端回调URL")
    notify_url: Optional[str] = Field(None, description="后端通知URL")
    description: Optional[str] = Field(None, max_length=1000, description="支付描述")
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        allowed_methods = ['alipay', 'wechat', 'credit_card', 'debit_card', 'bank_transfer', 'cash_on_delivery']
        if v not in allowed_methods:
            raise ValueError(f'支付方式必须是: {", ".join(allowed_methods)}')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('支付金额必须大于0')
        return v


class PaymentUpdate(BaseSchema):
    """支付更新模式"""
    external_payment_id: Optional[str] = Field(None, description="第三方支付ID")
    external_transaction_id: Optional[str] = Field(None, description="第三方交易ID")
    pay_url: Optional[str] = Field(None, description="支付页面URL")
    qr_code: Optional[str] = Field(None, description="支付二维码")
    description: Optional[str] = Field(None, description="支付描述")


class PaymentStatusUpdate(BaseSchema):
    """支付状态更新模式"""
    status: str = Field(..., description="支付状态")
    external_payment_id: Optional[str] = Field(None, description="第三方支付ID")
    external_transaction_id: Optional[str] = Field(None, description="第三方交易ID")
    callback_data: Optional[Dict[str, Any]] = Field(None, description="回调数据")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled', 'expired', 'refunded', 'partial_refunded']
        if v not in allowed_statuses:
            raise ValueError(f'支付状态必须是: {", ".join(allowed_statuses)}')
        return v


class PaymentRead(TimestampSchema):
    """支付展示模式"""
    id: int
    order_id: int
    user_id: int
    payment_no: str
    payment_method: str
    amount: Decimal
    currency: str
    status: str
    external_payment_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    pay_url: Optional[str] = None
    qr_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    description: Optional[str] = None
    
    # 时间节点
    paid_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentDetail(PaymentRead):
    """支付详情模式（包含更多信息）"""
    callback_received_at: Optional[datetime] = None
    payment_data: Optional[Dict[str, Any]] = None
    refunds: List['RefundRead'] = []


class PaymentSearch(BaseSchema):
    """支付搜索模式"""
    payment_no: Optional[str] = Field(None, description="支付单号")
    order_id: Optional[int] = Field(None, description="订单ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    payment_method: Optional[str] = Field(None, description="支付方式")
    status: Optional[str] = Field(None, description="支付状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额")


# ============ 退款相关模式 ============

class RefundCreate(BaseSchema):
    """退款创建模式"""
    amount: Decimal = Field(..., gt=0, description="退款金额")
    reason: str = Field(..., max_length=500, description="退款原因")
    operator_note: Optional[str] = Field(None, max_length=200, description="操作员备注")
    
    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('退款原因至少5个字符')
        return v.strip()


class RefundUpdate(BaseSchema):
    """退款更新模式"""
    external_refund_id: Optional[str] = Field(None, description="第三方退款ID")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="网关响应")
    operator_note: Optional[str] = Field(None, description="操作员备注")


class RefundStatusUpdate(BaseSchema):
    """退款状态更新模式"""
    status: str = Field(..., description="退款状态")
    operator_note: Optional[str] = Field(None, max_length=200, description="操作员备注")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'退款状态必须是: {", ".join(allowed_statuses)}')
        return v


class RefundRead(TimestampSchema):
    """退款展示模式"""
    id: int
    payment_id: int
    refund_no: str
    amount: Decimal
    reason: str
    status: str
    external_refund_id: Optional[str] = None
    operator_id: Optional[int] = None
    operator_note: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RefundDetail(RefundRead):
    """退款详情模式（包含更多信息）"""
    payment: Optional[PaymentRead] = None
    gateway_response: Optional[Dict[str, Any]] = None


# ============ 支付回调模式 ============

class PaymentCallback(BaseSchema):
    """支付回调基础模式"""
    payment_no: str = Field(..., description="支付单号")
    status: str = Field(..., description="支付状态")
    transaction_id: Optional[str] = Field(None, description="第三方交易ID")
    amount: Optional[Decimal] = Field(None, description="支付金额")
    callback_data: Dict[str, Any] = Field(..., description="回调原始数据")


class WechatPaymentCallback(PaymentCallback):
    """微信支付回调模式"""
    out_trade_no: str = Field(..., description="商户订单号")
    transaction_id: str = Field(..., description="微信支付订单号")
    trade_state: str = Field(..., description="交易状态")
    trade_state_desc: str = Field(..., description="交易状态描述")
    bank_type: Optional[str] = Field(None, description="银行类型")
    success_time: Optional[str] = Field(None, description="支付完成时间")


class AlipayCallback(PaymentCallback):
    """支付宝回调模式"""
    out_trade_no: str = Field(..., description="商户订单号")
    trade_no: str = Field(..., description="支付宝交易号")
    trade_status: str = Field(..., description="交易状态")
    total_amount: Decimal = Field(..., description="订单金额")
    gmt_payment: Optional[str] = Field(None, description="交易付款时间")


# ============ 统计分析模式 ============

class PaymentStats(BaseSchema):
    """支付统计模式"""
    total_payments: int
    completed_payments: int
    failed_payments: int
    success_rate: float
    total_amount: Decimal
    payment_methods: List[Dict[str, Any]]


class PaymentTrend(BaseSchema):
    """支付趋势模式"""
    date: str
    payment_count: int
    payment_amount: Decimal
    success_count: int
    success_amount: Decimal
    success_rate: float


class PaymentAnalysis(BaseSchema):
    """支付分析模式"""
    period: Dict[str, str]  # 统计周期
    summary: PaymentStats   # 汇总统计
    trends: List[PaymentTrend]  # 趋势数据
    top_methods: List[Dict[str, Any]]  # 热门支付方式
    hourly_distribution: List[Dict[str, Any]]  # 小时分布


# ============ 批量操作模式 ============

class PaymentBatch(BaseSchema):
    """支付批量操作模式"""
    payment_ids: List[int] = Field(..., min_items=1, description="支付ID列表")
    action: str = Field(..., pattern="^(export|cancel|retry)$", description="操作类型")
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")


class RefundBatch(BaseSchema):
    """退款批量操作模式"""
    refund_ids: List[int] = Field(..., min_items=1, description="退款ID列表")
    action: str = Field(..., pattern="^(approve|reject|process)$", description="操作类型")
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")