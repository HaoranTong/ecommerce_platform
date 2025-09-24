# 安全实现设计和加密方案

## 文档概述
**承接架构层**: [security.md](../../architecture/security.md) - 安全架构策略  
**设计职责**: 具体安全实现、加密算法、认证授权方案  
**边界约束**: 安全技术实现，不涉及具体业务安全规则  

## 认证授权实现

### JWT认证实现
```python
# JWT配置参数 - 迁移自architecture/security.md
import jwt
from datetime import datetime, timedelta
from typing import Optional

JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRE_MINUTES = 30
JWT_REFRESH_EXPIRE_DAYS = 7

# JWT配置结构
JWT_CONFIG = {
    "algorithm": "HS256",
    "access_token_expire": 3600,    # 1小时  
    "refresh_token_expire": 86400,  # 24小时
    "issuer": "ecommerce-platform",
    "audience": "api-users"
}

# JWT Token生成实现
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iss": JWT_CONFIG["issuer"],
        "aud": JWT_CONFIG["audience"]
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[JWT_ALGORITHM],
            audience=JWT_CONFIG["audience"],
            issuer=JWT_CONFIG["issuer"]
        )
        return payload
    except jwt.PyJWTError:
        return None
```

### 密码加密实现 - 多算法支持
```python
# 密码加密算法选择 - 迁移自architecture/security.md
from passlib.context import CryptContext

# 加密方案配置 - 支持bcrypt和Argon2
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"], 
    deprecated="auto",
    # Argon2 配置
    argon2__memory_cost=102400,  # 100MB内存成本
    argon2__time_cost=2,         # 时间成本
    argon2__parallelism=8,       # 并行度
    # bcrypt 配置
    bcrypt__rounds=12            # bcrypt轮次
)

# 密码哈希实现
def hash_password(password: str) -> str:
    """使用Argon2算法加密密码"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码，支持bcrypt和Argon2"""
    return pwd_context.verify(plain_password, hashed_password)

# 密码强度验证
def validate_password_strength(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return sum([has_upper, has_lower, has_digit, has_special]) >= 3
```

## 会话管理实现

### Redis会话存储
```python
# Redis会话配置
REDIS_SESSION_PREFIX = "session:"
SESSION_EXPIRE_SECONDS = 3600  # 1小时

# 会话存储实现
class RedisSessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def create_session(self, user_id: int, session_data: dict):
        session_id = secrets.token_urlsafe(32)
        key = f"{REDIS_SESSION_PREFIX}{session_id}"
        await self.redis.setex(key, SESSION_EXPIRE_SECONDS, json.dumps(session_data))
        return session_id
    
    async def get_session(self, session_id: str):
        key = f"{REDIS_SESSION_PREFIX}{session_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
```

### 会话安全机制
- **会话固化防护**: 登录后重新生成会话ID
- **并发会话控制**: 限制同一用户的并发会话数量
- **会话超时**: 自动过期和续期机制

## API安全实现

### 请求验证中间件
```python
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer

class SecurityMiddleware:
    def __init__(self):
        self.security = HTTPBearer()
    
    async def verify_token(self, request: Request):
        try:
            token = await self.security(request)
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

### CORS安全配置
```python
from fastapi.middleware.cors import CORSMiddleware

# CORS安全配置
CORS_ORIGINS = [
    "http://localhost:3000",  # 开发环境
    "https://yourdomain.com", # 生产环境
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 数据加密实现

### 敏感数据加密
```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### 数据库敏感字段加密
- **用户手机号**: AES加密存储
- **用户邮箱**: AES加密存储  
- **支付信息**: 独立加密密钥

## 安全中间件实现

### 请求限流实现
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# 全局限流配置
@limiter.limit("100/minute")
async def global_rate_limit(request: Request):
    pass

# 登录接口限流
@limiter.limit("5/minute") 
async def login_rate_limit(request: Request):
    pass
```

### SQL注入防护
```python
# 使用SQLAlchemy参数化查询
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).where(User.email == email)  # 安全的参数化查询
    )
    return result.scalar_one_or_none()
```

## 安全配置管理

### 环境变量安全
```python
# 安全配置
class SecuritySettings(BaseSettings):
    secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### 密钥管理策略
- **开发环境**: .env文件存储
- **测试环境**: 环境变量注入
- **生产环境**: 密钥管理服务(如AWS KMS)

## 安全监控实现

### 安全事件日志
```python
import structlog

security_logger = structlog.get_logger("security")

async def log_security_event(event_type: str, user_id: int = None, details: dict = None):
    security_logger.info(
        "security_event",
        event_type=event_type,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        details=details or {}
    )
```

### 异常行为检测
- **多次登录失败**: 自动锁定账户
- **异常IP访问**: 记录和告警
- **权限越界**: 实时监控和阻断

## 安全测试方案

### 安全测试工具
- **依赖扫描**: safety检查已知漏洞
- **静态分析**: bandit代码安全分析
- **渗透测试**: 定期安全评估

### 安全测试用例
- JWT Token篡改测试
- SQL注入防护测试  
- XSS防护测试
- CSRF防护测试

## 合规性要求

### 数据保护合规
- **GDPR**: 用户数据删除权
- **个人信息保护**: 数据最小化原则
- **数据留存**: 自动清理过期数据

### 安全审计
- **访问日志**: 完整的用户操作记录
- **权限变更**: 管理员操作审计
- **数据访问**: 敏感数据访问追踪

## 相关文档
- [架构层安全策略](../../architecture/security.md)
- [技术栈选型](./technology-stack.md)
- [性能设计方案](./performance-design.md)
- [用户认证模块设计](../modules/user-auth/design.md)
