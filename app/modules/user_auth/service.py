"""
文件名：service.py
文件路径：app/modules/user_auth/service.py
功能描述：用户管理相关的业务逻辑服务（四层架构 - Service层）

按照四层架构设计，Service层负责：
1. 业务逻辑处理
2. 数据验证和业务规则
3. 调用Repository层进行数据操作
4. 业务流程编排

主要功能：
- 用户注册、登录业务逻辑
- 用户信息管理和验证
- 用户权限控制逻辑
- 业务规则验证

使用说明：
- 导入：from app.modules.user_auth.service import UserService
- 在路由中调用：UserService.create_user(db, user_data)
"""

from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import (create_access_token, create_refresh_token,
                           get_password_hash, verify_password)
from app.modules.user_auth.models import User
from app.modules.user_auth.repository import (
    UserRepository, RoleRepository, PermissionRepository,
    UserRoleRepository, RolePermissionRepository, SessionRepository
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户管理业务逻辑服务"""

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
        real_name: Optional[str] = None,
        role: str = "user",
        is_active: bool = True,
    ) -> User:
        """
        创建新用户

        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            password: 明文密码
            phone: 手机号（可选）
            real_name: 真实姓名（可选）
            role: 角色（默认user）
            is_active: 是否激活（默认True）

        Returns:
            User: 创建的用户对象

        Raises:
            HTTPException: 用户名或邮箱已存在时抛出400错误
        """
        # 使用Repository检查用户名和邮箱唯一性
        if UserRepository.check_exists(db, username=username, email=email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或邮箱已存在"
            )

        # 创建用户实体
        password_hash = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            phone=phone,
            real_name=real_name,
            role=role,
            is_active=is_active,
        )

        try:
            # 使用Repository创建用户
            return UserRepository.create(db, user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户创建失败，数据冲突"
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
        # 使用Repository查询用户（支持用户名或邮箱登录）
        user = UserRepository.get_by_username_or_email(db, username)

        if not user:
            return None

        # 检查账户是否被锁定
        if user.locked_until and user.locked_until > datetime.now():
            return None

        # 验证密码
        if not verify_password(password, user.password_hash):
            # 增加失败次数
            UserRepository.increment_failed_login(db, user)
            return None

        # 认证成功，更新登录信息
        UserRepository.update_login_info(db, user)
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
        # 使用Repository获取用户
        return UserRepository.get_by_id(db, user_id)

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[User]:
        """
        获取用户列表

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            **filters: 过滤条件（is_active, status, role, search）

        Returns:
            List[User]: 用户列表
        """
        # 使用Repository获取用户列表，支持更多过滤条件
        return UserRepository.list(db, skip=skip, limit=limit, **filters)

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
        # 使用Repository获取用户
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None

        try:
            # 使用Repository更新用户
            return UserRepository.update(db, user, kwargs)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户更新失败，数据冲突"
            )

    @staticmethod
    def change_password(
        db: Session, user_id: int, old_password: str, new_password: str
    ) -> bool:
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
        # 使用Repository获取用户
        user = UserRepository.get_by_id(db, user_id)
        if not user or not verify_password(old_password, user.password_hash):
            return False

        # 使用Repository更新密码
        password_hash = get_password_hash(new_password)
        UserRepository.update(db, user, {"password_hash": password_hash})
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
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )

        return {
            "access_token": access_token,
            "refresh_token": None,  # 暂时不实现refresh_token
            "token_type": "bearer",
        }
