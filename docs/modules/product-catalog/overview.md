# 商品管理模块 (Product Catalog Module)

## 模块概述

商品管理模块是电商平台的核心业务模块，负责商品信息管理、分类体系、库存同步、搜索索引和内容管理。支持多规格商品、动态定价、个性化展示。

### 主要功能

1. **商品信息管理**
   - 商品基本信息 (名称、描述、图片、视频)
   - 商品规格管理 (SKU、颜色、尺寸、材质)
   - 商品分类体系 (多级分类、标签体系)
   - 商品状态管理 (上架、下架、预售、停产)

2. **价格管理**
   - 基础定价策略
   - 动态价格调整
   - 促销价格管理
   - 会员价格体系

3. **内容管理**
   - 商品详情页内容
   - 富文本编辑器
   - 多媒体资源管理
   - SEO优化支持

4. **搜索与发现**
   - 全文搜索
   - 分面搜索 (筛选器)
   - 智能推荐
   - 相关商品推荐

## 技术架构

### 核心组件

```
product-catalog/
├── controllers/
│   ├── product_controller.py     # 商品控制器
│   ├── category_controller.py    # 分类控制器
│   ├── sku_controller.py         # SKU控制器
│   └── search_controller.py      # 搜索控制器
├── services/
│   ├── product_service.py        # 商品业务逻辑
│   ├── category_service.py       # 分类服务
│   ├── pricing_service.py        # 定价服务
│   ├── inventory_sync_service.py # 库存同步服务
│   └── search_service.py         # 搜索服务
├── models/
│   ├── product.py               # 商品模型
│   ├── category.py              # 分类模型
│   ├── sku.py                   # SKU模型
│   ├── brand.py                 # 品牌模型
│   └── attribute.py             # 属性模型
├── events/
│   ├── product_events.py        # 商品事件
│   └── inventory_events.py      # 库存事件
└── utils/
    ├── seo_utils.py             # SEO工具
    ├── image_utils.py           # 图片处理工具
    └── search_utils.py          # 搜索工具
```

### 数据库设计

```sql
-- 商品表
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    brand_id UUID REFERENCES brands(id),
    category_id UUID REFERENCES categories(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    seo_title VARCHAR(200),
    seo_description TEXT,
    seo_keywords VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    sale_count INTEGER DEFAULT 0
);

-- 分类表
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    level INTEGER NOT NULL DEFAULT 1,
    path VARCHAR(500) NOT NULL, -- 层级路径 /1/2/3
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SKU表
CREATE TABLE skus (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    market_price DECIMAL(10,2),
    weight DECIMAL(8,3),
    volume DECIMAL(8,3),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 品牌表
CREATE TABLE brands (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 商品属性表
CREATE TABLE product_attributes (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value VARCHAR(500) NOT NULL,
    attribute_type VARCHAR(20) NOT NULL, -- 'text', 'number', 'boolean', 'select'
    is_searchable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SKU属性表 (颜色、尺寸等)
CREATE TABLE sku_attributes (
    id UUID PRIMARY KEY,
    sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value VARCHAR(200) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(sku_id, attribute_name)
);

-- 商品图片表
CREATE TABLE product_images (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 商品标签表
CREATE TABLE product_tags (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    tag_type VARCHAR(20) DEFAULT 'general', -- 'general', 'promotion', 'feature'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(product_id, tag_name)
);
```

### 搜索引擎设计 (Elasticsearch)

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "name": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart",
        "fields": {
          "suggest": {
            "type": "completion"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "category": {
        "type": "nested",
        "properties": {
          "id": { "type": "keyword" },
          "name": { "type": "keyword" },
          "path": { "type": "keyword" }
        }
      },
      "brand": {
        "type": "object",
        "properties": {
          "id": { "type": "keyword" },
          "name": { "type": "keyword" }
        }
      },
      "price": { "type": "double" },
      "price_range": { "type": "keyword" },
      "attributes": {
        "type": "nested",
        "properties": {
          "name": { "type": "keyword" },
          "value": { "type": "keyword" }
        }
      },
      "tags": { "type": "keyword" },
      "status": { "type": "keyword" },
      "created_at": { "type": "date" },
      "popularity_score": { "type": "double" },
      "rating": { "type": "double" },
      "review_count": { "type": "integer" },
      "sale_count": { "type": "integer" }
    }
  }
}
```

## API 接口

### 商品管理

```yaml
/api/v1/products:
  GET /:
    summary: 获取商品列表
    parameters:
      - name: category_id
        in: query
        schema:
          type: string
          format: uuid
      - name: brand_id
        in: query
        schema:
          type: string
          format: uuid
      - name: status
        in: query
        schema:
          type: string
          enum: [draft, published, archived]
      - name: page
        in: query
        schema:
          type: integer
          default: 1
      - name: limit
        in: query
        schema:
          type: integer
          default: 20
          maximum: 100
    responses:
      200:
        description: 商品列表
        content:
          application/json:
            schema:
              type: object
              properties:
                products:
                  type: array
                  items:
                    $ref: '#/components/schemas/Product'
                pagination:
                  $ref: '#/components/schemas/Pagination'

  POST /:
    summary: 创建商品
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProductCreateRequest'
    responses:
      201:
        description: 商品创建成功
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Product'

  GET /{product_id}:
    summary: 获取商品详情
    parameters:
      - name: product_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 商品详情
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProductDetail'

  PUT /{product_id}:
    summary: 更新商品
    security:
      - BearerAuth: []
    parameters:
      - name: product_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProductUpdateRequest'
    responses:
      200:
        description: 更新成功

  DELETE /{product_id}:
    summary: 删除商品
    security:
      - BearerAuth: []
    parameters:
      - name: product_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: 删除成功
