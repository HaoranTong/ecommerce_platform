# 购物车模块 - API规范文档

📅 **创建日期**: 2025-09-16  
👤 **设计者**: 后端架构师  
✅ **状态**: 设计中  
🔄 **最后更新**: 2025-09-16  
📋 **版本**: v1.0  

## API概览

### 基础信息
- **模块名**: shopping-cart  
- **API前缀**: `/api/v1/shopping-cart/`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 设计原则
- **RESTful设计**: 遵循REST架构风格
- **幂等性保证**: PUT/DELETE操作支持幂等
- **统一响应格式**: 成功/错误响应格式统一
- **版本兼容性**: 向前兼容，渐进式升级

### 端点列表

| 方法 | 路径 | 功能描述 | 状态 |
|------|------|----------|------|
| POST | `/api/v1/shopping-cart/items` | 添加商品到购物车 | 待实现 |
| GET | `/api/v1/shopping-cart/cart` | 获取购物车内容 | 待实现 |
| PUT | `/api/v1/shopping-cart/items/{item_id}` | 更新商品数量 | 待实现 |
| DELETE | `/api/v1/shopping-cart/items/{item_id}` | 删除单个商品 | 待实现 |
| DELETE | `/api/v1/shopping-cart/items` | 批量删除商品 | 待实现 |
| DELETE | `/api/v1/shopping-cart/cart` | 清空购物车 | 待实现 |

## 通用规范

### 请求头规范
```http
Content-Type: application/json
Authorization: Bearer {jwt_token}
Accept: application/json
User-Agent: {client_info}
```

### 统一响应格式

#### 成功响应
```json
{
    "success": true,
    "data": {
        // 具体业务数据
    },
    "message": "操作成功",
    "timestamp": "2025-09-16T10:30:00Z",
    "request_id": "req_12345678"
}
```

#### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "CART_ERROR_001",
        "message": "库存不足",
        "details": {
            "sku_id": 12345,
            "requested": 10,
            "available": 5
        }
    },
    "timestamp": "2025-09-16T10:30:00Z",
    "request_id": "req_12345678"
}
```

### HTTP状态码规范
| 状态码 | 描述 | 使用场景 |
|--------|------|----------|
| 200 | OK | 操作成功 |
| 201 | Created | 资源创建成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 用户未认证 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |

## 详细API规范

### 1. 添加商品到购物车

#### 端点信息
```
POST /api/v1/shopping-cart/items
```

#### 功能描述
将指定的商品添加到当前用户的购物车中，如果商品已存在则增加数量。

#### 请求参数
```json
{
    "sku_id": 12345,
    "quantity": 2
}
```

| 字段 | 类型 | 必填 | 描述 | 验证规则 |
|------|------|------|------|----------|
| sku_id | integer | 是 | 商品SKU ID | > 0 |
| quantity | integer | 是 | 商品数量 | 1-999 |

#### 响应示例

**成功响应 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "total_items": 3,
        "total_quantity": 5,
        "total_amount": 299.99,
        "items": [
            {
                "item_id": 456,
                "sku_id": 12345,
                "product_name": "iPhone 15 Pro",
                "unit_price": 99.99,
                "quantity": 2,
                "subtotal": 199.98,
                "added_at": "2025-09-16T10:30:00Z"
            }
        ],
        "updated_at": "2025-09-16T10:30:00Z"
    }
}
```

**错误响应 (400 - 库存不足)**
```json
{
    "success": false,
    "error": {
        "code": "CART_002",
        "message": "商品库存不足",
        "details": {
            "sku_id": 12345,
            "requested_quantity": 10,
            "available_stock": 5
        }
    }
}
```

#### 业务规则
1. 用户必须已登录
2. 商品必须处于上架状态
3. 库存必须充足
4. 购物车商品种类不超过50个
5. 单个商品数量不超过999个

### 2. 获取购物车内容

#### 端点信息
```
GET /api/v1/shopping-cart/cart
```

