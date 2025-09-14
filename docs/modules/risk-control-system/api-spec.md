# 风控系统模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/risk-control`
- **认证方式**: Bearer JWT Token + Admin权限
- **内容类型**: application/json

## 交易风控API

### 1. 风险评估
#### POST /api/v1/risk-control/assess
评估交易风险

**请求参数**:
```json
{
  "user_id": 123,
  "order_id": 456,
  "amount": 1000.00,
  "payment_method": "alipay",
  "device_info": {
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "device_id": "DEV123"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "risk_level": "medium",
    "risk_score": 65,
    "action": "manual_review",
    "reasons": ["异常登录地点", "大额交易"]
  }
}
```

### 2. 风险处理
#### POST /api/v1/risk-control/handle
处理风险订单

**请求参数**:
```json
{
  "order_id": 456,
  "action": "approve",
  "reviewer_id": 789,
  "notes": "人工审核通过"
}
```

## 反欺诈API

### 1. 检测虚假订单
#### POST /api/v1/risk-control/fraud-detection
检测订单是否为虚假订单

**请求参数**:
```json
{
  "order_id": 456,
  "user_behavior": {
    "browse_time": 30,
    "click_pattern": "normal",
    "purchase_speed": "fast"
  }
}
```

### 2. 黑名单管理
#### POST /api/v1/risk-control/blacklist
添加黑名单用户

**请求参数**:
```json
{
  "user_id": 123,
  "reason": "恶意刷单",
  "duration_days": 30
}
```

## 支付安全API

### 1. 支付风险检测
#### POST /api/v1/risk-control/payment-security
检测支付安全风险

**请求参数**:
```json
{
  "payment_id": 789,
  "user_id": 123,
  "amount": 500.00,
  "payment_method": "credit_card"
}
```

## 数据安全API

### 1. 敏感数据访问日志
#### GET /api/v1/risk-control/audit-logs
查询敏感数据访问日志

**查询参数**:
- `user_id`: 用户ID
- `resource_type`: 资源类型
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "log_id": 1,
      "user_id": 123,
      "action": "view_user_data",
      "resource": "user_profile",
      "timestamp": "2025-09-13T10:00:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足（需要管理员权限）
- 404: 资源不存在
- 500: 服务器内部错误