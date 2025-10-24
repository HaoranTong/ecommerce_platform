# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `AlipayCallback`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `payment_no` | `str` | ❌ | `` | 支付单号 |
| `status` | `str` | ❌ | `` | 支付状态 |
| `transaction_id` | `Optional[str]` | ❌ | `` | 第三方交易ID |
| `amount` | `Optional[Decimal]` | ❌ | `` | 支付金额 |
| `callback_data` | `Dict[str, Any]` | ❌ | `` | 回调原始数据 |
| `out_trade_no` | `str` | ❌ | `` | 商户订单号 |
| `trade_no` | `str` | ❌ | `` | 支付宝交易号 |
| `trade_status` | `str` | ❌ | `` | 交易状态 |
| `total_amount` | `Decimal` | ❌ | `` | 订单金额 |
| `gmt_payment` | `Optional[str]` | ❌ | `` | 交易付款时间 |

---

## `PaymentAnalysis`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `period` | `Dict[str, str]` | ✅ | `` |  |
| `summary` | `PaymentStats` | ✅ | `` |  |
| `trends` | `List[PaymentTrend]` | ✅ | `` |  |
| `top_methods` | `List[Dict[str, Any]]` | ✅ | `` |  |
| `hourly_distribution` | `List[Dict[str, Any]]` | ✅ | `` |  |

---

## `PaymentBatch`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `payment_ids` | `List[int]` | ❌ | `` | 支付ID列表 |
| `action` | `str` | ❌ | `` | 操作类型 |
| `params` | `Optional[Dict[str, Any]]` | ❌ | `` | 操作参数 |

---

## `PaymentCallback`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `payment_no` | `str` | ❌ | `` | 支付单号 |
| `status` | `str` | ❌ | `` | 支付状态 |
| `transaction_id` | `Optional[str]` | ❌ | `` | 第三方交易ID |
| `amount` | `Optional[Decimal]` | ❌ | `` | 支付金额 |
| `callback_data` | `Dict[str, Any]` | ❌ | `` | 回调原始数据 |

---

## `PaymentCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `order_id` | `int` | ❌ | `` | 订单ID |
| `payment_method` | `str` | ❌ | `` | 支付方式 |
| `amount` | `Optional[Decimal]` | ❌ | `` | 支付金额，为空时使用订单金额 |
| `currency` | `str` | ❌ | `` | 货币类型 |
| `return_url` | `Optional[str]` | ❌ | `` | 前端回调URL |
| `notify_url` | `Optional[str]` | ❌ | `` | 后端通知URL |
| `description` | `Optional[str]` | ❌ | `` | 支付描述 |

---

## `PaymentDetail`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `order_id` | `int` | ✅ | `` |  |
| `user_id` | `int` | ✅ | `` |  |
| `payment_no` | `str` | ✅ | `` |  |
| `payment_method` | `str` | ✅ | `` |  |
| `amount` | `Decimal` | ✅ | `` |  |
| `currency` | `str` | ✅ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `external_payment_id` | `Optional[str]` | ❌ | `` |  |
| `external_transaction_id` | `Optional[str]` | ❌ | `` |  |
| `pay_url` | `Optional[str]` | ❌ | `` |  |
| `qr_code` | `Optional[str]` | ❌ | `` |  |
| `expires_at` | `Optional[datetime]` | ❌ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `paid_at` | `Optional[datetime]` | ❌ | `` |  |
| `failed_at` | `Optional[datetime]` | ❌ | `` |  |
| `callback_received_at` | `Optional[datetime]` | ❌ | `` |  |
| `payment_data` | `Optional[Dict[str, Any]]` | ❌ | `` |  |
| `refunds` | `List['RefundRead']` | ❌ | `` |  |

---

## `PaymentRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `order_id` | `int` | ✅ | `` |  |
| `user_id` | `int` | ✅ | `` |  |
| `payment_no` | `str` | ✅ | `` |  |
| `payment_method` | `str` | ✅ | `` |  |
| `amount` | `Decimal` | ✅ | `` |  |
| `currency` | `str` | ✅ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `external_payment_id` | `Optional[str]` | ❌ | `` |  |
| `external_transaction_id` | `Optional[str]` | ❌ | `` |  |
| `pay_url` | `Optional[str]` | ❌ | `` |  |
| `qr_code` | `Optional[str]` | ❌ | `` |  |
| `expires_at` | `Optional[datetime]` | ❌ | `` |  |
| `description` | `Optional[str]` | ❌ | `` |  |
| `paid_at` | `Optional[datetime]` | ❌ | `` |  |
| `failed_at` | `Optional[datetime]` | ❌ | `` |  |

---

## `PaymentSearch`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `payment_no` | `Optional[str]` | ❌ | `` | 支付单号 |
| `order_id` | `Optional[int]` | ❌ | `` | 订单ID |
| `user_id` | `Optional[int]` | ❌ | `` | 用户ID |
| `payment_method` | `Optional[str]` | ❌ | `` | 支付方式 |
| `status` | `Optional[str]` | ❌ | `` | 支付状态 |
| `start_date` | `Optional[datetime]` | ❌ | `` | 开始日期 |
| `end_date` | `Optional[datetime]` | ❌ | `` | 结束日期 |
| `min_amount` | `Optional[Decimal]` | ❌ | `` | 最小金额 |
| `max_amount` | `Optional[Decimal]` | ❌ | `` | 最大金额 |

