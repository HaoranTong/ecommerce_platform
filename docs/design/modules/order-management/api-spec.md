---
title: "order-management - API规范文档"
version: "1.0.0"
status: "draft"
created: "2025-10-14"
updated: "2025-10-14"
owner: "交易域 · 订单管理团队"
dependencies:
  - "../../standards/document-management-standards.md"
  - "../../standards/api-standards.md"
  - "../../standards/naming-conventions-standards.md"
  - "../../architecture/application-architecture.md"
labels:
  - "module: order-management"
  - "layer: L2"
---

# Order Management Module - API 规范（A10）

## 依赖标准
- [文档管理标准](../../standards/document-management-standards.md)
- [API 设计标准](../../standards/api-standards.md)
- [命名规范标准](../../standards/naming-conventions-standards.md)
- [业务架构](../../architecture/business-architecture.md)
- [应用架构](../../architecture/application-architecture.md)

## 概述
本文档定义 order-management 模块对外提供的 HTTP API 接口契约，覆盖鉴权机制、端点清单、请求/响应结构、错误码以及幂等性与重试策略，确保客户端与服务端实现保持一致。

## 具体标准
- 所有端点统一挂载在 `/api/v1/order-management` 前缀下，路径使用 kebab-case。
- 认证遵循 JWT Bearer Token 标准，权限控制基于 RBAC 角色模型。
- 请求和响应内容均为 `application/json; charset=utf-8`，时间字段使用 ISO8601。
- 幂等接口需在规范中标注策略；非幂等接口禁止自动重试。
- 错误码前缀统一使用 `OM_`，并说明重试策略与诊断信息。
- 文档内的示例遵循统一响应包装结构（`success`、`code`、`message`、`data`、`metadata`）。

# Order Management Module - API 规范（A10）

## 文档元信息

📦 **模块**: order-management  
📄 **文档版本**: v1.0.0  
🕒 **最后更新**: 2025-10-14  
🧑‍💻 **维护责任人**: 交易域 · 订单管理团队

---

## 1. API 概览

- **服务描述**: 提供订单全生命周期管理能力（创建、查询、状态维护、统计）。
- **Base URL**: `/api/v1/order-management`
- **协议**: HTTPS / JSON (`Content-Type: application/json; charset=utf-8`)
- **字符编码**: UTF-8
- **幂等性策略**: 见第 3 节端点清单；所有幂等接口通过「业务主键 + 请求参数」保证；非幂等接口禁止重试。
- **分页约定**: `page` 从 1 开始，`page_size` ∈ [1,100]，返回 `total_count`、`page`、`page_size`。
- **时间格式**: ISO8601 (`YYYY-MM-DDTHH:mm:ssZ`)

---

## 2. 认证与授权要求

### 2.1 认证方式

| 项目 | 说明 |
|------|------|
| 认证机制 | JWT Bearer Token（由 `user_auth` 模块签发） |
| Header | `Authorization: Bearer <JWT_TOKEN>` |
| Token 载荷 | `user_id`, `username`, `role`, `exp`, `iat` |
| Token 过期 | Access Token 24 小时；Refresh Token 7 天 |
| 撤销策略 | 退出登录时加入 Redis 黑名单 |

### 2.2 权限模型（RBAC）

| 角色 | 描述 | 权限说明 |
|------|------|----------|
| `user` | 普通用户 | 仅能访问/管理自己的订单 |
| `admin` | 管理员 | 可访问所有订单，执行管理操作 |
| `super_admin` | 超级管理员 | 拥有最高权限，可进行统计、状态更新 |
| `system` | 系统服务账号 | 仅用于内部回调，不对外开放 |

🔒 **访问控制**:
- 所有接口必须携带有效 JWT。
- `user` 角色仅能操作自己订单（通过依赖 `validate_order_access` 校验）。
- `admin/super_admin` 可以按 `user_id` 过滤订单并执行状态更新、统计查看等高级操作。

---

## 3. 接口列表

