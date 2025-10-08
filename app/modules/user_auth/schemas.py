"""
文件名：user.py
文件路径：app/schemas/user.py
功能描述：用户管理相关的Pydantic模式定义
主要功能：
- 用户注册、登录、更新的输入验证模式
- 用户信息展示的输出模式
- 认证令牌和权限相关模式
使用说明：
- 导入：from app.schemas.user import UserCreate, UserRead, UserLogin
- 验证：user_data = UserCreate(**input_data)
- 序列化：user_response = UserRead.model_validate(user_obj)
依赖模块：
- app.schemas.base: 基础模式类
- pydantic: 数据验证和字段定义
"""

from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


# 模块内独立定义基础schemas，遵循模块化单体架构原则
class BaseSchema(BaseModel):
    """用户认证模块基础模式类"""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


# 泛型类型变量
T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """
    统一响应格式（符合 API 标准规范）
    
    用于包装所有成功响应，确保响应格式统一
    """
    success: bool = Field(True, description="请求是否成功")
    code: int = Field(200, description="业务状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据（如分页信息、统计数据等）")

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """
    统一错误响应格式（符合 API 标准规范）
    
    用于包装所有错误响应
    """
    success: bool = Field(False, description="请求是否成功")
    code: int = Field(..., description="错误状态码")
    message: str = Field(..., description="错误消息")
    data: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据（如请求ID、时间戳等）")

    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    """包含时间戳的基础模式"""

    created_at: datetime
    updated_at: datetime


class UserRegister(BaseSchema):
    """用户注册模式"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(
        ..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", description="邮箱地址"
    )
    password: str = Field(..., min_length=8, max_length=128, description="密码（至少8位，包含字母和数字）")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    verification_code: str = Field(
        ..., min_length=6, max_length=6, description="验证码"
    )
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和横线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """验证密码强度：至少8位，必须包含字母和数字"""
        if len(v) < 8:
            raise ValueError("密码长度至少为8位")
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v


class UserLogin(BaseSchema):
    """用户登录模式（密码登录）"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    verification_code: Optional[str] = Field(None, min_length=6, max_length=6, description="验证码（登录失败3次后必填）")


class PhoneLogin(BaseSchema):
    """手机号验证码登录模式"""

    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    verification_code: str = Field(..., min_length=6, max_length=6, description="短信验证码")


class PasswordResetRequest(BaseSchema):
    """请求重置密码模式"""

    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", description="邮箱地址")


class PasswordResetConfirm(BaseSchema):
    """确认重置密码模式"""

    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", description="邮箱地址")
    verification_code: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码（至少8位，包含字母和数字）")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        """验证新密码强度"""
        if len(v) < 8:
            raise ValueError("密码长度至少为8位")
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v


class UserCreate(BaseSchema):
    """用户创建模式（管理员用）"""

    username: str = Field(..., max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    password: Optional[str] = Field(None, min_length=8, description="密码（至少8位，包含字母和数字）")
    phone: Optional[str] = Field(None, description="手机号")
    real_name: Optional[str] = Field(None, description="真实姓名")
    role: Optional[str] = Field("user", description="用户角色")
    is_active: Optional[bool] = Field(True, description="是否激活")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """验证密码强度（如果提供了密码）"""
        if v is not None:
            if len(v) < 8:
                raise ValueError("密码长度至少为8位")
            if not any(c.isalpha() for c in v):
                raise ValueError("密码必须包含字母")
            if not any(c.isdigit() for c in v):
                raise ValueError("密码必须包含数字")
        return v


class UserUpdate(BaseSchema):
    """用户信息更新模式"""

    email: Optional[str] = Field(
        None, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", description="邮箱地址"
    )
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class UserChangePassword(BaseSchema):
    """用户修改密码模式"""

    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码（至少8位，包含字母和数字）")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v, info):
        """验证新密码强度和唯一性"""
        if "old_password" in info.data and v == info.data["old_password"]:
            raise ValueError("新密码不能与原密码相同")
        # 密码强度验证
        if len(v) < 8:
            raise ValueError("密码长度至少为8位")
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v


class UserRead(TimestampSchema):
    """用户信息展示模式"""

    id: int
    username: str
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: str
    status: str  # 新增status字段
    is_active: bool
    email_verified: bool = False  # 新增邮箱验证状态
    phone_verified: bool = False  # 新增手机验证状态
    two_factor_enabled: bool = False  # 新增MFA状态
    wx_openid: Optional[str] = None
    wx_unionid: Optional[str] = None
    last_login_at: Optional[datetime] = None  # 新增最后登录时间


class UserProfile(UserRead):
    """用户个人资料模式（包含敏感信息）"""

    pass  # 继承UserRead，可根据需要添加额外字段


class UserPublic(BaseSchema):
    """用户公开信息模式（不包含敏感信息）"""

    id: int
    username: str
    real_name: Optional[str] = None
    role: str
    created_at: datetime


class Token(BaseSchema):
    """认证令牌模式"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseSchema):
    """令牌刷新模式"""

    refresh_token: str


class TokenData(BaseSchema):
    """令牌数据模式（用于JWT解析）"""

    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None


class UserStats(BaseSchema):
    """用户统计信息模式"""

    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    user_roles_distribution: dict


class SendVerificationCode(BaseSchema):
    """发送验证码请求模式（支持邮箱和手机号）"""

    email: Optional[str] = Field(
        None, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", description="邮箱地址"
    )
    phone: Optional[str] = Field(
        None, pattern=r"^1[3-9]\d{9}$", description="手机号"
    )
    code_type: str = Field(
        "register",
        pattern=r"^(register|login|reset_password|phone_login)$",
        description="验证码类型：register(注册), login(登录), reset_password(重置密码), phone_login(手机登录)"
    )

    @field_validator("email")
    @classmethod
    def validate_email_or_phone(cls, v, info):
        """确保邮箱或手机号至少提供一个"""
        if not v and not info.data.get("phone"):
            raise ValueError("邮箱或手机号必须提供一个")
        return v


class UserRegisterResponse(BaseSchema):
    """用户注册响应模式"""

    user: UserRead
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
