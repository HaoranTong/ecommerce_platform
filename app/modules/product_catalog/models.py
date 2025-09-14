"""
商品目录模块数据模型

根据 docs/modules/data-models/overview.md 文档规范实现
符合数据库设计原则和字段命名标准

主要模型:
- Category: 商品分类层次结构管理
- Product: 商品信息、库存和状态管理
"""

from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, Integer, Boolean, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship

# 从技术基础设施层导入统一的Base类
from app.core.database import Base
# 从共享组件层导入混入类
from app.shared.base_models import TimestampMixin, SoftDeleteMixin, JSONType, ModelRegistry


@ModelRegistry.register
class Category(Base):
    """分类模型 - 管理商品分类层次结构
    
    根据数据模型文档规范实现，包含：
    - BigInteger主键
    - 层次结构支持（parent_id自引用）
    - 排序支持（sort_order）
    - 状态控制（is_active）
    """
    __tablename__ = 'categories'
    
    # 主键 - 使用BigInteger
    id = Column(BigInteger, primary_key=True, index=True)
    
    # 分类基础信息
    name = Column(String(100), nullable=False)
    
    # 层次结构 - 自引用外键
    parent_id = Column(BigInteger, ForeignKey('categories.id'), nullable=True)
    
    # 排序和状态
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳 - 仅创建时间（根据文档字段定义）
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # 关系定义
    # 一对多：分类可以包含多个商品
    products = relationship("Product", back_populates="category")
    
    # 自引用关系：父子分类
    children = relationship("Category", backref="parent", remote_side=[id])
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"


@ModelRegistry.register  
class Product(Base, SoftDeleteMixin):
    """商品模型 - 管理商品信息、库存和状态
    
    根据数据模型文档规范实现，包含：
    - BigInteger主键
    - SKU唯一性约束
    - 灵活属性（JSON存储）
    - 软删除支持
    - 状态管理和索引优化
    """
    __tablename__ = 'products'
    
    # 主键 - 使用BigInteger
    id = Column(BigInteger, primary_key=True, index=True)
    
    # 商品基础信息
    name = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # 分类关联
    category_id = Column(BigInteger, ForeignKey('categories.id'), nullable=True)
    
    # 价格和库存
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # 商品状态 - 枚举值: active, inactive, out_of_stock
    status = Column(String(20), nullable=False, default='active')
    
    # 商品图片
    image_url = Column(String(500), nullable=True)
    
    # 商品属性 - 使用JSONType存储灵活属性
    attributes = Column(JSONType, nullable=True)  # JSON格式: {"color":"钛原色","storage":"128GB"}
    images = Column(JSONType, nullable=True)      # JSON格式: ["url1","url2","url3"]
    
    # 软删除字段由SoftDeleteMixin提供：
    # - is_deleted: Boolean, default=False, nullable=False  
    # - deleted_at: DateTime, nullable=True
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关系定义
    # 多对一：商品属于一个分类
    category = relationship("Category", back_populates="products")
    # 一对多：商品可以出现在多个订单项中
    order_items = relationship("OrderItem", back_populates="product")
    
    # 索引优化 - 根据文档规范使用 idx_{表名}_{字段名} 格式
    __table_args__ = (
        Index('idx_products_category_status', 'category_id', 'status'),  # 分类状态复合索引
        Index('idx_products_status_created', 'status', 'created_at'),    # 状态时间复合索引  
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}', status='{self.status}')>"


# 导出模型
__all__ = ['Category', 'Product']