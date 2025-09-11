# 商品API模块 (Product API Module)

## 模块概述

商品API模块 (`app/api/product_routes.py`) 是电商平台商品管理的核心API组件，提供完整的商品生命周期管理接口，包括商品创建、查询、更新、删除等CRUD操作，支持商品状态管理、库存控制和价格管理。

### 主要功能

1. **商品信息管理**
   - 商品创建和注册
   - 商品信息更新
   - 商品状态控制
   - 商品删除管理

2. **商品查询服务**
   - 商品列表查询
   - 商品详情获取
   - 分页和排序支持
   - 条件过滤查询

3. **库存和价格管理**
   - 库存数量更新
   - 价格信息管理
   - 商品状态控制
   - 批量操作支持

4. **分类和属性管理**
   - 商品分类关联
   - 商品属性设置
   - 图片信息管理
   - SKU规格管理

## 技术架构

### API架构图

```mermaid
graph TB
    A[Client] --> B[Product API Router]
    B --> C[Authentication Layer]
    B --> D[Data Validation]
    B --> E[Business Logic]
    
    C --> F[JWT Verification]
    D --> G[Pydantic Schemas]
    
    E --> H[Product Service]
    E --> I[Category Service]
    E --> J[Inventory Service]
    
    H --> K[(MySQL Database)]
    I --> L[Category Validation]
    J --> M[Stock Management]
    
    subgraph "API Endpoints"
        N[POST /api/products]
        O[GET /api/products]
        P[GET /api/products/{id}]
        Q[PUT /api/products/{id}]
        R[DELETE /api/products/{id}]
    end
```

### 商品管理流程

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Product API
    participant Auth as Auth Service
    participant DB as Database
    participant Cat as Category Service
    participant Stock as Inventory
    
    Note over C,Stock: 创建商品流程
    C->>A: POST /api/products
    A->>Auth: 验证管理员权限
    Auth-->>A: 权限确认
    A->>Cat: 验证分类存在性
    Cat-->>A: 分类有效
    A->>DB: 创建商品记录
    DB-->>A: 返回商品信息
    A->>Stock: 初始化库存
    Stock-->>A: 库存设置成功
    A-->>C: 返回创建结果
    
    Note over C,Stock: 查询商品流程
    C->>A: GET /api/products
    A->>DB: 查询商品列表
    DB-->>A: 返回商品数据
    A->>A: 数据过滤和分页
    A-->>C: 返回商品列表
    
    Note over C,Stock: 更新商品流程
    C->>A: PUT /api/products/{id}
    A->>Auth: 验证管理员权限
    Auth-->>A: 权限确认
    A->>DB: 查询现有商品
    DB-->>A: 返回商品信息
    A->>DB: 更新商品数据
    DB-->>A: 更新成功
    A-->>C: 返回更新结果
