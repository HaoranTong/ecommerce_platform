<!--
文档说明：
- 内容：商品管理模块的技术设计方案
- 使用方法：开发实施前查阅，理解技术架构和设计决策
- 更新方法：技术方案变更时更新
- 引用关系：引用 [架构总览](../../architecture/overview.md)、[数据库规范](../../standards/database-standards.md)
- 更新频率：技术架构调整时
-->

# 商品管理模块技术设计

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-12  
👤 **负责人**: AI开发助手  
🔄 **最后更新**: 2025-09-12  
📋 **版本**: v1.0.0  

## 模块架构设计

### 整体架构
基于 [系统架构总览](../../architecture/overview.md) 的三层架构模式：

```
product-catalog/
├── routes/
│   ├── product.py         # 商品路由 (/api/v1/products/*)
│   └── category.py        # 分类路由 (/api/v1/categories/*)
├── services/
│   ├── product_service.py # 商品业务逻辑
│   └── category_service.py # 分类业务逻辑
└── models/
    ├── product.py         # 商品数据模型
    └── category.py        # 分类数据模型
```

### 核心组件职责

#### ProductService 业务逻辑层
```python
class ProductService:
    """商品业务逻辑服务"""
    
    @staticmethod
    def create_product(product_data: ProductCreateRequest) -> Product:
        """创建商品，包含业务验证和库存初始化"""
        
    @staticmethod  
    def get_products(filters: ProductFilters) -> PaginatedResponse:
        """获取商品列表，支持分页、筛选、排序"""
        
    @staticmethod
    def update_inventory(product_id: int, quantity: int) -> bool:
        """更新库存数量，包含并发控制和状态更新"""
```

#### CategoryService 业务逻辑层
```python
class CategoryService:
    """分类业务逻辑服务"""
    
    @staticmethod
    def get_category_tree() -> List[CategoryTree]:
        """获取分类树结构，缓存优化"""
        
    @staticmethod
    def create_category(category_data: CategoryCreateRequest) -> Category:
        """创建分类，验证层级深度和命名唯一性"""
```

## 数据模型设计

### 核心数据模型
严格遵循 [数据库设计规范](../../standards/database-standards.md) 和 [命名规范](../../standards/naming-conventions.md)：

#### Product 商品模型
```python
class Product(BaseModel, TimestampMixin):
    """商品模型"""
    __tablename__ = 'products'
    
    # 基础信息 - 遵循naming-conventions.md
    name = Column(String(200), nullable=False)              # 商品名称
    sku = Column(String(100), unique=True, nullable=False)  # 商品SKU
    description = Column(Text, nullable=True)               # 商品描述
    
    # 分类关联 - 遵循database-standards.md外键规范
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    # 价格和库存 - 遵循database-standards.md数据类型标准
    price = Column(DECIMAL(10, 2), nullable=False)         # 商品价格
    stock_quantity = Column(Integer, nullable=False)        # 库存数量
    
    # 状态管理
    status = Column(String(20), default='active')          # 商品状态
    
    # 扩展字段
    image_url = Column(String(500), nullable=True)         # 主图URL
    attributes = Column(Text, nullable=True)               # JSON属性
    
    # 关系映射
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("Cart", back_populates="product")
```

#### Category 分类模型
```python
class Category(BaseModel, TimestampMixin):
    """分类模型"""
    __tablename__ = 'categories'
    
    # 基础信息
    name = Column(String(100), nullable=False)             # 分类名称
    parent_id = Column(Integer, ForeignKey('categories.id')) # 父分类ID
    sort_order = Column(Integer, default=0)                # 排序序号
    is_active = Column(Boolean, default=True)              # 是否启用
    
    # 关系映射
    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])
```

