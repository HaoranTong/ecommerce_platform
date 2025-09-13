"""
文件名：order.py
文件路径：app/api/routes/order.py
功能描述：订单和购物车管理相关的API路由定义
主要功能：
- 订单CRUD操作（创建、查询、更新、删除）
- 购物车管理（添加、删除、修改商品）
- 订单状态管理和流程控制
- 订单统计和报表
- 订单搜索和筛选
使用说明：
- 路由前缀：/api/v1/orders
- 认证要求：所有接口需要用户认证
- 权限控制：用户只能操作自己的订单和购物车
依赖模块：
- app.services.OrderService: 订单业务逻辑服务
- app.schemas.order: 订单相关输入输出模式
- app.auth: 用户认证和权限控制
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderRead, OrderStatus,
    CartItemCreate, CartItemUpdate, CartItemRead, CartRead,
    OrderStats, OrderSummary
)
from app.services import OrderService
from app.auth import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/orders", tags=["订单管理"])


# === 订单相关路由 ===

@router.get("", response_model=List[OrderRead])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[OrderStatus] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户的订单列表
    
    - 需要用户认证
    - 支持按状态、时间范围筛选
    - 分页查询
    """
    orders = OrderService.get_user_orders(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    return orders


@router.get("/all", response_model=List[OrderRead])
def list_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[OrderStatus] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取所有订单列表
    
    - 需要管理员权限
    - 支持按用户、状态、时间筛选
    """
    orders = OrderService.get_all_orders(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    return orders


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    根据ID获取订单详情
    
    - 需要用户认证
    - 用户只能查看自己的订单
    """
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查订单所有权
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权访问此订单")
    
    return order


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    创建订单
    
    - 需要用户认证
    - 可从购物车创建或直接创建
    - 自动计算总金额和库存扣减
    """
    try:
        order = OrderService.create_order(
            db=db,
            user_id=current_user.id,
            items=order_data.items,
            shipping_address=order_data.shipping_address,
            payment_method=order_data.payment_method,
            note=order_data.note
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="订单创建失败")


@router.put("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    更新订单状态
    
    - 需要管理员权限
    - 状态流转验证
    """
    order = OrderService.update_order_status(
        db=db,
        order_id=order_id,
        new_status=new_status
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    取消订单
    
    - 需要用户认证
    - 用户只能取消自己的订单
    - 只能取消特定状态的订单
    """
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 检查订单所有权
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权操作此订单")
    
    success = OrderService.cancel_order(
        db=db,
        order_id=order_id,
        reason=reason
    )
    if not success:
        raise HTTPException(status_code=400, detail="订单状态不允许取消")
    
    return {"message": "订单取消成功"}


# === 购物车相关路由 ===

@router.get("/cart", response_model=CartRead)
def get_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户的购物车
    
    - 需要用户认证
    - 返回购物车商品列表和总计
    """
    cart = OrderService.get_user_cart(db=db, user_id=current_user.id)
    return cart


@router.post("/cart/items", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    添加商品到购物车
    
    - 需要用户认证
    - 检查商品存在性和库存
    - 如果商品已在购物车则增加数量
    """
    try:
        cart_item = OrderService.add_to_cart(
            db=db,
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        return cart_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="添加到购物车失败")


@router.put("/cart/items/{item_id}", response_model=CartItemRead)
def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    更新购物车商品数量
    
    - 需要用户认证
    - 验证商品库存
    """
    cart_item = OrderService.update_cart_item(
        db=db,
        user_id=current_user.id,
        item_id=item_id,
        quantity=item_update.quantity
    )
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车商品不存在")
    return cart_item


@router.delete("/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    从购物车移除商品
    
    - 需要用户认证
    """
    success = OrderService.remove_from_cart(
        db=db,
        user_id=current_user.id,
        item_id=item_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="购物车商品不存在")
    return None


@router.delete("/cart/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    清空购物车
    
    - 需要用户认证
    """
    OrderService.clear_cart(db=db, user_id=current_user.id)
    return None


@router.post("/cart/checkout", response_model=OrderRead)
def checkout_cart(
    shipping_address: str,
    payment_method: str,
    note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    购物车结算
    
    - 需要用户认证
    - 将购物车商品转换为订单
    - 清空购物车
    """
    try:
        order = OrderService.checkout_cart(
            db=db,
            user_id=current_user.id,
            shipping_address=shipping_address,
            payment_method=payment_method,
            note=note
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="结算失败")


# === 统计相关路由 ===

@router.get("/stats/user", response_model=OrderStats)
def get_user_order_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    获取当前用户的订单统计
    
    - 需要用户认证
    - 返回订单数量、金额等统计
    """
    stats = OrderService.get_user_order_statistics(
        db=db,
        user_id=current_user.id
    )
    return stats


@router.get("/stats/overview", response_model=OrderStats)
def get_order_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    获取订单统计概览
    
    - 需要管理员权限
    - 支持时间范围筛选
    """
    stats = OrderService.get_order_statistics(
        db=db,
        start_date=start_date,
        end_date=end_date
    )
    return stats