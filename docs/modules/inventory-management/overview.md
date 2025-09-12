# 库存管理模块 (Inventory Management Module)

## 模块概述

库存管理模块负责商品库存的实时跟踪、预占机制、补货预警和库存同步。确保库存数据的准确性和一致性，防止超卖现象。

### 主要功能

1. **库存跟踪**
   - 实时库存监控
   - 库存变更日志
   - 多维度库存视图 (可用、预占、总量)
   - 商品库存状态管理

2. **预占机制**
   - 购物车预占
   - 订单库存锁定
   - 预占超时释放
   - 库存回滚机制

3. **库存管理**
   - 管理员库存调整
   - 库存预警设置
   - 低库存商品监控
   - 库存变动历史追踪

4. **系统集成**
   - 与购物车模块集成
   - 与订单模块集成
   - 与商品模块集成
   - Redis缓存支持

## 技术架构

### 核心组件

```
inventory/
├── models/
│   ├── inventory.py              # 库存数据模型
│   ├── inventory_transaction.py  # 库存交易记录模型
│   └── cart_reservation.py       # 购物车预占模型
├── services/
│   └── inventory_service.py      # 库存业务逻辑服务
├── schemas/
│   └── inventory.py              # 库存数据传输对象
└── api/
    └── inventory_routes.py       # 库存API路由
```

### 数据库设计

#### 1. 库存主表 (inventory)
```sql
CREATE TABLE inventory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL COMMENT '商品ID',
    available_quantity INT NOT NULL DEFAULT 0 COMMENT '可用库存数量',
    reserved_quantity INT NOT NULL DEFAULT 0 COMMENT '预占库存数量', 
    total_quantity INT NOT NULL DEFAULT 0 COMMENT '总库存数量',
    warning_threshold INT NOT NULL DEFAULT 10 COMMENT '预警阈值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY uk_product_id (product_id),
    INDEX idx_available_quantity (available_quantity),
    INDEX idx_total_quantity (total_quantity)
);
```

#### 2. 库存交易记录表 (inventory_transactions)
```sql
CREATE TABLE inventory_transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL COMMENT '商品ID',
    transaction_type ENUM('purchase', 'sale', 'adjustment', 'reserve', 'release', 'deduct') NOT NULL COMMENT '交易类型',
    quantity INT NOT NULL COMMENT '数量变化',
    reference_id VARCHAR(100) COMMENT '关联业务ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_id (product_id),
    INDEX idx_transaction_type (transaction_type),
    INDEX idx_created_at (created_at),
    INDEX idx_reference_id (reference_id)
);
```

#### 3. 购物车预占表 (cart_reservations)
```sql
CREATE TABLE cart_reservations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    product_id BIGINT NOT NULL COMMENT '商品ID',
    reserved_quantity INT NOT NULL COMMENT '预占数量',
    expires_at TIMESTAMP NOT NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_expires_at (expires_at)
);
```

### Redis 缓存设计

#### 缓存策略
```python
# 库存缓存 (TTL: 60秒)
inventory:product:{product_id} = {
    "available_quantity": 50,
    "reserved_quantity": 10,
    "total_quantity": 60,
    "is_low_stock": false
}

# 低库存商品缓存 (TTL: 300秒)  
inventory:low_stock = [1001, 1002, 1003]

# 预占记录缓存 (TTL: 1800秒)
inventory:reservation:cart:{user_id} = {
    "items": [
        {"product_id": 1001, "quantity": 2}
    ],
    "expires_at": "2024-12-19T11:00:00Z"
}
```

## API 接口

库存管理模块提供完整的库存操作API，详细的接口规范请参考 [API规范文档](api-spec.md)。

### 主要接口分类

#### 1. 库存查询接口
- `GET /api/inventory/{product_id}` - 获取商品库存信息
- `POST /api/inventory/batch` - 批量获取商品库存

