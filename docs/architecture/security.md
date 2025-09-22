<!--
文档说明：
- 内容：系统安全架构设计和实施规范
- 使用方法：安全相关功能开发时的指导文档
- 更新方法：安全要求变更或漏洞修复时更新
- 引用关系：被各模块安全实现引用
- 更新频率：安全策略调整时
-->

# 安全架构规范

## 安全设计原则

### 核心原则
1. **零信任原则** - 不信任任何内外部网络和用户
2. **最小权限原则** - 用户和服务只获得必需的最小权限
3. **纵深防御** - 多层安全防护机制
4. **安全by设计** - 从架构设计阶段考虑安全
5. **持续监控** - 实时安全监控和威胁检测

### 安全目标
- **机密性** - 保护敏感数据不被未授权访问
- **完整性** - 确保数据在传输和存储过程中不被篡改
- **可用性** - 确保系统服务的持续可用
- **可追溯性** - 完整的操作审计和日志记录

## 身份认证架构

### 认证方式
```
用户认证流程：
1. 用户名密码认证
2. 手机验证码认证
3. 微信OAuth认证
4. JWT Token验证
```

### 多因子认证策略

#### 认证因子分类
- **知识因子**: 用户知道的信息（密码、PIN码）
- **持有因子**: 用户拥有的设备（短信验证码、硬件令牌）  
- **生物因子**: 用户身体特征（指纹、面部识别）

#### 认证策略原则
- **风险评估**: 根据操作风险等级选择认证因子组合
- **用户体验**: 平衡安全性和用户便利性
- **降级支持**: 在生物识别不可用时提供备用方案

### JWT认证架构原则

#### Token设计原则
- **无状态设计**: Token包含完整的身份和权限信息
- **有限生命周期**: 设置合理的Token过期时间
- **撤销机制**: 支持Token黑名单和主动撤销
- **签名验证**: 使用加密算法确保Token完整性

#### Token载荷结构
- **用户标识**: 用户ID和基础信息
- **角色权限**: 用户角色和具体权限列表
- **时间控制**: 发布时间、过期时间、生效时间
- **发布信息**: 发行者、受众、唯一标识符

> **具体实现方案**: 详见 [系统安全设计](../design/system/security-design.md)

## 授权访问控制

### RBAC权限架构

#### 角色层次设计
- **访客角色**: 未登录用户的基础浏览权限
- **用户角色**: 普通用户和高级会员的差异化权限
- **业务角色**: 分销商、供应商、商户的业务操作权限
- **管理角色**: 客服、运营、财务的后台管理权限
- **系统角色**: 管理员和超级管理员的系统控制权限

#### 权限分类体系
- **数据权限**: 对业务数据的读取、写入、删除权限
- **功能权限**: 对系统功能模块的访问和操作权限
- **管理权限**: 对系统配置和用户管理的控制权限
- **审计权限**: 对系统日志和报表的查看权限

#### 权限继承原则
- **垂直继承**: 上级角色自动继承下级角色的所有权限
- **权限最小化**: 每个角色只分配必需的最小权限集合
- **动态调整**: 支持运行时权限的动态授予和撤销

> **具体角色和权限定义**: 详见 [系统安全设计](../design/system/security-design.md)
    
    # 用户权限
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    MANAGE_USERS = "manage:users"
    
    # 分销权限
    READ_DISTRIBUTORS = "read:distributors"
    WRITE_DISTRIBUTORS = "write:distributors"
    MANAGE_COMMISSIONS = "manage:commissions"
    
    # 供应商权限
    READ_SUPPLIERS = "read:suppliers"
    WRITE_SUPPLIERS = "write:suppliers"
    MANAGE_SUPPLIERS = "manage:suppliers"
    
    # 会员权限
    READ_MEMBERS = "read:members"
    WRITE_MEMBERS = "write:members"
    MANAGE_POINTS = "manage:points"
    
    # 营销权限
    READ_CAMPAIGNS = "read:campaigns"
    WRITE_CAMPAIGNS = "write:campaigns"
    MANAGE_COUPONS = "manage:coupons"
    
    # 溯源权限
    READ_TRACE = "read:trace"
    WRITE_TRACE = "write:trace"
    
    # 客服权限
    READ_TICKETS = "read:tickets"
    WRITE_TICKETS = "write:tickets"
    MANAGE_TICKETS = "manage:tickets"
    
    # 财务权限
    READ_FINANCE = "read:finance"
    WRITE_FINANCE = "write:finance"
    MANAGE_SETTLEMENTS = "manage:settlements"
    
    # 系统权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"

