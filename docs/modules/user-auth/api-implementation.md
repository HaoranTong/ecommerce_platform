# 用户API路由模块 (User API Routes Module)

## 模块概述

用户API路由模块 (`app/api/user_routes.py`) 是电商平台用户管理的REST API接口层，提供用户注册、登录、信息管理、密码管理等完整的用户生命周期管理功能，集成JWT认证和权限控制。

### 主要功能

1. **用户注册认证**
   - 用户注册接口
   - 用户登录验证
   - 令牌刷新机制
   - 安全登出功能

2. **用户信息管理**
   - 获取用户资料
   - 更新用户信息
   - 用户状态管理
   - 密码修改功能

3. **管理员功能**
   - 用户列表查询
   - 用户详情获取
   - 用户状态控制
   - 权限管理基础

4. **安全控制**
   - JWT令牌验证
   - 权限检查机制
   - 数据验证和清理
   - 错误处理和日志

## 技术架构

### API架构图

```mermaid
graph TB
    C[Client] --> R[User Routes]
    R --> A[Auth Module]
    R --> S[Schemas]
    R --> D[Database]
    
    A --> J[JWT Service]
    A --> P[Password Hash]
    S --> V[Data Validation]
    D --> M[User Model]
    
    R --> E1[/api/auth/register]
    R --> E2[/api/auth/login]
    R --> E3[/api/auth/refresh]
    R --> E4[/api/auth/me]
    R --> E5[/api/auth/logout]
    R --> E6[/api/auth/change-password]
    R --> E7[/api/auth/users]
```

### 认证流程

```mermaid
sequenceDiagram
    participant C as Client
    participant R as User Routes
    participant A as Auth Module
    participant D as Database
    
    Note over C,D: 用户注册流程
    C->>R: POST /api/auth/register
    R->>D: 检查用户名/邮箱
    R->>A: 密码哈希
    R->>D: 创建用户
    R-->>C: 返回用户信息
    
    Note over C,D: 用户登录流程
    C->>R: POST /api/auth/login
    R->>A: 验证用户凭据
    A->>D: 查询用户
    A->>A: 验证密码
    A->>A: 生成JWT令牌
    R-->>C: 返回令牌
    
    Note over C,D: 访问保护资源
    C->>R: GET /api/auth/me (with JWT)
    R->>A: 验证令牌
    A->>D: 查询用户
    R-->>C: 返回用户信息
```

## 代码结构

### 文件组织

```
app/api/user_routes.py
├── 导入依赖
├── 路由器创建
├── 注册登录接口
├── 用户信息接口
├── 密码管理接口
├── 管理员接口
└── 辅助函数
```

### 路由分组

#### 1. 认证相关路由
- `/api/auth/register` - 用户注册
- `/api/auth/login` - 用户登录
- `/api/auth/refresh` - 令牌刷新
- `/api/auth/logout` - 用户登出

#### 2. 用户资料路由
- `/api/auth/me` - 获取/更新当前用户信息
- `/api/auth/change-password` - 修改密码

#### 3. 管理员路由
- `/api/auth/users` - 用户列表
- `/api/auth/users/{user_id}` - 用户详情

## API接口文档

### 1. 用户注册

**接口**: `POST /api/auth/register`

**请求体**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123",
  "real_name": "John Doe",
  "phone": "13800138000"
}
```

**响应体**:
```json
{
  "id": 1001,
  "username": "john_doe",
  "email": "john@example.com",
  "real_name": "John Doe",
  "phone": "13800138000",
  "is_active": true,
  "role": "user",
  "created_at": "2025-09-11T10:00:00",
  "updated_at": "2025-09-11T10:00:00"
}
```

**状态码**:
- `201`: 注册成功
- `400`: 用户名或邮箱已存在
- `422`: 数据验证失败

### 2. 用户登录

**接口**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "john_doe",  // 支持用户名或邮箱
  "password": "secure_password_123"
}
```

