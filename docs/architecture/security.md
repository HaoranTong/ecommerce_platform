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

### 敏感数据加密策略

**加密算法选择**:
- **对称加密**: AES-256-GCM用于敏感数据存储加密
- **非对称加密**: RSA-2048用于密钥交换和数字签名  
- **散列算法**: bcrypt用于密码散列存储
- **消息摘要**: SHA-256用于数据完整性验证

**数据分类加密**:
- **核心敏感数据**: 用户密码、银行卡号、身份证号等使用不可逆散列
- **重要业务数据**: 手机号、邮箱等使用可逆对称加密
- **一般业务数据**: 地址信息等使用部分加密或脱敏
- **公开展示数据**: 不加密，但需要防XSS处理

**密钥管理策略**:
- **密钥轮换**: 定期更换加密密钥，建立密钥版本管理
- **密钥分离**: 加密密钥与应用代码分离存储
- **访问控制**: 密钥访问需要多重身份验证
- **备份恢复**: 建立密钥的安全备份和恢复机制
```

## API 安全防护

### 请求验证

**设计原则**:
- 所有API输入必须进行严格验证
- 防止XSS、SQL注入等常见攻击
- 参数长度、格式、范围验证
- 恶意内容过滤和清理

**架构决策**:
- 输入验证：使用 Pydantic 模型进行请求验证
- XSS防护：过滤恶意脚本标签和JavaScript代码
- SQL注入防护：使用参数化查询，禁止动态SQL拼接
- 数据范围验证：价格、长度、数值范围验证

> **具体验证实现方案**: 详见 [API安全设计](../design/api/security-design.md)

### 速率限制
**设计原则**:
- 防止恶意用户过度调用API接口
- 不同用户角色实施不同的速率限制
- 敏感接口（登录、支付）实施更严格限制
- 支持基于IP和用户的多维度限流

**架构决策**:
- 限流器：使用 slowapi 实现分布式限流
- 限流策略：IP限流 + 用户角色限流
- 限流级别：全局默认 + 接口定制 + 用户角色定制
- 限流存储：Redis存储限流计数器

> **具体限流实现方案**: 详见 [API限流设计](../design/api/rate-limiting-design.md)

## 支付安全

### 支付数据保护

**设计原则**:
- 银行卡号等敏感信息必须脱敏处理
- 支付签名验证确保数据完整性
- 支付日志记录但不存储敏感信息
- 支付数据传输全程加密

**架构决策**:
- 数据脱敏：银行卡号、手机号等敏感信息脱敏显示
- 签名验证：支付数据使用HMAC-SHA256签名验证
- 日志安全：支付操作日志记录但脱敏处理
- 传输加密：支付接口使用HTTPS + 额外加密层

### 支付安全架构

**支付数据保护**:
- **传输安全**: 所有支付请求使用TLS 1.3加密传输
- **签名验证**: 使用RSA或HMAC-SHA256验证支付回调签名
- **敏感信息**: 支付密码、银行卡号等不在系统中存储
- **第三方集成**: 通过安全适配器与支付服务商对接

**支付风控策略**:
- **金额限制**: 单笔/日累计金额限制，超限需要额外验证
- **频率控制**: 同用户/IP/设备的支付频率限制
- **异常检测**: 基于用户行为模式的异常支付检测
- **黑名单机制**: IP黑名单、设备黑名单、风险用户黑名单

**支付状态管理**:
- **状态机控制**: 严格的支付状态流转控制
- **超时处理**: 支付超时自动取消和资源释放
- **补偿机制**: 支付失败的订单状态补偿和库存释放
- **对账机制**: 定时与第三方支付平台进行数据对账
```

### 安全审计架构

**审计日志策略**:
- **全量审计**: 所有涉及敏感数据的操作必须记录审计日志
- **分级记录**: 根据操作重要性分级记录，核心操作记录详细信息
- **结构化存储**: 使用结构化格式存储，便于后续分析和查询
- **长期保存**: 审计日志至少保存6个月，关键日志保存2年以上

**审计内容规范**:
- **用户行为**: 登录、权限变更、敏感操作等用户行为轨迹
- **系统事件**: 配置变更、系统启停、异常事件等系统级操作
- **数据访问**: 敏感数据的查询、修改、删除等数据操作
- **安全事件**: 攻击尝试、权限异常、安全策略触发等安全事件

**审计分析机制**:
- **实时监控**: 关键安全事件实时监控和告警
- **异常检测**: 基于机器学习的异常行为检测
- **合规报告**: 定期生成合规性审计报告
- **取证支持**: 支持安全事件的证据收集和分析
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
### 威胁检测架构

**实时威胁检测**:
- **攻击模式识别**: 识别SQL注入、XSS、CSRF等常见Web攻击模式  
- **异常行为检测**: 检测用户异常登录、批量操作、权限越权等行为
- **暴力破解防护**: 限制登录尝试次数，实施账户锁定和IP封禁
- **设备指纹识别**: 识别异常设备和可疑操作环境

**威胁响应机制**:
- **自动响应**: 对确认的攻击行为自动实施阻断和防护措施
- **告警通知**: 实时告警安全团队，提供威胁详情和影响评估
- **证据保全**: 自动收集和保存攻击证据，支持后续分析
- **恢复机制**: 攻击后的系统恢复和数据完整性验证

## 安全合规架构

### 数据保护合规
- **GDPR合规**: 用户数据收集授权、数据删除权、数据导出权
- **个人信息保护法**: 个人信息处理规则、敏感信息特殊保护
- **网络安全法**: 网络安全等级保护、数据本地化存储
- **行业标准**: 支付卡行业数据安全标准(PCI DSS)合规
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
### 安全配置管理架构

> **具体安全实现方案**: 详见 [安全实现设计](../design/system/security-design.md)

**配置安全原则**:
- **配置分离**: 安全配置与应用代码分离，使用环境变量或配置中心
- **加密存储**: 敏感配置信息加密存储，防止配置泄露  
- **权限控制**: 严格控制配置文件的访问和修改权限
- **版本管理**: 配置变更的版本控制和变更审计

**核心安全配置**:
- **JWT配置**: 密钥管理、令牌过期时间、签名算法选择
- **加密配置**: 加密算法、密钥轮换、密钥强度要求
- **密码策略**: 复杂度要求、过期策略、历史密码限制
- **会话配置**: 超时设置、Cookie安全属性、会话存储策略

### 安全中间件架构

**中间件分层**:
- **网络安全层**: WAF、DDoS防护、IP白名单/黑名单
- **传输安全层**: HTTPS强制、HSTS、SSL证书管理
- **应用安全层**: 认证授权、输入验证、安全头设置  
- **数据安全层**: 加密解密、敏感数据过滤、审计日志
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