---

## `PaymentStats`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_payments` | `int` | ✅ | `` |  |
| `completed_payments` | `int` | ✅ | `` |  |
| `failed_payments` | `int` | ✅ | `` |  |
| `success_rate` | `float` | ✅ | `` |  |
| `total_amount` | `Decimal` | ✅ | `` |  |
| `payment_methods` | `List[Dict[str, Any]]` | ✅ | `` |  |

---

## `PaymentStatusUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `status` | `str` | ❌ | `` | 支付状态 |
| `external_payment_id` | `Optional[str]` | ❌ | `` | 第三方支付ID |
| `external_transaction_id` | `Optional[str]` | ❌ | `` | 第三方交易ID |
| `callback_data` | `Optional[Dict[str, Any]]` | ❌ | `` | 回调数据 |

---

## `PaymentTrend`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `date` | `str` | ✅ | `` |  |
| `payment_count` | `int` | ✅ | `` |  |
| `payment_amount` | `Decimal` | ✅ | `` |  |
| `success_count` | `int` | ✅ | `` |  |
| `success_amount` | `Decimal` | ✅ | `` |  |
| `success_rate` | `float` | ✅ | `` |  |

---

## `PaymentUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `external_payment_id` | `Optional[str]` | ❌ | `` | 第三方支付ID |
| `external_transaction_id` | `Optional[str]` | ❌ | `` | 第三方交易ID |
| `pay_url` | `Optional[str]` | ❌ | `` | 支付页面URL |
| `qr_code` | `Optional[str]` | ❌ | `` | 支付二维码 |
| `description` | `Optional[str]` | ❌ | `` | 支付描述 |

---

## `RefundBatch`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `refund_ids` | `List[int]` | ❌ | `` | 退款ID列表 |
| `action` | `str` | ❌ | `` | 操作类型 |
| `params` | `Optional[Dict[str, Any]]` | ❌ | `` | 操作参数 |

---

## `RefundCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `amount` | `Decimal` | ❌ | `` | 退款金额 |
| `reason` | `str` | ❌ | `` | 退款原因 |
| `operator_note` | `Optional[str]` | ❌ | `` | 操作员备注 |

---

## `RefundDetail`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `payment_id` | `int` | ✅ | `` |  |
| `refund_no` | `str` | ✅ | `` |  |
| `amount` | `Decimal` | ✅ | `` |  |
| `reason` | `str` | ✅ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `external_refund_id` | `Optional[str]` | ❌ | `` |  |
| `operator_id` | `Optional[int]` | ❌ | `` |  |
| `operator_note` | `Optional[str]` | ❌ | `` |  |
| `processed_at` | `Optional[datetime]` | ❌ | `` |  |
| `payment` | `Optional[PaymentRead]` | ❌ | `` |  |
| `gateway_response` | `Optional[Dict[str, Any]]` | ❌ | `` |  |

---

## `RefundRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `payment_id` | `int` | ✅ | `` |  |
| `refund_no` | `str` | ✅ | `` |  |
| `amount` | `Decimal` | ✅ | `` |  |
| `reason` | `str` | ✅ | `` |  |
| `status` | `str` | ✅ | `` |  |
| `external_refund_id` | `Optional[str]` | ❌ | `` |  |
| `operator_id` | `Optional[int]` | ❌ | `` |  |
| `operator_note` | `Optional[str]` | ❌ | `` |  |
| `processed_at` | `Optional[datetime]` | ❌ | `` |  |

---

## `RefundStatusUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `status` | `str` | ❌ | `` | 退款状态 |
| `operator_note` | `Optional[str]` | ❌ | `` | 操作员备注 |

---

## `RefundUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `external_refund_id` | `Optional[str]` | ❌ | `` | 第三方退款ID |
| `gateway_response` | `Optional[Dict[str, Any]]` | ❌ | `` | 网关响应 |
| `operator_note` | `Optional[str]` | ❌ | `` | 操作员备注 |

---

## `WechatPaymentCallback`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `payment_no` | `str` | ❌ | `` | 支付单号 |
| `status` | `str` | ❌ | `` | 支付状态 |
| `transaction_id` | `str` | ❌ | `` | 微信支付订单号 |
| `amount` | `Optional[Decimal]` | ❌ | `` | 支付金额 |
| `callback_data` | `Dict[str, Any]` | ❌ | `` | 回调原始数据 |
| `out_trade_no` | `str` | ❌ | `` | 商户订单号 |
| `trade_state` | `str` | ❌ | `` | 交易状态 |
| `trade_state_desc` | `str` | ❌ | `` | 交易状态描述 |
| `bank_type` | `Optional[str]` | ❌ | `` | 银行类型 |
| `success_time` | `Optional[str]` | ❌ | `` | 支付完成时间 |

---