**响应体**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1001,
    "username": "john_doe",
    "email": "john@example.com",
    "real_name": "John Doe"
  }
}
```

**状态码**:
- `200`: 登录成功
- `400`: 用户名或密码错误
- `401`: 用户账户被禁用

### 3. 令牌刷新

**接口**: `POST /api/auth/refresh`

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应体**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**状态码**:
- `200`: 刷新成功
- `400`: 刷新令牌无效或过期

### 4. 获取当前用户信息

**接口**: `GET /api/auth/me`

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应体**:
```json
{
  "id": 1001,
  "username": "john_doe",
  "email": "john@example.com",
  "real_name": "John Doe",
  "phone": "13800138000",
  "is_active": true,
  "role": "user",
  "created_at": "2025-09-11T10:00:00",
  "updated_at": "2025-09-11T10:00:00"
}
```

**状态码**:
- `200`: 获取成功
- `401`: 未认证或令牌无效

### 5. 更新用户信息

**接口**: `PUT /api/auth/me`

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**请求体**:
```json
{
  "real_name": "John Smith",
  "phone": "13900139000"
}
```

**响应体**:
```json
{
  "id": 1001,
  "username": "john_doe",
  "email": "john@example.com",
  "real_name": "John Smith",
  "phone": "13900139000",
  "is_active": true,
  "role": "user",
  "created_at": "2025-09-11T10:00:00",
  "updated_at": "2025-09-11T10:30:00"
}
```

**状态码**:
- `200`: 更新成功
- `401`: 未认证
- `422`: 数据验证失败

### 6. 修改密码

**接口**: `POST /api/auth/change-password`

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**请求体**:
```json
{
  "old_password": "old_secure_password",
  "new_password": "new_secure_password_456"
}
```

**响应体**:
```json
{
  "message": "密码修改成功"
}
```

**状态码**:
- `200`: 修改成功
- `400`: 旧密码错误
- `401`: 未认证
- `422`: 新密码不符合要求

### 7. 用户登出

**接口**: `POST /api/auth/logout`

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应体**:
```json
{
  "message": "登出成功"
}
```

**状态码**:
- `200`: 登出成功
- `401`: 未认证

### 8. 用户列表 (管理员)

**接口**: `GET /api/auth/users`

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**查询参数**:
- `skip`: 跳过记录数 (默认: 0)
- `limit`: 返回记录数 (默认: 100)
- `search`: 搜索关键词

**响应体**:
```json
[
  {
    "id": 1001,
    "username": "john_doe",
    "email": "john@example.com",
    "real_name": "John Doe",
    "is_active": true,
    "role": "user",
    "created_at": "2025-09-11T10:00:00"
  },
  {
    "id": 1002,
    "username": "jane_smith",
    "email": "jane@example.com",
    "real_name": "Jane Smith",
    "is_active": true,
    "role": "admin",
    "created_at": "2025-09-11T11:00:00"
  }
]
```

**状态码**:
- `200`: 查询成功
- `401`: 未认证
- `403`: 权限不足

### 9. 用户详情 (管理员)

**接口**: `GET /api/auth/users/{user_id}`

**路径参数**:
- `user_id`: 用户ID

**请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应体**:
```json
{
  "id": 1001,
  "username": "john_doe",
  "email": "john@example.com",
  "real_name": "John Doe",
  "phone": "13800138000",
  "is_active": true,
  "role": "user",
  "wx_openid": null,
  "wx_unionid": null,
  "created_at": "2025-09-11T10:00:00",
  "updated_at": "2025-09-11T10:00:00"
}
```

**状态码**:
- `200`: 查询成功
- `401`: 未认证
- `403`: 权限不足
- `404`: 用户不存在

## 权限体系实现

### 角色定义

本模块实现基于角色的权限控制（RBAC），通过User模型的`role`字段定义用户权限级别：

#### 角色类型
- **`user`** - 普通用户 (默认)
  - 只能访问和操作自己的数据
  - 可以查看和修改个人信息
  - 可以创建和管理自己的订单、购物车等

- **`admin`** - 管理员
  - 拥有所有普通用户权限
  - 可以查看和管理所有用户的订单
  - 可以管理商品目录（增删改查）
  - 可以查看用户列表和详情

- **`super_admin`** - 超级管理员
  - 拥有所有管理员权限  
  - 可以管理用户角色（提升/降级权限）
  - 可以访问系统级管理功能
  - 拥有最高权限

### 权限检查机制

#### 认证依赖函数

```python
# 基础用户认证 - 验证token有效性
def get_current_active_user(token: str = Depends(oauth2_scheme)):
    """验证并返回当前活跃用户，适用于需要用户登录的操作"""
    
