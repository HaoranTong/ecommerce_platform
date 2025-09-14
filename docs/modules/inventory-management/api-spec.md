# 库存管理模块 API 规范

## 文档信息
- **模块名称**: 库存管理模块 (Inventory Management Module)  
- **API版本**: v1.0
- **最后更新**: 2024-12-19
- **文档类型**: API规范文档
- **遵循标准**: [API设计标准](../../api/api-design-standards.md)

## API 基础信息

### 基础路径
```
/api/inventory/
```

### 路由前缀
库存管理模块使用 `/api/inventory/` 前缀，区分于其他业务模块。

### 认证方式
- **类型**: Bearer Token (JWT)
- **权限等级**: 用户级别、管理员级别

### 响应格式
所有API响应遵循统一格式：
```json
{
    "code": 200,
    "message": "成功",
    "data": {},
    "timestamp": "2024-12-19T10:30:00Z"
}
```

## API 端点定义

### 1. 库存查询接口

#### 1.1 获取商品库存信息
- **方法**: `GET`
- **路径**: `/api/inventory/{product_id}`
- **描述**: 获取指定商品的库存信息
- **权限**: 已认证用户
- **参数**:
  - `product_id` (path, required): 商品ID
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "product_id": 1001,
        "available_quantity": 50,
        "reserved_quantity": 10,
        "total_quantity": 60,
        "warning_threshold": 10,
        "is_low_stock": false,
        "updated_at": "2024-12-19T10:30:00Z"
    }
}
```

#### 1.2 批量获取商品库存
- **方法**: `POST`
- **路径**: `/api/inventory/batch`
- **描述**: 批量获取多个商品的库存信息
- **权限**: 已认证用户
- **请求体**:
```json
{
    "product_ids": [1001, 1002, 1003]
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": [
        {
            "product_id": 1001,
            "available_quantity": 50,
            "reserved_quantity": 10,
            "total_quantity": 60,
            "is_low_stock": false
        }
    ]
}
```

### 2. 库存预占接口

#### 2.1 购物车库存预占
- **方法**: `POST`
- **路径**: `/api/inventory/reserve/cart`
- **描述**: 为购物车商品预占库存
- **权限**: 已认证用户
- **请求体**:
```json
{
    "items": [
        {
            "product_id": 1001,
            "quantity": 2
        }
    ],
    "expires_minutes": 30
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "库存预占成功",
    "data": {
        "reservation_id": "res_12345",
        "expires_at": "2024-12-19T11:00:00Z",
        "reserved_items": [
            {
                "product_id": 1001,
                "reserved_quantity": 2,
                "available_after_reserve": 48
            }
        ]
    }
}
```

#### 2.2 订单库存预占
- **方法**: `POST`
- **路径**: `/api/inventory/reserve/order`
- **描述**: 为订单预占库存
- **权限**: 已认证用户
- **请求体**:
```json
{
    "order_id": 12345,
    "items": [
        {
            "product_id": 1001,
            "quantity": 2
        }
    ]
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "订单库存预占成功",
    "data": {
        "reservation_id": "res_54321",
        "order_id": 12345,
        "expires_at": "2024-12-19T12:00:00Z",
        "reserved_items": [
            {
                "product_id": 1001,
                "reserved_quantity": 2
            }
        ]
    }
}
```

#### 2.3 释放购物车预占
- **方法**: `DELETE`
- **路径**: `/api/inventory/reserve/cart`
- **描述**: 释放用户购物车的库存预占
- **权限**: 已认证用户
- **查询参数**:
  - `user_id` (query, optional): 用户ID（管理员可指定）
- **响应**:
```json
{
    "code": 200,
    "message": "购物车预占已释放",
    "data": {
        "released_reservations": 3,
        "released_quantity": 15
    }
}
```

#### 2.4 释放订单预占
- **方法**: `DELETE`
- **路径**: `/api/inventory/reserve/order/{order_id}`
- **描述**: 释放指定订单的库存预占
- **权限**: 已认证用户（仅能释放自己的订单）
- **参数**:
  - `order_id` (path, required): 订单ID
- **响应**:
```json
{
    "code": 200,
    "message": "订单预占已释放",
    "data": {
        "order_id": 12345,
        "released_items": [
            {
                "product_id": 1001,
                "released_quantity": 2
            }
        ]
    }
}
```

### 3. 库存扣减接口

#### 3.1 订单完成库存扣减
- **方法**: `POST`
- **路径**: `/api/inventory/deduct`
- **描述**: 订单支付完成后执行库存扣减
- **权限**: 系统内部调用
- **请求体**:
```json
{
    "order_id": 12345,
    "items": [
        {
            "product_id": 1001,
            "quantity": 2
        }
    ]
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "库存扣减成功",
    "data": {
        "order_id": 12345,
        "deducted_items": [
            {
                "product_id": 1001,
                "deducted_quantity": 2,
                "remaining_quantity": 48
            }
        ]
    }
}
```

### 4. 库存管理接口（管理员）

#### 4.1 库存调整
- **方法**: `PUT`
- **路径**: `/api/inventory/{product_id}/adjust`
- **描述**: 管理员手动调整商品库存
- **权限**: 管理员
- **参数**:
  - `product_id` (path, required): 商品ID
- **请求体**:
```json
{
    "adjustment_type": "increase",
    "quantity": 100,
    "reason": "新货入库"
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "库存调整成功",
    "data": {
        "product_id": 1001,
        "old_quantity": 50,
        "new_quantity": 150,
        "adjustment_quantity": 100,
        "reason": "新货入库"
    }
}
```

#### 4.2 设置预警阈值
- **方法**: `PUT`
- **路径**: `/api/inventory/{product_id}/threshold`
- **描述**: 设置商品的低库存预警阈值
- **权限**: 管理员
- **参数**:
  - `product_id` (path, required): 商品ID
- **请求体**:
```json
{
    "warning_threshold": 20
}
```
- **响应**:
```json
{
    "code": 200,
    "message": "预警阈值设置成功",
    "data": {
        "product_id": 1001,
        "old_threshold": 10,
        "new_threshold": 20
    }
}
```

#### 4.3 获取低库存商品列表
- **方法**: `GET`
- **路径**: `/api/inventory/low-stock`
- **描述**: 获取低库存预警的商品列表
- **权限**: 管理员
- **查询参数**:
  - `page` (query, optional): 页码，默认1
  - `page_size` (query, optional): 每页数量，默认20
  - `category_id` (query, optional): 商品分类ID筛选
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "items": [
            {
                "product_id": 1001,
                "product_name": "商品名称",
                "current_quantity": 8,
                "warning_threshold": 10,
                "shortage": 2
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    }
}
```

