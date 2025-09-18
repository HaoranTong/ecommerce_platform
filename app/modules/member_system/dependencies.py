"""
文件名：dependencies.py
文件路径：app/modules/member_system/dependencies.py
功能描述：会员系统模块的FastAPI依赖注入组件
主要功能：
- 用户认证和权限验证
- 数据库会话管理
- 外部服务依赖注入
- 会员系统服务实例创建
使用说明：
- 导入：from app.modules.member_system.dependencies import get_member_service_dep, get_current_active_user
- 在路由中使用：member_service: MemberService = Depends(get_member_service_dep)
依赖模块：
- app.core.auth: 用户认证相关功能
- app.core.database: 数据库连接管理
- app.core.redis_client: Redis缓存客户端
创建时间：2025-09-18
最后修改：2025-09-18
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from redis import Redis

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.redis_client import get_redis_connection
from .service import (
    MemberService, PointService, BenefitService, EventService,
    get_member_service, get_point_service, get_benefit_service, get_event_service
)


# ================== 用户认证依赖 ==================

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: 当用户不存在或未激活时
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户未认证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态（假设User对象有is_active属性）
    if hasattr(current_user, 'is_active') and not getattr(current_user, 'is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return current_user


def get_user_id_from_token(
    current_user = Depends(get_current_active_user)
) -> int:
    """
    从JWT Token中提取用户ID
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户ID
        
    Raises:
        HTTPException: 当用户ID不存在时
    """
    # 处理用户对象，尝试获取ID
    user_id = None
    if hasattr(current_user, 'id'):
        user_id = current_user.id
    elif hasattr(current_user, 'user_id'):
        user_id = current_user.user_id
    elif isinstance(current_user, dict):
        user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户令牌"
        )
    
    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户ID格式错误"
        )


# ================== 服务层依赖注入 ==================

def get_member_service_dep(
    db: Session = Depends(get_db),
    redis_client: Optional[Redis] = Depends(get_redis_connection)
) -> MemberService:
    """
    获取会员服务依赖注入
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端
        
    Returns:
        MemberService: 会员服务实例
    """
    return get_member_service(db, redis_client)


def get_point_service_dep(
    db: Session = Depends(get_db),
    redis_client: Optional[Redis] = Depends(get_redis_connection)
) -> PointService:
    """
    获取积分服务依赖注入
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端
        
    Returns:
        PointService: 积分服务实例
    """
    return get_point_service(db, redis_client)


def get_benefit_service_dep(
    db: Session = Depends(get_db),
    redis_client: Optional[Redis] = Depends(get_redis_connection)
) -> BenefitService:
    """
    获取权益服务依赖注入
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端
        
    Returns:
        BenefitService: 权益服务实例
    """
    return get_benefit_service(db, redis_client)


def get_event_service_dep(
    db: Session = Depends(get_db),
    redis_client: Optional[Redis] = Depends(get_redis_connection)
) -> EventService:
    """
    获取活动服务依赖注入
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端
        
    Returns:
        EventService: 活动服务实例
    """
    return get_event_service(db, redis_client)


# ================== 业务规则验证 ==================

class MemberBusinessRules:
    """会员系统业务规则常量"""
    MAX_POINTS_PER_TRANSACTION = 100000     # 单次积分交易最大值
    MIN_POINTS_PER_TRANSACTION = 1          # 单次积分交易最小值
    MAX_MEMBER_CODE_LENGTH = 20             # 会员编号最大长度
    POINTS_EXPIRY_MONTHS = 24               # 积分过期月数
    MAX_BENEFIT_USAGE_PER_DAY = 10          # 每日最大权益使用次数


def validate_points_transaction(
    points: int,
    transaction_type: str
) -> None:
    """
    验证积分交易业务规则
    
    Args:
        points: 积分数量
        transaction_type: 交易类型
        
    Raises:
        HTTPException: 当违反业务规则时
    """
    if points <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="积分数量必须大于0"
        )
    
    if points > MemberBusinessRules.MAX_POINTS_PER_TRANSACTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"单次积分交易不能超过{MemberBusinessRules.MAX_POINTS_PER_TRANSACTION}分"
        )
    
    if transaction_type not in ["earn", "use", "expire", "freeze", "unfreeze"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的积分交易类型"
        )


def validate_member_data(
    member_data: Dict[str, Any]
) -> None:
    """
    验证会员数据业务规则
    
    Args:
        member_data: 会员数据
        
    Raises:
        HTTPException: 当违反业务规则时
    """
    if not member_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会员数据不能为空"
        )
    
    # 验证生日格式
    if "birthday" in member_data and member_data["birthday"]:
        try:
            from datetime import datetime
            datetime.fromisoformat(member_data["birthday"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="生日日期格式错误，请使用YYYY-MM-DD格式"
            )
