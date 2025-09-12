"""
文件名：cart_service.py
文件路径：app/services/cart_service.py
功能描述：购物车管理相关的业务逻辑服务
主要功能：
- 购物车商品的添加、查询、更新、删除
- 购物车金额计算和统计
- 购物车商品库存验证
使用说明：
- 导入：from app.services.cart_service import CartService
- 在路由中调用：CartService.add_to_cart(user_id, product_id, quantity)
"""

from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.data_models import Cart, Product, User


class CartService:
    """购物车管理业务逻辑服务"""
    
    @staticmethod
    def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1) -> Cart:
        """
        添加商品到购物车
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            product_id: 商品ID
            quantity: 数量
            
        Returns:
            Cart: 购物车项对象
            
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
        
        # 验证商品存在
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在"
            )
        
        # 验证商品状态
        if product.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="商品当前不可购买"
            )
        
        # 检查是否已存在该商品
        existing_cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()
        
        if existing_cart_item:
            # 更新数量
            new_quantity = existing_cart_item.quantity + quantity
            
            # 验证库存
            if new_quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"库存不足，当前库存：{product.stock_quantity}，购物车已有：{existing_cart_item.quantity}"
                )
            
            existing_cart_item.quantity = new_quantity
            db.commit()
            db.refresh(existing_cart_item)
            return existing_cart_item
        else:
            # 验证库存
            if quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"库存不足，当前库存：{product.stock_quantity}"
                )
            
            # 创建新的购物车项
            cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            
            try:
                db.add(cart_item)
                db.commit()
                db.refresh(cart_item)
                return cart_item
            except IntegrityError:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="添加购物车失败，数据冲突"
                )
    
    @staticmethod
    def get_cart_items(db: Session, user_id: int) -> List[Cart]:
        """
        获取用户购物车中的所有商品
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[Cart]: 购物车项列表
        """
        return db.query(Cart).options(
            joinedload(Cart.product)
        ).filter(Cart.user_id == user_id).all()
    
    @staticmethod
    def update_cart_item_quantity(db: Session, user_id: int, product_id: int, quantity: int) -> Optional[Cart]:
        """
        更新购物车商品数量
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            product_id: 商品ID
            quantity: 新数量
            
        Returns:
            Cart: 更新后的购物车项对象或None
            
        Raises:
            HTTPException: 库存不足时抛出错误
        """
        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()
        
        if not cart_item:
            return None
        
        # 验证库存
        product = db.query(Product).filter(Product.id == product_id).first()
        if product and quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，当前库存：{product.stock_quantity}"
            )
        
        if quantity <= 0:
            # 删除购物车项
            db.delete(cart_item)
            db.commit()
            return None
        else:
            # 更新数量
            cart_item.quantity = quantity
            db.commit()
            db.refresh(cart_item)
            return cart_item
    
    @staticmethod
    def remove_from_cart(db: Session, user_id: int, product_id: int) -> bool:
        """
        从购物车中移除商品
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            product_id: 商品ID
            
        Returns:
            bool: 移除成功返回True，失败返回False
        """
        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()
        
        if cart_item:
            db.delete(cart_item)
            db.commit()
            return True
        return False
    
    @staticmethod
    def clear_cart(db: Session, user_id: int) -> bool:
        """
        清空购物车
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            bool: 清空成功返回True
        """
        deleted_count = db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()
        return deleted_count > 0
    
    @staticmethod
    def get_cart_summary(db: Session, user_id: int) -> dict:
        """
        获取购物车摘要信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            dict: 包含购物车统计信息的字典
        """
        cart_items = CartService.get_cart_items(db, user_id)
        
        if not cart_items:
            return {
                'total_items': 0,
                'total_quantity': 0,
                'total_amount': 0.0,
                'items': []
            }
        
        total_quantity = 0
        total_amount = Decimal('0.00')
        items = []
        
        for item in cart_items:
            if item.product:
                quantity = item.quantity
                unit_price = item.product.price
                subtotal = unit_price * quantity
                
                total_quantity += quantity
                total_amount += subtotal
                
                items.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'quantity': quantity,
                    'unit_price': float(unit_price),
                    'subtotal': float(subtotal),
                    'stock_available': item.product.stock_quantity,
                    'is_available': item.product.status == 'active' and item.product.stock_quantity >= quantity
                })
        
        return {
            'total_items': len(items),
            'total_quantity': total_quantity,
            'total_amount': float(total_amount),
            'items': items
        }
    
    @staticmethod
    def validate_cart_for_checkout(db: Session, user_id: int) -> dict:
        """
        验证购物车是否可以结账
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            dict: 验证结果，包含是否可结账和错误信息
        """
        cart_items = CartService.get_cart_items(db, user_id)
        
        if not cart_items:
            return {
                'can_checkout': False,
                'errors': ['购物车为空'],
                'warnings': []
            }
        
        errors = []
        warnings = []
        
        for item in cart_items:
            if not item.product:
                errors.append(f"商品ID {item.product_id} 不存在")
                continue
            
            if item.product.status != 'active':
                errors.append(f"商品 {item.product.name} 当前不可购买")
            
            if item.quantity > item.product.stock_quantity:
                errors.append(f"商品 {item.product.name} 库存不足，当前库存：{item.product.stock_quantity}，购物车数量：{item.quantity}")
            
            if item.product.stock_quantity <= 5:  # 低库存警告
                warnings.append(f"商品 {item.product.name} 库存较低，仅剩 {item.product.stock_quantity} 件")
        
        return {
            'can_checkout': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def get_cart_item_count(db: Session, user_id: int) -> int:
        """
        获取购物车商品种类数量
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            int: 购物车中商品种类数量
        """
        return db.query(Cart).filter(Cart.user_id == user_id).count()
    
    @staticmethod
    def get_cart_total_quantity(db: Session, user_id: int) -> int:
        """
        获取购物车商品总数量
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            int: 购物车中商品总数量
        """
        result = db.query(db.func.sum(Cart.quantity)).filter(Cart.user_id == user_id).scalar()
        return result or 0
    
    @staticmethod
    def merge_guest_cart(db: Session, user_id: int, guest_cart_items: List[dict]) -> List[Cart]:
        """
        合并游客购物车到用户购物车
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            guest_cart_items: 游客购物车项列表 [{"product_id": int, "quantity": int}]
            
        Returns:
            List[Cart]: 合并后的购物车项列表
        """
        merged_items = []
        
        for guest_item in guest_cart_items:
            try:
                cart_item = CartService.add_to_cart(
                    db, user_id, guest_item['product_id'], guest_item['quantity']
                )
                merged_items.append(cart_item)
            except HTTPException:
                # 忽略无法添加的商品（如库存不足）
                continue
        
        return merged_items