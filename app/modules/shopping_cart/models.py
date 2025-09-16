"""
购物车模块数据模型
文件路径：app/modules/shopping_cart/models.py
功能描述：购物车和购物车商品项的SQLAlchemy ORM模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.shared.base_models import Base
from datetime import datetime
from decimal import Decimal

class ShoppingCart(Base):
    """购物车主表模型"""
    __tablename__ = "shopping_carts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    user = relationship("User", back_populates="shopping_cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ShoppingCart(id={self.id}, user_id={self.user_id}, items={len(self.items)})>"

class CartItem(Base):
    """购物车商品项模型"""
    __tablename__ = "cart_items"
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='check_price_non_negative'),
    )
    
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('shopping_carts.id'), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey('skus.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    cart = relationship("ShoppingCart", back_populates="items")
    sku = relationship("SKU", back_populates="cart_items")
    
    @property
    def subtotal(self) -> Decimal:
        """计算小计金额"""
        return Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, sku_id={self.sku_id}, quantity={self.quantity})>"
