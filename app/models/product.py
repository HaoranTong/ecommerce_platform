"""
文件名：product.py
文件路径：app/models/product.py
功能描述：商品和分类管理相关的数据模型定义
主要功能：
- Category分类模型：商品分类层级管理
- Product商品模型：商品基础信息、价格、库存管理
- 商品分类关联关系
使用说明：
- 导入：from app.models.product import Product, Category
- 关系：Category与Product的一对多关系
依赖模块：
- app.models.base: 基础模型类和时间戳混合类
- sqlalchemy: 数据库字段定义和关系映射
"""

from sqlalchemy import Column, String, Text, DECIMAL, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, TimestampMixin


class Category(BaseModel, TimestampMixin):
    """商品分类模型"""
    __tablename__ = 'categories'
    
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 分类层级关系
    children = relationship("Category", backref="parent", remote_side=[BaseModel.id])
    
    # 关系映射（延迟导入避免循环依赖）
    def __init_relationships__(self):
        """初始化关系映射"""
        self.products = relationship("Product", back_populates="category")
    
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
    
    # 关系映射（延迟导入避免循环依赖）
    def __init_relationships__(self):
        """初始化关系映射"""
        self.order_items = relationship("OrderItem", back_populates="product")
        self.cart_items = relationship("Cart", back_populates="product")
    
    # 索引优化
    __table_args__ = (
        Index('idx_category_status', 'category_id', 'status'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_sku', 'sku'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"