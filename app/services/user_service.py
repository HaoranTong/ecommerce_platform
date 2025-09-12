"""
文件名：user_service.py
文件路径：app/services/user_service.py
功能描述：用户管理相关的业务逻辑服务
主要功能：
- 用户注册、登录业务逻辑
- 用户信息管理和验证
- 用户权限控制逻辑
使用说明：
- 导入：from app.services.user_service import UserService
- 在路由中调用：UserService.register_user(user_data)
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models import User
from app.auth import create_access_token, create_refresh_token, verify_password, get_password_hash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户管理业务逻辑服务"""
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, 
                   phone: Optional[str] = None, real_name: Optional[str] = None) -> User:
        """
        创建新用户
        
        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            password: 明文密码
            phone: 手机号（可选）
            real_name: 真实姓名（可选）
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            HTTPException: 用户名或邮箱已存在时抛出400错误
        """
        # 检查用户名和邮箱唯一性
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名或邮箱已存在"
            )
        
        # 创建用户
        password_hash = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            phone=phone,
            real_name=real_name
        )
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户创建失败，数据冲突"
            )
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 明文密码
            
        Returns:
            User: 认证成功返回用户对象，失败返回None
        """
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not verify_password(password, user.password_hash):
            return None
            
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            User: 用户对象或None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        获取用户列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            List[User]: 用户列表
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            User: 更新后的用户对象或None
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户更新失败，数据冲突"
            )
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改用户密码
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 修改成功返回True，失败返回False
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not verify_password(old_password, user.password_hash):
            return False
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
        return True
    
    @staticmethod
    def generate_tokens(user: User) -> dict:
        """
        生成用户访问令牌
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 包含access_token的字典
        """
        access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": None,  # 暂时不实现refresh_token
            "token_type": "bearer"
        }