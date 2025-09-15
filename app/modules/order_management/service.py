"""
文件名：service.py
文件路径：app/modules/order_management/service.py
功能描述：订单管理模块的业务逻辑服务层

主要功能：
- 订单全生命周期管理：创建、查询、更新、删除
- 订单状态流转管理和状态历史记录
- 库存集成：库存检查、预占、扣减
- 订单金额计算和验证
- 事务管理和错误处理

使用说明：
- 导入：from app.modules.order_management.service import OrderService
- 初始化：service = OrderService(db_session)
- 方法调用：order = await service.create_order(order_data, user_id)

依赖模块：
- app.modules.order_management.models: 订单数据模型
- app.modules.order_management.schemas: API请求响应模型
- app.modules.inventory_management.service: 库存管理服务
- app.shared.models: 共享数据模型（Product、User）
- sqlalchemy.orm.Session: 数据库会话管理

业务特性：
- Product+SKU双重关联架构
- 完整的事务管理和错误处理
- 库存预占和释放机制
- 订单状态变更日志记录
- 支持高并发订单创建场景

创建时间：2025-09-15
最后修改：2025-09-15
"""

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import func
from fastapi import HTTPException, status

from .models import Order, OrderItem, OrderStatusHistory, OrderStatus
from .schemas import OrderCreateRequest, OrderItemRequest, ApiResponse
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Product, SKU
from app.modules.inventory_management.service import InventoryService


