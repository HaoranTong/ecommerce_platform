"""
商品目录模块Pydantic模式定义

根据docs/modules/product-catalog/overview.md文档规范实现
严格符合API设计标准和数据验证要求

主要功能：
- 商品分类的创建、更新、展示模式
- 商品信息的创建、更新、展示模式  
- 品牌管理的相关模式
- SKU规格管理的相关模式
- 商品属性、图片、标签管理模式
- 统一API响应格式
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# 模块内独立定义基础schemas，遵循模块化单体架构原则
class BaseSchema(BaseModel):
    """商品管理模块基础模式类"""
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

class TimestampSchema(BaseSchema):
    """包含时间戳的基础模式"""
    created_at: datetime
    updated_at: datetime


# ============ 统一API响应格式 ============

class ApiResponse(BaseSchema):
    """统一API响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    
class PaginatedResponse(BaseSchema):
    """分页响应格式"""
    success: bool = True
    message: str = "查询成功"
    data: Dict[str, Any]
    total: int
    page: int = 1
    limit: int = 20
    total_pages: int


# ============ 品牌管理模式 ============

class BrandBase(BaseSchema):
    """品牌基础模式"""
    name: str = Field(..., min_length=1, max_length=100, description="品牌名称")
    slug: str = Field(..., min_length=1, max_length=100, description="SEO友好的URL标识")
    description: Optional[str] = Field(None, description="品牌描述")
    logo_url: Optional[str] = Field(None, max_length=500, description="品牌Logo URL")
    website_url: Optional[str] = Field(None, max_length=500, description="品牌官网URL")
    is_active: bool = Field(True, description="是否活跃")

class BrandCreate(BrandBase):
    """创建品牌模式"""
    pass

class BrandUpdate(BaseSchema):
    """更新品牌模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class BrandRead(BrandBase, TimestampSchema):
    """品牌展示模式"""
    id: int


# ============ 分类相关模式 ============

class CategoryCreate(BaseSchema):
    """分类创建模式"""
    name: str = Field(..., max_length=100, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(default=0, ge=0, description="排序顺序")
    is_active: Optional[bool] = Field(True, description="是否激活")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")


class CategoryUpdate(BaseSchema):
    """分类更新模式"""
    name: Optional[str] = Field(None, max_length=100, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: Optional[int] = Field(None, ge=0, description="排序顺序")
    is_active: Optional[bool] = Field(None, description="是否激活")
    description: Optional[str] = Field(None, max_length=500, description="分类描述")


class CategoryRead(TimestampSchema):
    """分类展示模式"""
    id: int
    name: str
    parent_id: Optional[int] = None
    sort_order: int
    is_active: bool
    description: Optional[str] = None
    product_count: Optional[int] = 0  # 商品数量


class CategoryTreeRead(CategoryRead):
    """分类树形展示模式"""
    children: List['CategoryTreeRead'] = []
    
    # 处理循环引用
    model_config = {"from_attributes": True}


class CategoryStats(BaseSchema):
    """分类统计模式"""
    total_categories: int
    active_categories: int
    top_level_categories: int
    categories_with_products: int


# ============ 商品相关模式 ============

class ProductCreate(BaseSchema):
    """商品创建模式"""
    name: str = Field(..., max_length=200, description="商品名称")
    description: Optional[str] = Field(None, description="商品描述")
    brand_id: Optional[int] = Field(None, description="品牌ID")
    category_id: Optional[int] = Field(None, description="分类ID")
    status: str = Field("draft", pattern="^(draft|published|archived)$", description="商品状态")
    seo_title: Optional[str] = Field(None, max_length=200, description="SEO标题")
    seo_description: Optional[str] = Field(None, description="SEO描述")
    seo_keywords: Optional[str] = Field(None, max_length=500, description="SEO关键词")
    sort_order: int = Field(0, description="排序序号")


class ProductUpdate(BaseSchema):
    """商品更新模式"""
    name: Optional[str] = Field(None, max_length=200, description="商品名称")
    description: Optional[str] = Field(None, description="商品描述")
    brand_id: Optional[int] = Field(None, description="品牌ID")
    category_id: Optional[int] = Field(None, description="分类ID")
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$", description="商品状态")
    seo_title: Optional[str] = Field(None, max_length=200, description="SEO标题")
    seo_description: Optional[str] = Field(None, description="SEO描述")
    seo_keywords: Optional[str] = Field(None, max_length=500, description="SEO关键词")
    sort_order: Optional[int] = Field(None, description="排序序号")


class ProductPublish(BaseSchema):
    """商品发布模式"""
    status: str = Field("published", pattern="^(draft|published|archived)$", description="发布状态")


class ProductRead(TimestampSchema):
    """商品展示模式"""
    id: int
    name: str
    description: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    status: str
    published_at: Optional[datetime] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    sort_order: int
    view_count: int
    sale_count: int


class ProductDetail(ProductRead):
    """商品详情模式（包含更多信息）"""
    brand: Optional[BrandRead] = None
    category: Optional[CategoryRead] = None


class ProductSearch(BaseSchema):
    """商品搜索模式"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    brand_id: Optional[int] = Field(None, description="品牌筛选")
    category_id: Optional[int] = Field(None, description="分类筛选")
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$", description="状态筛选")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="排序方向")


