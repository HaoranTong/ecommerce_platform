"""
文件名：schemas.py
文件路径：app/modules/member_system/schemas.py
功能描述：会员系统模块的Pydantic数据模式定义
主要功能：
- 会员信息的创建、更新、读取模式
- 积分交易和统计的数据模式
- 会员权益和活动的数据模式
- API请求响应的数据验证和序列化
使用说明：
- 导入：from app.modules.member_system.schemas import MemberCreate, MemberRead
- 数据验证：自动进行类型检查和格式验证
- API序列化：FastAPI自动生成API文档和响应格式
- 嵌套模式：支持复杂对象的嵌套和关联
依赖模块：
- pydantic: 数据验证和序列化
- typing: 类型提示支持
- datetime: 日期时间处理
- decimal: 精确数值计算
创建时间：2024-09-17
最后修改：2024-09-17
"""

# 标准库
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal
from enum import Enum

# 第三方库
from pydantic import BaseModel, Field, validator, root_validator


# ================== 枚举类型定义 ==================

class MemberLevelCode(str, Enum):
    """会员等级代码枚举"""
    BASIC = "BASIC"      # 注册会员
    BRONZE = "BRONZE"    # 铜牌会员
    SILVER = "SILVER"    # 银牌会员
    GOLD = "GOLD"        # 金牌会员
    DIAMOND = "DIAMOND"  # 钻石会员


class TransactionType(str, Enum):
    """积分交易类型枚举"""
    EARN = "EARN"    # 获得积分
    USE = "USE"      # 使用积分


class EventType(str, Enum):
    """积分事件类型枚举"""
    PURCHASE = "PURCHASE"         # 购物获得
    REGISTER = "REGISTER"         # 注册奖励
    ACTIVITY = "ACTIVITY"         # 活动奖励
    REDEMPTION = "REDEMPTION"     # 积分兑换
    REFUND = "REFUND"            # 退款返还
    BIRTHDAY = "BIRTHDAY"         # 生日奖励
    INVITE = "INVITE"            # 邀请奖励
    REVIEW = "REVIEW"            # 评价奖励


class BenefitType(str, Enum):
    """权益类型枚举"""
    FREE_SHIPPING = "free_shipping"       # 免运费
    BIRTHDAY_GIFT = "birthday_gift"       # 生日礼品
    PRIORITY_SERVICE = "priority_service"  # 优先服务
    EXCLUSIVE_EVENTS = "exclusive_events"  # 专属活动
    POINTS_MULTIPLIER = "points_multiplier" # 积分倍数
    CUSTOM_SERVICE = "custom_service"      # 专属客服


class ActivityStatus(str, Enum):
    """活动状态枚举"""
    PENDING = "PENDING"    # 待开始
    ACTIVE = "ACTIVE"      # 进行中
    ENDED = "ENDED"        # 已结束
    CANCELLED = "CANCELLED" # 已取消


class ParticipationStatus(str, Enum):
    """参与状态枚举"""
    ACTIVE = "ACTIVE"        # 参与中
    COMPLETED = "COMPLETED"  # 已完成
    CANCELLED = "CANCELLED"  # 已取消


# ================== 基础模式类 ==================

class BaseSchema(BaseModel):
    """基础模式类"""
    
    class Config:
        # 启用ORM模式，支持SQLAlchemy模型
        orm_mode = True
        # 使用枚举值而非枚举名
        use_enum_values = True
        # 允许通过字段别名进行填充
        allow_population_by_field_name = True
        # JSON编码器配置
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }


# ================== 会员相关模式 ==================

class MemberBase(BaseSchema):
    """会员基础模式"""
    nickname: Optional[str] = Field(
        None, description="会员昵称，1-50个字符", min_length=1, max_length=50
    )
    birthday: Optional[date] = Field(None, description="生日日期")
    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="用户偏好设置"
    )
    
    @validator('birthday')
    def validate_birthday(cls, v):
        """验证生日日期"""
        if v and v > date.today():
            raise ValueError('生日不能晚于今天')
        if v and date.today().year - v.year > 150:
            raise ValueError('生日日期不合理')
        return v


class MemberCreate(MemberBase):
    """创建会员模式"""
    nickname: str = Field(
        ..., description="会员昵称，必填", min_length=1, max_length=50
    )
    
    @validator('preferences')
    def validate_preferences(cls, v):
        """验证偏好设置"""
        if v is None:
            return {}
        
        # 验证允许的偏好字段
        allowed_keys = {
            'notification_email', 'notification_sms', 'marketing_consent',
            'language', 'timezone', 'currency'
        }
        
        for key in v.keys():
            if key not in allowed_keys:
                raise ValueError(f'不支持的偏好设置: {key}')
        
        return v


