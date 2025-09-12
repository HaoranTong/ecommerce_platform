"""
文件名：product.py
文件路径：app/schemas/product.py
功能描述：商品和分类管理相关的Pydantic模式定义
主要功能：
- 商品分类的创建、更新、展示模式
- 商品信息的创建、更新、展示模式
- 商品库存管理和搜索筛选模式
使用说明：
- 导入：from app.schemas.product import ProductCreate, ProductRead, CategoryCreate
- 验证：product_data = ProductCreate(**input_data)
- 序列化：product_response = ProductRead.model_validate(product_obj)
依赖模块：
- app.schemas.base: 基础模式类
- pydantic: 数据验证和字段定义
- decimal: 金额字段类型
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.schemas.base import BaseSchema, TimestampSchema


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
    sku: str = Field(..., max_length=100, description="商品编号")
    description: Optional[str] = Field(None, description="商品描述")
    category_id: Optional[int] = Field(None, description="分类ID")
    price: Decimal = Field(..., ge=0, description="商品价格")
    stock_quantity: int = Field(..., ge=0, description="库存数量")
    status: str = Field(default="active", pattern="^(active|inactive|out_of_stock)$", description="商品状态")
    image_url: Optional[str] = Field(None, max_length=500, description="主图URL")
    attributes: Optional[Dict[str, Any]] = Field(None, description="商品属性")
    images: Optional[List[str]] = Field(None, description="商品图片列表")
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        if not v.isalnum():
            raise ValueError('SKU只能包含字母和数字')
        return v.upper()


class ProductUpdate(BaseSchema):
    """商品更新模式"""
    name: Optional[str] = Field(None, max_length=200, description="商品名称")
    sku: Optional[str] = Field(None, max_length=100, description="商品编号")
    description: Optional[str] = Field(None, description="商品描述")
    category_id: Optional[int] = Field(None, description="分类ID")
    price: Optional[Decimal] = Field(None, ge=0, description="商品价格")
    stock_quantity: Optional[int] = Field(None, ge=0, description="库存数量")
    status: Optional[str] = Field(None, pattern="^(active|inactive|out_of_stock)$", description="商品状态")
    image_url: Optional[str] = Field(None, max_length=500, description="主图URL")
    attributes: Optional[Dict[str, Any]] = Field(None, description="商品属性")
    images: Optional[List[str]] = Field(None, description="商品图片列表")


class ProductStockUpdate(BaseSchema):
    """商品库存更新模式"""
    quantity_change: int = Field(..., description="库存变更量，正数为增加，负数为减少")
    reason: Optional[str] = Field(None, max_length=200, description="变更原因")
    operator_id: Optional[int] = Field(None, description="操作员ID")


class ProductRead(TimestampSchema):
    """商品展示模式"""
    id: int
    name: str
    sku: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None  # 关联分类名称
    price: Decimal
    stock_quantity: int
    status: str
    image_url: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None


class ProductDetail(ProductRead):
    """商品详情模式（包含更多信息）"""
    category: Optional[CategoryRead] = None
    is_available: bool = True  # 是否可购买
    stock_status: str = "in_stock"  # 库存状态


class ProductSearch(BaseSchema):
    """商品搜索模式"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    category_id: Optional[int] = Field(None, description="分类筛选")
    min_price: Optional[Decimal] = Field(None, ge=0, description="最低价格")
    max_price: Optional[Decimal] = Field(None, ge=0, description="最高价格")
    status: Optional[str] = Field(None, pattern="^(active|inactive|out_of_stock)$", description="状态筛选")
    in_stock_only: Optional[bool] = Field(False, description="仅显示有库存商品")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="排序方向")


class ProductStats(BaseSchema):
    """商品统计模式"""
    total_products: int
    active_products: int
    out_of_stock_products: int
    low_stock_products: int
    total_value: Decimal
    categories_count: int


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
    product_ids: List[int] = Field(..., min_items=1, description="商品ID列表")
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