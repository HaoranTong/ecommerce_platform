# 购物车API模块 (Shopping Cart API Module)

## 模块概述

购物车API模块 (`app/api/cart_routes.py`) 是电商平台购物车管理的核心API组件，提供完整的购物车操作接口，包括商品添加、数量更新、商品移除、购物车查询和统计功能，集成Redis缓存和实时库存验证。

### 主要功能

1. **购物车商品管理**
   - 添加商品到购物车
   - 更新商品数量
   - 移除指定商品
   - 批量操作支持

2. **购物车查询服务**
   - 获取购物车详情
   - 商品信息聚合
   - 价格计算汇总
   - 库存状态检查

3. **购物车统计功能**
   - 商品种类统计
   - 总数量计算
   - 价格总计算
   - 购物车状态监控

4. **数据同步和缓存**
   - Redis缓存管理
   - 数据库同步机制
   - 实时库存验证
   - 多设备数据一致性

## 技术架构

### API架构图

```mermaid
graph TB
    A[Client] --> B[Cart API Router]
    B --> C[Authentication Layer]
    B --> D[Data Validation]
    B --> E[Business Logic]
    
    C --> F[JWT Verification]
    D --> G[Pydantic Schemas]
    
    E --> H[Cart Manager]
    E --> I[Product Service]
    E --> J[Inventory Service]
    
    H --> K[Redis Cache]
    I --> L[(MySQL Database)]
    J --> M[Stock Validation]
    
    subgraph "API Endpoints"
        N[/cart/add]
        O[/cart/items/{id}]
        P[/cart]
        Q[/cart/clear]
        R[/cart/count]
    end
```

### 购物车操作流程

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Cart API
    participant Auth as Auth Service
    participant Cache as Redis Cache
    participant DB as Database
    participant Stock as Inventory
    
    Note over C,Stock: 添加商品到购物车
    C->>A: POST /cart/add
    A->>Auth: 验证用户令牌
    Auth-->>A: 返回用户信息
    A->>DB: 查询商品信息
    DB-->>A: 返回商品详情
    A->>Stock: 检查库存可用性
    Stock-->>A: 确认库存状态
    A->>Cache: 更新购物车缓存
    Cache-->>A: 确认更新成功
    A-->>C: 返回操作结果
    
    Note over C,Stock: 获取购物车详情
    C->>A: GET /cart
    A->>Auth: 验证用户令牌
    Auth-->>A: 返回用户信息
    A->>Cache: 获取购物车数据
    Cache-->>A: 返回商品ID和数量
    A->>DB: 批量查询商品详情
    DB-->>A: 返回商品信息
    A->>A: 聚合数据和计算价格
    A-->>C: 返回购物车详情