```

### 商品搜索

```yaml
/api/v1/search:
  GET /products:
    summary: 搜索商品
    parameters:
      - name: q
        in: query
        description: 搜索关键词
        schema:
          type: string
      - name: category
        in: query
        description: 分类筛选
        schema:
          type: string
      - name: brand
        in: query
        description: 品牌筛选
        schema:
          type: string
      - name: price_min
        in: query
        description: 最低价格
        schema:
          type: number
      - name: price_max
        in: query
        description: 最高价格
        schema:
          type: number
      - name: sort
        in: query
        description: 排序方式
        schema:
          type: string
          enum: [relevance, price_asc, price_desc, sales, newest]
          default: relevance
      - name: page
        in: query
        schema:
          type: integer
          default: 1
      - name: limit
        in: query
        schema:
          type: integer
          default: 20
    responses:
      200:
        description: 搜索结果
        content:
          application/json:
            schema:
              type: object
              properties:
                products:
                  type: array
                  items:
                    $ref: '#/components/schemas/ProductSearchResult'
                facets:
                  type: object
                  properties:
                    categories:
                      type: array
                      items:
                        type: object
                        properties:
                          name:
                            type: string
                          count:
                            type: integer
                    brands:
                      type: array
                      items:
                        type: object
                        properties:
                          name:
                            type: string
                          count:
                            type: integer
                    price_ranges:
                      type: array
                      items:
                        type: object
                        properties:
                          range:
                            type: string
                          count:
                            type: integer
                pagination:
                  $ref: '#/components/schemas/Pagination'
                total:
                  type: integer

  GET /suggestions:
    summary: 搜索建议
    parameters:
      - name: q
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: 搜索建议
        content:
          application/json:
            schema:
              type: object
              properties:
                suggestions:
                  type: array
                  items:
                    type: string
