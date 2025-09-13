# 购物车模块 (Shopping Cart Module)

## 模块概述

购物车模块是电商平台的核心交易模块，负责商品选择、数量管理、价格计算和订单准备。支持多设备同步、实时库存检查和智能推荐。

### 主要功能

1. **购物车管理**
   - 商品添加/删除/更新
   - 批量操作支持
   - 购物车持久化
   - 多设备同步

2. **价格计算**
   - 实时价格更新
   - 优惠券应用
   - 促销活动计算
   - 运费估算

3. **库存检查**
   - 实时库存验证
   - 库存预占机制
   - 缺货提醒
   - 替代商品推荐

## 技术架构

### 核心组件

```
shopping_cart/
├── router.py           # API路由定义
├── service.py          # 购物车业务逻辑
├── models.py           # 购物车数据模型(Cart, CartItem)
├── schemas.py          # 请求/响应数据模型  
├── dependencies.py     # 模块依赖注入
└── utils.py            # 购物车工具函数(价格计算、库存检查)
```

### 依赖的核心服务
```
app/core/
├── redis_client.py     # Redis缓存客户端
├── database.py         # 数据库连接管理
└── auth.py             # 用户认证中间件
```

### 集成的适配器
```
app/adapters/
└── inventory/          # 库存管理适配器(待开发)
    └── stock_adapter.py # 实时库存检查
    └── sync_utils.py           # 同步工具
```

### 数据存储设计

#### 关系型数据库 (持久化存储)

```sql
-- 购物车表
CREATE TABLE shopping_carts (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    guest_id VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    total_discount DECIMAL(10,2) DEFAULT 0.00,
    item_count INTEGER DEFAULT 0,
    
    CONSTRAINT cart_user_check CHECK (
        (user_id IS NOT NULL AND guest_id IS NULL) OR 
        (user_id IS NULL AND guest_id IS NOT NULL)
    )
);

-- 购物车项表
CREATE TABLE cart_items (
    id UUID PRIMARY KEY,
    cart_id UUID REFERENCES shopping_carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    sku_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    original_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    total_price DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(cart_id, sku_id)
);

-- 价格规则表
CREATE TABLE pricing_rules (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'discount', 'coupon', 'promotion'
    conditions JSONB NOT NULL,
    actions JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 优惠券使用记录
CREATE TABLE coupon_usage (
    id UUID PRIMARY KEY,
    cart_id UUID REFERENCES shopping_carts(id),
    coupon_code VARCHAR(50) NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Redis 缓存设计

```python
# 购物车缓存结构
cart:{user_id} = {
    "items": {
        "sku_123": {
            "product_id": "prod_456",
            "quantity": 2,
            "unit_price": 99.99,
            "added_at": "2024-01-01T10:00:00Z"
        }
    },
    "totals": {
        "subtotal": 199.98,
        "discount": 20.00,
        "total": 179.98,
        "item_count": 2
    },
    "updated_at": "2024-01-01T10:30:00Z",
    "expires_at": "2024-01-08T10:30:00Z"
}

# 库存缓存
inventory:{sku_id} = {
    "available": 100,
    "reserved": 20,
    "last_updated": "2024-01-01T10:00:00Z"
}

# 价格缓存
price:{sku_id} = {
    "base_price": 99.99,
    "current_price": 89.99,
    "discount_rules": ["rule_123", "rule_456"],
    "valid_until": "2024-01-01T12:00:00Z"
}
```

## API 接口

### 购物车操作

```yaml
/api/v1/cart:
  GET /:
    summary: 获取购物车
    security:
      - BearerAuth: []
    responses:
      200:
        description: 购物车详情
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Cart'

  POST /items:
    summary: 添加商品到购物车
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              sku_id:
                type: string
                format: uuid
              quantity:
                type: integer
                minimum: 1
                maximum: 99
    responses:
      201:
        description: 商品添加成功
      400:
        description: 请求参数错误
      409:
        description: 库存不足

  PUT /items/{item_id}:
    summary: 更新购物车商品
    security:
      - BearerAuth: []
    parameters:
      - name: item_id
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
            type: object
            properties:
              quantity:
                type: integer
                minimum: 1
                maximum: 99
    responses:
      200:
        description: 更新成功
      404:
        description: 商品不存在

  DELETE /items/{item_id}:
    summary: 删除购物车商品
    security:
      - BearerAuth: []
    parameters:
      - name: item_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: 删除成功

  POST /clear:
    summary: 清空购物车
    security:
      - BearerAuth: []
    responses:
      200:
        description: 清空成功

  POST /merge:
    summary: 合并游客购物车
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              guest_cart_id:
                type: string
                format: uuid
    responses:
      200:
        description: 合并成功
