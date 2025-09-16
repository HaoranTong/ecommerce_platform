"""
文件名：router.py
文件路径：app/modules/inventory_management/router.py
功能描述：库存管理模块的FastAPI路由定义

主要功能：
- 定义库存管理相关的API端点
- 基于SKU的库存查询、预留、扣减、调整接口
- 提供管理员库存管理和历史查询功能
- 支持批量操作和系统维护接口

使用说明：
- 导入：from app.modules.inventory_management import router
- 路由前缀：/api/v1/inventory-management
- 认证要求：部分接口需要用户认证，管理接口需要管理员权限

依赖模块：
- app.modules.inventory_management.service.InventoryService: 业务逻辑层
- app.modules.inventory_management.schemas: 请求/响应模型
- app.core.auth: 用户认证和权限控制
- app.core.database: 数据库会话管理

API分类：
- 库存查询接口：支持单个和批量查询
- 库存预留接口：购物车和订单预留
- 库存操作接口：扣减、调整、补库存
- 管理接口：阈值设置、低库存监控
- 历史接口：变动记录查询和审计

创建时间：2025-09-15
最后修改：2025-09-15
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.modules.user_auth.models import User
from .service import InventoryService
from .schemas import (
    # 基础Schemas
    SKUInventoryRead, SKUInventorySimple, SKUInventoryCreate, SKUInventoryUpdate,
    
    # 批量操作Schemas
    BatchInventoryQuery,
    
    # 预占相关Schemas
    ReserveRequest, ReservationResponse, ReleaseReservationRequest,
    
    # 库存操作Schemas  
    InventoryDeductRequest, DeductResponse, InventoryAdjustment, AdjustmentResponse,
    
    # 管理相关Schemas
    ThresholdUpdate, LowStockItem, LowStockQuery,
    
    # 历史查询Schemas
    TransactionQuery, InventoryTransactionRead, TransactionSearchResponse,
    
    # 系统维护Schemas
    CleanupResponse, ConsistencyCheckResponse,
    
    # 通用响应Schemas
    PaginatedResponse, APIResponse
)

router = APIRouter()


# ============ 库存查询接口 ============

@router.get("/inventory-management/stock/{sku_id}", response_model=SKUInventoryRead, summary="获取SKU库存信息")
async def get_sku_inventory(
    sku_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定SKU的实时库存信息
    
    - **sku_id**: SKU唯一标识符
    
    返回SKU的详细库存信息，包括可用数量、预占数量、总数量等
    """
    service = InventoryService(db)
    
    try:
        inventory = await service.get_sku_inventory(sku_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SKU {sku_id} 的库存信息不存在"
            )
        return inventory
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取库存信息失败: {str(e)}"
        )


@router.post("/inventory-management/stock/batch", response_model=List[SKUInventorySimple], summary="批量获取SKU库存")
async def get_batch_sku_inventory(
    query: BatchInventoryQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量获取多个SKU的库存信息
    
    - **sku_ids**: SKU ID列表（最多100个）
    
    返回所有请求SKU的简要库存信息
    """
    service = InventoryService(db)
    
    try:
        inventories = await service.get_batch_inventory(query.sku_ids)
        return inventories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量获取库存信息失败: {str(e)}"
        )


# ============ 库存预占接口 ============

@router.post("/inventory-management/reserve", response_model=ReservationResponse, summary="库存预占")
async def reserve_inventory(
    request: ReserveRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    为购物车或订单预占库存
    
    - **reservation_type**: 预占类型 (cart/order)
    - **reference_id**: 关联ID（用户ID或订单ID）
    - **items**: 预占商品列表
    - **expires_minutes**: 预占有效期（分钟）
    
    预占成功返回预占详情，失败返回错误信息
    """
    service = InventoryService(db)
    
    try:
        reservation = await service.reserve_inventory(
            reservation_type=request.reservation_type,
            reference_id=request.reference_id,
            items=request.items,
            expires_minutes=request.expires_minutes,
            user_id=current_user.id
        )
        
        # 后台任务：发送库存预占事件
        background_tasks.add_task(
            service.publish_inventory_event,
            "inventory.stock.reserved",
            {
                "reservation_id": reservation.reservation_id,
                "user_id": current_user.id,
                "items": [{"sku_id": item.sku_id, "quantity": item.reserved_quantity} 
                         for item in reservation.reserved_items]
            }
        )
        
        return reservation
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"库存预占失败: {str(e)}"
        )


