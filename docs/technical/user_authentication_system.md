# 用户认证系统技术文档

**版本**: 1.0.0  
**创建日期**: 2025-09-09  
**最后更新**: 2025-09-09  

## 概述

用户认证系统实现了完整的 JWT 基础认证功能，包括用户注册、登录、身份验证和会话管理，为电商平台提供安全的用户访问控制。

## 技术栈

### 核心依赖
- **JWT 库**: PyJWT 2.8.0
- **密码加密**: passlib[bcrypt] 1.7.4  
- **HTTP 认证**: FastAPI HTTPBearer
- **数据验证**: Pydantic 2.x

### 库选择说明
选择 **PyJWT** 而不是 python-jose 的原因：
- 更轻量级，专注 JWT 功能
- 官方维护，更新及时
- 性能更优
- 依赖更少，减少潜在安全风险

## 架构设计

### 模块结构
```
app/
├── auth.py              # JWT 认证工具模块
├── api/
│   ├── user_routes.py   # 用户认证 API 路由
│   └── schemas.py       # Pydantic 数据模型
├── models.py            # 数据库模型
└── database.py          # 数据库连接
```

### 数据库模型

#### User 模型
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # 新增
    is_active = Column(Boolean, default=True)            # 新增
    
    # 微信集成字段（预留）
    wx_openid = Column(String(100), unique=True, nullable=True)
    wx_unionid = Column(String(100), unique=True, nullable=True)
    
    # 基础信息
    phone = Column(String(20), nullable=True)
    real_name = Column(String(100), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### JWT 配置

#### 令牌参数
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
```

#### 令牌结构
```json
{
  "sub": "31",              # 用户ID（字符串格式）
  "type": "access",         # 令牌类型
  "exp": 1725872563,        # 过期时间
  "iat": 1725872263         # 签发时间
}
```

## API 接口

### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "phone": "13800138000",    # 可选
  "real_name": "string"      # 可选
}
```

**响应**:
```json
{
  "id": 31,
  "username": "testuser",
  "email": "test@example.com",
  "phone": null,
  "real_name": null,
  "is_active": true,
  "wx_openid": null,
  "created_at": "2025-09-09T05:42:43"
}
```

### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",   # 可以是用户名或邮箱
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. 获取当前用户信息
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": 31,
  "username": "testuser",
  "email": "test@example.com",
  "phone": null,
  "real_name": null,
  "is_active": true,
  "wx_openid": null,
  "created_at": "2025-09-09T05:42:43"
}
```

### 4. 令牌刷新
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 安全特性

### 密码安全
- 使用 bcrypt 进行密码哈希
- 自动 salt 生成
- 密码明文不存储、不传输、不日志

### JWT 安全
- HS256 算法签名
- 访问令牌短期有效（30分钟）
- 刷新令牌长期有效（30天）
- 令牌类型验证（access/refresh）

### 输入验证
- Pydantic 2.x 数据验证
- 邮箱格式验证：`^[^\s@]+@[^\s@]+\.[^\s@]+$`
- 手机号验证（中国）：`^1[3-9]\d{9}$`
- 用户名长度：3-50字符
- 密码长度：6-128字符

### 认证中间件
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    # JWT 验证、用户查找、状态检查
```

## 数据库迁移

### 迁移文件
```
alembic/versions/339c8f4aa8cf_add_user_authentication_fields.py
```

### 变更内容
- 添加 `password_hash` 字段（VARCHAR(255), NOT NULL）
- 添加 `is_active` 字段（BOOLEAN, DEFAULT TRUE）

### 执行命令
```bash
alembic upgrade head
```

## 配置和环境变量

### 必需环境变量
```env
JWT_SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=mysql+pymysql://root:123456@localhost:3307/ecommerce_platform
```

### 可选配置
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 访问令牌有效期
REFRESH_TOKEN_EXPIRE_DAYS = 30      # 刷新令牌有效期
```

## 错误处理

### 认证错误
```python
class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 常见错误场景
- 令牌过期：`Token has expired`
- 令牌无效：`Invalid token`
- 用户不存在：`User not found`
- 用户已禁用：`User account is disabled`
- 密码错误：`Incorrect username or password`

## 测试用例

### 功能测试
```powershell
# 用户注册
$body = @{username="testuser"; email="test@example.com"; password="password123"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" -Method POST -Body $body -ContentType "application/json"

# 用户登录
$loginBody = @{username="testuser"; password="password123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"

# 获取用户信息
$headers = @{Authorization="Bearer $($response.access_token)"}
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Method GET -Headers $headers
```

### 预期结果
- 注册成功返回用户信息
- 登录成功返回 JWT 令牌
- 认证成功获取用户详情

## 已知问题和解决方案

### 1. Pydantic 2.x 兼容性
**问题**: `regex` 参数不再支持  
**解决**: 使用 `pattern` 参数替代

### 2. JWT Subject 类型
**问题**: Subject 必须是字符串  
**解决**: 用户ID转换为字符串 `str(user.id)`

### 3. Alembic 自动生成
**问题**: 模板文件损坏导致生成失败  
**解决**: 修复 `script.py.mako` 模板和 `alembic.ini` 配置

## 扩展计划

### 短期扩展
- 密码重置功能
- 邮箱验证
- 账户锁定机制

### 中期扩展
- 微信小程序登录集成
- 多因素认证（MFA）
- 社交登录集成

### 长期扩展
- OAuth2 服务器
- 单点登录（SSO）
- 联邦认证

## 维护注意事项

1. **密钥管理**: 生产环境必须使用强随机密钥
2. **令牌有效期**: 根据安全需求调整令牌生命周期
3. **日志记录**: 避免记录敏感信息（密码、令牌）
4. **定期更新**: 保持依赖库最新版本
5. **监控告警**: 异常登录行为监控

---

**文档维护**: 此文档应随代码变更同步更新  
**审核周期**: 每月技术评审更新
