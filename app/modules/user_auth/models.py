"""
用户认证模块数据模型
按照docs/modules/user-auth/overview.md设计文档实现
包含User、Role、Permission等完整认证模型
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.shared.models import Base

class User(Base):
    """用户表 - 核心用户信息和认证状态"""
    __tablename__ = 'users'
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 核心认证字段
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # 用户状态管理
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 验证状态
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    
    # 安全字段
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    # 基础信息
    real_name = Column(String(100), nullable=True)
    role = Column(String(20), default='user', nullable=False)  # 基础角色
    
    # 微信相关字段（业务扩展）
    wx_openid = Column(String(100), unique=True, nullable=True)
    wx_unionid = Column(String(100), unique=True, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系定义
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Role(Base):
    """角色表 - 角色定义和层级管理"""
    __tablename__ = 'roles'
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 角色信息
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False)  # 角色等级，数字越小权限越高
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系定义
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', level={self.level})>"


class Permission(Base):
    """权限表 - 细粒度权限控制"""
    __tablename__ = 'permissions'
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 权限信息
    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(100), nullable=False)  # 资源类型
    action = Column(String(50), nullable=False)     # 操作类型
    description = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # 关系定义
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"


class UserRole(Base):
    """用户角色关联表 - 多对多关系"""
    __tablename__ = 'user_roles'
    
    # 联合主键
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    
    # 分配信息
    assigned_at = Column(DateTime, server_default=func.now(), nullable=False)
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # 分配者
    
    # 关系定义
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class RolePermission(Base):
    """角色权限关联表 - 多对多关系"""
    __tablename__ = 'role_permissions'
    
    # 联合主键
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
    
    # 授权信息
    granted_at = Column(DateTime, server_default=func.now(), nullable=False)
    granted_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # 授权者
    
    # 关系定义
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    granter = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


class Session(Base):
    """会话表 - 用户会话管理"""
    __tablename__ = 'sessions'
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 会话信息
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # 会话状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 安全信息
    ip_address = Column(String(45), nullable=True)  # 支持IPv6
    user_agent = Column(Text, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_accessed_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # 关系定义
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"