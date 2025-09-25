# user-auth - API规范文档

## API端点定义

### 基础信息
- **模块名**: user-auth
- **API前缀**: /api/v1/user-auth/
- **认证**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 端点列表

| 方法 | 路径 | 功能 | 认证要求 | 权限要求 | 状态 |
|------|------|------|----------|----------|------|
| POST | /user-auth/register | 用户注册 | 无 | 公开 | ✅ 已实现 |
| POST | /user-auth/login | 用户登录 | 无 | 公开 | ✅ 已实现 |
| POST | /user-auth/logout | 用户登出 | Bearer Token | 已登录用户 | ✅ 已实现 |
| POST | /user-auth/refresh | 刷新令牌 | Refresh Token | 已登录用户 | ✅ 已实现 |
| POST | /user-auth/password/reset-request | 请求密码重置 | 无 | 公开 | ❌ 待实现 |
| POST | /user-auth/password/reset-confirm | 确认密码重置 | Reset Token | 公开 | ❌ 待实现 |
| PUT | /user-auth/password | 修改密码 | Bearer Token | 已登录用户 | ✅ 已实现 |
| GET | /user-auth/me | 获取用户信息 | Bearer Token | 已登录用户 | ✅ 已实现 |
| PUT | /user-auth/me | 更新用户信息 | Bearer Token | 已登录用户 | ✅ 已实现 |
| GET | /user-auth/users | 用户列表管理 | Bearer Token | 管理员权限 | ✅ 已实现 |
| GET | /user-auth/users/{user_id} | 获取指定用户信息 | Bearer Token | 管理员权限 | ✅ 已实现 |
| PUT | /user-auth/users/{id}/role | 修改用户角色 | Bearer Token | 管理员权限 | ❌ 待实现 |
| GET | /user-auth/health | 健康检查 | 无 | 公开 | ❌ 待实现 |

**注意**: 路径在main.py中自动添加全局前缀`/api/v1`，最终访问路径为`/api/v1/user-auth/register`等

## 详细接口规范

### 1. 用户注册 POST /user-auth/register

#### 请求参数
```json
{
    "username": "string (3-20字符，字母数字下划线)",
    "email": "string (有效邮箱格式)", 
    "password": "string (8-128位，包含大小写字母数字)"
}
```

#### 响应格式
**成功响应 (201 Created)**:
```json
{
    "success": true,
    "code": 201,
    "message": "用户注册成功",
    "data": {
        "user": {
            "id": 123,
            "username": "testuser",
            "email": "user@example.com",
            "role": "user",
            "is_active": true,
            "created_at": "2025-09-25T10:00:00Z"
        },
        "tokens": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900
        }
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "execution_time": 200
    }
}
```

**错误响应 (400 Bad Request)**:
```json
{
    "success": false,
    "code": 400,
    "message": "用户名或邮箱已存在",
    "error": {
        "type": "VALIDATION_ERROR",
        "code": "AUTH_ERROR_005",
        "details": [
            {
                "field": "username",
                "value": "testuser",
                "message": "用户名已存在",
                "constraint": "unique"
            }
        ]
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "error_id": "err_987654321"
    }
}
```

### 2. 用户登录 POST /user-auth/login

#### 请求参数
```json
{
    "username": "string (用户名或邮箱)",
    "password": "string (用户密码)"
}
```

#### 响应格式
**成功响应 (200 OK)**:
```json
{
    "success": true,
    "code": 200,
    "message": "登录成功",
    "data": {
        "user": {
            "id": 123,
            "username": "testuser",
            "email": "user@example.com",
            "role": "user",
            "last_login": "2025-09-25T10:00:00Z"
        },
        "tokens": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900
        }
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "execution_time": 150
    }
}
```

**错误响应 (401 Unauthorized)**:
```json
{
    "success": false,
    "code": 401,
    "message": "用户名或密码错误",
    "error": {
        "type": "AUTHENTICATION_ERROR",
        "code": "AUTH_ERROR_001",
        "details": [
            {
                "field": "credentials",
                "message": "用户名或密码错误",
                "constraint": "authentication"
            }
        ]
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "error_id": "err_987654321"
    }
}
```

### 3. 获取用户信息 GET /api/v1/user-auth/profile

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应格式
**成功响应 (200 OK)**:
```json
{
    "success": true,
    "code": 200,
    "message": "查询成功",
    "data": {
        "user": {
            "id": 123,
            "username": "testuser",
            "email": "user@example.com",
            "role": "user",
            "is_active": true,
            "last_login": "2025-09-25T10:00:00Z",
            "created_at": "2025-09-20T08:00:00Z"
        }
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "execution_time": 50
    }
}
```

### 4. 密码重置请求 POST /api/v1/user-auth/password/reset-request

#### 请求参数
```json
{
    "email": "string (注册邮箱地址)"
}
```

