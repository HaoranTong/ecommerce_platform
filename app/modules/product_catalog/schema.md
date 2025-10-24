# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `ApiResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `success` | `bool` | ❌ | `True` |  |
| `message` | `str` | ❌ | `操作成功` |  |
| `data` | `Optional[Any]` | ❌ | `` |  |

---

## `BrandBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `str` | ❌ | `` | 品牌名称 |
| `slug` | `str` | ❌ | `` | SEO友好的URL标识 |
| `description` | `Optional[str]` | ❌ | `` | 品牌描述 |
| `logo_url` | `Optional[str]` | ❌ | `` | 品牌Logo URL |
| `website_url` | `Optional[str]` | ❌ | `` | 品牌官网URL |
| `is_active` | `bool` | ❌ | `` | 是否活跃 |

---

## `BrandCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `str` | ❌ | `` | 品牌名称 |
| `slug` | `str` | ❌ | `` | SEO友好的URL标识 |
| `description` | `Optional[str]` | ❌ | `` | 品牌描述 |
| `logo_url` | `Optional[str]` | ❌ | `` | 品牌Logo URL |
| `website_url` | `Optional[str]` | ❌ | `` | 品牌官网URL |
| `is_active` | `bool` | ❌ | `` | 是否活跃 |

---

## `BrandRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `str` | ❌ | `` | 品牌名称 |
| `slug` | `str` | ❌ | `` | SEO友好的URL标识 |
| `description` | `Optional[str]` | ❌ | `` | 品牌描述 |
| `logo_url` | `Optional[str]` | ❌ | `` | 品牌Logo URL |
| `website_url` | `Optional[str]` | ❌ | `` | 品牌官网URL |
| `is_active` | `bool` | ❌ | `` | 是否活跃 |
| `id` | `int` | ✅ | `` |  |

---

## `BrandUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `Optional[str]` | ❌ | `` |  |
| `slug` | `Optional[str]` | ❌ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `logo_url` | `Optional[str]` | ❌ | `` |  |
| `website_url` | `Optional[str]` | ❌ | `` |  |
| `is_active` | `Optional[bool]` | ❌ | `` |  |

---

## `CategoryCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `str` | ❌ | `` | 分类名称 |
| `parent_id` | `Optional[int]` | ❌ | `` | 父分类ID |
| `sort_order` | `int` | ❌ | `` | 排序顺序 |
| `is_active` | `Optional[bool]` | ❌ | `` | 是否激活 |
| `description` | `Optional[str]` | ❌ | `` | 分类描述 |
| `meta_data` | `Optional[Dict[str, Any]]` | ❌ | `` | 元数据 |

---

## `CategoryRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `parent_id` | `Optional[int]` | ❌ | `` |  |
| `sort_order` | `int` | ✅ | `` |  |
| `is_active` | `bool` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `product_count` | `Optional[int]` | ❌ | `0` |  |
| `meta_data` | `Optional[Dict[str, Any]]` | ❌ | `` |  |

---

## `CategoryStats`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_categories` | `int` | ✅ | `` |  |
| `active_categories` | `int` | ✅ | `` |  |
| `top_level_categories` | `int` | ✅ | `` |  |
| `categories_with_products` | `int` | ✅ | `` |  |

---

## `CategoryTreeRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `parent_id` | `Optional[int]` | ❌ | `` |  |
| `sort_order` | `int` | ✅ | `` |  |
| `is_active` | `bool` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `product_count` | `Optional[int]` | ❌ | `0` |  |
| `meta_data` | `Optional[Dict[str, Any]]` | ❌ | `` |  |
| `children` | `List['CategoryTreeRead']` | ❌ | `` |  |

---

## `CategoryUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `Optional[str]` | ❌ | `` | 分类名称 |
| `parent_id` | `Optional[int]` | ❌ | `` | 父分类ID |
| `sort_order` | `Optional[int]` | ❌ | `` | 排序顺序 |
| `is_active` | `Optional[bool]` | ❌ | `` | 是否激活 |
| `description` | `Optional[str]` | ❌ | `` | 分类描述 |

---

## `PaginatedResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `success` | `bool` | ❌ | `True` |  |
| `message` | `str` | ❌ | `查询成功` |  |
| `data` | `Dict[str, Any]` | ✅ | `` |  |
| `total` | `int` | ✅ | `` |  |
| `page` | `int` | ❌ | `1` |  |
| `limit` | `int` | ❌ | `20` |  |
| `total_pages` | `int` | ✅ | `` |  |

