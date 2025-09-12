"""
库存管理模块 API 路由

此模块定义了库存管理相关的API端点，包括：
- 库存查询接口
- 库存预占和释放接口
- 库存扣减接口
- 库存管理接口（管理员）
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, get_current_admin_user
from app.database import get_db
from app.models import User
from app.services.inventory import InventoryService
from app.schemas.inventory import (
    InventoryRead, InventorySimple, BatchInventoryQuery,
    CartReserveRequest, OrderReserveRequest, ReservationResponse,
    InventoryDeductRequest, InventoryAdjustment, ThresholdUpdate,
    TransactionQuery, InventoryTransactionRead, LowStockQuery,
    LowStockItem, PaginatedResponse
)

router = APIRouter()


# ============ 库存查询接口 ============

@router.get("/{product_id}", response_model=InventoryRead, summary="获取商品库存信息")
async def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定商品的库存信息
    
    - **product_id**: 商品ID
    
    返回商品的详细库存信息，包括可用数量、预占数量、总数量等
    """
    service = InventoryService(db)
    inventory = service.get_or_create_inventory(product_id)
    return inventory


@router.post("/batch", response_model=List[InventorySimple], summary="批量获取商品库存")
async def get_inventories_batch(
    query: BatchInventoryQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量获取多个商品的库存信息
    
    - **product_ids**: 商品ID列表（最多100个）
    
    返回所有请求商品的库存信息列表
    """
    service = InventoryService(db)
    inventories = service.get_inventories_batch(query.product_ids)
    
    # 构造响应数据
    result = []
    for inventory in inventories:
        result.append(InventorySimple(
            product_id=inventory.product_id,
            available_quantity=inventory.available_quantity,
            reserved_quantity=inventory.reserved_quantity,
            total_quantity=inventory.total_quantity,
            is_low_stock=inventory.is_low_stock
        ))
    
    return result


# ============ 库存预占接口 ============

@router.post("/reserve/cart", response_model=ReservationResponse, summary="购物车库存预占")
async def reserve_cart_inventory(
    request: CartReserveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为购物车商品预占库存
    
    - **items**: 需要预占的商品列表
    - **expires_minutes**: 预占过期时间（分钟，默认30分钟）
    
    预占成功后返回预占ID和过期时间
    """
    service = InventoryService(db)
    result = service.reserve_for_cart(
        user_id=current_user.id,
        items=request.items,
        expires_minutes=request.expires_minutes or 30
    )
    return ReservationResponse(**result)


@router.post("/reserve/order", response_model=ReservationResponse, summary="订单库存预占")
async def reserve_order_inventory(
    request: OrderReserveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为订单预占库存
    
    - **order_id**: 订单ID
    - **items**: 需要预占的商品列表
    
    预占成功后返回预占ID和过期时间（默认15分钟）
    """
    service = InventoryService(db)
    result = service.reserve_for_order(
        order_id=request.order_id,
        items=request.items
    )
    return ReservationResponse(**result)


@router.delete("/reserve/cart", summary="释放购物车预占")
async def release_cart_reservation(
    product_ids: List[int] = Query(None, description="要释放的商品ID列表，不传则释放所有"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    释放购物车的库存预占
    
    - **product_ids**: 要释放的商品ID列表（可选，不传则释放当前用户所有预占）
    
    释放成功返回true
    """
    service = InventoryService(db)
    success = service.release_cart_reservation(
        user_id=current_user.id,
        product_ids=product_ids
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="释放预占失败"
        )
    
    return {"code": 200, "message": "释放预占成功"}


@router.delete("/reserve/order/{order_id}", summary="释放订单预占")
async def release_order_reservation(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    释放订单的库存预占
    
    - **order_id**: 订单ID
    
    释放成功返回true
    """
    service = InventoryService(db)
    success = service.release_order_reservation(order_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单预占记录不存在"
        )
    
    return {"code": 200, "message": "释放预占成功"}


# ============ 库存扣减接口 ============

@router.post("/deduct", summary="订单完成库存扣减")
async def deduct_inventory(
    request: InventoryDeductRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 仅管理员或系统调用
):
    """
    订单支付完成后扣减库存
    
    - **order_id**: 订单ID
    - **items**: 需要扣减的商品列表
    
    扣减成功返回true
    """
    service = InventoryService(db)
    success = service.deduct_inventory(
        order_id=request.order_id,
        items=request.items
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存扣减失败"
        )
    
    return {"code": 200, "message": "库存扣减成功"}


# ============ 库存管理接口（管理员） ============

@router.put("/{product_id}/adjust", summary="库存调整")
async def adjust_inventory(
    product_id: int,
    adjustment: InventoryAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    管理员手动调整库存
    
    - **product_id**: 商品ID
    - **adjustment_type**: 调整类型（ADD/SUBTRACT/SET）
    - **quantity**: 调整数量
    - **reason**: 调整原因
    
    调整成功返回更新后的库存信息
    """
    service = InventoryService(db)
    success = service.adjust_inventory(
        product_id=product_id,
        adjustment=adjustment,
        operator_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存调整失败"
        )
    
    # 返回更新后的库存信息
    inventory = service.get_inventory(product_id)
    return inventory


@router.put("/{product_id}/threshold", summary="设置预警阈值")
async def update_warning_threshold(
    product_id: int,
    threshold_update: ThresholdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    设置商品库存预警阈值
    
    - **product_id**: 商品ID
    - **warning_threshold**: 预警阈值
    
    设置成功返回更新后的库存信息
    """
    service = InventoryService(db)
    success = service.update_warning_threshold(
        product_id=product_id,
        threshold=threshold_update.warning_threshold
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="预警阈值设置失败"
        )
    
    # 返回更新后的库存信息
    inventory = service.get_inventory(product_id)
    return inventory


@router.get("/low-stock", response_model=PaginatedResponse, summary="获取低库存商品列表")
async def get_low_stock_products(
    query: LowStockQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取低于预警阈值的商品列表
    
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    
    返回低库存商品的分页列表
    """
    service = InventoryService(db)
    items, total = service.get_low_stock_products(
        page=query.page,
        page_size=query.page_size
    )
    
    total_pages = (total + query.page_size - 1) // query.page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=total_pages
    )


@router.get("/{product_id}/transactions", response_model=PaginatedResponse, summary="获取库存变动历史")
async def get_inventory_transactions(
    product_id: int,
    query: TransactionQuery = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取商品库存变动历史记录
    
    - **product_id**: 商品ID
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    - **transaction_type**: 变动类型筛选（可选）
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    
    返回库存变动记录的分页列表
    """
    service = InventoryService(db)
    items, total = service.get_inventory_transactions(
        product_id=product_id,
        query_params=query
    )
    
    total_pages = (total + query.page_size - 1) // query.page_size
    
    # 转换为响应格式
    transaction_items = []
    for item in items:
        transaction_items.append({
            "id": item.id,
            "product_id": item.product_id,
            "transaction_type": item.transaction_type,
            "quantity": item.quantity,
            "reference_type": item.reference_type,
            "reference_id": item.reference_id,
            "reason": item.reason,
            "before_quantity": item.before_quantity,
            "after_quantity": item.after_quantity,
            "operator_id": item.operator_id,
            "created_at": item.created_at
        })
    
    return PaginatedResponse(
        items=transaction_items,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=total_pages
    )


# ============ 系统维护接口 ============

@router.post("/cleanup/expired-reservations", summary="清理过期预占")
async def cleanup_expired_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    清理过期的购物车预占记录
    
    这是一个维护接口，通常由定时任务调用
    返回清理的预占记录数量
    """
    service = InventoryService(db)
    cleaned_count = service.cleanup_expired_reservations()
    
    return {
        "code": 200,
        "message": "清理完成",
        "data": {
            "cleaned_count": cleaned_count
        }
    }