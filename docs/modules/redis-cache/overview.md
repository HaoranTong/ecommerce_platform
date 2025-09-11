# Redis客户端模块 (Redis Client Module)

## 模块概述

Redis客户端模块 (`app/redis_client.py`) 是电商平台的缓存和会话存储核心组件，负责Redis连接管理、购物车数据存储、缓存操作和高性能数据访问，提供分布式环境下的数据一致性支持。

### 主要功能

1. **连接管理**
   - Redis连接池管理
   - 异步连接支持
   - 连接生命周期控制
   - 配置驱动连接

2. **购物车管理**
   - 用户购物车存储
   - 商品数量管理
   - 购物车操作API
   - 数据持久化控制

3. **缓存服务**
   - 高性能数据缓存
   - 键值存储管理
   - 过期时间控制
   - 数据序列化支持

4. **会话存储**
   - 用户会话数据
   - 临时数据存储
   - 跨请求状态保持
   - 分布式会话支持

## 技术架构

### Redis架构图

```mermaid
graph TB
    A[Redis Client Module] --> B[Connection Manager]
    A --> C[Cart Manager]
    A --> D[Cache Service]
    A --> E[Session Store]
    
    B --> F[Redis Pool]
    C --> G[Hash Operations]
    D --> H[Key-Value Store]
    E --> I[User Sessions]
    
    F --> J[(Redis Server)]
    G --> J
    H --> J
    I --> J
    
    K[FastAPI App] --> A
    L[Background Tasks] --> A
    M[Scheduled Jobs] --> A
```

### 购物车数据结构

```mermaid
graph LR
    A[User Cart] --> B[cart:user:1001]
    B --> C[product:2001 -> quantity:2]
    B --> D[product:2002 -> quantity:1]
    B --> E[product:2003 -> quantity:3]
    
    F[TTL] --> B
    F --> G[7 days expiry]
```

## 代码结构

### 文件组织

```
app/redis_client.py
├── 配置管理
├── 连接管理函数
├── RedisCartManager类
│   ├── 初始化方法
│   ├── 内部工具方法
│   ├── 购物车操作方法
│   └── 统计查询方法
└── 全局实例
```

### 关键组件说明

#### 1. 连接管理

```python
# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 连接池管理
redis_pool: Optional[redis.Redis] = None

async def get_redis_connection() -> redis.Redis:
    """获取Redis连接 - 单例模式"""
    global redis_pool
    if redis_pool is None:
        redis_pool = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_pool
```

**设计特点:**
- 单例连接池，避免重复连接
- 环境变量驱动配置
- 自动字符串解码
- 异步连接支持

#### 2. 购物车管理器

```python
class RedisCartManager:
    """Redis购物车管理器 - 完整的购物车操作封装"""
    
    def _get_cart_key(self, user_id: int) -> str:
        """生成购物车Redis key"""
        return f"cart:user:{user_id}"
    
    def _get_cart_item_key(self, user_id: int, product_id: int) -> str:
        """生成购物车商品Redis key"""
        return f"cart:user:{user_id}:product:{product_id}"
```

**键命名规范:**
- `cart:user:{user_id}`: 用户购物车哈希表
- `cart:user:{user_id}:product:{product_id}`: 购物车商品键 (备用)
- 层次化命名，便于管理和查询

#### 3. 数据存储模式

```
Redis Hash结构:
Key: cart:user:1001
Fields:
├── "2001" -> "2"    (product_id -> quantity)
├── "2002" -> "1"
└── "2003" -> "3"
TTL: 604800 (7天)
```

**存储优势:**
- Hash结构节省内存
- 原子操作支持
- 字段级别操作
- 自动过期管理

## API接口

### 连接管理函数

| 函数名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `get_redis_connection` | 无 | `redis.Redis` | 获取Redis连接实例 |
| `close_redis_connection` | 无 | `None` | 关闭Redis连接 |

### RedisCartManager方法

#### 商品操作

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `add_item` | `user_id: int`<br>`product_id: int`<br>`quantity: int` | `bool` | 添加商品到购物车 |
| `update_item_quantity` | `user_id: int`<br>`product_id: int`<br>`quantity: int` | `bool` | 更新商品数量 |
| `remove_item` | `user_id: int`<br>`product_id: int` | `bool` | 移除购物车商品 |