#### 功能描述
获取当前用户购物车的完整内容，包括商品详情和价格计算。

#### 请求参数
无

#### 响应示例

**成功响应 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "user_id": 789,
        "total_items": 2,
        "total_quantity": 4,
        "total_amount": 399.98,
        "items": [
            {
                "item_id": 456,
                "sku_id": 12345,
                "product_name": "iPhone 15 Pro",
                "product_image": "https://cdn.example.com/iphone15.jpg",
                "unit_price": 99.99,
                "quantity": 2,
                "subtotal": 199.98,
                "stock_status": "in_stock",
                "available_stock": 100,
                "added_at": "2025-09-16T10:30:00Z"
            },
            {
                "item_id": 457,
                "sku_id": 12346,
                "product_name": "AirPods Pro",
                "product_image": "https://cdn.example.com/airpods.jpg",
                "unit_price": 199.99,
                "quantity": 1,
                "subtotal": 199.99,
                "stock_status": "low_stock",
                "available_stock": 3,
                "added_at": "2025-09-16T11:00:00Z"
            }
        ],
        "created_at": "2025-09-16T10:30:00Z",
        "updated_at": "2025-09-16T11:00:00Z"
    }
}
```

**空购物车 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "user_id": 789,
        "total_items": 0,
        "total_quantity": 0,
        "total_amount": 0.00,
        "items": [],
        "created_at": "2025-09-16T10:30:00Z",
        "updated_at": "2025-09-16T10:30:00Z"
    }
}
```

### 3. 更新商品数量

#### 端点信息
```
PUT /api/v1/shopping-cart/items/{item_id}
```

#### 功能描述
更新购物车中指定商品的数量。

#### 路径参数
| 参数 | 类型 | 描述 |
|------|------|------|
| item_id | integer | 购物车商品项ID |

#### 请求参数
```json
{
    "quantity": 5
}
```

| 字段 | 类型 | 必填 | 描述 | 验证规则 |
|------|------|------|------|----------|
| quantity | integer | 是 | 新的商品数量 | 1-999 |

#### 响应示例

**成功响应 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "total_items": 2,
        "total_quantity": 6,
        "total_amount": 499.95,
        "updated_item": {
            "item_id": 456,
            "sku_id": 12345,
            "quantity": 5,
            "subtotal": 499.95
        },
        "updated_at": "2025-09-16T11:30:00Z"
    }
}
```

**错误响应 (400 - 库存不足)**
```json
{
    "success": false,
    "error": {
        "code": "CART_002",
        "message": "库存不足，已调整到最大可用数量",
        "details": {
            "item_id": 456,
            "sku_id": 12345,
            "requested_quantity": 10,
            "adjusted_quantity": 5,
            "available_stock": 5
        }
    }
}
```

### 4. 删除单个商品

#### 端点信息
```
DELETE /api/v1/shopping-cart/items/{item_id}
```

#### 功能描述
从购物车中删除指定的商品项。

#### 路径参数
| 参数 | 类型 | 描述 |
|------|------|------|
| item_id | integer | 购物车商品项ID |

#### 请求参数
无

#### 响应示例

**成功响应 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "total_items": 1,
        "total_quantity": 1,
        "total_amount": 199.99,
        "deleted_item": {
            "item_id": 456,
            "sku_id": 12345,
            "product_name": "iPhone 15 Pro"
        },
        "updated_at": "2025-09-16T12:00:00Z"
    }
}
```

**错误响应 (404)**
```json
{
    "success": false,
    "error": {
        "code": "CART_004",
        "message": "购物车商品项不存在",
        "details": {
            "item_id": 456
        }
    }
}
```

### 5. 批量删除商品

#### 端点信息
```
DELETE /api/v1/shopping-cart/items
```

#### 功能描述
批量删除购物车中的多个商品项。

#### 请求参数
```json
{
    "item_ids": [456, 457, 458]
}
```

| 字段 | 类型 | 必填 | 描述 | 验证规则 |
|------|------|------|------|----------|
| item_ids | array | 是 | 商品项ID列表 | 数组长度1-50 |

