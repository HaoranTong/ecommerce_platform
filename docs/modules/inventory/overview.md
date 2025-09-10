# 库存管理模块 (Inventory Management Module)

## 模块概述

库存管理模块负责商品库存的实时跟踪、预占机制、补货预警、多仓库管理和库存同步。确保库存数据的准确性和一致性，防止超卖现象。

### 主要功能

1. **库存跟踪**
   - 实时库存监控
   - 库存变更日志
   - 多维度库存视图 (可用、预占、在途)
   - 批次和序列号管理

2. **预占机制**
   - 购物车预占
   - 订单库存锁定
   - 预占超时释放
   - 库存回滚机制

3. **补货管理**
   - 库存预警设置
   - 自动补货建议
   - 采购订单生成
   - 供应商协同

4. **多仓库支持**
   - 仓库层级管理
   - 库存分配策略
   - 跨仓调拨
   - 就近发货规则

## 技术架构

### 核心组件

```
inventory/
├── controllers/
│   ├── inventory_controller.py    # 库存控制器
│   ├── warehouse_controller.py    # 仓库控制器
│   ├── reservation_controller.py  # 预占控制器
│   └── replenishment_controller.py # 补货控制器
├── services/
│   ├── inventory_service.py       # 库存业务逻辑
│   ├── reservation_service.py     # 预占服务
│   ├── replenishment_service.py   # 补货服务
│   ├── allocation_service.py      # 分配服务
│   └── sync_service.py            # 同步服务
├── models/
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

### 库存查询

```yaml
/api/v1/inventory:
  GET /:
    summary: 查询库存
    parameters:
      - name: sku_id
        in: query
        schema:
          type: string
          format: uuid
      - name: warehouse_id
        in: query
        schema:
          type: string
          format: uuid
      - name: include_reserved
        in: query
        schema:
          type: boolean
          default: false
    responses:
      200:
        description: 库存信息
        content:
          application/json:
            schema:
              type: object
              properties:
                inventories:
                  type: array
                  items:
                    $ref: '#/components/schemas/InventoryInfo'

  GET /{sku_id}/availability:
    summary: 检查商品可用性
    parameters:
      - name: sku_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: quantity
        in: query
        required: true
        schema:
          type: integer
          minimum: 1
      - name: warehouse_id
        in: query
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 可用性检查结果
        content:
          application/json:
            schema:
              type: object
              properties:
                available:
                  type: boolean
                quantity_available:
                  type: integer
                warehouses:
                  type: array
                  items:
                    type: object
                    properties:
                      warehouse_id:
                        type: string
                      quantity_available:
                        type: integer

  PUT /{sku_id}/adjust:
    summary: 库存调整
    security:
      - BearerAuth: []
    parameters:
      - name: sku_id
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
              warehouse_id:
                type: string
                format: uuid
              adjustment_type:
                type: string
                enum: [increase, decrease, set]
              quantity:
                type: integer
              reason:
                type: string
    responses:
      200:
        description: 调整成功
```

### 预占管理

```yaml
/api/v1/inventory/reservations:
  POST /:
    summary: 创建库存预占
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              items:
                type: array
                items:
                  type: object
                  properties:
                    sku_id:
                      type: string
                      format: uuid
                    quantity:
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