class MemberUpdate(MemberBase):
    """更新会员模式"""
    pass  # 所有字段都是可选的


class MemberRead(MemberBase):
    """读取会员模式"""
    member_id: str = Field(
        ..., description="会员ID", min_length=1, max_length=20
    )
    user_id: int = Field(..., description="用户ID", gt=0)
    level_id: int = Field(..., description="会员等级ID", gt=0)
    total_spent: float = Field(..., description="总消费金额", ge=0)
    total_orders: int = Field(..., description="总订单数", ge=0)
    join_date: datetime = Field(..., description="加入日期")
    last_active_at: Optional[datetime] = Field(None, description="最后活跃时间")
    level_upgrade_date: Optional[datetime] = Field(None, description="等级升级时间")


# ================== 会员等级相关模式 ==================

class MembershipLevelBase(BaseSchema):
    """会员等级基础模式"""
    level_name: str = Field(
        ..., description="等级名称", min_length=1, max_length=20
    )
    level_code: MemberLevelCode = Field(..., description="等级代码")
    required_spent: float = Field(..., description="升级所需消费金额", ge=0)
    discount_rate: float = Field(..., description="折扣率", ge=0, le=1)
    point_multiplier: float = Field(..., description="积分倍数", ge=0)
    description: Optional[str] = Field(None, description="等级描述")
    is_active: bool = Field(True, description="是否激活")


class MembershipLevelRead(MembershipLevelBase):
    """读取会员等级模式"""
    level_id: int = Field(..., description="等级ID", gt=0)


# ================== 积分相关模式 ==================

class PointTransactionBase(BaseSchema):
    """积分交易基础模式"""
    transaction_type: TransactionType = Field(..., description="交易类型")
    event_type: EventType = Field(..., description="事件类型") 
    points: int = Field(..., description="积分数量，正数为获得，负数为使用")
    reference_id: Optional[str] = Field(
        None, description="关联订单或活动ID", max_length=50
    )
    description: Optional[str] = Field(
        None, description="交易描述", max_length=200
    )
    
    @validator('points')
    def validate_points(cls, v, values):
        """验证积分数量"""
        if v == 0:
            raise ValueError('积分数量不能为0')
        transaction_type = values.get('transaction_type')
        if transaction_type == TransactionType.EARN and v <= 0:
            raise ValueError('获得积分必须为正数')
        if transaction_type == TransactionType.USE and v >= 0:
            raise ValueError('使用积分必须为负数')
        return v


class PointTransactionCreate(PointTransactionBase):
    """创建积分交易模式"""
    user_id: int = Field(..., description="用户ID", gt=0)


class PointTransactionRead(PointTransactionBase):
    """读取积分交易模式"""
    transaction_id: str = Field(
        ..., description="交易ID", min_length=1, max_length=20
    )
    user_id: int = Field(..., description="用户ID", gt=0)
    balance_after: int = Field(..., description="交易后余额", ge=0)
    expiry_date: Optional[datetime] = Field(None, description="过期时间")
    created_at: datetime = Field(..., description="创建时间")


class PointSummary(BaseSchema):
    """积分汇总模式"""
    total_points: int = Field(..., description="总获得积分", ge=0)
    available_points: int = Field(..., description="可用积分", ge=0)
    frozen_points: int = Field(0, description="冻结积分", ge=0)
    expiring_points: int = Field(0, description="即将过期积分", ge=0)
    expiring_date: Optional[datetime] = Field(None, description="最近过期时间")


# ================== 权益相关模式 ==================

class MembershipBenefitBase(BaseSchema):
    """会员权益基础模式"""
    benefit_type: BenefitType = Field(..., description="权益类型")
    benefit_name: str = Field(
        ..., description="权益名称", min_length=1, max_length=50
    )
    description: Optional[str] = Field(None, description="权益描述")
    usage_limit: Optional[int] = Field(None, description="使用次数限制", ge=0)
    reset_cycle: Optional[str] = Field(None, description="重置周期")
    is_active: bool = Field(True, description="是否激活")


class MembershipBenefitRead(MembershipBenefitBase):
    """读取会员权益模式"""
    benefit_id: int = Field(..., description="权益ID", gt=0)
    level_id: int = Field(..., description="等级ID", gt=0)


