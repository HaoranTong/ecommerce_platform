# social-features 模块 API 规范

---
title: "social-features 模块 API 规范"
version: "v1.0.0"
status: "draft"
created: "2025-10-25"
updated: "2025-10-25"
owner: "Growth Experience API 团队"
dependencies:
	- "docs/standards/api-standards.md"
	- "docs/design/modules/social-features/design.md"
labels:
	- "social-features"
	- "api-specification"
	- "restful"
---

## 1. 文档信息与对齐

| 项目 | 值 |
|------|----|
| 模块名称 | 社交功能模块 (social-features) |
| API 版本 | v1 |
| 文档版本 | v1.0.0 |
| 设计对齐 | [design.md](./design.md) §5 接口设计 |

## 2. 基础信息与约束

- 基础路径: `/api/v1/social-features/`
- 认证方式: JWT Bearer Token（匿名事件接口可选）
- 数据格式: 请求/响应使用 `application/json; charset=utf-8`
- 版本策略: 路径携带主版本号，非兼容变更发布 `/api/v2` 并保留旧版本 6 个月
- 幂等性: 带 `Idempotency-Key` 的 POST 接口需实现幂等

统一响应结构：

```json
{
	"success": true,
	"code": 200,
	"message": "ok",
	"data": {},
	"error": null,
	"metadata": {
		"request_id": "req-20251025-0001",
		"api_version": "v1"
	}
}
```

## 3. 数据模型概要

- **ShareCreateRequest**: `resource_type (enum)`, `resource_id`, `channel (enum)`, `metadata?`
- **ShareResponse**: `share_id`, `share_code`, `share_url`, `qr_code_url`, `status`, `expires_at`
- **ShareEventCreateRequest**: `share_code`, `event_type (enum)`, `session_id`, `actor_user_id?`, `order_id?`, `client(ip,user_agent,device_id)`
- **ReferralResponse**: `referral_id`, `inviter_user_id`, `invitee_user_id`, `status`, `first_order_id?`, `reward_status`
- **RewardResponse**: `reward_id`, `reward_type`, `value`, `status`, `claimed_at?`, `expires_at?`
- **DailyMetricsResponse**: `stat_date`, `channel`, `resource_type`, `resource_id`, `share_count`, `click_count`, `register_count`, `first_order_count`, `reward_cost`

字段类型与长度界限详见 [design.md §3 数据模型](./design.md)。

## 4. 端点列表

| 方法 | 路径 | 描述 | 认证 | 权限 | 状态 |
|------|------|------|------|------|------|
| POST | /api/v1/social-features/shares | 创建分享链接 | Bearer | 登录用户 | 📋 Planned |
| GET | /api/v1/social-features/shares | 查询我的分享链接（分页） | Bearer | 登录用户 | 📋 Planned |
| GET | /api/v1/social-features/shares/{share_id} | 获取分享详情与统计 | Bearer | 分享所有者/管理员 | 📋 Planned |
| POST | /api/v1/social-features/share-events | 记录分享事件（支持匿名） | 可选 Bearer | 匿名/登录均可 | 📋 Planned |
| POST | /api/v1/social-features/referrals | 创建/更新邀请关系（内部服务调用） | Bearer(Service) | 系统 | 📋 Planned |
| PATCH | /api/v1/social-features/referrals/{referral_id}/status | 人工调整邀请状态 | Bearer | 管理员 | 📋 Planned |
| GET | /api/v1/social-features/rewards/pending | 查询待领取奖励 | Bearer | 登录用户 | 📋 Planned |
| POST | /api/v1/social-features/rewards/{reward_id}/claim | 领取奖励 | Bearer | 登录用户 | 📋 Planned |
| GET | /api/v1/social-features/admin/metrics/daily | 查询日指标 | Bearer | 管理员 | 📋 Planned |
| GET | /api/v1/social-features/admin/violations | 违规记录查询 | Bearer | 管理员 | 📋 Planned |

## 5. 接口详情

### 5.1 创建分享链接

- **方法**: POST
- **路径**: `/api/v1/social-features/shares`
- **认证/权限**: 登录用户；需具备分享功能开关权限
- **请求体**:

```json
{
	"resource_type": "product",
	"resource_id": "SKU-20251025",
	"channel": "wechat",
	"metadata": {
		"entry": "product_detail",
		"utm_campaign": "double11"
	}
}
```

- **响应** `201 Created`:

```json
{
	"success": true,
	"code": 201,
	"message": "分享链接创建成功",
	"data": {
		"share_id": 1001,
		"share_code": "SHR8Y1ZK",
		"share_url": "https://example.com/s/SHR8Y1ZK",
		"qr_code_url": "https://cdn.example.com/qrcode/SHR8Y1ZK.png",
		"status": "active",
		"expires_at": "2025-11-24T10:00:00Z"
	}
}
```

- **失败** `409 Conflict`：资源禁止分享

```json
{
	"success": false,
	"code": 409,
	"message": "该商品暂不支持分享",
	"error": {
		"code": "SOCIAL_103",
		"details": {
			"resource_id": "SKU-20251025"
		}
	}
}
```