---

## `ProductAttributeBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_name` | `str` | ❌ | `` |  |
| `attribute_value` | `str` | ❌ | `` |  |
| `attribute_type` | `str` | ❌ | `` |  |
| `is_searchable` | `bool` | ❌ | `` | 是否可搜索 |

---

## `ProductAttributeCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_name` | `str` | ❌ | `` |  |
| `attribute_value` | `str` | ❌ | `` |  |
| `attribute_type` | `str` | ❌ | `` |  |
| `is_searchable` | `bool` | ❌ | `` | 是否可搜索 |

---

## `ProductAttributeRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_name` | `str` | ❌ | `` |  |
| `attribute_value` | `str` | ❌ | `` |  |
| `attribute_type` | `str` | ❌ | `` |  |
| `is_searchable` | `bool` | ❌ | `` | 是否可搜索 |
| `id` | `int` | ✅ | `` |  |
| `product_id` | `int` | ✅ | `` |  |

---

## `ProductAttributeUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_value` | `Optional[str]` | ❌ | `` |  |
| `is_searchable` | `Optional[bool]` | ❌ | `` |  |

---

## `ProductBatch`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `product_ids` | `List[int]` | ❌ | `` | 商品ID列表 |
| `action` | `str` | ❌ | `` | 操作类型 |
| `params` | `Optional[Dict[str, Any]]` | ❌ | `` | 操作参数 |

---

## `ProductComplete`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `brand_id` | `Optional[int]` | ❌ | `` |  |
| `category_id` | `Optional[int]` | ❌ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `published_at` | `Optional[datetime]` | ❌ | `` |  |
| `seo_title` | `Optional[str]` | ❌ | `` |  |
| `seo_description` | `Optional[str]` | ❌ | `` |  |
| `seo_keywords` | `Optional[str]` | ❌ | `` |  |
| `sort_order` | `int` | ✅ | `` |  |
| `view_count` | `int` | ✅ | `` |  |
| `sale_count` | `int` | ✅ | `` |  |
| `brand` | `Optional[BrandRead]` | ❌ | `` |  |
| `category` | `Optional[CategoryRead]` | ❌ | `` |  |
| `skus` | `Optional[List[SKURead]]` | ❌ | `` |  |
| `attributes_rel` | `Optional[List[ProductAttributeRead]]` | ❌ | `` |  |
| `images_rel` | `Optional[List[ProductImageRead]]` | ❌ | `` |  |
| `tags_rel` | `Optional[List[ProductTagRead]]` | ❌ | `` |  |

---

## `ProductCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `str` | ❌ | `` | 商品名称 |
| `description` | `Optional[str]` | ❌ | `` | 商品描述 |
| `brand_id` | `Optional[int]` | ❌ | `` | 品牌ID |
| `category_id` | `Optional[int]` | ❌ | `` | 分类ID |
| `status` | `Literal['draft', 'published', 'archived']` | ❌ | `` | 商品状态（draft, published, archived） |
| `seo_title` | `Optional[str]` | ❌ | `` | SEO标题 |
| `seo_description` | `Optional[str]` | ❌ | `` | SEO描述 |
| `seo_keywords` | `Optional[str]` | ❌ | `` | SEO关键词 |
| `sort_order` | `int` | ❌ | `` | 排序序号 |

---

## `ProductDetail`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `brand_id` | `Optional[int]` | ❌ | `` |  |
| `category_id` | `Optional[int]` | ❌ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `published_at` | `Optional[datetime]` | ❌ | `` |  |
| `seo_title` | `Optional[str]` | ❌ | `` |  |
| `seo_description` | `Optional[str]` | ❌ | `` |  |
| `seo_keywords` | `Optional[str]` | ❌ | `` |  |
| `sort_order` | `int` | ✅ | `` |  |
| `view_count` | `int` | ✅ | `` |  |
| `sale_count` | `int` | ✅ | `` |  |
| `brand` | `Optional[BrandRead]` | ❌ | `` |  |
| `category` | `Optional[CategoryRead]` | ❌ | `` |  |

---

## `ProductImageBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `image_url` | `str` | ❌ | `` | 图片URL |
| `alt_text` | `Optional[str]` | ❌ | `` | 图片描述 |
| `sort_order` | `int` | ❌ | `` | 排序序号 |
| `is_primary` | `bool` | ❌ | `` | 是否主图 |

