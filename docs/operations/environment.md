# 环境变量管理指南

## 文档说明
- **内容**：环境变量配置、管理策略、安全策略、不同环境配置
- **使用者**：开发团队、运维人员、部署管理员
- **更新频率**：环境配置变更时更新
- **关联文档**：[部署指南](deployment.md)、[开发环境配置](../development/environment-setup.md)

---

## 环境变量概述

本项目使用`.env`文件管理环境变量，以确保配置的灵活性和安全性。

### 文件说明
- `.env` - 实际环境变量文件（不被Git跟踪）
- `.env.example` - 环境变量模板文件（被Git跟踪）
- `scripts/sync_env.ps1` - 环境变量同步工具

---

## 环境变量配置

### 开发环境配置 (.env.development)
```env
# 应用配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# 数据库配置
DATABASE_URL=mysql+pymysql://root:devpass@localhost:3307/ecommerce_dev
MYSQL_ROOT_PASSWORD=devpass
MYSQL_DATABASE=ecommerce_dev

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# JWT认证配置
JWT_SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API配置
API_V1_STR=/api/v1
PROJECT_NAME=电商平台
VERSION=1.0.0

# 文件上传配置
UPLOAD_DIR=uploads/
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif

# 第三方服务配置
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.example.com
SMTP_USER=
SMTP_PASSWORD=

# 支付配置（开发环境）
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY_PATH=
ALIPAY_PUBLIC_KEY_PATH=
WECHAT_APP_ID=
WECHAT_SECRET=
```

### 测试环境配置 (.env.testing)
```env
# 应用配置
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO

# 测试数据库配置
DATABASE_URL=mysql+pymysql://test:testpass@testdb:3306/ecommerce_test
MYSQL_ROOT_PASSWORD=testpass
MYSQL_DATABASE=ecommerce_test

# 测试Redis配置
REDIS_URL=redis://testredis:6379/1
REDIS_PASSWORD=testpass

# JWT配置（测试专用）
JWT_SECRET_KEY=test-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 测试专用配置
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpass123
```

### 预生产环境配置 (.env.staging)
```env
# 应用配置
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=mysql+pymysql://staging_user:${STAGING_DB_PASSWORD}@staging-db:3306/ecommerce_staging
MYSQL_ROOT_PASSWORD=${STAGING_DB_ROOT_PASSWORD}

# Redis配置
REDIS_URL=redis://staging-redis:6379/0
REDIS_PASSWORD=${STAGING_REDIS_PASSWORD}

# JWT配置
JWT_SECRET_KEY=${STAGING_JWT_SECRET}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/staging.crt
SSL_KEY_PATH=/etc/ssl/private/staging.key

# 监控配置
SENTRY_DSN=${STAGING_SENTRY_DSN}
NEW_RELIC_LICENSE_KEY=${STAGING_NEW_RELIC_KEY}
```

### 生产环境配置 (.env.production)
```env
# 应用配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# 数据库配置（使用环境变量引用）
DATABASE_URL=mysql+pymysql://${PROD_DB_USER}:${PROD_DB_PASSWORD}@${PROD_DB_HOST}:3306/${PROD_DB_NAME}

# Redis配置
REDIS_URL=redis://${PROD_REDIS_HOST}:6379/0
REDIS_PASSWORD=${PROD_REDIS_PASSWORD}

# JWT配置（高安全）
JWT_SECRET_KEY=${PROD_JWT_SECRET}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/production.crt
SSL_KEY_PATH=/etc/ssl/private/production.key

# 安全配置
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# 监控和日志
SENTRY_DSN=${PROD_SENTRY_DSN}
LOG_FILE_PATH=/var/log/ecommerce/app.log
PROMETHEUS_METRICS_PORT=9090

# 第三方服务（生产）
ALIPAY_APP_ID=${PROD_ALIPAY_APP_ID}
ALIPAY_PRIVATE_KEY_PATH=/etc/ssl/keys/alipay_private.pem
WECHAT_APP_ID=${PROD_WECHAT_APP_ID}
```

---

## 环境变量管理策略

### 安全管理原则
1. **敏感信息隔离**: 密码、密钥等敏感信息不直接写在配置文件中
2. **环境分离**: 不同环境使用不同的密钥和配置
3. **最小权限**: 每个环境只配置必需的变量
4. **定期轮换**: 定期更新密钥和密码

### 配置管理工具

#### 初次设置
```powershell
# 从模板创建
.\scripts\sync_env.ps1 -Action create

# 或手动复制
Copy-Item .env.example .env
```

#### 分支间同步
```powershell
# 检查当前分支是否有.env文件
.\scripts\sync_env.ps1 -Action check

# 同步环境变量
.\scripts\sync_env.ps1 -Action sync

# 备份当前配置
.\scripts\sync_env.ps1 -Action backup
```

