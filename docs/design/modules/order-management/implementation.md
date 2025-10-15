---
title: "订单管理模块实现记录"
version: "1.0.0"
status: "draft"
created: "2025-09-16"
updated: "2025-10-14"
owner: "交易域 · 订单管理团队"
labels:
  - "module: order-management"
  - "layer: L2"
---

# Order Management Module - 实现记录（A9）

📅 **最新更新时间**: 2025-10-14  
🧑‍� **当前维护人**: 交易域 · 订单管理团队  
📊 **整体进度**: 85%（核心功能上线，性能优化与缓存仍在排期）  

---

## 1. 实施概览

| 项目 | 内容 |
|------|------|
| 当前状态 | ✅ 已对接核心业务流程；回归测试与性能优化待补齐 |
| 已完成功能 | 订单创建、查询、状态流转、取消、商品快照、统计报表 |
| 待实施项 | Redis 缓存接入、消息队列回调、购物车清空、全量自动化测试 |
| 技术债务 | 缓存/消息未落地、日志缺失、库存释放失败仅记录 TODO |

### 1.1 关键里程碑

| 日期 | 事项 | 状态 | 说明 |
|------|------|------|------|
| 2025-09-16 | 模块骨架 & 模型搭建 | ✅ | 完成 SQLAlchemy 模型与基础路由 |
| 2025-09-25 | 订单创建 & 库存预占 | ✅ | 接入库存服务、完成事务封装 |
| 2025-10-05 | 状态机与统计接口 | ✅ | 支持完整状态流转、聚合统计 |
| 2025-10-14 | 错误码统一 & 文档对齐 | ✅ | 统一 `OM_*` 错误码，补齐 A10/A11 文档 |
| 2025-10-20 | Redis 缓存 | 🔄 | 计划中，等待基础设施容量评估 |

---

## 2. 代码结构

```
app/modules/order_management/
├── __init__.py
├── router.py              # FastAPI 路由与响应格式
├── service.py             # 业务服务层（事务、状态机、跨模块协作）
├── repository.py          # 数据访问层（OrderRepository 封装 ORM 操作）
├── models.py              # SQLAlchemy ORM 模型
├── schemas.py             # Pydantic 请求/响应模型
├── dependencies.py        # 依赖注入与权限校验
├── category_service.py    # 商品分类扩展服务（规划保留）
└── README.md
```

### 2.1 核心组件说明

- **router.py**: 定义 8 个 REST API，统一返回 `ApiResponse`，成功响应携带 `code` 与 `metadata`。
- **service.py**: 实现订单创建、状态更新、取消、统计等应用层逻辑，集中处理事务与库存交互，依赖 Repository 完成持久化。
- **repository.py**: 封装 `Order`、`OrderItem`、`OrderStatusHistory` 的增删查聚合操作，仅负责数据访问不控制事务。
- **models.py**: `Order` / `OrderItem` / `OrderStatusHistory` 三个模型，新增 `receiver_*` 字段与 JSON 商品属性快照。
- **schemas.py**: 与数据库字段对齐，支持 `product_attributes` 自动反序列化；列表字段使用 `default_factory` 规避可变默认值。
- **dependencies.py**: 提供 `get_order_repository`、`get_order_service`、权限校验与统一的 `_http_error` 帮助函数。

---

## 3. 数据与事务实现

### 3.1 模型要点

- `Order`
  - 主键 `id`、业务键信息 `order_number`（唯一）。
  - 金额字段遵循 `DECIMAL(10,2)`；默认为 pending 状态。
  - 收货信息拆分为 `shipping_address` + `receiver_name` + `receiver_phone`，便于日志与发货系统使用。
- `OrderItem`
  - 保留 `product_id` / `sku_id` 外键，符合数据库标准。
  - `product_attributes` 使用 JSON 存储商品与 SKU 属性快照；`product_image_url` 保存展示图片。
- `OrderStatusHistory`
  - 记录每一次状态变更，供审计与业务追溯使用。

### 3.2 事务与状态约束

- 订单创建流程：
  1. 验证用户存在 (`OM_USER_NOT_FOUND`).
  2. 尝试库存预占，失败抛出 `OM_INSUFFICIENT_STOCK` / `OM_DEPENDENCY_TIMEOUT`。
  3. 校验商品、SKU 可售状态，写入快照与金额。
  4. 在单事务内写入 `Order`、`OrderItem`、`OrderStatusHistory`。
- 状态机：
  - 合法变迁：`pending -> paid/cancelled`、`paid -> shipped`、`shipped -> delivered/returned`。
  - 禁止 `paid -> cancelled`，违反规则返回 `OM_INVALID_STATUS_TRANSITION`。
- 取消订单：仅允许 `pending`，否则报 `OM_CANNOT_CANCEL`；成功后触发库存释放逻辑。
- 所有数据库异常都会触发 `rollback()` 并转化为 `OM_INTERNAL_ERROR`。

