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

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema, TimestampSchema


class UserRegister(BaseSchema):
    """用户注册模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$', description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和横线')
        return v


class UserLogin(BaseSchema):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserCreate(BaseSchema):
    """用户创建模式（管理员用）"""
    username: str = Field(..., max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    password: Optional[str] = Field(None, min_length=6, description="密码")
    phone: Optional[str] = Field(None, description="手机号")
    real_name: Optional[str] = Field(None, description="真实姓名")
    role: Optional[str] = Field("user", description="用户角色")
    is_active: Optional[bool] = Field(True, description="是否激活")


class UserUpdate(BaseSchema):
    """用户信息更新模式"""
    email: Optional[str] = Field(None, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$', description="邮箱地址")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    real_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class UserChangePassword(BaseSchema):
    """用户修改密码模式"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v, info):
        if 'old_password' in info.data and v == info.data['old_password']:
            raise ValueError('新密码不能与原密码相同')
        return v


class UserRead(TimestampSchema):
    """用户信息展示模式"""
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    real_name: Optional[str] = None
    role: str
    is_active: bool
    wx_openid: Optional[str] = None
    wx_unionid: Optional[str] = None


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