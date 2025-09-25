# 环境变量管理指南

## 文档说明
- **内容**：环境变量配置、管理策略、安全策略、跨环境配置
- **使用者**：开发团队、运维人员、部署管理员
- **更新频率**：环境配置变更时更新
- **关联文档**：[开发环境配置](development-setup.md)、[生产环境配置](production-config.md)、[测试环境配置](../../tests/README.md)

**[CHECK:DOC-001]** 环境变量管理必须确保敏感信息安全

---

## 🎯 环境变量概览

### 环境层级管理
```
开发环境 (.env.development) → 本地开发配置
测试环境 (.env.testing) → 自动化测试配置  
预生产环境 (.env.staging) → 发布前验证配置
生产环境 (.env.production) → 生产服务配置
```

### 配置管理策略
```
配置模板 (.env.example) → 版本控制跟踪
环境配置 (.env.*) → 环境特定设置
密钥管理 (外部系统) → 敏感信息存储
```

**[CHECK:DOC-001]** 环境变量必须按敏感级别分类管理

---

## 📋 环境变量分类

### 应用基础配置
```bash
# 应用运行环境
ENVIRONMENT=development|testing|staging|production
DEBUG=true|false
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL

# 应用信息
PROJECT_NAME=电商平台
VERSION=1.0.0
API_V1_STR=/api/v1

# 服务端口
PORT=8000
HOST=0.0.0.0
```

### 数据库配置
```bash
# 数据库连接
DATABASE_URL=mysql+pymysql://user:password@host:port/database
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=database_name
MYSQL_USER=app_user
MYSQL_PASSWORD=app_password

# 连接池配置
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_MAX_OVERFLOW=30
```

### 缓存配置
```bash
# Redis连接
REDIS_URL=redis://host:port/db
REDIS_PASSWORD=redis_password
REDIS_DB=0

# Redis连接池
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
```

### 安全配置
```bash
# JWT认证
JWT_SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 加密密钥
ENCRYPTION_KEY=your-encryption-key
PASSWORD_SALT=your-password-salt

# CORS配置
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### 第三方服务配置
```bash
# 邮件服务
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=smtp_user
SMTP_PASSWORD=smtp_password
SMTP_TLS=true

# 支付服务
ALIPAY_APP_ID=alipay_app_id
ALIPAY_PRIVATE_KEY_PATH=/path/to/alipay_private.pem
WECHAT_APP_ID=wechat_app_id
WECHAT_SECRET=wechat_secret

# 对象存储
S3_BUCKET=your-s3-bucket
S3_REGION=us-east-1
S3_ACCESS_KEY=s3_access_key
S3_SECRET_KEY=s3_secret_key
```

**[CHECK:DOC-005]** 第三方服务配置必须支持多环境切换

---

## 🔧 开发环境配置

### .env.development
```bash
# 开发环境配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
HOT_RELOAD=true

# 本地数据库
DATABASE_URL=mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev
MYSQL_ROOT_PASSWORD=devpass
MYSQL_DATABASE=ecommerce_dev

# 本地Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# 开发JWT配置
JWT_SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时，方便开发

# 开发文件配置
UPLOAD_DIR=uploads/
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf

# Mock服务配置
MOCK_EXTERNAL_SERVICES=false
MOCK_PAYMENT_SERVICE=true
MOCK_EMAIL_SERVICE=true

# 开发工具配置
SHOW_DEBUG_TOOLBAR=true
ENABLE_PROFILER=true
```

### 开发环境脚本配置
```powershell
# dev_env.ps1 - 开发环境变量设置
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:JWT_SECRET_KEY = "dev-secret-key"
$env:DEBUG = "true"
$env:LOG_LEVEL = "DEBUG"

Write-Host "✓ 开发环境变量已设置" -ForegroundColor Green
```

---

## 🧪 测试环境配置

### .env.testing
```bash
# 测试环境配置
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO
TESTING=true

# 测试数据库（内存数据库）
DATABASE_URL=mysql+pymysql://root:testpass@mysql-test:3306/ecommerce_test
TEST_DATABASE_URL=sqlite:///./test.db  # 快速单元测试

# 测试Redis
REDIS_URL=redis://redis-test:6379/1
TEST_REDIS_URL=redis://localhost:6379/15

