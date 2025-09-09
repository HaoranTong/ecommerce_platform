# 开发工具使用指南

## 概述

本项目提供了标准化的开发工具，用于简化日常开发、测试和维护工作。主要包含两个核心脚本：

## 工具清单

### 1. dev_env.ps1 - 开发环境配置脚本

#### 功能描述
统一配置开发环境，包括虚拟环境激活、环境变量设置、Docker服务检查和API服务状态检查。

#### 使用方法
```powershell
# 在项目根目录执行（注意前面的点和空格）
. .\dev_env.ps1
```

#### 执行流程
1. **虚拟环境检查**: 自动检查并激活 `.venv` 虚拟环境
2. **环境变量设置**: 设置数据库连接、Redis连接等必要环境变量
3. **Docker服务检查**: 检查MySQL和Redis容器运行状态，必要时自动启动
4. **API服务检查**: 检查FastAPI服务运行状态，显示进程信息

#### 配置项说明
- `DATABASE_URL`: MySQL数据库连接URL（根据docker-compose.yml配置）
- `MYSQL_ROOT_PASSWORD`: MySQL root用户密码
- `REDIS_URL`: Redis连接URL
- `SECRET_KEY`: JWT Token签名密钥
- `ALGORITHM`: JWT加密算法
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token过期时间

### 2. dev_tools.ps1 - 开发工具集

#### 功能描述
提供常用的开发任务命令，包括数据库检查、迁移、测试执行、服务管理等。

#### 使用方法
```powershell
.\dev_tools.ps1 <命令>
```

#### 可用命令

##### check-db - 检查数据库表结构
```powershell
.\dev_tools.ps1 check-db
```
- **功能**: 连接数据库并显示Product表的字段结构
- **用途**: 验证数据库迁移是否成功，检查表字段定义

##### migrate - 执行数据库迁移
```powershell
.\dev_tools.ps1 migrate
```
- **功能**: 执行Alembic数据库迁移到最新版本
- **用途**: 应用数据库schema变更

##### test-cart - 执行购物车测试
```powershell
.\dev_tools.ps1 test-cart
```
- **功能**: 运行完整的购物车功能测试套件
- **用途**: 验证购物车API的所有功能

##### start-api - 启动API服务
```powershell
.\dev_tools.ps1 start-api
```
- **功能**: 启动FastAPI开发服务器
- **特点**: 
  - 自动检查是否已有服务运行
  - 提供重启选项
  - 使用热重载模式

##### stop-api - 停止API服务
```powershell
.\dev_tools.ps1 stop-api
```
- **功能**: 停止所有运行中的FastAPI服务进程
- **用途**: 清理运行环境

##### reset-env - 重置开发环境
```powershell
.\dev_tools.ps1 reset-env
```
- **功能**: 完整重置开发环境
- **包含**: 
  - 停止API服务
  - 重启Docker容器
  - 重新加载环境配置

### 3. test_cart_system.ps1 - 购物车测试脚本

#### 功能描述
完整的购物车系统端到端测试，覆盖所有购物车相关API功能。

#### 测试覆盖范围
1. **用户注册和登录**
2. **获取空购物车状态**
3. **获取可用商品列表**
4. **添加商品到购物车**
5. **再次添加相同商品（数量累加）**
6. **获取购物车详情**
7. **更新购物车商品数量**
8. **获取购物车统计**
9. **移除购物车商品**
10. **验证购物车状态**
11. **测试清空购物车功能**
12. **测试边界情况**（库存不足、无效商品等）

#### 使用方法
```powershell
# 直接执行
.\test_cart_system.ps1

# 或通过开发工具执行
.\dev_tools.ps1 test-cart
```

## 标准开发工作流程

### 每日开发启动流程
```powershell
# 1. 配置开发环境
. .\dev_env.ps1

# 2. 检查数据库状态
.\dev_tools.ps1 check-db

# 3. 如需要，执行数据库迁移
.\dev_tools.ps1 migrate

# 4. 启动API服务（如未运行）
.\dev_tools.ps1 start-api
```

### 功能开发和测试流程
```powershell
# 1. 开发代码后测试购物车功能
.\dev_tools.ps1 test-cart

# 2. 检查数据库变更
.\dev_tools.ps1 check-db

# 3. 如需重置环境
.\dev_tools.ps1 reset-env
```

### 问题排查流程
```powershell
# 1. 重置环境
.\dev_tools.ps1 reset-env

# 2. 重新配置
. .\dev_env.ps1

# 3. 检查数据库连接
.\dev_tools.ps1 check-db

# 4. 重新测试
.\dev_tools.ps1 test-cart
```

## 环境要求

### 软件依赖
- Windows 11
- PowerShell 5.1+
- Python 3.9+
- Docker Desktop
- MySQL 8.0 (Docker)
- Redis 7 (Docker)

### 必要文件
- `.venv/` - Python虚拟环境
- `docker-compose.yml` - Docker服务配置
- `alembic.ini` - 数据库迁移配置
- `requirements.txt` - Python依赖清单

## 故障排除

### 常见问题

#### 1. 虚拟环境激活失败
```powershell
# 检查虚拟环境是否存在
Test-Path ".venv\Scripts\Activate.ps1"

# 重新创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 2. 数据库连接失败
```powershell
# 检查Docker容器状态
docker ps --filter "name=mysql"

# 重启Docker服务
docker-compose down
docker-compose up -d
```

#### 3. API服务端口冲突
```powershell
# 停止所有Python进程
.\dev_tools.ps1 stop-api

# 检查端口占用
netstat -ano | findstr :8000
```

#### 4. 环境变量未生效
```powershell
# 重新加载环境配置
. .\dev_env.ps1

# 检查环境变量
echo $env:DATABASE_URL
```

## 最佳实践

### 1. 每次开发前
- 总是先执行 `. .\dev_env.ps1` 配置环境
- 使用 `.\dev_tools.ps1 check-db` 验证数据库状态

### 2. 代码修改后
- 使用 `.\dev_tools.ps1 test-cart` 验证功能
- 如有数据库变更，执行 `.\dev_tools.ps1 migrate`

### 3. 遇到问题时
- 首先尝试 `.\dev_tools.ps1 reset-env` 重置环境
- 查看错误信息确定具体问题
- 按照故障排除指南逐步解决

### 4. 团队协作
- 所有开发者使用相同的工具脚本
- 确保docker-compose.yml和环境配置一致
- 提交代码前执行完整测试