# 角色权限映射
ROLE_PERMISSIONS = {
    Role.GUEST: [
        Permission.READ_PRODUCTS
    ],
    Role.USER: [
        Permission.READ_PRODUCTS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
        Permission.READ_TRACE
    ],
    Role.DISTRIBUTOR: [
        Permission.READ_PRODUCTS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
        Permission.READ_DISTRIBUTORS,
        Permission.WRITE_DISTRIBUTORS,
        Permission.READ_TRACE
    ],
    Role.SUPPLIER: [
        Permission.READ_PRODUCTS,
        Permission.WRITE_PRODUCTS,
        Permission.READ_ORDERS,
        Permission.MANAGE_ORDERS,
        Permission.READ_SUPPLIERS,
        Permission.WRITE_SUPPLIERS,
        Permission.WRITE_TRACE
    ],
    Role.CUSTOMER_SERVICE: [
        Permission.READ_PRODUCTS,
        Permission.READ_ORDERS,
        Permission.MANAGE_ORDERS,
        Permission.READ_USERS,
        Permission.READ_TICKETS,
        Permission.WRITE_TICKETS,
        Permission.MANAGE_TICKETS
    ],
    Role.OPERATIONS: [
        Permission.READ_PRODUCTS,
        Permission.WRITE_PRODUCTS,
        Permission.READ_CAMPAIGNS,
        Permission.WRITE_CAMPAIGNS,
        Permission.MANAGE_COUPONS,
        Permission.READ_USERS,
        Permission.WRITE_USERS
    ],
    Role.FINANCE: [
        Permission.READ_ORDERS,
        Permission.READ_FINANCE,
        Permission.WRITE_FINANCE,
        Permission.MANAGE_SETTLEMENTS,
        Permission.MANAGE_COMMISSIONS
    ],
    Role.MERCHANT: [
        Permission.READ_PRODUCTS,
        Permission.WRITE_PRODUCTS,
        Permission.READ_ORDERS
    ],
    Role.ADMIN: [
        Permission.READ_PRODUCTS,
        Permission.WRITE_PRODUCTS,
        Permission.DELETE_PRODUCTS,
        Permission.READ_ORDERS,
        Permission.MANAGE_ORDERS,
        Permission.READ_USERS,
        Permission.MANAGE_USERS,
        Permission.SYSTEM_MONITOR
    ]
}
```

### API权限控制架构

#### 权限控制设计原则
- **装饰器模式**: 使用装饰器实现权限控制的横切关注点
- **细粒度控制**: 支持接口级、方法级的细粒度权限控制
- **权限检查**: 在业务逻辑执行前进行权限验证
- **异常处理**: 统一的权限不足异常处理机制

#### API权限策略
- **资源权限**: 基于资源类型的权限控制
- **操作权限**: 基于操作类型的权限控制  
- **数据权限**: 基于数据归属的权限控制
- **上下文权限**: 基于请求上下文的动态权限控制

> **具体权限控制实现**: 详见 [系统安全设计](../design/system/security-design.md)

## 数据加密保护

### 传输安全架构

#### HTTPS安全策略
- **强制HTTPS**: 所有API通信必须使用HTTPS协议
- **TLS版本**: 支持TLS 1.2和1.3，禁用旧版本协议
- **加密套件**: 选择高强度的加密算法套件
- **HSTS策略**: 启用HTTP严格传输安全策略

#### 安全头配置
- **内容安全**: 配置CSP、CSRF保护等安全头
- **传输安全**: 启用HSTS、HPKP等传输安全机制
- **信息泄露**: 隐藏服务器版本等敏感信息
- **跨域安全**: 合理配置CORS策略

### 存储安全架构

#### 数据加密策略
- **敏感数据**: 用户隐私数据使用强加密算法加密存储
- **密码安全**: 使用安全的哈希算法存储用户密码
- **密钥管理**: 建立安全的密钥生成、存储和轮换机制
- **分级加密**: 根据数据敏感程度选择不同加密强度

#### 加密算法选择
- **对称加密**: 选择AES等安全的对称加密算法
- **哈希算法**: 选择bcrypt、Argon2等安全的密码哈希算法
- **随机数**: 使用加密安全的随机数生成器
- **盐值策略**: 为每个密码生成唯一的盐值

> **具体加密实现方案**: 详见 [系统安全设计](../design/system/security-design.md)
    
    @staticmethod
    def verify_password(password, hashed):
        """密码验证"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

# 数据库敏感字段加密
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone_encrypted = Column(Text)  # 加密存储的手机号
    password_hash = Column(String(255), nullable=False)
    
    @property
    def phone(self):
        if self.phone_encrypted:
            return encryption.decrypt_sensitive_data(self.phone_encrypted)
        return None
    
    @phone.setter
    def phone(self, value):
        self.phone_encrypted = encryption.encrypt_sensitive_data(value)
```

