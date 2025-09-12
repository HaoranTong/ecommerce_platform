"""
文件名：__init__.py
文件路径：app/models/__init__.py
功能描述：数据模型模块统一导出和初始化
主要功能：
- 统一导出所有数据模型类
- 初始化模型之间的关系映射
- 提供模型访问的统一入口
使用说明：
- 导入：from app.models import User, Product, Order, Payment
- 或：from app.models.user import User
- 基类：from app.models.base import Base
依赖模块：
- app.models.base: 基础模型配置
- app.models.user: 用户相关模型
- app.models.product: 商品相关模型
- app.models.order: 订单相关模型
- app.models.payment: 支付相关模型
"""

# 导入基础配置
from .base import Base, BaseModel, TimestampMixin

# 导入所有模型
from .user import User
from .product import Product, Category
from .order import Order, OrderItem, Cart
from .payment import Payment, Refund

# 统一导出所有模型
__all__ = [
    # 基础类
    'Base',
    'BaseModel', 
    'TimestampMixin',
    
    # 用户模块
    'User',
    
    # 商品模块
    'Product',
    'Category',
    
    # 订单模块
    'Order',
    'OrderItem',
    'Cart',
    
    # 支付模块
    'Payment',
    'Refund'
]


def init_relationships():
    """
    初始化模型之间的关系映射
    解决循环导入问题
    """
    # 用户关系
    from sqlalchemy.orm import relationship
    
    # User关系
    User.orders = relationship("Order", back_populates="user")
    User.payments = relationship("Payment", back_populates="user") 
    User.carts = relationship("Cart", back_populates="user")
    
    # Category关系
    Category.products = relationship("Product", back_populates="category")
    
    # Product关系  
    Product.order_items = relationship("OrderItem", back_populates="product")
    Product.cart_items = relationship("Cart", back_populates="product")
    
    # Order关系
    Order.payments = relationship("Payment", back_populates="order")
    
    print("✅ 模型关系映射初始化完成")


# 自动初始化关系（可选，在应用启动时调用）
# init_relationships()