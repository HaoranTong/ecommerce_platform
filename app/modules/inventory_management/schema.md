# API Schemas

> 自动生成于 schemas.py，勿手动修改

## `APIResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `code` | `int` | ❌ | `` |  |
| `message` | `str` | ❌ | `` |  |
| `data` | `Optional[Union[dict, list]]` | ❌ | `` |  |
| `timestamp` | `datetime` | ❌ | `` |  |

---

## `AdjustmentResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `old_quantity` | `int` | ✅ | `` |  |
| `new_quantity` | `int` | ✅ | `` |  |
| `adjustment_quantity` | `int` | ✅ | `` |  |
| `transaction_id` | `str` | ✅ | `` |  |

---

## `BatchInventoryQuery`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_ids` | `List[int]` | ❌ | `` | SKU ID列表 |

---

## `CleanupResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `cleaned_reservations` | `int` | ✅ | `` |  |
| `released_quantity` | `int` | ✅ | `` |  |

---

## `ConsistencyCheckItem`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `issue` | `str` | ✅ | `` |  |
| `suggested_action` | `str` | ✅ | `` |  |

---

## `ConsistencyCheckResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total_skus` | `int` | ✅ | `` |  |
| `inconsistent_skus` | `int` | ✅ | `` |  |
| `details` | `List[ConsistencyCheckItem]` | ✅ | `` |  |

---

## `DeductItem`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | SKU ID |
| `quantity` | `int` | ❌ | `` | 扣减数量 |
| `reservation_id` | `Optional[str]` | ❌ | `` | 对应的预占记录ID |

---

## `DeductItemResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `deducted_quantity` | `int` | ✅ | `` |  |
| `remaining_quantity` | `int` | ✅ | `` |  |

---

## `DeductResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `order_id` | `str` | ✅ | `` |  |
| `deducted_items` | `List[DeductItemResponse]` | ✅ | `` |  |

---

## `ErrorDetail`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `Optional[str]` | ❌ | `` |  |
| `requested` | `Optional[int]` | ❌ | `` |  |
| `available` | `Optional[int]` | ❌ | `` |  |
| `message` | `str` | ✅ | `` |  |

---

## `InventoryAdjustment`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | SKU ID |
| `adjustment_type` | `AdjustmentTypeEnum` | ❌ | `` | 调整类型 |
| `quantity` | `int` | ❌ | `` | 调整数量 |
| `reason` | `str` | ❌ | `` | 调整原因 |
| `reference` | `Optional[str]` | ❌ | `` | 参考单号 |

---

## `InventoryDeductRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `order_id` | `str` | ❌ | `` | 订单ID |
| `items` | `List[DeductItem]` | ❌ | `` | 扣减商品列表 |

---

## `InventoryEvent`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `event_type` | `str` | ❌ | `` | 事件类型 |
| `event_id` | `str` | ❌ | `` | 事件ID |
| `timestamp` | `datetime` | ❌ | `` |  |
| `data` | `dict` | ❌ | `` | 事件数据 |

---

## `InventoryTransactionRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `id` | `int` | ✅ | `` |  |
| `sku_id` | `int` | ✅ | `` |  |
| `transaction_type` | `TransactionTypeEnum` | ✅ | `` |  |
| `quantity_change` | `int` | ✅ | `` |  |
| `quantity_before` | `int` | ✅ | `` |  |
| `quantity_after` | `int` | ✅ | `` |  |
| `reason` | `Optional[str]` | ❌ | `` |  |
| `reference_id` | `Optional[str]` | ❌ | `` |  |
| `operator_id` | `Optional[int]` | ❌ | `` |  |
| `created_at` | `datetime` | ✅ | `` |  |

---

## `LowStockItem`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `current_quantity` | `int` | ✅ | `` |  |
| `warning_threshold` | `int` | ✅ | `` |  |
| `critical_threshold` | `int` | ✅ | `` |  |
| `level` | `str` | ❌ | `` | 预警级别: warning/critical |

---

## `LowStockQuery`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `level` | `Optional[str]` | ❌ | `` | 预警级别 |
| `limit` | `int` | ❌ | `` |  |
| `offset` | `int` | ❌ | `` |  |

---

## `LowStockWarningEvent`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `current_quantity` | `int` | ✅ | `` |  |
| `threshold` | `int` | ✅ | `` |  |
| `level` | `str` | ✅ | `` |  |

---

## `PaginatedResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total` | `int` | ✅ | `` |  |
| `items` | `List[Union[SKUInventoryRead, LowStockItem, InventoryTransactionRead]]` | ✅ | `` |  |
| `page` | `int` | ✅ | `` |  |
| `page_size` | `int` | ✅ | `` |  |
| `total_pages` | `int` | ✅ | `` |  |

---

## `ReleaseReservationRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `reservation_id` | `Optional[str]` | ❌ | `` | 预占记录ID |
| `user_id` | `Optional[str]` | ❌ | `` | 用户ID（释放该用户所有预占） |

---

## `ReservationItem`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | SKU ID |
| `quantity` | `int` | ❌ | `` | 预占数量 |

