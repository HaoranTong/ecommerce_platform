"""
商品目录模块数据模型

根据 docs/design/modules/product-catalog/overview.md 文档规范实现
严格符合数据库设计原则和字段命名标准

主要模型:
- Category: 商品分类层次结构管理 
- Product: 商品信息、库存和状态管理
- Brand: 品牌信息管理
- SKU: 商品规格管理
- ProductAttribute: 商品属性管理
- ProductImage: 商品图片管理
- ProductTag: 商品标签管理
"""

from sqlalchemy import Column, String, Text, DECIMAL, Integer, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship

# 从技术基础设施层导入统一的Base类
from app.core.database import Base
# 从共享组件层导入混入类
from app.shared.base_models import TimestampMixin, SoftDeleteMixin, JSONType, ModelRegistry


@ModelRegistry.register
class Category(Base, TimestampMixin, SoftDeleteMixin):
    """分类模型 - 管理商品分类层次结构
    
    根据数据模型文档规范实现，包含：
    - Integer主键（遵循database-standards.md标准）
    - 层次结构支持（parent_id自引用）
    - 排序支持（sort_order）
    - 状态控制（is_active）
    - 时间戳自动维护（TimestampMixin）
    - 软删除支持（SoftDeleteMixin）
    """
    __tablename__ = 'categories'
    
    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 分类基础信息
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 层次结构 - 自引用外键
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # 排序和状态
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系定义
    # 一对多：分类可以包含多个商品
    products = relationship("Product", back_populates="category")
    
    # 自引用关系：父子分类
    parent = relationship("Category", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"


@ModelRegistry.register
class Brand(Base, TimestampMixin):
    """品牌模型 - 管理商品品牌信息
    
    根据overview.md文档规范实现，包含：
    - Integer主键（遵循database-standards.md标准）
    - 唯一性约束（name, slug）
    - SEO友好的slug字段
    - 时间戳自动维护（TimestampMixin）
    """
    __tablename__ = 'brands'
    
    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 品牌基础信息
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系定义
    products = relationship("Product", back_populates="brand")
    
    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', slug='{self.slug}')>"


@ModelRegistry.register  
class Product(Base, TimestampMixin, SoftDeleteMixin):
    """商品模型 - 管理商品信息、库存和状态
    
    根据overview.md文档规范实现，包含：
    - Integer主键（遵循database-standards.md标准）
    - SKU唯一性约束
    - 品牌关联、分类关联
    - SEO字段支持
    - 统计字段（浏览量、销量等）
    - 软删除支持（SoftDeleteMixin）
    - 时间戳自动维护（TimestampMixin）
    """
    __tablename__ = 'products'
    
    # 主键 - 严格遵循docs/standards/database-standards.md规定
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 商品基础信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 关联信息
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # 商品状态 - 枚举值: draft, published, archived
    status = Column(String(20), nullable=False, default='draft')
    
    # 发布时间
    published_at = Column(DateTime, nullable=True)
    
    # SEO字段
    seo_title = Column(String(200), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(String(500), nullable=True)
    
    # 排序和统计
    sort_order = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    sale_count = Column(Integer, default=0, nullable=False)
    
    # 软删除字段由SoftDeleteMixin提供：
    # - is_deleted: Boolean, default=False, nullable=False  
    # - deleted_at: DateTime, nullable=True
    
    # 时间戳字段由TimestampMixin提供：
    # - created_at: DateTime, server_default=func.now(), nullable=False
    # - updated_at: DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    
    # 关系定义
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    skus = relationship("SKU", back_populates="product", cascade="all, delete-orphan")
    attributes_rel = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    images_rel = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    tags_rel = relationship("ProductTag", back_populates="product", cascade="all, delete-orphan")
    
    # 索引优化 - 根据文档规范使用 idx_{表名}_{字段名} 格式
    __table_args__ = (
        Index('idx_products_brand_category', 'brand_id', 'category_id'),     # 品牌分类复合索引
        Index('idx_products_status_published', 'status', 'published_at'),    # 状态发布时间复合索引
        Index('idx_products_view_count', 'view_count'),                      # 浏览量索引
        Index('idx_products_sale_count', 'sale_count'),                      # 销量索引
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', status='{self.status}')>"


@ModelRegistry.register
class SKU(Base, TimestampMixin):
    """SKU模型 - 管理商品规格信息
    
    根据overview.md文档规范实现，包含：
    - Integer主键（遵循database-standards.md标准）
    - 产品关联外键
    - SKU代码唯一性约束
    - 价格和成本管理
    - 重量体积等物理属性
    """
    __tablename__ = 'skus'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 商品关联
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    
    # SKU信息
    sku_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=True)
    
    # 价格信息
    price = Column(DECIMAL(10, 2), nullable=False)
    cost_price = Column(DECIMAL(10, 2), nullable=True)
    market_price = Column(DECIMAL(10, 2), nullable=True)
    
    # 物理属性
    weight = Column(DECIMAL(8, 3), nullable=True)  # 重量（千克）
    volume = Column(DECIMAL(8, 3), nullable=True)  # 体积（立方米）
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系定义
    product = relationship("Product", back_populates="skus")
    attributes_rel = relationship("SKUAttribute", back_populates="sku", cascade="all, delete-orphan")
    images_rel = relationship("ProductImage", back_populates="sku")
    
    # 索引
    __table_args__ = (
        Index('idx_skus_product_active', 'product_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<SKU(id={self.id}, sku_code='{self.sku_code}', product_id={self.product_id})>"


@ModelRegistry.register
class ProductAttribute(Base, TimestampMixin):
    """商品属性模型 - 管理商品的扩展属性
    
    支持多种属性类型：text, number, boolean, select
    可标记为可搜索属性以支持分面搜索
    """
    __tablename__ = 'product_attributes'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 商品关联
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    
    # 属性信息
    attribute_name = Column(String(100), nullable=False)
    attribute_value = Column(String(500), nullable=False)
    attribute_type = Column(String(20), nullable=False)  # text, number, boolean, select
    is_searchable = Column(Boolean, default=False, nullable=False)
    
    # 关系定义
    product = relationship("Product", back_populates="attributes_rel")
    
    def __repr__(self):
        return f"<ProductAttribute(id={self.id}, name='{self.attribute_name}', value='{self.attribute_value}')>"


@ModelRegistry.register
class SKUAttribute(Base, TimestampMixin):
    """SKU属性模型 - 管理SKU的规格属性（如颜色、尺寸等）
    
    用于区分同一商品的不同规格
    """
    __tablename__ = 'sku_attributes'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # SKU关联
    sku_id = Column(Integer, ForeignKey('skus.id', ondelete='CASCADE'), nullable=False)
    
    # 属性信息
    attribute_name = Column(String(100), nullable=False)
    attribute_value = Column(String(200), nullable=False)
    
    # 关系定义
    sku = relationship("SKU", back_populates="attributes_rel")
    
    # 唯一约束
    __table_args__ = (
        Index('uk_sku_attributes_sku_name', 'sku_id', 'attribute_name', unique=True),
    )
    
    def __repr__(self):
        return f"<SKUAttribute(id={self.id}, sku_id={self.sku_id}, name='{self.attribute_name}', value='{self.attribute_value}')>"


@ModelRegistry.register
class ProductImage(Base, TimestampMixin):
    """商品图片模型 - 管理商品和SKU的图片资源
    
    支持商品级别和SKU级别的图片管理
    可设置主图和排序
    """
    __tablename__ = 'product_images'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 关联（商品或SKU）
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=True)
    sku_id = Column(Integer, ForeignKey('skus.id', ondelete='CASCADE'), nullable=True)
    
    # 图片信息
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # 关系定义
    product = relationship("Product", back_populates="images_rel")
    sku = relationship("SKU", back_populates="images_rel")
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, sku_id={self.sku_id}, is_primary={self.is_primary})>"


@ModelRegistry.register
class ProductTag(Base, TimestampMixin):
    """商品标签模型 - 管理商品的标签分类
    
    支持多种标签类型：general, promotion, feature
    用于商品的灵活分类和搜索
    """
    __tablename__ = 'product_tags'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    # 商品关联
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    
    # 标签信息
    tag_name = Column(String(50), nullable=False)
    tag_type = Column(String(20), default='general', nullable=False)  # general, promotion, feature
    
    # 关系定义
    product = relationship("Product", back_populates="tags_rel")
    
    # 唯一约束
    __table_args__ = (
        Index('uk_product_tags_product_name', 'product_id', 'tag_name', unique=True),
    )
    
    def __repr__(self):
        return f"<ProductTag(id={self.id}, product_id={self.product_id}, tag_name='{self.tag_name}', tag_type='{self.tag_type}')>"


# 导出模型
__all__ = [
    'Category', 'Product', 'Brand', 'SKU', 
    'ProductAttribute', 'SKUAttribute', 'ProductImage', 'ProductTag'
]