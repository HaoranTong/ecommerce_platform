---
title: "订单管理模块 API 实施文档"
version: "1.0.0"
status: "draft"
created: "2025-09-16"
updated: "2025-10-14"
owner: "交易域 · 订单管理团队"
dependencies:
	- "../../standards/document-management-standards.md"
	- "../../standards/api-standards.md"
	- "../../standards/software-development-lifecycle-standards.md"
	- "../../architecture/application-architecture.md"
labels:
	- "module: order-management"
	- "layer: L2"
---

# Order Management Module - API 实施文档

## 依赖标准
- [文档管理标准](../../standards/document-management-standards.md)
- [API 设计标准](../../standards/api-standards.md)
- [软件开发生命周期标准](../../standards/software-development-lifecycle-standards.md)
- [应用架构](../../architecture/application-architecture.md)

## 具体标准
- 所有端点遵循 `/api/v1/order-management` 前缀与 RESTful 动词语义。
- 权限校验统一通过 `dependencies.py` 中的 `Depends` 链实现，复用 `get_current_user` / `get_current_admin_user`。
- 业务处理集中在 `OrderService`，路由层保持无状态，负责参数校验与异常透传。
- 统一返回 `ApiResponse[...]` 包装结构，错误通过 `HTTPException` 抛出并在路由层捕获。
- 幂等场景交由服务层结合数据库事务与库存服务保证，文档需对重试建议进行说明。
- 订单号生成遵循 `OM{yyyyMMddHHmmss}{0000-9999}` 规范，便于与 `api-spec.md` 示例一致。

## 实现概览
- **后端栈**: FastAPI + SQLAlchemy ORM，运行于同步 Session，部分接口定义为 `async` 以契合整体项目风格。
- **覆盖范围**: 8 个端点已在 `router.py` 完成实现；核心逻辑落在 `OrderService`，依赖库存/商品/用户模块。
- **责任边界**: 订单模块负责校验、库存预占与状态记录；支付、物流等仍通过外部模块回调。
- **当前状态**: 功能接口全部可用，仍需补充监控指标、缓存层与完整测试矩阵（列入技术债务）。

## 接口实施矩阵

| HTTP | 路径 | 路由处理函数 | 关键依赖 | 服务层方法 | 状态 | 测试/备注 |
|------|------|--------------|----------|-------------|------|-----------|
| POST | `/order-management/orders` | `create_order` (`router.py` L29) | `validate_order_creation_permission`、`get_order_service` | `OrderService.create_order` | ✅ 已实现 | 单元/集成测试待补齐；依赖库存预占 |
| GET | `/order-management/orders` | `list_orders` (L75) | `get_current_authenticated_user`、`get_order_service` | `OrderService.get_orders_list` | ✅ 已实现 | 目前分页总数使用局部计数，需优化 total 统计 |
| GET | `/order-management/orders/{order_id}` | `get_order_detail` (L142) | `validate_order_access` | `OrderService.get_order_by_id` (依赖内调用) | ✅ 已实现 | 依赖注入提前完成权限校验 |
| PATCH | `/order-management/orders/{order_id}/status` | `update_order_status` (L178) | `validate_order_status_update_permission`、`get_order_service` | `OrderService.update_order_status` | ✅ 已实现 | 状态机验证与库存扣减在服务层执行 |
| POST | `/order-management/orders/{order_id}/cancel` | `cancel_order` (L231) | `validate_order_access`、`get_order_service` | `OrderService.cancel_order` | ✅ 已实现 | 仅 `pending` 订单可取消，返回 ISO8601 时间戳 |
| GET | `/order-management/orders/{order_id}/items` | `get_order_items` (L275) | `validate_order_access`、`get_order_service` | `OrderService.get_order_items` | ✅ 已实现 | 当前返回快照列表，后续可补充分页 |
| GET | `/order-management/orders/{order_id}/history` | `get_order_status_history` (L322) | `validate_order_access`、`get_order_service` | `OrderService.get_order_status_history` | ✅ 已实现 | 响应为字典列表，未来可切换至 Pydantic 模型 |
| GET | `/order-management/statistics` | `get_order_statistics` (L361) | `validate_statistics_access_permission`、`get_order_service` | `OrderService.calculate_order_statistics` | ✅ 已实现 | 统计逻辑基于聚合查询，尚未做缓存 |