# 管理员权限认证 - 验证管理员角色
def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    """验证当前用户是否为管理员，用于管理功能"""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(403, "需要管理员权限")
    return current_user

# 所有权验证 - 检查资源所有权
def require_ownership(resource_user_id: int, current_user: User) -> bool:
    """检查用户是否有权访问特定资源"""
    # 管理员可以访问所有资源
    if current_user.role in ['admin', 'super_admin']:
        return True
    # 普通用户只能访问自己的资源
    return resource_user_id == current_user.id
```

#### 权限验证流程

```mermaid
graph TD
    A[API请求] --> B[Token验证]
    B --> C{Token有效?}
    C -->|否| D[返回401]
    C -->|是| E[获取用户信息]
    E --> F{需要管理员权限?}
    F -->|是| G{用户是管理员?}
    F -->|否| H[检查资源所有权]
    G -->|否| I[返回403]
    G -->|是| J[允许访问]
    H --> K{拥有资源?}
    K -->|否| I
    K -->|是| J
```

### 数据模型中的角色字段

在User模型中，role字段的实现细节：

```python
class User(SQLAlchemyBase):
    # ... 其他字段
    role: Mapped[str] = mapped_column(
        String(20), 
        default="user",  # 默认为普通用户
        nullable=False
    )
    
    # 角色验证约束
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin', 'super_admin')",
            name='valid_role_check'
        ),
    )
```

### API端点权限矩阵

| API端点 | 匿名用户 | 普通用户 | 管理员 | 超级管理员 | 说明 |
|---------|---------|---------|--------|------------|------|
| `POST /api/auth/register` | ✅ | ✅ | ✅ | ✅ | 用户注册 |
| `POST /api/auth/login` | ✅ | ✅ | ✅ | ✅ | 用户登录 |
| `GET /api/auth/me` | ❌ | ✅ | ✅ | ✅ | 获取个人信息 |
| `PUT /api/auth/me` | ❌ | ✅ | ✅ | ✅ | 更新个人信息 |
| `POST /api/auth/change-password` | ❌ | ✅ | ✅ | ✅ | 修改密码 |
| `GET /api/auth/users` | ❌ | ❌ | ✅ | ✅ | 用户列表 |
| `GET /api/auth/users/{id}` | ❌ | ❌ | ✅ | ✅ | 用户详情 |

## 数据模型

### 输入模型 (Request)

#### UserRegister
```python
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    real_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^1[3-9]\d{9}$")
```

#### UserLogin
```python
class UserLogin(BaseModel):
    username: str  # 支持用户名或邮箱
    password: str
```

#### UserUpdate
```python
class UserUpdate(BaseModel):
    real_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^1[3-9]\d{9}$")
```

#### UserChangePassword
```python
class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
```

### 输出模型 (Response)

#### UserRead
```python
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    real_name: Optional[str]
    phone: Optional[str]
    is_active: bool
    role: str  # 用户角色：'user', 'admin', 'super_admin'
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### Token
```python
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
```

## 使用示例

### 1. 前端集成示例

```javascript
// 用户注册
async function registerUser(userData) {
    const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });
    
    if (response.ok) {
        const user = await response.json();
        console.log('注册成功:', user);
        return user;
    } else {
        const error = await response.json();
        throw new Error(error.detail);
    }
}

// 用户登录
async function loginUser(credentials) {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
    });
    
    if (response.ok) {
        const tokenData = await response.json();
        // 存储令牌
        localStorage.setItem('access_token', tokenData.access_token);
        localStorage.setItem('refresh_token', tokenData.refresh_token);
        return tokenData;
    } else {
        const error = await response.json();
        throw new Error(error.detail);
    }
}

// 获取用户信息
async function getCurrentUser() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (response.ok) {
        return await response.json();
    } else if (response.status === 401) {
        // 令牌过期，尝试刷新
        await refreshToken();
        return getCurrentUser(); // 重试
    } else {
        throw new Error('获取用户信息失败');
    }
}

// 刷新令牌
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    if (response.ok) {
        const tokenData = await response.json();
        localStorage.setItem('access_token', tokenData.access_token);
        return tokenData;
    } else {
        // 刷新失败，重新登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
}
```