#### 响应格式
**成功响应 (200 OK)**:
```json
{
    "success": true,
    "code": 200,
    "message": "密码重置邮件已发送，请查收",
    "data": {
        "expires_in": 900
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "execution_time": 100
    }
}
```

**错误响应 (404 Not Found)**:
```json
{
    "success": false,
    "code": 404,
    "message": "邮箱地址不存在",
    "error": {
        "type": "RESOURCE_NOT_FOUND",
        "code": "AUTH_ERROR_008",
        "details": [
            {
                "field": "email",
                "value": "notfound@example.com",
                "message": "邮箱地址不存在",
                "constraint": "exists"
            }
        ]
    },
    "metadata": {
        "request_id": "req_123456789",
        "timestamp": "2025-09-25T10:00:00Z",
        "error_id": "err_987654321"
    }
}
}
```

### 5. 密码重置确认 POST /api/v1/user-auth/password/reset-confirm

#### 请求参数
```json
{
    "reset_token": "string (密码重置令牌)",
    "new_password": "string (新密码，8-128位)",
    "confirm_password": "string (确认新密码)"
}
```

#### 响应格式
**成功响应 (200 OK)**:
```json
{
    "success": true,
    "message": "密码重置成功",
    "data": {
        "tokens": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 1800
        }
    }
}
```

### 6. 修改密码 PUT /api/v1/user-auth/password

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
    "current_password": "string (当前密码)",
    "new_password": "string (新密码，8-128位)",
    "confirm_password": "string (确认新密码)"
}
```

#### 响应格式
**成功响应 (200 OK)**:
```json
{
    "success": true,
    "message": "密码修改成功"
}
```

### 5. 管理员-用户列表 GET /api/v1/user-auth/users

#### 请求头
```
Authorization: Bearer <access_token> (需要管理员权限)
```

#### 查询参数
```
?page=1&size=20&role=user&is_active=true&search=username
```

#### 响应格式
**成功响应 (200 OK)**:
```json
{
    "success": true,
    "data": {
        "users": [
            {
                "id": 123,
                "username": "testuser",
                "email": "user@example.com",
                "role": "user",
                "is_active": true,
                "last_login": "2025-09-25T10:00:00Z",
                "created_at": "2025-09-20T08:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "size": 20,
            "total": 100,
            "pages": 5
        }
    }
}
```

## 统一错误码定义

| 错误码 | HTTP状态码 | 错误描述 | 处理建议 |
|--------|-----------|---------|---------|
| AUTH_ERROR_001 | 401 | 用户名或密码错误 | 检查登录凭据 |
| AUTH_ERROR_002 | 401 | 令牌无效或过期 | 刷新令牌或重新登录 |
| AUTH_ERROR_003 | 403 | 权限不足 | 联系管理员获取权限 |
| AUTH_ERROR_004 | 423 | 账户被锁定 | 等待解锁或联系管理员 |
| AUTH_ERROR_005 | 400 | 用户名或邮箱已存在 | 使用其他用户名或邮箱 |
| AUTH_ERROR_006 | 400 | 密码格式不符合要求 | 参考密码规则重新设置 |
| AUTH_ERROR_007 | 400 | 必填字段缺失 | 检查请求参数完整性 |
| AUTH_ERROR_008 | 404 | 邮箱地址不存在 | 检查邮箱地址或先注册 |
| AUTH_ERROR_009 | 400 | 重置令牌无效或过期 | 重新申请密码重置 |
| AUTH_ERROR_010 | 429 | 请求过于频繁 | 稍后再试或联系支持 |
| AUTH_ERROR_003 | 403 | 权限不足 | 联系管理员获取权限 |
| AUTH_ERROR_004 | 423 | 账户被锁定 | 等待解锁或联系管理员 |
| AUTH_ERROR_005 | 400 | 用户名或邮箱已存在 | 使用其他用户名或邮箱 |
| AUTH_ERROR_006 | 400 | 密码格式不符合要求 | 参考密码规则重新设置 |
| AUTH_ERROR_007 | 400 | 必填字段缺失 | 检查请求参数完整性 |

## 数据验证规则

### 用户名验证
- 长度：3-20个字符
- 格式：字母、数字、下划线组合
- 唯一性：系统内唯一

### 邮箱验证
- 格式：符合RFC 5322标准
- 唯一性：系统内唯一
- 示例：user@example.com

### 密码验证
- 长度：8-128个字符
- 复杂度：必须包含大小写字母和数字
- 建议：包含特殊符号增强安全性

## 认证流程说明

### Bearer Token认证
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 令牌刷新机制
1. 访问令牌过期时，客户端收到401响应
2. 使用refresh_token调用/refresh端点
3. 获得新的access_token和refresh_token
4. 重新发起原始请求

### 权限检查流程
1. 验证Bearer Token有效性
2. 解析Token获取用户信息
3. 检查用户状态(is_active)
4. 验证用户角色权限
5. 允许或拒绝请求

详细API规范请参考 [standards/openapi.yaml](../../standards/openapi.yaml)
