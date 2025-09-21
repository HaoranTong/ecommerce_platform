# 事件驱动架构设计

## 文档说明
- **内容**：事件驱动架构设计、事件Schema规范、版本管理策略
- **使用者**：架构师、后端开发、系统集成工程师
- **更新频率**：架构变更或新增事件类型时更新
- **关联文档**：[系统集成](integration.md)、[API设计标准](api-standards.md)

---

## 事件驱动架构概览

### 设计原则
1. **事件优先**: 通过事件实现服务间松耦合通信
2. **最终一致性**: 接受暂时不一致，保证最终一致性
3. **幂等性**: 所有事件处理必须支持幂等
4. **可追溯性**: 完整的事件流水线和审计日志
5. **版本兼容**: 严格的向后兼容性管理

### 架构模式
- **Event Sourcing**: 核心业务实体使用事件溯源
- **CQRS**: 命令查询责任分离
- **Saga Pattern**: 分布式事务管理
- **Event Streaming**: 实时事件流处理

---

## 事件分类与命名规范

### 事件类型分类
```yaml
域事件 (Domain Events):
  格式: "{Entity}.{Action}.v{Version}"
  示例: "User.Created.v1", "Order.Paid.v1"
  
集成事件 (Integration Events):
  格式: "{Service}.{Entity}.{Action}.v{Version}"
  示例: "Payment.Order.Paid.v1", "Inventory.Product.Updated.v1"
  
系统事件 (System Events):
  格式: "System.{Component}.{Event}.v{Version}"
  示例: "System.Health.CheckFailed.v1", "System.Backup.Completed.v1"
```

### 版本管理规则
1. **向后兼容原则**: 新版本只能新增可选字段，不能移除字段
2. **字段弃用**: 使用 `deprecated: true` 标记，至少保留2个版本周期
3. **重大变更**: 需要增加主版本号，如v1 → v2
4. **Schema验证**: 所有事件必须通过JSON Schema验证

---

## 核心事件Schema定义

### 用户相关事件

#### User.Created.v1
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "用户创建事件",
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "事件唯一标识"
    },
    "event_type": {
      "type": "string",
      "const": "User.Created",
      "description": "事件类型"
    },
    "version": {
      "type": "string",
      "const": "1",
      "description": "Schema版本"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "事件发生时间"
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "关联ID，用于追踪业务流程"
    },
    "data": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "integer",
          "description": "用户ID"
        },
        "username": {
          "type": "string",
          "maxLength": 50,
          "description": "用户名"
        },
        "email": {
          "type": "string",
          "format": "email",
          "description": "邮箱地址"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "创建时间"
        },
        "user_type": {
          "type": "string",
          "enum": ["customer", "vendor", "admin"],
          "description": "用户类型"
        }
      },
      "required": ["user_id", "username", "email", "created_at", "user_type"]
    }
  },
  "required": ["event_id", "event_type", "version", "timestamp", "correlation_id", "data"]
}
```

### 商品相关事件

#### Product.Created.v1
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "商品创建事件",
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "Product.Created"},
    "version": {"type": "string", "const": "1"},
    "timestamp": {"type": "string", "format": "date-time"},
    "correlation_id": {"type": "string", "format": "uuid"},
    "data": {
      "type": "object",
      "properties": {
        "product_id": {"type": "integer"},
        "name": {"type": "string", "maxLength": 200},
        "description": {"type": "string"},
        "brand_id": {"type": "integer"},
        "category_id": {"type": "integer"},
        "status": {"type": "string", "enum": ["draft", "published", "archived"]},
        "created_by": {"type": "integer"},
        "created_at": {"type": "string", "format": "date-time"}
      },
      "required": ["product_id", "name", "category_id", "status", "created_by", "created_at"]
    }
  },
  "required": ["event_id", "event_type", "version", "timestamp", "correlation_id", "data"]
}
```