### 2. Python客户端示例

```python
import requests
from typing import Optional, Dict, Any

class UserAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """用户注册"""
        response = self.session.post(
            f"{self.base_url}/api/auth/register",
            json=user_data
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data["refresh_token"]
        
        # 设置默认认证头
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        
        return token_data
    
    def get_current_user(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        response = self.session.get(f"{self.base_url}/api/auth/me")
        
        if response.status_code == 401 and self.refresh_token:
            # 尝试刷新令牌
            self.refresh_access_token()
            response = self.session.get(f"{self.base_url}/api/auth/me")
        
        response.raise_for_status()
        return response.json()
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """刷新访问令牌"""
        response = self.session.post(
            f"{self.base_url}/api/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        
        # 更新认证头
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        
        return token_data
    
    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户资料"""
        response = self.session.put(
            f"{self.base_url}/api/auth/me",
            json=updates
        )
        response.raise_for_status()
        return response.json()
    
    def change_password(self, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        response = self.session.post(
            f"{self.base_url}/api/auth/change-password",
            json={
                "old_password": old_password,
                "new_password": new_password
            }
        )
        response.raise_for_status()
        return response.json()

# 使用示例
client = UserAPIClient("http://localhost:8000")

# 注册用户
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "secure123",
    "real_name": "Test User",
    "phone": "13800138000"
}
user = client.register(user_data)
print("注册成功:", user)

# 登录
token_data = client.login("testuser", "secure123")
print("登录成功:", token_data["user"])

# 获取用户信息
current_user = client.get_current_user()
print("当前用户:", current_user)

# 更新资料
updated_user = client.update_profile({
    "real_name": "Updated Test User",
    "phone": "13900139000"
})
print("更新成功:", updated_user)
```

## 安全考虑

### 1. 密码安全

```python
# 密码强度验证
def validate_password_strength(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*" for c in password)
    
    return sum([has_upper, has_lower, has_digit, has_special]) >= 3

# 密码策略中间件
@router.post("/api/auth/register")
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=400,
            detail="密码强度不足，需要包含大小写字母、数字和特殊字符"
        )
    # ... 注册逻辑
```

### 2. 频率限制

```python
from collections import defaultdict
from datetime import datetime, timedelta

# 简单的内存频率限制器
login_attempts = defaultdict(list)

def check_rate_limit(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """检查登录频率限制"""
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    # 清理过期记录
    login_attempts[identifier] = [
        attempt_time for attempt_time in login_attempts[identifier]
        if attempt_time > window_start
    ]
    
    # 检查是否超过限制
    if len(login_attempts[identifier]) >= max_attempts:
        return False
    
    # 记录本次尝试
    login_attempts[identifier].append(now)
    return True

@router.post("/api/auth/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # 检查频率限制
    if not check_rate_limit(user_data.username):
        raise HTTPException(
            status_code=429,
            detail="登录尝试过于频繁，请稍后再试"
        )
    # ... 登录逻辑
```

### 3. 输入验证

```python
from pydantic import validator
import re

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', v):
            raise ValueError('用户名只能包含字母、数字和下划线，长度3-50字符')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8个字符')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v
```

## 性能优化

### 1. 数据库查询优化

```python
# 优化用户查询
@router.get("/api/auth/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(User).options(
        defer(User.password_hash)  # 延迟加载密码哈希
    )
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.username.like(search_pattern)) |
            (User.email.like(search_pattern)) |
            (User.real_name.like(search_pattern))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users
```

### 2. 缓存优化

