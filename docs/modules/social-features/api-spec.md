# 社交功能模块API规范

📝 **状态**: 草稿  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/social`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 分享机制API

### 1. 生成分享链接
#### POST /api/v1/social/share
生成商品分享链接

**请求参数**:
```json
{
  "product_id": 123,
  "user_id": 456,
  "share_type": "wechat"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "share_url": "https://domain.com/share/ABC123",
    "share_code": "ABC123",
    "reward_points": 10
  }
}
```

### 2. 分享回调
#### POST /api/v1/social/share/callback
分享成功回调

**请求参数**:
```json
{
  "share_code": "ABC123",
  "action": "shared"
}
```

## 拼团功能API

### 1. 发起拼团
#### POST /api/v1/social/group-buying
发起拼团活动

**请求参数**:
```json
{
  "product_id": 123,
  "group_size": 5,
  "initiator_id": 456,
  "expire_hours": 24
}
```

### 2. 加入拼团
#### POST /api/v1/social/group-buying/{group_id}/join
加入拼团

**请求参数**:
```json
{
  "user_id": 789,
  "quantity": 1
}
```

## 推荐奖励API

### 1. 生成邀请码
#### POST /api/v1/social/invitation
生成用户邀请码

**请求参数**:
```json
{
  "user_id": 123
}
```

### 2. 使用邀请码
#### POST /api/v1/social/invitation/use
新用户使用邀请码注册

**请求参数**:
```json
{
  "invitation_code": "INV123",
  "new_user_id": 789
}
```

## 状态码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未授权
- 404: 资源不存在
- 409: 拼团已满/已过期
- 500: 服务器内部错误