```

## API接口详解

### 购物车操作接口

#### 1. 添加商品到购物车

**端点**: `POST /cart/add`  
**功能**: 将指定商品添加到用户购物车  
**认证**: 需要有效的访问令牌  

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**请求体**:
```json
{
    "product_id": 2001,
    "quantity": 2
}
```

**响应**:
```json
{
    "success": true,
    "message": "商品已添加到购物车",
    "data": {
        "product_id": 2001,
        "quantity": 3,
        "total_quantity": 5,
        "cart_count": 3
    }
}
```

**业务逻辑**:
1. 验证用户身份
2. 验证商品存在性
3. 检查库存可用性
4. 更新Redis购物车缓存
5. 返回更新后的购物车状态

**错误响应**:
- `400 Bad Request`: 商品不存在或库存不足
- `401 Unauthorized`: 用户未认证
- `422 Unprocessable Entity`: 请求参数无效

#### 2. 更新购物车商品数量

**端点**: `PUT /cart/items/{product_id}`  
**功能**: 更新购物车中指定商品的数量  
**认证**: 需要有效的访问令牌  

**路径参数**:
- `product_id`: 商品ID

**请求体**:
```json
{
    "quantity": 5
}
```

**响应**:
```json
{
    "success": true,
    "message": "购物车商品数量已更新",
    "data": {
        "product_id": 2001,
        "old_quantity": 3,
        "new_quantity": 5,
        "total_quantity": 7,
        "cart_count": 3
    }
}
```

**特殊处理**:
- 数量为0时自动移除商品
- 超出库存时限制为库存数量
- 支持增量和绝对数量更新

#### 3. 移除购物车商品

**端点**: `DELETE /cart/items/{product_id}`  
**功能**: 从购物车中移除指定商品  
**认证**: 需要有效的访问令牌  

**路径参数**:
- `product_id`: 商品ID

**响应**:
```json
{
    "success": true,
    "message": "商品已从购物车移除",
    "data": {
        "removed_product_id": 2001,
        "removed_quantity": 5,
        "remaining_count": 2,
        "total_quantity": 3
    }
}
```

#### 4. 获取购物车详情

**端点**: `GET /cart`  
**功能**: 获取用户购物车的完整详情  
**认证**: 需要有效的访问令牌  

**响应**:
```json
{
    "user_id": 1001,
    "items": [
        {
            "product_id": 2001,
            "product_name": "iPhone 15 Pro",
            "product_sku": "IPH15P-128G-TIT",
            "price": 9999.00,
            "quantity": 2,
            "subtotal": 19998.00,
            "image_url": "https://example.com/images/iphone15pro.jpg",
            "stock_quantity": 50,
            "status": "active"
        },
        {
            "product_id": 2002,
            "product_name": "MacBook Pro 14",
            "product_sku": "MBP14-M3-512G",
            "price": 14999.00,
            "quantity": 1,
            "subtotal": 14999.00,
            "image_url": "https://example.com/images/macbook14.jpg",
            "stock_quantity": 30,
            "status": "active"
        }
    ],
    "summary": {
        "total_items": 2,
        "total_quantity": 3,
        "subtotal": 34997.00,
        "estimated_shipping": 15.00,
        "estimated_total": 35012.00
    },
    "updated_at": "2025-09-11T10:30:00Z"
}
```

**数据聚合逻辑**:
1. 从Redis获取购物车商品列表
2. 批量查询商品详细信息
3. 计算价格小计和总计
4. 检查库存状态和商品可用性
5. 返回聚合后的完整信息

#### 5. 清空购物车

**端点**: `DELETE /cart/clear`  
**功能**: 清空用户购物车中的所有商品  
**认证**: 需要有效的访问令牌  

**响应**:
```json
{
    "success": true,
    "message": "购物车已清空",
    "data": {
        "cleared_items": 3,
        "cleared_quantity": 7
    }
}
```

#### 6. 获取购物车统计

**端点**: `GET /cart/count`  
**功能**: 获取购物车的基本统计信息  
**认证**: 需要有效的访问令牌  

**响应**:
```json
{
    "cart_count": 3,
    "total_quantity": 7,
    "last_updated": "2025-09-11T10:30:00Z"
}
```

## 数据模型Schema

### 请求模型

#### CartItemAdd
```python
class CartItemAdd(BaseModel):
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., gt=0, le=999, description="商品数量")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('商品数量必须大于0')
        if v > 999:
            raise ValueError('商品数量不能超过999')
        return v
```

#### CartItemUpdate  
```python
class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0, le=999, description="更新后的商品数量")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('商品数量不能为负数')
        if v > 999:
            raise ValueError('商品数量不能超过999')
        return v
```

### 响应模型

#### CartItemRead
```python
class CartItemRead(BaseModel):
    product_id: int
    product_name: str
    product_sku: str
    price: Decimal
    quantity: int
    subtotal: Decimal
    image_url: Optional[str] = None
    stock_quantity: int
    status: str
    
    class Config:
        from_attributes = True
```

#### CartSummary
```python
class CartSummary(BaseModel):
    user_id: int
    items: List[CartItemRead]
    summary: Dict[str, Any]
    updated_at: datetime
