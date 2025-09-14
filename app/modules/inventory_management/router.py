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

from app.core.auth import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.modules.user_auth.models import User
from .service import InventoryService
from .schemas import (
    InventoryRead, InventorySimple, BatchInventoryQuery,
    CartReserveRequest, OrderReserveRequest, ReservationResponse,
    InventoryDeductRequest, InventoryAdjustment, ThresholdUpdate,
    TransactionQuery, InventoryTransactionRead, LowStockQuery,
    LowStockItem, PaginatedResponse
)

router = APIRouter()


# ============ 库存查询接口 ============

@router.get("/inventory/{product_id}", response_model=InventoryRead, summary="获取商品库存信息")
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
async def get_batch_inventory(
    query: BatchInventoryQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量获取多个商品的库存信息
    
    - **product_ids**: 商品ID列表
    
    返回所有请求商品的简要库存信息
    """
    service = InventoryService(db)
    return service.get_batch_inventory(query.product_ids)


# ============ 库存预占接口 ============

@router.post("/reserve/cart", response_model=ReservationResponse, summary="购物车库存预占")
async def reserve_cart_inventory(
    request: CartReserveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为购物车商品预占库存
    
    - **cart_id**: 购物车ID
    - **items**: 商品列表，包含商品ID和数量
    - **reserve_duration**: 预占时长（分钟）
    
    预占成功返回预占详情，失败返回错误信息
    """
    service = InventoryService(db)
    return service.reserve_for_cart(
        user_id=current_user.id,
        cart_id=request.cart_id,
        items=request.items,
        reserve_duration=request.reserve_duration
    )


@router.post("/reserve/order", response_model=ReservationResponse, summary="订单库存预占")
async def reserve_order_inventory(
    request: OrderReserveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为订单预占库存
    
    - **order_id**: 订单ID
    - **items**: 商品列表，包含商品ID和数量
    - **reserve_duration**: 预占时长（分钟）
    
    预占成功返回预占详情，失败返回错误信息
    """
    service = InventoryService(db)
    return service.reserve_for_order(
        user_id=current_user.id,
        order_id=request.order_id,
        items=request.items,
        reserve_duration=request.reserve_duration
    )


@router.delete("/reserve/{reservation_id}", summary="释放库存预占")
async def release_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    释放指定的库存预占
    
    - **reservation_id**: 预占记录ID
    
    释放预占的库存，使其重新可用
    """
    service = InventoryService(db)
    success = service.release_reservation(reservation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="预占记录不存在或已过期")
    return {"message": "库存预占已释放"}


# ============ 库存扣减接口 ============

@router.post("/deduct", summary="扣减库存")
async def deduct_inventory(
    request: InventoryDeductRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    扣减商品库存（实际出库）
    
    - **order_id**: 订单ID
    - **items**: 商品列表，包含商品ID和数量
    - **reservation_id**: 对应的预占记录ID（可选）
    
    从库存中实际扣减商品数量，用于订单确认出库
    """
    service = InventoryService(db)
    success = service.deduct_inventory(
        order_id=request.order_id,
        items=request.items,
        reservation_id=request.reservation_id
    )
    if not success:
        raise HTTPException(status_code=400, detail="库存扣减失败，库存不足或预占已过期")
    return {"message": "库存扣减成功"}


# ============ 库存管理接口（管理员） ============

@router.post("/adjust", summary="调整商品库存")
async def adjust_inventory(
    adjustment: InventoryAdjustment,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    调整商品库存（管理员操作）
    
    - **product_id**: 商品ID
    - **adjustment_type**: 调整类型（入库/出库/盘点）
    - **quantity**: 调整数量
    - **reason**: 调整原因
    
    管理员可以手动调整库存，用于入库、出库、盘点等操作
    """
    service = InventoryService(db)
    success = service.adjust_inventory(
        product_id=adjustment.product_id,
        adjustment_type=adjustment.adjustment_type,
        quantity=adjustment.quantity,
        reason=adjustment.reason,
        operator_id=admin_user.id
    )
    if not success:
        raise HTTPException(status_code=400, detail="库存调整失败")
    return {"message": "库存调整成功"}


@router.put("/threshold/{product_id}", summary="更新库存阈值")
async def update_inventory_threshold(
    product_id: int,
    threshold: ThresholdUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    更新商品库存阈值（管理员操作）
    
    - **product_id**: 商品ID
    - **low_stock_threshold**: 低库存阈值
    - **out_of_stock_threshold**: 缺货阈值
    
    设置库存预警阈值，当库存低于阈值时会触发预警
    """
    service = InventoryService(db)
    success = service.update_thresholds(
        product_id=product_id,
        low_stock_threshold=threshold.low_stock_threshold,
        out_of_stock_threshold=threshold.out_of_stock_threshold
    )
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"message": "库存阈值更新成功"}


# ============ 库存统计和查询接口 ============

@router.get("/transactions", response_model=PaginatedResponse[InventoryTransactionRead], summary="查询库存变动记录")
async def get_inventory_transactions(
    product_id: int = Query(None, description="商品ID"),
    transaction_type: str = Query(None, description="变动类型"),
    start_date: str = Query(None, description="开始日期"),
    end_date: str = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    查询库存变动记录
    
    支持按商品ID、变动类型、时间范围等条件筛选库存变动记录
    """
    service = InventoryService(db)
    query = TransactionQuery(
        product_id=product_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )
    return service.get_transactions(query)


@router.get("/low-stock", response_model=List[LowStockItem], summary="获取低库存商品列表")
async def get_low_stock_products(
    threshold_type: str = Query("low", description="阈值类型：low（低库存）或 out（缺货）"),
    category_id: int = Query(None, description="商品分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    获取低库存商品列表（管理员操作）
    
    返回库存低于设定阈值的商品列表，用于及时补货
    """
    service = InventoryService(db)
    query = LowStockQuery(
        threshold_type=threshold_type,
        category_id=category_id,
        page=page,
        page_size=page_size
    )
    return service.get_low_stock_products(query)