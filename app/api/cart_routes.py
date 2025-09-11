"""
购物车管理路由
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, Product
from ..redis_client import cart_manager
from .schemas import (
    CartItemAdd, 
    CartItemUpdate, 
    CartItemRead, 
    CartSummary
)
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/api/carts/items", response_model=dict, summary="添加商品到购物车")
async def add_to_cart(
    item: CartItemAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    添加商品到购物车
    
    Args:
        item: 商品信息（product_id, quantity）
        current_user: 当前登录用户
        db: 数据库连接
    
    Returns:
        操作结果和购物车统计信息
    """
    # 检查商品是否存在且有效
    product = db.query(Product).filter(
        Product.id == item.product_id,
        Product.status == 'active'
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在或已下架"
        )
    
    # 检查库存
    if product.stock_quantity < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存：{product.stock_quantity}"
        )
    
    # 检查购物车中已有数量
    current_quantity = await cart_manager.get_item_quantity(current_user.id, item.product_id)
    total_quantity = current_quantity + item.quantity
    
    if total_quantity > product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"购物车数量超出库存限制，当前购物车：{current_quantity}，库存：{product.stock_quantity}"
        )
    
    # 添加到购物车
    success = await cart_manager.add_item(current_user.id, item.product_id, item.quantity)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加到购物车失败"
        )
    
    # 获取购物车统计信息
    cart_count = await cart_manager.get_cart_count(current_user.id)
    total_quantity = await cart_manager.get_cart_total_quantity(current_user.id)
    
    return {
        "message": "商品已添加到购物车",
        "cart_count": cart_count,
        "total_quantity": total_quantity
    }


@router.put("/api/carts/items/{product_id}", response_model=dict, summary="更新购物车商品数量")
async def update_cart_item(
    product_id: int,
    item: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新购物车中商品的数量
    
    Args:
        product_id: 商品ID
        item: 更新信息（quantity）
        current_user: 当前登录用户
        db: 数据库连接
    
    Returns:
        操作结果
    """
    # 检查商品是否存在且有效
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == 'active'
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在或已下架"
        )
    
    # 检查商品是否在购物车中
    current_quantity = await cart_manager.get_item_quantity(current_user.id, product_id)
    if current_quantity == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不在购物车中"
        )
    
    # 如果数量为0，删除商品
    if item.quantity == 0:
        success = await cart_manager.remove_item(current_user.id, product_id)
        message = "商品已从购物车移除"
    else:
        # 检查库存
        if item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"数量超出库存限制，当前库存：{product.stock_quantity}"
            )
        
        success = await cart_manager.update_item_quantity(current_user.id, product_id, item.quantity)
        message = "购物车数量已更新"
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新购物车失败"
        )
    
    # 获取购物车统计信息
    cart_count = await cart_manager.get_cart_count(current_user.id)
    total_quantity = await cart_manager.get_cart_total_quantity(current_user.id)
    
    return {
        "message": message,
        "cart_count": cart_count,
        "total_quantity": total_quantity
    }


@router.delete("/api/carts/items/{product_id}", response_model=dict, summary="从购物车移除商品")
async def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    从购物车移除指定商品
    
    Args:
        product_id: 商品ID
        current_user: 当前登录用户
    
    Returns:
        操作结果
    """
    # 检查商品是否在购物车中
    current_quantity = await cart_manager.get_item_quantity(current_user.id, product_id)
    if current_quantity == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不在购物车中"
        )
    
    success = await cart_manager.remove_item(current_user.id, product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="移除商品失败"
        )
    
    # 获取购物车统计信息
    cart_count = await cart_manager.get_cart_count(current_user.id)
    total_quantity = await cart_manager.get_cart_total_quantity(current_user.id)
    
    return {
        "message": "商品已从购物车移除",
        "cart_count": cart_count,
        "total_quantity": total_quantity
    }


@router.get("/api/carts", response_model=CartSummary, summary="获取购物车详情")
async def get_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的购物车详情
    
    Args:
        current_user: 当前登录用户
        db: 数据库连接
    
    Returns:
        购物车详细信息
    """
    # 获取购物车中的商品
    cart_items = await cart_manager.get_cart_items(current_user.id)
    
    if not cart_items:
        return CartSummary(
            user_id=current_user.id,
            items=[],
            total_items=0,
            total_quantity=0,
            total_amount=Decimal('0.00')
        )
    
    # 获取商品详细信息
    product_ids = [int(pid) for pid in cart_items.keys()]
    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.status == 'active'
    ).all()
    
    # 构建购物车商品列表
    cart_item_list = []
    total_amount = Decimal('0.00')
    total_quantity = 0
    
    for product in products:
        quantity = cart_items[str(product.id)]
        subtotal = product.price * quantity
        
        cart_item_list.append(CartItemRead(
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            price=product.price,
            quantity=quantity,
            subtotal=subtotal,
            stock_quantity=product.stock_quantity,
            image_url=product.image_url
        ))
        
        total_amount += subtotal
        total_quantity += quantity
    
    # 检查是否有商品已下架或删除
    invalid_product_ids = []
    for pid in product_ids:
        if not any(p.id == pid for p in products):
            invalid_product_ids.append(pid)
    
    # 清理无效商品
    for pid in invalid_product_ids:
        await cart_manager.remove_item(current_user.id, pid)
    
    return CartSummary(
        user_id=current_user.id,
        items=cart_item_list,
        total_items=len(cart_item_list),
        total_quantity=total_quantity,
        total_amount=total_amount
    )


@router.delete("/api/carts/items", response_model=dict, summary="清空购物车")
async def clear_cart(
    current_user: User = Depends(get_current_active_user)
):
    """
    清空当前用户的购物车
    
    Args:
        current_user: 当前登录用户
    
    Returns:
        操作结果
    """
    success = await cart_manager.clear_cart(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清空购物车失败"
        )
    
    return {
        "message": "购物车已清空",
        "cart_count": 0,
        "total_quantity": 0
    }


@router.get("/api/carts/summary", response_model=dict, summary="获取购物车统计")
async def get_cart_count(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取购物车商品统计信息
    
    Args:
        current_user: 当前登录用户
    
    Returns:
        购物车统计信息
    """
    cart_count = await cart_manager.get_cart_count(current_user.id)
    total_quantity = await cart_manager.get_cart_total_quantity(current_user.id)
    
    return {
        "cart_count": cart_count,
        "total_quantity": total_quantity
    }