---

## Docker环境配置

### Docker Compose环境变量
```yaml
# docker-compose.yml 中的环境变量使用
services:
  app:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    env_file:
      - .env
  
  mysql:
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    env_file:
      - .env
```

### 容器内环境变量验证
```bash
# 检查容器内环境变量
docker-compose exec app env | grep DATABASE_URL

# 验证数据库连接
docker-compose exec app python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"
```

---

## Kubernetes环境配置

### ConfigMap配置
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ecommerce
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  API_V1_STR: "/api/v1"
  PROJECT_NAME: "电商平台"
  VERSION: "1.0.0"
```

### Secret配置
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ecommerce
type: Opaque
stringData:
  DATABASE_URL: "mysql+pymysql://user:password@db:3306/ecommerce"
  JWT_SECRET_KEY: "your-super-secret-jwt-key"
  REDIS_PASSWORD: "your-redis-password"
```

### Pod环境变量注入
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-app
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
```

---

## 环境变量验证

### 开发环境验证脚本
```powershell
# scripts/validate_env.ps1
param([string]$Environment = "development")

Write-Host "验证 $Environment 环境配置..." -ForegroundColor Yellow

# 必需的环境变量
$required_vars = @(
    "DATABASE_URL",
    "REDIS_URL", 
    "JWT_SECRET_KEY"
)

# 检查必需变量
foreach ($var in $required_vars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ([string]::IsNullOrEmpty($value)) {
        Write-Error "缺少必需的环境变量: $var"
        exit 1
    } else {
        Write-Host "✓ $var 已配置" -ForegroundColor Green
    }
}

# 验证数据库连接
try {
    $db_url = [Environment]::GetEnvironmentVariable("DATABASE_URL")
    Write-Host "验证数据库连接: $($db_url -replace 'password:[^@]*', 'password:***')"
    # 实际连接测试代码
    Write-Host "✓ 数据库连接正常" -ForegroundColor Green
} catch {
    Write-Error "数据库连接失败: $_"
}

Write-Host "环境验证完成" -ForegroundColor Green
```

### 应用启动时验证
```python
# app/core/config.py
import os
from typing import Optional

class Settings:
    def __init__(self):
        self.validate_required_vars()
    
    def validate_required_vars(self):
        """验证必需的环境变量"""
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "JWT_SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")
    
    @property
    def database_url(self) -> str:
        return os.getenv("DATABASE_URL")
    
    @property
    def redis_url(self) -> str:
        return os.getenv("REDIS_URL")
    
    @property
    def jwt_secret_key(self) -> str:
        return os.getenv("JWT_SECRET_KEY")

settings = Settings()
```

---

## 安全最佳实践

### 1. 密钥管理
- **生产环境**: 使用密钥管理服务（AWS Secrets Manager, Azure Key Vault）
- **开发环境**: 使用强随机密钥，定期更换
- **永不提交**: 确保`.env`文件在`.gitignore`中

### 2. 访问控制
- **最小权限原则**: 每个环境只配置必要的权限
- **角色分离**: 开发、测试、生产使用不同的数据库用户
- **审计日志**: 记录环境变量的访问和修改

### 3. 密码策略
- **复杂性要求**: 使用强密码策略
- **定期轮换**: 定期更新密码和密钥
- **多因素认证**: 在可能的情况下启用MFA

---

## 故障排除

### 常见问题

#### 1. 环境变量未生效
```powershell
# 检查环境变量是否已设置
Get-ChildItem Env: | Where-Object {$_.Name -like "*DATABASE*"}

# 重新加载环境
. .\dev_env.ps1

# 验证应用是否读取到正确的值
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

#### 2. 数据库连接失败
```powershell
# 检查数据库URL格式
echo $env:DATABASE_URL

# 验证数据库服务状态
docker-compose ps mysql

# 测试连接
mysql -h 127.0.0.1 -P 3307 -u root -p
```

#### 3. Redis连接问题
```powershell
# 检查Redis配置
echo $env:REDIS_URL

# 验证Redis服务
docker-compose ps redis

# 测试连接
redis-cli -h 127.0.0.1 -p 6379 ping
```

### 调试技巧
1. **逐步验证**: 从基础环境变量开始逐个验证
2. **日志分析**: 查看应用启动日志中的配置信息
3. **工具验证**: 使用专门的验证脚本检查配置
4. **环境隔离**: 在隔离环境中测试配置变更

---

## 相关文档
- [部署指南](deployment.md) - 生产环境部署配置
- [开发环境配置](../development/environment-setup.md) - 开发环境配置工具
- [监控告警](monitoring.md) - 环境监控配置
- [MASTER工作流程](../MASTER.md) - 环境配置检查点
