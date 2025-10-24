# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `ApiResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `success` | `bool` | ❌ | `True` |  |
| `code` | `int` | ❌ | `200` |  |
| `message` | `str` | ❌ | `操作成功` |  |
| `data` | `Optional[T]` | ❌ | `` |  |
| `metadata` | `Optional[Dict[str, Any]]` | ❌ | `` |  |

---

## `OrderCancelRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `reason` | `Optional[str]` | ❌ | `` | 取消原因 |

---

## `OrderCreateRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `items` | `List[OrderItemRequest]` | ❌ | `` | 订单商品列表 |
| `shipping_address` | `ShippingAddressRequest` | ❌ | `` | 收货地址 |
| `notes` | `Optional[str]` | ❌ | `` | 订单备注 |

---

## `OrderDetailResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `created_at` | `datetime` | ✅ | `` |  |
| `updated_at` | `datetime` | ✅ | `` |  |
| `id` | `int` | ✅ | `` |  |
| `order_number` | `str` | ✅ | `` |  |
| `user_id` | `int` | ✅ | `` |  |
| `status` | `OrderStatus` | ✅ | `` |  |
| `subtotal` | `Decimal` | ✅ | `` |  |
| `shipping_fee` | `Decimal` | ✅ | `` |  |
| `discount_amount` | `Decimal` | ✅ | `` |  |
| `total_amount` | `Decimal` | ✅ | `` |  |
| `shipping_address` | `Optional[str]` | ❌ | `` |  |
| `receiver_name` | `Optional[str]` | ❌ | `` |  |
| `receiver_phone` | `Optional[str]` | ❌ | `` |  |
| `shipping_method` | `str` | ❌ | `standard` |  |
| `notes` | `Optional[str]` | ❌ | `` |  |
| `items` | `List[OrderItemResponse]` | ❌ | `` |  |
| `status_history` | `List['OrderStatusHistoryResponse']` | ❌ | `` |  |

---

## `OrderErrorDetail`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `type` | `str` | ✅ | `` |  |
| `details` | `List[Dict[str, Any]]` | ❌ | `` |  |

---

## `OrderErrorResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `success` | `bool` | ❌ | `False` |  |
| `code` | `int` | ✅ | `` |  |
| `message` | `str` | ✅ | `` |  |
| `error` | `Optional[OrderErrorDetail]` | ❌ | `` |  |
| `metadata` | `Optional[Dict[str, Any]]` | ❌ | `` |  |

---

## `OrderItemRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `product_id` | `int` | ❌ | `` | 商品ID |
| `sku_id` | `int` | ❌ | `` | SKU ID |
| `quantity` | `int` | ❌ | `` | 购买数量 |

---

## `OrderItemResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `order_id` | `int` | ✅ | `` |  |
| `product_id` | `int` | ✅ | `` |  |
| `sku_id` | `int` | ✅ | `` |  |
| `sku_code` | `str` | ✅ | `` |  |
| `product_name` | `str` | ✅ | `` |  |
| `sku_name` | `str` | ✅ | `` |  |
| `product_attributes` | `Optional[Dict[str, Any]]` | ❌ | `` |  |
| `product_image_url` | `Optional[str]` | ❌ | `` |  |
| `quantity` | `int` | ✅ | `` |  |
| `unit_price` | `Decimal` | ✅ | `` |  |
| `total_price` | `Decimal` | ✅ | `` |  |
| `created_at` | `datetime` | ✅ | `` |  |

---

## `OrderListQueryParams`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `status` | `Optional[OrderStatus]` | ❌ | `` | 订单状态筛选 |
| `page` | `int` | ❌ | `` | 页码 |
| `size` | `int` | ❌ | `` | 每页数量 |
| `start_date` | `Optional[str]` | ❌ | `` | 开始日期(YYYY-MM-DD) |
| `end_date` | `Optional[str]` | ❌ | `` | 结束日期(YYYY-MM-DD) |

---

## `OrderResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `created_at` | `datetime` | ✅ | `` |  |
| `updated_at` | `datetime` | ✅ | `` |  |
| `id` | `int` | ✅ | `` |  |
| `order_number` | `str` | ✅ | `` |  |
| `user_id` | `int` | ✅ | `` |  |
| `status` | `OrderStatus` | ✅ | `` |  |
| `subtotal` | `Decimal` | ✅ | `` |  |
| `shipping_fee` | `Decimal` | ✅ | `` |  |
| `discount_amount` | `Decimal` | ✅ | `` |  |
| `total_amount` | `Decimal` | ✅ | `` |  |
| `shipping_address` | `Optional[str]` | ❌ | `` |  |
| `receiver_name` | `Optional[str]` | ❌ | `` |  |
| `receiver_phone` | `Optional[str]` | ❌ | `` |  |
| `shipping_method` | `str` | ❌ | `standard` |  |
| `notes` | `Optional[str]` | ❌ | `` |  |

---

## `OrderStatisticsResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_orders` | `int` | ❌ | `` | 订单总数 |
| `pending_orders` | `int` | ❌ | `` | 待支付订单数 |
| `paid_orders` | `int` | ❌ | `` | 已支付订单数 |
| `shipped_orders` | `int` | ❌ | `` | 已发货订单数 |
| `delivered_orders` | `int` | ❌ | `` | 已送达订单数 |
| `cancelled_orders` | `int` | ❌ | `` | 已取消订单数 |
| `returned_orders` | `int` | ❌ | `` | 已退货订单数 |
| `total_amount` | `float` | ❌ | `` | 订单总金额 |
| `completion_rate` | `float` | ❌ | `` | 订单完成率（%） |
| `cancellation_rate` | `float` | ❌ | `` | 订单取消率（%） |

---

## `OrderStatusHistoryResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `order_id` | `int` | ✅ | `` |  |
| `old_status` | `Optional[str]` | ❌ | `` |  |
| `new_status` | `str` | ✅ | `` |  |
| `remark` | `Optional[str]` | ❌ | `` |  |
| `operator_id` | `Optional[int]` | ❌ | `` |  |
| `created_at` | `datetime` | ✅ | `` |  |

---

## `OrderStatusUpdateRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `status` | `OrderStatus` | ❌ | `` | 订单状态 |
| `remark` | `Optional[str]` | ❌ | `` | 状态变更备注 |

---

## `PaginatedResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `items` | `List[T]` | ❌ | `` | 数据项列表 |
| `page` | `int` | ❌ | `` | 当前页码 |
| `page_size` | `int` | ❌ | `` | 每页数量 |
| `total_count` | `int` | ❌ | `` | 总数据量 |

---

## `PaginationInfo`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `page` | `int` | ✅ | `` |  |
| `page_size` | `int` | ✅ | `` |  |
| `total_pages` | `int` | ✅ | `` |  |
| `total_items` | `int` | ✅ | `` |  |
| `has_next` | `bool` | ✅ | `` |  |
| `has_prev` | `bool` | ✅ | `` |  |

---

## `ShippingAddressRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `recipient` | `str` | ❌ | `` | 收货人 |
| `phone` | `str` | ❌ | `` | 联系电话 |
| `address` | `str` | ❌ | `` | 详细地址 |

---

## `ShippingAddressResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `recipient` | `str` | ❌ | `` | 收货人 |
| `phone` | `str` | ❌ | `` | 联系电话 |
| `address` | `str` | ❌ | `` | 详细地址 |

---

## `TimestampMixin`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `created_at` | `datetime` | ✅ | `` |  |
| `updated_at` | `datetime` | ✅ | `` |  |

---

