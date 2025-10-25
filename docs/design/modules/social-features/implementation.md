---
title: "social-features 模块实施记录"
version: "v0.3.0"
status: "Planning"
created: "2025-10-18"
updated: "2025-10-25"
owner: "Growth Experience 开发团队"
dependencies:
  - "./design.md"
  - "./api-implementation.md"
labels:
  - "implementation"
  - "module"
---

# social-features 模块实施记录

📅 **创建日期**: 2025-10-18  
� **责任团队**: Growth Experience 开发小组  
🔄 **最后更新**: 2025-10-25  
📊 **当前进度**: 10%（设计冻结，开发待启动）

## 1. 实施概述

- **状态**: 准备中（需求与设计已冻结，等待 2025-11-05 Sprint 开发启动）。
- **完成功能**: 文档体系、数据模型、接口设计、监控指标定义。
- **待实施**: API 开发、数据库迁移、异步任务、运营后台联调、性能压测。
- **技术债务**: 暂无，开发阶段评估后更新。

### 1.1 项目里程碑

| 日期 | 里程碑 | 状态 | 说明 |
|------|--------|------|------|
| 2025-10-18 | 完成需求澄清 | ✅ | REQ 文档确认 |
| 2025-10-24 | 设计评审通过 | ✅ | 关键风险与方案确认 |
| 2025-11-05 | 开发启动 | 📋 Planned | 任务拆分完成后执行 |
| 2025-11-19 | 功能开发完成 | 📋 Planned | 包含单元/集成/契约测试 |
| 2025-11-26 | 预发布验证 | � Planned | 压测与灰度计划执行 |
| 2025-12-05 | 灰度上线 | 📋 Planned | Feature flag 控制 |

## 2. 代码结构映射

```
app/modules/social_features/
├── __init__.py
├── router.py                # 路由注册与依赖
├── schemas.py               # Pydantic DTO
├── service.py               # Share/Referral/Reward/Metrics 服务
├── repository.py            # SQLAlchemy async 仓储
├── models.py                # ORM 实体定义
├── tasks.py                 # Celery 任务
├── events.py                # Kafka 事件封装
├── validators.py            # 资源/风控校验
├── dependencies.py          # DI 工厂
├── exceptions.py            # 领域异常
└── config.py                # 模块配置读取
```

### 2.1 模块与设计对应关系

| 模块文件 | 对应设计章节 | 实施要点 |
|----------|--------------|----------|
| `router.py` | Design §2.1 | 子路由拆分、限流依赖、统一响应封装 |
| `service.py` | Design §4 | 业务流程与规则执行、幂等控制 |
| `repository.py` | Design §3.2/§3.3 | 提供事务 helper、批量写入、视图查询 |
| `tasks.py` | Design §4.3/§4.4 | 奖励发放、指标聚合、违规复查 |
| `events.py` | Design §6.2 | Avro 契约、Kafka Producer/Consumer |
| `validators.py` | Design §7 | 分享白名单、风控策略、限流判断 |

## 3. 开发计划

### 3.1 迭代拆分

| Sprint Day | 工作内容 | 负责人 |
|------------|----------|--------|
| D1-D3 | 分享 API（create/list/detail）+ Redis 幂等 | Zhang Wei |
| D2-D5 | 分享事件流水 + Kafka 出站 + 限流模块 | Chen Hao |
| D4-D7 | 邀请关系绑定、冲突处理、审计日志 | Liu Yan |
| D6-D9 | 奖励领取流程、Celery 任务、member_system 适配 | Wang Jie |
| D8-D11 | 指标视图、违规查询、管理员接口 | Zhang Wei |
| D10-D12 | 测试、性能压测、文档修订 | 全员 |

### 3.2 依赖准备

- 与 DevOps 协调创建 Redis 命名空间 `social_features:*`。
- 申请 Kafka topic `social.feature.events`、`social.feature.metrics`。
- 创建 Celery 队列 `social_features_reward`、`social_features_metrics`。
- 落地 feature flag `SOCIAL_FEATURES_ENABLED`、`SOCIAL_FEATURES_REWARD_ASYNC`。

## 4. 数据库与存储实施

- Alembic 迁移脚本：
  - `20251105_social_features_init.py`：创建 `social_share`, `social_share_event`, `social_referral`, `social_reward`, `social_violation` 表。
  - `20251108_social_features_metrics.py`：创建物化视图 `social_share_daily_metrics` 与相关索引。