#### 响应示例

**成功响应 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "total_items": 0,
        "total_quantity": 0,
        "total_amount": 0.00,
        "deleted_count": 3,
        "deleted_items": [
            {"item_id": 456, "sku_id": 12345},
            {"item_id": 457, "sku_id": 12346},
            {"item_id": 458, "sku_id": 12347}
        ],
        "updated_at": "2025-09-16T12:30:00Z"
    }
}
```

### 6. 清空购物车

#### 端点信息
```
DELETE /api/v1/shopping-cart/cart
```

#### 功能描述
清空当前用户的整个购物车。

#### 请求参数
无

#### 响应示例

**成功响应 (200)**
```json
{
    "success": true,
    "data": {
        "cart_id": 123,
        "total_items": 0,
        "total_quantity": 0,
        "total_amount": 0.00,
        "cleared_count": 5,
        "updated_at": "2025-09-16T13:00:00Z"
    },
    "message": "购物车已清空"
}
```

## 错误码定义

| 错误码 | HTTP状态码 | 错误描述 | 解决方案 |
|--------|------------|----------|----------|
| CART_001 | 400 | 请求参数验证失败 | 检查参数格式和取值范围 |
| CART_002 | 400 | 商品库存不足 | 调整商品数量或选择其他商品 |
| CART_003 | 400 | 购物车商品数量超限 | 购物车最多50种商品 |
| CART_004 | 404 | 购物车商品项不存在 | 确认商品项ID正确性 |
| CART_005 | 404 | 商品不存在或已下架 | 选择其他在售商品 |
| CART_006 | 409 | 商品已在购物车中 | 使用更新数量接口 |
| CART_007 | 429 | 操作过于频繁 | 稍后重试 |
| CART_008 | 500 | 缓存服务异常 | 系统异常，请联系客服 |
| CART_009 | 500 | 数据库服务异常 | 系统异常，请联系客服 |

## 数据模型定义

### CartResponse
```json
{
    "cart_id": "integer",
    "user_id": "integer", 
    "total_items": "integer",
    "total_quantity": "integer",
    "total_amount": "decimal(10,2)",
    "items": "array[CartItem]",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### CartItem
```json
{
    "item_id": "integer",
    "sku_id": "integer",
    "product_name": "string",
    "product_image": "string",
    "unit_price": "decimal(10,2)",
    "quantity": "integer",
    "subtotal": "decimal(10,2)",
    "stock_status": "enum[in_stock, low_stock, out_of_stock]",
    "available_stock": "integer",
    "added_at": "datetime"
}
```

### AddItemRequest  
```json
{
    "sku_id": "integer",
    "quantity": "integer"
}
```

### UpdateQuantityRequest
```json
{
    "quantity": "integer"
}
```

### BatchDeleteRequest
```json
{
    "item_ids": "array[integer]"
}
```

## 性能考虑

### 缓存策略
- **购物车数据**: Redis缓存，TTL 1小时
- **商品信息**: 本地缓存，TTL 10分钟
- **库存数据**: 实时查询，不缓存

### 限流策略
- **添加商品**: 每用户每秒最多5次
- **查询购物车**: 每用户每秒最多10次
- **批量操作**: 每用户每分钟最多10次

### 并发处理
- **乐观锁**: 使用version字段防止并发冲突
- **分布式锁**: Redis锁保护库存验证
- **幂等性**: PUT/DELETE操作支持重试

## 测试用例

### 功能测试
1. **正常流程测试**: 添加→查看→修改→删除
2. **边界值测试**: 数量限制、商品数限制
3. **异常场景测试**: 库存不足、商品下架
4. **并发测试**: 多用户同时操作

### 性能测试
1. **响应时间**: 95%请求 < 100ms
2. **并发能力**: 1000并发用户
3. **缓存命中率**: > 85%

## 版本变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0 | 2025-09-16 | 初始API规范设计 | 后端架构师 |
