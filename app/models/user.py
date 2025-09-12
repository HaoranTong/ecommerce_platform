"""
文件名：user.py
文件路径：app/models/user.py
功能描述：用户管理相关的数据模型定义
主要功能：
- User用户模型：用户基础信息、认证、权限管理
- 用户角色和状态管理
- 微信小程序对接字段预留
使用说明：
- 导入：from app.models.user import User
- 关系：User与Order、Payment、Cart的一对多关系
依赖模块：
- app.models.base: 基础模型类和时间戳混合类
- sqlalchemy: 数据库字段定义和关系映射
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """用户模型"""
    __tablename__ = 'users'
    
    # 主键
    id = Column(BigInteger, primary_key=True, index=True)
    
    # 基础认证信息
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 用户状态和权限
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String(20), default='user', nullable=False)  # 'user', 'admin', 'super_admin'
    
    # 微信相关字段（为小程序对接预留）
    wx_openid = Column(String(100), unique=True, nullable=True)
    wx_unionid = Column(String(100), unique=True, nullable=True)
    
    # 基础用户信息
    phone = Column(String(20), nullable=True)
    real_name = Column(String(100), nullable=True)
    
    # 关系映射
    # orders = relationship("Order", back_populates="user")
    # payments = relationship("Payment", back_populates="user") 
    # carts = relationship("Cart", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"