---
title: "social-features 模块导航"
version: "v0.3.0"
status: "Design Frozen"
created: "2025-10-18"
updated: "2025-10-25"
owner: "Growth Experience 团队"
dependencies:
	- "../../architecture/overview.md"
	- "./overview.md"
labels:
	- "module"
	- "navigation"
---

# social-features 模块

📋 **当前状态**: 设计冻结，开发待启动  
� **责任团队**: Growth Experience 团队（模块负责人: Zhang Wei）  
🔄 **最后审查**: 2025-10-25  

## 快速导航

| 文档类型 | 文档名称 | 描述 |
|---------|----------|------|
| 概述 | [overview.md](./overview.md) | 模块职责、边界、关键指标 |
| 需求 | [requirements.md](./requirements.md) | 业务需求、场景与验收标准 |
| 详细设计 | [design.md](./design.md) | 架构设计、数据/流程建模、接口 |
| API 规范 | [api-spec.md](./api-spec.md) | REST API、错误码、幂等策略 |
| API 实施 | [api-implementation.md](./api-implementation.md) | 接口实现映射与测试范围 |
| 实现记录 | [implementation.md](./implementation.md) | 开发计划、迁移、运维与风险 |

## 模块简介

社交能力模块（social-features）面向 Growth Experience 场景，提供商品分享、邀请裂变、奖励发放以及增长指标采集等能力，确保用户裂变路径与运营活动闭环。

### 核心能力
- 多渠道分享链接生成、二维码交付与有效期管理。
- 分享事件采集、反作弊去重与实时指标聚合。
- 邀请关系绑定、首购识别与奖励策略执行。
- 奖励领取流程、外部会员系统积分/券发放。
- 运营侧数据洞察与违规监控。

### 技术栈
- **后端**: FastAPI 0.110、SQLAlchemy 2.x（异步）
- **数据层**: MySQL 8.0（主从）、Redis 7（限流与幂等）、Kafka（事件总线）
- **异步处理**: Celery + RabbitMQ
- **监控**: Prometheus + Loki + Grafana
- **鉴权**: JWT（`user_auth` 模块）

## 模块边界

- **上游依赖**: `user_auth`（认证与角色）、`product_catalog`（可分享资源）、`marketing_campaigns`（活动策略）、`member_system`（奖励库存）。
- **下游消费者**: `notification_service`（推送提醒）、数据分析平台（Kafka topic `social.feature.metrics`）、运营后台。
- **不负责内容**: 用户等级计算、营销预算决策、广告归因模型。

更多边界细节参见 [overview.md](./overview.md#模块边界)。

## 快速开始

1. 阅读 [requirements.md](./requirements.md) 理解业务目标与成功指标。
2. 在 [design.md](./design.md) 查看数据模型、流程与接口契约。
3. 实现 API 时参考 [api-spec.md](./api-spec.md) 与 [api-implementation.md](./api-implementation.md)。
4. 开发落地遵循 [implementation.md](./implementation.md) 的迁移与部署计划。

测试指南与环境说明详见 `tests/modules/social_features/README.md`（待建设）。

## 健康与状态

- 最新模块健康状态：见 [docs/status/module-status.md](../../status/module-status.md) 中 `social-features` 条目。
- 维护节奏：设计文档季度审查，开发期间每次发布后复核。

## 联系方式

- **模块负责人**: Zhang Wei `<zhang.wei@example.com>`
- **技术负责人**: Chen Hao `<chen.hao@example.com>`
- **产品对接**: Liu Jing `<liu.jing@example.com>`
- **Slack 频道**: `#growth-social-features`
