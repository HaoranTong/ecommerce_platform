<!--version info: v2.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions.md,project-structure-standards.md-->

# 部署标准规范 (Deployment Standards)

## 概述

本文档定义容器化部署、环境配置和运维管道的具体标准，属于L2领域标准。基于项目实际的docker-compose.yml和start.ps1设计。

## 依赖标准

本标准依赖以下L1核心标准：
- `naming-conventions.md` - 容器、服务、环境变量命名规范
- `project-structure-standards.md` - 部署文件结构和组织标准

## 具体标准

### 容器化标准

**Docker镜像标准**:
```yaml
# 基础镜像选择
- Python服务: python:3.11-slim
- 数据库: postgres:15-alpine  
- 缓存: redis:7-alpine
```

**容器命名规范**:
```yaml
services:
  ecommerce_app:     # 主应用容器
  ecommerce_db:      # 数据库容器  
  ecommerce_redis:   # 缓存容器
```

### 环境配置标准

**环境变量分类**:
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@host:5432/db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_platform
DB_USER=ecommerce_user

# 应用配置  
SECRET_KEY=your-secret-key-here
DEBUG=false
ENVIRONMENT=production

# 外部服务
REDIS_URL=redis://localhost:6379/0
```

**docker-compose.yml结构标准**:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment: {}
    volumes: []
    depends_on: []
    
  database:
    image: postgres:15
    environment: {}
    volumes: []
    
  cache:  
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### 启动脚本标准

**PowerShell脚本格式 (start.ps1)**:
```powershell
#!/usr/bin/env pwsh

# 标准脚本头
param([string]$Environment = "development")

# 环境检查
Write-Host "启动环境: $Environment" -ForegroundColor Green

# Docker Compose启动
docker-compose up -d

# 健康检查
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep 10

# 验证服务状态
docker-compose ps
```

### 部署流水线标准

**本地开发环境**:
1. 环境准备: `scripts/setup_test_env.ps1`
2. 服务启动: `start.ps1`  
3. 数据库迁移: `alembic upgrade head`
4. 健康检查: `http://localhost:8000/health`

**生产环境部署**:
1. 镜像构建: `docker build -t ecommerce:latest .`
2. 环境变量配置: `.env.production` 
3. 服务编排: `docker-compose -f docker-compose.prod.yml up -d`
4. 监控启动: 日志收集、性能监控、告警配置

### 监控和日志标准

**日志格式标准**:
```json
{
  "timestamp": "2025-09-23T10:30:00Z",
  "level": "INFO",
  "service": "ecommerce_app",
  "message": "Request processed successfully",
  "request_id": "req-123456",
  "user_id": "user-789"
}
```

**健康检查端点**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "redis": "connected"
        }
    }
```

### 安全配置标准

**网络安全**:
- 容器间网络隔离
- 敏感端口不对外暴露
- SSL/TLS证书配置

**数据安全**:
- 数据库连接加密
- 环境变量敏感信息保护
- 定期安全更新

### 性能优化标准

**资源限制**:
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**缓存策略**:
- Redis缓存配置优化
- 静态文件CDN部署
- 数据库查询优化

### 维护

本标准需要在以下情况更新：
1. Docker镜像版本升级
2. 新增外部服务依赖
3. 环境配置变更
4. 安全要求更新

相关文件：
- `docker-compose.yml` - 服务编排配置
- `start.ps1` - 本地启动脚本  
- `.env.*` - 环境变量配置
- `scripts/setup_test_env.ps1` - 环境准备脚本