#### 2. 库存预占接口  
- `POST /api/inventory/reserve/cart` - 购物车库存预占
- `POST /api/inventory/reserve/order` - 订单库存预占
- `DELETE /api/inventory/reserve/cart` - 释放购物车预占
- `DELETE /api/inventory/reserve/order/{order_id}` - 释放订单预占

#### 3. 库存扣减接口
- `POST /api/inventory/deduct` - 订单完成库存扣减

#### 4. 库存管理接口（管理员）
- `PUT /api/inventory/{product_id}/adjust` - 库存调整
- `PUT /api/inventory/{product_id}/threshold` - 设置预警阈值
- `GET /api/inventory/low-stock` - 获取低库存商品列表

#### 5. 库存历史接口
- `GET /api/inventory/{product_id}/transactions` - 获取库存变动历史

#### 6. 系统维护接口
- `POST /api/inventory/cleanup/expired-reservations` - 清理过期预占

### API 设计特点

#### 数据模型
- **基于商品ID**: 使用 `product_id` 作为主要标识符
- **简化设计**: 适合中小型电商平台的库存管理需求
- **实时同步**: 库存数据实时更新，确保准确性

#### 权限控制
- **用户级接口**: 库存查询、预占操作
- **管理员接口**: 库存调整、阈值设置、历史查询
- **系统内部**: 库存扣减、过期清理

#### 性能优化
- **Redis缓存**: 热门商品库存缓存
- **批量操作**: 支持批量库存查询
- **异步处理**: 过期预占自动清理

## 业务流程

### 购物车预占流程
```mermaid
sequenceDiagram
    participant User as 用户
    participant Cart as 购物车
    participant Inventory as 库存服务
    participant Redis as Redis缓存
    
    User->>Cart: 添加商品到购物车
    Cart->>Inventory: 请求库存预占
    Inventory->>Inventory: 检查库存可用性
    Inventory->>Redis: 更新缓存
    Inventory->>Cart: 返回预占结果
    Cart->>User: 显示购物车状态
    
    Note over Inventory: 30分钟后自动释放预占
```

### 订单库存扣减流程
```mermaid
sequenceDiagram
    participant Order as 订单服务
    participant Payment as 支付服务
    participant Inventory as 库存服务
    participant DB as 数据库
    
    Order->>Inventory: 创建订单预占
    Inventory->>DB: 记录预占信息
    Payment->>Order: 支付成功通知
    Order->>Inventory: 执行库存扣减
    Inventory->>DB: 更新库存数据
    Inventory->>Order: 扣减完成确认
```

### 库存调整流程
```mermaid
sequenceDiagram
    participant Admin as 管理员
    participant Inventory as 库存服务
    participant DB as 数据库
    participant Redis as Redis缓存
    
    Admin->>Inventory: 提交库存调整
    Inventory->>DB: 更新库存数量
    Inventory->>DB: 记录调整历史
    Inventory->>Redis: 清除缓存
    Inventory->>Admin: 返回调整结果
```

## 核心服务

### InventoryService 核心方法

```python
class InventoryService:
    def get_or_create_inventory(self, product_id: int) -> Inventory
    def get_inventories_batch(self, product_ids: List[int]) -> List[Inventory]
    def reserve_for_cart(self, user_id: int, items: List[CartItem], expires_minutes: int) -> ReservationResponse
    def reserve_for_order(self, order_id: int, items: List[OrderItem]) -> ReservationResponse
    def release_cart_reservations(self, user_id: int) -> ReleaseResult
    def release_order_reservations(self, order_id: int) -> ReleaseResult
    def deduct_inventory(self, order_id: int, items: List[OrderItem]) -> DeductResult
    def adjust_inventory(self, product_id: int, adjustment: InventoryAdjustment) -> Inventory
    def set_warning_threshold(self, product_id: int, threshold: int) -> Inventory
    def get_low_stock_products(self, filters: LowStockQuery) -> PaginatedResponse
    def get_inventory_transactions(self, product_id: int, filters: TransactionQuery) -> PaginatedResponse
    def cleanup_expired_reservations(self) -> CleanupResult
```