```

### 价格计算

```yaml
/api/v1/cart/pricing:
  POST /calculate:
    summary: 计算购物车价格
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              coupon_codes:
                type: array
                items:
                  type: string
              shipping_address:
                $ref: '#/components/schemas/Address'
    responses:
      200:
        description: 价格计算结果
        content:
          application/json:
            schema:
              type: object
              properties:
                subtotal:
                  type: number
                  format: decimal
                discount:
                  type: number
                  format: decimal
                shipping:
                  type: number
                  format: decimal
                tax:
                  type: number
                  format: decimal
                total:
                  type: number
                  format: decimal
                applied_coupons:
                  type: array
                  items:
                    type: object
                    properties:
                      code:
                        type: string
                      discount:
                        type: number
                        format: decimal
```

## 业务逻辑

### 价格计算引擎

```python
class PricingEngine:
    def __init__(self):
        self.rule_processors = {
            'discount': DiscountProcessor(),
            'coupon': CouponProcessor(),
            'promotion': PromotionProcessor(),
            'shipping': ShippingProcessor(),
            'tax': TaxProcessor()
        }
    
    def calculate_cart_total(self, cart: Cart, context: PricingContext) -> PricingResult:
        """
        计算购物车总价
        
        计算顺序:
        1. 商品原价汇总
        2. 应用商品级折扣
        3. 应用购物车级折扣
        4. 应用优惠券
        5. 计算运费
        6. 计算税费
        """
        result = PricingResult()
        
        # 1. 计算商品小计
        for item in cart.items:
            item_total = self._calculate_item_total(item, context)
            result.add_item_total(item_total)
        
        # 2. 应用购物车级规则
        cart_rules = self._get_applicable_rules(cart, context)
        for rule in sorted(cart_rules, key=lambda x: x.priority):
            processor = self.rule_processors[rule.rule_type]
            result = processor.apply(result, rule, context)
        
        # 3. 计算运费和税费
        result.shipping = self._calculate_shipping(cart, context)
        result.tax = self._calculate_tax(result.subtotal, context)
        result.total = result.subtotal - result.discount + result.shipping + result.tax
        
        return result
```

### 库存管理

```python
class InventoryManager:
    def __init__(self, redis_client, inventory_service):
        self.redis = redis_client
        self.inventory_service = inventory_service
    
    async def check_availability(self, sku_id: str, quantity: int) -> bool:
        """检查商品库存可用性"""
        # 1. 从缓存获取库存信息
        inventory = await self._get_cached_inventory(sku_id)
        
        if not inventory:
            # 2. 缓存未命中，从数据库获取
            inventory = await self.inventory_service.get_inventory(sku_id)
            await self._cache_inventory(sku_id, inventory)
        
        available = inventory['available'] - inventory['reserved']
        return available >= quantity
    
    async def reserve_inventory(self, sku_id: str, quantity: int, cart_id: str) -> bool:
        """预占库存"""
        lock_key = f"inventory_lock:{sku_id}"
        
        async with self.redis.lock(lock_key, timeout=30):
            if await self.check_availability(sku_id, quantity):
                # 更新预占数量
                await self.redis.hincrby(f"inventory:{sku_id}", "reserved", quantity)
                
                # 记录预占信息
                reservation = {
                    "cart_id": cart_id,
                    "quantity": quantity,
                    "reserved_at": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
                }
                await self.redis.hset(f"reservation:{cart_id}:{sku_id}", mapping=reservation)
                
                return True
        
        return False