@router.delete("/inventory-management/reserve/{reservation_id}", summary="释放库存预占")
async def release_reservation(
    reservation_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    释放指定的库存预占
    
    - **reservation_id**: 预占记录ID
    
    释放预占的库存，使其重新可用
    """
    service = InventoryService(db)
    
    try:
        success = await service.release_reservation(reservation_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="预占记录不存在或已过期"
            )
        
        # 后台任务：发送库存释放事件
        background_tasks.add_task(
            service.publish_inventory_event,
            "inventory.stock.released",
            {"reservation_id": reservation_id, "user_id": current_user.id}
        )
        
        return {"message": "库存预占已释放"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"释放预占失败: {str(e)}"
        )


@router.delete("/inventory-management/reserve/user/{user_id}", summary="批量释放用户预占")
async def release_user_reservations(
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    释放指定用户的所有预占（购物车清空）
    
    - **user_id**: 用户ID（用户只能释放自己的预占）
    
    释放该用户所有有效的库存预占
    """
    # 权限检查：用户只能释放自己的预占
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只能释放自己的预占"
        )
    
    service = InventoryService(db)
    
    try:
        result = await service.release_user_reservations(user_id)
        
        # 后台任务：发送批量释放事件
        background_tasks.add_task(
            service.publish_inventory_event,
            "inventory.stock.batch_released",
            {
                "user_id": user_id,
                "released_reservations": result["released_reservations"],
                "total_released_quantity": result["total_released_quantity"]
            }
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量释放预占失败: {str(e)}"
        )


# ============ 库存操作接口 ============

@router.post("/inventory-management/deduct", response_model=DeductResponse, summary="库存扣减")
async def deduct_inventory(
    request: InventoryDeductRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    订单完成后扣减库存（从预占转为实际扣减）
    
    - **order_id**: 订单ID
    - **items**: 扣减商品列表
    
    从库存中实际扣减商品数量，用于订单确认出库
    """
    service = InventoryService(db)
    
    try:
        result = await service.deduct_inventory(
            order_id=request.order_id,
            items=request.items,
            operator_id=current_user.id
        )
        
        # 后台任务：发送库存扣减事件
        background_tasks.add_task(
            service.publish_inventory_event,
            "inventory.stock.deducted",
            {
                "order_id": request.order_id,
                "items": [{"sku_id": item.sku_id, "quantity": item.deducted_quantity} 
                         for item in result.deducted_items],
                "operator_id": current_user.id
            }
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"库存扣减失败: {str(e)}"
        )


@router.post("/inventory-management/adjust/{sku_id}", response_model=AdjustmentResponse, summary="库存调整")
async def adjust_inventory(
    sku_id: str,
    adjustment: InventoryAdjustment,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    管理员调整SKU库存数量
    
    - **sku_id**: SKU ID
    - **adjustment_type**: 调整类型（increase/decrease/set）
    - **quantity**: 调整数量
    - **reason**: 调整原因
    
    管理员可以手动调整库存，用于入库、出库、盘点等操作
    """
    # 确保路径中的sku_id与请求体中的一致
    if adjustment.sku_id != sku_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="路径中的sku_id与请求体中的不一致"
        )
    
    service = InventoryService(db)
    
    try:
        result = await service.adjust_inventory(
            sku_id=sku_id,
            adjustment_type=adjustment.adjustment_type,
            quantity=adjustment.quantity,
            reason=adjustment.reason,
            reference=adjustment.reference,
            operator_id=admin_user.id
        )
        
        # 后台任务：发送库存调整事件
        background_tasks.add_task(
            service.publish_inventory_event,
            "inventory.stock.adjusted",
            {
                "sku_id": sku_id,
                "adjustment_type": adjustment.adjustment_type.value,
                "old_quantity": result.old_quantity,
                "new_quantity": result.new_quantity,
                "operator_id": admin_user.id,
                "reason": adjustment.reason
            }
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"库存调整失败: {str(e)}"
        )


# ============ 库存管理接口 ============

@router.put("/inventory-management/threshold/{sku_id}", summary="设置库存阈值")
async def update_inventory_threshold(
    sku_id: str,
    threshold: ThresholdUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    设置SKU的库存预警阈值
    
    - **sku_id**: SKU ID
    - **warning_threshold**: 库存预警阈值
    - **critical_threshold**: 库存严重不足阈值
    
    设置库存预警阈值，当库存低于阈值时会触发预警
    """
    service = InventoryService(db)
    
    try:
        success = await service.update_thresholds(
            sku_id=sku_id,
            warning_threshold=threshold.warning_threshold,
            critical_threshold=threshold.critical_threshold
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SKU不存在"
            )
        
        return {"message": "库存阈值更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"阈值更新失败: {str(e)}"
        )


@router.get("/inventory-management/low-stock", response_model=List[LowStockItem], summary="获取低库存SKU列表")
async def get_low_stock_skus(
    level: Optional[str] = Query("warning", description="预警级别: warning|critical"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="分页偏移"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    获取库存不足的SKU列表
    
    返回库存低于设定阈值的SKU列表，用于及时补货
    """
    service = InventoryService(db)
    
    try:
        query = LowStockQuery(level=level, limit=limit, offset=offset)
        low_stock_items = await service.get_low_stock_skus(query)
        return low_stock_items
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取低库存列表失败: {str(e)}"
        )


