# 会员系统模块 - API设计文档

📅 **创建日期**: 2024-09-17  
👤 **设计者**: 技术负责人  
✅ **评审状态**: 设计中  
🔄 **最后更新**: 2024-09-17  

## API概述

### 基础信息
- **基础路径**: `/api/v1/member-system`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API版本**: v1.0

### 通用响应格式
```json
{
  "code": 200,
  "message": "success", 
  "data": {},
  "timestamp": "2024-09-17T10:00:00Z"
}
```

### 错误码定义
| 错误码 | HTTP状态码 | 错误信息 | 描述 |
|--------|------------|----------|------|
| 200 | 200 | success | 请求成功 |
| 400 | 400 | invalid_request | 请求参数错误 |
| 401 | 401 | unauthorized | 未授权访问 |
| 403 | 403 | forbidden | 权限不足 |
| 404 | 404 | not_found | 资源不存在 |
| 409 | 409 | conflict | 数据冲突 |
| 500 | 500 | internal_error | 服务器内部错误 |

## 会员信息管理 API

### 1. 获取会员信息
**GET** `/member-system/profile`

获取当前用户的完整会员信息

**请求参数**: 无（从JWT token获取用户ID）

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "member_id": "M123456789",
    "user_id": 1001,
    "level": {
      "level_id": 3,
      "level_name": "银牌会员",
      "level_code": "SILVER",
      "discount_rate": 0.9,
      "point_multiplier": 1.0
    },
    "points": {
      "total_points": 2580,
      "available_points": 2380,
      "frozen_points": 200,
      "expiring_points": 500,
      "expiring_date": "2025-01-15"
    },
    "statistics": {
      "total_spent": 2500.00,
      "total_orders": 15,
      "join_date": "2024-01-15",
      "last_active": "2024-09-17T09:30:00Z"
    },
    "benefits": {
      "free_shipping": true,
      "birthday_gift": true,
      "priority_service": false,
      "exclusive_events": false
    },
    "next_level": {
      "level_name": "金牌会员",
      "required_spent": 5000.00,
      "remaining_spent": 2500.00,
      "progress_percentage": 50.0
    }
  }
}
```

### 2. 更新会员信息
**PUT** `/member-system/profile`

更新会员可修改的基础信息

**请求参数**:
```json
{
  "nickname": "新昵称",
  "birthday": "1990-01-15",
  "preferences": {
    "notification_email": true,
    "notification_sms": false,
    "marketing_consent": true
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "会员信息更新成功",
  "data": {
    "updated_fields": ["nickname", "birthday", "preferences"],
    "updated_at": "2024-09-17T10:00:00Z"
  }
}
```

## 会员等级管理 API

### 3. 获取等级列表
**GET** `/member-system/levels`

获取所有会员等级信息和权益对比

**请求参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "levels": [
      {
        "level_id": 1,
        "level_name": "注册会员",
        "level_code": "BASIC",
        "required_spent": 0,
        "discount_rate": 1.0,
        "point_multiplier": 1.0,
        "benefits": {
          "free_shipping": false,
          "birthday_gift": false,
          "priority_service": false,
          "exclusive_events": false
        }
      },
      {
        "level_id": 2,
        "level_name": "铜牌会员", 
        "level_code": "BRONZE",
        "required_spent": 500,
        "discount_rate": 0.95,
        "point_multiplier": 1.0,
        "benefits": {
          "free_shipping": false,
          "birthday_gift": true,
          "priority_service": false,
          "exclusive_events": false
        }
      }
    ]
  }
}
```

### 4. 手动升级会员等级（管理员接口）
**POST** `/member-system/levels/upgrade`

管理员手动调整用户会员等级

**请求参数**:
```json
{
  "user_id": 1001,
  "target_level_id": 4,
  "reason": "客服手动调整",
  "operator": "admin001"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "等级调整成功",
  "data": {
    "old_level": "银牌会员",
    "new_level": "金牌会员",
    "effective_time": "2024-09-17T10:00:00Z",
    "operation_id": "OP123456789"
  }
}
```

## 积分管理 API

### 5. 获取积分明细
**GET** `/member-system/points/transactions`

获取用户积分收支明细记录

**请求参数**:
```
?page=1&limit=20&type=all&start_date=2024-08-01&end_date=2024-09-17
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "summary": {
      "total_earned": 3200,
      "total_used": 820,
      "current_balance": 2380
    },
    "transactions": [
      {
        "transaction_id": "PT123456789",
        "type": "EARN",
        "event_type": "PURCHASE",
        "points": 250,
        "description": "购物获得积分",
        "related_order": "ORD123456",
        "created_at": "2024-09-16T14:30:00Z",
        "expiry_date": "2026-09-16"
      },
      {
        "transaction_id": "PT123456790",
        "type": "USE",
        "event_type": "REDEMPTION",
        "points": -100,
        "description": "积分抵扣",
        "related_order": "ORD123457",
        "created_at": "2024-09-15T10:15:00Z",
        "expiry_date": null
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

### 6. 积分获得接口
**POST** `/member-system/points/earn`

记录用户积分获得（内部服务调用）

**请求参数**:
```json
{
  "user_id": 1001,
  "event_type": "PURCHASE",
  "points": 250,
  "description": "订单ORD123456购物获得积分",
  "related_order": "ORD123456",
  "related_data": {
    "order_amount": 250.00,
    "point_rate": 1.0
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "积分发放成功",
  "data": {
    "transaction_id": "PT123456789",
    "points_earned": 250,
    "total_points": 2630,
    "expiry_date": "2026-09-17",
    "level_upgraded": false
  }
}
```

### 7. 积分使用接口
**POST** `/member-system/points/use`

使用积分进行抵扣

**请求参数**:
```json
{
  "user_id": 1001,
  "points_to_use": 100,
  "order_amount": 200.00,
  "order_id": "ORD123457"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "积分使用成功",
  "data": {
    "transaction_id": "PT123456790",
    "points_used": 100,
    "discount_amount": 1.00,
    "remaining_points": 2530,
    "final_amount": 199.00
  }
}
```

### 8. 积分兑换商品
**POST** `/member-system/points/redeem`

使用积分兑换指定商品或权益

**请求参数**:
```json
{
  "redemption_item_id": "GIFT001",
  "quantity": 1,
  "delivery_address": {
    "name": "张三",
    "phone": "13800138000",
    "address": "北京市朝阳区xxx街道xxx号"
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "兑换成功",
  "data": {
    "redemption_id": "RED123456789",
    "item_name": "积分商城礼品",
    "points_cost": 500,
    "remaining_points": 2030,
    "estimated_delivery": "2024-09-20",
    "tracking_code": null
  }
}
```

## 权益管理 API

### 9. 获取可用权益
**GET** `/member-system/benefits/available`

获取当前会员可用的所有权益

**请求参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "current_level": "银牌会员",
    "benefits": [
      {
        "benefit_id": "B001",
        "benefit_name": "会员专享折扣",
        "benefit_type": "DISCOUNT",
        "value": 0.9,
        "description": "全场商品9折优惠",
        "usage_limit": null,
        "used_count": 0,
        "valid_until": null
      },
      {
        "benefit_id": "B002", 
        "benefit_name": "免运费",
        "benefit_type": "FREE_SHIPPING",
        "value": 1,
        "description": "全场免运费",
        "usage_limit": null,
        "used_count": 15,
        "valid_until": null
      },
      {
        "benefit_id": "B003",
        "benefit_name": "生日礼品",
        "benefit_type": "BIRTHDAY_GIFT",
        "value": 1,
        "description": "生日月份专属礼品",
        "usage_limit": 1,
        "used_count": 0,
        "valid_until": "2024-12-31"
      }
    ]
  }
}
```

### 10. 使用权益
**POST** `/member-system/benefits/use`

使用指定权益（内部服务调用）

**请求参数**:
```json
{
  "user_id": 1001,
  "benefit_id": "B001",
  "order_id": "ORD123458",
  "usage_context": {
    "original_amount": 100.00,
    "discount_applied": 10.00
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "权益使用成功",
  "data": {
    "usage_id": "BU123456789",
    "benefit_name": "会员专享折扣",
    "discount_amount": 10.00,
    "remaining_usage": null,
    "used_at": "2024-09-17T10:00:00Z"
  }
}
```

## 会员活动 API

### 11. 获取会员活动列表
**GET** `/member-system/activities`

获取当前可参与的会员专属活动

**请求参数**:
```
?status=active&category=all&page=1&limit=10
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success", 
  "data": {
    "activities": [
      {
        "activity_id": "ACT123456",
        "title": "银牌会员双倍积分周",
        "description": "银牌及以上会员购物享受双倍积分奖励",
        "category": "POINTS_PROMOTION",
        "required_level": 3,
        "start_time": "2024-09-15T00:00:00Z",
        "end_time": "2024-09-22T23:59:59Z",
        "participation_count": 156,
        "max_participants": 1000,
        "is_eligible": true,
        "is_participated": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

### 12. 参与会员活动
**POST** `/member-system/activities/{activity_id}/join`

参与指定的会员活动

**路径参数**:
- `activity_id`: 活动ID

**请求参数**: 
```json
{
  "participation_data": {
    "contact_phone": "13800138000",
    "preferences": ["电子产品", "服装"]
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "活动参与成功",
  "data": {
    "participation_id": "PAR123456789",
    "activity_title": "银牌会员双倍积分周", 
    "joined_at": "2024-09-17T10:00:00Z",
    "benefits_activated": ["double_points"],
    "next_action": "开始购物享受双倍积分奖励"
  }
}
```

## 统计分析 API

### 13. 获取会员统计数据（管理员接口）
**GET** `/member-system/admin/statistics`

获取会员系统整体统计数据

**请求参数**:
```
?date_range=30d&group_by=level&metrics=count,revenue,activity
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "overview": {
      "total_members": 15420,
      "active_members": 8350,
      "new_members_this_month": 1240,
      "total_points_issued": 2580000,
      "total_points_redeemed": 890000
    },
    "level_distribution": [
      {
        "level_name": "注册会员",
        "count": 8500,
        "percentage": 55.1,
        "avg_spent": 150.00,
        "avg_points": 120
      },
      {
        "level_name": "铜牌会员",
        "count": 4200,
        "percentage": 27.2,
        "avg_spent": 750.00,
        "avg_points": 680
      }
    ],
    "trends": {
      "member_growth": [
        {
          "date": "2024-09-01",
          "new_members": 42,
          "upgraded_members": 15
        }
      ],
      "points_activity": [
        {
          "date": "2024-09-01", 
          "points_earned": 12500,
          "points_used": 8300
        }
      ]
    }
  }
}
```

## 批量操作 API

### 14. 批量积分操作（管理员接口）
**POST** `/member-system/admin/points/batch`

批量给用户发放或扣除积分

**请求参数**:
```json
{
  "operation_type": "EARN",
  "reason": "系统补偿积分", 
  "operator": "admin001",
  "users": [
    {
      "user_id": 1001,
      "points": 100,
      "note": "订单异常补偿"
    },
    {
      "user_id": 1002,
      "points": 150,
      "note": "活动奖励"
    }
  ]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "批量操作成功",
  "data": {
    "batch_id": "BAT123456789",
    "total_users": 2,
    "successful_count": 2,
    "failed_count": 0,
    "total_points": 250,
    "results": [
      {
        "user_id": 1001,
        "status": "success",
        "transaction_id": "PT123456791",
        "points": 100
      },
      {
        "user_id": 1002,
        "status": "success", 
        "transaction_id": "PT123456792",
        "points": 150
      }
    ]
  }
}
```

## WebHook通知接口

### 15. 会员事件通知
**POST** `/member-system/webhooks/events`

接收其他服务的会员相关事件通知

**请求参数**:
```json
{
  "event_type": "ORDER_COMPLETED",
  "event_data": {
    "user_id": 1001,
    "order_id": "ORD123456",
    "order_amount": 299.99,
    "payment_time": "2024-09-17T10:00:00Z",
    "items": [
      {
        "product_id": "P123",
        "category": "electronics",
        "quantity": 1,
        "price": 299.99
      }
    ]
  },
  "timestamp": "2024-09-17T10:01:00Z",
  "signature": "webhook_signature_hash"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "事件处理成功",
  "data": {
    "processed_actions": [
      {
        "action": "points_earned",
        "points": 300,
        "transaction_id": "PT123456793"
      },
      {
        "action": "level_check", 
        "level_changed": false,
        "current_level": "银牌会员"
      }
    ],
    "processed_at": "2024-09-17T10:01:05Z"
  }
}
```

## API认证和授权

### JWT Token格式
```json
{
  "sub": "1001",
  "username": "user001",
  "role": "member",
  "level": 3,
  "iat": 1694944800,
  "exp": 1694951000
}
```

### 权限级别
- **public**: 无需认证
- **member**: 需要用户登录
- **admin**: 需要管理员权限
- **internal**: 仅内部服务调用

### 接口权限矩阵
| 接口 | 权限级别 | 说明 |
|------|----------|------|
| GET /profile | member | 获取自己的会员信息 |
| PUT /profile | member | 更新自己的会员信息 |
| GET /levels | public | 查看等级体系 |
| POST /levels/upgrade | admin | 管理员调整等级 |
| GET /points/transactions | member | 查看自己的积分明细 |
| POST /points/earn | internal | 内部服务发放积分 |
| POST /points/use | member | 使用积分 |
| GET /admin/statistics | admin | 管理员统计数据 |
| POST /admin/points/batch | admin | 批量积分操作 |
| POST /webhooks/events | internal | 接收事件通知 |

## 错误处理示例

### 400 - 请求参数错误
```json
{
  "code": 400,
  "message": "请求参数错误",
  "data": {
    "errors": [
      {
        "field": "points_to_use",
        "message": "积分使用数量必须大于0"
      },
      {
        "field": "order_amount", 
        "message": "订单金额格式不正确"
      }
    ]
  },
  "timestamp": "2024-09-17T10:00:00Z"
}
```

### 409 - 业务冲突
```json
{
  "code": 409,
  "message": "积分余额不足",
  "data": {
    "required_points": 500,
    "available_points": 300,
    "shortage": 200
  },
  "timestamp": "2024-09-17T10:00:00Z"
}
```

## 性能考虑

### 缓存策略
- 会员等级信息：Redis缓存，TTL 1小时
- 积分余额：Redis缓存，TTL 5分钟
- 权益列表：Redis缓存，TTL 30分钟

### 限流规则
- 普通用户：100 请求/分钟
- 管理员用户：1000 请求/分钟
- 内部服务：无限制

### 数据库优化
- 积分明细表按月分表
- 会员行为日志异步写入
- 统计数据定时预计算