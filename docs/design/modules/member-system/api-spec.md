# 会员系统模块 - API规范文档

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-18  
👤 **负责人**: API架构师  
🔄 **最后更新**: 2025-09-18  
📋 **版本**: v1.0.0  

## API规范概述

本文档定义会员系统模块的API接口规范，遵循项目的OpenAPI契约标准，确保接口的一致性、可维护性和互操作性。

## 📋 规范遵循

### 全局API契约
- **契约文件**: [docs/standards/openapi.yaml](../../../docs/standards/openapi.yaml)
- **API前缀**: `/api/v1/member-system`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON (Content-Type: application/json)
- **字符编码**: UTF-8

### HTTP状态码规范
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

### 错误响应格式
```json
{
  "error": {
    "code": "MEMBER_NOT_FOUND",
    "message": "会员信息不存在",
    "details": {
      "user_id": 12345,
      "timestamp": "2025-09-18T10:30:00Z"
    }
  }
}
```

## 🔐 认证和授权规范

### JWT Token要求
- **Header**: `Authorization: Bearer <token>`
- **Token有效期**: 24小时
- **刷新机制**: 通过refresh_token刷新
- **权限范围**: 基于用户角色的接口访问控制

### 权限级别定义
| 权限级别 | 说明 | 可访问接口 |
|----------|------|-----------|
| `member` | 普通会员 | 个人信息查询、积分查询使用 |
| `admin` | 管理员 | 所有会员数据查询和管理 |
| `system` | 系统服务 | 内部服务调用接口 |

## 📊 会员信息管理API

### GET /api/v1/member-system/profile
**功能**: 获取当前用户会员信息
**权限**: member, admin
**参数**: 无 (从JWT token中获取user_id)

**响应示例**:
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

### PUT /api/v1/member-system/profile
**功能**: 更新会员个人信息
**权限**: member, admin
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

**响应**: 200 OK + 更新后的会员信息

### GET /api/v1/member-system/members/{member_id}
**功能**: 管理员获取指定会员信息
**权限**: admin
**参数**: 
- `member_id` (path): 会员ID

**响应**: 与 GET /profile 相同格式

## 💰 积分管理API

### GET /api/v1/member-system/points/balance
**功能**: 获取当前用户积分余额
**权限**: member, admin

**响应示例**:
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

### POST /api/v1/member-system/points/earn
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

**响应示例**:
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

### POST /api/v1/member-system/points/use
**功能**: 积分使用接口
**权限**: member, admin, system
**请求体**:
```json
{
  "points": 500,
  "usage_type": "order_discount",
  "reference_id": "ORDER_2025091800002",
  "description": "订单积分抵扣"
}
```

**响应**: 与earn接口类似的交易确认信息

### GET /api/v1/member-system/points/transactions
**功能**: 获取积分变动历史
**权限**: member, admin
**查询参数**:
- `page` (query, optional): 页码，默认1
- `limit` (query, optional): 每页数量，默认20
- `type` (query, optional): 交易类型过滤
- `start_date` (query, optional): 开始日期
- `end_date` (query, optional): 结束日期

**响应示例**:
```json
{
  "data": {
    "transactions": [
      {
        "id": 98765,
        "type": "earn",
        "points_change": 100,
        "description": "订单完成奖励",
        "created_at": "2025-09-18T10:30:00Z",
        "reference_type": "order",
        "reference_id": "ORDER_2025091800001"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 156,
      "total_pages": 8
    }
  }
}
```

## 🏆 等级管理API

### GET /api/v1/member-system/levels
**功能**: 获取会员等级列表
**权限**: public (无需认证)

**响应示例**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "铜牌会员",
      "min_points": 0,
      "discount_rate": 1.000,
      "benefits": ["基础客服", "生日祝福"]
    },
    {
      "id": 2,
      "name": "银牌会员", 
      "min_points": 1000,
      "discount_rate": 0.950,
      "benefits": ["优先客服", "生日折扣", "免邮特权"]
    }
  ]
}
```

### POST /api/v1/member-system/levels/{member_id}/upgrade
**功能**: 手动升级会员等级
**权限**: admin
**参数**:
- `member_id` (path): 会员ID
**请求体**:
```json
{
  "target_level_id": 3,
  "reason": "VIP客户特殊升级"
}
```

**响应**: 200 OK + 升级结果信息

## 📈 统计分析API

### GET /api/v1/member-system/stats/summary
**功能**: 获取会员系统统计概览
**权限**: admin
**响应示例**:
```json
{
  "data": {
    "total_members": 12580,
    "active_members_30d": 8940,
    "level_distribution": {
      "level_1": 7500,
      "level_2": 3200,
      "level_3": 1300,
      "level_4": 580
    },
    "points_statistics": {
      "total_points_issued": 15680000,
      "total_points_used": 8940000,
      "avg_points_per_member": 1245
    }
  }
}
```

## 🔧 系统管理API

### POST /api/v1/member-system/admin/recalculate/{member_id}
**功能**: 重新计算会员积分和等级
**权限**: admin
**请求体**:
```json
{
  "recalculate_points": true,
  "recalculate_level": true,
  "reason": "数据修复"
}
```

### GET /api/v1/member-system/health
**功能**: 系统健康检查
**权限**: public
**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-18T10:30:00Z",
  "database": "connected",
  "cache": "connected"
}
```

## 📋 数据验证规范

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

## 🚨 错误码定义

### 业务错误码
| 错误码 | 说明 | HTTP状态码 |
|--------|------|-----------|
| `MEMBER_NOT_FOUND` | 会员信息不存在 | 404 |
| `INSUFFICIENT_POINTS` | 积分余额不足 | 409 |
| `INVALID_LEVEL_UPGRADE` | 无效的等级升级操作 | 409 |
| `MEMBER_STATUS_INVALID` | 会员状态异常 | 409 |
| `POINTS_EXPIRED` | 积分已过期 | 409 |
| `DUPLICATE_MEMBER_CODE` | 会员编号重复 | 409 |

### 系统错误码
| 错误码 | 说明 | HTTP状态码 |
|--------|------|-----------|
| `INVALID_REQUEST_FORMAT` | 请求格式错误 | 400 |
| `AUTHENTICATION_REQUIRED` | 需要身份认证 | 401 |
| `PERMISSION_DENIED` | 权限不足 | 403 |
| `RATE_LIMIT_EXCEEDED` | 访问频率超限 | 429 |
| `INTERNAL_SERVER_ERROR` | 服务器内部错误 | 500 |

## 📊 性能规范

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

## 🔄 版本管理

### API版本策略
- **版本格式**: v{major}.{minor}
- **向后兼容**: 同一major版本内保证向后兼容
- **废弃流程**: 提前3个月通知，提供迁移指南

### 变更通知
- **Breaking Changes**: 提前通知，提供迁移方案
- **新增功能**: 发布说明，示例代码
- **Bug修复**: 修复记录，影响评估

## 相关文档

- [全局API契约](../../../docs/standards/openapi.yaml) - 项目统一API规范
- [API实施文档](./api-implementation.md) - 具体的开发实现记录
- [数据库设计文档](./database-design.md) - 数据模型定义
- [测试计划文档](./testing-plan.md) - API测试策略

---
📄 **规范遵循**: 严格按照 [openapi.yaml](../../../docs/standards/openapi.yaml) 契约标准制作  
🔄 **文档更新**: 2025-09-18 - 创建符合标准的API规范文档