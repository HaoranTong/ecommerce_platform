"""
用户认证相关API路由
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.modules.user_auth.models import User
from app.modules.user_auth.schemas import (
    StandardResponse,
    Token,
    TokenRefresh,
    UserChangePassword,
    UserLogin,
    PhoneLogin,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserRead,
    UserRegister,
    UserRegisterResponse,
    UserUpdate,
    SendVerificationCode,
)
from app.modules.user_auth.service import UserService

router = APIRouter()


@router.post(
    "/user-auth/verification-code",
    response_model=StandardResponse[dict],
    summary="发送验证码",
    description="发送邮箱或短信验证码，用于注册、登录、重置密码或手机号登录"
)
async def send_verification_code(
    request: SendVerificationCode,
    db: Session = Depends(get_db)
):
    """发送验证码"""
    result = await UserService.send_verification_code(
        db=db,
        email=request.email,
        phone=request.phone,
        code_type=request.code_type
    )
    return StandardResponse(
        success=True,
        code=200,
        message="验证码发送成功",
        data=result
    )


@router.post(
    "/user-auth/register",
    response_model=StandardResponse[UserRegisterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="用户注册，需要先调用发送验证码接口获取验证码"
)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    result = await UserService.register_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        verification_code=user_data.verification_code,
        phone=user_data.phone,
        real_name=user_data.real_name,
    )
    return StandardResponse(
        success=True,
        code=201,
        message="注册成功",
        data=result
    )


@router.post(
    "/user-auth/login",
    response_model=StandardResponse[Token],
    summary="用户登录",
    description="用户登录，使用用户名/邮箱和密码。登录失败3次后需要提供验证码"
)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录（密码登录）"""
    result = await UserService.login_user(
        db=db,
        username=user_credentials.username,
        password=user_credentials.password,
        verification_code=user_credentials.verification_code,
    )
    return StandardResponse(
        success=True,
        code=200,
        message="登录成功",
        data=result
    )


@router.post(
    "/user-auth/phone-login",
    response_model=StandardResponse[Token],
    summary="手机号验证码登录",
    description="使用手机号和短信验证码登录"
)
async def phone_login(credentials: PhoneLogin, db: Session = Depends(get_db)):
    """手机号验证码登录"""
    result = await UserService.phone_login(
        db=db,
        phone=credentials.phone,
        verification_code=credentials.verification_code,
    )
    return StandardResponse(
        success=True,
        code=200,
        message="登录成功",
        data=result
    )


@router.post(
    "/user-auth/refresh",
    response_model=StandardResponse[Token],
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌"
)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """刷新访问令牌"""
    result = UserService.refresh_access_token(
        db=db,
        refresh_token=token_data.refresh_token,
    )
    return StandardResponse(
        success=True,
        code=200,
        message="令牌刷新成功",
        data=result
    )


@router.get(
    "/user-auth/me",
    response_model=StandardResponse[UserRead],
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息。需要有效的JWT Token认证。返回用户的基本信息、角色、权限状态等。"
)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息（需要JWT Token认证）"""
    return StandardResponse(
        success=True,
        code=200,
        message="获取用户信息成功",
        data=current_user
    )


@router.put(
    "/user-auth/me",
    response_model=StandardResponse[UserRead],
    summary="更新当前用户信息",
    description="更新当前登录用户的个人信息"
)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新当前用户信息"""
    result = UserService.update_user_info(
        db=db,
        user_id=current_user.id,
        email=user_update.email,
        phone=user_update.phone,
        real_name=user_update.real_name,
    )
    return StandardResponse(
        success=True,
        code=200,
        message="用户信息更新成功",
        data=result
    )


@router.put(
    "/user-auth/password",
    response_model=StandardResponse[dict],
    summary="修改密码",
    description="修改当前用户的登录密码（需要登录）"
)
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    result = UserService.change_user_password(
        db=db,
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    return StandardResponse(
        success=True,
        code=200,
        message="密码修改成功",
        data=result
    )


@router.post(
    "/user-auth/password/reset-request",
    response_model=StandardResponse[dict],
    summary="请求重置密码",
    description="忘记密码时，请求发送重置密码的验证码到邮箱"
)
async def reset_password_request(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """请求重置密码"""
    result = await UserService.reset_password_request(
        db=db,
        email=request.email
    )
    return StandardResponse(
        success=True,
        code=200,
        message="重置密码验证码已发送",
        data=result
    )


@router.post(
    "/user-auth/password/reset-confirm",
    response_model=StandardResponse[dict],
    summary="确认重置密码",
    description="使用验证码重置密码"
)
async def reset_password_confirm(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """确认重置密码"""
    result = await UserService.reset_password_confirm(
        db=db,
        email=request.email,
        verification_code=request.verification_code,
        new_password=request.new_password
    )
    return StandardResponse(
        success=True,
        code=200,
        message="密码重置成功",
        data=result
    )


@router.post(
    "/user-auth/logout",
    response_model=StandardResponse[dict],
    summary="用户登出",
    description="用户登出（客户端需删除token）"
)
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """用户登出"""
    # 注意：由于JWT是无状态的，真正的登出需要在客户端删除token
    # 或者实现token黑名单机制（需要Redis等外部存储）
    return StandardResponse(
        success=True,
        code=200,
        message="登出成功",
        data={"message": "Logged out successfully"}
    )


# 管理员相关路由（可选）
@router.get(
    "/user-auth/users",
    response_model=StandardResponse[list[UserRead]],
    summary="获取用户列表",
    description="获取系统用户列表，支持分页查询。需要管理员权限（V1.0暂时允许所有认证用户访问，V2.0将增加权限控制）。返回用户的基本信息列表，不包含敏感信息如密码哈希。"
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户列表（需要JWT Token认证，V2.0将限制为管理员权限）"""
    # 这里可以添加管理员权限检查
    # 暂时允许所有认证用户查看
    result = UserService.get_user_list(db=db, skip=skip, limit=limit)
    return StandardResponse(
        success=True,
        code=200,
        message="获取用户列表成功",
        data=result,
        metadata={"skip": skip, "limit": limit, "total": len(result)}
    )


@router.get(
    "/user-auth/users/{user_id}",
    response_model=StandardResponse[UserRead],
    summary="通过ID获取用户信息",
    description="通过用户ID获取指定用户的详细信息。需要管理员权限（V1.0暂时允许所有认证用户访问，V2.0将增加权限控制）。如果用户不存在返回404错误。"
)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """通过ID获取用户信息"""
    user = UserService.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 只允许用户查看自己的信息，或者管理员查看所有用户
    if user.id != current_user.id:
        # 这里可以添加管理员权限检查
        pass

    return StandardResponse(
        success=True,
        code=200,
        message="获取用户信息成功",
        data=user
    )