# ============ 库存历史接口 ============

@router.get("/inventory-management/logs/{sku_id}", response_model=TransactionSearchResponse, summary="获取SKU库存变动历史")
async def get_sku_transaction_logs(
    sku_id: str,
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    transaction_type: Optional[str] = Query(None, description="交易类型过滤"),
    limit: int = Query(50, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="分页偏移"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    获取指定SKU的库存变动历史记录
    
    - **sku_id**: SKU ID
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **transaction_type**: 交易类型过滤
    - **limit**: 返回数量限制
    
    返回指定SKU的库存变动历史记录
    """
    service = InventoryService(db)
    
    try:
        query = TransactionQuery(
            sku_ids=[sku_id],
            transaction_types=[transaction_type] if transaction_type else None,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        result = await service.get_transaction_logs(query)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取变动历史失败: {str(e)}"
        )


@router.get("/inventory-management/logs/search", response_model=List[TransactionSearchResponse], summary="搜索库存变动记录")
async def search_inventory_transactions(
    sku_ids: Optional[str] = Query(None, description="SKU ID列表，逗号分隔"),
    transaction_types: Optional[str] = Query(None, description="交易类型列表，逗号分隔"),
    operator_id: Optional[int] = Query(None, description="操作人ID"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    limit: int = Query(50, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="分页偏移"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    按条件搜索库存变动记录
    
    支持多维度条件筛选库存变动记录
    """
    service = InventoryService(db)
    
    try:
        # 处理查询参数
        sku_id_list = sku_ids.split(',') if sku_ids else None
        transaction_type_list = transaction_types.split(',') if transaction_types else None
        
        query = TransactionQuery(
            sku_ids=sku_id_list,
            transaction_types=transaction_type_list,
            operator_id=operator_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        results = await service.search_transaction_logs(query)
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索变动记录失败: {str(e)}"
        )


# ============ 系统维护接口 ============

@router.post("/inventory-management/maintenance/cleanup-reservations", response_model=CleanupResponse, summary="清理过期预占")
async def cleanup_expired_reservations(
    db: Session = Depends(get_db),
    # 注意：这个接口应该由系统内部调用或定时任务调用
    # 这里暂时使用管理员权限，实际生产中可能需要特殊的系统权限
    admin_user: User = Depends(get_current_admin_user)
):
    """
    清理过期的库存预占记录
    
    释放所有已过期的库存预占，使库存重新可用
    """
    service = InventoryService(db)
    
    try:
        result = await service.cleanup_expired_reservations()
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清理过期预占失败: {str(e)}"
        )


@router.post("/inventory-management/maintenance/consistency-check", response_model=ConsistencyCheckResponse, summary="库存一致性检查")
async def check_inventory_consistency(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    检查库存数据一致性
    
    检查库存数据的一致性，发现并报告数据异常
    """
    service = InventoryService(db)
    
    try:
        result = await service.check_inventory_consistency()
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"一致性检查失败: {str(e)}"
        )


# ============ SKU库存初始化接口 ============

@router.post("/inventory-management/stock", response_model=SKUInventoryRead, summary="创建SKU库存")
async def create_sku_inventory(
    inventory_data: SKUInventoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    为新SKU创建库存记录
    
    - **sku_id**: SKU ID
    - **initial_quantity**: 初始库存数量
    - **warning_threshold**: 库存预警阈值
    - **critical_threshold**: 库存严重不足阈值
    
    为新SKU创建库存管理记录
    """
    service = InventoryService(db)
    
    try:
        inventory = await service.create_sku_inventory(inventory_data)
        return inventory
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建库存记录失败: {str(e)}"
        )


@router.put("/inventory-management/stock/{sku_id}", summary="更新SKU库存配置")
async def update_sku_inventory_config(
    sku_id: str,
    update_data: SKUInventoryUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    更新SKU库存配置
    
    - **sku_id**: SKU ID
    - **warning_threshold**: 库存预警阈值（可选）
    - **critical_threshold**: 库存严重不足阈值（可选）
    - **is_active**: 是否启用库存管理（可选）
    
    更新SKU的库存管理配置
    """
    service = InventoryService(db)
    
    try:
        success = await service.update_sku_inventory_config(sku_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SKU库存记录不存在"
            )
        
        return {"message": "SKU库存配置更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新库存配置失败: {str(e)}"
        )
