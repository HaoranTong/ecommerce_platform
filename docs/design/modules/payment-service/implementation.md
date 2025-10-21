<!--
文档说明：
- 内容：模块实现记录文档模板
- 作用：记录开发过程、实现细节、技术问题和解决方案
- 使用方法：开发过程中实时记录，便于知识传承
-->

# payment-service 模块 - 实现记录文档

📅 创建日期: 2025-09-16  
👤 开发者: 支付域团队  
🔄 最后更新: 2025-10-20  
📊 完成进度: 68%  

## 实施概述

### 实施状态
- 当前状态: 开发中
- 完成功能: 支付创建、支付查询、管理员查询、微信回调处理、审计日志、路由层与依赖注入重构
- 待实施: 退款流程、统计报表、回调签名与幂等、支付宝适配器
- 技术债务: 回调签名校验未实现、渠道错误码细化

### 关键里程碑
| 日期 | 里程碑 | 状态 | 备注 |
|------|--------|------|------|
| 2025-09-30 | Mini-MVP: 创建/查询/回调 | ✅ | 基本闭环验证 |
| 2025-10-15 | 退款流程实现 | 🔄 | 进行中 |
| 2025-10-31 | 风控与统计 | ⏳ | 规划中 |
## 代码实现

### 目录结构
```
app/modules/payment_service/
├── __init__.py
├── router.py           # API路由（支付、回调、管理员）
├── service.py          # 业务逻辑（校验、渠道调用封装）
├── repository.py       # 仓储层（支付/退款/流水/事件外发封装）
├── models.py           # SQLAlchemy模型（Payment、Refund）
├── schemas.py          # Pydantic v2 模型
├── dependencies.py     # 依赖注入与权限
├── auth_helpers.py     # 审计与安全校验
└── utils.py            # 编号生成等工具
```

### 核心组件实现

#### API路由层 (router.py)
- 路径前缀统一在 app/main.py 中注册为 `/api/v1`
- 已实现端点：
    - POST `/api/v1/payment-service/payments` → 创建支付
    - GET `/api/v1/payment-service/payments/{id}` → 支付详情
    - GET `/api/v1/payment-service/payments` → 支付列表
    - POST `/api/v1/payment-service/payments/callback/wechat` → 微信回调（待对齐规范路径）
    - 管理端：GET `/api/v1/payment-service/admin/payments`，PATCH `/api/v1/payment-service/admin/payments/{id}/status`

#### 业务逻辑层 (service.py)
- 校验：订单所有权与金额一致性
- 渠道：调用 `wechat_pay_service.create_unified_order` 生成支付凭证
- 审计：`create_payment_audit_log` 记录关键行为

#### 数据访问层 / 仓储层
- `repository.py` 已实现 `PaymentRepository`，封装 `get_by_payment_no`、`ensure_callback_idempotent`、`mark_callback_processed`、`append_transaction`、`enqueue_event` 等操作。
- `models.py` 新增 `PaymentTransaction`、`PaymentEventOutbox` 模型，配合仓储方法落库支付流水与事件外发记录。
- 已完成：Service 层通过依赖注入接入仓储与渠道适配器，FastAPI 路由已切换至新的应用服务实现。
- 已完成：仓储层补充 Outbox 扫描/状态更新接口，并在 `tasks/outbox_worker.py` 提供事件调度工具。
- 后续：补充仓储与服务层的单元测试，并将 Outbox Worker 接入实际调度及告警闭环。

### 数据模型实现

#### SQLAlchemy模型
见 `models.py`，包含索引：payment_no、(order_id,user_id)、(status,created_at) 等。

## 技术实现细节

### 关键算法实现
- **算法1**: {算法描述和实现}
- **算法2**: {算法描述和实现}

### 性能优化
- **数据库优化**: 依托新增索引（payment_no、status+created_at、outbox status）保持查询效率，后续按照压测结果再行调优。
- **缓存实现**: 支付详情、统计信息缓存策略待结合仓储重构后的查询接口排期。
- **异步处理**: 回调事件采用 Outbox + Worker 方案，详见下节。

#### 异步处理（Outbox Worker 计划）
- **调度模式**：使用 Celery Beat 或 APScheduler 每 5 秒扫描 `payment_event_outbox`（支持配置化），单批默认处理 100 条；`dispatch_outbox_events` 提供独立函数方便集成到不同执行器。
- **处理流程**：
    1. 将待处理事件更新为 `sending` 状态，调用 MQ 客户端发布消息；
    2. 发布成功写回 `sent`、`delivered_at`，失败累加 `retry_count` 并根据阈值决定是否继续 `pending` 或标记 `failed`，同时记录 `last_error`；
    3. 当 `retry_count >= 5` 触发告警（Prometheus/日志），需要人工介入或脚本补偿。
