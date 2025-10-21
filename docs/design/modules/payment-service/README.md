<!--
文档说明：
- 内容：模块README导航模板，模块入口文档
- 作用：提供快速导航和基本信息，不包含详细内容
- 使用方法：复制此模板，替换模板变量，保持简洁
-->

# payment-service 支付服务模块

📋 **状态**: Mini-MVP 已交付（迭代中）  
👤 **负责人**: 支付域团队  
🔄 **最后更新**: 2025-10-21  

## 快速导航

| 文档类型 | 文档名称 | 描述 |
|---------|----------|------|
| **概述** | [overview.md](./overview.md) | 模块详细概述和技术架构 |
| **需求** | [requirements.md](./requirements.md) | 业务需求和功能规格 |
| **设计** | [design.md](./design.md) | 技术设计和架构决策 |
| **API规范** | [api-spec.md](./api-spec.md) | API接口规范定义 |
| **API实施** | [api-implementation.md](./api-implementation.md) | API开发实施记录 |
| **实现** | [implementation.md](./implementation.md) | 开发实现详细记录 |

## 模块简介

为电商平台提供统一、安全、可扩展的支付能力。当前 Mini-MVP 聚焦于支付单创建、查询、管理员审核以及微信回调处理，后续迭代将逐步补充退款、统计与多渠道能力。

### 核心功能
- 支付单创建、详情查询、列表查询
- 管理员视角的支付列表与状态更新
- 微信支付回调处理及基本幂等控制
- 支付审计辅助：记录创建与回调行为
- 规划中：退款流程、统计报表、更多支付渠道（支付宝等）

### 技术栈
- 后端: FastAPI 0.104.1, SQLAlchemy 2.0.x, Pydantic 2.x
- 数据库: MySQL 8.0
- 缓存: Redis 7.0（后续幂等与事件调度规划中）
- 其他: Celery 5.3（Outbox Worker 规划中）

## 快速开始

### API端点
- 基础路径: `/api/v1/payment-service/`
- 主要接口: 详见 [api-spec.md](./api-spec.md)

### 数据模型
- 核心表: `payments`, `payment_transactions`, `payment_event_outbox`
- 退款模型 `refunds` 已在数据库层预留，但尚未开放 API
- 详细模型与索引: 见 [design.md 第3章 数据模型](./design.md)

## 相关链接
- [系统架构](../../../architecture/overview.md)
- [API设计规范](../../../standards/api-standards.md)
- [开发规范](../../../standards/code-standards.md)
