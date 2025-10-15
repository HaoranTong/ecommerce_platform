"""
订单管理模块数据访问层（Repository）

该层负责与数据库交互，提供对订单、订单项及状态历史等模型的查询与持久化操作，
并为服务层屏蔽底层 ORM 细节。事务提交与业务编排仍由服务层负责。
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.modules.inventory_management.models import InventoryStock
from app.modules.product_catalog.models import Product, SKU
from app.modules.user_auth.models import User

from .models import Order, OrderItem, OrderStatus, OrderStatusHistory


class OrderRepository:
    """订单管理数据访问封装。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ========== 基础实体检索 ==========

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.query(Product).filter(Product.id == product_id).first()

    def get_sku_by_id(self, sku_id: int) -> Optional[SKU]:
        return self.session.query(SKU).filter(SKU.id == sku_id).first()

    # ========== 订单与相关实体操作 ==========

    def save_order(self, order: Order) -> Order:
        """保存订单（不提交事务）"""
        self.session.add(order)
        self.session.flush()
        self.session.refresh(order)
        return order

    def save_order_item(self, order_item: OrderItem) -> OrderItem:
        """保存订单项（不提交事务）"""
        self.session.add(order_item)
        self.session.flush()
        self.session.refresh(order_item)
        return order_item

    def save_status_history(self, history: OrderStatusHistory) -> OrderStatusHistory:
        """保存订单状态历史（不提交事务）"""
        self.session.add(history)
        self.session.flush()
        self.session.refresh(history)
        return history

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.session.query(Order)
            .options(joinedload(Order.order_items), joinedload(Order.status_history))
            .filter(Order.id == order_id)
            .first()
        )

    def get_order_with_items(self, order_id: int) -> Optional[Order]:
        """获取包含订单项的订单信息。"""
        return (
            self.session.query(Order)
            .options(joinedload(Order.order_items))
            .filter(Order.id == order_id)
            .first()
        )

    def list_orders(
        self,
        *,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Order], int]:
        query = self.session.query(Order).options(joinedload(Order.order_items))

        if user_id:
            query = query.filter(Order.user_id == user_id)

        if status:
            status_value = status.value if isinstance(status, OrderStatus) else status
            query = query.filter(Order.status == status_value)

        total_count = query.order_by(None).count()
        orders = (
            query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        )
        return orders, total_count

    def get_order_items(
        self, order_id: int, *, user_id: Optional[int] = None
    ) -> List[OrderItem]:
        query = (
            self.session.query(OrderItem)
            .join(Order)
            .filter(OrderItem.order_id == order_id)
        )

        if user_id:
            query = query.filter(Order.user_id == user_id)

        return query.all()

    def get_order_status_history(self, order_id: int) -> List[OrderStatusHistory]:
        return (
            self.session.query(OrderStatusHistory)
            .filter(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.created_at.desc())
            .all()
        )

    def get_orders_by_status(
        self, status: OrderStatus, *, limit: int = 100
    ) -> List[Order]:
        status_value = status.value if isinstance(status, OrderStatus) else status
        return (
            self.session.query(Order)
            .filter(Order.status == status_value)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )

    # ========== 库存相关 ==========

    def get_inventory_stock_for_update(self, sku_id: int) -> Optional[InventoryStock]:
        return (
            self.session.query(InventoryStock)
            .filter(InventoryStock.sku_id == sku_id)
            .with_for_update()
            .first()
        )

    # ========== 统计信息 ==========

    def calculate_order_statistics(
        self, *, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        query = self.session.query(Order)
        if user_id:
            query = query.filter(Order.user_id == user_id)

        total_orders = query.count()
        pending_orders = query.filter(Order.status == OrderStatus.PENDING.value).count()
        paid_orders = query.filter(Order.status == OrderStatus.PAID.value).count()
        shipped_orders = query.filter(Order.status == OrderStatus.SHIPPED.value).count()
        delivered_orders = (
            query.filter(Order.status == OrderStatus.DELIVERED.value).count()
        )
        cancelled_orders = (
            query.filter(Order.status == OrderStatus.CANCELLED.value).count()
        )
        returned_orders = (
            query.filter(Order.status == OrderStatus.RETURNED.value).count()
        )

        amount_query = self.session.query(func.sum(Order.total_amount)).filter(
            Order.status.in_(
                [
                    OrderStatus.PAID.value,
                    OrderStatus.SHIPPED.value,
                    OrderStatus.DELIVERED.value,
                ]
            )
        )
        if user_id:
            amount_query = amount_query.filter(Order.user_id == user_id)
        total_amount = amount_query.scalar() or Decimal("0.00")

        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "paid_orders": paid_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "returned_orders": returned_orders,
            "total_amount": float(total_amount),
        }

    # ========== 事务控制 ==========

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, entity: Any) -> None:
        self.session.refresh(entity)