---

## `ProductImageCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `image_url` | `str` | ❌ | `` | 图片URL |
| `alt_text` | `Optional[str]` | ❌ | `` | 图片描述 |
| `sort_order` | `int` | ❌ | `` | 排序序号 |
| `is_primary` | `bool` | ❌ | `` | 是否主图 |
| `product_id` | `Optional[int]` | ❌ | `` | 商品ID |
| `sku_id` | `Optional[int]` | ❌ | `` | SKU ID |

---

## `ProductImageRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `image_url` | `str` | ❌ | `` | 图片URL |
| `alt_text` | `Optional[str]` | ❌ | `` | 图片描述 |
| `sort_order` | `int` | ❌ | `` | 排序序号 |
| `is_primary` | `bool` | ❌ | `` | 是否主图 |
| `id` | `int` | ✅ | `` |  |
| `product_id` | `Optional[int]` | ❌ | `` |  |
| `sku_id` | `Optional[int]` | ❌ | `` |  |

---

## `ProductImageUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `alt_text` | `Optional[str]` | ❌ | `` |  |
| `sort_order` | `Optional[int]` | ❌ | `` |  |
| `is_primary` | `Optional[bool]` | ❌ | `` |  |

---

## `ProductImport`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `str` | ✅ | `` |  |
| `sku` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `category_name` | `Optional[str]` | ❌ | `` |  |
| `price` | `Decimal` | ✅ | `` |  |
| `stock_quantity` | `int` | ✅ | `` |  |
| `image_url` | `Optional[str]` | ❌ | `` |  |

---

## `ProductPublic`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `price` | `Decimal` | ✅ | `` |  |
| `image_url` | `Optional[str]` | ❌ | `` |  |
| `category_name` | `Optional[str]` | ❌ | `` |  |
| `is_available` | `bool` | ❌ | `True` |  |
| `rating` | `Optional[float]` | ❌ | `` |  |
| `review_count` | `int` | ❌ | `0` |  |

---

## `ProductPublish`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `status` | `Literal['draft', 'published', 'archived']` | ❌ | `` | 发布状态（draft, published, archived） |

---

## `ProductRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `name` | `str` | ✅ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `brand_id` | `Optional[int]` | ❌ | `` |  |
| `category_id` | `Optional[int]` | ❌ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `published_at` | `Optional[datetime]` | ❌ | `` |  |
| `seo_title` | `Optional[str]` | ❌ | `` |  |
| `seo_description` | `Optional[str]` | ❌ | `` |  |
| `seo_keywords` | `Optional[str]` | ❌ | `` |  |
| `sort_order` | `int` | ✅ | `` |  |
| `view_count` | `int` | ✅ | `` |  |
| `sale_count` | `int` | ✅ | `` |  |

---

## `ProductSearch`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `keyword` | `Optional[str]` | ❌ | `` | 搜索关键词 |
| `brand_id` | `Optional[int]` | ❌ | `` | 品牌筛选 |
| `category_id` | `Optional[int]` | ❌ | `` | 分类筛选 |
| `status` | `Optional[str]` | ❌ | `` | 状态筛选 |
| `sort_by` | `Optional[Literal['created_at', 'name', 'price', 'view_count']]` | ❌ | `` | 排序字段 |
| `sort_order` | `Optional[Literal['asc', 'desc']]` | ❌ | `` | 排序方向（asc 或 desc） |

---

## `ProductStats`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_products` | `int` | ✅ | `` |  |
| `draft_products` | `int` | ✅ | `` |  |
| `published_products` | `int` | ✅ | `` |  |
| `archived_products` | `int` | ✅ | `` |  |
| `total_views` | `int` | ✅ | `` |  |
| `total_sales` | `int` | ✅ | `` |  |
| `brands_count` | `int` | ✅ | `` |  |
| `categories_count` | `int` | ✅ | `` |  |

---

## `ProductTagBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `tag_name` | `str` | ❌ | `` | 标签名称 |
| `tag_type` | `str` | ❌ | `` | 标签类型 |

---

## `ProductTagCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `tag_name` | `str` | ❌ | `` | 标签名称 |
| `tag_type` | `str` | ❌ | `` | 标签类型 |

---

