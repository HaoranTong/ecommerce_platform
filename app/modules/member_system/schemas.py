"""
会员系统模块的Pydantic数据模式定义

遵循四层架构设计，定义所有数据模式用于API接口、数据验证和序列化。
严格按照 design.md 文档要求，提供完整的数据类型定义。
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# 泛型类型变量
T = TypeVar('T')


# ================== 枚举类型定义 ==================


class MemberLevelCode(str, Enum):
    """会员等级代码枚举"""
    BASIC = "BASIC"  # 注册会员
    BRONZE = "BRONZE"  # 铜牌会员
    SILVER = "SILVER"  # 银牌会员
    GOLD = "GOLD"  # 金牌会员
    DIAMOND = "DIAMOND"  # 钻石会员


class PointTransactionType(str, Enum):
    """积分交易类型枚举"""
    EARN = "earn"  # 获得积分
    USE = "use"  # 使用积分
    EXPIRED = "expired"  # 积分过期
    REFUND = "refund"  # 积分退回


class PointReferenceType(str, Enum):
    """积分关联业务类型枚举"""
    ORDER = "order"  # 订单消费
    REVIEW = "review"  # 商品评价
    SIGNIN = "signin"  # 签到
    ACTIVITY = "activity"  # 活动奖励
    MANUAL = "manual"  # 手动调整
    REFUND = "refund"  # 退款返还


# ================== 基础模式定义 ==================


class BaseConfigModel(BaseModel):
    """基础配置模型"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }
    )


# ================== 会员等级相关模式 ==================


class MemberLevelBase(BaseConfigModel):
    """会员等级基础模式"""
    level_name: str = Field(..., description="等级名称")
    level_code: MemberLevelCode = Field(..., description="等级代码")
    min_points: int = Field(ge=0, description="最低积分要求")
    discount_rate: Decimal = Field(ge=0, le=1, description="折扣率")
    point_multiplier: Decimal = Field(ge=1, description="积分倍率")
    benefits: Optional[Dict[str, Any]] = Field(default=None, description="等级权益")


class MemberLevelRead(MemberLevelBase):
    """会员等级读取模式"""
    id: int = Field(..., description="等级ID")
    is_active: bool = Field(True, description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ================== 会员档案相关模式 ==================


class MemberProfileCreate(BaseConfigModel):
    """创建会员档案请求模式"""
    nickname: str = Field(..., min_length=1, max_length=50, description="会员昵称")
    birthday: Optional[date] = Field(default=None, description="生日")
    gender: Optional[str] = Field(default=None, pattern=r"^(M|F|U)$", description="性别")
    phone: Optional[str] = Field(default=None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="偏好设置")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nickname": "张三",
                    "birthday": "1990-01-15",
                    "gender": "M",
                    "phone": "13800138000",
                    "preferences": {
                        "notification_enabled": True,
                        "marketing_enabled": False
                    }
                }
            ]
        }
    )