### 5. 库存历史接口

#### 5.1 获取库存变动历史
- **方法**: `GET`
- **路径**: `/api/inventory/{product_id}/transactions`
- **描述**: 获取商品的库存变动历史记录
- **权限**: 管理员
- **参数**:
  - `product_id` (path, required): 商品ID
- **查询参数**:
  - `page` (query, optional): 页码，默认1
  - `page_size` (query, optional): 每页数量，默认20
  - `start_date` (query, optional): 开始日期
  - `end_date` (query, optional): 结束日期
  - `transaction_type` (query, optional): 交易类型筛选
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "items": [
            {
                "id": 12345,
                "product_id": 1001,
                "transaction_type": "purchase",
                "quantity": 100,
                "reference_id": "PO-2024-001",
                "created_at": "2024-12-19T10:00:00Z",
                "operator": "admin_user"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    }
}
```

### 6. 系统维护接口

#### 6.1 清理过期预占
- **方法**: `POST`
- **路径**: `/api/inventory/cleanup/expired-reservations`
- **描述**: 清理过期的库存预占记录
- **权限**: 系统内部调用或管理员
- **响应**:
```json
{
    "code": 200,
    "message": "过期预占清理完成",
    "data": {
        "cleaned_reservations": 25,
        "released_quantity": 150
    }
}
```

## 错误码定义

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| 40001 | 商品不存在 | 检查商品ID是否正确 |
| 40002 | 库存不足 | 提示用户减少购买数量 |
| 40003 | 预占已过期 | 重新发起预占请求 |
| 40004 | 预占不存在 | 检查预占ID是否正确 |
| 40005 | 库存调整数量无效 | 检查调整数量是否为正数 |
| 50001 | 库存服务异常 | 稍后重试或联系技术支持 |
| 50002 | 数据库连接异常 | 检查系统状态 |

## 数据模型

### 库存信息模型 (InventoryRead)
```json
{
    "product_id": "integer",
    "available_quantity": "integer",
    "reserved_quantity": "integer", 
    "total_quantity": "integer",
    "warning_threshold": "integer",
    "is_low_stock": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 预占响应模型 (ReservationResponse)
```json
{
    "reservation_id": "string",
    "order_id": "integer (optional)",
    "expires_at": "datetime",
    "reserved_items": [
        {
            "product_id": "integer",
            "reserved_quantity": "integer",
            "available_after_reserve": "integer (optional)"
        }
    ]
}
```

### 交易记录模型 (InventoryTransactionRead)
```json
{
    "id": "integer",
    "product_id": "integer",
    "transaction_type": "string",
    "quantity": "integer",
    "reference_id": "string",
    "created_at": "datetime",
    "operator": "string"
}
```

## 集成说明

### 与其他模块的集成

#### 购物车模块集成
- 添加商品到购物车时调用库存预占接口
- 清空购物车时调用预占释放接口
- 定期清理过期的购物车预占

#### 订单模块集成  
- 创建订单时调用订单库存预占
- 取消订单时调用预占释放接口
- 订单支付完成时调用库存扣减接口

#### 商品模块集成
- 新增商品时自动创建库存记录
- 商品下架时处理库存预占和扣减

## 性能指标

### 响应时间要求
- 库存查询: < 100ms
- 库存预占: < 200ms  
- 库存扣减: < 300ms
- 批量操作: < 500ms

### 并发处理能力
- 支持1000+ QPS的库存查询
- 支持500+ QPS的库存预占
- 支持200+ QPS的库存扣减

### 缓存策略
- 热门商品库存信息Redis缓存（TTL: 60秒）
- 低库存商品列表缓存（TTL: 300秒）
- 预占记录Redis缓存（TTL: 1800秒）

---

**注意**: 此API规范与实际代码实现完全对应，任何修改需要同步更新代码和文档。