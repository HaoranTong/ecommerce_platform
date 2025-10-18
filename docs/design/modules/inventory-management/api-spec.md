---
title: "库存管理模块API规范"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "API架构师"
dependencies:
  - "docs/standards/api-standards.md"
  - "docs/design/modules/inventory-management/design.md"
labels:
  - "inventory-management"
  - "api-specification"
  - "restful"
---

# 库存管理模块 API 规范

<!--
文件名：api-spec.md
文件路径：docs/design/modules/inventory-management/api-spec.md
文档类型：API规范文档
模块名称：库存管理模块 (Inventory Management Module)
文档版本：v1.1.0
创建时间：2025-09-15
最后修改：2025-10-18
维护人员：API架构师
文档状态：正式版本

文档用途：
- 定义库存管理模块的API接口规范
- 提供API契约和调用标准
- 指导前端开发和第三方集成

相关文档：
- API实现文档：api-implementation.md
- 系统设计文档：design.md
- 模块概览：overview.md
-->

## 依赖标准

本文档遵循以下标准规范：

| 标准文档 | 版本 | 应用范围 |
|---------|------|---------|
| [API设计标准](../../standards/api-standards.md) | v1.0 | RESTful API设计、路由命名 |
| [数据库设计标准](../../standards/database-standards.md) | v1.0 | 表结构设计、字段命名、索引设计 |
| [架构设计标准](../../standards/architecture-standards.md) | v1.0 | 四层架构、Repository模式、依赖注入 |
| [应用架构](../../architecture/application-architecture.md) | v1.0 | 模块化单体、模块边界、依赖管理 |

**架构版本**: V2.0 - 四层架构 (Router → Service → Repository → Model)
## 文档信息
- **模块名称**: 库存管理模块 (Inventory Management Module)  
- **API版本**: v1.0
- **最后更新**: 2025-10-18
- **文档类型**: API规范文档
- **遵循标准**: [API设计标准](../../standards/api-standards.md)
- **架构对齐**: 严格遵循 [表模块映射](../../architecture/table-module-mapping.md) 架构设计

## 架构原则

### 🎯 **核心设计原则**
1. **SKU级别管理**: 库存直接关联SKU，而不是Product
2. **Product-SKU分离**: 遵循架构设计，Product管理基础信息，SKU管理规格和定价
3. **统一标识**: 使用 `sku_id` 作为库存操作的核心标识符
4. **事件驱动**: 库存变动触发相应事件，实现模块解耦
5. **四层架构**: 采用Router → Service → Repository → Model四层架构设计 ⭐
   - **API层**: 本文档定义的RESTful接口
   - **业务层**: Service层实现业务逻辑
   - **数据层**: Repository层封装数据访问
   - **模型层**: Model层定义数据结构

## API 基础信息

### 基础路径
```text
/api/inventory/
```text

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
    "timestamp": "2025-09-15T10:30:00Z"
}
```json

## API 端点定义

### 1. 库存查询接口

#### 1.1 获取SKU库存信息
- **方法**: `GET`
- **路径**: `/api/inventory/stock/{sku_id}`
- **描述**: 获取指定SKU的实时库存信息
- **权限**: 已认证用户
- **参数**:
  - `sku_id` (path, required): SKU唯一标识符
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "sku_id": "SKU001001",
        "available_quantity": 50,
        "reserved_quantity": 10,
        "total_quantity": 60,
        "warning_threshold": 10,
        "is_low_stock": false,
        "last_updated": "2025-09-15T10:30:00Z"
    }
}
```text

