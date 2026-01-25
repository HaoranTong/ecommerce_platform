<!-- 文档用于跟踪 social-features 模块从设计到上线的实施细节 -->

# social-features 模块实施记录

📅 **创建日期**: 2025-10-25  
� **负责团队**: Growth Experience 团队  
🔄 **最后更新**: 2025-10-25  
📊 **整体进度**: 10%（设计完成，开发待启动）

## 1. 实施概述

- **当前状态**: 准备中（需求冻结，API 规范锁定）
- **完成功能**: 文档体系、数据模型、API 设计
- **待实施**: 代码开发、数据库迁移、异步任务、监控告警
- **技术债务**: 无已知债务，等待开发阶段评估

### 关键里程碑

| 日期 | 里程碑 | 状态 | 备注 |
|------|--------|------|------|
| 2025-10-18 | 完成业务需求澄清 | ✅ | 与产品、运营对齐目标指标 |
| 2025-10-25 | 设计文档冻结 | ✅ | README/overview/requirements/design/api-spec 全量完成 |
| 2025-11-05 | 启动开发冲刺 | 📋 Planned | 完成开发前准备与任务拆分 |
| 2025-11-19 | 开发完成进入测试 | 📋 Planned | 包含单元/集成/契约测试 |
| 2025-11-26 | 预发布验证 | � Planned | 压测+灰度发布计划 |

## 2. 代码实施计划

### 模块目录布局（计划）
```
app/modules/social_features/
├── __init__.py
├── router.py                # 路由与依赖声明
├── schemas.py               # Pydantic DTOs
├── service.py               # 业务服务层
├── repository.py            # ORM 访问封装
├── models.py                # SQLAlchemy 实体
├── tasks.py                 # Celery 异步任务
├── dependencies.py          # DI 工厂
├── events.py                # 事件发布/订阅
├── exceptions.py            # 领域异常定义
└── validators.py            # 复杂校验逻辑
```

### 核心组件实施要点

- `router.py`: 组装子路由与速率限制依赖，暴露 `/shares`, `/share-events`, `/referrals`, `/rewards`, `/admin` 等前缀。
- `schemas.py`: 复用 `design.md` 数据字典，确保请求体和响应模型与 `api-spec.md` 一致。
- `service.py`: 拆分 `ShareService`, `ReferralService`, `RewardService`, `MetricsService`，以接口职责为单位。
- `repository.py`: 使用 SQLAlchemy 2.0 ORM style（`async_session`），封装常用查询 + 写入，统一事务控制。
- `tasks.py`: 定义 `dispatch_reward_task`, `sync_referral_status_task`，落地异步补偿与对外同步。
- `events.py`: 使用 `event_bus.publish/subscribe`，处理 `social.share_event.received` 与 `member.reward_issued`。
- `exceptions.py`: 对应错误码 `SOCIAL_100~SOCIAL_500`，继承 `PlatformException`，在路由层统一捕获转换。

## 3. 数据与迁移实施

- **表结构**: `social_share`, `social_share_event`, `social_referral`, `social_reward`, `social_violation`, `social_share_aggregate`。
- **迁移策略**: 编写两阶段 Alembic 脚本
  1. `2025-11-05_init_social_features` 创建核心表及索引
  2. `2025-11-08_add_aggregates_and_views` 添加聚合视图与物化视图刷新任务
- **索引规划**: `social_share` 按 `user_id`, `resource_type`, `resource_id` 建复合索引；`social_share_event` 使用 `(share_id,event_type,occurred_at)`。
- **数据初始化**: 预置热门渠道配置、违规关键词列表，脚本位于 `tools/seed_social_features.py`（待实现）。

## 4. 集成实施

- **用户中心** (`user_auth`): 引入 `UserProfileClient` 获取邀请人实名状态。
- **会员系统** (`member_system`): 通过 gRPC `RedeemReward` 接口发放积分/优惠券，失败走 Celery 重试。
- **营销活动** (`marketing_campaigns`): 同步活动配置，限制邀请规则与奖励上限。
- **通知服务** (`notification_service`): 发布 `InviteeFirstOrder` 事件后推送消息。
- **数据分析**: 通过 `Kafka` topic `social.feature.metrics` 输出实时事件，供埋点系统消费。

## 5. 测试实施计划

- **单元测试**: 覆盖服务层和仓储层关键逻辑，使用 pytest + async fixtures，目标覆盖率 ≥ 85%。
- **集成测试**: 借助 FastAPI TestClient + 测试数据库，验证 API 整体行为、权限和错误码。
- **契约测试**: 使用 `schemathesis` 校验 `api-spec.md`，持续集成流水线执行。
- **性能测试**: JMeter 脚本模拟分享高峰，确保 P95 延迟达标；重点关注 `share-events` 吞吐与 Redis 限流表现。
- **安全测试**: 注入攻击、越权场景、限流绕过等，联合安全团队复核。

## 6. 部署与运维

- **配置项**: 在 `app/core/settings.py` 引入 `SOCIAL_FEATURES_ENABLED`, `SOCIAL_FEATURES_RATE_LIMIT`, `SOCIAL_REWARD_TASK_QUEUE`。
- **环境变量**: `SOCIAL_FEATURES_REDIS_PREFIX`, `SOCIAL_FEATURES_EVENT_TOPIC`, `SOCIAL_FEATURES_REWARD_TIMEOUT`。
- **监控告警**:
  - Prometheus 指标：分享创建成功率、邀请转化率、奖励发放失败数、限流命中次数。
  - 日志：结构化日志（包含 `request_id`, `share_code`），违规事件单独打标签。
  - 告警规则：奖励发放失败 5 分钟内 > 20 次触发 PagerDuty。
- **灰度发布**: 先行开启 10% 用户分享功能，观察 24 小时再全量；奖励发放模块提供安全开关。

## 7. 风险与应对

- **高并发写入**: 分享事件写入量大 → 使用批量异步入库 + Redis 去重，预留扩展到 ClickHouse 的接口。
- **奖励成本控制**: 奖励发放需实时核对活动预算 → 与营销系统建立额度校验，失败立即回滚。
- **合规风险**: 需监控违规内容 → 构建敏感词过滤与人工审核流程。

## 8. 知识沉淀

- **经验**: 在设计阶段提前锁定错误码与事件格式，降低后续契约变更成本。
- **改进**: 计划在开发期同步编写 Swagger 示例，提前让前端联调 mock。
- **最佳实践**: 使用 `Idempotency-Key` 保障分享创建幂等；事件消费与数据库写入保持事务一致性。

## 9. 后续待办

- [ ] 完成任务拆分并录入 Jira（SOCIAL-101 ~ SOCIAL-118）
- [ ] 编写 Alembic 首版迁移脚本草稿并走 DB review
- [ ] 建立 Redis 限流与幂等 POC，验证配置可行性
- [ ] 与数据团队确认指标字段与上报频率

## 10. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2025-10-25 | v0.1 | 初始化实施计划，结合设计文档输出开发路线 | Zhang Wei |