```python
from app.redis_client import get_redis_connection
import json

async def get_user_from_cache(user_id: int) -> Optional[dict]:
    """从缓存获取用户信息"""
    redis = await get_redis_connection()
    cached_user = await redis.get(f"user:{user_id}")
    
    if cached_user:
        return json.loads(cached_user)
    return None

async def cache_user_info(user: User, ttl: int = 300):
    """缓存用户信息"""
    redis = await get_redis_connection()
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "real_name": user.real_name,
        "is_active": user.is_active
    }
    await redis.setex(
        f"user:{user.id}",
        ttl,
        json.dumps(user_data)
    )

@router.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    # 尝试从缓存获取
    cached_user = await get_user_from_cache(current_user.id)
    if cached_user:
        return cached_user
    
    # 缓存用户信息
    await cache_user_info(current_user)
    
    return UserRead.from_orm(current_user)
```

## 错误处理

### 1. 统一错误响应

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class UserAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

# 错误处理器
@app.exception_handler(UserAPIException)
async def user_api_exception_handler(request, exc: UserAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code or "USER_API_ERROR",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

# 使用示例
@router.post("/api/auth/register")
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise UserAPIException(
                    status_code=400,
                    detail="用户名已存在",
                    error_code="USERNAME_EXISTS"
                )
            else:
                raise UserAPIException(
                    status_code=400,
                    detail="邮箱已存在",
                    error_code="EMAIL_EXISTS"
                )
        
        # ... 注册逻辑
        
    except IntegrityError:
        db.rollback()
        raise UserAPIException(
            status_code=500,
            detail="数据库操作失败",
            error_code="DATABASE_ERROR"
        )
```

## 测试示例

### 1. 单元测试

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User
from tests.conftest import override_get_db

client = TestClient(app)

def test_user_registration():
    """测试用户注册"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "real_name": "Test User"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data

def test_user_login():
    """测试用户登录"""
    # 先注册用户
    user_data = {
        "username": "logintest",
        "email": "login@example.com",
        "password": "LoginPass123!"
    }
    client.post("/api/auth/register", json=user_data)
    
    # 测试登录
    login_data = {
        "username": "logintest",
        "password": "LoginPass123!"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint():
    """测试受保护的端点"""
    # 登录获取令牌
    user_data = {
        "username": "protectedtest",
        "email": "protected@example.com",
        "password": "ProtectedPass123!"
    }
    client.post("/api/auth/register", json=user_data)
    
    login_response = client.post("/api/auth/login", json={
        "username": "protectedtest",
        "password": "ProtectedPass123!"
    })
    token = login_response.json()["access_token"]
    
    # 访问受保护端点
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "protectedtest"
```

### 2. 集成测试

```python
def test_complete_user_flow():
    """测试完整的用户流程"""
    # 1. 注册
    user_data = {
        "username": "flowtest",
        "email": "flow@example.com",
        "password": "FlowPass123!",
        "real_name": "Flow Test"
    }
    
    register_response = client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # 2. 登录
    login_response = client.post("/api/auth/login", json={
        "username": "flowtest",
        "password": "FlowPass123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. 获取用户信息
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    
    # 4. 更新用户信息
    update_response = client.put("/api/auth/me", 
        headers=headers,
        json={"real_name": "Updated Flow Test"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["real_name"] == "Updated Flow Test"
    
    # 5. 修改密码
    change_password_response = client.post("/api/auth/change-password",
        headers=headers,
        json={
            "old_password": "FlowPass123!",
            "new_password": "NewFlowPass456!"
        }
    )
    assert change_password_response.status_code == 200
    
    # 6. 用新密码登录
    new_login_response = client.post("/api/auth/login", json={
        "username": "flowtest",
        "password": "NewFlowPass456!"
    })
    assert new_login_response.status_code == 200
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1.0 | 2025-09-11 | 初始版本，实现基础用户认证API |

## 相关文档

- [用户认证模块](../authentication/overview.md)
- [API数据模型Schema](../schemas/overview.md)
- [JWT认证文档](../../api/standards.md#认证机制)
- [FastAPI路由文档](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