# 测试JWT配置（短过期时间）
JWT_SECRET_KEY=test-secret-key-for-testing-only
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 测试用户配置
TEST_USER_EMAIL=testuser@example.com
TEST_USER_PASSWORD=testpass123
TEST_ADMIN_EMAIL=admin@example.com
TEST_ADMIN_PASSWORD=adminpass123

# 测试文件配置
TEST_UPLOAD_DIR=/tmp/test_uploads/
TEST_MAX_FILE_SIZE=1048576  # 1MB for testing

# Mock服务配置（测试环境全部Mock）
MOCK_EXTERNAL_SERVICES=true
MOCK_PAYMENT_SERVICE=true
MOCK_EMAIL_SERVICE=true
MOCK_SMS_SERVICE=true

# 测试超时配置
TEST_TIMEOUT_UNIT=10
TEST_TIMEOUT_INTEGRATION=30
TEST_TIMEOUT_E2E=120
```

### CI/CD环境变量
```yaml
# GitHub Actions环境变量
env:
  DATABASE_URL: mysql+pymysql://root:testpass@127.0.0.1:3306/ecommerce_test
  REDIS_URL: redis://127.0.0.1:6379/1
  ENVIRONMENT: testing
  JWT_SECRET_KEY: test-secret-for-ci
  MOCK_EXTERNAL_SERVICES: true
```

---

## 🏭 生产环境配置

### .env.production
```bash
# 生产环境配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# 生产数据库（从环境变量获取敏感信息）
DATABASE_URL=mysql+pymysql://${PROD_DB_USER}:${PROD_DB_PASSWORD}@${PROD_DB_HOST}:3306/${PROD_DB_NAME}

# 生产Redis
REDIS_URL=redis://:{PROD_REDIS_PASSWORD}@${PROD_REDIS_HOST}:6379/0

# 生产JWT配置（高安全性）
JWT_SECRET_KEY=${PROD_JWT_SECRET}
ACCESS_TOKEN_EXPIRE_MINUTES=120  # 2小时

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/production.crt
SSL_KEY_PATH=/etc/ssl/private/production.key

# 安全配置
CORS_ORIGINS=${PROD_CORS_ORIGINS}
ALLOWED_HOSTS=${PROD_ALLOWED_HOSTS}

# 监控配置
SENTRY_DSN=${PROD_SENTRY_DSN}
NEW_RELIC_LICENSE_KEY=${PROD_NEW_RELIC_KEY}
PROMETHEUS_METRICS_PORT=9090

# 生产第三方服务
ALIPAY_APP_ID=${PROD_ALIPAY_APP_ID}
ALIPAY_PRIVATE_KEY_PATH=/etc/ssl/keys/alipay_private.pem
WECHAT_APP_ID=${PROD_WECHAT_APP_ID}
WECHAT_SECRET=${PROD_WECHAT_SECRET}

# 生产文件存储
UPLOAD_STORAGE=s3
S3_BUCKET=${PROD_S3_BUCKET}
S3_REGION=${PROD_S3_REGION}
CDN_URL=${PROD_CDN_URL}

# 性能配置
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
WORKER_CLASS=uvicorn.workers.UvicornWorker
```

### Kubernetes ConfigMap和Secret
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ecommerce-prod
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "WARNING"
  API_V1_STR: "/api/v1"
  PROJECT_NAME: "电商平台"
  GUNICORN_WORKERS: "4"

---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ecommerce-prod
type: Opaque
stringData:
  DATABASE_URL: "mysql+pymysql://user:password@mysql:3306/ecommerce"
  REDIS_URL: "redis://:password@redis:6379/0"
  JWT_SECRET_KEY: "production-secret-key"
```

---

## 🔒 安全管理策略

### 敏感信息分级
| 敏感级别 | 信息类型 | 存储方式 | 访问控制 |
|----------|----------|----------|----------|
| **L1-极敏感** | 数据库密码、JWT密钥 | 密钥管理系统 | 运维人员Only |
| **L2-敏感** | 第三方API密钥 | 环境变量注入 | 运维+开发主管 |
| **L3-一般** | 配置参数 | ConfigMap | 开发团队 |
| **L4-公开** | 应用信息、端口 | 代码仓库 | 所有人员 |