---

## `ReservationItemResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `reserved_quantity` | `int` | ✅ | `` |  |
| `available_after_reserve` | `int` | ✅ | `` |  |

---

## `ReservationResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `reservation_id` | `str` | ✅ | `` |  |
| `expires_at` | `datetime` | ✅ | `` |  |
| `reserved_items` | `List[ReservationItemResponse]` | ✅ | `` |  |

---

## `ReserveRequest`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `reservation_type` | `ReservationTypeEnum` | ❌ | `` | 预占类型 |
| `reference_id` | `str` | ❌ | `` | 关联ID（用户ID或订单ID） |
| `items` | `List[ReservationItem]` | ❌ | `` | 预占商品列表 |
| `expires_minutes` | `int` | ❌ | `` | 预占有效期（分钟） |

---

## `SKUInventoryBase`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | SKU唯一标识符 |
| `available_quantity` | `int` | ❌ | `` | 可用库存数量 |
| `reserved_quantity` | `int` | ❌ | `` | 预占库存数量 |
| `total_quantity` | `int` | ❌ | `` | 总库存数量 |
| `warning_threshold` | `int` | ❌ | `` | 库存预警阈值 |
| `critical_threshold` | `int` | ❌ | `` | 库存严重不足阈值 |

---

## `SKUInventoryCreate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | SKU ID |
| `initial_quantity` | `int` | ❌ | `` | 初始库存数量 |
| `warning_threshold` | `int` | ❌ | `` | 库存预警阈值 |
| `critical_threshold` | `int` | ❌ | `` | 库存严重不足阈值 |

---

## `SKUInventoryRead`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ❌ | `` | SKU唯一标识符 |
| `available_quantity` | `int` | ❌ | `` | 可用库存数量 |
| `reserved_quantity` | `int` | ❌ | `` | 预占库存数量 |
| `total_quantity` | `int` | ❌ | `` | 总库存数量 |
| `warning_threshold` | `int` | ❌ | `` | 库存预警阈值 |
| `critical_threshold` | `int` | ❌ | `` | 库存严重不足阈值 |
| `id` | `int` | ✅ | `` |  |
| `is_low_stock` | `bool` | ❌ | `` | 是否库存不足 |
| `is_critical_stock` | `bool` | ❌ | `` | 是否库存严重不足 |
| `is_out_of_stock` | `bool` | ❌ | `` | 是否缺货 |
| `is_active` | `bool` | ❌ | `` | 是否启用库存管理 |
| `updated_at` | `datetime` | ❌ | `` | 最后更新时间 |

---

## `SKUInventorySimple`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `available_quantity` | `int` | ✅ | `` |  |
| `reserved_quantity` | `int` | ✅ | `` |  |
| `total_quantity` | `int` | ✅ | `` |  |
| `is_low_stock` | `bool` | ✅ | `` |  |

---

## `SKUInventoryUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `warning_threshold` | `Optional[int]` | ❌ | `` | 库存预警阈值 |
| `critical_threshold` | `Optional[int]` | ❌ | `` | 库存严重不足阈值 |
| `is_active` | `Optional[bool]` | ❌ | `` | 是否启用库存管理 |

---

## `StockAdjustedEvent`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `old_quantity` | `int` | ✅ | `` |  |
| `new_quantity` | `int` | ✅ | `` |  |
| `adjustment_type` | `AdjustmentTypeEnum` | ✅ | `` |  |
| `operator_id` | `int` | ✅ | `` |  |

---

## `StockDeductedEvent`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `quantity` | `int` | ✅ | `` |  |
| `order_id` | `str` | ✅ | `` |  |

---

## `StockReleasedEvent`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `quantity` | `int` | ✅ | `` |  |
| `reservation_id` | `str` | ✅ | `` |  |

---

## `StockReservedEvent`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `quantity` | `int` | ✅ | `` |  |
| `reservation_id` | `str` | ✅ | `` |  |
| `user_id` | `Optional[str]` | ❌ | `` |  |

---

## `ThresholdUpdate`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `warning_threshold` | `int` | ❌ | `` | 库存预警阈值 |
| `critical_threshold` | `int` | ❌ | `` | 库存严重不足阈值 |

---

## `TransactionQuery`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_ids` | `Optional[List[int]]` | ❌ | `` | SKU ID列表 |
| `transaction_types` | `Optional[List[TransactionTypeEnum]]` | ❌ | `` | 变动类型列表 |
| `operator_id` | `Optional[int]` | ❌ | `` | 操作人ID |
| `start_date` | `Optional[str]` | ❌ | `` | 开始日期 |
| `end_date` | `Optional[str]` | ❌ | `` | 结束日期 |
| `limit` | `int` | ❌ | `` |  |
| `offset` | `int` | ❌ | `` |  |

---

## `TransactionSearchResponse`

| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `sku_id` | `int` | ✅ | `` |  |
| `total` | `int` | ✅ | `` |  |
| `logs` | `List[InventoryTransactionRead]` | ✅ | `` |  |

---