class BenefitUsageBase(BaseSchema):
    """权益使用基础模式"""
    benefit_type: BenefitType = Field(..., description="权益类型")
    reference_id: Optional[str] = Field(
        None, description="关联订单或活动ID", max_length=50
    )
    description: Optional[str] = Field(
        None, description="使用描述", max_length=200
    )
    benefit_value: Optional[float] = Field(
        None, description="权益价值", ge=0
    )


class BenefitUsageCreate(BenefitUsageBase):
    """创建权益使用模式"""
    user_id: int = Field(..., description="用户ID", gt=0)


class BenefitUsageRead(BenefitUsageBase):
    """读取权益使用模式"""
    usage_id: int = Field(..., description="使用记录ID", gt=0)
    user_id: int = Field(..., description="用户ID", gt=0)
    used_at: datetime = Field(..., description="使用时间")


class BenefitEligibility(BaseSchema):
    """权益资格模式"""
    user_id: int = Field(..., description="用户ID", gt=0)
    benefit_type: BenefitType = Field(..., description="权益类型")
    benefit_name: str = Field(..., description="权益名称")
    eligible: bool = Field(..., description="是否有资格")
    level_required: bool = Field(..., description="是否需要等级")
    usage_limit: int = Field(..., description="使用限制", ge=0)
    used_count: int = Field(..., description="已使用次数", ge=0)
    remaining_count: int = Field(..., description="剩余次数", ge=0)
    reset_cycle: Optional[str] = Field(None, description="重置周期")
    next_reset_date: Optional[datetime] = Field(None, description="下次重置时间")


# ================== 活动相关模式 ==================

class MemberActivityBase(BaseSchema):
    """会员活动基础模式"""
    title: str = Field(..., description="活动标题", min_length=1, max_length=100)
    description: str = Field(..., description="活动描述")
    activity_type: str = Field(
        ..., description="活动类型", min_length=1, max_length=20
    )
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    max_participants: Optional[int] = Field(
        None, description="最大参与人数", gt=0
    )
    reward_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="奖励配置"
    )
    participation_rules: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="参与规则"
    )
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        """验证结束时间"""
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class MemberActivityCreate(MemberActivityBase):
    """创建会员活动模式"""
    pass


class MemberActivityUpdate(BaseSchema):
    """更新会员活动模式"""
    title: Optional[str] = Field(
        None, description="活动标题", min_length=1, max_length=100
    )
    description: Optional[str] = Field(None, description="活动描述")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    max_participants: Optional[int] = Field(
        None, description="最大参与人数", gt=0
    )
    status: Optional[ActivityStatus] = Field(None, description="活动状态")
    reward_config: Optional[Dict[str, Any]] = Field(None, description="奖励配置")
    participation_rules: Optional[Dict[str, Any]] = Field(None, description="参与规则")


class MemberActivityRead(MemberActivityBase):
    """读取会员活动模式"""
    activity_id: int = Field(..., description="活动ID", gt=0)
    current_participants: int = Field(..., description="当前参与人数", ge=0)
    status: ActivityStatus = Field(..., description="活动状态")
    created_at: datetime = Field(..., description="创建时间")


# ================== 活动参与相关模式 ==================

class ActivityParticipationBase(BaseSchema):
    """活动参与基础模式"""
    progress_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="进度数据"
    )


class ActivityParticipationCreate(ActivityParticipationBase):
    """创建活动参与模式"""
    user_id: int = Field(..., description="用户ID", gt=0)
    activity_id: int = Field(..., description="活动ID", gt=0)


class ActivityParticipationRead(ActivityParticipationBase):
    """读取活动参与模式"""
    participation_id: int = Field(..., description="参与ID", gt=0)
    user_id: int = Field(..., description="用户ID", gt=0)
    activity_id: int = Field(..., description="活动ID", gt=0)
    participation_time: datetime = Field(..., description="参与时间")
    status: ParticipationStatus = Field(..., description="参与状态")


# ================== 复合模式 ==================

class LevelInfo(BaseSchema):
    """等级信息模式"""
    level_id: int = Field(..., description="等级ID", gt=0)
    level_name: str = Field(..., description="等级名称")
    level_code: MemberLevelCode = Field(..., description="等级代码")
    discount_rate: float = Field(..., description="折扣率", ge=0, le=1)
    point_multiplier: float = Field(..., description="积分倍数", ge=0)