## API 安全防护

### 请求验证
```python
from pydantic import BaseModel, validator
from typing import Optional

class ProductCreateRequest(BaseModel):
    name: str
    price: float
    category_id: int
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1 or len(v) > 200:
            raise ValueError('商品名称长度必须在1-200字符之间')
        # XSS 防护
        if '<script>' in v.lower() or 'javascript:' in v.lower():
            raise ValueError('商品名称包含非法字符')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('价格不能为负数')
        if v > 999999.99:
            raise ValueError('价格不能超过999999.99')
        return v

# SQL 注入防护
class ProductRepository:
    def get_by_category(self, category_id: int):
        # 使用参数化查询防止 SQL 注入
        query = """
        SELECT * FROM products 
        WHERE category_id = :category_id 
        AND status = 'active'
        """
        return self.db.execute(query, {"category_id": category_id})
```

### 速率限制
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 限流器配置
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# 应用限流
@app.get("/api/v1/products")
@limiter.limit("10 per minute")
def get_products(request: Request):
    return ProductService.get_all()

@app.post("/api/v1/auth/login")
@limiter.limit("5 per minute")  # 登录接口更严格的限制
def login(request: Request, credentials: LoginRequest):
    return AuthService.login(credentials)

# 自定义限流策略
class UserBasedLimiter:
    def __init__(self):
        self.limits = {
            'guest': "50 per minute",
            'user': "200 per minute",
            'premium': "500 per minute",
            'admin': "1000 per minute"
        }
    
    def get_limit(self, user_role):
        return self.limits.get(user_role, "50 per minute")
```

## 支付安全

### 支付数据保护
```python
class PaymentSecurity:
    @staticmethod
    def mask_card_number(card_number):
        """银行卡号脱敏"""
        if len(card_number) < 8:
            return card_number
        return card_number[:4] + '*' * (len(card_number) - 8) + card_number[-4:]
    
    @staticmethod
    def generate_payment_signature(data, secret_key):
        """生成支付签名"""
        sorted_data = sorted(data.items())
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_data])
        sign_string += f"&key={secret_key}"
        return hashlib.md5(sign_string.encode()).hexdigest().upper()
    
    @staticmethod
    def verify_payment_callback(data, signature, secret_key):
        """验证支付回调签名"""
        expected_signature = PaymentSecurity.generate_payment_signature(
            data, secret_key
        )
        return signature == expected_signature

# 支付风控
class PaymentRiskControl:
    def __init__(self):
        self.risk_rules = [
            self.check_amount_limit,
            self.check_frequency_limit,
            self.check_device_fingerprint,
            self.check_ip_blacklist
        ]
    
    def evaluate_risk(self, payment_request):
        risk_score = 0
        for rule in self.risk_rules:
            risk_score += rule(payment_request)
        
        if risk_score > 80:
            return "HIGH_RISK"
        elif risk_score > 50:
            return "MEDIUM_RISK"
        else:
            return "LOW_RISK"
```

## 安全监控与审计

### 操作审计
```python
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=func.now())

