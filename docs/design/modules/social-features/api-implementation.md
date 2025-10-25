# social-features 模块 API 实施记录

## 1. 文档概览

- **设计基线**: 对齐 `api-spec.md@v1.0.0`
- **当前阶段**: `Design Freeze`，预计 2025-11-05 启动开发冲刺
- **负责人**: Growth Experience API 小组（主责: Zhang Wei）
- **协同团队**: 前端 Web/小程序组、数据分析组、Member System 团队

## 2. 实施进度一览

| 模块 | 接口 | FastAPI 处理函数 | 状态 | 计划交付 | 负责人 |
|------|------|------------------|------|----------|--------|
| 分享 | `POST /shares` | `create_share()` | 📋 Planned | 2025-11-07 | Zhang Wei |
| 分享 | `GET /shares` | `list_shares()` | 📋 Planned | 2025-11-08 | Liu Yan |
| 分享 | `GET /shares/{share_id}` | `get_share_detail()` | 📋 Planned | 2025-11-08 | Liu Yan |
| 事件 | `POST /share-events` | `ingest_share_event()` | 📋 Planned | 2025-11-10 | Chen Hao |
| 邀请 | `POST /referrals` | `upsert_referral()` | 📋 Planned | 2025-11-12 | Chen Hao |
| 邀请 | `PATCH /referrals/{id}/status` | `update_referral_status()` | 📋 Planned | 2025-11-13 | Chen Hao |
| 奖励 | `GET /rewards/pending` | `list_pending_rewards()` | 📋 Planned | 2025-11-14 | Wang Jie |
| 奖励 | `POST /rewards/{id}/claim` | `claim_reward()` | 📋 Planned | 2025-11-14 | Wang Jie |
| 指标 | `GET /admin/metrics/daily` | `get_daily_metrics()` | 📋 Planned | 2025-11-18 | Zhang Wei |
| 运营 | `GET /admin/violations` | `list_violations()` | 📋 Planned | 2025-11-19 | Zhang Wei |

> 状态说明：📋 Planned = 已落设计、待开发；✅ Done = 已合并主干；🚧 In progress = 开发中。

## 3. 集成与技术要点

- **认证授权**: 重用 `app.shared.security.jwt.get_current_user`；管理员接口附加 `require_role("admin")`。
- **速率限制**: 在 `router.py` 中使用平台限流依赖 `RateLimiter`，对匿名事件接口配置 `key_func=client_fingerprint`。
- **幂等控制**: `create_share` 支持 `Idempotency-Key`，在 Redis 写入 24 小时 Key；冲突返回 `409`。
- **事件投递**: `ingest_share_event` 通过 `event_bus.publish("social.share_event.received", payload)` 触发异步消费者；消息序列化遵循 design §6。
- **奖励发放**: `claim_reward` 调用 `member_system` RPC 客户端；失败时写入 `reward_jobs` 表并交由 Celery 重试。
- **指标查询**: `get_daily_metrics` 调 `social_feature_metrics_view` 物化视图，提供分页和过滤。

## 4. 测试与质量门槛

- **单元测试**: 每个处理函数配套 `tests/modules/social_features/test_{feature}.py`，覆盖正常/异常场景，行覆盖率 ≥ 85%。
- **契约测试**: 使用 `schemathesis` 基于 `api-spec.md` 自动化回归，重点验证错误码与幂等行为。
- **性能基准**: `create_share`、`ingest_share_event` 需在 50ms P95 内（预热后），`get_daily_metrics` P95 < 120ms。
- **安全扫描**: 合并前执行 `bandit`, `pip-audit`, OWASP API 规范检查清单。

## 5. 风险与缓解

- Redis 幂等键过期策略需与分享有效期一致 → 开发阶段引入集成测试验证。
- 奖励领取依赖外部 RPC，失败回滚方案需重点联调 → 预留熔断与补偿队列。
- 管理端指标可能跨日大数据量查询 → SQL 加索引 + 定时刷新物化视图，必要时引入分页游标。

## 6. 待办清单

- [ ] 生成 `openapi` 片段并同步至 `docs/standards/openapi.yaml`
- [ ] 与前端确认 `share_url`、`qr_code_url` 命名和静态资源 CDN 方案
- [ ] 与安全团队复核匿名事件接口的限流参数
- [ ] 编写 API 使用手册并推送至 `docs/development/api-guides/social-features.md`