```

## API接口详解

### 商品管理接口

#### 1. 创建商品

**端点**: `POST /api/products`  
**功能**: 创建新的商品记录  
**认证**: 需要管理员权限  

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**请求体**:
```json
{
    "name": "iPhone 15 Pro",
    "sku": "IPH15P-128G-TIT",
    "description": "Apple iPhone 15 Pro 128GB 钛原色",
    "category_id": 101,
    "price": 9999.00,
    "stock_quantity": 100,
    "status": "active",
    "image_url": "https://example.com/images/iphone15pro.jpg",
    "attributes": "{\"color\":\"钛原色\",\"storage\":\"128GB\",\"network\":\"5G\"}",
    "images": "[\"https://example.com/img1.jpg\",\"https://example.com/img2.jpg\"]"
}
```

**响应**:
```json
{
    "id": 2001,
    "name": "iPhone 15 Pro",
    "sku": "IPH15P-128G-TIT",
    "description": "Apple iPhone 15 Pro 128GB 钛原色",
    "category_id": 101,
    "price": 9999.00,
    "stock_quantity": 100,
    "status": "active",
    "image_url": "https://example.com/images/iphone15pro.jpg",
    "attributes": "{\"color\":\"钛原色\",\"storage\":\"128GB\",\"network\":\"5G\"}",
    "images": "[\"https://example.com/img1.jpg\",\"https://example.com/img2.jpg\"]",
    "created_at": "2025-09-11T10:00:00Z",
    "updated_at": "2025-09-11T10:00:00Z"
}
```

**错误响应**:
- `400 Bad Request`: SKU已存在或分类不存在
- `401 Unauthorized`: 用户未认证
- `403 Forbidden`: 权限不足
- `422 Unprocessable Entity`: 数据验证失败

#### 2. 获取商品列表

**端点**: `GET /api/products`  
**功能**: 获取商品列表，支持分页和筛选  
**认证**: 无需认证（公开接口）  

**查询参数**:
- `skip`: 跳过记录数 (默认: 0)
- `limit`: 返回记录数 (默认: 100, 最大: 1000)
- `category_id`: 按分类筛选
- `status`: 按状态筛选 (active/inactive/out_of_stock)
- `min_price`: 最低价格
- `max_price`: 最高价格
- `search`: 搜索关键词 (商品名称或描述)

**请求示例**:
```
GET /api/products?category_id=101&status=active&skip=0&limit=20&min_price=1000&max_price=10000
```

**响应**:
```json
[
    {
        "id": 2001,
        "name": "iPhone 15 Pro",
        "sku": "IPH15P-128G-TIT",
        "description": "Apple iPhone 15 Pro 128GB 钛原色",
        "category_id": 101,
        "price": 9999.00,
        "stock_quantity": 100,
        "status": "active",
        "image_url": "https://example.com/images/iphone15pro.jpg",
        "created_at": "2025-09-11T10:00:00Z",
        "updated_at": "2025-09-11T10:00:00Z"
    },
    {
        "id": 2002,
        "name": "MacBook Pro 14",
        "sku": "MBP14-M3-512G",
        "description": "Apple MacBook Pro 14英寸 M3芯片 512GB",
        "category_id": 101,
        "price": 14999.00,
        "stock_quantity": 50,
        "status": "active",
        "image_url": "https://example.com/images/macbook14.jpg",
        "created_at": "2025-09-11T11:00:00Z",
        "updated_at": "2025-09-11T11:00:00Z"
    }
]
```

#### 3. 获取商品详情

**端点**: `GET /api/products/{product_id}`  
**功能**: 获取指定商品的详细信息  
**认证**: 无需认证（公开接口）  

**路径参数**:
- `product_id`: 商品ID

**响应**: 返回完整的商品信息（同创建商品响应格式）

**错误响应**:
- `404 Not Found`: 商品不存在

#### 4. 更新商品信息

**端点**: `PUT /api/products/{product_id}`  
**功能**: 更新指定商品的信息  
**认证**: 需要管理员权限  

**路径参数**:
- `product_id`: 商品ID

**请求体** (部分更新支持):
```json
{
    "name": "iPhone 15 Pro Max",
    "price": 10999.00,
    "stock_quantity": 80,
    "status": "active",
    "description": "Apple iPhone 15 Pro Max 128GB 钛原色"
}
```

**响应**: 返回更新后的完整商品信息

**业务规则**:
- SKU不允许修改（业务约束）
- 商品ID不允许修改
- 价格必须为正数
- 库存数量不能为负数

#### 5. 删除商品

**端点**: `DELETE /api/products/{product_id}`  
**功能**: 删除指定商品（软删除，标记为不可用）  
**认证**: 需要管理员权限  

**路径参数**:
- `product_id`: 商品ID

**响应**: `204 No Content`

**业务逻辑**:
- 实现软删除，将状态设置为`inactive`
- 检查是否有关联的订单或购物车
- 清理相关缓存数据

## 数据模型Schema

### 请求模型

#### ProductCreate
```python
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    category_id: Optional[int] = Field(None, gt=0)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)
    status: str = Field(default="active", regex="^(active|inactive|out_of_stock)$")
    image_url: Optional[str] = Field(None, max_length=500)
    attributes: Optional[str] = Field(None, description="JSON格式的商品属性")
    images: Optional[str] = Field(None, description="JSON格式的图片URL数组")
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('价格必须大于0')
        return v
    
    @validator('sku')
    def validate_sku(cls, v):
        if not v.strip():
            raise ValueError('SKU不能为空')
        return v.strip().upper()
