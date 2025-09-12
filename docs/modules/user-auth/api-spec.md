<!--
文档说明：
- 内容：用户认证模块API接口详细规范
- 使用方法：API开发和对接时的标准参考
- 更新方法：API变更时同步更新，保持与代码一致
- 引用关系：基于requirements.md，被implementation.md引用
- 更新频率：API接口变更时
-->

# 用户认证模块API规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-12  
👤 **负责人**: AI开发团队  
🔄 **最后更新**: 2025-09-12  
📋 **版本**: v1.0.0  

## API设计原则

基于[API设计标准](../../standards/api-standards.md)，遵循RESTful设计风格。

### 基础路径
- **Base URL**: `/api/v1/users`
- **认证方式**: Bearer JWT Token
- **内容类型**: application/json

## 认证相关API

### 1. 用户注册

#### POST /api/v1/users/register
用户注册接口

**请求参数**:
```json
{
  "username": "string",           // 必填，3-20字符
  "email": "string",              // 必填，有效邮箱格式
  "password": "string",           // 必填，8-20字符
  "phone": "string",              // 可选，手机号格式
  "verification_code": "string"   // 必填，验证码
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 123,
      "username": "testuser",
      "email": "test@example.com",
      "phone": "13800138000",
      "role": "user",
      "is_active": true,
      "created_at": "2025-09-12T10:00:00Z"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "Bearer",
      "expires_in": 7200
    }
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "用户名已存在",
  "error_code": "USERNAME_EXISTS",
  "data": null
}
```

**状态码**:
- `201`: 注册成功
- `400`: 参数错误
- `409`: 用户已存在
- `422`: 验证失败

### 2. 用户登录

#### POST /api/v1/users/login
用户登录接口

**请求参数**:
```json
{
  "username": "string",    // 用户名/邮箱/手机号
  "password": "string"     // 密码
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 123,
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "is_active": true,
      "last_login": "2025-09-12T10:00:00Z"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "Bearer",
      "expires_in": 7200
    }
  }
}
```

**状态码**:
- `200`: 登录成功
- `401`: 认证失败
- `423`: 账户被锁定

### 3. Token刷新

#### POST /api/v1/users/refresh
刷新访问令牌

**请求头**:
```
Authorization: Bearer {refresh_token}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 7200
  }
}
```

### 4. 用户登出

#### POST /api/v1/users/logout
用户登出接口

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登出成功",
  "data": null
}
```

## 用户信息API

### 5. 获取当前用户信息

#### GET /api/v1/users/me
获取当前登录用户信息

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "real_name": "张三",
    "role": "user",
    "is_active": true,
    "wx_openid": "o1234567890",
    "created_at": "2025-09-01T10:00:00Z",
    "updated_at": "2025-09-12T10:00:00Z",
    "last_login": "2025-09-12T10:00:00Z"
  }
}
```

### 6. 更新用户信息

#### PUT /api/v1/users/me
更新当前用户信息

**请求参数**:
```json
{
  "real_name": "string",      // 可选，真实姓名
  "phone": "string"           // 可选，手机号
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "更新成功",
  "data": {
    "id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138001",
    "real_name": "李四",
    "updated_at": "2025-09-12T10:05:00Z"
  }
}
```

### 7. 修改密码

#### PUT /api/v1/users/password
修改用户密码

**请求参数**:
```json
{
  "old_password": "string",    // 必填，原密码
  "new_password": "string"     // 必填，新密码
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "密码修改成功",
  "data": null
}
```

## 验证码API

### 8. 发送验证码

#### POST /api/v1/users/verification-code
发送手机/邮箱验证码

**请求参数**:
```json
{
  "contact": "string",      // 必填，手机号或邮箱
  "type": "string"          // 必填，register|login|reset_password
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "验证码发送成功",
  "data": {
    "expires_in": 300,
    "next_request_in": 60
  }
}
```

## 权限验证API

### 9. 验证用户权限

#### GET /api/v1/users/permissions
获取当前用户权限列表

**响应示例**:
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "role": "user",
    "permissions": [
      "product:read",
      "order:create",
      "order:read",
      "cart:manage"
    ]
  }
}
```

## 错误代码表

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| USERNAME_EXISTS | 409 | 用户名已存在 |
| EMAIL_EXISTS | 409 | 邮箱已存在 |
| PHONE_EXISTS | 409 | 手机号已存在 |
| INVALID_CREDENTIALS | 401 | 用户名或密码错误 |
| ACCOUNT_LOCKED | 423 | 账户已被锁定 |
| ACCOUNT_DISABLED | 403 | 账户已被禁用 |
| TOKEN_EXPIRED | 401 | Token已过期 |
| TOKEN_INVALID | 401 | Token无效 |
| PERMISSION_DENIED | 403 | 权限不足 |
| VERIFICATION_CODE_INVALID | 400 | 验证码无效 |
| VERIFICATION_CODE_EXPIRED | 400 | 验证码已过期 |
| PASSWORD_TOO_WEAK | 400 | 密码强度不足 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |

## 请求/响应示例

### 完整注册流程示例

1. **发送验证码**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/verification-code" \
  -H "Content-Type: application/json" \
  -d '{
    "contact": "test@example.com",
    "type": "register"
  }'
```

2. **用户注册**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "verification_code": "123456"
  }'
```

### 完整登录流程示例

1. **用户登录**:
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

2. **访问受保护资源**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## 安全考虑

### 1. 认证安全
- 密码使用bcrypt加密存储
- JWT Token包含过期时间和签名
- Refresh Token单独存储和验证

### 2. 传输安全
- 所有API强制使用HTTPS
- 敏感信息不在URL中传递
- 请求响应都包含安全头

### 3. 防护措施
- 登录失败次数限制
- 验证码发送频率限制
- Token黑名单机制
- IP访问频率限制