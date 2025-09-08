# 事件 Schema 注册表

本目录包含平台所有事件的 Schema 定义，采用 JSON Schema 格式。

## 版本管理规则

- 每个事件类型使用独立文件：`{EventType}.v{Version}.json`
- 向后兼容原则：新版本只能新增可选字段，不能移除字段
- 字段弃用：使用 `deprecated: true` 标记，至少保留 2 个版本周期

## 当前事件列表

### 用户相关事件
- `User.Created.v1.json` - 用户创建事件
- `User.Updated.v1.json` - 用户更新事件

### 商品相关事件
- `Product.Created.v1.json` - 商品创建事件
- `Product.Updated.v1.json` - 商品更新事件

### 订单相关事件（预留）
- `Order.Created.v1.json` - 订单创建事件（Sprint 1 实现）
- `Order.Paid.v1.json` - 订单支付完成事件（Sprint 1 实现）
- `Order.Shipped.v1.json` - 订单发货事件（Sprint 1 实现）

### 支付相关事件（预留）
- `Payment.Started.v1.json` - 支付发起事件（Sprint 1 实现）
- `Payment.Succeeded.v1.json` - 支付成功事件（Sprint 1 实现）
- `Payment.Failed.v1.json` - 支付失败事件（Sprint 1 实现）

## 使用说明

1. 事件发布方必须按照对应 Schema 发布事件
2. 事件消费方必须能处理 Schema 中的所有必需字段
3. 新增字段时更新 Schema 文件并增加版本号
4. 重大变更需要在技术评审中讨论

## 示例事件结构

```json
{
  "event_id": "uuid",
  "event_type": "User.Created",
  "version": "1",
  "timestamp": "2025-09-08T12:00:00Z",
  "correlation_id": "uuid",
  "data": {
    "user_id": 123,
    "username": "user123",
    "email": "user@example.com"
  }
}
```
