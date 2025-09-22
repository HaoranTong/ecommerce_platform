# 完整环境配置和管理指南

## 📋 文档说明

本文档整合了开发环境配置和运维环境管理的完整指南。

**文档整合说明**:
- **来源**: 合并自 `docs/development/environment-setup.md` + `docs/operations/environment.md`
- **职责**: 统一的环境配置和管理指南
- **使用者**: 开发人员、运维人员、新成员

---

## 🎯 快速导航

### 开发人员使用
- [本地开发环境配置](#本地开发环境配置) - 首次环境搭建
- [开发工具配置](#开发工具配置) - VS Code、Git等工具配置
- [日常开发脚本](#日常开发脚本) - 开发环境维护

### 运维人员使用  
- [多环境配置管理](#多环境配置管理) - 测试、预生产、生产环境
- [环境变量安全](#环境变量安全) - 敏感信息管理
- [部署环境配置](#部署环境配置) - 部署相关环境设置

---

## 🔧 本地开发环境配置

> **目标用户**: 开发人员首次环境搭建
> **使用场景**: 新员工入职、开发环境重置

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **内存**: 8GB RAM (推荐16GB)  
- **存储**: 50GB可用空间
- **网络**: 稳定的互联网连接

### Python环境配置
```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.\.venv\Scripts\Activate.ps1

# 激活虚拟环境 (Linux/Mac)  
source .venv/bin/activate

# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 开发环境变量配置
```bash
# .env (开发环境)
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=mysql+pymysql://root:rootpass@localhost:3307/ecommerce_dev
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
```

---

## 💻 开发工具配置

### VS Code IDE配置
详见 [工具使用手册](../tools/scripts-usage-manual.md) 相关章节

### Docker开发环境
```yaml
# docker-compose.dev.yml  
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: ecommerce_dev
    ports:
      - "3307:3306"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## 🏢 多环境配置管理

> **目标用户**: 运维人员、部署管理员
> **使用场景**: 环境部署、配置管理

### 环境层级
```
开发环境 (Development) → 本地开发
测试环境 (Testing) → 自动化测试
预生产环境 (Staging) → 发布前验证  
生产环境 (Production) → 用户服务
```

### 测试环境配置
```env
ENVIRONMENT=testing
DEBUG=false
DATABASE_URL=mysql+pymysql://test:testpass@testdb:3306/ecommerce_test
REDIS_URL=redis://testredis:6379/1
JWT_SECRET_KEY=test-secret-key
```

### 生产环境配置
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=mysql+pymysql://${PROD_DB_USER}:${PROD_DB_PASSWORD}@${PROD_DB_HOST}:3306/${PROD_DB_NAME}
REDIS_URL=redis://${PROD_REDIS_HOST}:6379/0
JWT_SECRET_KEY=${PROD_JWT_SECRET}
SSL_CERT_PATH=/etc/ssl/certs/production.crt
```

---

## 🔒 环境变量安全管理

### 敏感信息处理
- **开发环境**: 使用默认值，.env文件本地管理
- **测试环境**: CI/CD系统注入环境变量
- **生产环境**: 容器编排系统或密钥管理服务

### 安全最佳实践
1. **永不提交**: .env文件永不提交到版本控制
2. **模板管理**: 维护.env.example模板文件
3. **权限控制**: 生产环境变量仅运维人员可访问
4. **定期轮换**: 定期更换JWT密钥等敏感信息

---

## 🚀 日常开发脚本

### 环境配置脚本 (dev_env.ps1)
```powershell
# 在项目根目录执行
. .\dev_env.ps1
```
**功能**: 自动激活虚拟环境、检查Docker服务、设置环境变量

### 开发工具脚本 (dev_tools.ps1)  
```powershell
.\dev_tools.ps1 check-db     # 检查数据库连接
.\dev_tools.ps1 migrate      # 执行数据库迁移
.\dev_tools.ps1 start-api    # 启动API服务
```

**详细使用说明**: 参见 [工具使用手册](../tools/scripts-usage-manual.md)

---

## 🆘 故障排除

### 常见问题
详见 [工具故障排除](../tools/troubleshooting.md) 相关章节

---

## 🔗 相关文档
- **[工具使用手册](../tools/scripts-usage-manual.md)** - 开发脚本详细说明
- **[部署指南](deployment.md)** - 生产环境部署流程  
- **[故障排除](../tools/troubleshooting.md)** - 环境问题解决方案
- **[测试工具](../tools/testing-tools.md)** - 测试环境配置

---
*更新时间: 2025-09-22 | 版本: v1.0 (合并版本)*