"""
库存管理服务层

此模块提供库存管理的核心业务逻辑，包括：
- 库存查询和更新服务
- 库存预占和释放服务
- 库存扣减和调整服务
- 库存变动记录服务
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status
import redis

from app.data_models import Product
from app.data_models import Inventory, InventoryTransaction, CartReservation, TransactionType, ReferenceType
from app.schemas.inventory import (
    InventoryCreate, InventoryUpdate, ReservationItem, DeductItem,
    InventoryAdjustment, AdjustmentType, TransactionQuery
)

# 同步Redis客户端用于库存管理
import os
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class InventoryService:
    """库存管理服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.redis = redis_client

    # ============ 库存查询相关 ============

    def get_inventory(self, product_id: int) -> Optional[Inventory]:
        """获取商品库存信息"""
        return self.db.query(Inventory).filter(Inventory.product_id == product_id).first()

    def get_inventories_batch(self, product_ids: List[int]) -> List[Inventory]:
        """批量获取商品库存信息"""
        return self.db.query(Inventory).filter(Inventory.product_id.in_(product_ids)).all()

    def get_or_create_inventory(self, product_id: int) -> Inventory:
        """获取或创建商品库存记录"""
        inventory = self.get_inventory(product_id)
        if not inventory:
            # 检查商品是否存在
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"商品不存在: {product_id}"
                )
            
            # 创建库存记录
            inventory = Inventory(
                product_id=product_id,
                available_quantity=product.stock_quantity or 0,
                reserved_quantity=0,
                total_quantity=product.stock_quantity or 0,
                warning_threshold=10
            )
            self.db.add(inventory)
            self.db.commit()
            self.db.refresh(inventory)
            
            # 清除缓存
            self._clear_inventory_cache(product_id)
            
        return inventory

    def get_low_stock_products(self, page: int = 1, page_size: int = 20) -> Tuple[List[Dict], int]:
        """获取低库存商品列表"""
        # 缓存键
        cache_key = f"inventory:low_stock:{page}:{page_size}"
        cached_result = self.redis.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # 查询低库存商品
        query = (
            self.db.query(Inventory, Product)
            .join(Product, Inventory.product_id == Product.id)
            .filter(Inventory.available_quantity <= Inventory.warning_threshold)
            .order_by(Inventory.available_quantity.asc())
        )
        
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 构造响应数据
        result_items = []
        for inventory, product in items:
            result_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_sku": product.sku,
                "available_quantity": inventory.available_quantity,
                "warning_threshold": inventory.warning_threshold,
                "category_name": product.category.name if product.category else None
            })
        
        result = (result_items, total)
        
        # 缓存结果 10分钟
        self.redis.setex(cache_key, 600, json.dumps(result))
        
        return result

    # ============ 库存预占相关 ============

    def reserve_for_cart(self, user_id: int, items: List[ReservationItem], expires_minutes: int = 30) -> Dict:
        """为购物车预占库存"""
        reservation_id = f"cart_{user_id}_{uuid.uuid4().hex[:8]}"
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        reserved_items = []
        
        try:
            # 检查并预占每个商品的库存
            for item in items:
                inventory = self.get_or_create_inventory(item.product_id)
                
                # 检查库存是否充足
                if not inventory.can_reserve(item.quantity):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"商品 {item.product_id} 库存不足，需要 {item.quantity}，可用 {inventory.available_quantity}"
                    )
                
                # 更新或创建预占记录
                existing_reservation = (
                    self.db.query(CartReservation)
                    .filter(
                        and_(
                            CartReservation.user_id == user_id,
                            CartReservation.product_id == item.product_id
                        )
                    )
                    .first()
                )
                
                if existing_reservation:
                    # 更新现有预占
                    old_quantity = existing_reservation.reserved_quantity
                    inventory.update_quantities(
                        available_delta=old_quantity - item.quantity,
                        reserved_delta=item.quantity - old_quantity
                    )
                    existing_reservation.reserved_quantity = item.quantity
                    existing_reservation.expires_at = expires_at
                else:
                    # 创建新预占
                    inventory.update_quantities(
                        available_delta=-item.quantity,
                        reserved_delta=item.quantity
                    )
                    reservation = CartReservation(
                        user_id=user_id,
                        product_id=item.product_id,
                        reserved_quantity=item.quantity,
                        expires_at=expires_at
                    )
                    self.db.add(reservation)
                
                # 记录变动
                self._create_transaction(
                    product_id=item.product_id,
                    transaction_type=TransactionType.RESERVE,
                    quantity=item.quantity,
                    reference_type=ReferenceType.CART,
                    reference_id=user_id,
                    reason="购物车预占",
                    operator_id=user_id,
                    before_quantity=inventory.available_quantity + item.quantity,
                    after_quantity=inventory.available_quantity
                )
                
                reserved_items.append({
                    "product_id": item.product_id,
                    "reserved_quantity": item.quantity,
                    "available_after_reserve": inventory.available_quantity
                })
                
                # 清除缓存
                self._clear_inventory_cache(item.product_id)
            
            self.db.commit()
            
            return {
                "reservation_id": reservation_id,
                "expires_at": expires_at,
                "reserved_items": reserved_items
            }
            
        except Exception as e:
            self.db.rollback()
            raise e

    def reserve_for_order(self, order_id: int, items: List[ReservationItem]) -> Dict:
        """为订单预占库存"""
        reservation_id = f"order_{order_id}_{uuid.uuid4().hex[:8]}"
        expires_at = datetime.utcnow() + timedelta(minutes=15)  # 订单预占15分钟
        reserved_items = []
        
        try:
            for item in items:
                inventory = self.get_or_create_inventory(item.product_id)
                
                # 检查库存是否充足
                if not inventory.can_reserve(item.quantity):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"商品 {item.product_id} 库存不足，需要 {item.quantity}，可用 {inventory.available_quantity}"
                    )
                
                # 预占库存
                inventory.update_quantities(
                    available_delta=-item.quantity,
                    reserved_delta=item.quantity
                )
                
                # 记录变动
                self._create_transaction(
                    product_id=item.product_id,
                    transaction_type=TransactionType.RESERVE,
                    quantity=item.quantity,
                    reference_type=ReferenceType.ORDER,
                    reference_id=order_id,
                    reason="订单预占"
                )
                
                reserved_items.append({
                    "product_id": item.product_id,
                    "reserved_quantity": item.quantity,
                    "available_after_reserve": inventory.available_quantity
                })
                
                # 清除缓存
                self._clear_inventory_cache(item.product_id)
            
            self.db.commit()
            
            # 在Redis中存储订单预占信息，用于后续释放
            reservation_key = f"inventory:order_reservation:{order_id}"
            reservation_data = {
                "items": [{"product_id": item.product_id, "quantity": item.quantity} for item in items],
                "expires_at": expires_at.isoformat()
            }
            self.redis.setex(reservation_key, 900, json.dumps(reservation_data))  # 15分钟过期
            
            return {
                "reservation_id": reservation_id,
                "expires_at": expires_at,
                "reserved_items": reserved_items
            }
            
        except Exception as e:
            self.db.rollback()
            raise e

    def release_cart_reservation(self, user_id: int, product_ids: List[int] = None) -> bool:
        """释放购物车预占"""
        try:
            query = self.db.query(CartReservation).filter(CartReservation.user_id == user_id)
            
            if product_ids:
                query = query.filter(CartReservation.product_id.in_(product_ids))
            
            reservations = query.all()
            
            for reservation in reservations:
                # 释放库存
                inventory = self.get_inventory(reservation.product_id)
                if inventory:
                    inventory.update_quantities(
                        available_delta=reservation.reserved_quantity,
                        reserved_delta=-reservation.reserved_quantity
                    )
                    
                    # 记录变动
                    self._create_transaction(
                        product_id=reservation.product_id,
                        transaction_type=TransactionType.RELEASE,
                        quantity=reservation.reserved_quantity,
                        reference_type=ReferenceType.CART,
                        reference_id=user_id,
                        reason="购物车预占释放",
                        operator_id=user_id
                    )
                    
                    # 清除缓存
                    self._clear_inventory_cache(reservation.product_id)
                
                # 删除预占记录
                self.db.delete(reservation)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    def release_order_reservation(self, order_id: int) -> bool:
        """释放订单预占"""
        try:
            reservation_key = f"inventory:order_reservation:{order_id}"
            reservation_data = self.redis.get(reservation_key)
            
            if not reservation_data:
                return False
            
            data = json.loads(reservation_data)
            items = data.get("items", [])
            
            for item in items:
                inventory = self.get_inventory(item["product_id"])
                if inventory:
                    inventory.update_quantities(
                        available_delta=item["quantity"],
                        reserved_delta=-item["quantity"]
                    )
                    
                    # 记录变动
                    self._create_transaction(
                        product_id=item["product_id"],
                        transaction_type=TransactionType.RELEASE,
                        quantity=item["quantity"],
                        reference_type=ReferenceType.ORDER,
                        reference_id=order_id,
                        reason="订单预占释放"
                    )
                    
                    # 清除缓存
                    self._clear_inventory_cache(item["product_id"])
            
            self.db.commit()
            
            # 删除Redis中的预占记录
            self.redis.delete(reservation_key)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    # ============ 库存扣减相关 ============

    def deduct_inventory(self, order_id: int, items: List[DeductItem]) -> bool:
        """订单完成后扣减库存"""
        try:
            for item in items:
                inventory = self.get_inventory(item.product_id)
                if not inventory:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"商品 {item.product_id} 库存记录不存在"
                    )
                
                # 检查预占库存是否充足
                if inventory.reserved_quantity < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"商品 {item.product_id} 预占库存不足，需要 {item.quantity}，预占 {inventory.reserved_quantity}"
                    )
                
                # 扣减库存（从预占转为实际扣减）
                inventory.update_quantities(
                    available_delta=0,
                    reserved_delta=-item.quantity
                )
                
                # 记录变动
                self._create_transaction(
                    product_id=item.product_id,
                    transaction_type=TransactionType.OUT,
                    quantity=item.quantity,
                    reference_type=ReferenceType.ORDER,
                    reference_id=order_id,
                    reason="订单扣减库存"
                )
                
                # 清除缓存
                self._clear_inventory_cache(item.product_id)
            
            self.db.commit()
            
            # 删除订单预占记录
            reservation_key = f"inventory:order_reservation:{order_id}"
            self.redis.delete(reservation_key)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    # ============ 库存调整相关 ============

    def adjust_inventory(self, product_id: int, adjustment: InventoryAdjustment, operator_id: int) -> bool:
        """调整商品库存"""
        try:
            inventory = self.get_or_create_inventory(product_id)
            
            before_quantity = inventory.available_quantity
            
            if adjustment.adjustment_type == AdjustmentType.ADD:
                new_quantity = inventory.available_quantity + adjustment.quantity
            elif adjustment.adjustment_type == AdjustmentType.SUBTRACT:
                new_quantity = max(0, inventory.available_quantity - adjustment.quantity)
            else:  # SET
                new_quantity = adjustment.quantity
            
            # 更新库存
            delta = new_quantity - inventory.available_quantity
            inventory.update_quantities(available_delta=delta)
            
            # 记录变动
            self._create_transaction(
                product_id=product_id,
                transaction_type=TransactionType.ADJUST,
                quantity=abs(delta),
                reference_type=ReferenceType.MANUAL,
                reason=adjustment.reason or f"管理员{adjustment.adjustment_type.value}库存",
                operator_id=operator_id,
                before_quantity=before_quantity,
                after_quantity=new_quantity
            )
            
            self.db.commit()
            
            # 清除缓存
            self._clear_inventory_cache(product_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    def update_warning_threshold(self, product_id: int, threshold: int) -> bool:
        """更新预警阈值"""
        try:
            inventory = self.get_or_create_inventory(product_id)
            inventory.warning_threshold = threshold
            
            self.db.commit()
            
            # 清除缓存
            self._clear_inventory_cache(product_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise e

    # ============ 库存变动记录相关 ============

    def get_inventory_transactions(
        self, 
        product_id: int, 
        query_params: TransactionQuery
    ) -> Tuple[List[InventoryTransaction], int]:
        """获取库存变动历史记录"""
        query = (
            self.db.query(InventoryTransaction)
            .filter(InventoryTransaction.product_id == product_id)
        )
        
        # 添加筛选条件
        if query_params.start_date:
            query = query.filter(InventoryTransaction.created_at >= query_params.start_date)
        
        if query_params.end_date:
            query = query.filter(InventoryTransaction.created_at <= query_params.end_date)
        
        if query_params.transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == query_params.transaction_type)
        
        # 排序
        query = query.order_by(desc(InventoryTransaction.created_at))
        
        # 分页
        total = query.count()
        items = query.offset((query_params.page - 1) * query_params.page_size).limit(query_params.page_size).all()
        
        return items, total

    # ============ 辅助方法 ============

    def _create_transaction(
        self,
        product_id: int,
        transaction_type: TransactionType,
        quantity: int,
        reference_type: ReferenceType = None,
        reference_id: int = None,
        reason: str = None,
        operator_id: int = None,
        before_quantity: int = None,
        after_quantity: int = None
    ) -> InventoryTransaction:
        """创建库存变动记录"""
        transaction = InventoryTransaction(
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            operator_id=operator_id,
            before_quantity=before_quantity,
            after_quantity=after_quantity
        )
        self.db.add(transaction)
        return transaction

    def _clear_inventory_cache(self, product_id: int):
        """清除库存相关缓存"""
        # 清除单个商品库存缓存
        cache_keys = [
            f"inventory:product:{product_id}",
            "inventory:low_stock:*"
        ]
        
        for key in cache_keys:
            if "*" in key:
                # 删除匹配的所有键
                keys = self.redis.keys(key)
                if keys:
                    self.redis.delete(*keys)
            else:
                self.redis.delete(key)

    def cleanup_expired_reservations(self):
        """清理过期的购物车预占"""
        try:
            expired_reservations = (
                self.db.query(CartReservation)
                .filter(CartReservation.expires_at <= datetime.utcnow())
                .all()
            )
            
            for reservation in expired_reservations:
                # 释放库存
                inventory = self.get_inventory(reservation.product_id)
                if inventory:
                    inventory.update_quantities(
                        available_delta=reservation.reserved_quantity,
                        reserved_delta=-reservation.reserved_quantity
                    )
                    
                    # 记录变动
                    self._create_transaction(
                        product_id=reservation.product_id,
                        transaction_type=TransactionType.RELEASE,
                        quantity=reservation.reserved_quantity,
                        reference_type=ReferenceType.CART,
                        reference_id=reservation.user_id,
                        reason="预占过期自动释放"
                    )
                    
                    # 清除缓存
                    self._clear_inventory_cache(reservation.product_id)
                
                # 删除预占记录
                self.db.delete(reservation)
            
            self.db.commit()
            return len(expired_reservations)
            
        except Exception as e:
            self.db.rollback()
            raise e