```

## 业务逻辑实现

### 1. 购物车添加逻辑

```python
async def add_item_to_cart(
    user_id: int, 
    product_id: int, 
    quantity: int,
    db: Session,
    cart_manager: RedisCartManager
) -> dict:
    """添加商品到购物车的完整业务逻辑"""
    
    # 1. 验证商品存在性
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == 'active'
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=400,
            detail="商品不存在或已下架"
        )
    
    # 2. 检查库存可用性
    if product.stock_quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"库存不足，当前库存: {product.stock_quantity}"
        )
    
    # 3. 检查购物车中是否已存在该商品
    current_quantity = await cart_manager.get_item_quantity(user_id, product_id)
    total_quantity = current_quantity + quantity
    
    if total_quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"添加失败，总数量将超出库存限制"
        )
    
    # 4. 更新购物车缓存
    success = await cart_manager.add_item(user_id, product_id, quantity)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="购物车更新失败"
        )
    
    # 5. 返回更新结果
    new_total = await cart_manager.get_cart_total_quantity(user_id)
    cart_count = await cart_manager.get_cart_count(user_id)
    
    return {
        "success": True,
        "message": "商品已添加到购物车",
        "data": {
            "product_id": product_id,
            "quantity": total_quantity,
            "total_quantity": new_total,
            "cart_count": cart_count
        }
    }
```

### 2. 购物车查询聚合逻辑

```python
async def get_cart_details(
    user_id: int,
    db: Session,
    cart_manager: RedisCartManager
) -> CartSummary:
    """获取购物车详情的聚合逻辑"""
    
    # 1. 从Redis获取购物车数据
    cart_items = await cart_manager.get_cart_items(user_id)
    
    if not cart_items:
        return CartSummary(
            user_id=user_id,
            items=[],
            summary={
                "total_items": 0,
                "total_quantity": 0,
                "subtotal": 0.00,
                "estimated_shipping": 0.00,
                "estimated_total": 0.00
            },
            updated_at=datetime.now()
        )
    
    # 2. 批量查询商品详情
    product_ids = list(cart_items.keys())
    products = db.query(Product).filter(
        Product.id.in_([int(pid) for pid in product_ids])
    ).all()
    
    # 3. 构建商品详情映射
    product_map = {str(p.id): p for p in products}
    
    # 4. 聚合购物车项目数据
    cart_item_list = []
    total_quantity = 0
    subtotal = Decimal('0.00')
    
    for product_id_str, quantity in cart_items.items():
        product = product_map.get(product_id_str)
        if not product:
            # 商品不存在，从购物车移除
            await cart_manager.remove_item(user_id, int(product_id_str))
            continue
        
        item_subtotal = product.price * quantity
        total_quantity += quantity
        subtotal += item_subtotal
        
        cart_item_list.append(CartItemRead(
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            price=product.price,
            quantity=quantity,
            subtotal=item_subtotal,
            image_url=product.image_url,
            stock_quantity=product.stock_quantity,
            status=product.status
        ))
    
    # 5. 计算运费和总计
    estimated_shipping = calculate_shipping_fee(subtotal)
    estimated_total = subtotal + estimated_shipping
    
    return CartSummary(
        user_id=user_id,
        items=cart_item_list,
        summary={
            "total_items": len(cart_item_list),
            "total_quantity": total_quantity,
            "subtotal": float(subtotal),
            "estimated_shipping": float(estimated_shipping),
            "estimated_total": float(estimated_total)
        },
        updated_at=datetime.now()
    )

def calculate_shipping_fee(subtotal: Decimal) -> Decimal:
    """计算运费"""
    if subtotal >= Decimal('99.00'):
        return Decimal('0.00')  # 满99免运费
    else:
        return Decimal('15.00')  # 标准运费15元
```

## 使用示例

### 1. 添加商品到购物车

```python
import httpx

