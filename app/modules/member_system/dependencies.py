"""
会员系统模块的FastAPI依赖注入组件

提供会员系统相关的服务依赖注入，确保在API路由中能够正确获取服务实例。
遵循四层架构设计，支持依赖注入和单元测试。
"""

from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db

from .service import MemberService, PointService, LevelService, BenefitService


def _resolve_user_id(current_user: Any) -> Optional[int]:
    if isinstance(current_user, dict):
        return current_user.get("user_id") or current_user.get("id")
    return getattr(current_user, "id", None) or getattr(current_user, "user_id", None)


# ================== 用户认证依赖 ==================


async def get_current_active_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 用户状态异常时抛出
    """
    is_active = (
        current_user.get("is_active", True)
        if isinstance(current_user, dict)
        else getattr(current_user, "is_active", True)
    )
    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user


async def get_current_member_user(
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取当前会员用户（确保用户已是会员）
    
    Args:
        current_user: 当前用户信息
        db: 数据库会话
        
    Returns:
        会员用户信息字典
        
    Raises:
        HTTPException: 用户不是会员时抛出
    """
    # 检查用户是否已是会员
    member_service = MemberService(db)
    user_id = _resolve_user_id(current_user)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未能识别当前用户",
        )

    member_profile = member_service.get_member_profile(user_id)
    
    if not member_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户不是会员，无法访问会员功能"
        )
    
    return current_user


# ================== 服务依赖注入 ==================


def get_member_service(
    db: Session = Depends(get_db),
    redis_client: Optional[Any] = None,
) -> MemberService:
    """
    获取会员服务实例
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端（可选）
        
    Returns:
        会员服务实例
    """
    return MemberService(db, redis_client)


def get_point_service(
    db: Session = Depends(get_db),
    redis_client: Optional[Any] = None,
) -> PointService:
    """
    获取积分服务实例
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端（可选）
        
    Returns:
        积分服务实例
    """
    return PointService(db, redis_client)


def get_level_service(
    db: Session = Depends(get_db),
    redis_client: Optional[Any] = None,
) -> LevelService:
    """
    获取等级服务实例
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端（可选）
        
    Returns:
        等级服务实例
    """
    return LevelService(db, redis_client)


def get_benefit_service(
    db: Session = Depends(get_db),
    redis_client: Optional[Any] = None,
) -> BenefitService:
    """
    获取权益服务实例
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端（可选）
        
    Returns:
        权益服务实例
    """
    return BenefitService(db, redis_client)


# ================== 权限验证依赖 ==================


async def verify_member_access(
    user_id: int,
    current_user: Any = Depends(get_current_active_user),
) -> bool:
    """
    验证会员访问权限
    
    Args:
        user_id: 要访问的用户ID
        current_user: 当前用户信息
        
    Returns:
        是否有权限访问
        
    Raises:
        HTTPException: 权限不足时抛出
    """
    # 用户只能访问自己的信息，除非是管理员
    current_user_id = _resolve_user_id(current_user)
    is_admin = (
        current_user.get("is_admin", False)
        if isinstance(current_user, dict)
        else getattr(current_user, "is_admin", False)
    )
    if current_user_id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法访问其他用户信息"
        )
    return True


# ================== 业务验证依赖 ==================


async def validate_point_operation(
    points: int,
    operation_type: str = "earn",
) -> int:
    """
    验证积分操作参数
    
    Args:
        points: 积分数量
        operation_type: 操作类型
        
    Returns:
        验证通过的积分数量
        
    Raises:
        HTTPException: 参数无效时抛出
    """
    if points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="积分数量必须大于0"
        )
    
    # 设置积分操作的上限
    max_points = 100000 if operation_type == "earn" else 50000
    if points > max_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"单次{operation_type}积分数量不能超过{max_points}"
        )
    
    return points


# ================== 导出依赖列表 ==================

__all__ = [
    "get_current_active_user",
    "get_current_member_user",
    "get_member_service",
    "get_point_service", 
    "get_level_service",
    "verify_member_access",
    "validate_point_operation",
]