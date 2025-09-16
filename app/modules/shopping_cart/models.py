"""
文件名：models.py
文件路径：app/modules/shopping_cart/models.py
功能描述：购物车模块的数据模型定义
主要功能：
- Cart: 购物车主表模型，一对一关联用户
- CartItem: 购物车商品项模型，多对一关联购物车和商品
使用说明：
- 导入：from app.modules.shopping_cart.models import Cart, CartItem
- 关联关系：User(1) -> Cart(1) -> CartItem(N) -> Product(1)
依赖模块：
- app.shared.base_models.Base: 统一ORM基础类
- sqlalchemy: ORM框架
创建时间：2025-09-16
最后修改：2025-09-16
"""
from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.shared.base_models import Base
from datetime import datetime
from decimal import Decimal


class Cart(Base):
    """
    购物车主表模型
    
    业务规则：
    - 每个用户只有一个活跃购物车（user_id唯一约束）
    - 购物车删除时级联删除所有商品项
    - 自动维护创建时间和更新时间
    """
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='购物车ID')
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), 
                     nullable=False, unique=True, comment='用户ID，唯一约束确保每用户一个购物车')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, 
                       nullable=False, comment='更新时间')
    
    # 索引定义
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
    )
    
    # 关联关系
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan",
                        passive_deletes=True, lazy='select')
    
    @property
    def total_items(self) -> int:
        """购物车商品种类数量"""
        return len(self.items)
    
    @property
    def total_quantity(self) -> int:
        """购物车商品总数量"""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self) -> Decimal:
        """购物车总金额"""
        return sum(item.subtotal for item in self.items)
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={self.total_items})>"


class CartItem(Base):
    """
    购物车商品项模型
    
    业务规则：
    - 每个购物车中同一商品只能有一条记录（cart_id + sku_id 唯一约束）
    - 数量必须为正整数且不超过999
    - 单价必须为非负数
    - 删除购物车时级联删除商品项
    """
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='商品项ID')
    cart_id = Column(Integer, ForeignKey('carts.id', ondelete='CASCADE'), 
                     nullable=False, comment='购物车ID')
    sku_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), 
                    nullable=False, comment='商品SKU ID')
    quantity = Column(Integer, nullable=False, default=1, comment='商品数量')
    unit_price = Column(Numeric(10, 2), nullable=False, comment='加入时的商品单价')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, 
                       nullable=False, comment='更新时间')
    
    # 约束定义
    __table_args__ = (
        UniqueConstraint('cart_id', 'sku_id', name='uk_cart_sku'),
        CheckConstraint('quantity > 0 AND quantity <= 999', name='chk_quantity_range'),
        CheckConstraint('unit_price >= 0', name='chk_unit_price_non_negative'),
        Index('idx_cart_id', 'cart_id'),
        Index('idx_sku_id', 'sku_id'),
    )
    
    # 关联关系
    cart = relationship("Cart", back_populates="items")
    
    @property
    def subtotal(self) -> Decimal:
        """计算商品项小计金额"""
        return Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
    
    def update_quantity(self, new_quantity: int) -> None:
        """
        更新商品数量
        
        Args:
            new_quantity: 新的数量值
            
        Raises:
            ValueError: 当数量不在有效范围内时
        """
        if not (1 <= new_quantity <= 999):
            raise ValueError(f"数量必须在1-999之间，当前值: {new_quantity}")
        self.quantity = new_quantity
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, sku_id={self.sku_id}, quantity={self.quantity})>"
