"""
文件名：product.py
文件路径：app/models/product.py
功能描述：商品和分类管理相关的数据模型定义
主要功能：
- Category分类模型：商品分类层级管理
- Product商品模型：商品基础信息、价格、库存管理
- Inventory库存模型：详细库存管理、预占机制
- InventoryTransaction库存交易记录模型：库存变更日志
- CartReservation购物车预占模型：临时库存锁定
使用说明：
- 导入：from app.models.product import Product, Category, Inventory, InventoryTransaction, CartReservation
- 关系：Category与Product的一对多关系，Product与Inventory的一对一关系
依赖模块：
- app.models.base: 基础模型类和时间戳混合类
- sqlalchemy: 数据库字段定义和关系映射
"""

from sqlalchemy import Column, String, Text, DECIMAL, Integer, Boolean, ForeignKey, Index, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, TimestampMixin
import enum


# 枚举定义
class TransactionType(enum.Enum):
    """库存交易类型枚举"""
    IN = "in"           # 入库
    OUT = "out"         # 出库
    RESERVE = "reserve" # 预占
    RELEASE = "release" # 释放
    ADJUST = "adjust"   # 调整


class ReferenceType(enum.Enum):
    """关联类型枚举"""
    PURCHASE = "purchase"     # 采购入库
    SALE = "sale"            # 销售出库
    CART = "cart"            # 购物车预占
    ORDER = "order"          # 订单锁定
    MANUAL = "manual"        # 手工调整
    SYSTEM = "system"        # 系统调整


class Category(BaseModel, TimestampMixin):
    """商品分类模型"""
    __tablename__ = 'categories'
    
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 分类层级关系（暂时注释掉，避免循环引用问题）
    # children = relationship("Category", backref="parent", remote_side=[id])
    
    # 关系映射
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Product(BaseModel, TimestampMixin):
    """商品模型"""
    __tablename__ = 'products'
    
    # 基础信息
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 分类关联
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # 价格和库存
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # 商品状态
    status = Column(String(20), nullable=False, default='active')  # active, inactive, out_of_stock
    
    # 商品图片
    image_url = Column(String(500), nullable=True)  # 主图URL
    
    # 商品属性（JSON 存储，为后续扩展预留）
    attributes = Column(Text, nullable=True)  # JSON string
    images = Column(Text, nullable=True)      # JSON string of image URLs
    
    # 关系映射
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product") 
    cart_items = relationship("Cart", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    
    # 索引优化
    __table_args__ = (
        Index('idx_category_status', 'category_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_sku', 'sku'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"


class Inventory(BaseModel, TimestampMixin):
    """库存模型"""
    __tablename__ = 'inventory'
    
    # 商品关联
    product_id = Column(Integer, ForeignKey('products.id'), unique=True, nullable=False)
    
    # 库存数量
    total_quantity = Column(Integer, nullable=False, default=0)        # 总库存
    available_quantity = Column(Integer, nullable=False, default=0)    # 可用库存
    reserved_quantity = Column(Integer, nullable=False, default=0)     # 预占库存
    
    # 预警设置
    warning_threshold = Column(Integer, nullable=False, default=10)    # 低库存预警阈值
    
    # 关系定义
    product = relationship("Product", back_populates="inventory")
    
    # 索引定义
    __table_args__ = (
        Index('idx_inventory_available_quantity', 'available_quantity'),
        Index('idx_inventory_warning_threshold', 'warning_threshold'),
    )
    
    @property
    def is_low_stock(self):
        """判断是否为低库存"""
        return self.available_quantity <= self.warning_threshold
    
    @property
    def is_out_of_stock(self):
        """判断是否缺货"""
        return self.available_quantity <= 0
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, product_id={self.product_id}, available={self.available_quantity})>"


class InventoryTransaction(BaseModel, TimestampMixin):
    """库存交易记录模型"""
    __tablename__ = 'inventory_transactions'
    
    # 商品关联
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 交易信息
    transaction_type = Column(Enum(TransactionType), nullable=False)   # 交易类型
    quantity = Column(Integer, nullable=False)                         # 变更数量(正数为增加，负数为减少)
    
    # 库存快照
    before_quantity = Column(Integer, nullable=True)                   # 变更前数量
    after_quantity = Column(Integer, nullable=True)                    # 变更后数量
    
    # 关联信息
    reference_type = Column(Enum(ReferenceType), nullable=False)       # 关联类型
    reference_id = Column(Integer, nullable=True)                      # 关联ID(订单ID、购物车ID等)
    
    # 操作信息
    operator_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 操作员ID
    remark = Column(Text, nullable=True)                               # 备注
    
    # 关系定义
    product = relationship("Product")
    operator = relationship("User")
    
    # 索引定义
    __table_args__ = (
        Index('idx_inventory_transactions_product_created', 'product_id', 'created_at'),
        Index('idx_inventory_transactions_reference', 'reference_type', 'reference_id'),
        Index('idx_inventory_transactions_created_at', 'created_at'),
        Index('idx_inventory_transactions_type', 'transaction_type'),
    )
    
    def __repr__(self):
        return f"<InventoryTransaction(id={self.id}, product_id={self.product_id}, type={self.transaction_type})>"


class CartReservation(BaseModel, TimestampMixin):
    """购物车库存预占模型"""
    __tablename__ = 'cart_reservations'
    
    # 用户和商品关联
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 预占信息
    quantity = Column(Integer, nullable=False)                         # 预占数量
    expires_at = Column(DateTime, nullable=False)                      # 过期时间
    status = Column(String(20), nullable=False, default='active')      # 状态: active, expired, consumed
    
    # 关联信息
    cart_id = Column(Integer, nullable=True)                           # 购物车ID(可选)
    order_id = Column(Integer, nullable=True)                          # 订单ID(转换为订单时填入)
    
    # 关系定义
    user = relationship("User")
    product = relationship("Product")
    
    # 索引定义
    __table_args__ = (
        Index('idx_cart_reservations_user_product', 'user_id', 'product_id'),
        Index('idx_cart_reservations_expires', 'expires_at'),
        Index('idx_cart_reservations_status', 'status'),
    )
    
    def __repr__(self):
        return f"<CartReservation(id={self.id}, user_id={self.user_id}, product_id={self.product_id})>"