## 配置说明

### 环境变量配置
```bash
# 库存预占过期时间（分钟）
INVENTORY_CART_RESERVATION_MINUTES=30
INVENTORY_ORDER_RESERVATION_MINUTES=60

# 库存缓存配置
INVENTORY_CACHE_TTL=60
LOW_STOCK_CACHE_TTL=300

# 批量操作限制
INVENTORY_BATCH_QUERY_LIMIT=100

# 清理任务配置
INVENTORY_CLEANUP_INTERVAL_MINUTES=10
```

### Redis配置
```bash
# Redis连接配置
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_password
REDIS_DB=0
```

## 监控与运维

### 关键指标
- **库存准确率**: 实际库存与系统库存的一致性
- **预占成功率**: 库存预占操作的成功率
- **响应时间**: API接口响应时间
- **并发处理**: 高并发下的系统稳定性

### 日志记录
- 所有库存变动操作记录详细日志
- 预占和扣减操作的审计记录
- 系统异常和错误日志

### 定时任务
- 过期预占自动清理（每10分钟）
- 低库存商品检查（每小时）
- 库存数据一致性检查（每日）

---

**文档关联**:
- [API规范文档](api-spec.md) - 详细的API接口定义
- [购物车模块](../shopping-cart/overview.md) - 库存预占集成
- [订单管理模块](../order-management/overview.md) - 库存扣减集成
- [商品目录模块](../product-catalog/overview.md) - 商品库存关联
│   ├── inventory.py               # 库存模型
│   ├── warehouse.py               # 仓库模型
│   ├── reservation.py             # 预占模型
│   ├── movement.py                # 库存变动模型
│   └── replenishment.py           # 补货模型
├── events/
│   ├── inventory_events.py        # 库存事件
│   └── allocation_events.py       # 分配事件
└── utils/
    ├── allocation_utils.py        # 分配算法工具
    ├── forecast_utils.py          # 预测工具
    └── sync_utils.py              # 同步工具