| # | 接口名称 | 方法 | 路径 | 描述 | 角色权限 | 幂等性 |
|---|----------|------|------|------|----------|--------|
| 1 | 创建订单 | POST | `/orders` | 创建新订单并预占库存 | `user` | ❌ 非幂等 |
| 2 | 查询订单列表 | GET | `/orders` | 按状态/分页获取订单列表 | `user`（仅本人）/`admin` | ✅ 幂等 |
| 3 | 获取订单详情 | GET | `/orders/{order_id}` | 获取单个订单的详细信息 | `user`（仅本人）/`admin` | ✅ 幂等 |
| 4 | 更新订单状态 | PATCH | `/orders/{order_id}/status` | 管理端更新订单状态 | `admin`/`super_admin` | 🔁 条件幂等（同状态重复请求返回最新状态） |
| 5 | 取消订单 | POST | `/orders/{order_id}/cancel` | 取消待支付订单并释放库存 | `user`（仅本人）/`admin` | ❌ 非幂等 |
| 6 | 获取订单商品项 | GET | `/orders/{order_id}/items` | 获取订单内商品项快照 | `user`（仅本人）/`admin` | ✅ 幂等 |
| 7 | 获取状态历史 | GET | `/orders/{order_id}/history` | 查询订单状态流转历史 | `user`（仅本人）/`admin` | ✅ 幂等 |
| 8 | 获取订单统计 | GET | `/statistics` | 获取订单数量与金额统计 | `admin`/`super_admin`（可指定 user_id） | ✅ 幂等 |

> 所有路径均需在业务网关层加上前缀 `/api/v1/order-management`。

---

## 4. 请求参数定义

### 4.1 POST `/orders` — 创建订单

- **Header**: `Authorization: Bearer <JWT>`
- **请求体（OrderCreateRequest）**

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `items` | `OrderItem[]` | 是 | 1 ≤ 长度 ≤ 50，SKU 禁止重复 | 订单商品列表 |
| `shipping_address` | `ShippingAddress` | 是 | - | 收货地址信息 |
| `notes` | `string` | 否 | ≤ 500 字符 | 订单备注 |

**OrderItem**

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `product_id` | `integer` | 是 | > 0 | 商品 ID |
| `sku_id` | `integer` | 是 | > 0 | SKU ID |
| `quantity` | `integer` | 是 | 1 ≤ quantity ≤ 999 | 购买数量 |

**ShippingAddress**

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `recipient` | `string` | 是 | ≤ 100 字符 | 收货人姓名 |
| `phone` | `string` | 是 | ≤ 20 字符 | 联系电话 |
| `address` | `string` | 是 | ≤ 500 字符 | 详细地址 |

### 4.2 GET `/orders` — 查询订单列表

- **Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `status` | `string` (`pending\|paid\|shipped\|delivered\|cancelled\|returned`) | 否 | - | 状态筛选 |
| `user_id` | `integer` | 否 | 当前用户 ID | 仅 `admin`/`super_admin` 可指定其他用户 |
| `page` | `integer` | 否 | 1 | 页码（1-1000） |
| `page_size` | `integer` | 否 | 20 | 每页数量（1-100） |

### 4.3 GET `/orders/{order_id}` — 获取订单详情

- **Path 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `order_id` | `integer` | 是 | 订单主键 ID（≥1） |

- **响应体（OrderResponse）补充字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| `receiver_name` | `string` | 收货人姓名快照 |
| `receiver_phone` | `string` | 收货人联系方式 |

### 4.4 PATCH `/orders/{order_id}/status` — 更新订单状态

- **Path 参数**: 同 4.3
- **请求体（OrderStatusUpdateRequest）**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | `string` (`pending\|paid\|shipped\|delivered\|cancelled\|returned`) | 是 | 目标状态；遵循状态机校验 |
| `remark` | `string` | 否 | 状态变更备注（≤ 500 字符） |

### 4.5 POST `/orders/{order_id}/cancel` — 取消订单

