# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `AddItemRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | 商品SKU ID |
| `quantity` | `int` | ❌ | `` | 商品数量 |

---

## `BatchDeleteRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `item_ids` | `List[int]` | ❌ | `` | 要删除的商品项ID列表 |

---

## `CartItemResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `item_id` | `int` | ❌ | `` | 商品项ID |
| `sku_id` | `int` | ❌ | `` | 商品SKU ID |
| `product_name` | `str` | ❌ | `` | 商品名称 |
| `product_image` | `Optional[str]` | ❌ | `` | 商品图片URL |
| `unit_price` | `Decimal` | ❌ | `` | 商品单价 |
| `quantity` | `int` | ❌ | `` | 商品数量 |
| `subtotal` | `Decimal` | ❌ | `` | 小计金额 |
| `stock_status` | `StockStatus` | ❌ | `` | 库存状态 |
| `available_stock` | `Optional[int]` | ❌ | `` | 可用库存数量 |
| `added_at` | `datetime` | ❌ | `` | 添加时间 |

---

## `CartResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `cart_id` | `int` | ❌ | `` | 购物车ID |
| `user_id` | `int` | ❌ | `` | 用户ID |
| `total_items` | `int` | ❌ | `` | 商品种类数量 |
| `total_quantity` | `int` | ❌ | `` | 商品总数量 |
| `total_amount` | `Decimal` | ❌ | `` | 购物车总金额 |
| `items` | `List[CartItemResponse]` | ❌ | `` | 购物车商品项列表 |
| `created_at` | `datetime` | ❌ | `` | 创建时间 |
| `updated_at` | `datetime` | ❌ | `` | 更新时间 |

---

## `CartUpdateResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `cart_id` | `int` | ❌ | `` | 购物车ID |
| `total_items` | `int` | ❌ | `` | 商品种类数量 |
| `total_quantity` | `int` | ❌ | `` | 商品总数量 |
| `total_amount` | `Decimal` | ❌ | `` | 购物车总金额 |
| `updated_item` | `Optional[UpdatedItemResponse]` | ❌ | `` | 更新的商品项 |
| `updated_at` | `datetime` | ❌ | `` | 更新时间 |

---

## `ErrorDetail`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `Optional[int]` | ❌ | `` | 相关商品SKU ID |
| `item_id` | `Optional[int]` | ❌ | `` | 相关商品项ID |
| `requested_quantity` | `Optional[int]` | ❌ | `` | 请求数量 |
| `available_stock` | `Optional[int]` | ❌ | `` | 可用库存 |
| `adjusted_quantity` | `Optional[int]` | ❌ | `` | 调整后数量 |

---

## `ErrorInfo`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `str` | ❌ | `` | 错误码 |
| `message` | `str` | ❌ | `` | 错误消息 |
| `details` | `Optional[ErrorDetail]` | ❌ | `` | 错误详情 |

---

## `SuccessResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `success` | `bool` | ❌ | `` | 操作是否成功 |
| `message` | `str` | ❌ | `` | 响应消息 |

---

## `UpdateQuantityRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `quantity` | `int` | ❌ | `` | 新的商品数量 |

---

## `UpdatedItemResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `item_id` | `int` | ❌ | `` | 商品项ID |
| `sku_id` | `int` | ❌ | `` | 商品SKU ID |
| `quantity` | `int` | ❌ | `` | 更新后数量 |
| `subtotal` | `Decimal` | ❌ | `` | 更新后小计 |

---