#### 1.2 批量获取SKU库存
- **方法**: `POST`
- **路径**: `/api/inventory/stock/batch`
- **描述**: 批量获取多个SKU的库存信息
- **权限**: 已认证用户
- **请求体**:
```json
{
    "sku_ids": ["SKU001001", "SKU001002", "SKU001003"]
}
```json
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": [
        {
            "sku_id": "SKU001001",
            "available_quantity": 50,
            "reserved_quantity": 10,
            "total_quantity": 60,
            "is_low_stock": false
        },
        {
            "sku_id": "SKU001002",
            "available_quantity": 0,
            "reserved_quantity": 5,
            "total_quantity": 5,
            "is_low_stock": true
        }
    ]
}
```text

### 2. 库存预占接口

#### 2.1 库存预占
- **方法**: `POST`
- **路径**: `/api/inventory/reserve`
- **描述**: 为购物车或订单预占库存
- **权限**: 已认证用户
- **请求体**:
```json
{
    "reservation_type": "cart", // 或 "order"
    "reference_id": "user_123", // 用户ID或订单ID
    "items": [
        {
            "sku_id": "SKU001001",
            "quantity": 2
        }
    ],
    "expires_minutes": 30
}
```text
- **响应**:
```json
{
    "code": 200,
    "message": "库存预占成功",
    "data": {
        "reservation_id": "res_12345",
        "expires_at": "2025-09-15T11:00:00Z",
        "reserved_items": [
            {
                "sku_id": "SKU001001",
                "reserved_quantity": 2,
                "available_after_reserve": 48
            }
        ]
    }
}
```text

#### 2.2 释放库存预占
- **方法**: `DELETE`
- **路径**: `/api/inventory/reserve/{reservation_id}`
- **描述**: 释放指定的库存预占
- **权限**: 已认证用户（仅能释放自己的预占）
- **参数**:
  - `reservation_id` (path, required): 预占记录ID
- **响应**:
```json
{
    "code": 200,
    "message": "预占已释放",
    "data": {
        "reservation_id": "res_12345",
        "released_items": [
            {
                "sku_id": "SKU001001",
                "released_quantity": 2
            }
        ]
    }
}
```text

#### 2.3 批量释放用户预占
- **方法**: `DELETE`
- **路径**: `/api/inventory/reserve/user/{user_id}`
- **描述**: 释放指定用户的所有预占（购物车清空）
- **权限**: 已认证用户（仅能释放自己的预占）或管理员
- **参数**:
  - `user_id` (path, required): 用户ID
- **响应**:
```json
{
    "code": 200,
    "message": "用户预占已释放",
    "data": {
        "user_id": 123,
        "released_reservations": 3,
        "total_released_quantity": 15
    }
}
```text

### 3. 库存操作接口

#### 3.1 库存扣减
- **方法**: `POST`
- **路径**: `/api/inventory/deduct`
- **描述**: 订单完成后扣减库存（从预占转为实际扣减）
- **权限**: 系统内部调用或管理员
- **请求体**:
```json
{
    "order_id": "ORD123456",
    "items": [
        {
            "sku_id": "SKU001001",
            "quantity": 2,
            "reservation_id": "res_12345"
        }
    ]
}
```text
- **响应**:
```json
{
    "code": 200,
    "message": "库存扣减成功",
    "data": {
        "order_id": "ORD123456",
        "deducted_items": [
            {
                "sku_id": "SKU001001",
                "deducted_quantity": 2,
                "remaining_quantity": 58
            }
        ]
    }
}
```text

#### 3.2 库存调整
- **方法**: `POST`
- **路径**: `/api/inventory/adjust/{sku_id}`
- **描述**: 管理员调整SKU库存数量
- **权限**: 管理员
- **参数**:
  - `sku_id` (path, required): SKU ID
- **请求体**:
```json
{
    "adjustment_type": "increase", // 或 "decrease", "set"
    "quantity": 100,
    "reason": "新进货入库",
    "reference": "PO202509150001"
}
```text
- **响应**:
```json
{
    "code": 200,
    "message": "库存调整成功",
    "data": {
        "sku_id": "SKU001001",
        "old_quantity": 60,
        "new_quantity": 160,
        "adjustment_quantity": 100,
        "transaction_id": "txn_78901"
    }
}
```text

### 4. 库存管理接口

#### 4.1 设置库存阈值
- **方法**: `PUT`
- **路径**: `/api/inventory/threshold/{sku_id}`
- **描述**: 设置SKU的库存预警阈值
- **权限**: 管理员
- **参数**:
  - `sku_id` (path, required): SKU ID
- **请求体**:
```json
{
    "warning_threshold": 10,
    "critical_threshold": 5
}
```json
- **响应**:
```json
{
    "code": 200,
    "message": "阈值设置成功",
    "data": {
        "sku_id": "SKU001001",
        "warning_threshold": 10,
        "critical_threshold": 5
    }
}
```text

#### 4.2 获取低库存SKU列表
- **方法**: `GET`
- **路径**: `/api/inventory/low-stock`
- **描述**: 获取库存不足的SKU列表
- **权限**: 管理员
- **查询参数**:
  - `level` (query, optional): 预警级别 (warning|critical)
  - `limit` (query, optional): 返回数量限制，默认100
  - `offset` (query, optional): 分页偏移，默认0
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "total": 25,
        "items": [
            {
                "sku_id": "SKU001002",
                "current_quantity": 3,
                "warning_threshold": 10,
                "critical_threshold": 5,
                "level": "critical"
            }
        ]
    }
}
```text

### 5. 库存历史接口

#### 5.1 获取SKU库存变动历史
- **方法**: `GET`
- **路径**: `/api/inventory/logs/{sku_id}`
- **描述**: 获取指定SKU的库存变动历史记录
- **权限**: 管理员
- **参数**:
  - `sku_id` (path, required): SKU ID