### 密钥轮换策略
```bash
#!/bin/bash
# 密钥轮换脚本
rotate_secrets() {
    local secret_name=$1
    local namespace=$2
    
    echo "轮换密钥: $secret_name"
    
    # 1. 生成新密钥
    NEW_JWT_SECRET=$(openssl rand -base64 32)
    NEW_DB_PASSWORD=$(openssl rand -base64 16)
    
    # 2. 创建新Secret
    kubectl create secret generic ${secret_name}-new \
      --from-literal=JWT_SECRET_KEY=$NEW_JWT_SECRET \
      --from-literal=DB_PASSWORD=$NEW_DB_PASSWORD \
      -n $namespace
    
    # 3. 更新Deployment
    kubectl patch deployment ecommerce-app -n $namespace -p \
      '{"spec":{"template":{"spec":{"containers":[{"name":"app","envFrom":[{"secretRef":{"name":"'${secret_name}'-new"}}]}]}}}}'
    
    # 4. 等待部署完成
    kubectl rollout status deployment/ecommerce-app -n $namespace
    
    # 5. 删除旧Secret
    kubectl delete secret $secret_name -n $namespace
    
    # 6. 重命名新Secret
    kubectl patch secret ${secret_name}-new -n $namespace -p \
      '{"metadata":{"name":"'$secret_name'"}}'
    
    echo "密钥轮换完成"
}
```

### 环境变量验证
```python
# app/core/config_validator.py
import os
from typing import List, Dict, Any
import logging

class ConfigValidator:
    """配置验证器"""
    
    REQUIRED_VARS = {
        'development': [
            'DATABASE_URL', 'REDIS_URL', 'JWT_SECRET_KEY'
        ],
        'testing': [
            'DATABASE_URL', 'REDIS_URL', 'JWT_SECRET_KEY', 'TESTING'
        ],
        'production': [
            'DATABASE_URL', 'REDIS_URL', 'JWT_SECRET_KEY',
            'SSL_CERT_PATH', 'SSL_KEY_PATH', 'SENTRY_DSN'
        ]
    }
    
    SENSITIVE_VARS = [
        'JWT_SECRET_KEY', 'DATABASE_URL', 'REDIS_PASSWORD',
        'ALIPAY_PRIVATE_KEY_PATH', 'WECHAT_SECRET'
    ]
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self.logger = logging.getLogger(__name__)
    
    def validate_required_vars(self) -> List[str]:
        """验证必需的环境变量"""
        missing_vars = []
        required = self.REQUIRED_VARS.get(self.environment, [])
        
        for var in required:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")
        
        return missing_vars
    
    def validate_sensitive_vars(self) -> Dict[str, bool]:
        """验证敏感变量的安全性"""
        validation_results = {}
        
        for var in self.SENSITIVE_VARS:
            value = os.getenv(var)
            if value:
                # 检查是否使用默认值
                is_secure = not self._is_default_value(var, value)
                validation_results[var] = is_secure
                
                if not is_secure:
                    self.logger.warning(f"环境变量 {var} 使用默认值，存在安全风险")
        
        return validation_results
    
    def _is_default_value(self, var_name: str, value: str) -> bool:
        """检查是否为默认值"""
        default_patterns = [
            'dev-secret', 'test-secret', 'changeme',
            'password', '123456', 'admin'
        ]
        
        return any(pattern in value.lower() for pattern in default_patterns)

# 使用示例
validator = ConfigValidator()
try:
    validator.validate_required_vars()
    security_check = validator.validate_sensitive_vars()
    print("配置验证通过")
except ValueError as e:
    print(f"配置验证失败: {e}")
```

**[CHECK:DOC-007]** 敏感环境变量必须定期安全审计

---

## 🛠️ 配置管理工具