```

### 多设备同步

```python
class CartSyncManager:
    def __init__(self, redis_client, event_publisher):
        self.redis = redis_client
        self.event_publisher = event_publisher
    
    async def sync_cart_update(self, user_id: str, cart_data: dict):
        """同步购物车更新到所有设备"""
        # 1. 更新缓存
        cache_key = f"cart:{user_id}"
        await self.redis.hset(cache_key, mapping=cart_data)
        
        # 2. 发布同步事件
        sync_event = {
            "event_type": "cart.updated",
            "user_id": user_id,
            "cart_data": cart_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.event_publisher.publish("cart.sync", sync_event)
    
    async def handle_offline_sync(self, user_id: str, device_id: str, offline_changes: list):
        """处理离线设备的同步"""
        current_cart = await self._get_current_cart(user_id)
        
        # 冲突解决策略: 最新时间戳优先
        merged_cart = self._merge_changes(current_cart, offline_changes)
        
        await self.sync_cart_update(user_id, merged_cart)
        
        return merged_cart
```

## 性能优化

### 缓存策略

1. **多级缓存**
   - L1: 应用内存缓存 (商品信息)
   - L2: Redis缓存 (购物车数据)
   - L3: 数据库 (持久化存储)

2. **缓存更新策略**
   - 购物车数据: Write-through
   - 商品价格: TTL + 主动刷新
   - 库存信息: 事件驱动更新

3. **缓存预热**
   - 热门商品价格预加载
   - 用户购物车预加载
   - 促销规则预计算

### 数据库优化

1. **索引策略**
   ```sql
   -- 购物车查询优化
   CREATE INDEX idx_carts_user_status ON shopping_carts(user_id, status);
   CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
   CREATE INDEX idx_cart_items_sku ON cart_items(sku_id);
   
   -- 价格规则查询优化
   CREATE INDEX idx_pricing_rules_active ON pricing_rules(is_active, start_date, end_date);
   ```

2. **分区策略**
   - 按用户ID哈希分区
   - 按时间范围分区 (历史数据)

## 监控指标

### 业务指标

- 购物车添加率
- 购物车放弃率
- 平均购物车价值
- 转化漏斗分析

### 技术指标

- API响应时间
- 缓存命中率
- 数据库连接池使用率
- 库存检查延迟

### 异常指标

- 库存超卖次数
- 价格计算错误
- 同步失败率
- 缓存穿透次数

## 事件处理

### 事件类型

```python
# 购物车事件
class CartEvents:
    ITEM_ADDED = "cart.item.added"
    ITEM_UPDATED = "cart.item.updated"
    ITEM_REMOVED = "cart.item.removed"
    CART_CLEARED = "cart.cleared"
    CART_ABANDONED = "cart.abandoned"
    CHECKOUT_STARTED = "cart.checkout.started"

# 库存事件
class InventoryEvents:
    STOCK_RESERVED = "inventory.reserved"
    STOCK_RELEASED = "inventory.released"
    STOCK_DEPLETED = "inventory.depleted"
    STOCK_REPLENISHED = "inventory.replenished"
```

### 事件处理器

```python
@event_handler(CartEvents.ITEM_ADDED)
async def handle_item_added(event_data):
    """处理商品添加事件"""
    # 1. 更新推荐算法
    await recommendation_service.update_user_preferences(
        event_data['user_id'], 
        event_data['product_id']
    )
    
    # 2. 检查库存预警
    await inventory_service.check_stock_levels(event_data['sku_id'])
    
    # 3. 触发个性化营销
    await marketing_service.trigger_cart_abandon_prevention(
        event_data['user_id']
    )

@event_handler(InventoryEvents.STOCK_DEPLETED)
async def handle_stock_depleted(event_data):
    """处理库存耗尽事件"""
    sku_id = event_data['sku_id']
    
    # 1. 通知相关购物车用户
    affected_carts = await cart_service.get_carts_with_sku(sku_id)
    for cart in affected_carts:
        await notification_service.send_stock_alert(cart.user_id, sku_id)
    
    # 2. 推荐替代商品
    alternatives = await product_service.get_alternatives(sku_id)
    await recommendation_service.push_alternatives(affected_carts, alternatives)
```

## 部署配置

### 环境变量

```bash
# Redis配置
CART_REDIS_URL=redis://localhost:6379/1
CART_CACHE_TTL=3600

# 数据库配置
CART_DB_URL=postgresql://user:pass@localhost/cart_db

# 库存服务配置
INVENTORY_SERVICE_URL=http://inventory-service:8080
INVENTORY_CHECK_TIMEOUT=5

# 价格服务配置
PRICING_SERVICE_URL=http://pricing-service:8080
PRICING_CACHE_TTL=1800

# 消息队列配置
MESSAGE_BROKER_URL=redis://localhost:6379/2
CART_SYNC_TOPIC=cart.sync
```

### 依赖服务

- Redis (缓存和消息队列)
- PostgreSQL (数据持久化)
- 库存服务 (库存检查)
- 商品服务 (商品信息)
- 用户服务 (用户认证)
- 推荐服务 (智能推荐)

## 相关文档

- [商品模块](../product-catalog/overview.md)
- [订单模块](../order-management/overview.md)
- [库存模块](../inventory/overview.md)
- [推荐系统](../recommendation/overview.md)
- [事件架构](../../architecture/event-driven.md)
