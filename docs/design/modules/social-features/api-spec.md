---
title: "social-features 模块 API 规范"
version: "v0.4.0"
status: "Draft"
created: "2025-10-18"
updated: "2025-10-25"
owner: "Growth Experience API 团队"
dependencies:
	- "../../standards/api-standards.md"
	- "./design.md"
labels:
	- "api"
	- "spec"
---

# social-features 模块 API 规范

## 1. 文档信息与对齐

| 项目 | 值 |
|------|----|
| 模块名称 | social-features |
| API 版本 | v1 |
| 文档版本 | v0.4.0 |
| 设计参考 | [design.md](./design.md) §5 接口设计 |

## 2. 基础信息与约束

- 基础路径: `/api/v1/social-features/`
- 认证方式: JWT Bearer Token（`POST /share-events` 支持匿名，但需提供 client 指纹）
- 数据格式: `application/json; charset=utf-8`
- 版本策略: 在 URL 中维护主版本号；若发生不兼容变更，新增 `/api/v2/social-features`；旧版本保留 6 个月
- 幂等策略:
	- `POST /shares` 支持 `Idempotency-Key`
	- `POST /share-events` 使用 session 去重，重复返回 `deduplicated=true`
	- 其他写操作默认非幂等

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

## 3. 数据模型概览

- `ShareCreateRequest`: `resource_type`(`enum`), `resource_id`, `channel`(`enum`), `metadata?`
- `ShareResponse`: `share_id`, `share_code`, `share_url`, `qr_code_url`, `status`, `expires_at`
- `ShareEventCreateRequest`: `share_code`, `event_type`(`enum`), `session_id`, `actor_user_id?`, `order_id?`, `client{ip,user_agent,device_id}`
- `ReferralUpsertRequest`: `inviter_user_id`, `invitee_user_id`, `share_code`, `activity_id`, `event`
- `RewardResponse`: `reward_id`, `reward_type`, `value`, `status`, `claimed_at?`, `expires_at?`
- `DailyMetricsResponse`: `stat_date`, `channel`, `resource_type`, `resource_id`, `share_count`, `click_count`, `register_count`, `first_order_count`, `reward_cost`