#### 查询操作

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `get_cart_items` | `user_id: int` | `Dict[str, int]` | 获取购物车所有商品 |
| `get_item_quantity` | `user_id: int`<br>`product_id: int` | `int` | 获取特定商品数量 |
| `get_cart_count` | `user_id: int` | `int` | 获取购物车商品种类数 |
| `get_cart_total_quantity` | `user_id: int` | `int` | 获取购物车商品总数量 |

#### 管理操作

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `clear_cart` | `user_id: int` | `bool` | 清空购物车 |

## 使用示例

### 1. 基础连接使用

```python
from app.redis_client import get_redis_connection

async def cache_user_data(user_id: int, user_data: dict):
    """缓存用户数据"""
    redis = await get_redis_connection()
    
    # 存储用户数据，5分钟过期
    await redis.setex(
        f"user:{user_id}",
        300,
        json.dumps(user_data)
    )

async def get_cached_user_data(user_id: int) -> Optional[dict]:
    """获取缓存的用户数据"""
    redis = await get_redis_connection()
    
    cached_data = await redis.get(f"user:{user_id}")
    if cached_data:
        return json.loads(cached_data)
    return None
```

### 2. 购物车操作

```python
from app.redis_client import cart_manager

@app.post("/cart/add")
async def add_to_cart(
    item: CartItemAdd,
    current_user: User = Depends(get_current_user)
):
    """添加商品到购物车"""
    success = await cart_manager.add_item(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="添加商品失败")
    
    # 返回购物车摘要
    cart_items = await cart_manager.get_cart_items(current_user.id)
    total_quantity = await cart_manager.get_cart_total_quantity(current_user.id)
    
    return {
        "message": "商品添加成功",
        "cart_count": len(cart_items),
        "total_quantity": total_quantity
    }

@app.get("/cart")
async def get_cart(current_user: User = Depends(get_current_user)):
    """获取购物车内容"""
    cart_items = await cart_manager.get_cart_items(current_user.id)
    
    # 获取商品详细信息
    cart_details = []
    for product_id, quantity in cart_items.items():
        # 从数据库获取商品信息 (可以加缓存优化)
        product = db.query(Product).filter(Product.id == int(product_id)).first()
        if product:
            cart_details.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": float(product.price),
                "quantity": quantity,
                "subtotal": float(product.price) * quantity
            })
    
    total_amount = sum(item["subtotal"] for item in cart_details)
    
    return {
        "items": cart_details,
        "total_amount": total_amount,
        "item_count": len(cart_details)
    }
```

### 3. 购物车管理

```python
@app.put("/cart/update")
async def update_cart_item(
    item: CartItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新购物车商品数量"""
    success = await cart_manager.update_item_quantity(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="更新失败")
    
    return {"message": "更新成功"}

@app.delete("/cart/clear")
async def clear_cart(current_user: User = Depends(get_current_user)):
    """清空购物车"""
    success = await cart_manager.clear_cart(current_user.id)
    
    if not success:
        raise HTTPException(status_code=500, detail="清空失败")
    
    return {"message": "购物车已清空"}

@app.delete("/cart/items/{product_id}")
async def remove_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user)
):
    """移除购物车商品"""
    success = await cart_manager.remove_item(
        user_id=current_user.id,
        product_id=product_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="商品不在购物车中")
    
    return {"message": "商品已移除"}
```

### 4. 批量操作

