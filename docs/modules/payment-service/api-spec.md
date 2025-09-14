# 支付服务API规格说明 (Payment Service API Specification)

## 文档说明
- **内容**: 支付服务模块的API接口详细规格说明
- **使用方法**: API开发和集成的技术规范参考
- **更新方法**: API接口变更时同步更新
- **引用关系**: 实现overview.md中的功能设计，被api-implementation.md引用
- **更新频率**: API设计变更时

## API概述

### 认证要求
支付相关API具有严格的安全要求：
- **普通支付操作**: 需要用户认证 (`get_current_active_user`)
- **管理员操作**: 需要管理员权限 (`get_current_admin_user`)
- **Webhook回调**: 验证支付网关签名，无需用户认证

### 基础路径
- 基础路径: `/api/payments`
- 版本: `v1` (隐含在路径中)
- 认证方式: `Bearer Token` + 支付网关签名验证

## API接口规格

### 1. 支付订单管理

#### 1.1 创建支付订单
- **端点**: `POST /api/payments`
- **功能**: 为订单创建支付请求
- **认证**: 用户认证 + 所有权验证
- **权限**: 用户只能为自己的订单创建支付，管理员可为任意订单创建

**请求体**:
```json
{
  "order_id": 12345,
  "payment_method": "alipay",
  "amount": "299.99",
  "currency": "CNY",
  "return_url": "https://shop.example.com/payment/return",
  "notify_url": "https://shop.example.com/api/payments/webhook",
  "description": "订单支付 - 有机大米 2kg"
}
```

**响应体**:
```json
{
  "payment_id": "PAY_20250911_123456",
  "order_id": 12345,
  "amount": "299.99",
  "currency": "CNY",
  "status": "pending",
  "payment_method": "alipay",
  "gateway_order_id": "2025091122001234567890123456",
  "pay_url": "https://openapi.alipay.com/gateway.do?...",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "expires_at": "2025-09-11T11:30:00Z",
  "created_at": "2025-09-11T10:30:00Z"
}
```

#### 1.2 查询支付状态
- **端点**: `GET /api/payments/{payment_id}`
- **功能**: 查询支付订单状态
- **认证**: 用户认证 + 所有权验证
- **权限**: 用户只能查询自己的支付，管理员可查询所有支付

**响应体**:
```json
{
  "payment_id": "PAY_20250911_123456",
  "order_id": 12345,
  "user_id": 1001,
  "amount": "299.99",
  "currency": "CNY",
  "status": "paid",
  "payment_method": "alipay",
  "gateway_order_id": "2025091122001234567890123456",
  "gateway_transaction_id": "2025091122001234567890654321",
  "paid_at": "2025-09-11T10:35:28Z",
  "created_at": "2025-09-11T10:30:00Z",
  "updated_at": "2025-09-11T10:35:30Z"
}
```

#### 1.3 获取支付列表
- **端点**: `GET /api/payments`
- **功能**: 获取支付订单列表（分页）
- **认证**: 用户认证 + 数据隔离
- **权限**: 用户只能查看自己的支付，管理员可查看所有支付

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页大小 (默认: 20, 最大: 100)
- `status`: 支付状态过滤 (pending/paid/failed/cancelled)
- `payment_method`: 支付方式过滤
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

