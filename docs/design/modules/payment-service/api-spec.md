---
title: "支付服务模块 API 规范"
version: "v1.0.0"
status: "active"
created: "2025-10-20"
updated: "2025-10-20"
owner: "API架构师"
dependencies:
  - "docs/standards/api-standards.md"
  - "docs/design/modules/payment-service/design.md"
labels:
  - "payment-service"
  - "api-specification"
  - "restful"
---

# 支付服务模块 API 规范

<!-- 文件路径：docs/design/modules/payment-service/api-spec.md -->

## 1. 文档信息与依赖

| 项目 | 值 |
|------|----|
| 模块名称 | 支付服务模块 (Payment Service) |
| API版本 | v1 |
| 文档版本 | v1.0.0 |
| 依据标准 | [API设计标准](../../../standards/api-standards.md) |
| 设计对齐 | [design.md](./design.md) 第5章 接口设计 |

## 2. 基础信息与版本管理

- 基础路径: `/api/v1/payment-service/`
- 认证方式: JWT Bearer Token（除回调接口）
- 数据格式: JSON（回调遵循各网关规范）
- 字符编码: UTF-8
- 版本策略: 主路径前缀携带版本号（/api/v1），非向后兼容变更发布 /api/v2

统一响应格式（遵循平台标准）：
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {},
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2025-10-20T10:00:00Z",
    "api_version": "v1"
  }
}
```

## 3. 资源模型定义（简要）

- PaymentCreate: { order_id:int, payment_method:enum, amount:decimal(10,2), description?:str, client_ip?:str, notify_url?:str, return_url?:str }
- PaymentRead/Detail: 支付只读字段集，包含状态、第三方ID、二维码、时间戳
- RefundCreate: { payment_id:int, amount:decimal(10,2), reason:str(10-500), refund_account?:enum(original|balance) }
- RefundRead: 退款只读字段集

完整字段见 [design.md 第5章 Pydantic Schema定义](./design.md)。

## 4. 端点列表

| 方法 | 路径 | 功能 | 认证 | 权限 | 状态 |
|------|------|------|------|------|------|
| POST | /api/v1/payment-service/payments | 创建支付单 | Bearer | 登录用户 | ✅ |
| GET | /api/v1/payment-service/payments/{id} | 查询支付详情 | Bearer | 所有者/管理员 | ✅ |
| GET | /api/v1/payment-service/payments | 支付列表查询 | Bearer | 登录用户 | ✅ |
| PUT | /api/v1/payment-service/payments/{id}/cancel | 取消支付 | Bearer | 所有者/管理员 | ✅ |
| POST | /api/v1/payment-service/refunds | 申请退款 | Bearer | 支付所有者 | ✅ |
| GET | /api/v1/payment-service/refunds | 退款列表 | Bearer | 登录用户 | ✅ |
| GET | /api/v1/payment-service/refunds/{id} | 退款详情 | Bearer | 所有者/管理员 | ✅ |
| PUT | /api/v1/payment-service/refunds/{id}/approve | 审批退款 | Bearer | 管理员 | ✅ |
| POST | /api/v1/payment-service/callbacks/wechat | 微信支付回调 | 无 | 签名校验 | ✅ |
| POST | /api/v1/payment-service/callbacks/alipay | 支付宝回调 | 无 | 签名校验 | 📋 待实现 |
| GET | /api/v1/payment-service/statistics/daily | 每日支付统计 | Bearer | 管理员 | 📋 待实现 |

## 5. 详细接口规范

### 5.1 创建支付单
- 方法: POST
- 路径: `/api/v1/payment-service/payments`
- 权限: 登录用户
- 请求体:
```json
{
  "order_id": 123,
  "payment_method": "wechat",
  "amount": "100.00",
  "currency": "CNY",
  "return_url": "https://example.com/success",
  "notify_url": "https://example.com/notify",
  "description": "商品支付"
}
```
- 成功响应(201):
```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "payment_id": 456,
    "payment_no": "PAY202510201234567890",
    "order_id": 123,
    "amount": "100.00",
    "currency": "CNY",
    "payment_method": "wechat",
    "status": "pending",
    "qr_code": "data:image/png;base64,iVBORw0KGgo...",
    "pay_url": "https://wx.tenpay.com/\u2026",
    "expires_at": "2025-10-20T11:00:00Z",
    "created_at": "2025-10-20T10:30:00Z"
  }
}
```

### 5.2 查询支付详情
- 方法: GET
- 路径: `/api/v1/payment-service/payments/{id}`
- 权限: 所有者/管理员
- 成功响应(200):
```json
{
  "success": true,
  "code": 200,
  "message": "success",
  "data": {
    "id": 456,
    "payment_no": "PAY202510201234567890",
    "order_id": 123,
    "user_id": 789,
    "amount": "100.00",
    "currency": "CNY",
    "payment_method": "wechat",
    "status": "completed",
    "external_payment_id": "4200001234567890123456789012",
    "external_transaction_id": "1234567890",
    "paid_at": "2025-10-20T10:35:00Z",
    "created_at": "2025-10-20T10:30:00Z",
    "updated_at": "2025-10-20T10:35:00Z"
  }
}
```

### 5.3 申请退款
- 方法: POST
- 路径: `/api/v1/payment-service/refunds`
- 权限: 支付所有者
- 请求体:
```json
{
  "payment_id": 456,
  "amount": "50.00",
  "reason": "商品质量问题，申请退款",
  "refund_account": "original"
}
```
- 成功响应(201):
```json
{
  "success": true,
  "code": 201,
  "message": "退款申请成功",
  "data": {
    "id": 789,
    "refund_no": "REF20251020100000000001",
    "payment_id": 456,
    "amount": "50.00",
    "reason": "商品质量问题，申请退款",
    "status": "processing",
    "created_at": "2025-10-20T10:40:00Z"
  }
}
```

### 5.4 微信支付回调（WeChat v3 JSON）
- 方法: POST
- 路径: `/api/v1/payment-service/callbacks/wechat`
- 认证: 无（签名校验）
- 请求头:
```
Wechatpay-Signature: {signature}
Wechatpay-Timestamp: {timestamp}
Wechatpay-Nonce: {nonce}
Wechatpay-Serial: {serial}
Content-Type: application/json
```
- 请求体（加密资源示例）:
```json
{
  "id": "EV-2025102012345678901234567890",
  "create_time": "2025-10-20T18:35:00+08:00",
  "resource_type": "encrypt-resource",
  "event_type": "TRANSACTION.SUCCESS",
  "summary": "支付成功",
  "resource": {
    "algorithm": "AEAD_AES_256_GCM",
    "ciphertext": "...",
    "nonce": "...",
    "associated_data": "transaction"
  }
}
```
- 成功响应(200):
```json
{
  "code": "SUCCESS",
  "message": "成功"
}
```

## 6. 错误码与错误响应

| 错误码 | HTTP状态 | 错误消息 | 说明 |
|--------|----------|----------|------|
| PAYMENT_001 | 400 | 支付金额格式错误 | 金额不合法 |
| PAYMENT_002 | 404 | 订单不存在 | 订单ID无效 |
| PAYMENT_003 | 409 | 订单已支付 | 状态异常 |
| PAYMENT_004 | 400 | 支付方式不支持 | 使用支持的支付方式 |
| PAYMENT_005 | 400 | 支付金额不匹配 | 金额与订单不符 |
| PAYMENT_101 | 404 | 支付单不存在 | ID无效 |
| PAYMENT_102 | 410 | 支付已过期 | 超过支付时限 |
| PAYMENT_201 | 400 | 退款金额超限 | 超过可退金额 |
| PAYMENT_203 | 410 | 退款期限已过 | 超过退款期限 |
| PAYMENT_301 | 401 | 回调签名错误 | 签名校验失败 |
| PAYMENT_401 | 502 | 第三方支付失败 | 网关异常 |
| PAYMENT_402 | 504 | 第三方超时 | 请求超时 |

错误响应标准：
```json
{
  "success": false,
  "code": 400,
  "message": "请求参数错误",
  "error": {
    "error_code": "PAYMENT_001",
    "error_message": "支付金额格式错误",
    "details": {"amount": "最多两位小数"}
  },
  "metadata": {
    "request_id": "req_123",
    "timestamp": "2025-10-20T10:00:00Z"
  }
}
```

## 7. 安全与限流策略

- 认证授权：所有非回调接口需 Bearer Token，资源级所有权校验（支付单只能由所有者或管理员访问）
- 回调安全：签名验证 + 幂等处理（分布式锁 + 回调时间戳）
- 限流策略：创建支付 100次/分钟/用户，查询 500次/分钟/用户，回调无限制但入口有全局保护
- 版本管理：破坏性变更发布 /api/v2；旧版保持至少一个迭代周期支持

参考契约：`docs/standards/openapi.yaml`