- **Path 参数**: 同 4.3
- **请求体**: 空（取消原因由服务层记录，后续版本可扩展 `reason` 字段）

### 4.6 GET `/orders/{order_id}/items` — 获取订单商品项

- **Path 参数**: 同 4.3
- **Query**: 无

- **响应体（OrderItemResponse[]）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `integer` | 订单项主键 |
| `order_id` | `integer` | 所属订单 ID |
| `product_id` / `sku_id` | `integer` | 商品与 SKU 关联标识 |
| `sku_code` | `string` | SKU 编码快照 |
| `product_name` / `sku_name` | `string` | 商品、规格名称快照 |
| `product_attributes` | `object` | 商品 & SKU 属性快照（JSON） |
| `product_image_url` | `string` | 商品展示图快照 |
| `quantity` / `unit_price` / `total_price` | `integer` / `number` | 购买数量及价格快照 |
| `created_at` | `string` | 创建时间（ISO8601） |

### 4.7 GET `/orders/{order_id}/history` — 获取状态历史

- **Path 参数**: 同 4.3

### 4.8 GET `/statistics` — 获取订单统计

- **Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `user_id` | `integer` | 否 | 当前用户 ID | `admin`/`super_admin` 可指定任意用户；普通用户忽略该参数 |

---

## 5. 响应结构说明

### 5.1 统一成功响应