### 环境配置脚本
```powershell
# scripts/env_manager.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("development", "testing", "staging", "production")]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("create", "validate", "sync", "backup")]
    [string]$Action
)

function New-EnvironmentConfig {
    param([string]$Env)
    
    $templateFile = ".env.example"
    $targetFile = ".env.$Env"
    
    if (Test-Path $templateFile) {
        Copy-Item $templateFile $targetFile
        Write-Host "✓ 创建环境配置文件: $targetFile" -ForegroundColor Green
        
        # 根据环境调整默认值
        switch ($Env) {
            "development" {
                (Get-Content $targetFile) -replace 'ENVIRONMENT=.*', 'ENVIRONMENT=development' |
                Set-Content $targetFile
            }
            "testing" {
                (Get-Content $targetFile) -replace 'ENVIRONMENT=.*', 'ENVIRONMENT=testing' |
                Set-Content $targetFile
            }
        }
    } else {
        Write-Error "模板文件不存在: $templateFile"
    }
}

function Test-EnvironmentConfig {
    param([string]$Env)
    
    $configFile = ".env.$Env"
    
    if (-not (Test-Path $configFile)) {
        Write-Error "配置文件不存在: $configFile"
        return
    }
    
    # 检查必需变量
    $requiredVars = @("DATABASE_URL", "REDIS_URL", "JWT_SECRET_KEY")
    $content = Get-Content $configFile
    
    foreach ($var in $requiredVars) {
        if (-not ($content | Select-String "^$var=")) {
            Write-Warning "缺少必需变量: $var"
        } else {
            Write-Host "✓ 发现必需变量: $var" -ForegroundColor Green
        }
    }
}

function Sync-EnvironmentConfig {
    param([string]$Env)
    
    Write-Host "同步环境配置: $Env"
    
    # 备份现有配置
    $configFile = ".env.$Env"
    if (Test-Path $configFile) {
        $backupFile = "$configFile.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item $configFile $backupFile
        Write-Host "✓ 备份现有配置: $backupFile" -ForegroundColor Yellow
    }
    
    # 从模板更新
    New-EnvironmentConfig -Env $Env
}

# 执行操作
switch ($Action) {
    "create" { New-EnvironmentConfig -Env $Environment }
    "validate" { Test-EnvironmentConfig -Env $Environment }
    "sync" { Sync-EnvironmentConfig -Env $Environment }
    "backup" { 
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        Copy-Item ".env.$Environment" ".env.$Environment.backup.$timestamp"
        Write-Host "✓ 配置已备份" -ForegroundColor Green
    }
}
```

### Docker环境变量管理
```yaml
# docker-compose.override.yml (本地开发)
version: '3.8'

services:
  app:
    env_file:
      - .env.development
    environment:
      # 覆盖特定变量
      - LOG_LEVEL=DEBUG
      - DEBUG=true
```

### Kubernetes环境变量注入
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        # 从Secret注入敏感变量
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        # 从ConfigMap注入配置变量
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
```

---

## 🔍 配置监控和审计

### 配置变更监控
```python
# app/monitoring/config_monitor.py
import os
import hashlib
import json
from datetime import datetime

