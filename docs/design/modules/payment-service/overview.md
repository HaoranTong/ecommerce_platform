# payment-service 支付服务模块

📝 状态: Mini-MVP 已交付（迭代中）  
📅 创建日期: 2025-09-16  
👤 负责人: 支付域团队  
🔄 最后更新: 2025-10-21  
📋 文档版本: v1.0.1  

## 模块概述

### 主要职责
当前版本的支付服务模块聚焦以下能力：
- **支付单创建与校验**：基于订单信息生成支付单，校验金额及所有权。
- **支付状态查询**：支持用户按 ID 或分页查询支付信息，管理员可查询所有记录。
- **微信支付回调处理**：接收微信渠道的回调通知，完成签名校验、状态更新与审计记录。
- **管理员状态调整**：管理员可手动更新支付状态以处理异常场景。

未来迭代将逐步补充退款、统计、更多支付渠道以及风控相关能力。

### 模块边界
- **包含功能（MVP）**：支付单创建、支付查询、微信回调处理、管理员状态更新。
- **规划中功能**：退款流程、支付统计、资金对账、风控策略、多渠道适配。
- **依赖模块**：
  - `user_auth`：提供身份认证和角色信息。
  - `order_management`：提供订单金额与所有权校验。
- **不负责的功能**：订单创建、库存扣减、优惠核算、通知推送由各自模块承担。

## 技术架构

### 模块文件结构
```
app/modules/payment_service/
├── router.py           # FastAPI 路由层
├── service.py          # 支付业务编排
├── repository.py       # 支付仓储封装
├── models.py           # SQLAlchemy 模型
├── schemas.py          # Pydantic 校验模型
├── dependencies.py     # 依赖装配
├── auth_helpers.py     # 审计与鉴权辅助
└── utils.py            # 编号、校验工具

app/adapters/payment/
├── wechat_adapter.py   # 微信支付适配器（已接入）
└── config.py           # 渠道配置常量
```

### 分层说明
- **Router 层**：声明 API 路径，完成请求体校验与权限控制，统一使用 `ApiResponse` 返回格式。
- **Service 层**：聚合业务规则（金额校验、订单验证、回调处理、事件记录），并维持事务边界。
- **Repository 层**：收敛数据库访问，提供支付单、流水、外发表等操作封装。
- **Adapter 层**：与第三方支付渠道交互，目前仅实现微信渠道的 `create_unified_order` 与回调签名校验。

### 技术栈
- Python 3.11 / FastAPI 0.104.1 / SQLAlchemy 2.0 / Pydantic 2.5
- 数据库：MySQL 8.0（主库），未来 Outbox 工作流将引入 Celery Worker
- 缓存：Redis 暂未使用，预留用于幂等控制与热点查询

## 功能状态

| 功能 | 描述 | 当前状态 |
|------|------|----------|
| 支付单创建 | POST `/api/v1/payment-service/payments` | ✅ 已实现 |
| 支付详情查询 | GET `/api/v1/payment-service/payments/{id}` | ✅ 已实现 |
| 用户支付列表 | GET `/api/v1/payment-service/payments` | ✅ 已实现 |
| 管理员支付列表 | GET `/api/v1/payment-service/admin/payments` | ✅ 已实现 |
| 管理员状态更新 | PATCH `/api/v1/payment-service/admin/payments/{id}/status` | ✅ 已实现 |
| 微信回调处理 | POST `/api/v1/payment-service/payments/callback/wechat` | ✅ 已实现 |
| 退款 API | 涉及 `/refunds` 系列端点 | ⏳ 规划中 |
| 统计与对账 | 面向管理后台的统计、报表 | ⏳ 规划中 |

## 数据模型

### 已落地的核心数据表
- `payments`：支付主表，记录订单、用户、金额、支付通道、状态以及第三方凭据。
- `payment_transactions`：支付流水表，记录资金变动（回调时写入）。
- `payment_event_outbox`：Outbox 事件表，支撑可靠消息投递（接口已就绪，Worker 待接入）。
- `refunds`：退款表结构已定义，但暂未通过 API 对外开放。

详细字段说明见 [design.md](./design.md) 第 3 章。

## 业务规则要点
1. 支付金额需与订单金额一致，使用 `PaymentValidator.validate_amount` 进行校验。
2. 支付单状态枚举：`pending/processing/completed/failed/cancelled/expired/refunded`，当前流程使用 `pending → completed` 或管理员手动更新。
3. 微信回调需验证签名并保持幂等，重复通知会直接返回成功。
4. 管理员更新状态操作会记录审计日志，防止越权。

## 接口概览

- POST `/api/v1/payment-service/payments`
- GET `/api/v1/payment-service/payments/{payment_id}`
- GET `/api/v1/payment-service/payments`
- GET `/api/v1/payment-service/admin/payments`
- PATCH `/api/v1/payment-service/admin/payments/{payment_id}/status`
- POST `/api/v1/payment-service/payments/callback/wechat`

完整字段、请求示例见 [api-spec.md](./api-spec.md)。

## 测试现状
- 单元测试：模型、仓储、服务、独立场景共 70+ 用例，覆盖核心分支。
- 集成测试：API 场景覆盖支付创建→查询→管理员操作→回调；性能、安全测试脚本均已通过。
- TODO：退款相关测试将在功能开放后补齐；Outbox Worker 需要端到端回归。

## 路线图
- **当前迭代（10 月）**：夯实支付闭环、补充文档与测试、完善回调签名校验。
- **下一迭代**：实现退款 API、引入 Outbox Worker、补充支付统计接口。
- **后续规划**：接入支付宝/银行卡渠道、对接风控服务、完善对账工具。

## 相关文档
- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [api-spec.md](./api-spec.md)
- [implementation.md](./implementation.md)

> 本文档反映 2025-10-21 的实现状态，如需了解未来范围，请参考路线图与需求文档。

