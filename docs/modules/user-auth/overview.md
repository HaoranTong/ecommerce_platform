# 用户认证模块 (User Authentication Module)

## 模块概述

用户认证模块是平台的核心安全模块，负责处理用户注册、登录、权限管理和会话控制。

### 主要职责

1. **用户身份验证**
   - 多因素认证支持
   - OAuth2/OIDC集成
   - JWT令牌管理
   - 生物识别认证

2. **权限管理**
   - 基于角色的访问控制 (RBAC)
   - 细粒度权限控制
   - 动态权限分配
   - 权限继承机制

3. **会话管理**
   - 分布式会话存储
   - 会话超时控制
   - 并发会话限制
   - 会话安全策略

## 技术架构

### 核心组件

```
user_auth/
├── router.py           # API路由定义
├── service.py          # 认证业务逻辑
├── models.py           # 用户数据模型(User, Role, Permission)
├── schemas.py          # 请求/响应数据模型
├── dependencies.py     # 模块依赖注入
└── utils.py            # 认证工具函数(JWT, 密码加密)
```

### 核心基础设施
```
app/core/
├── auth.py             # 认证中间件和JWT服务
├── database.py         # 数据库连接管理
└── redis_client.py     # 会话存储和缓存
```

### 数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE
);

-- 角色表
CREATE TABLE roles (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    level INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 权限表
CREATE TABLE permissions (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户角色关联表
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by INTEGER REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by INTEGER REFERENCES users(id),
    PRIMARY KEY (role_id, permission_id)
);

-- 会话表
CREATE TABLE sessions (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
```

## API 接口

### 认证接口

```yaml
/api/v1/auth:
  POST /register:
    summary: 用户注册
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
              password:
                type: string
                minLength: 8
              phone:
                type: string
                pattern: "^\\+?[1-9]\\d{1,14}$"
              name:
                type: string
                maxLength: 100
    responses:
      201:
        description: 注册成功
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
                  format: uuid
                message:
                  type: string
      400:
        description: 请求参数错误
      409:
        description: 用户已存在

  POST /login:
    summary: 用户登录
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
              password:
                type: string
              mfa_code:
                type: string
                description: 多因素认证代码
    responses:
      200:
        description: 登录成功
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
                expires_in:
                  type: integer
                user:
                  $ref: '#/components/schemas/User'
      401:
        description: 认证失败
      423:
        description: 账户被锁定

  POST /logout:
    summary: 用户登出
    security:
      - BearerAuth: []
    responses:
      200:
        description: 登出成功

  POST /refresh:
    summary: 刷新令牌
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              refresh_token:
                type: string
    responses:
      200:
        description: 令牌刷新成功
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                expires_in:
                  type: integer
```

## 安全策略

### 密码策略

1. **密码复杂度要求**
   - 最少8个字符
   - 包含大小写字母
   - 包含数字和特殊字符
   - 不能使用常见密码

2. **密码存储**
   - 使用bcrypt加密
   - 盐值长度12位
   - 成本因子12

3. **密码重置**
   - 邮箱验证机制
   - 重置链接有效期30分钟
   - 限制重置频率

### 多因素认证

1. **支持方式**
   - TOTP (Google Authenticator)
   - SMS验证码
   - 邮箱验证码
   - 生物识别

2. **实施策略**
   - 高风险操作强制MFA
   - 新设备登录要求MFA
   - 管理员账户强制MFA

### 会话安全

1. **令牌管理**
   - JWT访问令牌 (15分钟有效期)
   - 刷新令牌 (7天有效期)
   - 令牌黑名单机制

2. **会话监控**
   - 异常登录检测
   - 地理位置验证
   - 设备指纹识别

## 监控指标

### 业务指标

- 日活跃用户数 (DAU)
- 注册转化率
- 登录成功率
- MFA启用率

### 技术指标

- 认证响应时间
- 令牌刷新频率
- 失败登录次数
- 会话超时率

### 安全指标

- 暴力破解尝试
- 异常登录检测
- 权限违规次数
- 账户锁定率

## 部署要求

### 环境变量

```bash
# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 数据库配置
AUTH_DB_URL=postgresql://user:pass@localhost/auth_db

# Redis配置 (会话存储)
REDIS_URL=redis://localhost:6379/0

# 邮件配置
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=your-password

# 短信配置
SMS_PROVIDER=twilio
SMS_API_KEY=your-api-key
SMS_API_SECRET=your-api-secret
```

### 依赖服务

- PostgreSQL (用户数据存储)
- Redis (会话缓存)
- SMTP服务 (邮件发送)
- SMS网关 (短信发送)

## 测试策略

### 单元测试

- 认证逻辑测试
- 权限验证测试
- 密码加密测试
- JWT令牌测试

### 集成测试

- API接口测试
- 数据库集成测试
- 缓存集成测试
- 外部服务集成测试

### 安全测试

- 暴力破解测试
- SQL注入测试
- XSS攻击测试
- CSRF攻击测试

## 相关文档

- [API标准规范](../architecture/api-standards.md)
- [数据模型规范](../architecture/data-models.md)
- [安全架构](../architecture/security.md)
- [监控告警](../operations/monitoring.md)