async def add_to_cart(access_token: str, product_id: int, quantity: int):
    """添加商品到购物车示例"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    cart_data = {
        "product_id": product_id,
        "quantity": quantity
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/cart/add",
            headers=headers,
            json=cart_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"添加成功: {result['message']}")
            print(f"购物车统计: {result['data']}")
            return result
        else:
            print(f"添加失败: {response.json()}")
            return None
```

### 2. 获取购物车详情

```python
async def get_cart(access_token: str):
    """获取购物车详情示例"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/cart",
            headers=headers
        )
        
        if response.status_code == 200:
            cart = response.json()
            print(f"购物车商品数量: {cart['summary']['total_items']}")
            print(f"购物车总金额: {cart['summary']['estimated_total']}")
            
            for item in cart['items']:
                print(f"- {item['product_name']}: {item['quantity']}个, 小计: ¥{item['subtotal']}")
            
            return cart
        else:
            print(f"获取购物车失败: {response.json()}")
            return None
```

### 3. 更新商品数量

```python
async def update_cart_item(access_token: str, product_id: int, quantity: int):
    """更新购物车商品数量示例"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    update_data = {
        "quantity": quantity
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"http://localhost:8000/api/cart/items/{product_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"更新成功: {result['message']}")
            return result
        else:
            print(f"更新失败: {response.json()}")
            return None
```

### 4. 移除购物车商品

```python
async def remove_from_cart(access_token: str, product_id: int):
    """移除购物车商品示例"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://localhost:8000/api/cart/items/{product_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"移除成功: {result['message']}")
            return result
        else:
            print(f"移除失败: {response.json()}")
            return None
```

### 5. 清空购物车

```python
async def clear_cart(access_token: str):
    """清空购物车示例"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            "http://localhost:8000/api/cart/clear",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"清空成功: {result['message']}")
            return result
        else:
            print(f"清空失败: {response.json()}")
            return None
```

## 错误处理

### 常见错误类型

| HTTP状态码 | 错误类型 | 描述 | 解决方案 |
|-----------|----------|------|----------|
| 400 | Bad Request | 商品不存在、库存不足、参数错误 | 检查商品状态和库存 |
| 401 | Unauthorized | 用户未认证或令牌无效 | 重新登录获取令牌 |
| 404 | Not Found | 购物车商品不存在 | 确认商品在购物车中 |
| 422 | Unprocessable Entity | 数据验证失败 | 检查请求参数格式 |
| 500 | Internal Server Error | Redis连接失败、数据库错误 | 检查服务状态 |

### 业务错误处理

```python
# 库存不足错误
{
    "detail": "库存不足，当前库存: 5",
    "error_code": "INSUFFICIENT_STOCK",
    "available_quantity": 5
}

# 商品不存在错误
{
    "detail": "商品不存在或已下架",
    "error_code": "PRODUCT_NOT_FOUND",
    "product_id": 2001
}

# 购物车操作失败
{
    "detail": "购物车更新失败",
    "error_code": "CART_UPDATE_FAILED",
    "retry_suggested": true
}
```

## 性能优化

### 1. Redis缓存优化

```python
# 缓存策略
- 购物车数据存储在Redis Hash结构中
- 设置7天过期时间，支持长期保存
- 使用pipeline批量操作提高性能
- 实现缓存预热和刷新机制
```

### 2. 数据库查询优化

```python
# 查询优化
- 批量查询商品信息，减少数据库访问
- 使用索引字段进行查询
- 实现查询结果缓存
- 避免N+1查询问题
```

### 3. 业务逻辑优化

```python
# 性能优化点
- 异步处理Redis操作
- 并发安全的库存检查
- 智能的数据聚合算法
- 合理的错误重试机制
```

## 监控和日志

### 1. 操作日志

```python
# 关键操作记录
- 商品添加到购物车
- 购物车数量更新
- 商品移除操作
- 购物车清空事件
```

### 2. 性能指标

```python
# 监控指标
- API响应时间
- Redis操作延迟
- 数据库查询时间
- 购物车转化率
```

### 3. 业务指标

```python
# 业务监控
- 购物车平均商品数量
- 购物车平均金额
- 购物车放弃率
- 热门商品统计
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1.0 | 2025-09-11 | 初始版本，实现基础购物车API功能 |

## 相关文档

- [Redis客户端模块](../redis/overview.md)
- [购物车业务模块](../shopping-cart/overview.md)
- [商品管理模块](../product-catalog/overview.md)
- [用户认证模块](../authentication/overview.md)