class MemberStatistics(BaseSchema):
    """会员统计信息模式"""
    total_spent: float = Field(..., description="总消费金额", ge=0)
    total_orders: int = Field(..., description="总订单数", ge=0)
    join_date: str = Field(..., description="加入日期")
    last_active: Optional[str] = Field(None, description="最后活跃时间")


class BenefitStatus(BaseSchema):
    """权益状态模式"""
    free_shipping: bool = Field(False, description="免运费")
    birthday_gift: bool = Field(False, description="生日礼品")
    priority_service: bool = Field(False, description="优先服务")
    exclusive_events: bool = Field(False, description="专属活动")
    points_multiplier: bool = Field(False, description="积分倍数")
    custom_service: bool = Field(False, description="专属客服")


class NextLevelInfo(BaseSchema):
    """下一等级信息模式"""
    level_name: str = Field(..., description="等级名称")
    level_code: MemberLevelCode = Field(..., description="等级代码")
    required_spent: float = Field(..., description="升级所需消费", ge=0)
    remaining_spent: float = Field(..., description="剩余所需消费", ge=0)
    progress_percentage: float = Field(..., description="升级进度百分比", ge=0, le=100)


class MemberWithDetails(BaseSchema):
    """包含完整详情的会员信息模式"""
    member_id: str = Field(..., description="会员ID")
    user_id: int = Field(..., description="用户ID", gt=0)
    level: LevelInfo = Field(..., description="等级信息")
    points: PointSummary = Field(..., description="积分信息")
    statistics: MemberStatistics = Field(..., description="统计信息")
    benefits: BenefitStatus = Field(..., description="权益状态")
    next_level: Optional[NextLevelInfo] = Field(None, description="下一等级信息")


# ================== 分页和响应模式 ==================

class PaginationInfo(BaseSchema):
    """分页信息模式"""
    page: int = Field(..., description="当前页码", gt=0)
    limit: int = Field(..., description="每页数量", gt=0, le=100)
    total: int = Field(..., description="总记录数", ge=0)
    total_pages: int = Field(..., description="总页数", ge=0)


class PointTransactionList(BaseSchema):
    """积分交易列表模式"""
    summary: PointSummary = Field(..., description="积分汇总")
    transactions: List[PointTransactionRead] = Field(..., description="交易记录")
    pagination: PaginationInfo = Field(..., description="分页信息")


class BenefitUsageList(BaseSchema):
    """权益使用列表模式"""
    usage_history: List[BenefitUsageRead] = Field(..., description="使用历史")
    pagination: PaginationInfo = Field(..., description="分页信息")


class ActivityList(BaseSchema):
    """活动列表模式"""
    activities: List[MemberActivityRead] = Field(..., description="活动列表")
    pagination: PaginationInfo = Field(..., description="分页信息")


class UserActivityList(BaseSchema):
    """用户活动参与列表模式"""
    activities: List[Dict[str, Any]] = Field(..., description="参与的活动")
    pagination: PaginationInfo = Field(..., description="分页信息")


# ================== API响应模式 ==================

class APIResponse(BaseSchema):
    """通用API响应模式"""
    code: int = Field(..., description="响应状态码", ge=100, le=599)
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")


class MemberProfileResponse(APIResponse):
    """会员档案响应模式"""
    data: Optional[MemberWithDetails] = Field(None, description="会员档案数据")


class PointTransactionResponse(APIResponse):
    """积分交易响应模式"""
    data: Optional[PointTransactionRead] = Field(None, description="积分交易数据")


class BenefitUsageResponse(APIResponse):
    """权益使用响应模式"""
    data: Optional[BenefitUsageRead] = Field(None, description="权益使用数据")


class ActivityParticipationResponse(APIResponse):
    """活动参与响应模式"""
    data: Optional[ActivityParticipationRead] = Field(None, description="活动参与数据")


# ================== 系统配置模式 ==================

class SystemConfigBase(BaseSchema):
    """系统配置基础模式"""
    config_key: str = Field(..., description="配置键", min_length=1, max_length=50)
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: bool = Field(True, description="是否激活")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置模式"""
    pass


class SystemConfigUpdate(BaseSchema):
    """更新系统配置模式"""
    config_value: Optional[str] = Field(None, description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class SystemConfigRead(SystemConfigBase):
    """读取系统配置模式"""
    config_id: int = Field(..., description="配置ID", gt=0)
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
