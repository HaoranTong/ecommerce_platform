"""
文件名：dependencies.py
文件路径：app/modules/shopping_cart/dependencies.py
功能描述：购物车模块的FastAPI依赖注入组件
主要功能：
- 用户认证和权限验证
- 数据库会话管理
- 外部服务依赖注入
- 购物车服务实例创建
使用说明：
- 导入：from app.modules.shopping_cart.dependencies import get_cart_service, get_current_user
- 在路由中使用：cart_service: CartService = Depends(get_cart_service)
依赖模块：
- app.core.auth: 用户认证相关功能
- app.core.database: 数据库连接管理
- app.core.redis_client: Redis缓存客户端
创建时间：2025-09-16
最后修改：2025-09-16
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from redis import Redis

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.redis_client import get_redis_connection
from .service import CartService


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
    
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号未激活"
        )
    
    return current_user


def get_cart_service(
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_connection)
) -> CartService:
    """
    获取购物车服务实例
    
    Args:
        db: 数据库会话
        redis_client: Redis客户端
        
    Returns:
        CartService实例
    """
    return CartService(db=db, redis_client=redis_client)


# 业务规则常量
class CartBusinessRules:
    """购物车业务规则常量"""
    MAX_ITEMS_PER_CART = 50      # 购物车最大商品种类数
    MAX_QUANTITY_PER_ITEM = 999  # 单商品最大数量
    MIN_QUANTITY_PER_ITEM = 1    # 单商品最小数量
    CACHE_TTL = 3600            # 缓存过期时间(秒)


def validate_cart_business_rules(
    total_items: int,
    quantity: int
) -> None:
    """
    验证购物车业务规则
    
    Args:
        total_items: 购物车当前商品种类数
        quantity: 商品数量
        
    Raises:
        HTTPException: 当违反业务规则时
    """
    if total_items >= CartBusinessRules.MAX_ITEMS_PER_CART:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"购物车商品种类不能超过{CartBusinessRules.MAX_ITEMS_PER_CART}个"
        )
    
    if not (CartBusinessRules.MIN_QUANTITY_PER_ITEM <= quantity <= CartBusinessRules.MAX_QUANTITY_PER_ITEM):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"商品数量必须在{CartBusinessRules.MIN_QUANTITY_PER_ITEM}-{CartBusinessRules.MAX_QUANTITY_PER_ITEM}之间"
        )


def get_user_id_from_token(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
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
    user_id = current_user.get("sub") or current_user.get("user_id")
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