class ProductStats(BaseSchema):
    """商品统计模式"""
    total_products: int
    draft_products: int
    published_products: int
    archived_products: int
    total_views: int
    total_sales: int
    brands_count: int
    categories_count: int


# ============ SKU管理模式 ============

class SKUAttributeBase(BaseSchema):
    """SKU属性基础模式"""
    attribute_name: str = Field(..., min_length=1, max_length=100)
    attribute_value: str = Field(..., min_length=1, max_length=200)

class SKUAttributeCreate(SKUAttributeBase):
    """创建SKU属性模式"""
    pass

class SKUAttributeRead(SKUAttributeBase, TimestampSchema):
    """SKU属性展示模式"""
    id: int
    sku_id: int

class SKUBase(BaseSchema):
    """SKU基础模式"""
    sku_code: str = Field(..., min_length=1, max_length=100, description="SKU编码")
    name: Optional[str] = Field(None, max_length=200, description="SKU名称")
    price: Decimal = Field(..., ge=0, description="SKU价格")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本价格")
    market_price: Optional[Decimal] = Field(None, ge=0, description="市场价格")
    weight: Optional[Decimal] = Field(None, ge=0, description="重量（千克）")
    volume: Optional[Decimal] = Field(None, ge=0, description="体积（立方米）")
    is_active: bool = Field(True, description="是否活跃")

class SKUCreate(SKUBase):
    """创建SKU模式"""
    product_id: int = Field(..., description="所属商品ID")
    attributes: Optional[List[SKUAttributeCreate]] = Field(None, description="SKU属性列表")

class SKUUpdate(BaseSchema):
    """更新SKU模式"""
    name: Optional[str] = Field(None, max_length=200)
    price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    market_price: Optional[Decimal] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0)
    volume: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None

class SKURead(SKUBase, TimestampSchema):
    """SKU展示模式"""
    id: int
    product_id: int
    attributes_rel: Optional[List[SKUAttributeRead]] = None


# ============ 商品属性管理模式 ============

class ProductAttributeBase(BaseSchema):
    """商品属性基础模式"""
    attribute_name: str = Field(..., min_length=1, max_length=100)
    attribute_value: str = Field(..., min_length=1, max_length=500)
    attribute_type: str = Field(..., pattern="^(text|number|boolean|select)$")
    is_searchable: bool = Field(False, description="是否可搜索")

class ProductAttributeCreate(ProductAttributeBase):
    """创建商品属性模式"""
    pass

class ProductAttributeUpdate(BaseSchema):
    """更新商品属性模式"""
    attribute_value: Optional[str] = Field(None, min_length=1, max_length=500)
    is_searchable: Optional[bool] = None

class ProductAttributeRead(ProductAttributeBase, TimestampSchema):
    """商品属性展示模式"""
    id: int
    product_id: int


# ============ 商品图片管理模式 ============

class ProductImageBase(BaseSchema):
    """商品图片基础模式"""
    image_url: str = Field(..., max_length=500, description="图片URL")
    alt_text: Optional[str] = Field(None, max_length=200, description="图片描述")
    sort_order: int = Field(0, description="排序序号")
    is_primary: bool = Field(False, description="是否主图")

class ProductImageCreate(ProductImageBase):
    """创建商品图片模式"""
    product_id: Optional[int] = Field(None, description="商品ID")
    sku_id: Optional[int] = Field(None, description="SKU ID")

class ProductImageUpdate(BaseSchema):
    """更新商品图片模式"""
    alt_text: Optional[str] = Field(None, max_length=200)
    sort_order: Optional[int] = None
    is_primary: Optional[bool] = None

class ProductImageRead(ProductImageBase, TimestampSchema):
    """商品图片展示模式"""
    id: int
    product_id: Optional[int]
    sku_id: Optional[int]


# ============ 商品标签管理模式 ============

class ProductTagBase(BaseSchema):
    """商品标签基础模式"""
    tag_name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    tag_type: str = Field("general", pattern="^(general|promotion|feature)$", description="标签类型")

class ProductTagCreate(ProductTagBase):
    """创建商品标签模式"""
    pass

class ProductTagRead(ProductTagBase, TimestampSchema):
    """商品标签展示模式"""
    id: int
    product_id: int


# ============ 扩展的商品模式（包含完整信息）============

class ProductComplete(ProductRead):
    """完整商品信息模式"""
    brand: Optional[BrandRead] = None
    category: Optional[CategoryRead] = None
    skus: Optional[List[SKURead]] = None
    attributes_rel: Optional[List[ProductAttributeRead]] = None
    images_rel: Optional[List[ProductImageRead]] = None
    tags_rel: Optional[List[ProductTagRead]] = None


class ProductPublic(BaseSchema):
    """商品公开信息模式（对外展示）"""
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    category_name: Optional[str] = None
    is_available: bool = True
    rating: Optional[float] = None
    review_count: int = 0


class ProductBatch(BaseSchema):
    """商品批量操作模式"""
    product_ids: List[int] = Field(..., min_length=1, description="商品ID列表")
    action: str = Field(..., pattern="^(activate|deactivate|delete|update_category)$", description="操作类型")
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")


class ProductImport(BaseSchema):
    """商品导入模式"""
    name: str
    sku: str
    description: Optional[str] = None
    category_name: Optional[str] = None
    price: Decimal
    stock_quantity: int
    image_url: Optional[str] = None