详细字段与约束参见 [design.md](./design.md#3-数据模型)。

## 4. 端点列表

| 方法 | 路径 | 名称 | 描述 | 认证 | 权限 | 幂等 | 状态 |
|------|------|------|------|------|------|------|------|
| POST | /shares | CreateShare | 创建分享链接 | Bearer | 登录用户 | ✅ | 📋 Planned |
| GET | /shares | ListShares | 查询我的分享列表 | Bearer | 登录用户 | ❌ | 📋 Planned |
| GET | /shares/{share_id} | GetShareDetail | 获取分享详情与统计 | Bearer | 分享所有者/管理员 | ❌ | 📋 Planned |
| POST | /share-events | IngestShareEvent | 记录分享事件 | 可选 Bearer | 匿名/登录 | 部分 (去重) | 📋 Planned |
| POST | /referrals | UpsertReferral | 创建或更新邀请关系（内部调用） | Bearer (Service) | 系统 | ✅ | 📋 Planned |
| PATCH | /referrals/{referral_id}/status | UpdateReferralStatus | 人工调整邀请状态 | Bearer | 管理员 | ❌ | 📋 Planned |
| GET | /rewards/pending | ListPendingRewards | 查询待领取奖励 | Bearer | 登录用户 | ❌ | 📋 Planned |
| POST | /rewards/{reward_id}/claim | ClaimReward | 领取奖励 | Bearer | 登录用户 | ❌ | 📋 Planned |
| GET | /admin/metrics/daily | GetDailyMetrics | 查询日指标 | Bearer | 管理员 | ❌ | 📋 Planned |
| GET | /admin/violations | ListViolations | 查询违规记录 | Bearer | 管理员 | ❌ | 📋 Planned |

## 5. 接口详情

### 5.1 `POST /shares` — 创建分享链接

- **请求头**: `Idempotency-Key`(必填), `Authorization: Bearer <token>`
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

- **响应 201**:

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

- **错误**: `409` (`SOCIAL_103`) 资源不可分享；`400` (`SOCIAL_100`) 参数错误。

### 5.2 `GET /shares` — 查询分享列表

- **查询参数**: `page` 默认 1, `page_size` ≤ 50, `status?`, `channel?`。
- **响应 200**:

```json
{
	"success": true,
	"code": 200,
	"message": "ok",
	"data": {
		"items": [
			{
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
					"first_orders": 12
				}
			}
		],
		"pagination": {
			"page": 1,
			"page_size": 20,
			"total": 240
		}
	}
}
```

### 5.3 `GET /shares/{share_id}` — 获取分享详情

- **路径参数**: `share_id` (int)
- **响应**: 包含基本信息、渠道指标、最近事件列表。

### 5.4 `POST /share-events` — 记录分享事件

- **请求体**:

```json
{
	"share_code": "SHR8Y1ZK",
	"event_type": "click",
	"session_id": "f7d5c1ab-6afe-4b6e-b172-ff23e0a9d0a1",
	"actor_user_id": null,
	"order_id": null,
	"client": {
		"ip": "203.0.113.24",
		"user_agent": "Mozilla/5.0",
		"device_id": "ios-uuid"
	}
}
```

- **响应 202**:

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

- **错误**: `404` (`SOCIAL_101`) 分享不存在；`429` (`SOCIAL_301`) 触发限流；`400` (`SOCIAL_100`) 参数错误。

### 5.5 `POST /referrals` — 创建/更新邀请关系

- **用途**: 服务间调用，绑定注册事件与分享。
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

- **响应**: 返回最新邀请状态与冲突信息。
- **错误**: `409` (`SOCIAL_201`) 邀请关系冲突；`403` (`SOCIAL_102`) 无权限调用。

### 5.6 `POST /rewards/{reward_id}/claim` — 奖励领取

- **请求体**:

```json
{
	"channel": "app",
	"remark": "用户手动领取"
}
```

- **响应 200**:

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

- **错误**: `409` (`SOCIAL_202`) 奖励状态异常；`403` (`SOCIAL_102`) 非资源所有者。

### 5.7 `GET /admin/metrics/daily` — 日指标查询

- **查询参数**: `start_date`、`end_date` (必填, YYYY-MM-DD)；`channel?`, `resource_type?`, `resource_id?`, `page`, `page_size`。
- **响应 200**: 返回 `items` 数组与分页信息。
- **CSV 导出**: 通过 `Accept: text/csv` 触发。

### 5.8 `GET /admin/violations` — 违规列表

- **功能**: 支持按 `status`, `rule_code`, `date_range` 过滤；支持分页与导出。
- **响应字段**: `violation_id`, `share_id`, `rule_code`, `severity`, `status`, `blocked_reward_ids`, `operator`, `updated_at`。

## 6. 错误码定义

| 错误码 | HTTP 状态 | 描述 | 常见触发场景 |
|--------|-----------|------|--------------|
| `SOCIAL_100` | 400 | 请求参数无效 | 缺少必填字段、格式不正确 |
| `SOCIAL_101` | 404 | 分享链接不存在或已过期 | share_code/ID 不存在 |
| `SOCIAL_102` | 403 | 无访问权限 | 非资源所有者或缺少管理员权限 |
| `SOCIAL_103` | 409 | 分享资源冲突 | 资源禁用分享、重复创建 |
| `SOCIAL_201` | 409 | 邀请关系冲突 | 被邀请人已绑定其他邀请人 |
| `SOCIAL_202` | 409 | 奖励状态异常 | 重复领取、奖励过期或被阻断 |
| `SOCIAL_301` | 429 | 限流或风控触发 | IP/session 超过阈值 |
| `SOCIAL_500` | 500 | 内部服务错误 | 数据库/外部服务异常 |

错误响应示例：

```json
{
	"success": false,
	"code": 409,
	"message": "邀请关系已存在",
	"error": {
		"code": "SOCIAL_201",
		"details": {
			"invitee_user_id": 6200
		}
	},
	"metadata": {
		"request_id": "req-20251025-0042"
	}
}
```

## 7. 安全与速率限制

- 所有非匿名端点必须传入 `Authorization` header。
- 管理员端点额外要求 `X-Admin-Role` header 存在且角色 >= `admin`。
- 默认限流：普通用户 60 req/min；管理员端 30 req/min；匿名事件 150 req/5min（按 IP+session）。
- 所有响应头带 `X-Request-ID`、`X-RateLimit-Remaining` 等信息。

## 8. 合规与审计

- 记录关键操作日志：人工调整邀请、奖励领取、违规状态变更。
- 数据保留：事件数据保留 365 天，违规日志 730 天。
- 敏感字段（IP、User-Agent）在响应中脱敏，不向普通用户暴露。

## 9. 变更日志

| 日期 | 版本 | 说明 | 作者 |
|------|------|------|------|
| 2025-10-18 | v0.2 | 初版接口清单 | Chen Hao |
| 2025-10-21 | v0.3 | 增加错误码、幂等策略 | Zhang Wei |
| 2025-10-25 | v0.4 | 对齐文档标准，补充详细示例与安全约束 | Zhang Wei |
