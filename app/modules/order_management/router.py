"""
订单管理API路由
"""
import uuid
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.database import get_db
from app.data_models import Order, OrderItem, Product, User
# V1.0 Mini-MVP: 导入更新的认证依赖
from app.auth import get_current_active_user, get_current_admin_user, require_ownership
from app.api.schemas import (
    OrderCreate,
    OrderRead,
    OrderStatusUpdate,
    OrderItemRead
)

router = APIRouter()


def generate_order_no() -> str:
    """生成订单号"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4()).replace('-', '')[:8].upper()
    return f"ORD{timestamp}{random_suffix}"


@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建订单（用户只能为自己创建，管理员可为任何人创建）"""
    
    # V1.0 Mini-MVP: 使用新的权限检查
    if order_data.user_id != current_user.id:
        # 检查是否是管理员
        if current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能为自己创建订单"
            )
    
    # 验证用户存在
    user = db.query(User).filter(User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证商品存在并计算金额
    order_items_data = []
    subtotal = Decimal('0.00')
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"商品ID {item.product_id} 不存在"
            )
        
        if product.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 已下架"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品 {product.name} 库存不足，当前库存：{product.stock_quantity}"
            )
        
        # 计算价格
        unit_price = product.price
        total_price = unit_price * item.quantity
        subtotal += total_price
        
        order_items_data.append({
            'product': product,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'total_price': total_price
        })
    
    # 计算总金额（暂时不考虑运费和优惠）
    shipping_fee = Decimal('0.00')  # 暂时免运费
    discount_amount = Decimal('0.00')  # 暂时无优惠
    total_amount = subtotal + shipping_fee - discount_amount
    
    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        user_id=order_data.user_id,
        status='pending',
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        remark=order_data.remark
    )
    
    db.add(order)
    db.flush()  # 获取order.id
    
    # 创建订单项并减少库存
    for item_data in order_items_data:
        product = item_data['product']
        quantity = item_data['quantity']
        
        # 减少库存
        product.stock_quantity -= quantity
        
        # 创建订单项
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            quantity=quantity,
            unit_price=item_data['unit_price'],
            total_price=item_data['total_price']
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/orders", response_model=List[OrderRead])
async def list_orders(
    status_filter: Optional[str] = Query(None, description="订单状态过滤"),
    user_id: Optional[int] = Query(None, description="用户ID过滤"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单列表（用户只能查看自己的订单，管理员可查看所有）"""
    
    query = db.query(Order)
    
    # V1.0 Mini-MVP: 使用新的权限检查
    if current_user.role not in ['admin', 'super_admin']:
        query = query.filter(Order.user_id == current_user.id)
    elif user_id:
        # 管理员可以按用户ID过滤
        query = query.filter(Order.user_id == user_id)
    
    # 状态过滤
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    # 排序和分页
    orders = query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
    
    return orders


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单详情（所有权验证）"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # V1.0 Mini-MVP: 使用新的权限检查
    if not require_ownership(order.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此订单"
        )
    
    return order


@router.patch("/orders/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)  # V1.0: 管理员权限
):
    """更新订单状态（需要管理员权限）"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    old_status = order.status
    new_status = status_update.status
    
    # 验证状态转换的合法性
    valid_transitions = {
        'pending': ['paid', 'cancelled'],
        'paid': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
        'delivered': [],  # 已完成的订单不能再变更
        'cancelled': []   # 已取消的订单不能再变更
    }
    
    if new_status not in valid_transitions.get(old_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"订单状态不能从 {old_status} 变更为 {new_status}"
        )
    
    # 更新状态和时间戳
    order.status = new_status
    
    if new_status == 'paid':
        order.paid_at = datetime.utcnow()
    elif new_status == 'shipped':
        order.shipped_at = datetime.utcnow()
    elif new_status == 'delivered':
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消订单（用户可取消自己的订单，管理员可取消任何订单）"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # V1.0 Mini-MVP: 使用新的权限检查
    if not require_ownership(order.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权取消此订单"
        )
    
    # 只有pending状态的订单可以取消
    if order.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"只有待付款订单可以取消，当前状态：{order.status}"
        )
    
    # 恢复库存
    for order_item in order.order_items:
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if product:
            product.stock_quantity += order_item.quantity
    
    # 更新订单状态
    order.status = 'cancelled'
    
    db.commit()
    
    return {"message": "订单已取消", "order_id": order_id}


@router.get("/orders/{order_id}/items", response_model=List[OrderItemRead])
async def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单商品列表（所有权验证）"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # V1.0 Mini-MVP: 使用新的权限检查
    if not require_ownership(order.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此订单"
        )
    
    return order.order_items