class MemberProfileUpdate(BaseConfigModel):
    """更新会员档案请求模式"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="会员昵称")
    birthday: Optional[date] = Field(default=None, description="生日")
    gender: Optional[str] = Field(default=None, pattern=r"^(M|F|U)$", description="性别")
    phone: Optional[str] = Field(default=None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="偏好设置")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nickname": "李四",
                    "birthday": "1992-05-20",
                    "preferences": {
                        "notification_enabled": False
                    }
                }
            ]
        }
    )


class MemberStatistics(BaseConfigModel):
    """会员统计信息模式"""
    total_spent: Decimal = Field(ge=0, description="总消费金额")
    join_date: date = Field(..., description="加入日期")
    last_active: Optional[datetime] = Field(default=None, description="最后活跃时间")


class MemberLevel(BaseConfigModel):
    """会员等级信息模式"""
    level_id: int = Field(..., description="等级ID")
    level_name: str = Field(..., description="等级名称")
    min_points: int = Field(ge=0, description="最低积分要求")
    discount_rate: Decimal = Field(ge=0, le=1, description="折扣率")


class MemberPoints(BaseConfigModel):
    """会员积分信息模式"""
    total_earned: int = Field(ge=0, description="累计获得积分")
    current_points: int = Field(ge=0, description="当前可用积分")
    total_used: int = Field(ge=0, description="累计使用积分")
    frozen_points: int = Field(ge=0, description="冻结积分")


class MemberBenefits(BaseConfigModel):
    """会员权益模式"""
    free_shipping: bool = Field(default=False, description="免运费")
    birthday_gift: bool = Field(default=False, description="生日礼品")
    priority_service: bool = Field(default=False, description="优先客服")
    exclusive_events: bool = Field(default=False, description="专属活动")
    points_multiplier: bool = Field(default=False, description="积分倍率")
    custom_service: bool = Field(default=False, description="定制服务")


class MemberProfileRead(BaseConfigModel):
    """会员档案读取模式"""
    member_id: str = Field(..., description="会员ID")
    user_id: int = Field(..., description="用户ID")
    level: MemberLevel = Field(..., description="等级信息")
    points: MemberPoints = Field(..., description="积分信息")
    statistics: MemberStatistics = Field(..., description="统计信息")
    benefits: MemberBenefits = Field(..., description="权益信息")


# ================== 积分相关模式 ==================


class PointTransactionCreate(BaseConfigModel):
    """创建积分交易请求模式"""
    points: int = Field(gt=0, description="积分数量")
    reference_id: Optional[str] = Field(default=None, description="关联业务ID")
    reference_type: PointReferenceType = Field(default=PointReferenceType.MANUAL, description="关联业务类型")
    description: str = Field(..., min_length=1, max_length=200, description="交易描述")


class PointEarnRequest(BaseConfigModel):
    """积分获得请求模式"""
    points: int = Field(gt=0, description="积分数量")
    reference_id: Optional[str] = Field(default=None, description="关联业务ID")
    reference_type: PointReferenceType = Field(default=PointReferenceType.MANUAL, description="关联业务类型")
    description: str = Field(default="积分获得", description="交易描述")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            return "积分获得"
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "points": 100,
                    "reference_id": "ORDER-20250123001",
                    "reference_type": "purchase",
                    "description": "订单消费获得积分"
                }
            ]
        }
    )


class PointUseRequest(BaseConfigModel):
    """积分使用请求模式"""
    points: int = Field(gt=0, description="积分数量")
    reference_id: Optional[str] = Field(default=None, description="关联业务ID")
    reference_type: PointReferenceType = Field(default=PointReferenceType.MANUAL, description="关联业务类型")
    description: str = Field(default="积分使用", description="交易描述")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            return"积分使用"
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "points": 50,
                    "reference_id": "REDEEM-20250123001",
                    "reference_type": "redemption",
                    "description": "积分兑换商品"
                }
            ]
        }
    )


class PointTransactionRead(BaseConfigModel):
    """积分交易读取模式"""
    id: int = Field(..., description="交易ID")
    user_id: int = Field(..., description="用户ID")
    transaction_type: PointTransactionType = Field(..., description="交易类型")
    points_change: int = Field(..., description="积分变动")
    balance_after: int = Field(ge=0, description="交易后余额")
    reference_id: Optional[str] = Field(default=None, description="关联业务ID")
    reference_type: PointReferenceType = Field(..., description="关联业务类型")
    description: str = Field(..., description="交易描述")
    transaction_date: datetime = Field(..., description="交易时间")


class PointBalanceRead(BaseConfigModel):
    """积分余额读取模式"""
    current_points: int = Field(ge=0, description="当前可用积分")
    total_earned: int = Field(ge=0, description="累计获得积分")
    total_used: int = Field(ge=0, description="累计使用积分")


class PointTransactionListRead(BaseConfigModel):
    """积分交易列表读取模式"""
    transactions: List[PointTransactionRead] = Field(..., description="交易记录列表")
    total_count: int = Field(ge=0, description="总记录数")
    has_more: bool = Field(..., description="是否还有更多记录")


# ================== 查询参数模式 ==================


class PointTransactionQuery(BaseConfigModel):
    """积分交易查询参数模式"""
    transaction_type: Optional[PointTransactionType] = Field(default=None, description="交易类型过滤")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    limit: int = Field(default=20, ge=1, le=100, description="每页数量")
    offset: int = Field(default=0, ge=0, description="偏移量")

    @model_validator(mode='after')
    def validate_date_range(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("开始日期不能晚于结束日期")
        return self


# ================== 响应元数据模式 ==================


class ResponseMeta(BaseConfigModel):
    """响应元数据模式 - 符合API标准"""
    success: bool = Field(default=True, description="是否成功")
    message: Optional[str] = Field(default=None, description="提示信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    request_id: Optional[str] = Field(default=None, description="请求追踪ID")


# ================== 标准响应模式定义 ==================


class StandardResponse(BaseConfigModel, Generic[T]):
    """标准响应基类 - 符合API设计标准"""
    data: Optional[T] = Field(None, description="响应数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class MemberResponse(BaseConfigModel):
    """会员操作响应模式"""
    data: Optional[MemberProfileRead] = Field(default=None, description="会员数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class PointTransactionResponse(BaseConfigModel):
    """积分交易响应模式"""
    data: Optional[PointTransactionRead] = Field(default=None, description="交易数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class PointBalanceResponse(BaseConfigModel):
    """积分余额响应模式"""
    data: Optional[PointBalanceRead] = Field(default=None, description="余额数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class PointTransactionListResponse(BaseConfigModel):
    """积分交易列表响应模式"""
    data: Optional[PointTransactionListRead] = Field(default=None, description="交易列表数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class LevelListResponse(BaseConfigModel):
    """等级列表响应模式"""
    data: Optional[List[MemberLevelRead]] = Field(default=None, description="等级列表数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


# ================== 权益相关模式 ==================


class BenefitRead(BaseConfigModel):
    """单个权益展示模式"""
    type: str = Field(..., description="权益类型")
    name: str = Field(..., description="权益名称")
    description: Optional[str] = Field(default="", description="权益描述")
    enabled: bool = Field(default=True, description="是否启用")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="权益配置")


class MemberBenefitsRead(BaseConfigModel):
    """会员权益完整展示模式"""
    level_id: int = Field(..., description="等级ID")
    level_name: str = Field(..., description="等级名称")
    discount_rate: float = Field(..., description="折扣率")
    benefits: List[BenefitRead] = Field(default_factory=list, description="权益列表")
    special_privileges: List[str] = Field(default_factory=list, description="特殊特权")


class LevelBenefitsRead(BaseConfigModel):
    """等级权益展示模式"""
    level_id: int = Field(..., description="等级ID")
    level_name: str = Field(..., description="等级名称")
    discount_rate: float = Field(..., description="折扣率")
    min_points: int = Field(..., description="所需最低积分")
    benefits: List[BenefitRead] = Field(default_factory=list, description="权益列表")


class BenefitEligibilityRead(BaseConfigModel):
    """权益资格检查结果模式"""
    eligible: bool = Field(..., description="是否有资格")
    benefit_type: str = Field(..., description="权益类型")
    reason: Optional[str] = Field(default=None, description="不符合资格的原因")
    benefit_info: Optional[Dict[str, Any]] = Field(default=None, description="权益详情")
    level_name: Optional[str] = Field(default=None, description="会员等级名称")


class BenefitsResponse(BaseConfigModel):
    """权益响应模式"""
    data: Optional[MemberBenefitsRead] = Field(default=None, description="权益数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class LevelBenefitsResponse(BaseConfigModel):
    """等级权益响应模式"""
    data: Optional[LevelBenefitsRead] = Field(default=None, description="等级权益数据")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


class BenefitEligibilityResponse(BaseConfigModel):
    """权益资格检查响应模式"""
    data: Optional[BenefitEligibilityRead] = Field(default=None, description="资格检查结果")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


# ================== 错误响应模式 ==================


class ErrorDetail(BaseConfigModel):
    """错误详情模式"""
    field: Optional[str] = Field(default=None, description="错误字段")
    message: str = Field(..., description="错误消息")
    code: Optional[str] = Field(default=None, description="业务错误码")


class ErrorResponse(BaseConfigModel):
    """错误响应模式 - 符合API标准"""
    error: Dict[str, Any] = Field(..., description="错误信息")
    meta: ResponseMeta = Field(default_factory=ResponseMeta, description="响应元数据")


# ================== 导出模式列表 ==================

__all__ = [
    # 枚举
    "MemberLevelCode",
    "PointTransactionType", 
    "PointReferenceType",
    
    # 等级相关
    "MemberLevelBase",
    "MemberLevelRead",
    
    # 会员档案相关
    "MemberProfileCreate",
    "MemberProfileUpdate",
    "MemberProfileRead",
    "MemberStatistics",
    "MemberLevel",
    "MemberPoints",
    "MemberBenefits",
    
    # 积分相关
    "PointTransactionCreate",
    "PointEarnRequest",
    "PointUseRequest", 
    "PointTransactionRead",
    "PointBalanceRead",
    "PointTransactionListRead",
    
    # 查询参数
    "PointTransactionQuery",
    
    # 响应模式
    "ResponseMeta",
    "StandardResponse",
    "MemberResponse",
    "PointTransactionResponse",
    "PointBalanceResponse", 
    "PointTransactionListResponse",
    "LevelListResponse",
    "ErrorResponse",
    "ErrorDetail",
]