### 数据库索引策略
按照 [数据库规范](../../standards/database-standards.md#索引规范) 设计：

```python
# Product表索引
__table_args__ = (
    Index('idx_category_status', 'category_id', 'status'),    # 分类+状态查询
    Index('idx_status_created', 'status', 'created_at'),      # 状态+时间查询
    Index('idx_sku', 'sku'),                                  # SKU唯一索引
    Index('idx_price_range', 'price'),                        # 价格范围查询
)

# Category表索引  
__table_args__ = (
    Index('idx_parent_sort', 'parent_id', 'sort_order'),      # 父分类+排序
    Index('idx_active_name', 'is_active', 'name'),            # 状态+名称
)
```

## API接口设计

### RESTful接口规范
严格遵循 [API设计标准](../../standards/api-standards.md)：

#### 商品接口设计
```python
# GET /api/v1/products - 商品列表
@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc")
) -> PaginatedResponse[ProductListItem]:
    """获取商品列表，支持分页、筛选、搜索、排序"""

# POST /api/v1/products - 创建商品
@router.post("/products")
async def create_product(
    product_data: ProductCreateRequest,
    current_user: User = Depends(get_current_admin_user)
) -> ProductResponse:
    """创建商品，需要管理员权限"""
```

#### 分类接口设计
```python
# GET /api/v1/categories - 分类树
@router.get("/categories")
async def get_categories() -> List[CategoryTree]:
    """获取分类树结构，包含缓存优化"""

# POST /api/v1/categories - 创建分类
@router.post("/categories")  
async def create_category(
    category_data: CategoryCreateRequest,
    current_user: User = Depends(get_current_admin_user)
) -> CategoryResponse:
    """创建分类，验证层级和唯一性"""
```

### 数据传输对象设计
遵循 [API标准](../../standards/api-standards.md#请求响应格式)：

```python
# 请求模型
class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)
    image_url: Optional[str] = None

# 响应模型
class ProductListItem(BaseModel):
    id: int
    name: str
    sku: str
    price: Decimal
    stock_quantity: int
    status: str
    category_name: str
    image_url: Optional[str]
    created_at: datetime
```

## 缓存策略设计

### Redis缓存方案
基于 [Redis缓存模块](../redis-cache/overview.md) 的设计：

```python
# 分类树缓存 - 1小时过期
CATEGORY_TREE_CACHE_KEY = "category_tree"
CATEGORY_TREE_TTL = 3600

# 商品详情缓存 - 30分钟过期  
PRODUCT_DETAIL_CACHE_KEY = "product_detail:{product_id}"
PRODUCT_DETAIL_TTL = 1800

# 商品列表缓存 - 5分钟过期
PRODUCT_LIST_CACHE_KEY = "product_list:{hash}"
PRODUCT_LIST_TTL = 300
```

### 缓存更新策略
```python
class ProductCacheManager:
    """商品缓存管理器"""
    
    @staticmethod
    def invalidate_product_cache(product_id: int):
        """商品更新时清除相关缓存"""
        cache.delete(f"product_detail:{product_id}")
        cache.delete_pattern("product_list:*")
        
    @staticmethod
    def invalidate_category_cache():
        """分类更新时清除分类树缓存"""
        cache.delete("category_tree")
```

## 性能优化设计

### 数据库查询优化
1. **分页查询优化**：使用游标分页避免大偏移量
2. **N+1问题解决**：使用joinedload预加载关联数据
3. **索引优化**：为常用查询字段建立复合索引

### 并发控制设计
```python
class InventoryService:
    """库存并发控制服务"""
    
    @staticmethod
    def update_stock_with_lock(product_id: int, quantity: int) -> bool:
        """使用数据库行锁更新库存"""
        with db.session.begin():
            product = db.session.query(Product).with_for_update().get(product_id)
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                return True
            return False
```

## 错误处理设计

### 业务异常定义
```python
class ProductNotFoundError(BusinessError):
    """商品不存在异常"""
    code = "PRODUCT_NOT_FOUND"
    message = "商品不存在"

class InsufficientStockError(BusinessError):
    """库存不足异常"""  
    code = "INSUFFICIENT_STOCK"
    message = "库存不足"
```

### 错误响应格式
遵循 [API标准](../../standards/api-standards.md#错误处理) 的统一格式：

```json
{
    "success": false,
    "error": {
        "code": "PRODUCT_NOT_FOUND",
        "message": "商品不存在",
        "details": {
            "product_id": 123
        }
    }
}
```

## 监控和日志

### 关键指标监控
- 商品查询响应时间
- 库存更新成功率
- 分类树查询缓存命中率
- API错误率统计

### 业务日志记录
```python
# 重要业务操作日志
logger.info("Product created", extra={
    "action": "create_product",
    "product_id": product.id,
    "sku": product.sku,
    "operator": current_user.username
})
```

参考文档：
- [架构总览](../../architecture/overview.md)
- [数据库设计规范](../../standards/database-standards.md)
- [API设计标准](../../standards/api-standards.md)
- [Redis缓存模块](../redis-cache/overview.md)