```python
async def batch_add_to_cart(user_id: int, items: List[dict]) -> bool:
    """批量添加商品到购物车"""
    try:
        for item in items:
            success = await cart_manager.add_item(
                user_id=user_id,
                product_id=item["product_id"],
                quantity=item["quantity"]
            )
            if not success:
                return False
        return True
    except Exception:
        return False

async def sync_cart_from_local(user_id: int, local_cart: dict) -> bool:
    """从本地购物车同步到Redis"""
    try:
        # 先清空现有购物车
        await cart_manager.clear_cart(user_id)
        
        # 批量添加商品
        for product_id, quantity in local_cart.items():
            await cart_manager.add_item(
                user_id=user_id,
                product_id=int(product_id),
                quantity=quantity
            )
        
        return True
    except Exception:
        return False
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 描述 | 示例 |
|--------|--------|------|------|
| `REDIS_URL` | `"redis://localhost:6379/0"` | Redis连接字符串 | `"redis://user:pass@host:port/db"` |

### 连接字符串格式

```
redis://[username:password@]host:port[/database]
```

**组成部分:**
- `redis://`: 协议标识
- `username:password@`: 认证信息 (可选)
- `host`: Redis服务器地址
- `port`: Redis端口号
- `/database`: 数据库编号 (0-15)

### 环境配置示例

#### 开发环境
```bash
export REDIS_URL="redis://localhost:6379/0"
```

#### 生产环境
```bash
export REDIS_URL="redis://redis_user:${REDIS_PASSWORD}@redis-cluster:6379/0"
```

#### 集群环境
```bash
export REDIS_URL="redis://redis-sentinel:26379/0"
```

## 数据模型

### 购物车数据结构

```json
{
  "cart:user:1001": {
    "2001": "2",    // iPhone 15 Pro x2
    "2002": "1",    // MacBook Pro x1
    "2003": "3"     // AirPods x3
  },
  "TTL": 604800     // 7天过期
}
```

### 缓存键命名规范

| 键模式 | 用途 | 示例 | TTL |
|--------|------|------|-----|
| `cart:user:{user_id}` | 用户购物车 | `cart:user:1001` | 7天 |
| `user:{user_id}` | 用户缓存 | `user:1001` | 5分钟 |
| `product:{product_id}` | 商品缓存 | `product:2001` | 1小时 |
| `session:{session_id}` | 用户会话 | `session:abc123` | 30分钟 |

## 性能优化

### 1. 连接池优化

```python
# 优化连接配置
redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,        # 最大连接数
    socket_keepalive=True,     # 保持连接活跃
    socket_keepalive_options={ # TCP Keep-Alive参数
        'TCP_KEEPINTVL': 1,
        'TCP_KEEPCNT': 3,
        'TCP_KEEPIDLE': 1,
    },
    decode_responses=True,     # 自动解码响应
    retry_on_timeout=True,     # 超时重试
)
```

### 2. 批量操作优化

```python
async def batch_get_cart_details(user_ids: List[int]) -> Dict[int, dict]:
    """批量获取多个用户的购物车详情"""
    redis = await get_redis_connection()
    
    # 使用pipeline批量操作
    pipeline = redis.pipeline()
    
    for user_id in user_ids:
        cart_key = f"cart:user:{user_id}"
        pipeline.hgetall(cart_key)
    
    results = await pipeline.execute()
    
    # 处理结果
    cart_details = {}
    for i, user_id in enumerate(user_ids):
        items = results[i]
        cart_details[user_id] = {
            product_id: int(quantity) 
            for product_id, quantity in items.items()
        }
    
    return cart_details
```

### 3. 缓存预热

```python
async def preload_hot_products(product_ids: List[int]):
    """预加载热门商品到缓存"""
    redis = await get_redis_connection()
    session = SessionLocal()
    
    try:
        # 批量查询商品
        products = session.query(Product).filter(
            Product.id.in_(product_ids)
        ).all()
        
        # 批量缓存
        pipeline = redis.pipeline()
        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity
            }
            pipeline.setex(
                f"product:{product.id}",
                3600,  # 1小时缓存
                json.dumps(product_data)
            )
        
        await pipeline.execute()
        
    finally:
        session.close()
```

## 监控和调试

### 1. Redis性能监控

```python
import time
from functools import wraps

def monitor_redis_performance(func):
    """Redis操作性能监控"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 0.01:  # 慢操作阈值10ms
                print(f"慢Redis操作: {func.__name__} 耗时 {duration:.3f}s")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"Redis操作失败: {func.__name__} 耗时 {duration:.3f}s, 错误: {e}")
            raise
    
    return wrapper
```

