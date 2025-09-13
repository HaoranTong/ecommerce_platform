"""
用户认证模块数据模型

按照docs/modules/user-auth/overview.md设计文档实现
根据docs/modules/data-models/overview.md文档规范实现
包含User、Role、Permission等完整认证模型
符合数据库设计原则和字段命名标准

主要模型:
- User: 用户    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 关联用户
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
- Role: 角色定义
- Permission: 权限控制
- UserRole: 用户角色关联
- RolePermission: 角色权限关联
- Session: 会话管理
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# 从技术基础设施层导入统一的Base类和混入
from app.core.database import Base
from app.shared.models import TimestampMixin, SoftDeleteMixin, ModelRegistry


@ModelRegistry.register
class User(Base, TimestampMixin, SoftDeleteMixin):
    """用户模型 - 管理平台用户信息和认证
    
    根据数据模型文档规范实现，包含：
    - 主键使用Integer
    - 唯一约束字段（username, email, wx_openid, wx_unionid）
    - 软删除支持
    - 微信集成字段
    - 时间戳自动维护
    """
    __tablename__ = 'users'

    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 核心认证字段 - 唯一约束
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # 用户状态
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended

    # 验证状态
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)

    # 安全字段
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    # 基础信息
    phone = Column(String(20), nullable=True)
    real_name = Column(String(100), nullable=True)
    role = Column(String(20), default='user', nullable=False)  # 基础角色

    # 微信相关字段（业务扩展）
    wx_openid = Column(String(100), unique=True, nullable=True)
    wx_unionid = Column(String(100), unique=True, nullable=True)

    # 软删除字段由SoftDeleteMixin提供：
    # - is_deleted: Boolean, default=False, nullable=False
    # - deleted_at: DateTime, nullable=True

    # 时间戳字段由TimestampMixin提供：
    # - created_at: DateTime, server_default=func.now(), nullable=False
    # - updated_at: DateTime, server_default=func.now(), onupdate=func.now(), nullable=False

    # 关系定义
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserRole.user_id")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


@ModelRegistry.register
class Role(Base, TimestampMixin):
    """角色模型 - 定义系统角色和权限层级"""
    __tablename__ = 'roles'

    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 角色信息
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False)  # 角色层级，数字越大权限越高

    # 关系定义
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', level={self.level})>"


@ModelRegistry.register
class Permission(Base, TimestampMixin):
    """权限模型 - 定义系统具体权限"""
    __tablename__ = 'permissions'

    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 权限信息
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(100), nullable=False)  # 资源类型
    action = Column(String(50), nullable=False)     # 操作类型
    description = Column(Text, nullable=True)

    # 关系定义
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"


@ModelRegistry.register
class UserRole(Base, TimestampMixin):
    """用户角色关联模型"""
    __tablename__ = 'user_roles'

    # 联合主键 - 遵循docs/standards/database-standards.md规定使用Integer外键
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)

    # 分配信息
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 关系定义
    user = relationship("User", back_populates="user_roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


@ModelRegistry.register
class RolePermission(Base, TimestampMixin):
    """角色权限关联模型"""
    __tablename__ = 'role_permissions'

    # 联合主键 - 遵循docs/standards/database-standards.md规定使用Integer外键
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)

    # 授权信息
    granted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    granted_at = Column(DateTime, server_default=func.now(), nullable=False)

    # 关系定义
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    granted_by_user = relationship("User", foreign_keys=[granted_by])

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


@ModelRegistry.register
class Session(Base, TimestampMixin):
    """会话模型 - 用户登录会话管理"""
    __tablename__ = 'sessions'

    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # 关联用户
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # 会话信息
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    last_accessed_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # 客户端信息
    ip_address = Column(String(45), nullable=True)  # 支持IPv6
    user_agent = Column(Text, nullable=True)

    # 关系定义
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"