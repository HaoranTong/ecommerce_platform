---
title: "会员系统模块 API 规范"
version: "v1.0.0"
status: "active"
created: "2025-09-18"
updated: "2025-10-22"
owner: "API架构师"
dependencies:
  - "docs/standards/api-standards.md"
  - "docs/design/modules/member-system/design.md"
labels:
  - "member-system"
  - "api-specification"
  - "restful"
---

# 会员系统模块 API 规范

## 1. 文档信息与依赖

| 项目 | 值 |
|------|----|
| 模块名称 | 会员系统模块 (Member System) |
| API版本 | v1 |
| 文档版本 | v1.0.0 |
| 依据标准 | [API设计标准](../../../standards/api-standards.md) |
| 设计对齐 | [design.md](./design.md) 第5章 接口设计 |

## 2. API 概览

### 服务描述
会员系统模块提供会员档案管理、积分系统和等级管理的完整API服务，支持会员生命周期的全流程操作。

### 版本信息
- **API版本**: v1
- **基础路径**: `/api/v1/member-system`
- **协议**: HTTPS
- **数据格式**: JSON (application/json)
- **字符编码**: UTF-8

## 3. 认证与授权要求

### 认证方式
- **类型**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`
- **获取方式**: 通过用户认证模块获取

### 权限模型
| 权限级别 | 描述 | 适用接口 |
|---------|------|----------|
| `member:read` | 读取会员信息 | GET /profile, GET /points |
| `member:write` | 修改会员信息 | PUT /profile |
| `member:points` | 积分操作 | POST /points/earn, POST /points/use |
| `admin:member` | 管理员权限 | 所有管理接口 |

## 4. 接口列表

| 接口名称 | 方法 | 路径 | 描述 | 幂等性 |
|---------|------|------|------|--------|
| 获取会员信息 | GET | `/profile` | 获取当前用户会员档案 | ✅ |
| 更新会员信息 | PUT | `/profile` | 更新会员个人信息 | ✅ |
| 获取积分余额 | GET | `/points` | 获取积分账户详情 | ✅ |
| 积分获得 | POST | `/points/earn` | 记录积分获得 | ❌ |
| 积分使用 | POST | `/points/use` | 使用积分抵扣 | ❌ |
| 积分历史 | GET | `/points/transactions` | 获取积分变动记录 | ✅ |
| 获取等级列表 | GET | `/levels` | 获取所有会员等级 | ✅ |
| 获取等级权益 | GET | `/levels/{level_id}/benefits` | 获取等级权益详情 | ✅ |

## 5. 请求参数规范

### 通用参数
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `user_id` | integer | 是 | 用户唯一标识 | 12345 |
| `member_id` | integer | 是 | 会员唯一标识 | 67890 |
| `points` | integer | 是 | 积分数量(1-999999) | 100 |
| `page` | integer | 否 | 页码(默认1) | 1 |
| `limit` | integer | 否 | 每页数量(默认20,最大100) | 20 |

### 日期时间格式
| 格式 | 说明 | 示例 |
|------|------|------|
| `date` | ISO 8601日期格式 | "2025-09-18" |
| `datetime` | ISO 8601时间格式 | "2025-09-18T10:30:00Z" |

### 积分操作参数
| 参数名 | 类型 | 必填 | 说明 | 约束 |
|--------|------|------|------|------|
| `points` | integer | 是 | 积分数量 | 1-999999 |
| `source_type` | string | 是 | 积分来源类型 | order_complete, sign_in, activity |
| `source_id` | string | 是 | 来源记录ID | 最大50字符 |
| `description` | string | 否 | 操作描述 | 最大200字符 |

## 6. 响应结构规范

### 标准成功响应
```json
{
  "data": {
    // 具体业务数据
  },
  "meta": {
    "timestamp": "2025-10-22T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

### 分页响应结构
```json
{
  "data": [
    // 数据数组
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### 会员信息响应结构
```json
{
  "data": {
    "member_id": 12345,
    "member_code": "M2025091800001",
    "user_id": 67890,
    "level": {
      "id": 2,
      "name": "银牌会员",
      "discount_rate": 0.95,
      "min_spent": 1000.00
    },
    "points": {
      "current": 1580,
      "frozen": 200,
      "total_earned": 3200,
      "total_used": 1620
    },
    "profile": {
      "join_date": "2024-06-15",
      "total_spent": 12680.00,
      "status": 1,
      "last_active": "2025-09-18T09:15:00Z"
    }
  }
}
```

### 积分交易响应结构
```json
{
  "data": {
    "transaction_id": "PT_2025091800001",
    "type": "earn",
    "points_change": 100,
    "current_balance": 1680,
    "description": "订单完成奖励积分",
    "source_type": "order_complete",
    "source_id": "ORDER_2025091800001",
    "created_at": "2025-09-18T10:30:00Z"
  }
}
```

## 7. 错误码与处理策略

### HTTP状态码使用
| 状态码 | 使用场景 | 说明 |
|--------|----------|------|
| `200` | 成功响应 | GET/PUT操作成功 |
| `201` | 创建成功 | POST操作成功创建资源 |
| `204` | 无内容 | DELETE操作成功 |
| `400` | 请求错误 | 参数验证失败 |
| `401` | 未认证 | Token缺失或无效 |
| `403` | 无权限 | Token有效但权限不足 |
| `404` | 资源不存在 | 请求的资源未找到 |
| `409` | 资源冲突 | 业务规则冲突 |
| `500` | 服务器错误 | 系统内部错误 |

### 业务错误码
| 错误码 | HTTP状态码 | 描述 | 处理建议 |
|--------|-----------|------|----------|
| `MEMBER_001` | 404 | 会员信息不存在 | 检查用户是否已注册会员 |
| `MEMBER_002` | 409 | 积分余额不足 | 提示用户余额不足 |
| `MEMBER_003` | 409 | 无效的等级升级 | 检查升级条件 |
| `MEMBER_004` | 409 | 会员状态异常 | 联系客服处理 |
| `MEMBER_005` | 409 | 积分已过期 | 提示用户积分过期 |
| `MEMBER_006` | 409 | 重复的积分操作 | 检查操作唯一性 |

### 错误响应格式
```json
{
  "error": {
    "code": "MEMBER_002",
    "message": "积分余额不足",
    "details": {
      "required_points": 500,
      "current_balance": 300,
      "member_id": 12345
    },
    "timestamp": "2025-10-22T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## 8. 接口详细定义

### 8.1 会员信息管理

#### GET /profile
**功能**: 获取当前用户会员信息  
**权限**: member:read  
**参数**: 无 (从JWT token中获取user_id)

**成功响应**: 200 OK
```json
{
  "data": {
    "member_id": 12345,
    "member_code": "M2025091800001",
    "user_id": 67890,
    "level": {
      "id": 2,
      "name": "银牌会员",
      "discount_rate": 0.95
    },
    "points": {
      "current": 1580,
      "total_earned": 3200,
      "total_used": 1620
    },
    "profile": {
      "join_date": "2024-06-15",
      "total_spent": 12680.00,
      "status": 1,
      "last_active": "2025-09-18T09:15:00Z"
    }
  }
}
```

#### PUT /profile
**功能**: 更新会员个人信息  
**权限**: member:write  
**请求体**:
```json
{
  "birthday": "1990-05-20",
  "preferences": {
    "newsletter": true,
    "sms_notification": false,
    "promotion_notification": true
  }
}
```

**成功响应**: 200 OK + 更新后的会员信息

### 8.2 积分管理

#### GET /points
**功能**: 获取积分账户详情  
**权限**: member:read

**成功响应**: 200 OK
```json
{
  "data": {
    "current_points": 1580,
    "frozen_points": 200,
    "total_earned": 3200,
    "total_used": 1620,
    "pending_expiry": [
      {
        "points": 300,
        "expire_date": "2025-12-31"
      }
    ]
  }
}
```

#### POST /points/earn
**功能**: 系统积分发放接口  
**权限**: system, admin  
**请求体**:
```json
{
  "user_id": 12345,
  "points": 100,
  "source_type": "order_complete",
  "source_id": "ORDER_2025091800001",
  "description": "订单完成奖励积分"
}
```

**成功响应**: 201 Created
```json
{
  "data": {
    "transaction_id": "PT_2025091800001",
    "points_earned": 100,
    "current_balance": 1680,
    "transaction_time": "2025-09-18T10:30:00Z"
  }
}
```

#### POST /points/use
**功能**: 积分使用接口  
**权限**: member:points  
**请求体**:
```json
{
  "points": 500,
  "usage_type": "order_discount",
  "reference_id": "ORDER_2025091800002",
  "description": "订单积分抵扣"
}
```

**成功响应**: 201 Created + 交易确认信息

#### GET /points/transactions
**功能**: 获取积分变动历史  
**权限**: member:read  
**查询参数**:
- `page` (int, optional): 页码，默认1
- `limit` (int, optional): 每页数量，默认20
- `type` (string, optional): 交易类型过滤 (earn|use)
- `start_date` (date, optional): 开始日期
- `end_date` (date, optional): 结束日期

**成功响应**: 200 OK + 分页数据

### 8.3 等级管理

#### GET /levels
**功能**: 获取会员等级列表  
**权限**: public (无需认证)

**成功响应**: 200 OK
```json
{
  "data": [
    {
      "id": 1,
      "name": "铜牌会员",
      "min_spent": 0,
      "discount_rate": 1.000,
      "benefits": ["基础客服", "生日祝福"]
    },
    {
      "id": 2,
      "name": "银牌会员", 
      "min_spent": 1000,
      "discount_rate": 0.950,
      "benefits": ["优先客服", "生日折扣", "免邮特权"]
    }
  ]
}
```

#### GET /levels/{level_id}/benefits
**功能**: 获取等级权益详情  
**权限**: public  
**参数**: level_id (int, path): 等级ID

**成功响应**: 200 OK + 权益详情

## 9. 数据验证规范

### 请求参数验证
- **member_code**: 格式 M + 年月日 + 4位序号 (M20250918XXXX)
- **points**: 正整数，范围 1-999999
- **user_id**: 正整数，必须存在于用户表
- **date字段**: ISO 8601格式 (YYYY-MM-DD)
- **datetime字段**: ISO 8601格式 (YYYY-MM-DDTHH:mm:ssZ)

### 业务规则验证
- 积分使用不能超过当前可用余额
- 等级升级必须满足对应消费门槛
- 积分有效期不能超过系统配置上限
- 会员状态变更需要记录操作日志

## 10. 性能与安全规范

### 响应时间要求
- **查询接口**: 95% < 200ms, 99% < 500ms
- **更新接口**: 95% < 300ms, 99% < 800ms  
- **批量接口**: 95% < 1s, 99% < 3s

### 并发处理能力
- **QPS峰值**: 1000 requests/second
- **并发用户**: 500 concurrent users
- **数据一致性**: 强一致性保证

### 限流策略
- **用户级别**: 100 requests/minute
- **IP级别**: 1000 requests/minute
- **接口级别**: 根据具体接口复杂度设定

### 安全措施
- **认证**: JWT Token必须在每个请求中验证
- **授权**: 基于角色的权限控制
- **数据验证**: 严格的输入参数验证
- **审计日志**: 记录所有关键操作

## 11. 版本管理与变更

### API版本策略
- **版本格式**: v{major}.{minor}
- **向后兼容**: 同一major版本内保证向后兼容
- **废弃流程**: 提前3个月通知，提供迁移指南

### 变更通知机制
- **Breaking Changes**: 提前通知，提供迁移方案
- **新增功能**: 发布说明，示例代码
- **Bug修复**: 修复记录，影响评估

## 12. 相关文档引用

### 设计文档
- [技术设计文档](./design.md) - 第5章 接口设计
- [数据库设计文档](./database-design.md) - 数据模型定义
- [业务需求文档](./requirements.md) - 功能需求追溯

### 标准规范
- [API设计标准](../../../standards/api-standards.md) - 项目API设计规范
- [全局API契约](../../../standards/openapi.yaml) - 统一API契约
- [数据库标准](../../../standards/database-standards.md) - 数据库设计规范

### 实施文档
- [API实施文档](./api-implementation.md) - 具体开发实现记录
- [测试计划文档](./testing-plan.md) - API测试策略

---
📄 **标准遵循**: 严格按照 [A10 api-spec标准](../../../standards/document-management-standards.md) 制作  
🔄 **文档更新**: 2025-10-22 - 更新为符合A10标准的API规范文档
