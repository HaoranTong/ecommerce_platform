---
title: "支付服务 API 实施记录"
updated: "2025-10-20"
owner: "支付域团队"
---

# payment-service - API 实施记录

本记录映射 API 规范到代码实现，跟踪接口状态、处理逻辑、权限与错误码对应关系。

## 1. 实施映射总览

| 规范路径 | 方法 | 路由实现 | 代码位置 | 认证/权限 | 状态 |
|---|---|---|---|---|---|
| /api/v1/payment-service/payments | POST | create_payment | app/modules/payment_service/router.py | Bearer 登录 | ✅ 已实现 |
| /api/v1/payment-service/payments/{id} | GET | get_payment | app/modules/payment_service/router.py | Bearer 所有权 | ✅ 已实现 |
| /api/v1/payment-service/payments | GET | list_payments | app/modules/payment_service/router.py | Bearer 登录 | ✅ 已实现 |
| /api/v1/payment-service/payments/callback/wechat | POST | wechat_payment_callback | app/modules/payment_service/router.py | 无（签名校验） | ✅ 已实现（签名校验待补） |
| /api/v1/payment-service/refunds | POST | 待实现 | - | Bearer 所有权 | ⏳ 规划中 |
| /api/v1/payment-service/refunds/{id} | GET | 待实现 | - | Bearer 所有权 | ⏳ 规划中 |
| /api/v1/payment-service/refunds | GET | 待实现 | - | Bearer 登录 | ⏳ 规划中 |
| /api/v1/payment-service/statistics/daily | GET | 待实现 | - | Bearer 管理员 | ⏳ 规划中 |

备注：当前代码中的回调路径为 `/payment-service/payments/callback/wechat`（无 `/callbacks` 段），规范已在 A10 中使用 `/callbacks/wechat`。统一时需更新路由或在网关层做映射。

## 2. 端点实现细节

### 2.1 创建支付单 POST /payments
- 处理函数：`create_payment`
- 核心逻辑：
	- 验证订单所有权 `verify_order_ownership_for_payment`
	- 校验是否存在 pending 支付单
	- 校验金额一致 `validate_payment_amount`
	- 插入 Payment 记录，调用渠道（微信）创建统一下单
	- 失败回滚删除支付单；审计日志 `create_payment_audit_log`
- 返回：`PaymentRead` 或包含渠道支付凭证的扩展数据
- 错误映射：
	- 400：已有待支付单/金额不符 → PAYMENT_005
	- 500：渠道下单失败 → PAYMENT_401

### 2.2 查询支付详情 GET /payments/{id}
- 处理函数：`get_payment`
- 权限：所有权/管理员（`verify_payment_ownership`）
- 返回：`PaymentRead`
- 错误映射：404 支付单不存在 → PAYMENT_101

### 2.3 支付列表 GET /payments
- 处理函数：`list_payments`
- 筛选：order_id、status、分页
- 权限：非管理员仅能查看本人记录

### 2.4 微信支付回调 POST /payments/callback/wechat
- 处理函数：`wechat_payment_callback`
- 安全：签名验证 TODO；幂等性与重复回调处理 TODO
- 状态流转：成功→paid；失败→failed；更新订单状态
- 审计：记录回调来源、UA、IP

### 2.5 管理端接口
- 列表：`GET /payment-service/admin/payments` → `admin_list_all_payments`
- 状态变更：`PATCH /payment-service/admin/payments/{id}/status` → `admin_update_payment_status`

## 3. 与规范的差异与对齐计划
1) 路径差异：规范使用 `/callbacks/wechat`；实现为 `/payments/callback/wechat` → 计划采用规范路径并保留旧路径作为兼容别名一周期。
2) 响应包裹：实现返回 `PaymentRead`，规范为统一响应包装 → 通过响应拦截器或路由适配层统一封装。
3) 退款与统计端点：尚未落地 → 在迭代 M2 实施。

## 4. 测试覆盖
- 单元：服务层校验、金额校验、号段生成
- 集成：创建支付→渠道下单（mock）→回调更新
- 安全：所有权校验、管理员列表权限

## 5. 变更记录

| 日期 | 版本 | 说明 |
|---|---|---|
| 2025-10-20 | v1.0 | 初版对齐当前实现 |