### 2. 连接状态检查

```python
async def check_redis_health() -> dict:
    """检查Redis连接健康状态"""
    try:
        redis = await get_redis_connection()
        
        # 测试连接
        await redis.ping()
        
        # 获取Redis信息
        info = await redis.info()
        
        return {
            "status": "healthy",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "unknown"),
            "uptime": info.get("uptime_in_seconds", 0),
            "version": info.get("redis_version", "unknown")
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### 3. 购物车统计

```python
async def get_cart_statistics() -> dict:
    """获取购物车使用统计"""
    redis = await get_redis_connection()
    
    # 扫描所有购物车键
    cart_keys = []
    async for key in redis.scan_iter(match="cart:user:*"):
        cart_keys.append(key)
    
    # 统计信息
    total_carts = len(cart_keys)
    non_empty_carts = 0
    total_items = 0
    
    for cart_key in cart_keys:
        cart_size = await redis.hlen(cart_key)
        if cart_size > 0:
            non_empty_carts += 1
            cart_items = await redis.hgetall(cart_key)
            total_items += sum(int(qty) for qty in cart_items.values())
    
    return {
        "total_carts": total_carts,
        "non_empty_carts": non_empty_carts,
        "total_items": total_items,
        "avg_items_per_cart": total_items / non_empty_carts if non_empty_carts > 0 else 0
    }
```

## 安全考虑

### 1. 访问控制

```python
def validate_user_access(user_id: int, current_user: User) -> bool:
    """验证用户访问权限"""
    # 用户只能访问自己的购物车
    if user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="无权访问其他用户的购物车"
        )
    return True

async def secure_cart_operation(user_id: int, current_user: User, operation):
    """安全的购物车操作"""
    validate_user_access(user_id, current_user)
    return await operation()
```

### 2. 数据验证

```python
def validate_cart_data(product_id: int, quantity: int) -> bool:
    """验证购物车数据"""
    if product_id <= 0:
        raise ValueError("商品ID必须大于0")
    
    if quantity < 0:
        raise ValueError("数量不能为负数")
    
    if quantity > 999:
        raise ValueError("单个商品数量不能超过999")
    
    return True
```

### 3. Redis安全配置

```bash
# Redis配置文件安全设置
requirepass your-redis-password
bind 127.0.0.1
protected-mode yes
rename-command FLUSHDB ""
rename-command FLUSHALL ""
```

## 故障排除

### 常见问题

1. **连接失败**
   ```
   redis.exceptions.ConnectionError: Error connecting to Redis
   ```
   **解决方案:**
   - 检查Redis服务状态
   - 验证连接配置
   - 确认网络连通性

2. **数据序列化错误**
   ```
   json.JSONDecodeError: Expecting value
   ```
   **解决方案:**
   - 检查存储的数据格式
   - 验证编码设置
   - 清理损坏的缓存数据

3. **内存不足**
   ```
   redis.exceptions.ResponseError: OOM command not allowed
   ```
   **解决方案:**
   - 增加Redis内存限制
   - 清理过期数据
   - 优化数据结构

### 调试工具

```python
async def debug_cart_data(user_id: int):
    """调试购物车数据"""
    redis = await get_redis_connection()
    cart_key = f"cart:user:{user_id}"
    
    # 检查键是否存在
    exists = await redis.exists(cart_key)
    print(f"购物车键存在: {exists}")
    
    if exists:
        # 获取TTL
        ttl = await redis.ttl(cart_key)
        print(f"过期时间: {ttl}秒")
        
        # 获取所有数据
        cart_data = await redis.hgetall(cart_key)
        print(f"购物车数据: {cart_data}")
        
        # 获取字段数量
        field_count = await redis.hlen(cart_key)
        print(f"商品种类数: {field_count}")
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1.0 | 2025-09-11 | 初始版本，实现Redis购物车管理 |

## 相关文档

- [购物车模块文档](../shopping-cart/overview.md)
- [缓存策略文档](../../architecture/performance.md#缓存策略)
- [Redis官方文档](https://redis.io/documentation)
- [redis-py异步文档](https://redis-py.readthedocs.io/en/stable/)