```

#### ProductUpdate
```python
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category_id: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, regex="^(active|inactive|out_of_stock)$")
    image_url: Optional[str] = Field(None, max_length=500)
    attributes: Optional[str] = Field(None)
    images: Optional[str] = Field(None)
```

### 响应模型

#### ProductRead
```python
class ProductRead(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Decimal
    stock_quantity: int
    status: str
    image_url: Optional[str] = None
    attributes: Optional[str] = None
    images: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## 业务逻辑实现

### 1. 商品创建逻辑

```python
async def create_product(
    product_data: ProductCreate,
    db: Session,
    current_user: User
) -> Product:
    """创建商品的完整业务逻辑"""
    
    # 1. 权限检查
    if not is_admin_user(current_user):
        raise HTTPException(
            status_code=403,
            detail="权限不足，需要管理员权限"
        )
    
    # 2. SKU唯一性检查
    existing_product = db.query(Product).filter(
        Product.sku == product_data.sku
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail=f"SKU '{product_data.sku}' 已存在"
        )
    
    # 3. 分类存在性检查
    if product_data.category_id:
        category = db.query(Category).filter(
            Category.id == product_data.category_id,
            Category.is_active == True
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=400,
                detail="指定的分类不存在或已禁用"
            )
    
    # 4. 创建商品记录
    db_product = Product(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # 5. 记录操作日志
    log_product_operation(
        user_id=current_user.id,
        operation="CREATE",
        product_id=db_product.id,
        details=f"创建商品: {db_product.name}"
    )
    
    return db_product
```

### 2. 商品查询逻辑

```python
async def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    search: Optional[str] = None
) -> List[Product]:
    """商品列表查询的业务逻辑"""
    
    # 1. 构建查询条件
    query = db.query(Product)
    
    # 2. 分类过滤
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # 3. 状态过滤
    if status:
        query = query.filter(Product.status == status)
    else:
        # 默认只显示活跃商品
        query = query.filter(Product.status.in_(['active', 'out_of_stock']))
    
    # 4. 价格范围过滤
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # 5. 搜索关键词过滤
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        )
    
    # 6. 排序和分页
    products = query.order_by(Product.created_at.desc())\
                   .offset(skip)\
                   .limit(min(limit, 1000))\
                   .all()
    
    return products
```

### 3. 库存管理逻辑

```python
async def update_product_stock(
    product_id: int,
    quantity_change: int,
    operation_type: str,
    db: Session
) -> bool:
    """更新商品库存的业务逻辑"""
    
    # 1. 获取商品信息
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )
    
    # 2. 计算新库存
    new_stock = product.stock_quantity + quantity_change
    
    # 3. 库存检查
    if new_stock < 0:
        raise HTTPException(
            status_code=400,
            detail=f"库存不足，当前库存: {product.stock_quantity}"
        )
    
    # 4. 更新库存
    product.stock_quantity = new_stock
    
    # 5. 自动更新商品状态
    if new_stock == 0:
        product.status = 'out_of_stock'
    elif product.status == 'out_of_stock' and new_stock > 0:
        product.status = 'active'
    
    # 6. 提交更改
    db.commit()
    
    # 7. 记录库存变更日志
    log_stock_change(
        product_id=product_id,
        old_stock=product.stock_quantity - quantity_change,
        new_stock=new_stock,
        operation=operation_type
    )
    
    return True
```

## 使用示例

### 1. 创建商品

```python
import httpx

async def create_product(access_token: str, product_data: dict):
    """创建商品示例"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/products",
            headers=headers,
            json=product_data
        )
        
        if response.status_code == 201:
            product = response.json()
            print(f"商品创建成功: {product['name']} (ID: {product['id']})")
            return product
        else:
            print(f"创建失败: {response.json()}")
            return None

# 使用示例
product_data = {
    "name": "iPhone 15 Pro",
    "sku": "IPH15P-128G-TIT",
    "description": "Apple iPhone 15 Pro 128GB 钛原色",
    "category_id": 101,
    "price": 9999.00,
    "stock_quantity": 100,
    "status": "active",
    "image_url": "https://example.com/images/iphone15pro.jpg"
}

await create_product(access_token, product_data)
```

### 2. 查询商品列表

```python
async def get_products_list(category_id: int = None, search: str = None):
    """获取商品列表示例"""
    params = {}
    if category_id:
        params['category_id'] = category_id
    if search:
        params['search'] = search
    params['limit'] = 20
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/products",
            params=params
        )
        
        if response.status_code == 200:
            products = response.json()
            print(f"找到 {len(products)} 个商品:")
            for product in products:
                print(f"- {product['name']}: ¥{product['price']}")
            return products
        else:
            print(f"查询失败: {response.json()}")
            return []
```

### 3. 更新商品信息

```python
async def update_product(access_token: str, product_id: int, updates: dict):
    """更新商品信息示例"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"http://localhost:8000/api/products/{product_id}",
            headers=headers,
            json=updates
        )
        
        if response.status_code == 200:
            product = response.json()
            print(f"商品更新成功: {product['name']}")
            return product
        else:
            print(f"更新失败: {response.json()}")
            return None

# 使用示例：更新价格和库存
updates = {
    "price": 8999.00,
    "stock_quantity": 150
}
await update_product(access_token, 2001, updates)
```

### 4. 删除商品

```python
async def delete_product(access_token: str, product_id: int):
    """删除商品示例"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://localhost:8000/api/products/{product_id}",
            headers=headers
        )
        
        if response.status_code == 204:
            print(f"商品 {product_id} 删除成功")
            return True
        else:
            print(f"删除失败: {response.json()}")
            return False
```

## 错误处理

### 常见错误类型

| HTTP状态码 | 错误类型 | 描述 | 解决方案 |
|-----------|----------|------|----------|
| 400 | Bad Request | SKU重复、分类不存在、价格格式错误 | 检查输入数据的合法性 |
| 401 | Unauthorized | 用户未认证 | 提供有效的访问令牌 |
| 403 | Forbidden | 权限不足 | 需要管理员权限 |
| 404 | Not Found | 商品不存在 | 确认商品ID正确 |
| 422 | Unprocessable Entity | 数据验证失败 | 检查字段格式和约束 |
| 500 | Internal Server Error | 数据库错误、系统错误 | 检查服务状态 |

### 详细错误信息

```python
# SKU重复错误
{
    "detail": "SKU 'IPH15P-128G-TIT' 已存在",
    "error_code": "DUPLICATE_SKU",
    "existing_product_id": 2001
}

# 分类不存在错误
{
    "detail": "指定的分类不存在或已禁用",
    "error_code": "CATEGORY_NOT_FOUND",
    "category_id": 999
}

# 价格格式错误
{
    "detail": [
        {
            "loc": ["body", "price"],
            "msg": "价格必须大于0",
            "type": "value_error"
        }
    ]
}
```

## 性能优化

### 1. 数据库优化

```python
# 索引策略
- 商品名称索引用于搜索
- SKU唯一索引用于快速查找
- 分类状态复合索引用于列表查询
- 价格范围索引用于价格筛选

# 查询优化
- 使用select_related加载关联分类
- 实现查询结果缓存
- 分页查询避免大量数据加载
```

### 2. 缓存策略

```python
# 缓存设计
- 热门商品信息缓存
- 商品列表查询结果缓存
- 分类商品计数缓存
- 设置合理的缓存过期时间
```

### 3. 搜索优化

```python
# 搜索性能
- 实现全文搜索索引
- 搜索结果相关性排序
- 搜索历史和热词统计
- 搜索建议和自动完成
```

## 监控和日志

### 1. 操作日志

```python
# 关键操作记录
- 商品创建、更新、删除
- 库存变更记录
- 价格调整历史
- 状态变更日志
```

### 2. 业务指标

```python
# 监控指标
- 商品查询频率
- 热门商品排行
- 库存预警统计
- 价格变动趋势
```

### 3. 性能指标

```python
# 技术指标
- API响应时间
- 数据库查询性能
- 缓存命中率
- 搜索查询延迟
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1.0 | 2025-09-11 | 初始版本，实现基础商品管理API |

## 相关文档

- [商品管理模块](../product-catalog/overview.md)
- [数据模型定义](../models/overview.md)
- [分类管理API](../category-routes/overview.md)
- [库存管理系统](../inventory/overview.md)
