<!--
文档说明：
- 内容：自动化脚本目录说明和使用指南
- 使用方法：开发者了解和使用项目自动化脚本
- 更新方法：新增或修改脚本时更新
- 更新频率：脚本变化时
-->

# 🤖 脚本使用指南

项目开发中使用的PowerShell自动化脚本。

## � 当前可用脚本

### 1. 快速文档检查
```powershell
.\scripts\check_docs.ps1
```
- 检查文档数量和状态
- 发现空文档
- 验证核心文件

### 2. 详细文档检查  
```powershell
.\scripts\doc_basic_check.ps1
```
- 显示所有文档详情
- 检查文档大小和结构

### 3. 环境变量管理
```powershell
# 创建.env文件
.\scripts\sync_env.ps1 -Action create

# 检查环境
.\scripts\sync_env.ps1 -Action check
```

## 🚀 快速开始

**第一次使用**:
1. 打开PowerShell，进入项目目录
2. 运行: `.\scripts\check_docs.ps1`
3. 如果出现权限错误，运行: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

**日常使用**:
- 检查项目状态: `.\scripts\check_docs.ps1`
- 设置环境: `.\scripts\sync_env.ps1 -Action create`

## ⚠️ 注意事项

- 简化脚本，避免复杂功能
- 在项目根目录运行
- 有错误就检查文件路径

#### 4. 执行冒烟测试
```powershell
# 部署后验证系统功能
.\scripts\smoke_test.ps1
```

#### 5. 同步环境配置
```powershell
# 同步开发环境配置
.\scripts\sync_env.ps1
```

#### 6. SSL证书验证
```python
# 验证SSL证书
python scripts\_smoke_cert.py
```

## ⚙️ 脚本配置

### 环境变量
大部分脚本会使用以下环境变量：
- `ECOMMERCE_ENV`: 环境标识 (dev/staging/prod)
- `DATABASE_URL`: 数据库连接字符串
- `REDIS_URL`: Redis连接字符串

### 配置文件
脚本配置存储在：
- `.env`: 环境变量配置
- `docker-compose.yml`: 容器配置
- `alembic.ini`: 数据库迁移配置

## 🔧 脚本开发规范

### 文件命名
- 功能脚本: `{功能名}.ps1`
- 工具脚本: `_{工具名}.{扩展名}`
- 测试脚本: `test_{功能名}.ps1`

### 脚本结构
```powershell
# 脚本头部说明
# 功能: 脚本功能描述
# 作者: 开发者
# 版本: 1.0.0
# 更新: 2025-09-10

# 参数定义
param(
    [string]$Environment = "dev",
    [switch]$Force
)

# 函数定义
function Write-StatusLog {
    # 函数实现
}

# 主逻辑
try {
    # 脚本主要逻辑
} catch {
    Write-Error "脚本执行失败: $_"
    exit 1
}
```

### 错误处理
- 使用 `try-catch` 处理异常
- 设置适当的退出码
- 提供清晰的错误信息

## 📊 脚本监控

### 日志记录
- 所有脚本执行都会记录到 `docs/status/daily-log.md`
- 错误日志记录到 `logs/` 目录 (如果存在)

### 执行历史
- 使用 `log_status.ps1` 记录重要操作
- Git提交记录包含脚本执行信息

## 🔗 相关文档

- [开发工作流程](../docs/development/workflow.md)
- [脚本使用指南](../docs/usage/scripts.md)
- [环境配置说明](../docs/operations/environment.md)
- [测试指南](../docs/development/testing.md)

## ⚠️ 注意事项

1. **执行权限**: 确保有PowerShell脚本执行权限
2. **环境检查**: 脚本会检查必要的依赖和环境
3. **备份**: 重要操作前脚本会自动备份
4. **日志**: 所有操作都有详细日志记录
5. **回滚**: 支持操作回滚的脚本会提供回滚选项