```

### 数据库设计

```sql
-- 仓库表
CREATE TABLE warehouses (
    id UUID PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'main', 'regional', 'local'
    address JSONB NOT NULL,
    capacity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 库存表
CREATE TABLE inventory (
    id UUID PRIMARY KEY,
    warehouse_id UUID REFERENCES warehouses(id),
    sku_id UUID NOT NULL,
    available_quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,
    in_transit_quantity INTEGER NOT NULL DEFAULT 0,
    safety_stock INTEGER NOT NULL DEFAULT 0,
    reorder_point INTEGER NOT NULL DEFAULT 0,
    max_stock INTEGER,
    cost_price DECIMAL(10,2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(warehouse_id, sku_id),
    CONSTRAINT inventory_quantity_check CHECK (
        available_quantity >= 0 AND 
        reserved_quantity >= 0 AND 
        in_transit_quantity >= 0
    )
);

-- 库存预占表
CREATE TABLE inventory_reservations (
    id UUID PRIMARY KEY,
    warehouse_id UUID REFERENCES warehouses(id),
    sku_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    reservation_type VARCHAR(20) NOT NULL, -- 'cart', 'order', 'manual'
    reference_id UUID NOT NULL, -- 购物车ID或订单ID
    reserved_by UUID, -- 用户ID
    reserved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'consumed', 'expired', 'cancelled'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 库存变动记录表
CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY,
    warehouse_id UUID REFERENCES warehouses(id),
    sku_id UUID NOT NULL,
    movement_type VARCHAR(20) NOT NULL, -- 'in', 'out', 'transfer', 'adjustment'
    quantity INTEGER NOT NULL,
    reference_type VARCHAR(20), -- 'purchase', 'sale', 'transfer', 'adjustment'
    reference_id UUID,
    reason VARCHAR(200),
    cost_price DECIMAL(10,2),
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT movement_quantity_check CHECK (
        (movement_type = 'in' AND quantity > 0) OR
        (movement_type = 'out' AND quantity < 0) OR
        movement_type IN ('transfer', 'adjustment')
    )
);

-- 补货建议表
CREATE TABLE replenishment_suggestions (
    id UUID PRIMARY KEY,
    warehouse_id UUID REFERENCES warehouses(id),
    sku_id UUID NOT NULL,
    current_stock INTEGER NOT NULL,
    suggested_quantity INTEGER NOT NULL,
    priority VARCHAR(10) NOT NULL, -- 'low', 'medium', 'high', 'urgent'
    reason TEXT,
    supplier_id UUID,
    estimated_cost DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'ordered', 'received', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID
);

-- 库存批次表 (可选，用于批次管理)
CREATE TABLE inventory_batches (
    id UUID PRIMARY KEY,
    warehouse_id UUID REFERENCES warehouses(id),
    sku_id UUID NOT NULL,
    batch_number VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    production_date DATE,
    expiry_date DATE,
    cost_price DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(warehouse_id, sku_id, batch_number)
);
```

### Redis 缓存设计

```python
# 库存缓存结构
inventory:{warehouse_id}:{sku_id} = {
    "available": 100,
    "reserved": 20,
    "in_transit": 10,
    "last_updated": "2024-01-01T10:00:00Z"
}

# 预占缓存
reservation:{reference_id}:{sku_id} = {
    "quantity": 5,
    "warehouse_id": "warehouse_123",
    "expires_at": "2024-01-01T10:30:00Z",
    "status": "active"
}

# 全局库存汇总
global_inventory:{sku_id} = {
    "total_available": 500,
    "total_reserved": 100,
    "warehouses": {
        "warehouse_1": {"available": 200, "reserved": 50},
        "warehouse_2": {"available": 300, "reserved": 50}
    },
    "last_updated": "2024-01-01T10:00:00Z"
}

# 预警库存列表
low_stock_alerts = [
    {
        "sku_id": "sku_123",
        "warehouse_id": "warehouse_1",
        "current": 5,
        "reorder_point": 10,
        "priority": "high"
    }
]
```

## API 接口

库存管理模块提供完整的库存操作API，详细的接口规范请参考 [API规范文档](api-spec.md)。

### 主要接口分类

#### 1. 库存查询接口
- `GET /api/inventory/{product_id}` - 获取商品库存信息
- `POST /api/inventory/batch` - 批量获取商品库存

#### 2. 库存预占接口  
- `POST /api/inventory/reserve/cart` - 购物车库存预占
- `POST /api/inventory/reserve/order` - 订单库存预占
- `DELETE /api/inventory/reserve/cart` - 释放购物车预占
- `DELETE /api/inventory/reserve/order/{order_id}` - 释放订单预占

#### 3. 库存扣减接口
- `POST /api/inventory/deduct` - 订单完成库存扣减

#### 4. 库存管理接口（管理员）
- `PUT /api/inventory/{product_id}/adjust` - 库存调整
- `PUT /api/inventory/{product_id}/threshold` - 设置预警阈值
- `GET /api/inventory/low-stock` - 获取低库存商品列表

#### 5. 库存历史接口
- `GET /api/inventory/{product_id}/transactions` - 获取库存变动历史

#### 6. 系统维护接口
- `POST /api/inventory/cleanup/expired-reservations` - 清理过期预占

### API 设计特点

#### 数据模型
- **基于商品ID**: 使用 `product_id` 作为主要标识符
- **简化设计**: 适合中小型电商平台的库存管理需求
- **实时同步**: 库存数据实时更新，确保准确性

#### 权限控制
- **用户级接口**: 库存查询、预占操作
- **管理员接口**: 库存调整、阈值设置、历史查询
- **系统内部**: 库存扣减、过期清理

#### 性能优化
- **Redis缓存**: 热门商品库存缓存
- **批量操作**: 支持批量库存查询
- **异步处理**: 过期预占自动清理
                      type: integer
                      minimum: 1
                    warehouse_id:
                      type: string
                      format: uuid
              reference_type:
                type: string
                enum: [cart, order]
              reference_id:
                type: string
                format: uuid
              expires_in_minutes:
                type: integer
                default: 30
    responses:
      201:
        description: 预占创建成功
        content:
          application/json:
            schema:
              type: object
              properties:
                reservation_id:
                  type: string
                  format: uuid
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      sku_id:
                        type: string
                      reserved_quantity:
                        type: integer
                      warehouse_id:
                        type: string

  PUT /{reservation_id}/extend:
    summary: 延长预占时间
    security:
      - BearerAuth: []
    parameters:
      - name: reservation_id
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
              additional_minutes:
                type: integer
                minimum: 1
                maximum: 60
    responses:
      200:
        description: 延长成功

  DELETE /{reservation_id}:
    summary: 取消预占
    security:
      - BearerAuth: []
    parameters:
      - name: reservation_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: 取消成功
```

## 业务逻辑

### 库存预占服务

```python
class InventoryReservationService:
    def __init__(self, db, redis_client, event_publisher):
        self.db = db
        self.redis = redis_client
        self.event_publisher = event_publisher
    
    async def reserve_inventory(self, reservation_request: ReservationRequest) -> ReservationResult:
        """
        库存预占
        1. 检查库存可用性
        2. 创建预占记录
        3. 更新库存状态
        4. 设置过期时间
        """
        reservation_id = str(uuid.uuid4())
        reserved_items = []
        
        async with self.db.transaction():
            for item in reservation_request.items:
                # 检查库存
                available = await self._check_availability(
                    item.sku_id, 
                    item.quantity, 
                    item.warehouse_id
                )
                
                if not available:
                    # 回滚已预占的库存
                    await self._rollback_reservations(reserved_items)
                    raise InsufficientInventoryError(item.sku_id)
                
                # 创建预占记录
                reservation = await self.db.create_reservation(
                    warehouse_id=item.warehouse_id,
                    sku_id=item.sku_id,
                    quantity=item.quantity,
                    reservation_type=reservation_request.reference_type,
                    reference_id=reservation_request.reference_id,
                    expires_at=datetime.utcnow() + timedelta(
                        minutes=reservation_request.expires_in_minutes
                    )
                )
                
                # 更新库存
                await self.db.update_inventory_reserved(
                    item.warehouse_id,
                    item.sku_id,
                    item.quantity
                )
                
                # 更新缓存
                await self._update_inventory_cache(
                    item.warehouse_id,
                    item.sku_id,
                    available_delta=-item.quantity,
                    reserved_delta=item.quantity
                )
                
                reserved_items.append(reservation)
        
        # 设置过期处理
        await self._schedule_expiration(reservation_id, reservation_request.expires_in_minutes)
        
        # 发布事件
        await self.event_publisher.publish('inventory.reserved', {
            'reservation_id': reservation_id,
            'items': [
                {
                    'sku_id': item.sku_id,
                    'quantity': item.quantity,
                    'warehouse_id': item.warehouse_id
                }
                for item in reserved_items
            ],
            'reference_type': reservation_request.reference_type,
            'reference_id': reservation_request.reference_id
        })
        
        return ReservationResult(
            reservation_id=reservation_id,
            items=reserved_items
        )
    
    async def consume_reservation(self, reservation_id: str) -> bool:
        """
        消费预占库存 (订单确认时调用)
        """
        async with self.db.transaction():
            reservations = await self.db.get_active_reservations(reservation_id)
            
            for reservation in reservations:
                # 更新预占状态
                await self.db.update_reservation_status(
                    reservation.id, 
                    'consumed'
                )
                
                # 减少预占数量，减少可用库存
                await self.db.update_inventory_consumed(
                    reservation.warehouse_id,
                    reservation.sku_id,
                    reservation.quantity
                )
                
                # 记录库存变动
                await self.db.create_inventory_movement(
                    warehouse_id=reservation.warehouse_id,
                    sku_id=reservation.sku_id,
                    movement_type='out',
                    quantity=-reservation.quantity,
                    reference_type='order',
                    reference_id=reservation.reference_id
                )
                
                # 更新缓存
                await self._update_inventory_cache(
                    reservation.warehouse_id,
                    reservation.sku_id,
                    reserved_delta=-reservation.quantity
                )
        
        return True
    
    async def release_expired_reservations(self):
        """
        释放过期预占 (定时任务)
        """
        expired_reservations = await self.db.get_expired_reservations()
        
        for reservation in expired_reservations:
            async with self.db.transaction():
                # 更新预占状态
                await self.db.update_reservation_status(
                    reservation.id, 
                    'expired'
                )
                
                # 释放预占库存
                await self.db.update_inventory_reserved(
                    reservation.warehouse_id,
                    reservation.sku_id,
                    -reservation.quantity
                )
                
                # 更新缓存
                await self._update_inventory_cache(
                    reservation.warehouse_id,
                    reservation.sku_id,
                    available_delta=reservation.quantity,
                    reserved_delta=-reservation.quantity
                )
```

### 库存分配算法

```python
class InventoryAllocationService:
    def __init__(self, db):
        self.db = db
    
    async def allocate_inventory(self, order_items: List[OrderItem], shipping_address: Address) -> AllocationResult:
        """
        库存分配算法
        1. 就近发货优先
        2. 库存充足度考虑
        3. 仓库优先级考虑
        4. 最小拆分原则
        """
        allocation_plan = []
        
        for item in order_items:
            # 获取所有有库存的仓库
            warehouses_with_stock = await self.db.get_warehouses_with_stock(
                item.sku_id, 
                item.quantity
            )
            
            if not warehouses_with_stock:
                raise InsufficientInventoryError(item.sku_id)
            
            # 计算仓库距离
            warehouses_with_distance = []
            for warehouse in warehouses_with_stock:
                distance = self._calculate_distance(
                    warehouse.address, 
                    shipping_address
                )
                warehouses_with_distance.append((warehouse, distance))
            
            # 分配策略
            allocation = await self._allocate_item(
                item, 
                warehouses_with_distance
            )
            
            allocation_plan.extend(allocation)
        
        return AllocationResult(allocation_plan)
    
    async def _allocate_item(self, item: OrderItem, warehouses_with_distance: List) -> List[Allocation]:
        """
        单个商品分配算法
        """
        # 按距离和优先级排序
        sorted_warehouses = sorted(
            warehouses_with_distance,
            key=lambda x: (x[1], -x[0].priority)  # 距离升序，优先级降序
        )
        
        allocations = []
        remaining_quantity = item.quantity
        
        for warehouse, distance in sorted_warehouses:
            if remaining_quantity <= 0:
                break
            
            # 获取该仓库的可用库存
            available = await self.db.get_available_inventory(
                warehouse.id, 
                item.sku_id
            )
            
            if available > 0:
                allocated_quantity = min(available, remaining_quantity)
                
                allocations.append(Allocation(
                    warehouse_id=warehouse.id,
                    sku_id=item.sku_id,
                    quantity=allocated_quantity,
                    distance=distance
                ))
                
                remaining_quantity -= allocated_quantity
        
        if remaining_quantity > 0:
            raise InsufficientInventoryError(item.sku_id)
        
        return allocations
```

### 补货建议算法

```python
class ReplenishmentService:
    def __init__(self, db, forecast_service):
        self.db = db
        self.forecast_service = forecast_service
    
    async def generate_replenishment_suggestions(self):
        """
        生成补货建议
        基于安全库存、预测需求、供应商交期等因素
        """
        # 获取所有需要检查的SKU
        skus_to_check = await self.db.get_active_skus()
        
        suggestions = []
        
        for sku in skus_to_check:
            warehouses = await self.db.get_warehouses_for_sku(sku.id)
            
            for warehouse in warehouses:
                suggestion = await self._generate_sku_warehouse_suggestion(
                    sku, warehouse
                )
                
                if suggestion:
                    suggestions.append(suggestion)
        
        # 批量保存建议
        await self.db.bulk_create_replenishment_suggestions(suggestions)
        
        return suggestions
    
    async def _generate_sku_warehouse_suggestion(self, sku, warehouse) -> Optional[ReplenishmentSuggestion]:
        """
        为特定SKU和仓库生成补货建议
        """
        # 获取当前库存
        current_inventory = await self.db.get_inventory(warehouse.id, sku.id)
        current_stock = current_inventory.available_quantity + current_inventory.in_transit_quantity
        
        # 检查是否低于重订点
        if current_stock > current_inventory.reorder_point:
            return None
        
        # 获取历史销售数据
        sales_history = await self.db.get_sales_history(
            sku.id, 
            warehouse.id, 
            days=90
        )
        
        # 预测未来需求
        forecast = await self.forecast_service.forecast_demand(
            sku.id, 
            warehouse.id, 
            sales_history,
            days=30
        )
        
        # 计算建议补货量
        safety_stock = current_inventory.safety_stock
        lead_time_demand = forecast.daily_average * 7  # 假设7天供应商交期
        
        suggested_quantity = max(
            safety_stock + lead_time_demand - current_stock,
            0
        )
        
        if suggested_quantity <= 0:
            return None
        
        # 确定优先级
        priority = self._calculate_priority(
            current_stock, 
            current_inventory.reorder_point,
            forecast.trend
        )
        
        return ReplenishmentSuggestion(
            warehouse_id=warehouse.id,
            sku_id=sku.id,
            current_stock=current_stock,
            suggested_quantity=int(suggested_quantity),
            priority=priority,
            reason=f"当前库存 {current_stock} 低于重订点 {current_inventory.reorder_point}"
        )
    
    def _calculate_priority(self, current_stock: int, reorder_point: int, trend: float) -> str:
        """计算补货优先级"""
        stock_ratio = current_stock / reorder_point if reorder_point > 0 else 0
        
        if stock_ratio <= 0.3 or trend > 0.2:  # 库存很低或需求上升
            return 'urgent'
        elif stock_ratio <= 0.5:
            return 'high'
        elif stock_ratio <= 0.8:
            return 'medium'
        else:
            return 'low'
```

## 监控指标

### 业务指标

- 库存周转率
- 缺货率
- 预占超时率
- 补货及时率

### 技术指标

- 库存查询响应时间
- 预占成功率
- 缓存命中率
- 数据一致性检查

### 异常指标

- 库存超卖次数
- 预占泄露次数
- 库存同步失败率
- 数据不一致次数

## 部署配置

### 环境变量

```bash
# 数据库配置
INVENTORY_DB_URL=postgresql://user:pass@localhost/inventory_db

# 缓存配置
INVENTORY_REDIS_URL=redis://localhost:6379/3
INVENTORY_CACHE_TTL=3600

# 预占配置
DEFAULT_RESERVATION_TIMEOUT=30
MAX_RESERVATION_EXTENSION=60

# 补货配置
REPLENISHMENT_CHECK_INTERVAL=86400
LOW_STOCK_THRESHOLD=0.2
```

## 相关文档

- [商品模块](../product-catalog/overview.md)
- [订单模块](../order-management/overview.md)
- [事件架构](../../architecture/event-driven.md)
- [缓存策略](../../architecture/caching.md)
