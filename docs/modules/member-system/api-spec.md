# 会员系统模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/members`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 会员等级管理API

### 1. 获取会员信息
#### GET /api/v1/members/{user_id}
获取用户会员信息

**请求参数**:
- `user_id`: 用户ID (path parameter)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "level": "gold",
    "level_name": "黄金会员",
    "points": 8500,
    "total_spent": 25000.00,
    "next_level": "platinum",
    "next_level_requirement": 50000.00
  }
}
```

### 2. 更新会员等级
#### PUT /api/v1/members/{user_id}/level
更新用户会员等级

**请求参数**:
```json
{
  "level": "platinum",
  "reason": "消费金额达标"
}
```

## 积分系统API

### 1. 获取积分记录
#### GET /api/v1/members/{user_id}/points
获取用户积分记录

**查询参数**:
- `page`: 页码
- `limit`: 每页数量
- `type`: 积分类型 (earn/spend)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total": 8500,
    "records": [
      {
        "id": 1,
        "type": "earn",
        "amount": 100,
        "description": "购物获得积分",
        "created_at": "2025-09-13T10:00:00Z"
      }
    ]
  }
}
```

### 2. 积分兑换
#### POST /api/v1/members/{user_id}/points/redeem
积分兑换商品或优惠券

**请求参数**:
```json
{
  "reward_id": 1,
  "points_cost": 1000,
  "reward_type": "coupon"
}
```

## 会员权益API

### 1. 获取会员权益
#### GET /api/v1/members/{user_id}/benefits
获取用户可享受的会员权益

**响应示例**:
```json
{
  "success": true,
  "data": {
    "level": "gold",
    "benefits": [
      {
        "type": "discount",
        "value": 0.95,
        "description": "全场95折"
      },
      {
        "type": "shipping",
        "value": "free",
        "description": "免费配送"
      }
    ]
  }
}
```

## 错误响应

所有API的错误响应格式统一为：
```json
{
  "success": false,
  "error_code": "MEMBER_NOT_FOUND",
  "message": "会员信息不存在"
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 404: 会员信息不存在
- 500: 服务器内部错误