class OrderService:
    """
    订单管理服务类
    
    提供完整的订单生命周期管理功能，集成库存管理，
    确保数据一致性和业务规则正确性。
    """

    def __init__(self, db: Session):
        """
        初始化订单服务
        
        Args:
            db: 数据库会话实例
        """
        self.db = db
        self.inventory_service = InventoryService(db)

    def _generate_order_number(self) -> str:
        """
        生成订单号
        
        Returns:
            str: 格式为 ORD{timestamp}{random} 的唯一订单号
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4()).replace('-', '')[:8].upper()
        return f"ORD{timestamp}{random_suffix}"
    
    async def create_order(self, order_data: OrderCreateRequest, user_id: int) -> Order:
        """
        创建新订单
        
        完整的订单创建流程：
        1. 验证用户和商品信息
        2. 检查并预占库存
        3. 计算订单金额
        4. 创建订单和订单项
        5. 记录状态变更历史
        
        Args:
            order_data: 订单创建请求数据
            user_id: 用户ID
            
        Returns:
            Order: 创建的订单对象
            
        Raises:
            HTTPException: 各种业务异常情况
        """
        try:
            # 1. 验证用户存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            # 2. 验证并预占库存
            await self._validate_and_reserve_stock(order_data.items, user_id)
            
            # 3. 验证商品信息并计算金额
            total_amount, order_items_data = await self._validate_products_and_calculate_amount(
                order_data.items
            )
            
            # 4. 创建订单 - 使用事务
            order = await self._create_order_with_transaction(
                order_data=order_data,
                user_id=user_id,
                total_amount=total_amount,
                order_items_data=order_items_data
            )
            
            return order
            
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except Exception as e:
            # 记录未预期异常并包装为HTTP异常
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"订单创建失败: {str(e)}"
            )
    
    async def _validate_and_reserve_stock(self, items: List[OrderItemRequest], user_id: int):
        """
        验证并预占库存
        
        Args:
            items: 订单项列表
            user_id: 用户ID（用于预占记录）
            
        Raises:
            HTTPException: 库存不足或其他库存相关异常
        """
        try:
            # 准备预占数据
            reservation_items = []
            for item in items:
                reservation_items.append({
                    "sku_id": str(item.sku_id),
                    "quantity": item.quantity
                })
            
            # 调用库存服务预占库存
            reservation_result = await self.inventory_service.reserve_inventory(
                reservation_type="ORDER",
                reference_id=f"order_temp_{user_id}_{datetime.now().timestamp()}",
                items=reservation_items,
                expires_minutes=30,  # 30分钟预占时间
                user_id=user_id
            )
            
            return reservation_result
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存验证失败: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"库存操作失败: {str(e)}"
            )

    async def _validate_products_and_calculate_amount(
        self, items: List[OrderItemRequest]
    ) -> tuple[Decimal, List[Dict[str, Any]]]:
        """
        验证商品信息并计算订单金额
        
        Args:
            items: 订单项列表
            
        Returns:
            tuple: (总金额, 订单项数据列表)
        """
        total_amount = Decimal('0.00')
        order_items_data = []
        
        for item in items:
            # 获取商品信息
            product = self.db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"商品ID {item.product_id} 不存在"
                )
            
            # 获取SKU信息
            sku = self.db.query(SKU).filter(SKU.id == item.sku_id).first()
            if not sku:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"SKU ID {item.sku_id} 不存在"
                )
            
            # 检查商品状态
            if product.status != 'active':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"商品 {product.name} 当前不可购买"
                )
            
            # 检查SKU状态
            if not sku.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SKU {sku.sku_code} 当前不可购买"
                )
            
            # 使用SKU当前价格（防止价格篡改）
            unit_price = sku.price
            total_price = unit_price * item.quantity
            total_amount += total_price
            
            # 准备订单项数据
            order_items_data.append({
                'product_id': product.id,
                'sku_id': sku.id,
                'sku_code': sku.sku_code,
                'product_name': product.name,
                'sku_name': sku.name if sku.name else product.name,
                'quantity': item.quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })
        
        return total_amount, order_items_data

    async def _create_order_with_transaction(
        self,
        order_data: OrderCreateRequest,
        user_id: int,
        total_amount: Decimal,
        order_items_data: List[Dict[str, Any]]
    ) -> Order:
        """
        在事务中创建订单和相关数据
        
        Args:
            order_data: 订单数据
            user_id: 用户ID
            total_amount: 总金额
            order_items_data: 订单项数据
            
        Returns:
            Order: 创建的订单对象
        """
        try:
            # 创建订单
            order = Order(
                order_number=self._generate_order_number(),
                user_id=user_id,
                status='pending',
                subtotal=total_amount,  # 小计金额
                shipping_fee=Decimal('10.00'),  # 运费
                discount_amount=Decimal('0.00'),  # 折扣金额
                total_amount=total_amount + Decimal('10.00'),  # 总金额 = 小计 + 运费 - 折扣
                shipping_address=f"{order_data.shipping_address.recipient}, {order_data.shipping_address.phone}, {order_data.shipping_address.address}",
                notes=order_data.notes
            )
            
            self.db.add(order)
            self.db.flush()  # 获取订单ID
            
            # 创建订单项
            for item_data in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    **item_data
                )
                self.db.add(order_item)
            
            # 记录状态变更历史
            status_history = OrderStatusHistory(
                order_id=order.id,
                old_status=None,
                new_status=OrderStatus.PENDING.value,
                remark="订单创建",
                operator_id=user_id
            )
            self.db.add(status_history)
            
            self.db.commit()
            self.db.refresh(order)
            
            return order
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"订单数据创建失败: {str(e)}"
            )

    async def get_order_by_id(self, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """
        根据ID获取订单详情
        
        Args:
            order_id: 订单ID
            user_id: 用户ID（可选，用于权限验证）
            
        Returns:
            Order: 订单对象或None
        """
        try:
            query = self.db.query(Order).options(
                joinedload(Order.order_items),
                joinedload(Order.status_history)
            )
            
            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            order = query.filter(Order.id == order_id).first()
            return order
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取订单失败: {str(e)}"
            )
    
    async def get_orders_list(
        self, 
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        获取订单列表
        
        Args:
            user_id: 用户ID筛选（可选）
            status: 状态筛选（可选）
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            List[Order]: 订单列表
        """
        try:
            query = self.db.query(Order).options(
                joinedload(Order.order_items)
            )
            
            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            if status:
                query = query.filter(Order.status == status)
            
            orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
            return orders
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取订单列表失败: {str(e)}"
            )
    
    async def update_order_status(
        self,
        order_id: int,
        new_status: str,
        operator_id: int,
        remark: Optional[str] = None
    ) -> Optional[Order]:
        """
        更新订单状态
        
        完整的状态变更流程：
        1. 验证订单存在
        2. 验证状态转换合法性
        3. 执行状态相关的业务逻辑（如库存操作）
        4. 记录状态变更历史
        
        Args:
            order_id: 订单ID
            new_status: 新状态
            operator_id: 操作者ID
            remark: 备注
            
        Returns:
            Order: 更新后的订单对象或None
            
        Raises:
            HTTPException: 状态转换不合法或其他异常
        """
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="订单不存在"
                )
            
            old_status = order.status
            
            # 验证状态转换合法性
            if not self._is_valid_status_transition(old_status, new_status):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无法从状态 {old_status} 转换到 {new_status}"
                )
            
            # 执行状态相关的业务逻辑
            await self._handle_status_change_business_logic(order, old_status, new_status)
            
            # 更新订单状态
            order.status = new_status  # 直接使用字符串值
            
            # 记录状态变更历史
            status_history = OrderStatusHistory(
                order_id=order.id,
                old_status=old_status,  # 已经是字符串
                new_status=new_status,  # 已经是字符串值
                remark=remark or f"状态从 {old_status} 变更为 {new_status}",
                operator_id=operator_id
            )
            self.db.add(status_history)
            
            self.db.commit()
            self.db.refresh(order)
            
            return order
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新订单状态失败: {str(e)}"
            )

    def _is_valid_status_transition(
        self, 
        current_status: str, 
        new_status: str
    ) -> bool:
        """
        验证订单状态转换是否合法
        
        Args:
            current_status: 当前状态
            new_status: 目标状态
            
        Returns:
            bool: 转换是否合法
        """
        valid_transitions = {
            "pending": ["paid", "cancelled"],
            "paid": ["shipped", "cancelled"],
            "shipped": ["delivered", "returned"],
            "delivered": ["returned"],
            "cancelled": [],
            "returned": []
        }
        
        return new_status in valid_transitions.get(current_status, [])

    async def _handle_status_change_business_logic(
        self,
        order: Order,
        old_status: str,
        new_status: str
    ):
        """
        处理状态变更相关的业务逻辑
        
        Args:
            order: 订单对象
            old_status: 原状态
            new_status: 新状态
        """
        # 订单取消 - 释放库存
        if new_status == "cancelled" and old_status != "cancelled":
            await self._release_order_stock(order)
        
        # 订单支付 - 确认库存扣减
        elif new_status == "paid" and old_status == "pending":
            await self._confirm_stock_deduction(order)

    async def _release_order_stock(self, order: Order):
        """
        释放订单库存
        
        Args:
            order: 订单对象
        """
        try:
            # 导入所需的模型
            from app.modules.inventory_management.models import InventoryStock
            
            for item in order.order_items:
                # 获取库存记录并释放数量
                inventory = self.db.query(InventoryStock).filter(
                    InventoryStock.sku_id == item.sku_id
                ).with_for_update().first()
                
                if inventory:
                    inventory.release_quantity(item.quantity)
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            # 库存释放失败不应阻止订单状态变更，但需要记录
            # 可以考虑使用日志或消息队列进行异步处理
            pass

    async def _confirm_stock_deduction(self, order: Order):
        """
        确认库存扣减
        
        Args:
            order: 订单对象
        """
        try:
            # 导入所需的模型
            from app.modules.inventory_management.models import InventoryStock
            
            for item in order.order_items:
                # 获取库存记录并确认扣减
                inventory = self.db.query(InventoryStock).filter(
                    InventoryStock.sku_id == item.sku_id
                ).with_for_update().first()
                
                if inventory:
                    # 从预占库存中扣减（实际出库）
                    if not inventory.deduct_quantity(item.quantity, from_reserved=True):
                        raise Exception(f"SKU {item.sku_id} 预占库存不足，无法确认扣减")
            
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            # 库存确认失败需要处理，可能需要回滚订单状态
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"库存确认失败: {str(e)}"
            )
    
    async def cancel_order(self, order_id: int, operator_id: int, reason: Optional[str] = None) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            operator_id: 操作者ID
            reason: 取消原因
            
        Returns:
            bool: 取消成功返回True，失败返回False
        """
        try:
            order = await self.update_order_status(
                order_id=order_id,
                new_status="cancelled",
                operator_id=operator_id,
                remark=reason or "订单取消"
            )
            return order is not None
        except Exception:
            return False
    
    async def get_order_items(self, order_id: int, user_id: Optional[int] = None) -> List[OrderItem]:
        """
        获取订单项列表
        
        Args:
            order_id: 订单ID
            user_id: 用户ID（可选，用于权限验证）
            
        Returns:
            List[OrderItem]: 订单项列表
        """
        try:
            query = self.db.query(OrderItem).join(Order).filter(OrderItem.order_id == order_id)
            
            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            items = query.all()
            return items
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取订单项失败: {str(e)}"
            )

    async def get_order_status_history(self, order_id: int) -> List[OrderStatusHistory]:
        """
        获取订单状态变更历史
        
        Args:
            order_id: 订单ID
            
        Returns:
            List[OrderStatusHistory]: 状态变更历史列表
        """
        try:
            history = self.db.query(OrderStatusHistory).filter(
                OrderStatusHistory.order_id == order_id
            ).order_by(OrderStatusHistory.created_at.desc()).all()
            
            return history
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取状态历史失败: {str(e)}"
            )
    
    async def calculate_order_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        计算订单统计信息
        
        Args:
            user_id: 用户ID（可选，计算指定用户的统计）
            
        Returns:
            dict: 包含各种统计信息的字典
        """
        try:
            query = self.db.query(Order)
            if user_id:
                query = query.filter(Order.user_id == user_id)
            
            # 基础统计 - 使用枚举的值属性以支持SQLite
            total_orders = query.count()
            pending_orders = query.filter(Order.status == OrderStatus.PENDING.value).count()
            paid_orders = query.filter(Order.status == OrderStatus.PAID.value).count()
            shipped_orders = query.filter(Order.status == OrderStatus.SHIPPED.value).count()
            delivered_orders = query.filter(Order.status == OrderStatus.DELIVERED.value).count()
            cancelled_orders = query.filter(Order.status == OrderStatus.CANCELLED.value).count()
            returned_orders = query.filter(Order.status == OrderStatus.RETURNED.value).count()
            
            # 计算总金额（已支付和已完成的订单）- 使用枚举的值属性
            amount_query = self.db.query(func.sum(Order.total_amount)).filter(
                Order.status.in_([OrderStatus.PAID.value, OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value])
            )
            if user_id:
                amount_query = amount_query.filter(Order.user_id == user_id)
            total_amount = amount_query.scalar() or Decimal('0.00')
            
            return {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'paid_orders': paid_orders,
                'shipped_orders': shipped_orders,
                'delivered_orders': delivered_orders,
                'cancelled_orders': cancelled_orders,
                'returned_orders': returned_orders,
                'total_amount': float(total_amount),
                'completion_rate': round((delivered_orders / total_orders * 100) if total_orders > 0 else 0, 2),
                'cancellation_rate': round((cancelled_orders / total_orders * 100) if total_orders > 0 else 0, 2)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"计算统计信息失败: {str(e)}"
            )

    async def get_orders_by_status(self, status: OrderStatus, limit: int = 100) -> List[Order]:
        """
        根据状态获取订单列表
        
        Args:
            status: 订单状态
            limit: 限制数量
            
        Returns:
            List[Order]: 订单列表
        """
        try:
            orders = self.db.query(Order).filter(
                Order.status == status
            ).order_by(Order.created_at.desc()).limit(limit).all()
            
            return orders
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取订单列表失败: {str(e)}"
            )