# 营销活动模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/marketing`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 优惠券系统API

### 1. 获取可用优惠券
#### GET /api/v1/marketing/coupons/available
获取用户可用的优惠券列表

**查询参数**:
- `user_id`: 用户ID
- `category`: 券类型 (discount/shipping/gift)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "新用户专享券",
      "type": "discount",
      "value": 50.00,
      "min_amount": 100.00,
      "expire_at": "2025-12-31T23:59:59Z"
    }
  ]
}
```

### 2. 使用优惠券
#### POST /api/v1/marketing/coupons/{coupon_id}/use
使用优惠券

**请求参数**:
```json
{
  "order_id": 12345,
  "user_id": 123
}
```

## 促销活动API

### 1. 获取活动列表
#### GET /api/v1/marketing/promotions
获取当前进行的促销活动

**查询参数**:
- `status`: 活动状态 (active/upcoming/ended)
- `type`: 活动类型 (flash_sale/bulk_discount/gift)

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "限时抢购",
      "type": "flash_sale",
      "discount_rate": 0.8,
      "start_time": "2025-09-13T10:00:00Z",
      "end_time": "2025-09-13T18:00:00Z",
      "products": [1, 2, 3]
    }
  ]
}
```

### 2. 参与促销活动
#### POST /api/v1/marketing/promotions/{promotion_id}/join
用户参与促销活动

**请求参数**:
```json
{
  "user_id": 123,
  "product_id": 1,
  "quantity": 2
}
```

## 营销工具API

### 1. 创建拼团
#### POST /api/v1/marketing/group-buy
创建拼团活动

**请求参数**:
```json
{
  "product_id": 1,
  "group_size": 5,
  "group_price": 80.00,
  "expire_hours": 24
}
```

### 2. 参与拼团
#### POST /api/v1/marketing/group-buy/{group_id}/join
参与已有拼团

**请求参数**:
```json
{
  "user_id": 123,
  "quantity": 1
}
```

## 活动分析API

### 1. 获取活动统计
#### GET /api/v1/marketing/analytics/{campaign_id}
获取活动效果统计

**响应示例**:
```json
{
  "success": true,
  "data": {
    "campaign_id": 1,
    "participants": 1250,
    "conversion_rate": 0.15,
    "revenue": 125000.00,
    "roi": 2.5
  }
}
```

## 错误响应

```json
{
  "success": false,
  "error_code": "COUPON_EXPIRED",
  "message": "优惠券已过期"
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 404: 活动不存在
- 409: 活动冲突（如已参与）
- 500: 服务器内部错误