### 5.2 分享事件采集

- **方法**: POST
- **路径**: `/api/v1/social-features/share-events`
- **认证**: 可选（匿名点击无需 token）
- **请求体**:

```json
{
	"share_code": "SHR8Y1ZK",
	"event_type": "click",
	"session_id": "f7d5c1ab-6afe-4b6e-b172-ff23e0a9d0a1",
	"client": {
		"ip": "203.0.113.24",
		"user_agent": "Mozilla/5.0",
		"device_id": "ios-uuid"
	}
}
```

- **响应** `202 Accepted`:

```json
{
	"success": true,
	"code": 202,
	"message": "事件已接收",
	"data": {
		"share_id": 1001,
		"event_id": 90001,
		"deduplicated": false
	}
}
```

### 5.3 查询分享详情

- **方法**: GET
- **路径**: `/api/v1/social-features/shares/{share_id}`
- **响应** `200 OK`:

```json
{
	"success": true,
	"code": 200,
	"message": "ok",
	"data": {
		"share_id": 1001,
		"share_code": "SHR8Y1ZK",
		"resource_type": "product",
		"resource_id": "SKU-20251025",
		"channel": "wechat",
		"status": "active",
		"expires_at": "2025-11-24T10:00:00Z",
		"metrics": {
			"clicks": 128,
			"registers": 34,
			"first_orders": 12,
			"rewards_dispatched": 10
		}
	}
}
```

### 5.4 创建/更新邀请关系（内部）

- **方法**: POST
- **路径**: `/api/v1/social-features/referrals`
- **认证**: 服务账号（系统内部调用）
- **请求体**:

```json
{
	"inviter_user_id": 5001,
	"invitee_user_id": 6200,
	"share_code": "SHR8Y1ZK",
	"activity_id": "CAMP-202510",
	"event": "registered"
}
```

- **响应** `200 OK`:

```json
{
	"success": true,
	"code": 200,
	"message": "ok",
	"data": {
		"referral_id": 3001,
		"status": "registered",
		"first_order_id": null,
		"reward_status": "pending"
	}
}
```

### 5.5 奖励领取

- **方法**: POST
- **路径**: `/api/v1/social-features/rewards/{reward_id}/claim`
- **请求体**:

```json
{
	"channel": "app",
	"remark": "用户手动领取"
}
```

- **响应** `200 OK`:

```json
{
	"success": true,
	"code": 200,
	"message": "奖励领取成功",
	"data": {
		"reward_id": 7801,
		"reward_type": "points",
		"value": 200,
		"status": "succeeded",
		"claimed_at": "2025-10-25T11:20:00Z"
	}
}
```

### 5.6 运营指标查询

- **方法**: GET
- **路径**: `/api/v1/social-features/admin/metrics/daily`
- **查询参数**: `start_date` (必填), `end_date` (必填), `channel?`, `resource_type?`, `resource_id?`, `page`, `page_size`
- **响应** `200 OK`:

```json
{
	"success": true,
	"code": 200,
	"message": "ok",
	"data": {
		"items": [
			{
				"stat_date": "2025-10-24",
				"channel": "wechat",
				"resource_type": "campaign",
				"resource_id": "CAMP-202510",
				"share_count": 560,
				"click_count": 2380,
				"register_count": 420,
				"first_order_count": 180,
				"reward_cost": "1280.50"
			}
		],
		"pagination": {
			"page": 1,
			"page_size": 50,
			"total": 12
		}
	}
}
```

## 6. 错误码

| 错误码 | HTTP 状态 | 描述 | 说明 |
|--------|-----------|------|------|
| SOCIAL_100 | 400 | 请求参数无效 | Schema 校验失败，返回字段错误详情 |
| SOCIAL_101 | 404 | 分享链接不存在 | share_id 或 share_code 未找到 |
| SOCIAL_102 | 403 | 无访问权限 | 非资源所有者或角色未授权 |
| SOCIAL_103 | 409 | 分享资源冲突 | 资源被禁止分享或重复创建 |
| SOCIAL_201 | 409 | 邀请关系冲突 | 被邀请人已绑定其他邀请人 |
| SOCIAL_202 | 409 | 奖励状态异常 | 重复领取或奖励失效 |
| SOCIAL_301 | 429 | 触发限流或风控 | 返回重试时间 `retry_after` |
| SOCIAL_500 | 500 | 内部服务错误 | 记录 request_id 以便排查 |

错误响应示例：

```json
{
	"success": false,
	"code": 429,
	"message": "触发限流，请稍后重试",
	"error": {
		"code": "SOCIAL_301",
		"details": {
			"retry_after": 30
		}
	}
}
```

## 7. 安全与合规

- 分享事件接口对 IP + session 实施限流，默认 150 req / 5 min
- 管理员接口需二次验证（依赖 `user_auth` 模块）
- 所有响应头必携带 `X-Request-ID`，供日志追踪
- 记录审计日志：创建分享、奖励发放、违规处理必须写入审计表

## 8. 变更日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2025-10-25 | v1.0.0 | 首次发布，覆盖分享、事件、邀请、奖励、指标相关端点定义 |