class ConfigMonitor:
    """配置监控器"""
    
    def __init__(self):
        self.config_hash = self._calculate_config_hash()
        self.last_check = datetime.now()
    
    def _calculate_config_hash(self) -> str:
        """计算配置哈希值"""
        config_vars = {}
        
        # 收集所有环境变量（排除敏感信息）
        for key, value in os.environ.items():
            if not self._is_sensitive_var(key):
                config_vars[key] = value
        
        config_str = json.dumps(config_vars, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _is_sensitive_var(self, var_name: str) -> bool:
        """判断是否为敏感变量"""
        sensitive_patterns = ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']
        return any(pattern in var_name.upper() for pattern in sensitive_patterns)
    
    def check_config_changes(self) -> bool:
        """检查配置是否发生变化"""
        new_hash = self._calculate_config_hash()
        
        if new_hash != self.config_hash:
            print(f"检测到配置变更: {self.config_hash} -> {new_hash}")
            self.config_hash = new_hash
            self.last_check = datetime.now()
            return True
        
        return False

# 配置审计日志
def log_config_access(var_name: str, access_type: str = "read"):
    """记录配置访问日志"""
    audit_log = {
        "timestamp": datetime.now().isoformat(),
        "variable": var_name,
        "access_type": access_type,
        "is_sensitive": "PASSWORD" in var_name.upper() or "SECRET" in var_name.upper()
    }
    
    # 写入审计日志
    with open("/var/log/config_audit.log", "a") as f:
        f.write(json.dumps(audit_log) + "\n")
```

### 配置合规检查
```bash
#!/bin/bash
# scripts/config_compliance_check.sh

echo "=== 配置合规性检查 ==="

# 检查敏感信息是否暴露
check_sensitive_exposure() {
    echo "检查敏感信息暴露..."
    
    # 检查是否有明文密码
    if grep -r "password.*=" . --exclude-dir=.git --exclude="*.log" | grep -v "example"; then
        echo "❌ 发现明文密码配置"
    else
        echo "✓ 未发现明文密码暴露"
    fi
    
    # 检查默认密钥
    if grep -r "secret.*=.*secret" . --exclude-dir=.git; then
        echo "❌ 发现使用默认密钥"
    else
        echo "✓ 未发现默认密钥使用"
    fi
}

# 检查环境隔离
check_environment_isolation() {
    echo "检查环境隔离..."
    
    # 检查生产配置是否包含开发信息
    if [ -f ".env.production" ]; then
        if grep -q "localhost\|127.0.0.1\|dev" .env.production; then
            echo "❌ 生产配置包含开发环境信息"
        else
            echo "✓ 生产环境隔离正常"
        fi
    fi
}

# 检查配置完整性
check_config_completeness() {
    echo "检查配置完整性..."
    
    required_files=(".env.example" ".env.development" ".env.testing")
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo "✓ 发现配置文件: $file"
        else
            echo "❌ 缺少配置文件: $file"
        fi
    done
}

# 执行检查
check_sensitive_exposure
check_environment_isolation  
check_config_completeness

echo "=== 合规性检查完成 ==="
```

**[CHECK:DOC-001]** 配置合规检查必须纳入CI/CD流程

---

## 📋 最佳实践

### 配置管理原则
1. **环境隔离**: 不同环境使用独立的配置文件
2. **敏感分离**: 敏感信息与普通配置分离存储
3. **模板管理**: 使用配置模板确保一致性
4. **版本控制**: 配置模板纳入版本控制，实际配置不入库
5. **动态加载**: 支持运行时配置热更新
6. **审计记录**: 记录配置访问和变更日志

### 安全管理原则
1. **最小权限**: 每个环境只配置必要的权限
2. **定期轮换**: 定期更新密钥和密码
3. **访问控制**: 严格控制生产环境配置访问
4. **加密存储**: 敏感配置使用加密存储
5. **监控告警**: 配置变更实时监控告警
6. **合规审计**: 定期进行配置安全审计

### 故障预防原则
1. **配置验证**: 启动时验证配置完整性
2. **默认值处理**: 提供合理的配置默认值
3. **降级策略**: 配置异常时的服务降级
4. **备份恢复**: 配置变更前自动备份
5. **回滚机制**: 支持快速配置回滚

**[CHECK:DOC-003]** 配置管理必须遵循最佳实践原则

---

## 🆘 故障排除

### 常见配置问题
| 问题类型 | 症状 | 解决方案 |
|----------|------|----------|
| 环境变量未加载 | 应用启动失败 | 检查环境变量设置和文件路径 |
| 数据库连接失败 | 连接超时错误 | 验证DATABASE_URL格式和网络连通性 |
| Redis连接异常 | 缓存功能异常 | 检查REDIS_URL和密码配置 |
| JWT验证失败 | 认证错误 | 确认JWT_SECRET_KEY一致性 |
| 第三方服务调用失败 | API调用超时 | 检查第三方服务配置和网络访问 |

### 配置诊断脚本
```bash
#!/bin/bash
# 配置诊断脚本
echo "=== 环境配置诊断 ==="

# 检查环境变量
echo "1. 环境变量检查:"
echo "ENVIRONMENT: ${ENVIRONMENT:-未设置}"
echo "DATABASE_URL: ${DATABASE_URL:0:20}..." 
echo "REDIS_URL: ${REDIS_URL:-未设置}"

# 测试数据库连接
echo "2. 数据库连接测试:"
if command -v mysql &> /dev/null; then
    mysql --connect-timeout=5 -e "SELECT 1;" 2>/dev/null && echo "✓ 数据库连接正常" || echo "❌ 数据库连接失败"
fi

# 测试Redis连接
echo "3. Redis连接测试:"
if command -v redis-cli &> /dev/null; then
    redis-cli ping 2>/dev/null && echo "✓ Redis连接正常" || echo "❌ Redis连接失败"
fi

# 检查文件权限
echo "4. 配置文件权限:"
ls -la .env* 2>/dev/null || echo "无配置文件"

echo "=== 诊断完成 ==="
```

---

## 相关文档
- [开发环境配置](development-setup.md) - 开发环境详细配置
- [测试环境配置](../../tests/README.md) - 测试环境配置管理
- [生产环境配置](production-config.md) - 生产环境安全配置
- [部署指南](deployment.md) - 配置在部署中的应用
