"""
文件名：repository.py
文件路径：app/modules/shopping_cart/repository.py
功能描述：购物车模块的数据访问层（Repository Pattern）
主要功能：
- CartRepository: 购物车主表数据访问接口
- CartItemRepository: 购物车商品项数据访问接口
- 数据库查询封装：提供统一的CRUD操作接口
- 职责隔离：将数据访问逻辑从Service层分离
使用说明：
- 导入：from app.modules.shopping_cart.repository import CartRepository
- 实例化：cart_repo = CartRepository(db_session)
- 调用：cart = cart_repo.find_by_user_id(user_id)
依赖模块：
- sqlalchemy.orm.Session: 数据库会话管理
- app.modules.shopping_cart.models: Cart, CartItem数据模型
创建时间：2025-10-10
架构决策：实施四层架构，符合依赖倒置原则
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from .models import Cart, CartItem

logger = logging.getLogger(__name__)


class CartRepository:
    """
    购物车主表数据访问仓库

    职责：
        - 封装Cart表的所有数据库操作
        - 提供统一的查询、创建、更新、删除接口
        - 隐藏SQLAlchemy具体实现细节

    设计原则：
        - 单一职责：仅负责购物车主表数据访问
        - 接口隔离：提供最小必要的方法集合
        - 依赖倒置：Service依赖Repository抽象，不直接依赖数据库
    """

    def __init__(self, db: Session):
        """
        初始化购物车仓库

        Args:
            db (Session): SQLAlchemy数据库会话
        """
        self.db = db

    def find_by_user_id(self, user_id: int) -> Optional[Cart]:
        """
        根据用户ID查找购物车

        Args:
            user_id (int): 用户ID

        Returns:
            Optional[Cart]: 购物车实例，不存在时返回None
        """
        return self.db.query(Cart).filter(Cart.user_id == user_id).first()

    def find_by_id(self, cart_id: int) -> Optional[Cart]:
        """
        根据购物车ID查找

        Args:
            cart_id (int): 购物车ID

        Returns:
            Optional[Cart]: 购物车实例，不存在时返回None
        """
        return self.db.query(Cart).filter(Cart.id == cart_id).first()

    def create(self, user_id: int) -> Cart:
        """
        创建新购物车

        Args:
            user_id (int): 用户ID

        Returns:
            Cart: 新创建的购物车实例

        Note:
            - 此方法仅创建对象并添加到session，不提交事务
            - 调用方需要自行管理事务提交
        """
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.flush()  # 刷新以获取ID，但不提交事务
        return cart

    def get_or_create(self, user_id: int) -> Cart:
        """
        获取或创建购物车（幂等操作）

        Args:
            user_id (int): 用户ID

        Returns:
            Cart: 现有或新创建的购物车实例
        """
        cart = self.find_by_user_id(user_id)
        if not cart:
            cart = self.create(user_id)
        return cart

    def update_timestamp(self, cart: Cart) -> None:
        """
        更新购物车时间戳

        Args:
            cart (Cart): 购物车实例
        """
        cart.updated_at = datetime.utcnow()

    def delete(self, cart: Cart) -> None:
        """
        删除购物车（物理删除）

        Args:
            cart (Cart): 要删除的购物车实例

        Warning:
            - 由于级联删除配置，会同时删除所有购物车商品项
            - 调用方需要自行管理事务提交
        """
        self.db.delete(cart)


class CartItemRepository:
    """
    购物车商品项数据访问仓库

    职责：
        - 封装CartItem表的所有数据库操作
        - 提供购物车商品项的查询、创建、更新、删除接口
        - 支持批量操作和复杂查询
    """

    def __init__(self, db: Session):
        """
        初始化购物车商品项仓库

        Args:
            db (Session): SQLAlchemy数据库会话
        """
        self.db = db

    def find_by_id(self, item_id: int) -> Optional[CartItem]:
        """
        根据ID查找购物车商品项

        Args:
            item_id (int): 商品项ID

        Returns:
            Optional[CartItem]: 商品项实例，不存在时返回None
        """
        return self.db.query(CartItem).filter(CartItem.id == item_id).first()

    def find_by_cart_and_sku(self, cart_id: int, sku_id: int) -> Optional[CartItem]:
        """
        根据购物车ID和SKU ID查找商品项

        用途：检查商品是否已在购物车中

        Args:
            cart_id (int): 购物车ID
            sku_id (int): 商品SKU ID

        Returns:
            Optional[CartItem]: 商品项实例，不存在时返回None
        """
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.sku_id == sku_id)
            .first()
        )

    def find_by_cart_id(self, cart_id: int) -> List[CartItem]:
        """
        查找购物车的所有商品项

        Args:
            cart_id (int): 购物车ID

        Returns:
            List[CartItem]: 商品项列表，可能为空列表
        """
        return self.db.query(CartItem).filter(CartItem.cart_id == cart_id).all()

    def find_by_id_and_user(self, item_id: int, user_id: int) -> Optional[CartItem]:
        """
        根据商品项ID和用户ID查找（权限验证）

        用途：确保用户只能访问自己的购物车商品项

        Args:
            item_id (int): 商品项ID
            user_id (int): 用户ID

        Returns:
            Optional[CartItem]: 商品项实例，不存在或无权限时返回None
        """
        return (
            self.db.query(CartItem)
            .join(Cart)
            .filter(CartItem.id == item_id, Cart.user_id == user_id)
            .first()
        )

    def count_by_cart_id(self, cart_id: int) -> int:
        """
        统计购物车中商品种类数量

        Args:
            cart_id (int): 购物车ID

        Returns:
            int: 商品种类数量
        """
        return self.db.query(CartItem).filter(CartItem.cart_id == cart_id).count()

    def create(self, cart_item: CartItem) -> CartItem:
        """
        创建新的购物车商品项

        Args:
            cart_item (CartItem): 商品项实例

        Returns:
            CartItem: 创建后的商品项实例

        Note:
            - 此方法仅添加到session，不提交事务
            - 调用方需要自行管理事务提交
        """
        self.db.add(cart_item)
        self.db.flush()  # 刷新以获取ID
        return cart_item

    def update(self, cart_item: CartItem) -> None:
        """
        更新购物车商品项

        Args:
            cart_item (CartItem): 已修改的商品项实例

        Note:
            - SQLAlchemy会自动跟踪对象变更
            - 此方法主要用于显式标记更新意图
        """
        cart_item.updated_at = datetime.utcnow()

    def delete(self, cart_item: CartItem) -> None:
        """
        删除购物车商品项

        Args:
            cart_item (CartItem): 要删除的商品项实例
        """
        self.db.delete(cart_item)

    def delete_by_ids(self, item_ids: List[int], user_id: int) -> int:
        """
        批量删除购物车商品项（带权限验证）

        Args:
            item_ids (List[int]): 商品项ID列表
            user_id (int): 用户ID，用于权限验证

        Returns:
            int: 实际删除的商品项数量
        """
        items = (
            self.db.query(CartItem)
            .join(Cart)
            .filter(CartItem.id.in_(item_ids), Cart.user_id == user_id)
            .all()
        )

        for item in items:
            self.db.delete(item)

        return len(items)

    def delete_by_cart_id(self, cart_id: int) -> int:
        """
        删除购物车的所有商品项

        Args:
            cart_id (int): 购物车ID

        Returns:
            int: 删除的商品项数量
        """
        deleted_count = (
            self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        )
        return deleted_count
