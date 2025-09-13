"""
用户认证和JWT工具模块
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Union

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.modules.user_auth.models import User
from app.core.database import get_db

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()


class AuthenticationError(HTTPException):
    """认证错误"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except InvalidTokenError:
        raise AuthenticationError("Invalid token")


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户凭据，包含账户锁定逻辑"""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    
    # 检查账户是否被锁定
    if is_account_locked(user):
        raise AuthenticationError("Account is locked due to too many failed login attempts")
    
    # 检查账户是否激活
    if not user.is_active:
        raise AuthenticationError("Account is disabled")
    
    # 验证密码
    if not verify_password(password, user.password_hash):
        # 密码错误，增加失败次数
        increment_failed_attempts(db, user)
        return None
    
    # 登录成功，重置失败次数并更新最后登录时间
    reset_failed_attempts(db, user)
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    return user


def is_account_locked(user: User) -> bool:
    """检查账户是否被锁定"""
    if user.locked_until is None:
        return False
    
    # 检查锁定时间是否已过期
    if user.locked_until <= datetime.utcnow():
        # 锁定时间已过，应该解锁账户（但不在这里操作数据库）
        return False
    
    return True


def increment_failed_attempts(db: Session, user: User) -> None:
    """增加登录失败次数，必要时锁定账户"""
    MAX_FAILED_ATTEMPTS = 5  # 最大失败次数
    LOCK_DURATION_MINUTES = 30  # 锁定时长（分钟）
    
    user.failed_login_attempts += 1
    
    # 达到最大失败次数，锁定账户
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCK_DURATION_MINUTES)
        user.status = 'locked'
        
        # 记录安全事件
        from app.core.security_logger import log_security_event
        log_security_event(
            event_type="account_locked",
            message=f"Account locked due to excessive failed login attempts",
            user_data={
                "user_id": user.id,
                "username": user.username,
                "failed_attempts": user.failed_login_attempts,
                "locked_until": user.locked_until.isoformat()
            }
        )
    
    db.commit()


def reset_failed_attempts(db: Session, user: User) -> None:
    """重置登录失败次数"""
    if user.failed_login_attempts > 0 or user.locked_until is not None:
        user.failed_login_attempts = 0
        user.locked_until = None
        if user.status == 'locked':
            user.status = 'active'
        
        # 记录安全事件
        from app.core.security_logger import log_security_event
        log_security_event(
            event_type="login_success",
            message=f"Account login successful, failed attempts reset",
            user_data={
                "user_id": user.id,
                "username": user.username
            }
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（依赖注入）"""
    try:
        payload = decode_token(credentials.credentials)
        
        # 检查令牌类型
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise AuthenticationError("Invalid token payload")
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid user ID in token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("User account is disabled")
        
        return user
    
    except AuthenticationError:
        raise
    except Exception:
        raise AuthenticationError("Authentication failed")


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise AuthenticationError("User account is disabled")
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前管理员用户（权限检查）"""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员权限不足，无法访问此资源"
        )
    return current_user


async def get_current_super_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前超级管理员用户（最高权限检查）"""
    if current_user.role != 'super_admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员权限不足，无法访问此资源"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取可选的当前用户（用于可选认证的端点）"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except AuthenticationError:
        return None


def require_ownership(resource_user_id: int, current_user: User) -> bool:
    """检查资源所有权（用户只能操作自己的资源）"""
    if current_user.role in ['admin', 'super_admin']:
        return True  # 管理员可以操作所有资源
    
    return resource_user_id == current_user.id


def check_resource_ownership(resource_user_id: int, current_user: User = Depends(get_current_active_user)):
    """资源所有权检查依赖"""
    if not require_ownership(resource_user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能操作自己的资源"
        )
    return current_user
