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
from app.core.async_utils import run_in_thread
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
        用户认证（纯认证，不修改数据库）

        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 明文密码

        Returns:
            User: 认证成功返回用户对象，失败返回None
            
        Note:
            此方法仅做认证检查，不会修改数据库（失败次数、登录信息等）
            数据库修改操作应在调用方（如login_user）中处理
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
            return None

        # 认证成功，返回用户对象
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

    @staticmethod
    async def register_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        verification_code: str,
        phone: Optional[str] = None,
        real_name: Optional[str] = None,
    ) -> dict:
        """
        用户注册业务逻辑

        Args:
            db: 数据库会话
            username: 用户名
            email: 邮箱
            password: 明文密码
            verification_code: 邮箱验证码
            phone: 手机号（可选）
            real_name: 真实姓名（可选）

        Returns:
            dict: 包含用户信息和token的字典

        Raises:
            HTTPException: 验证码错误、用户名或邮箱已存在时抛出400错误
        """
        from app.core.verification import VerificationCodeService
        
        # 1. 验证验证码
        is_valid = await VerificationCodeService.verify_code(
            email=email,
            code=verification_code,
            code_type="register"
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期",
            )
        
        # 2. 检查用户名是否已存在（通过线程池执行，避免阻塞事件循环）
        existing_user = await run_in_thread(UserRepository.get_by_username, db, username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        # 3. 检查邮箱是否已存在（通过线程池执行，避免阻塞事件循环）
        existing_email = await run_in_thread(UserRepository.get_by_email, db, email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # 4. 创建用户（通过线程池执行，避免阻塞事件循环）
        try:
            password_hash = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                phone=phone,
                real_name=real_name,
                role="user",  # V1.0 Mini-MVP: 默认普通用户角色
                is_active=True,
                email_verified=True,  # 通过验证码注册，邮箱已验证
            )
            created_user = await run_in_thread(UserRepository.create, db, user)
            
            # 5. 生成token
            tokens = UserService.generate_tokens(created_user)
            
            # 6. 返回用户信息和token
            return {
                "user": created_user,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": tokens["token_type"],
            }
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed due to data conflict",
            )

    @staticmethod
    async def login_user(
        db: Session,
        username: str,
        password: str,
        verification_code: Optional[str] = None
    ) -> dict:
        """
        用户登录业务逻辑（支持验证码）

        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 明文密码
            verification_code: 验证码（登录失败3次后必填）

        Returns:
            dict: 包含token信息的字典

        Raises:
            HTTPException: 认证失败或需要验证码时抛出错误
        """
        from app.core.auth import ACCESS_TOKEN_EXPIRE_MINUTES
        from app.core.verification import VerificationCodeService
        
        # 先查找用户（用于失败次数统计）（通过线程池执行，避免阻塞事件循环）
        user_for_check = await run_in_thread(UserRepository.get_by_username_or_email, db, username)
        
        # 检查是否需要验证码（失败3次以上）
        if user_for_check and user_for_check.failed_login_attempts >= 3:
            if not verification_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="登录失败次数过多，需要验证码",
                )
            
            # 验证验证码
            # 使用邮箱作为验证码的key（如果是邮箱登录）或使用用户的邮箱
            email = user_for_check.email
            is_valid = await VerificationCodeService.verify_code(
                email=email,
                code=verification_code,
                code_type="login"
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="验证码错误或已过期",
                )
        
        # 认证用户（纯认证，不修改数据库）
        user = UserService.authenticate_user(db, username, password)
        
        if not user:
            # 如果用户存在但认证失败，增加失败次数（通过线程池执行，避免阻塞事件循环）
            if user_for_check:
                await run_in_thread(UserRepository.increment_failed_login, db, user_for_check)
            
            # 记录登录失败事件
            from app.core.security_logger import log_security_event
            log_security_event(
                event_type="login_failed",
                message="Login failed - invalid credentials",
                user_data={
                    "username": username,
                    "reason": "invalid_credentials",
                },
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 认证成功，更新登录信息（会重置失败次数）（通过线程池执行，避免阻塞事件循环）
        await run_in_thread(UserRepository.update_login_info, db, user)
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        """
        刷新访问令牌业务逻辑

        Args:
            db: 数据库会话
            refresh_token: 刷新令牌

        Returns:
            dict: 包含新token信息的字典

        Raises:
            HTTPException: 令牌无效时抛出401错误
        """
        from app.core.auth import decode_token, AuthenticationError, ACCESS_TOKEN_EXPIRE_MINUTES
        
        try:
            payload = decode_token(refresh_token)

            # 检查令牌类型
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")

            user_id: int = payload.get("sub")
            if user_id is None:
                raise AuthenticationError("Invalid token payload")

            # 验证用户是否存在且激活
            user = UserRepository.get_by_id(db, user_id)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")

            # 创建新的访问令牌
            access_token = create_access_token(data={"sub": str(user.id)})
            new_refresh_token = create_refresh_token(data={"sub": user.id})

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }

        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def update_user_info(
        db: Session,
        user_id: int,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        real_name: Optional[str] = None,
    ) -> User:
        """
        更新用户信息业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            email: 邮箱（可选）
            phone: 手机号（可选）
            real_name: 真实姓名（可选）

        Returns:
            User: 更新后的用户对象

        Raises:
            HTTPException: 邮箱冲突或更新失败时抛出400错误
        """
        # 获取用户
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # 检查邮箱是否已被其他用户使用
        if email:
            existing_user = UserRepository.get_by_email(db, email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use by another user",
                )

        # 更新用户信息
        update_data = {}
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if real_name is not None:
            update_data["real_name"] = real_name

        try:
            return UserRepository.update(db, user, update_data)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed due to data conflict",
            )

    @staticmethod
    def change_user_password(
        db: Session, user_id: int, old_password: str, new_password: str
    ) -> dict:
        """
        修改用户密码业务逻辑

        Args:
            db: 数据库会话
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            dict: 成功消息

        Raises:
            HTTPException: 密码错误或修改失败时抛出错误
        """
        # 获取用户
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password",
            )

        # 更新密码
        try:
            password_hash = get_password_hash(new_password)
            UserRepository.update(db, user, {"password_hash": password_hash})
            return {"message": "Password changed successfully"}
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password",
            )

    @staticmethod
    def get_user_list(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        获取用户列表业务逻辑

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[User]: 用户列表
        """
        return UserRepository.list(db, skip=skip, limit=limit)

    @staticmethod
    async def send_verification_code(
        db: Session,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        code_type: str = "register"
    ) -> dict:
        """
        发送验证码业务逻辑（支持邮箱和手机号）

        Args:
            db: 数据库会话
            email: 邮箱地址（邮箱验证码）
            phone: 手机号（短信验证码）
            code_type: 验证码类型（register/login/reset_password/phone_login）

        Returns:
            dict: 成功消息

        Raises:
            HTTPException: 验证失败时抛出错误
        """
        from app.core.verification import VerificationCodeService
        
        # 确定使用邮箱还是手机号
        if email:
            identifier = email
            
            # 如果是注册验证码，检查邮箱是否已注册（通过线程池执行，避免阻塞事件循环）
            if code_type == "register":
                existing_email = await run_in_thread(UserRepository.get_by_email, db, email)
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered",
                    )
            
            # 如果是重置密码或登录验证码，检查邮箱是否存在（通过线程池执行，避免阻塞事件循环）
            if code_type in ["reset_password", "login"]:
                existing_email = await run_in_thread(UserRepository.get_by_email, db, email)
                if not existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Email not found",
                    )
        elif phone:
            identifier = phone
            
            # 如果是手机号登录，检查手机号是否存在（通过线程池执行，避免阻塞事件循环）
            if code_type == "phone_login":
                user = await run_in_thread(UserRepository.get_by_phone, db, phone)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Phone number not found",
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or phone is required",
            )
        
        # 生成并发送验证码
        code = await VerificationCodeService.send_verification_code(identifier, code_type)
        
        # 开发环境返回验证码（生产环境不应返回）
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {
                "message": "Verification code sent successfully",
                "code": code,  # 仅开发环境返回
                "expires_in": VerificationCodeService.CODE_EXPIRY,
            }
        
        return {
            "message": "Verification code sent successfully",
            "expires_in": VerificationCodeService.CODE_EXPIRY,
        }

    @staticmethod
    async def phone_login(
        db: Session,
        phone: str,
        verification_code: str
    ) -> dict:
        """
        手机号验证码登录业务逻辑

        Args:
            db: 数据库会话
            phone: 手机号
            verification_code: 短信验证码

        Returns:
            dict: 包含token信息的字典

        Raises:
            HTTPException: 验证失败时抛出错误
        """
        from app.core.auth import ACCESS_TOKEN_EXPIRE_MINUTES
        from app.core.verification import VerificationCodeService
        
        # 验证验证码
        is_valid = await VerificationCodeService.verify_code(
            email=phone,  # 使用phone作为key
            code=verification_code,
            code_type="phone_login"
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期",
            )
        
        # 查找用户（通过线程池执行，避免阻塞事件循环）
        user = await run_in_thread(UserRepository.get_by_phone, db, phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found",
            )
        
        # 检查账户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        
        # 更新登录信息（通过线程池执行，避免阻塞事件循环）
        await run_in_thread(UserRepository.update_login_info, db, user)
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    async def reset_password_request(
        db: Session,
        email: str
    ) -> dict:
        """
        请求重置密码业务逻辑

        Args:
            db: 数据库会话
            email: 邮箱地址

        Returns:
            dict: 成功消息
        """
        # 直接调用发送验证码
        return await UserService.send_verification_code(
            db=db,
            email=email,
            code_type="reset_password"
        )

    @staticmethod
    async def reset_password_confirm(
        db: Session,
        email: str,
        verification_code: str,
        new_password: str
    ) -> dict:
        """
        确认重置密码业务逻辑

        Args:
            db: 数据库会话
            email: 邮箱地址
            verification_code: 验证码
            new_password: 新密码

        Returns:
            dict: 成功消息

        Raises:
            HTTPException: 验证失败时抛出错误
        """
        from app.core.verification import VerificationCodeService
        
        # 验证验证码
        is_valid = await VerificationCodeService.verify_code(
            email=email,
            code=verification_code,
            code_type="reset_password"
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期",
            )
        
        # 查找用户（通过线程池执行，避免阻塞事件循环）
        user = await run_in_thread(UserRepository.get_by_email, db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found",
            )
        
        # 更新密码（通过线程池执行，避免阻塞事件循环）
        try:
            password_hash = get_password_hash(new_password)
            await run_in_thread(UserRepository.update, db, user, {"password_hash": password_hash})
            return {"message": "Password reset successfully"}
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password",
            )