#### SKU.Created.v1
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "SKU创建事件",
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "SKU.Created"},
    "version": {"type": "string", "const": "1"},
    "timestamp": {"type": "string", "format": "date-time"},
    "correlation_id": {"type": "string", "format": "uuid"},
    "data": {
      "type": "object",
      "properties": {
        "sku_id": {"type": "integer"},
        "product_id": {"type": "integer"},
        "sku_code": {"type": "string", "maxLength": 100},
        "name": {"type": "string", "maxLength": 200},
        "price": {"type": "number", "minimum": 0},
        "cost_price": {"type": "number", "minimum": 0},
        "market_price": {"type": "number", "minimum": 0},
        "weight": {"type": "number", "minimum": 0},
        "volume": {"type": "number", "minimum": 0},
        "is_active": {"type": "boolean"},
        "created_by": {"type": "integer"},
        "created_at": {"type": "string", "format": "date-time"}
      },
      "required": ["sku_id", "product_id", "sku_code", "name", "price", "is_active", "created_by", "created_at"]
    }
  },
  "required": ["event_id", "event_type", "version", "timestamp", "correlation_id", "data"]
}
```

### 订单相关事件

#### Order.Created.v1
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "订单创建事件",
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "Order.Created"},
    "version": {"type": "string", "const": "1"},
    "timestamp": {"type": "string", "format": "date-time"},
    "correlation_id": {"type": "string", "format": "uuid"},
    "data": {
      "type": "object",
      "properties": {
        "order_id": {"type": "integer"},
        "order_number": {"type": "string"},
        "user_id": {"type": "integer"},
        "total_amount": {"type": "number", "minimum": 0},
        "status": {"type": "string", "enum": ["pending", "confirmed", "paid", "shipped", "delivered", "cancelled"]},
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "product_id": {"type": "integer"},
              "sku_id": {"type": "integer"},
              "sku_code": {"type": "string"},
              "product_name": {"type": "string"},
              "sku_name": {"type": "string"},
              "quantity": {"type": "integer", "minimum": 1},
              "unit_price": {"type": "number", "minimum": 0},
              "subtotal": {"type": "number", "minimum": 0}
            },
            "required": ["product_id", "sku_id", "sku_code", "product_name", "sku_name", "quantity", "unit_price", "subtotal"]
          }
        },
        "shipping_address": {
          "type": "object",
          "properties": {
            "recipient": {"type": "string"},
            "phone": {"type": "string"},
            "address": {"type": "string"},
            "city": {"type": "string"},
            "province": {"type": "string"},
            "postal_code": {"type": "string"}
          },
          "required": ["recipient", "phone", "address", "city", "province"]
        },
        "created_at": {"type": "string", "format": "date-time"}
      },
      "required": ["order_id", "order_number", "user_id", "total_amount", "status", "items", "shipping_address", "created_at"]
    }
  },
  "required": ["event_id", "event_type", "version", "timestamp", "correlation_id", "data"]
}
```

---

## 事件发布与订阅机制

### 事件发布者 (Event Publisher)
```python
# 事件发布接口
class EventPublisher:
    def publish(self, event: DomainEvent) -> None:
        """发布领域事件"""
        # 1. 验证事件Schema
        self.validate_schema(event)
        
        # 2. 添加元数据
        enriched_event = self.enrich_event(event)
        
        # 3. 发布到消息队列
        self.message_broker.publish(enriched_event)
        
        # 4. 记录发布日志
        self.audit_logger.log_event_published(enriched_event)

# 使用示例
publisher = EventPublisher()
user_created_event = UserCreatedEvent(
    user_id=123,
    username="testuser",
    email="test@example.com",
    created_at=datetime.utcnow()
)
publisher.publish(user_created_event)
```

### 事件订阅者 (Event Subscriber)
```python
# 事件处理器基类
class EventHandler:
    def handle(self, event: dict) -> None:
        """处理事件的抽象方法"""
        raise NotImplementedError

# 具体事件处理器
class UserCreatedHandler(EventHandler):
    def handle(self, event: dict) -> None:
        """处理用户创建事件"""
        user_data = event['data']
        
        # 1. 验证事件数据
        if not self.validate_event(event):
            raise InvalidEventError("事件数据验证失败")
        
        # 2. 幂等性检查
        if self.is_already_processed(event['event_id']):
            return
        
        # 3. 业务逻辑处理
        self.create_user_profile(user_data)
        self.send_welcome_email(user_data['email'])
        
        # 4. 标记为已处理
        self.mark_as_processed(event['event_id'])
```

---

## 消息队列配置

