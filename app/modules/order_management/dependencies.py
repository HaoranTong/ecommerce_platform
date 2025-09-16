"""
文件名：dependencies.py
文件路径：app/modules/order_management/dependencies.py
功能描述：订单管理模块的依赖注入定义

主要功能：
- 定义订单管理模块的依赖注入组件
- 提供服务层实例化和权限验证
- 管理模块间的依赖关系和权限控制
- 统一的错误处理和验证逻辑

使用说明：
- 导入：from app.modules.order_management.dependencies import get_order_service, validate_order_access
- FastAPI依赖：order_service: OrderService = Depends(get_order_service)
- 权限验证：current_user = Depends(get_current_user)
- 订单访问：order = Depends(validate_order_access)

依赖模块：
- app.modules.order_management.service.OrderService: 订单服务类
- app.modules.order_management.models: 订单数据模型
- app.core.database: 数据库会话管理
- app.core.auth: 用户认证和权限验证
- fastapi.Depends: FastAPI依赖注入装饰器

创建时间：2025-09-15
最后修改：2025-09-15
"""

from typing import Optional, Union
from fastapi import Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session

# 核心依赖
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_admin_user

# 模块内依赖
from .service import OrderService
from .models import Order
from app.modules.user_auth.models import User


# ============ 基础服务依赖 ============

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """
    获取订单管理服务实例
    
    Args:
        db (Session): 数据库会话实例
        
    Returns:
        OrderService: 订单管理服务实例
        
    Note:
        此依赖会在每次API调用时创建新的服务实例
        服务实例会自动注入数据库会话和库存服务
    """
    return OrderService(db)


# ============ 权限验证依赖 ============

def get_current_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前已认证用户
    
    提供标准化的用户认证依赖，确保用户已登录且账户状态正常
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        User: 已认证的用户对象
        
    Raises:
        HTTPException: 401 - 用户未认证或认证失败
    """
    return current_user


def get_current_admin_user_validated(admin_user: User = Depends(get_current_admin_user)) -> User:
    """
    获取当前管理员用户
    
    验证用户具有管理员权限，用于需要管理员权限的API
    
    Args:
        admin_user: 当前管理员用户
        
    Returns:
        User: 已验证的管理员用户对象
        
    Raises:
        HTTPException: 403 - 权限不足，非管理员用户
    """
    return admin_user


# ============ 订单访问权限验证 ============

async def validate_order_access(
    order_id: int = Path(..., ge=1, description="订单ID"),
    current_user: User = Depends(get_current_authenticated_user),
    order_service: OrderService = Depends(get_order_service)
) -> Order:
    """
    验证订单访问权限
    
    检查订单是否存在以及当前用户是否有权限访问该订单：
    - 普通用户只能访问自己的订单
    - 管理员可以访问所有订单
    
    Args:
        order_id: 订单ID
        current_user: 当前登录用户
        order_service: 订单服务实例
        
    Returns:
        Order: 验证通过的订单对象
        
    Raises:
        HTTPException: 
            - 404: 订单不存在
            - 403: 权限不足，无法访问该订单
    """
    # 获取订单
    order = await order_service.get_order_by_id(order_id=order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 权限验证：普通用户只能访问自己的订单
    if not _has_order_access_permission(order, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法访问该订单"
        )
    
    return order


def validate_order_modification_access(
    order_id: int = Path(..., ge=1, description="订单ID"),
    current_user: User = Depends(get_current_authenticated_user),
    order_service: OrderService = Depends(get_order_service)
) -> Order:
    """
    验证订单修改权限
    
    用于需要修改订单的API，通常需要管理员权限或订单所有者权限
    
    Args:
        order_id: 订单ID
        current_user: 当前登录用户
        order_service: 订单服务实例
        
    Returns:
        Order: 验证通过的订单对象
        
    Raises:
        HTTPException: 
            - 404: 订单不存在
            - 403: 权限不足，无法修改该订单
    """
    # 重用订单访问验证逻辑
    return validate_order_access(order_id, current_user, order_service)


# ============ 业务权限验证 ============

def validate_order_creation_permission(
    current_user: User = Depends(get_current_authenticated_user)
) -> User:
    """
    验证订单创建权限
    
    检查用户是否具有创建订单的权限
    通常所有已认证用户都可以创建订单
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        User: 已验证权限的用户对象
    """
    # 目前所有已认证用户都可以创建订单
    # 未来可以在这里添加额外的业务规则验证
    return current_user


def validate_order_status_update_permission(
    current_user: User = Depends(get_current_admin_user_validated)
) -> User:
    """
    验证订单状态更新权限
    
    只有管理员可以更新订单状态
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        User: 已验证权限的管理员用户对象
        
    Raises:
        HTTPException: 403 - 权限不足，非管理员用户
    """
    return current_user


# ============ 内部辅助函数 ============

def _has_order_access_permission(order: Order, user: User) -> bool:
    """
    检查用户是否有权限访问指定订单
    
    Args:
        order: 订单对象
        user: 用户对象
        
    Returns:
        bool: True if user has access permission
    """
    # 管理员可以访问所有订单
    if hasattr(user, 'role') and user.role in ['admin', 'super_admin']:
        return True
    
    # 普通用户只能访问自己的订单
    return order.user_id == user.id


def _is_admin_user(user: User) -> bool:
    """
    检查用户是否为管理员
    
    Args:
        user: 用户对象
        
    Returns:
        bool: True if user is admin
    """
    return hasattr(user, 'role') and user.role in ['admin', 'super_admin']


# ============ 复合依赖 ============

class OrderAccessValidator:
    """订单访问验证器类"""
    
    def __init__(self, require_admin: bool = False):
        self.require_admin = require_admin
    
    async def __call__(
        self,
        order_id: int = Path(..., ge=1),
        current_user: User = Depends(get_current_authenticated_user),
        order_service: OrderService = Depends(get_order_service)
    ) -> tuple[Order, User]:
        """
        执行订单访问验证
        
        Returns:
            tuple[Order, User]: 验证通过的订单和用户对象
        """
        if self.require_admin and not _is_admin_user(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        
        order = await validate_order_access(order_id, current_user, order_service)
        return order, current_user


# 创建常用的验证器实例
validate_order_admin_access = OrderAccessValidator(require_admin=True)
validate_order_user_access = OrderAccessValidator(require_admin=False)


async def validate_statistics_access_permission(
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_authenticated_user)
) -> None:
    """
    验证统计信息访问权限
    
    Args:
        user_id: 请求查询的用户ID
        current_user: 当前登录用户
        
    Raises:
        HTTPException: 权限验证失败
    """
    # 如果请求查询其他用户的统计信息，需要管理员权限
    if user_id and user_id != current_user.id:
        if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="普通用户只能查看自己的统计信息"
            )
