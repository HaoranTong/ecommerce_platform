"""
文件名：router.py
文件路径：app/modules/order_management/router.py
功能描述：订单管理模块的API路由定义

主要功能：
- 订单全生命周期管理API接口
- 权限控制和用户认证集成
- 标准化的错误处理和响应格式
- RESTful API设计原则实现

使用说明：
- 导入：from app.modules.order_management import router
- 路由前缀：/orders (在主应用中挂载时添加/api/v1前缀)
- 认证要求：所有接口都需要JWT认证
- 权限控制：用户只能访问自己的订单，管理员可访问所有订单

依赖模块：
- app.modules.order_management.service.OrderService: 业务逻辑服务
- app.modules.order_management.schemas: API请求响应模型
- app.modules.order_management.dependencies: 依赖注入定义
- app.core.auth: 用户认证和权限验证

创建时间：2025-09-15
最后修改：2025-09-15
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from .service import OrderService
from .models import Order, OrderStatus
from ..user_auth.models import User
from .schemas import (
    OrderCreateRequest, OrderResponse, OrderListResponse, 
    OrderStatusUpdateRequest, OrderItemResponse, ApiResponse,
    PaginatedResponse, OrderDetailResponse, OrderStatisticsResponse
)
from .dependencies import (
    get_order_service, get_current_authenticated_user, get_current_admin_user_validated,
    validate_order_access, validate_order_creation_permission,
    validate_order_status_update_permission, validate_statistics_access_permission
)

router = APIRouter()


@router.post("/", response_model=ApiResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreateRequest,
    order_service: OrderService = Depends(get_order_service),
    current_user = Depends(validate_order_creation_permission)
):
    """
    创建新订单
    
    创建订单的完整流程：
    1. 验证用户权限（用户只能为自己创建订单）
    2. 验证商品信息和库存
    3. 预占库存
    4. 创建订单和订单项
    5. 返回订单详情
    
    Args:
        order_data: 订单创建请求数据
        order_service: 订单服务实例（依赖注入）
        current_user: 当前登录用户（认证依赖）
        
    Returns:
        ApiResponse[OrderResponse]: 标准化的API响应，包含创建的订单信息
        
    Raises:
        HTTPException: 
            - 403: 权限不足（尝试为他人创建订单）
            - 404: 用户或商品不存在
            - 400: 库存不足或其他业务异常
            - 500: 服务器内部错误
    """
    try:
        # 创建订单（服务层已包含完整的权限验证和业务逻辑）
        order = await order_service.create_order(
            order_data=order_data,
            user_id=current_user.id
        )
        
        # 转换为响应模型
        order_response = OrderResponse.model_validate(order)
        
        return ApiResponse[OrderResponse](
            success=True,
            message="订单创建成功",
            data=order_response
        )
        
    except HTTPException:
        # 重新抛出HTTP异常（由服务层抛出的业务异常）
        raise
    except Exception as e:
        # 捕获未处理的异常并包装
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/", response_model=ApiResponse[PaginatedResponse[OrderListResponse]])
async def list_orders(
    status_filter: Optional[OrderStatus] = Query(None, description="订单状态筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选（仅管理员可用）"),
    page: int = Query(1, ge=1, le=1000, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_service: OrderService = Depends(get_order_service),
    current_user = Depends(get_current_authenticated_user)
):
    """
    获取订单列表
    
    支持分页查询和状态筛选：
    - 普通用户只能查看自己的订单
    - 管理员可以查看所有订单，并支持按用户ID筛选
    - 支持按订单状态筛选
    - 支持分页查询
    
    Args:
        status_filter: 订单状态筛选（可选）
        user_id: 用户ID筛选（仅管理员可用）
        page: 页码，从1开始
        page_size: 每页数量，最大100
        order_service: 订单服务实例
        current_user: 当前登录用户
        
    Returns:
        ApiResponse[PaginatedResponse[OrderListResponse]]: 分页的订单列表
        
    Raises:
        HTTPException: 
            - 403: 普通用户尝试查看其他用户订单
            - 500: 服务器内部错误
    """
    try:
        # 权限验证：普通用户只能查看自己的订单
        query_user_id = current_user.id
        if user_id and user_id != current_user.id:
            # 只有管理员可以查看其他用户的订单
            if not hasattr(current_user, 'role') or current_user.role not in ['admin', 'super_admin']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="普通用户只能查看自己的订单"
                )
            query_user_id = user_id
        
        # 计算分页参数
        skip = (page - 1) * page_size
        
        # 获取订单列表
        orders = await order_service.get_orders_list(
            user_id=query_user_id,
            status=status_filter,
            skip=skip,
            limit=page_size
        )
        
        # 转换为响应模型
        order_list = [OrderListResponse.model_validate(order) for order in orders]
        
        # 构造分页响应
        paginated_response = PaginatedResponse[OrderListResponse](
            items=order_list,
            page=page,
            page_size=page_size,
            total_count=len(order_list)  # 简化实现，实际应该查询总数
        )
        
        return ApiResponse[PaginatedResponse[OrderListResponse]](
            success=True,
            message="获取订单列表成功",
            data=paginated_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
async def get_order_detail(
    order: Order = Depends(validate_order_access)
):
    """
    获取订单详情
    
    根据订单ID获取完整的订单信息，包括订单项详情。
    权限验证通过依赖注入自动处理，确保用户只能访问有权限的订单。
    
    Args:
        order: 已验证权限的订单对象（通过依赖注入）
        
    Returns:
        ApiResponse[OrderResponse]: 包含订单详情的标准化响应
        
    Raises:
        HTTPException: 
            - 404: 订单不存在（由依赖注入处理）
            - 403: 无权限访问该订单（由依赖注入处理）
            - 500: 服务器内部错误
    """
    try:
        # 转换为响应模型
        order_response = OrderResponse.model_validate(order)
        
        return ApiResponse[OrderResponse](
            success=True,
            message="获取订单详情成功",
            data=order_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单详情失败: {str(e)}"
        )


@router.patch("/{order_id}/status", response_model=ApiResponse[OrderResponse])
async def update_order_status(
    order_id: int = Path(..., ge=1, description="订单ID"),
    status_update: OrderStatusUpdateRequest = ...,
    order_service: OrderService = Depends(get_order_service),
    current_admin = Depends(validate_order_status_update_permission)
):
    """
    更新订单状态
    
    更新指定订单的状态，执行相关的业务逻辑：
    - 需要管理员权限
    - 验证状态转换的合法性
    - 执行状态变更相关的业务逻辑（如库存操作）
    - 记录状态变更历史
    
    Args:
        order_id: 订单ID
        status_update: 状态更新请求数据
        order_service: 订单服务实例
        current_admin: 当前管理员用户（权限验证）
        
    Returns:
        ApiResponse[OrderResponse]: 更新后的订单信息
        
    Raises:
        HTTPException: 
            - 404: 订单不存在
            - 400: 状态转换不合法
            - 403: 权限不足（非管理员）
            - 500: 服务器内部错误
    """
    try:
        # 更新订单状态（服务层包含完整的业务逻辑和验证）
        updated_order = await order_service.update_order_status(
            order_id=order_id,
            new_status=status_update.status,
            operator_id=current_admin.id,
            remark=status_update.remark
        )
        
        if not updated_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 转换为响应模型
        order_response = OrderResponse.model_validate(updated_order)
        
        return ApiResponse[OrderResponse](
            success=True,
            message=f"订单状态已更新为 {status_update.status.value}",
            data=order_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新订单状态失败: {str(e)}"
        )


@router.post("/{order_id}/cancel", response_model=ApiResponse[dict])
async def cancel_order(
    order: Order = Depends(validate_order_access),
    order_service: OrderService = Depends(get_order_service),
    current_user = Depends(get_current_authenticated_user)
):
    """
    取消订单
    
    用户可以取消自己的订单，管理员可以取消任何订单：
    - 只有待支付状态的订单可以取消
    - 取消订单会自动释放预占的库存
    - 记录取消操作的历史
    
    Args:
        order_id: 订单ID
        order_service: 订单服务实例
        current_user: 当前登录用户
        
    Returns:
        ApiResponse[dict]: 取消结果信息
        
    Raises:
        HTTPException: 
            - 404: 订单不存在
            - 403: 无权限取消该订单
            - 400: 订单状态不允许取消
            - 500: 服务器内部错误
    """
    try:
        # 取消订单（权限验证已通过依赖注入完成）
        success = await order_service.cancel_order(
            order_id=order.id,
            operator_id=current_user.id,
            reason="用户主动取消"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单无法取消"
            )
        
        return ApiResponse[dict](
            success=True,
            message="订单取消成功",
            data={"order_id": order.id, "cancelled_at": "now"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消订单失败: {str(e)}"
        )


@router.get("/{order_id}/items", response_model=ApiResponse[List[OrderItemResponse]])
async def get_order_items(
    order: Order = Depends(validate_order_access),
    current_user: User = Depends(get_current_authenticated_user),
    order_service: OrderService = Depends(get_order_service)
):
    """
    获取订单商品列表
    
    获取指定订单的所有商品项信息。
    用户只能查看自己订单的商品项，管理员可以查看所有订单的商品项。
    
    Args:
        order_id: 订单ID
        order_service: 订单服务实例
        current_user: 当前登录用户
        
    Returns:
        ApiResponse[List[OrderItemResponse]]: 订单商品项列表
        
    Raises:
        HTTPException: 
            - 404: 订单不存在
            - 403: 无权限访问该订单
            - 500: 服务器内部错误
    """
    try:
        # 获取订单商品项列表（权限验证已通过依赖注入完成）
        order_items = await order_service.get_order_items(
            order_id=order.id,
            user_id=None  # 依赖注入已确保用户有访问权限
        )
        
        # 转换为响应模型
        items_response = [OrderItemResponse.model_validate(item) for item in order_items]
        
        return ApiResponse[List[OrderItemResponse]](
            success=True,
            message="获取订单商品列表成功",
            data=items_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单商品列表失败: {str(e)}"
        )


@router.get("/{order_id}/history", response_model=ApiResponse[List[dict]])
async def get_order_status_history(
    order: Order = Depends(validate_order_access),
    current_user: User = Depends(get_current_authenticated_user),
    order_service: OrderService = Depends(get_order_service)
):
    """
    获取订单状态变更历史
    
    Args:
        order_id: 订单ID
        order_service: 订单服务实例
        current_user: 当前登录用户
        
    Returns:
        ApiResponse[List[dict]]: 状态变更历史列表
    """
    try:
        # 获取状态变更历史（权限验证已通过依赖注入完成）
        history = await order_service.get_order_status_history(order_id=order.id)
        
        # 转换为简单的字典格式
        history_data = [
            {
                "old_status": h.old_status,
                "new_status": h.new_status,
                "remark": h.remark,
                "operator_id": h.operator_id,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in history
        ]
        
        return ApiResponse[List[dict]](
            success=True,
            message="获取状态变更历史成功",
            data=history_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取状态变更历史失败: {str(e)}"
        )


@router.get("/statistics", response_model=ApiResponse[OrderStatisticsResponse])
async def get_order_statistics(
    user_id: Optional[int] = Query(None, description="用户ID（仅管理员可用）"),
    current_user: User = Depends(get_current_authenticated_user),
    order_service: OrderService = Depends(get_order_service),
    _: None = Depends(validate_statistics_access_permission)
):
    """
    获取订单统计信息
    
    Args:
        user_id: 用户ID筛选（仅管理员可用）
        order_service: 订单服务实例
        current_user: 当前登录用户
        
    Returns:
        ApiResponse[OrderStatisticsResponse]: 订单统计数据
    """
    try:
        # 确定查询的用户ID（权限验证已通过依赖注入完成）
        query_user_id = user_id if user_id and hasattr(current_user, 'role') and \
                        current_user.role in ['admin', 'super_admin'] else current_user.id
        
        # 获取统计信息
        statistics = await order_service.calculate_order_statistics(user_id=query_user_id)
        
        # 转换为响应模型
        stats_response = OrderStatisticsResponse.model_validate(statistics)
        
        return ApiResponse[OrderStatisticsResponse](
            success=True,
            message="获取统计信息成功",
            data=stats_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
