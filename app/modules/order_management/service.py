"""
文件名：order_service.py
文件路径：app/services/order_service.py
功能描述：订单管理相关的业务逻辑服务
主要功能：
- 订单的创建、查询、更新、删除
- 订单状态流转管理
- 订单金额计算和验证
使用说明：
- 导入：from app.services.order_service import OrderService
- 在路由中调用：OrderService.create_order(order_data)
"""

import uuid
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models import Order, OrderItem, Product, User


class OrderService:
    """订单管理业务逻辑服务"""
    
    @staticmethod
    def generate_order_no() -> str:
        """
        生成订单号
        
        Returns:
            str: 格式为 ORD{timestamp}{random} 的订单号
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4()).replace('-', '')[:8].upper()
        return f"ORD{timestamp}{random_suffix}"
    
    @staticmethod
    def create_order(db: Session, user_id: int, items: List[dict],
                    shipping_address: Optional[str] = None,
                    shipping_method: str = "standard",
                    notes: Optional[str] = None) -> Order:
        """
        创建新订单
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            items: 订单项列表 [{"product_id": int, "quantity": int, "unit_price": float}]
            shipping_address: 收货地址
            shipping_method: 配送方式
            notes: 订单备注
            
        Returns:
            Order: 创建的订单对象
            
        Raises:
            HTTPException: 用户不存在、商品不存在或库存不足时抛出错误
        """
        # 验证用户存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 验证商品存在性和库存
        total_amount = Decimal('0.00')
        order_items = []
        
        for item in items:
            product = db.query(Product).filter(Product.id == item['product_id']).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"商品ID {item['product_id']} 不存在"
                )
            
            if product.stock_quantity < item['quantity']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"商品 {product.name} 库存不足，当前库存：{product.stock_quantity}"
                )
            
            if product.status != 'active':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"商品 {product.name} 当前不可购买"
                )
            
            # 使用商品当前价格，而不是传入的价格（防止价格篡改）
            unit_price = product.price
            subtotal = unit_price * item['quantity']
            total_amount += subtotal
            
            order_items.append({
                'product_id': product.id,
                'quantity': item['quantity'],
                'unit_price': unit_price,
                'subtotal': subtotal
            })
        
        # 创建订单
        order = Order(
            order_no=OrderService.generate_order_no(),
            user_id=user_id,
            status='pending',
            total_amount=total_amount,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            notes=notes
        )
        
        try:
            db.add(order)
            db.flush()  # 获取订单ID
            
            # 创建订单项
            for item_data in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    **item_data
                )
                db.add(order_item)
            
            # 减少商品库存
            for item in items:
                product = db.query(Product).filter(Product.id == item['product_id']).first()
                product.stock_quantity -= item['quantity']
                
                # 更新商品状态
                if product.stock_quantity == 0:
                    product.status = 'out_of_stock'
            
            db.commit()
            db.refresh(order)
            return order
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单创建失败，数据冲突"
            )
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """
        根据ID获取订单
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID（可选，用于权限验证）
            
        Returns:
            Order: 订单对象或None
        """
        query = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.user)
        )
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        return query.filter(Order.id == order_id).first()
    
    @staticmethod
    def get_orders(db: Session, user_id: Optional[int] = None, 
                  status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        获取订单列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID筛选（可选）
            status: 状态筛选（可选）
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            List[Order]: 订单列表
        """
        query = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.user)
        )
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: str,
                           user_id: Optional[int] = None) -> Optional[Order]:
        """
        更新订单状态
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            new_status: 新状态
            user_id: 用户ID（可选，用于权限验证）
            
        Returns:
            Order: 更新后的订单对象或None
            
        Raises:
            HTTPException: 状态转换不合法时抛出错误
        """
        query = db.query(Order)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        order = query.filter(Order.id == order_id).first()
        if not order:
            return None
        
        # 验证状态转换合法性
        valid_transitions = {
            'pending': ['paid', 'cancelled'],
            'paid': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'returned'],
            'delivered': ['returned'],
            'cancelled': [],
            'returned': []
        }
        
        if new_status not in valid_transitions.get(order.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法从状态 {order.status} 转换到 {new_status}"
            )
        
        order.status = new_status
        
        # 如果订单被取消，恢复商品库存
        if new_status == 'cancelled' and order.status != 'cancelled':
            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
                    if product.status == 'out_of_stock' and product.stock_quantity > 0:
                        product.status = 'active'
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: int, user_id: Optional[int] = None) -> bool:
        """
        取消订单
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID（可选，用于权限验证）
            
        Returns:
            bool: 取消成功返回True，失败返回False
        """
        order = OrderService.update_order_status(db, order_id, 'cancelled', user_id)
        return order is not None
    
    @staticmethod
    def get_order_items(db: Session, order_id: int, user_id: Optional[int] = None) -> List[OrderItem]:
        """
        获取订单项列表
        
        Args:
            db: 数据库会话
            order_id: 订单ID
            user_id: 用户ID（可选，用于权限验证）
            
        Returns:
            List[OrderItem]: 订单项列表
        """
        query = db.query(OrderItem).join(Order).options(
            joinedload(OrderItem.product)
        ).filter(OrderItem.order_id == order_id)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        return query.all()
    
    @staticmethod
    def calculate_order_statistics(db: Session, user_id: Optional[int] = None) -> dict:
        """
        计算订单统计信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID（可选，计算指定用户的统计）
            
        Returns:
            dict: 包含各种统计信息的字典
        """
        query = db.query(Order)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        total_orders = query.count()
        pending_orders = query.filter(Order.status == 'pending').count()
        completed_orders = query.filter(Order.status == 'delivered').count()
        cancelled_orders = query.filter(Order.status == 'cancelled').count()
        
        # 计算总金额
        total_amount = db.query(db.func.sum(Order.total_amount)).filter(
            Order.status.in_(['paid', 'shipped', 'delivered'])
        )
        if user_id:
            total_amount = total_amount.filter(Order.user_id == user_id)
        total_amount = total_amount.scalar() or 0
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_amount': float(total_amount)
        }