- 迁移执行策略：
  1. 在 staging 环境先执行迁移并跑回归测试。
  2. 生产迁移采用 `--sql` Dry-run 审核后执行。
  3. 迁移后运行数据初始化脚本 `tools/seed_social_features.py`（预置渠道配置、违规规则）。
- 数据回填：将旧系统分享数据导入 `social_share`，保留原始 share_code 映射。

## 5. 异步与事件实现

- Celery Worker 镜像沿用平台基础镜像，安装模块依赖（`protobuf`, `grpcio`, `aiokafka`）。
- 任务列表：
  - `dispatch_reward_task(reward_id)`：调用 `member_system` 兑换奖励。
  - `retry_reward_task(reward_id)`：针对失败奖励的补偿。
  - `aggregate_daily_metrics()`：刷新日指标视图。
  - `review_violations()`：复核违规记录并通知运营。
- Kafka 消费者部署：使用共享 `event-consumer` 服务，新增 Handler `social_features_order_handler`。

## 6. 错误处理与风控

- 统一异常：`SocialFeaturesException`，在 `router.py` 注册全局 handler。
- 风控规则：
  - Redis 计数 `rc:share:{fingerprint}`；阈值可动态调整。
  - 黑名单来自 `marketing_campaigns`，每日同步。
- 审计：人工操作（邀请状态、违规处理）记录 `audit_log`，并写入 `security_logger`。

## 7. 日志与监控落地

- 日志采用 JSON 格式输出，字段包含 `request_id`, `user_id`, `share_code`, `event_type`, `reward_id`。
- Prometheus 指标：
  - API: `social_features_api_latency_seconds`, `social_features_api_errors_total`
  - 事件: `social_features_events_ingested_total`, `social_features_rate_limit_rejections_total`
  - 奖励: `social_features_reward_latency_seconds`, `social_features_reward_retry_total`
- Grafana 仪表板：`dashboards/social-features.json`（待创建）。

## 8. 部署与回滚

- 配置项新增：
  - `SOCIAL_FEATURES_REDIS_PREFIX`
  - `SOCIAL_FEATURES_EVENT_TOPIC`
  - `SOCIAL_FEATURES_REWARD_TIMEOUT`
- 环境变量在 `config/social_features.yaml` 中集中管理，使用 Vault 注入。
- 回滚策略：
  - Feature flag 关闭入口 → 切回旧分享服务。
  - 数据库迁移提供 `downgrade`（谨慎使用，仅限紧急回滚）。
  - Celery 队列可通过 Helm 回滚旧版本。

## 9. 测试与质量保障

- 单元测试覆盖率目标 ≥ 85%，重点覆盖服务层逻辑。
- 集成测试：
  - 使用 pytest + async fixtures + SQLite 内存库。
  - 关键场景：幂等、限流、邀请冲突、奖励补偿、管理员查询。
- 契约测试：`schemathesis` 基于 `api-spec.md` 自动生成场景。
- 性能测试：JMeter 脚本 `tests/perf/social_features_share_events.jmx`，目标：P95 < 80ms。
- 联调计划：与前端、member_system、notification_service 在 staging 环境完成至少一次端到端演练。

## 10. 风险与问题追踪

| 编号 | 描述 | 状态 | 对策 |
|------|------|------|------|
| RISK-01 | member_system 新接口上线时间紧张 | 开放 | 准备 Mock 服务 + 补偿方案 |
| RISK-02 | Redis 使用量激增 | 开放 | 申请独立 Redis 集群或分区；监控内存 |
| RISK-03 | Kafka Schema 变更审批周期长 | 开放 | 提前提交 Schema，准备临时 JSON fallback |
| ISSUE-01 | 指标对账脚本尚未开发 | 进行中 | 数据组负责，11-15 前完成 |

## 11. 待办清单

- [ ] 将任务拆分同步至 Jira（SOCIAL-101 ~ SOCIAL-118）。
- [ ] 编写 Alembic 迁移脚本初稿并发起数据库评审。
- [ ] 实现 Redis 限流与幂等 PoC，验证性能指标。
- [ ] 准备 Kafka Schema 并提交审批。
- [ ] 跟进数据团队的指标对账脚本。

## 12. 变更记录

| 日期 | 版本 | 变更内容 | 责任人 |
|------|------|----------|--------|
| 2025-10-18 | v0.1 | 初始实施规划 | Zhang Wei |
| 2025-10-22 | v0.2 | 增补异步任务、监控计划 | Chen Hao |
| 2025-10-25 | v0.3 | 对齐文档标准，完善风险、待办、回滚策略 | Zhang Wei |