- **查询参数**:
  - `start_date` (query, optional): 开始日期
  - `end_date` (query, optional): 结束日期
  - `transaction_type` (query, optional): 交易类型过滤
  - `limit` (query, optional): 返回数量限制
- **响应**:
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "sku_id": "SKU001001",
        "total": 150,
        "logs": [
            {
                "transaction_id": "txn_78901",
                "transaction_type": "adjustment",
                "quantity_change": 100,
                "quantity_before": 60,
                "quantity_after": 160,
                "reason": "新进货入库",
                "reference": "PO202509150001",
                "operator_id": 1001,
                "created_at": "2025-09-15T10:30:00Z"
            }
        ]
    }
}
```text

#### 5.2 搜索库存变动记录
- **方法**: `GET`
- **路径**: `/api/inventory/logs/search`
- **描述**: 按条件搜索库存变动记录
- **权限**: 管理员
- **查询参数**:
  - `sku_ids` (query, optional): SKU ID列表，逗号分隔
  - `transaction_types` (query, optional): 交易类型列表
  - `operator_id` (query, optional): 操作人ID
  - `start_date` (query, optional): 开始日期
  - `end_date` (query, optional): 结束日期
  - `limit` (query, optional): 返回数量限制
  - `offset` (query, optional): 分页偏移
- **响应**: 与5.1类似的格式

### 6. 系统维护接口

#### 6.1 清理过期预占
- **方法**: `POST`
- **路径**: `/api/inventory/maintenance/cleanup-reservations`
- **描述**: 清理过期的库存预占记录
- **权限**: 系统内部调用
- **响应**:
```json
{
    "code": 200,
    "message": "清理完成",
    "data": {
        "cleaned_reservations": 25,
        "released_quantity": 150
    }
}
```text

#### 6.2 库存一致性检查
- **方法**: `POST`
- **路径**: `/api/inventory/maintenance/consistency-check`
- **描述**: 检查库存数据一致性
- **权限**: 管理员
- **响应**:
```json
{
    "code": 200,
    "message": "检查完成",
    "data": {
        "total_skus": 1000,
        "inconsistent_skus": 2,
        "details": [
            {
                "sku_id": "SKU001003",
                "issue": "reserved_quantity > total_quantity",
                "suggested_action": "调整预占数量"
            }
        ]
    }
}
```text

## 错误响应

### 错误格式
```json
{
    "code": 400,
    "message": "库存不足",
    "error_code": "INSUFFICIENT_INVENTORY",
    "details": {
        "sku_id": "SKU001001",
        "requested": 10,
        "available": 5
    },
    "timestamp": "2025-09-15T10:30:00Z"
}
```text

### 常见错误码
- `INSUFFICIENT_INVENTORY`: 库存不足
- `RESERVATION_EXPIRED`: 预占已过期
- `RESERVATION_NOT_FOUND`: 预占记录不存在
- `SKU_NOT_FOUND`: SKU不存在
- `INVALID_QUANTITY`: 数量无效
- `PERMISSION_DENIED`: 权限不足

## 事件通知

### 库存变动事件
库存操作会触发相应的事件，供其他模块订阅：

1. **inventory.stock.reserved** - 库存预占事件
2. **inventory.stock.released** - 库存释放事件  
3. **inventory.stock.deducted** - 库存扣减事件
4. **inventory.stock.adjusted** - 库存调整事件
5. **inventory.stock.low_warning** - 库存不足预警事件

### 事件格式示例
```json
{
    "event_type": "inventory.stock.reserved",
    "event_id": "evt_12345",
    "timestamp": "2025-09-15T10:30:00Z",
    "data": {
        "sku_id": "SKU001001",
        "quantity": 2,
        "reservation_id": "res_12345",
        "user_id": 123
    }
}
```text

## 性能要求

- **查询响应时间**: < 100ms
- **操作响应时间**: < 200ms
- **并发支持**: 1000+ TPS
- **数据一致性**: 强一致性（库存操作）

## 安全要求

- JWT认证必须
- 敏感操作记录审计日志
- 权限分级控制
- 防止恶意库存操作

---

## 相关文档

### 本模块文档
- [模块概述](./overview.md) - 库存管理模块整体介绍
- [需求规格说明书](./requirements.md) - 详细的功能需求和业务规则
- [系统设计文档](./design.md) - 架构设计和技术选型
- [实现指南](./implementation.md) - 具体的实现细节和代码结构
- [API实现文档](./api-implementation.md) - 详细的API端点实现和使用说明
- [模块快速指南](./README.md) - 快速开始和使用指南

### 架构和标准文档
- [架构设计 - 表模块映射](../../architecture/table-module-mapping.md)
- [API设计标准](../../standards/api-standards.md)