---

## 4. 接口实现摘要

| 接口 | 主要逻辑 | 关键依赖 | 备注 |
|------|----------|----------|------|
| `POST /orders` | 库存预占 → 商品快照 → 事务写入 | `InventoryService.reserve_inventory` | 返回 metadata.tracking.order_number |
| `GET /orders` | 支持分页与状态过滤，返回真实 `total_count` | `OrderService.get_orders_list` | 目前未实现缓存 |
| `PATCH /orders/{id}/status` | 状态机校验 + 库存扣减 | `_handle_status_change_business_logic` | 仅管理员可调用 |
| `POST /orders/{id}/cancel` | 权限校验 + 状态检查 + 状态机 | `validate_order_access` | 返回 ISO8601 `cancelled_at` |
| `GET /statistics` | 聚合订单数量/金额 + 完成率/取消率 | SQLAlchemy `func.sum` | 未做缓存，列为性能提升项 |

错误码实现与 `api-spec.md` 第 6 章同步，统一调用 `_http_error(...)` 生成结构化 `HTTPException`。

---

## 5. 集成情况

| 集成对象 | 当前实现 | 风险/备注 |
|----------|----------|-----------|
| `inventory_management` | `reserve_inventory` 预占；状态回滚时释放库存 | `_release_order_stock` 失败仅记录 TODO，需要完善日志或重试机制 |
| `product_catalog` | 读取商品/SKU 信息，写入属性/图片快照 | 商品/规格状态校验已对接；建议加强异常日志 |
| `user_auth` | JWT 认证 + RBAC；管理员权限用于状态更新 | 依赖 `current_user.role` 字段，需保证权限模型稳定 |
| `payment_service` | 通过状态接口进行协作（接口留待回调） | 回调接口尚未实现，需在后续迭代补齐 |
| `shopping_cart` | 按设计计划清空购物车 | 尚未实现，技术债务 |

---

## 6. 测试与质量

- **现状**：已有的单元/集成测试覆盖有限，主要依赖人工验证。
- **待补充测试场景**：
  1. 订单创建成功、库存不足、商品或 SKU 下线。
  2. 状态机非法跳转（`pending -> shipped`、`paid -> cancelled`）。
  3. 非 `pending` 订单取消校验 `OM_CANNOT_CANCEL`。
  4. 分页接口返回真实 `total_count`。
  5. 权限依赖：普通用户访问他人订单、统计接口管理员访问。
- **工具链**：待接入 `tools/validate_standards.ps1`、`tools/check_code_standards.ps1`，以及 CI 中的 API 集成测试脚本。

---

## 7. 问题与解决方案

| 时间 | 问题 | 处理方案 | 状态 |
|------|------|----------|------|
| 2025-10-02 | 订单号格式与 API 文档不一致 (`ORD...`) | 改为 `OM{timestamp}{rand}` 并同步文档 | ✅ |
| 2025-10-06 | 分页接口 `total_count` 不准确 | 新增 `count()` 查询并返回 | ✅ |
| 2025-10-11 | 错误码与客户端约定不统一 | 抽象 `_http_error`，统一 `OM_*` | ✅ |
| 2025-10-14 | 商品快照缺失属性/图片 | 新增 JSON/URL 字段并生成快照 | ✅ |
| – | Redis 缓存未接入 | 排期中 | 🔄 |
| – | 购物车清空、消息通知 | 待产品确认 | 🔄 |

---

## 8. 技术债务与计划

| 类别 | 描述 | 计划 |
|------|------|------|
| 性能 | Redis 缓存、结果缓存刷新策略 | 待基础设施容量评估，目标 Q4 implement |
| 异步 | 库存释放失败缺少补偿机制 | 引入日志告警 + MQ 异步修正 |
| 功能 | 支付回调、购物车清空、订单搜索接口 | 拟在下一次迭代拆分需求 |
| 质量 | 自动化测试缺口、缺乏结构化日志 | 新增 Pytest 场景 + 统一日志格式 |

---

## 9. 后续行动

1. 接入 Redis 缓存与缓存失效策略，完成性能压测。
2. 实现库存释放失败的日志与重试机制，纳入 SRE 监控。
3. 完成订单搜索与购物车清空逻辑，并同步文档。
4. 编写端到端测试（创建 → 支付 → 发货 → 统计），确保回归可重复执行。

---

## 10. 变更记录

| 日期 | 版本 | 内容 | 负责人 |
|------|------|------|---------|
| 2025-09-16 | v0.1 | 初始化模块骨架 | 架构团队 |
| 2025-10-05 | v0.9 | 补齐状态机与统计接口 | 订单管理团队 |
| 2025-10-14 | v1.0 | 错误码统一、字段对齐、文档落地 | 订单管理团队 |