```json
{
	"success": true,
	"code": 200,
	"message": "操作成功",
	"data": {},
	"metadata": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | `boolean` | 操作是否成功 |
| `code` | `integer` | 业务码（默认 200；创建成功为 201） |
| `message` | `string` | 人类可读提示信息 |
| `data` | `object/array` | 业务数据内容 |
| `metadata` | `object` | 额外元信息（分页、追踪 ID 等） |

### 5.2 统一错误响应

```json
{
	"success": false,
	"code": 400,
	"message": "库存不足",
	"error": {
		"type": "OM_INSUFFICIENT_STOCK",
		"details": [
			{
				"sku_id": 91001,
				"required": 2,
				"available": 0
			}
		]
	}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | `integer` | 对应 HTTP 状态码 |
| `error.type` | `string` | 错误码（见第 6 节） |
| `error.details` | `array` | 错误上下文（字段校验、库存详情等） |

### 5.3 端点响应示例

#### 5.3.1 创建订单成功（201）

```json
{
	"success": true,
	"code": 201,
	"message": "订单创建成功",
	"data": {
		"id": 12001,
		"order_number": "OM202510141230450001",
		"user_id": 9527,
		"status": "pending",
		"subtotal": 299.00,
		"shipping_fee": 0.00,
		"discount_amount": 20.00,
		"total_amount": 279.00,
		"shipping_address": "北京市朝阳区...",
		"receiver_name": "张三",
		"receiver_phone": "13800000000",
		"shipping_method": "express",
		"notes": "请尽快发货",
		"created_at": "2025-10-14T12:30:45Z",
		"updated_at": "2025-10-14T12:30:45Z"
	},
	"metadata": {
		"tracking": {
			"order_number": "OM202510141230450001"
		}
	}
}
```

#### 5.3.2 订单列表（200）

```json
{
	"success": true,
	"code": 200,
	"message": "获取订单列表成功",
	"data": {
		"items": [
			{
				"id": 12001,
				"order_number": "OM202510141230450001",
				"user_id": 9527,
				"status": "paid",
				"subtotal": 299.00,
				"shipping_fee": 0.00,
				"discount_amount": 20.00,
				"receiver_name": "张三",
				"receiver_phone": "13800000000",
				"created_at": "2025-10-14T12:30:45Z",
				"updated_at": "2025-10-14T12:35:02Z"
				"updated_at": "2025-10-14T12:35:02Z"
			}
		],
		"page": 1,
		"total_count": 35
		"total_count": 35
	}
}
```

#### 5.3.3 状态历史（200）

```json
{
	"success": true,
	"code": 200,
	"message": "获取状态变更历史成功",
	"data": [
		{
			"old_status": null,
			"new_status": "pending",
			"remark": "订单创建",
			"operator_id": 9527,
			"created_at": "2025-10-14T12:30:45Z"
		},
		{
			"old_status": "pending",
			"new_status": "paid",
			"remark": "支付成功",
			"operator_id": 0,
			"created_at": "2025-10-14T12:35:02Z"
		}
	]
}
```

#### 5.3.4 统计信息（200）

```json
{
	"success": true,
	"code": 200,
	"message": "获取统计信息成功",
	"data": {
		"total_orders": 1520,
		"pending_orders": 120,
		"paid_orders": 980,
		"shipped_orders": 230,
		"delivered_orders": 150,
		"cancelled_orders": 30,
		"returned_orders": 10,
		"total_amount": 523000.50,
		"completion_rate": 78.5,
		"cancellation_rate": 2.0
	}
}
```

---

## 6. 错误码与重试策略

| 错误码 | HTTP 状态 | 提示信息 | 触发场景 | 重试策略 |
|--------|-----------|----------|----------|----------|
| `OM_NOT_FOUND` | 404 | 订单不存在 | 访问不存在的订单 ID | ❌ 不可重试，检查参数 |
| `OM_PERMISSION_DENIED` | 403 | 无权访问该订单 | 用户访问非本人订单 | ❌ 不可重试 |
| `OM_INSUFFICIENT_STOCK` | 400 | 库存不足 | 订单创建时库存不足 | ✅ 可在补货后重试 |
| `OM_AMOUNT_MISMATCH` | 400 | 订单金额不一致 | 商品快照金额校验失败 | ❌ 不可直接重试（检查请求） |
| `OM_INVALID_STATUS_TRANSITION` | 400 | 非法的状态流转 | 状态更新违反状态机规则 | ❌ 不可重试 |
| `OM_CANNOT_CANCEL` | 400 | 订单无法取消 | 非待支付状态取消 | ❌ 不可重试 |
| `OM_RATE_LIMITED` | 429 | 请求过于频繁 | 触发下单限流或接口限流 | ✅ 等待后重试 |
| `OM_USER_NOT_FOUND` | 404 | 用户不存在 | `user_id` 无效 | ❌ 不可重试 |
| `OM_PRODUCT_NOT_FOUND` | 404 | 商品不存在 | `product_id` 无效 | ❌ 不可重试 |
| `OM_SKU_NOT_FOUND` | 404 | SKU 不存在 | `sku_id` 无效 | ❌ 不可重试 |
| `OM_PRODUCT_UNAVAILABLE` | 400 | 商品不可购买 | 商品状态非 `active` | ❌ 不可重试 |
| `OM_SKU_UNAVAILABLE` | 400 | SKU 不可购买 | SKU 状态非 `is_active` | ❌ 不可重试 |
| `OM_INTERNAL_ERROR` | 500 | 服务内部错误 | 未预期异常 | ✅ 支持熔断策略下的重试（指数退避） |
| `OM_DEPENDENCY_TIMEOUT` | 504 | 依赖服务超时 | 库存/支付等依赖超时 | ✅ 建议 1~3 次指数退避重试 |

> 服务端日志中以 `error.type` 字段记录错误码，便于数据平台统计。

---

## 7. 变更日志

| 版本 | 日期 | 变更描述 | 责任人 |
|------|------|----------|--------|
| v1.0.0 | 2025-10-14 | 首次发布，覆盖 8 个订单管理接口 | 架构团队 |

---

**附录**

- 关联文档：
	- [design.md](./design.md)
	- [requirements.md](./requirements.md)
	- [ORDER_MANAGEMENT_BOUNDARY_ANALYSIS.yaml](../../../ORDER_MANAGEMENT_BOUNDARY_ANALYSIS.yaml)
- 验证命令：
	- `python tools/api_service_mapping_analyzer.py --analyze order_management`
	- `pwsh tools/validate_standards.ps1 -Action full -DocPath docs/design/modules/order-management/api-spec.md`
