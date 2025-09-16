# payment-service - API规范文档

## API端点定义

### 基础信息
- **模块名**: payment-service
- **API前缀**: /payment-service/
- **认证**: JWT Bearer Token
- **数据格式**: JSON
- **编码**: UTF-8

### 端点列表

| 方法 | 路径 | 功能 | 权限 | 状态 |
|------|------|------|------|------|
| POST | /payment-service/payments | 创建支付单 | 登录用户 | ✅ 已实现 |
| GET | /payment-service/payments/{id} | 查询支付详情 | 数据所有者 | ✅ 已实现 |
| GET | /payment-service/payments | 支付列表查询 | 登录用户 | ✅ 已实现 |
| PUT | /payment-service/payments/{id}/cancel | 取消支付 | 数据所有者 | ✅ 已实现 |
| POST | /payment-service/refunds | 申请退款 | 支付所有者 | ✅ 已实现 |
| GET | /payment-service/refunds | 退款列表 | 登录用户 | ✅ 已实现 |
| GET | /payment-service/refunds/{id} | 退款详情 | 相关用户 | ✅ 已实现 |
| PUT | /payment-service/refunds/{id}/approve | 审批退款 | 管理员 | ✅ 已实现 |
| POST | /payment-service/callbacks/wechat | 微信支付回调 | 无需认证 | ✅ 已实现 |
| POST | /payment-service/callbacks/alipay | 支付宝回调 | 无需认证 | 📋 待实现 |
| GET | /payment-service/admin/payments | 管理员查询支付 | 管理员 | ✅ 已实现 |
| GET | /payment-service/stats/daily | 每日支付统计 | 管理员 | 📋 待实现 |

## API详细规范

### 1. 创建支付单

**POST** `/payment-service/payments`

**请求参数:**
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

**响应示例:**
```json
{
  "id": 456,
  "payment_no": "PAY202509161234567890",
  "order_id": 123,
  "amount": "100.00",
  "currency": "CNY",
  "payment_method": "wechat",
  "status": "pending",
  "qr_code": "data:image/png;base64,iVBORw0KGgo...",
  "expires_at": "2025-09-16T11:00:00Z",
  "created_at": "2025-09-16T10:30:00Z"
}
```

### 2. 查询支付详情

**GET** `/payment-service/payments/{id}`

**路径参数:**
- `id`: 支付单ID

**响应示例:**
```json
{
  "id": 456,
  "payment_no": "PAY202509161234567890", 
  "order_id": 123,
  "user_id": 789,
  "amount": "100.00",
  "currency": "CNY",
  "payment_method": "wechat",
  "status": "completed",
  "external_transaction_id": "4200001234202509161234567890",
  "paid_at": "2025-09-16T10:35:00Z",
  "created_at": "2025-09-16T10:30:00Z",
  "updated_at": "2025-09-16T10:35:00Z"
}
```

### 3. 申请退款

**POST** `/payment-service/refunds`

**请求参数:**
```json
{
  "payment_id": 456,
  "amount": "100.00", 
  "reason": "商品质量问题",
  "description": "用户申请全额退款"
}
```

**响应示例:**
```json
{
  "id": 789,
  "refund_no": "REF202509161234567890",
  "payment_id": 456,
  "amount": "100.00",
  "reason": "商品质量问题",
  "status": "pending",
  "created_at": "2025-09-16T11:00:00Z"
}
```

### 4. 支付回调处理

**POST** `/payment-service/callbacks/wechat`

**请求头:**
```
Content-Type: application/xml
```

**请求体 (XML格式):**
```xml
<xml>
  <appid>wx1234567890</appid>
  <mch_id>1234567890</mch_id>
  <out_trade_no>PAY202509161234567890</out_trade_no>
  <transaction_id>4200001234202509161234567890</transaction_id>
  <result_code>SUCCESS</result_code>
  <sign>ABC123DEF456</sign>
</xml>
```

**响应示例:**
```xml
<xml>
  <return_code>SUCCESS</return_code>
  <return_msg>OK</return_msg>
</xml>
```

## 错误代码定义

| 错误代码 | HTTP状态码 | 错误描述 | 解决方案 |
|----------|------------|----------|----------|
| PAYMENT_001 | 400 | 支付金额与订单不符 | 检查订单金额 |
| PAYMENT_002 | 400 | 不支持的支付方式 | 使用支持的支付方式 |
| PAYMENT_003 | 404 | 支付单不存在 | 检查支付单ID |
| PAYMENT_004 | 403 | 无权限访问支付数据 | 检查用户权限 |
| PAYMENT_005 | 409 | 支付单状态不允许操作 | 检查支付状态 |
| REFUND_001 | 400 | 退款金额超过支付金额 | 调整退款金额 |
| REFUND_002 | 409 | 订单不支持退款 | 检查订单状态 |

详细API规范请参考 [standards/openapi.yaml](../../standards/openapi.yaml)