**响应体**:
```json
{
  "items": [
    {
      "payment_id": "PAY_20250911_123456",
      "order_id": 12345,
      "amount": "299.99",
      "currency": "CNY",
      "status": "paid",
      "payment_method": "alipay",
      "paid_at": "2025-09-11T10:35:28Z",
      "created_at": "2025-09-11T10:30:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

### 2. 支付操作

#### 2.1 取消支付
- **端点**: `POST /api/payments/{payment_id}/cancel`
- **功能**: 取消未支付的支付订单
- **认证**: 用户认证 + 所有权验证
- **权限**: 用户只能取消自己的支付，管理员可取消任意支付

**响应体**:
```json
{
  "payment_id": "PAY_20250911_123456",
  "status": "cancelled",
  "cancelled_at": "2025-09-11T10:45:00Z",
  "message": "支付已取消"
}
```

#### 2.2 同步支付状态
- **端点**: `POST /api/payments/{payment_id}/sync`
- **功能**: 主动同步支付网关状态
- **认证**: 管理员权限
- **权限**: 仅管理员可操作

**响应体**:
```json
{
  "payment_id": "PAY_20250911_123456",
  "old_status": "pending",
  "new_status": "paid",
  "gateway_status": "TRADE_SUCCESS",
  "synced_at": "2025-09-11T10:50:00Z"
}
```

### 3. 退款管理

#### 3.1 创建退款
- **端点**: `POST /api/payments/{payment_id}/refunds`
- **功能**: 为已支付订单创建退款
- **认证**: 管理员权限（涉及资金安全）
- **权限**: 仅管理员可发起退款

**请求体**:
```json
{
  "amount": "100.00",
  "reason": "商品缺货，部分退款",
  "operator_id": 2001
}
```

**响应体**:
```json
{
  "refund_id": "REF_20250911_789012",
  "payment_id": "PAY_20250911_123456",
  "amount": "100.00",
  "reason": "商品缺货，部分退款",
  "status": "processing",
  "gateway_refund_id": "2025091122001234567890999888",
  "operator_id": 2001,
  "created_at": "2025-09-11T11:00:00Z"
}
```

#### 3.2 查询退款状态
- **端点**: `GET /api/payments/{payment_id}/refunds/{refund_id}`
- **功能**: 查询退款状态
- **认证**: 用户认证 + 所有权验证
- **权限**: 用户可查询自己支付的退款，管理员可查询所有退款

**响应体**:
```json
{
  "refund_id": "REF_20250911_789012",
  "payment_id": "PAY_20250911_123456",
  "amount": "100.00",
  "reason": "商品缺货，部分退款",
  "status": "success",
  "gateway_refund_id": "2025091122001234567890999888",
  "processed_at": "2025-09-11T11:05:15Z",
  "operator_id": 2001,
  "created_at": "2025-09-11T11:00:00Z"
}
```

### 4. Webhook回调

#### 4.1 支付结果通知
- **端点**: `POST /api/payments/webhook/{gateway}`
- **功能**: 接收支付网关异步通知
- **认证**: 验证网关签名，无需用户认证
- **权限**: 公开端点，但需要验证网关签名

**路径参数**:
- `gateway`: 支付网关标识 (alipay/wechat/unionpay)

**请求体**: (根据不同网关格式不同)
```json
{
  "notify_type": "trade_status_sync",
  "trade_status": "TRADE_SUCCESS",
  "out_trade_no": "PAY_20250911_123456",
  "trade_no": "2025091122001234567890654321",
  "total_amount": "299.99",
  "receipt_amount": "299.99",
  "gmt_payment": "2025-09-11 10:35:28",
  "sign": "ERITJKEIJKJHKKKKKKKHJEREEEEEEEEEEE"
}
```

**响应体**:
```text
success
```

### 5. 管理员接口

#### 5.1 支付统计
- **端点**: `GET /api/payments/stats`
- **功能**: 获取支付统计数据
- **认证**: 管理员权限
- **权限**: 仅管理员可访问

**查询参数**:
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `group_by`: 分组维度 (day/week/month/payment_method)

**响应体**:
```json
{
  "period": {
    "start_date": "2025-09-01",
    "end_date": "2025-09-11"
  },
  "summary": {
    "total_amount": "25680.50",
    "total_count": 156,
    "success_rate": "98.7%",
    "avg_amount": "164.62"
  },
  "by_method": {
    "alipay": {
      "amount": "15280.30",
      "count": 89,
      "rate": "57.1%"
    },
    "wechat": {
      "amount": "8750.20",
      "count": 52,
      "rate": "33.3%"
    },
    "unionpay": {
      "amount": "1650.00",
      "count": 15,
      "rate": "9.6%"
    }
  },
  "daily_trend": [
    {
      "date": "2025-09-11",
      "amount": "2580.50",
      "count": 18
    }
  ]
}
```

## 状态码规范

### 成功状态码
- `200 OK` - 查询成功
- `201 Created` - 支付订单创建成功

### 客户端错误
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未认证
- `403 Forbidden` - 权限不足
- `404 Not Found` - 支付记录不存在
- `409 Conflict` - 支付状态冲突（如重复支付）
- `422 Unprocessable Entity` - 业务逻辑错误

### 服务端错误
- `500 Internal Server Error` - 服务器内部错误
- `502 Bad Gateway` - 支付网关错误
- `503 Service Unavailable` - 支付服务暂不可用
- `504 Gateway Timeout` - 支付网关超时

## 错误响应格式

```json
{
  "error": {
    "code": "PAYMENT_AMOUNT_INVALID",
    "message": "支付金额无效",
    "details": "支付金额必须大于0.01元",
    "timestamp": "2025-09-11T10:30:00Z",
    "request_id": "req_20250911_123456"
  }
}
```

## 支付状态定义

### 支付状态 (Payment Status)
- `pending` - 待支付：支付订单已创建，等待用户支付
- `paid` - 已支付：支付成功完成
- `failed` - 支付失败：支付过程中发生错误
- `cancelled` - 已取消：用户或系统取消支付
- `expired` - 已过期：支付超时未完成
- `refunding` - 退款中：正在处理退款
- `refunded` - 已退款：退款完成

### 退款状态 (Refund Status)
- `processing` - 处理中：退款请求已提交，等待处理
- `success` - 退款成功：退款已完成
- `failed` - 退款失败：退款处理失败
- `cancelled` - 退款取消：退款请求被取消

## 支付方式标识

### 支持的支付方式
- `alipay` - 支付宝
- `wechat` - 微信支付
- `unionpay` - 银联支付
- `paypal` - PayPal（国际支付）
- `balance` - 余额支付（用户账户余额）

---

**API版本**: V1.0 Mini-MVP  
**最后更新**: 2025-09-11  
**下次评审**: 支付功能扩展时
