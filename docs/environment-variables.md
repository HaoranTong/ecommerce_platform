# 环境变量管理指南

## 概述

本项目使用`.env`文件管理环境变量，以确保配置的灵活性和安全性。

## 文件说明

- `.env` - 实际环境变量文件（不被Git跟踪）
- `.env.example` - 环境变量模板文件（被Git跟踪）
- `scripts/sync_env.ps1` - 环境变量同步工具

## 初次设置

### 1. 创建.env文件

```powershell
# 从模板创建
.\scripts\sync_env.ps1 -Action create

# 或手动复制
Copy-Item .env.example .env
```

### 2. 修改配置

编辑`.env`文件，根据你的环境修改以下配置：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:你的密码@localhost:3307/ecommerce_db

# JWT密钥（重要：生产环境必须修改）
JWT_SECRET_KEY=你的安全密钥

# 其他配置...
```

## 分支间同步

### 问题
由于`.env`文件不被Git跟踪，切换分支时可能丢失环境变量配置。

### 解决方案

#### 方法1：使用同步脚本
```powershell
# 检查当前分支是否有.env文件
.\scripts\sync_env.ps1 -Action check

# 从main分支复制.env文件
.\scripts\sync_env.ps1 -Action copy -FromBranch main

# 从模板重新创建
.\scripts\sync_env.ps1 -Action create
```

#### 方法2：手动备份恢复
```powershell
# 切换分支前备份
Copy-Item .env .env.backup

# 切换分支后恢复
Copy-Item .env.backup .env
```

#### 方法3：全局配置
将环境变量配置放在系统环境变量或用户配置文件中。

## 启动脚本说明

`start.ps1`脚本会按以下优先级加载环境变量：

1. **读取.env文件**（如果存在）
2. **使用默认值**（如果.env不存在）

### 启动选项

```powershell
# 默认前台启动
.\start.ps1

# 后台启动
.\start.ps1 -Background

# 启动时运行数据库迁移
.\start.ps1 -migrate

# 组合使用
.\start.ps1 -Background -migrate
```

## 最佳实践

### 1. 安全性
- ✅ 永远不要提交`.env`文件到Git
- ✅ 生产环境使用强密码和安全密钥
- ✅ 定期更新`.env.example`模板

### 2. 团队协作
- ✅ 更新`.env.example`时通知团队成员
- ✅ 在项目文档中说明必需的环境变量
- ✅ 提供不同环境的配置示例

### 3. 开发流程
- ✅ 新分支创建后立即检查环境变量
- ✅ 功能开发时考虑是否需要新的环境变量
- ✅ 合并前确保`.env.example`是最新的

## 常见问题

### Q: 切换分支后应用无法启动？
A: 可能是`.env`文件丢失，运行 `.\scripts\sync_env.ps1 -Action check` 检查。

### Q: 如何添加新的环境变量？
A: 
1. 在`.env`中添加变量
2. 更新`.env.example`模板
3. 在应用代码中使用变量
4. 更新文档

### Q: 生产环境如何管理环境变量？
A: 建议使用以下方式之一：
- 服务器系统环境变量
- Docker环境变量
- 配置管理系统（如Consul、etcd）
- 云平台环境变量服务

## 环境变量参考

### 数据库
- `DATABASE_URL` - 数据库连接URL
- `ALEMBIC_DSN` - Alembic迁移连接（通常与DATABASE_URL相同）

### 缓存
- `REDIS_URL` - Redis连接URL

### 认证
- `JWT_SECRET_KEY` - JWT签名密钥
- `JWT_ALGORITHM` - JWT算法（默认HS256）
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token过期时间

### 应用
- `DEBUG` - 调试模式开关
- `APP_NAME` - 应用名称
- `APP_VERSION` - 应用版本