### Redis Streams配置
```python
# Redis Streams事件队列配置
REDIS_STREAMS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "streams": {
        "user-events": {
            "maxlen": 10000,
            "retention": "7d"
        },
        "product-events": {
            "maxlen": 50000,
            "retention": "30d"
        },
        "order-events": {
            "maxlen": 100000,
            "retention": "90d"
        }
    },
    "consumer_groups": {
        "user-service": ["user-events"],
        "notification-service": ["user-events", "order-events"],
        "analytics-service": ["user-events", "product-events", "order-events"]
    }
}
```

### 事件路由配置
```yaml
# 事件路由规则
event_routing:
  User.Created:
    - notification-service
    - analytics-service
    - recommendation-service
  
  Product.Created:
    - search-service
    - analytics-service
    - cache-service
  
  Order.Created:
    - inventory-service
    - payment-service
    - notification-service
    - analytics-service
```

---

## 事件溯源实现

### 事件存储
```python
class EventStore:
    def append_events(self, stream_id: str, events: List[DomainEvent], 
                     expected_version: int) -> None:
        """追加事件到事件流"""
        with self.db.transaction():
            # 1. 版本检查
            current_version = self.get_stream_version(stream_id)
            if current_version != expected_version:
                raise ConcurrencyError("版本冲突")
            
            # 2. 存储事件
            for event in events:
                self.db.execute("""
                    INSERT INTO event_store 
                    (stream_id, event_id, event_type, event_data, version, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (stream_id, event.event_id, event.event_type, 
                      event.to_json(), current_version + 1, event.timestamp))
                current_version += 1
            
            # 3. 发布事件
            for event in events:
                self.event_publisher.publish(event)

    def get_events(self, stream_id: str, from_version: int = 0) -> List[DomainEvent]:
        """获取事件流"""
        rows = self.db.execute("""
            SELECT event_type, event_data, version, timestamp
            FROM event_store 
            WHERE stream_id = ? AND version > ?
            ORDER BY version
        """, (stream_id, from_version))
        
        return [self.deserialize_event(row) for row in rows]
```

### 聚合根重建
```python
class AggregateRoot:
    def load_from_history(self, events: List[DomainEvent]) -> None:
        """从事件历史重建聚合根状态"""
        for event in events:
            self.apply_event(event)
        self.mark_events_as_committed()
    
    def apply_event(self, event: DomainEvent) -> None:
        """应用事件到聚合根"""
        handler_name = f"on_{event.event_type.lower().replace('.', '_')}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event)

# 用户聚合根示例
class User(AggregateRoot):
    def on_user_created(self, event: UserCreatedEvent) -> None:
        self.id = event.user_id
        self.username = event.username
        self.email = event.email
        self.created_at = event.created_at
    
    def on_user_updated(self, event: UserUpdatedEvent) -> None:
        if event.username:
            self.username = event.username
        if event.email:
            self.email = event.email
        self.updated_at = event.updated_at
```

---

## 监控与故障处理

### 事件监控指标
```yaml
监控指标:
  事件发布:
    - 发布成功率
    - 发布延迟
    - 每秒发布数量
    
  事件处理:
    - 处理成功率
    - 处理延迟
    - 队列积压数量
    - 重试次数
    
  事件存储:
    - 存储延迟
    - 存储大小
    - 查询性能
```

### 故障恢复策略
1. **重试机制**: 指数退避重试，最大重试3次
2. **死信队列**: 失败事件进入死信队列，人工处理
3. **断路器**: 下游服务异常时暂停事件发送
4. **补偿机制**: 提供事件回滚和补偿操作

---

## 事件驱动开发指南

### 事件设计最佳实践
1. **事件命名**: 使用过去式，描述已发生的事实
2. **事件粒度**: 粒度适中，既不过大也不过小
3. **事件数据**: 包含处理所需的最小数据集
4. **事件顺序**: 设计时考虑事件的先后依赖关系

### 开发工作流程
1. **定义Schema**: 先定义事件Schema，再编写代码
2. **版本管理**: 遵循严格的版本兼容性规则
3. **测试策略**: 事件发布和订阅的集成测试
4. **文档维护**: 及时更新事件文档和示例

---

## 相关文档
- [系统集成](integration.md) - 第三方系统集成规范
- [API设计标准](api-standards.md) - RESTful API设计规范
- [数据模型标准](data-standards.md) - 数据库设计规范
- [MASTER工作流程](../MASTER.md) - 事件驱动架构检查点