def audit_log(action, resource_type, resource_id=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = get_current_request()
            user = get_current_user()
            
            # 记录请求信息
            audit = AuditLog(
                user_id=user.id if user else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=request.client.host,
                user_agent=request.headers.get('user-agent'),
                request_data=request.json()
            )
            
            try:
                result = func(*args, **kwargs)
                audit.response_data = {"success": True}
                return result
            except Exception as e:
                audit.response_data = {
                    "success": False,
                    "error": str(e)
                }
                raise
            finally:
                db.add(audit)
                db.commit()
        
        return wrapper
    return decorator

# 使用审计装饰器
@app.post("/api/v1/products")
@audit_log("CREATE", "PRODUCT")
def create_product(product_data):
    return ProductService.create(product_data)
```

### 安全监控
```python
class SecurityMonitor:
    def __init__(self):
        self.threat_patterns = [
            self.detect_sql_injection,
            self.detect_xss_attempt,
            self.detect_brute_force,
            self.detect_unusual_activity
        ]
    
    def analyze_request(self, request):
        threats = []
        for pattern in self.threat_patterns:
            threat = pattern(request)
            if threat:
                threats.append(threat)
        
        if threats:
            self.alert_security_team(threats, request)
        
        return threats
    
    def detect_sql_injection(self, request):
        sql_patterns = [
            r"union.*select",
            r"drop.*table",
            r"insert.*into",
            r"delete.*from"
        ]
        
        content = str(request.json()) + str(request.query_params)
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    "type": "SQL_INJECTION",
                    "pattern": pattern,
                    "content": content[:100]
                }
        return None
    
    def detect_brute_force(self, request):
        if request.url.path.endswith('/login'):
            ip = request.client.host
            # 检查该IP的登录失败次数
            failed_attempts = get_failed_login_attempts(ip, 
                                                      last_minutes=10)
            if failed_attempts > 5:
                return {
                    "type": "BRUTE_FORCE",
                    "ip": ip,
                    "attempts": failed_attempts
                }
        return None
```

## 合规性要求

### 数据保护合规
```python
class GDPRCompliance:
    """GDPR/个人信息保护法合规"""
    
    def user_consent_required(self, data_type):
        """检查是否需要用户同意"""
        sensitive_data = [
            'email', 'phone', 'address', 
            'payment_info', 'biometric_data'
        ]
        return data_type in sensitive_data
    
    def anonymize_user_data(self, user_id):
        """用户数据匿名化"""
        # 删除或匿名化个人标识信息
        # 保留必要的业务数据（如订单统计）
        pass
    
    def export_user_data(self, user_id):
        """导出用户数据（数据可携带权）"""
        # 导出用户的所有个人数据
        pass
    
    def delete_user_data(self, user_id):
        """删除用户数据（被遗忘权）"""
        # 删除用户的所有个人数据
        # 保留法律要求的审计数据
        pass

# PCI DSS 合规
class PCIDSSCompliance:
    """支付卡行业数据安全标准合规"""
    
    def validate_card_data_handling(self):
        """验证银行卡数据处理合规性"""
        checks = [
            self.check_card_data_encryption(),
            self.check_access_control(),
            self.check_network_security(),
            self.check_vulnerability_management(),
            self.check_monitoring_and_testing()
        ]
        return all(checks)
```

## 安全配置管理

### 环境配置
```python
# 安全配置
SECURITY_CONFIG = {
    # JWT 配置
    "jwt": {
        "secret_key": os.getenv("JWT_SECRET_KEY"),
        "algorithm": "HS256",
        "access_token_expire": 3600,
        "refresh_token_expire": 86400
    },
    
    # 加密配置
    "encryption": {
        "key": os.getenv("ENCRYPTION_KEY"),
        "algorithm": "AES-256-GCM"
    },
    
    # 密码策略
    "password": {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": False,
        "max_age_days": 90
    },
    
    # 会话配置
    "session": {
        "timeout": 3600,
        "secure": True,
        "http_only": True,
        "same_site": "strict"
    }
}
```

### 安全头配置
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

# 安全中间件
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["api.example.com", "*.example.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 安全响应头
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```