```

## 业务逻辑

### 商品发布流程

```python
class ProductPublishService:
    def __init__(self, db, search_engine, event_publisher):
        self.db = db
        self.search_engine = search_engine
        self.event_publisher = event_publisher
    
    async def publish_product(self, product_id: str, user_id: str) -> bool:
        """
        商品发布流程
        1. 验证商品信息完整性
        2. 检查库存配置
        3. 更新商品状态
        4. 同步搜索索引
        5. 发布事件通知
        """
        async with self.db.transaction():
            # 1. 获取商品信息
            product = await self.db.get_product(product_id)
            if not product:
                raise ProductNotFoundError()
            
            # 2. 验证发布条件
            validation_result = await self._validate_product_for_publish(product)
            if not validation_result.is_valid:
                raise ProductValidationError(validation_result.errors)
            
            # 3. 更新商品状态
            await self.db.update_product_status(
                product_id, 
                'published',
                published_at=datetime.utcnow(),
                published_by=user_id
            )
            
            # 4. 同步搜索索引
            search_doc = self._build_search_document(product)
            await self.search_engine.index_document('products', product_id, search_doc)
            
            # 5. 发布事件
            event = {
                'event_type': 'product.published',
                'product_id': product_id,
                'published_by': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            await self.event_publisher.publish('product.events', event)
            
            return True
    
    async def _validate_product_for_publish(self, product) -> ValidationResult:
        """验证商品发布条件"""
        errors = []
        
        # 基本信息检查
        if not product.name or len(product.name.strip()) < 2:
            errors.append("商品名称不能为空且长度不能少于2个字符")
        
        if not product.description:
            errors.append("商品描述不能为空")
        
        if not product.category_id:
            errors.append("必须选择商品分类")
        
        # SKU检查
        skus = await self.db.get_product_skus(product.id)
        if not skus:
            errors.append("至少需要一个SKU")
        
        for sku in skus:
            if sku.price <= 0:
                errors.append(f"SKU {sku.sku_code} 价格必须大于0")
        
        # 图片检查
        images = await self.db.get_product_images(product.id)
        if not images:
            errors.append("至少需要一张商品图片")
        
        return ValidationResult(len(errors) == 0, errors)
```

### 价格计算引擎

```python
class PricingEngine:
    def __init__(self, rule_engine):
        self.rule_engine = rule_engine
    
    async def calculate_price(self, sku_id: str, context: PricingContext) -> PriceResult:
        """
        价格计算
        1. 获取基础价格
        2. 应用定价规则
        3. 计算最终价格
        """
        # 获取SKU基础价格
        sku = await self.db.get_sku(sku_id)
        base_price = sku.price
        
        # 应用定价规则
        applicable_rules = await self.rule_engine.get_applicable_rules(
            sku_id, context
        )
        
        current_price = base_price
        applied_rules = []
        
        for rule in sorted(applicable_rules, key=lambda x: x.priority):
            rule_result = await rule.apply(current_price, context)
            if rule_result.applied:
                current_price = rule_result.new_price
                applied_rules.append(rule_result)
        
        return PriceResult(
            sku_id=sku_id,
            base_price=base_price,
            current_price=current_price,
            discount_amount=base_price - current_price,
            applied_rules=applied_rules
        )

class DynamicPricingRule:
    """动态定价规则"""
    
    async def apply(self, current_price: Decimal, context: PricingContext) -> RuleResult:
        # 基于库存水位调价
        inventory_level = await self._get_inventory_level(context.sku_id)
        
        if inventory_level < 10:  # 库存紧张，提价
            new_price = current_price * Decimal('1.05')  # 提价5%
            return RuleResult(
                applied=True,
                new_price=new_price,
                reason="库存紧张自动提价"
            )
        elif inventory_level > 100:  # 库存过多，降价
            new_price = current_price * Decimal('0.95')  # 降价5%
            return RuleResult(
                applied=True,
                new_price=new_price,
                reason="库存过多自动降价"
            )
        
        return RuleResult(applied=False, new_price=current_price)
```

### 搜索服务

```python
class ProductSearchService:
    def __init__(self, elasticsearch_client):
        self.es = elasticsearch_client
    
    async def search_products(self, query: SearchQuery) -> SearchResult:
        """
        商品搜索
        支持全文搜索、分面搜索、排序、分页
        """
        # 构建ES查询
        es_query = {
            "query": self._build_query(query),
            "aggs": self._build_aggregations(),
            "sort": self._build_sort(query.sort),
            "from": (query.page - 1) * query.limit,
            "size": query.limit,
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {}
                }
            }
        }
        
        # 执行搜索
        response = await self.es.search(index="products", body=es_query)
        
        # 解析结果
        products = []
        for hit in response['hits']['hits']:
            product = ProductSearchResult.from_es_hit(hit)
            products.append(product)
        
        # 解析分面
        facets = self._parse_aggregations(response.get('aggregations', {}))
        
        return SearchResult(
            products=products,
            total=response['hits']['total']['value'],
            facets=facets,
            pagination=Pagination(
                page=query.page,
                limit=query.limit,
                total=response['hits']['total']['value']
            )
        )
    
    def _build_query(self, query: SearchQuery) -> dict:
        """构建ES查询"""
        must_clauses = []
        filter_clauses = []
        
        # 全文搜索
        if query.keyword:
            must_clauses.append({
                "multi_match": {
                    "query": query.keyword,
                    "fields": ["name^3", "description", "attributes.value"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        # 分类筛选
        if query.category_id:
            filter_clauses.append({
                "term": {"category.id": query.category_id}
            })
        
        # 品牌筛选
        if query.brand_id:
            filter_clauses.append({
                "term": {"brand.id": query.brand_id}
            })
        
        # 价格范围筛选
        if query.price_min or query.price_max:
            price_filter = {"range": {"price": {}}}
            if query.price_min:
                price_filter["range"]["price"]["gte"] = query.price_min
            if query.price_max:
                price_filter["range"]["price"]["lte"] = query.price_max
            filter_clauses.append(price_filter)
        
        # 状态筛选
        filter_clauses.append({
            "term": {"status": "published"}
        })
        
        return {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses
            }
        }
```

## 性能优化

### 缓存策略

1. **商品信息缓存**
   - Redis缓存热门商品详情
   - CDN缓存商品图片
   - 应用层缓存分类树

2. **搜索优化**
   - ES索引优化
   - 搜索结果缓存
   - 分面结果缓存

3. **数据库优化**
   - 读写分离
   - 分库分表
   - 索引优化

### 监控指标

- 商品发布成功率
- 搜索响应时间
- 缓存命中率
- 数据库慢查询

## 部署配置

### 环境变量

```bash
# 数据库配置
PRODUCT_DB_URL=postgresql://user:pass@localhost/product_db

# 搜索引擎配置
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=products

# 缓存配置
PRODUCT_REDIS_URL=redis://localhost:6379/2

# 文件存储配置
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=product-images
```

## 相关文档

- [库存模块](../inventory/overview.md)
- [搜索架构](../../architecture/search.md)
- [缓存策略](../../architecture/caching.md)
- [事件架构](../../architecture/event-driven.md)