- **示例伪代码**：
```python
@celery_app.task(bind=True, name="payment_event_outbox.dispatch")
def dispatch_outbox(self):
    with session_factory() as session:
        repo = PaymentRepository(session)
        events = repo.fetch_pending_outbox(limit=100)
        for event in events:
            repo.mark_outbox_sending(event)
        session.flush()

        for event in events:
            try:
                mq_client.publish(event.event_type, event.payload)
            except Exception as exc:  # noqa: BLE001
                repo.mark_outbox_retry(event, error=str(exc), max_retries=5)
            else:
                repo.mark_outbox_sent(event)
        session.commit()
```
- **后续任务**：
    - [x] 在仓储层补充 `fetch_pending_outbox`、`mark_outbox_sent`、`mark_outbox_retry` 接口（2025-10-20）。
    - [x] 在 `dependencies.py` 注册仓储实例，Service 层通过 DI 获取（2025-10-20）。
    - [x] 新建 `tasks/outbox_worker.py` 并在运维手册中记录告警策略（待文档更新，代码已提交于 2025-10-20）。

### 错误处理
- 业务错误使用 FastAPI HTTPException 抛出 4xx/5xx；错误码映射参见 `docs/design/modules/payment-service/api-spec.md`

## 集成实现

### 模块间集成
- **依赖模块**: {集成实现}
- **事件发布**: {事件实现}
- **接口调用**: {调用实现}

### 外部服务集成
使用 `app/adapters/payment/wechat_adapter.py` 与 `alipay_adapter.py` 封装渠道差异；重试、降级策略将在接入层统一处理。

## 数据库实施

### 迁移脚本
见 Alembic 目录，按模块前缀 `payment_` 命名迁移；当前表由自动发现 create_all 创建，后续将迁移化。

### 数据初始化
```python
# 初始化数据脚本
def init_{module}_data():
    """
    数据初始化：
    - 基础数据：{基础数据说明}
    - 测试数据：{测试数据说明}
    """
    # 实现代码
    pass
```

## 测试实施

### 单元测试实现
- 建议覆盖：金额验证、订单所有权校验、编号生成、状态流转
- 2025-10-20：使用 `tools/generate_test_template.py payment_service` 生成模型/仓储/服务/集成/安全/性能等测试骨架，自动校验通过；待补充跨模块工厂（OrderManagementFactoryManager）并完善自定义用例。

### 集成测试实现
- 场景：创建支付→模拟渠道下单成功→调用回调→校验状态与订单联动

## 配置实施

### 环境配置
沿用平台统一配置，支付模块无专有环境变量需求。

### 依赖注入配置
见 `dependencies.py` 与 `auth_helpers.py`。

## 部署实施

### Docker配置
无模块专有 Docker 要求，沿用项目根镜像与依赖。

### 环境变量
环境变量由平台统一管理。

## 问题和解决方案

### 技术问题记录
| 日期 | 问题描述 | 解决方案 | 状态 |
|------|----------|----------|------|
| 2025-09-16 | {问题描述} | {解决方案} | ✅ |
| 2025-09-16 | {问题描述} | {解决方案} | 🔄 |

### 性能问题
- **问题**: {性能问题描述}
- **原因**: {问题原因分析}
- **解决**: {解决方案实施}
- **效果**: {优化效果}

### 集成问题
- **问题**: {集成问题}
- **影响**: {问题影响}
- **解决**: {解决过程}

## 知识总结

### 经验教训
- **经验1**: {具体经验}
- **教训1**: {具体教训}
- **改进**: {改进建议}

### 最佳实践
- **实践1**: {最佳实践描述}
- **实践2**: {最佳实践描述}

### 技术债务
- **债务1**: {技术债务描述和还债计划}
- **债务2**: {技术债务描述和还债计划}

## 后续计划

### 优化计划（Coding Standards）
- [x] 重构 `PaymentService` 以使用 `PaymentRepository`，实现事务边界、幂等锁与事件入箱（2025-10-20）
- [x] 在 `dependencies.py` 注册仓储与适配器依赖，路由层通过 DI 获取实例（2025-10-20）
- [x] 整合统一响应包装与错误码映射，满足 API 标准的 envelope 要求（响应包装已完成，错误码映射待细化）
- [ ] 引入结构化日志与审计记录（支付创建、回调、退款）

### 功能/集成实现（API Standards）
- [ ] 对齐 `api-spec.md` 的端点路径、状态码、请求/响应 schema
- [ ] 落实 Idempotency-Key 处理（路由 → Service → Repository）
- [ ] 实现支付回调签名校验（微信/支付宝）及重放防护
- [ ] 完成退款流程 API（申请、审批、拒绝）与状态机联动

### 数据库与基础设施（Database Standards）
- [ ] 编写 Alembic 迁移（`payment_transactions`、`payment_event_outbox` 及字段变更）
- [ ] 在仓储层补充 `fetch_pending_outbox`、`mark_outbox_sent`、`mark_outbox_retry`
- [ ] 新增 Outbox Worker（Celery/APS）及告警策略实现
- [ ] 覆盖仓储与服务层的数据库单元测试，包含并发/幂等场景

### 测试与质量保障
- [ ] 更新/新增 Pydantic schema 校验测试，确保必填字段与格式符合标准
- [ ] 编写集成测试：创建支付→回调→事件出站→订单模块模拟消费
- [ ] 压测与限流策略验证，输出性能测试报告
- [ ] 安全扫描（输入校验、签名、敏感日志脱敏）并记录整改结果

## 变更记录

| 日期 | 版本 | 变更内容 | 开发者 |
|------|------|----------|--------|
| 2025-10-20 | v1.0 | 同步文档与实现现状 | 支付域团队 |
