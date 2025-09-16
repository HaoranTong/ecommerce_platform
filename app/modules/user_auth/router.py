"""
用户认证相关API路由
"""
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.modules.user_auth.models import User
from app.core.auth import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    get_password_hash,
    get_current_user,
    get_current_active_user,
    decode_token,
    AuthenticationError,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.modules.user_auth.schemas import (
    UserRegister,
    UserLogin, 
    UserRead,
    UserUpdate,
    UserChangePassword,
    Token,
    TokenRefresh
)

router = APIRouter()


@router.post("/user-auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 创建新用户
    try:
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            phone=user_data.phone,
            real_name=user_data.real_name,
            role='user',  # V1.0 Mini-MVP: 默认普通用户角色
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed due to data conflict"
        )


@router.post("/user-auth/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        
        if not user:
            # 记录登录失败事件（用户名不存在或密码错误）
            from app.core.security_logger import log_security_event
            log_security_event(
                event_type="login_failed",
                message="Login failed - invalid credentials",
                user_data={
                    "username": user_credentials.username,
                    "reason": "invalid_credentials"
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except AuthenticationError as e:
        # 处理账户锁定等认证错误
        from app.core.security_logger import log_security_event
        log_security_event(
            event_type="login_failed",
            message=f"Login failed - {str(e)}",
            user_data={
                "username": user_credentials.username,
                "reason": "authentication_error"
            }
        )
        
        if "locked" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    
    # 创建访问令牌和刷新令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/user-auth/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        payload = decode_token(token_data.refresh_token)
        
        # 检查令牌类型
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
        
        # 验证用户是否存在且激活
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # 创建新的访问令牌
        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/user-auth/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user


@router.put("/user-auth/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 检查邮箱是否已被其他用户使用
    if user_update.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another user"
            )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed due to data conflict"
        )


@router.put("/user-auth/password")
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    from app.core.auth import verify_password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    
    try:
        db.commit()
        return {"message": "Password changed successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/user-auth/logout")
async def logout_user(
    current_user: User = Depends(get_current_active_user)
):
    """用户登出"""
    # 注意：由于JWT是无状态的，真正的登出需要在客户端删除token
    # 或者实现token黑名单机制（需要Redis等外部存储）
    return {"message": "Logged out successfully"}


# 管理员相关路由（可选）
@router.get("/user-auth/users", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅限管理员）"""
    # 这里可以添加管理员权限检查
    # 暂时允许所有认证用户查看
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/user-auth/users/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """通过ID获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 只允许用户查看自己的信息，或者管理员查看所有用户
    if user.id != current_user.id:
        # 这里可以添加管理员权限检查
        pass
    
    return user