## `ProductTagRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `tag_name` | `str` | ❌ | `` | 标签名称 |
| `tag_type` | `str` | ❌ | `` | 标签类型 |
| `id` | `int` | ✅ | `` |  |
| `product_id` | `int` | ✅ | `` |  |

---

## `ProductUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `Optional[str]` | ❌ | `` | 商品名称 |
| `description` | `Optional[str]` | ❌ | `` | 商品描述 |
| `brand_id` | `Optional[int]` | ❌ | `` | 品牌ID |
| `category_id` | `Optional[int]` | ❌ | `` | 分类ID |
| `status` | `Optional[Literal['draft', 'published', 'archived']]` | ❌ | `` | 商品状态（draft, published, archived） |
| `seo_title` | `Optional[str]` | ❌ | `` | SEO标题 |
| `seo_description` | `Optional[str]` | ❌ | `` | SEO描述 |
| `seo_keywords` | `Optional[str]` | ❌ | `` | SEO关键词 |
| `sort_order` | `Optional[int]` | ❌ | `` | 排序序号 |

---

## `SKUAttributeBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_name` | `str` | ❌ | `` |  |
| `attribute_value` | `str` | ❌ | `` |  |

---

## `SKUAttributeCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_name` | `str` | ❌ | `` |  |
| `attribute_value` | `str` | ❌ | `` |  |

---

## `SKUAttributeRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `attribute_name` | `str` | ❌ | `` |  |
| `attribute_value` | `str` | ❌ | `` |  |
| `id` | `int` | ✅ | `` |  |
| `sku_id` | `int` | ✅ | `` |  |

---

## `SKUBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_code` | `str` | ❌ | `` | SKU编码 |
| `name` | `Optional[str]` | ❌ | `` | SKU名称 |
| `price` | `Decimal` | ❌ | `` | 价格 |
| `cost_price` | `Optional[Decimal]` | ❌ | `` | 成本价 |
| `market_price` | `Optional[Decimal]` | ❌ | `` | 市场价 |
| `weight` | `Optional[Decimal]` | ❌ | `` | 重量（千克） |
| `volume` | `Optional[Decimal]` | ❌ | `` | 体积（立方米） |
| `is_active` | `bool` | ❌ | `` | 是否活跃 |

---

## `SKUCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_code` | `str` | ❌ | `` | SKU编码 |
| `name` | `Optional[str]` | ❌ | `` | SKU名称 |
| `price` | `Decimal` | ❌ | `` | 价格 |
| `cost_price` | `Optional[Decimal]` | ❌ | `` | 成本价 |
| `market_price` | `Optional[Decimal]` | ❌ | `` | 市场价 |
| `weight` | `Optional[Decimal]` | ❌ | `` | 重量（千克） |
| `volume` | `Optional[Decimal]` | ❌ | `` | 体积（立方米） |
| `is_active` | `bool` | ❌ | `` | 是否活跃 |
| `product_id` | `int` | ❌ | `` | 所属商品ID |
| `attributes` | `Optional[List[SKUAttributeCreate]]` | ❌ | `` | SKU属性列表 |

---

## `SKURead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_code` | `str` | ❌ | `` | SKU编码 |
| `name` | `Optional[str]` | ❌ | `` | SKU名称 |
| `price` | `Decimal` | ❌ | `` | 价格 |
| `cost_price` | `Optional[Decimal]` | ❌ | `` | 成本价 |
| `market_price` | `Optional[Decimal]` | ❌ | `` | 市场价 |
| `weight` | `Optional[Decimal]` | ❌ | `` | 重量（千克） |
| `volume` | `Optional[Decimal]` | ❌ | `` | 体积（立方米） |
| `is_active` | `bool` | ❌ | `` | 是否活跃 |
| `id` | `int` | ✅ | `` |  |
| `product_id` | `int` | ✅ | `` |  |
| `attributes_rel` | `Optional[List[SKUAttributeRead]]` | ❌ | `` |  |

---

## `SKUUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `name` | `Optional[str]` | ❌ | `` |  |
| `price` | `Optional[Decimal]` | ❌ | `` |  |
| `cost_price` | `Optional[Decimal]` | ❌ | `` |  |
| `market_price` | `Optional[Decimal]` | ❌ | `` |  |
| `weight` | `Optional[Decimal]` | ❌ | `` |  |
| `volume` | `Optional[Decimal]` | ❌ | `` |  |
| `is_active` | `Optional[bool]` | ❌ | `` |  |

---

