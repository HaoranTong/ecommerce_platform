"""
文件名：user.py
文件路径：app/api/routes/user.py
功能描述：用户管理相关的API路由定义
主要功能：
- 用户注册、登录、登出
- 用户信息查询、更新、删除
- 用户权限管理和状态管理
- 用户统计和批量操作
使用说明：
- 路由前缀：/api/v1/users
- 认证要求：部分接口需要JWT认证
- 权限控制：管理员接口需要admin权限
依赖模块：
- app.services.UserService: 用户业务逻辑服务
- app.schemas.user: 用户相关输入输出模式
- app.auth: 用户认证和权限控制
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserRead, UserRegister, UserLogin, 
    UserChangePassword, Token, UserStats, UserPublic
)
from app.services import UserService
from app.auth import get_current_active_user, get_current_admin_user, create_access_token

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册
    
    - 创建新用户账户
    - 验证用户名和邮箱唯一性
    - 密码加密存储
    """
    try:
        user = UserService.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            phone=user_data.phone,
            real_name=user_data.real_name
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="用户注册失败")


@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    
    - 验证用户名/邮箱和密码
    - 返回JWT访问令牌和刷新令牌
    """
    user = UserService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成访问令牌
    tokens = UserService.generate_tokens(user)
    
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=3600  # 1小时
    )


@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    获取当前用户信息
    
    - 需要JWT认证
    - 返回当前登录用户的详细信息
    """
    return current_user


@router.put("/me", response_model=UserRead)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    更新当前用户信息
    
    - 需要JWT认证
    - 用户只能更新自己的信息
    """
    user = UserService.update_user(
        db=db,
        user_id=current_user.id,
        email=user_update.email,
        phone=user_update.phone,
        real_name=user_update.real_name
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/me/password")
def change_password(
    password_data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    修改当前用户密码
    
    - 需要JWT认证
    - 验证原密码正确性
    """
    success = UserService.change_password(
        db=db,
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail="原密码错误")
    
    return {"message": "密码修改成功"}


@router.get("", response_model=List[UserRead])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取用户列表
    
    - 需要管理员权限
    - 支持分页和筛选
    """
    users = UserService.get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active
    )
    return users


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    创建用户
    
    - 需要管理员权限
    - 可指定用户角色和状态
    """
    try:
        user = UserService.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password or "123456",  # 默认密码
            phone=user_data.phone,
            real_name=user_data.real_name,
            role=user_data.role,
            is_active=user_data.is_active
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="用户创建失败")


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    根据ID获取用户信息
    
    - 需要管理员权限
    """
    user = UserService.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新用户信息
    
    - 需要管理员权限
    """
    user = UserService.update_user(
        db=db,
        user_id=user_id,
        email=user_update.email,
        phone=user_update.phone,
        real_name=user_update.real_name
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    删除用户
    
    - 需要管理员权限
    - 软删除或硬删除
    """
    success = UserService.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return None


@router.get("/stats/overview", response_model=UserStats)
def get_user_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取用户统计信息
    
    - 需要管理员权限
    - 返回用户数量、活跃度等统计
    """
    stats = UserService.get_user_statistics(db=db)
    return stats