> 行号以 2025-10-14 版本为准，后续变更请同步更新。

## 权限与依赖注入
- `get_order_service` 基于 `get_db` 构造 `OrderService`，保证每次请求获取新的 Session。
- `validate_order_access`/`validate_order_status_update_permission`/`validate_statistics_access_permission` 封装 RBAC 判定，管理员角色由 `user_auth` 模块角色字段识别。
- `OrderAccessValidator` 提供复合依赖形式，便于在未来扩展组合授权逻辑。
- `dependencies.py` 中统一使用 `OM_*` 错误码格式化 `HTTPException`，与 API 规范保持一致。

## 业务逻辑层摘要
- **订单创建**: `create_order` 依序执行库存预占、商品快照生成、金额计算与状态历史写入，统一在事务中提交。
- **订单号生成**: `_generate_order_number` 使用 UTC 时间戳 + 4 位随机数，输出 `OM202510141530120123` 形式。
- **状态更新**: `update_order_status` 通过 `_is_valid_status_transition` 保证状态机合法性，并在 `_handle_status_change_business_logic` 中处理库存释放/扣减。
- **取消订单**: 限定 `pending -> cancelled`，否则返回 `OM_CANNOT_CANCEL`；取消原因默认记录为 "用户主动取消"，后续可透传参数。
- **数据查询**: `get_orders_list` 使用 `joinedload` 预取订单项；`get_order_items` 和 `get_order_status_history` 直接按订单 ID 查询。
- **统计分析**: `calculate_order_statistics` 聚合各状态数量与金额，并计算完成率/取消率等 KPI。

## 数据访问与事务
- Service 直接操作 SQLAlchemy Session；成功路径 `commit()`，异常时 `rollback()`，暂不使用 Repository 层。
- 表结构定义见 `models.py`，字段与 `design.md` 第 3 章保持一致，新增 `receiver_name`、`receiver_phone`、`product_attributes(JSON)` 等字段记录结构化快照。
- 库存交互依赖 `InventoryService.reserve_inventory` 与 `InventoryStock` 模型，预占记录设置 30 分钟过期；状态取消时释放库存。
- 未来计划：引入缓存层存储订单详情与统计结果，降低重复查询成本。

## 监控与日志
- 当前仅依赖 FastAPI 默认日志；未对关键路径输出结构化日志。
- 建议埋点：订单创建/取消计数、状态变更耗时、库存交互成功率；使用 `metadata.tracking` 携带 order_number 便于追踪。
- 建议在 `_release_order_stock` 和 `_confirm_stock_deduction` 中加入失败事件告警，避免静默失败。

## 错误处理与回退
- 路由层捕获未知异常并包装为 500（含 detail），业务异常全部通过 `_http_error` 返回统一结构。
- 服务层在数据库异常时回滚事务，避免脏写；库存释放失败目前仅记录 TODO，需补充日志或异步补偿。
- 错误码与客户端约定参见 `api-spec.md` 第 6 章，新增 `OM_USER_NOT_FOUND` / `OM_PRODUCT_NOT_FOUND` 等识别码。

## 测试与验证
- 封闭测试尚未完成；建议覆盖以下场景：
	- 订单创建成功/库存不足/商品下线；
	- 状态机非法跳转（如 `pending -> shipped`）；
	- 非 `pending` 订单取消时返回 `OM_CANNOT_CANCEL`；
	- 普通用户越权访问他人订单。
- 后续需将该文档纳入 `tools/validate_standards.ps1` 全流程验证，并在 CI 中执行 API 集成测试脚本。
