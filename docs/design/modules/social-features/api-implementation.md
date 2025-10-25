---
title: "social-features API 实施说明"
version: "v0.3.0"
status: "Planned"
created: "2025-10-23"
updated: "2025-10-25"
owner: "Growth Experience Backend Squad"
dependencies:
	- "./api-spec.md"
	- "./implementation.md"
labels:
	- "api"
	- "implementation"
---

# social-features 模块 API 实施说明

## 1. 概览

- **设计基线**: 对齐 [api-spec.md](./api-spec.md) v0.4.0。
- **目标版本**: API v1 首次上线，覆盖分享、事件、邀请、奖励、运营端 10 个接口。
- **代码位置**: `app/modules/social_features/`（详情见 [implementation.md](./implementation.md) §2）。
- **开发阶段**: 2025-11-05 ~ 2025-11-19 Sprint。

## 2. 路由与服务映射

| API | Router 函数 | Service 方法 | Repository 调用 | 备注 |
|-----|-------------|---------------|-----------------|------|
| `POST /shares` | `create_share` | `ShareService.create_share` | `ShareRepository.create` | 校验资源 + Redis 幂等 |
| `GET /shares` | `list_shares` | `ShareService.list_shares` | `ShareRepository.list_by_user` | 支持分页与过滤 |
| `GET /shares/{id}` | `get_share_detail` | `ShareService.get_detail` | `ShareRepository.fetch_with_metrics` | 包含聚合指标 |
| `POST /share-events` | `ingest_share_event` | `EventService.ingest` | `EventRepository.bulk_insert` | 限流 + 去重，异步事件 |
| `POST /referrals` | `upsert_referral` | `ReferralService.upsert_referral` | `ReferralRepository.upsert` | 服务间鉴权，记录冲突 |
| `PATCH /referrals/{id}/status` | `update_referral_status` | `ReferralService.update_status` | `ReferralRepository.update_status` | 审计日志 |
| `GET /rewards/pending` | `list_pending_rewards` | `RewardService.list_pending` | `RewardRepository.list_pending_by_user` | 分页 |
| `POST /rewards/{id}/claim` | `claim_reward` | `RewardService.claim` | `RewardRepository.mark_claimed` | 触发 Celery 发放 |
| `GET /admin/metrics/daily` | `get_daily_metrics` | `MetricsService.list_daily` | `MetricsRepository.list_daily` | 查询视图，支持 CSV |
| `GET /admin/violations` | `list_violations` | `ViolationService.list` | `ViolationRepository.list` | 含导出 |

## 3. 关键实现说明

### 3.1 认证与权限

- 路由层引入 `Depends(get_current_user)`；管理员接口额外调用 `require_role("admin")`。
- 服务间调用（`POST /referrals`）使用服务账号 JWT + `X-Service-Key` header 校验。

### 3.2 输入校验

- 所有请求模型定义于 `schemas.py`，使用 Pydantic v2；自定义校验器校验 `resource_type`, `channel`, `event_type`。
- `ShareEventCreateRequest` 在模型层进行 IP 格式与 User-Agent 长度校验。

### 3.3 幂等与限流

- `ShareService.create_share`: 使用 Redis `SETNX` 实现幂等，Key=`share:{user_id}:{idem_key}`，TTL=24h。
- `EventService.ingest`: 使用组合 key `event:{share_code}:{session_id}:{event_type}` 进行去重；限流器 `RateLimiter` 实现按 IP+session 维度限制。

### 3.4 数据访问模式

- 统一使用 `AsyncSession` + context manager；写操作包裹在 `Repository.transaction()` 中。
- 列表查询均采用分页 (limit/offset)；管理员指标查询映射到物化视图 `social_share_daily_metrics`。
- 读取传播 `for_update` 锁：在邀请冲突处理时锁定 `social_referral` 记录。

### 3.5 事件与异步

- `EventService` 在写库成功后调用 `events.publish_share_event` 推送 Kafka。
- 奖励领取过程中，`RewardService.claim` 将任务推送至 Celery `social_features_reward` 队列，Worker 调 `member_system`。
- Celery 任务完成后回写状态并发布事件 `social.reward.status_changed`。

### 3.6 日志与监控

- API 层通过 `APIRouter` 中间件写入 `security_logger`，字段：`request_id`, `user_id`, `path`, `status_code`。
- 指标：`
	- `social_features_api_latency_seconds{route=...,method=...}`
	- `social_features_api_error_total{code=...}`
- 限流命中调度 `social_features_rate_limit_rejections_total`。

## 4. 错误处理策略

- 自定义异常 `SocialFeaturesException` 包含 `code`, `http_status`, `message`, `details`。
- 路由层引入异常处理器，将异常映射到统一响应格式。
- 常见错误码参见 [api-spec.md](./api-spec.md#6-错误码定义)。

## 5. 测试覆盖

- **单元测试**: `tests/modules/social_features/test_shares.py` 等；覆盖正常、幂等、限流、权限场景。
- **集成测试**: 使用 `TestClient` + 测试数据库；重点覆盖邀请冲突、奖励领取全流程。
- **契约测试**: `schemathesis run docs/design/modules/social-features/api-spec.yaml`（由 CI 执行）。
- **性能测试**: `tests/perf/social_features_share_events.jmx`，压测目标与要求见 [implementation.md](./implementation.md#5-测试实施计划)。

## 6. 发布检查清单

- [ ] 生成并上传最新 OpenAPI 片段至 `docs/standards/openapi.yaml`。
- [ ] 所有接口添加 `request_id`, `idempotency_key` 日志字段。
- [ ] Kafka 事件 Schema 注册并通过 `schema-registry` 校验。
- [ ] Celery 队列在 staging 环境进行一次端到端演练。
- [ ] 运营后台联调完成，确认指标接口与 CSV 导出无误。

## 7. 风险与缓解

| 风险 | 描述 | 应对 |
|------|------|------|
| Redis 幂等 key 未及时过期 | 可能导致重复分享失败 | 通过扫描任务清理、支持强制刷新接口 |
| Kafka 发布失败 | 事件丢失 | 实现重试队列 + 存储 fallback 表 `social_share_event_outbox` |
| Celery Worker 队列堆积 | 奖励延迟 | 启用自动扩容策略，设定最大重试次数 + 告警 |

## 8. 变更记录

| 日期 | 版本 | 变更内容 | 责任人 |
|------|------|----------|--------|
| 2025-10-23 | v0.1 | 初版路由映射 | Zhang Wei |
| 2025-10-24 | v0.2 | 补充监控、测试说明 | Chen Hao |
| 2025-10-25 | v0.3 | 对齐标准，新增发布清单与风险 | Zhang Wei |
