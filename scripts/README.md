<!--
文档说明：
- 内容：自动化脚本目录说明和使用指南
- 使用方法：开发者了解和使用项目自动化脚本
- 更新方法：新增或修改脚本时更新
- 引用关系：被docs/usage/scripts.md引用
- 更新频率：脚本变化时
-->

# 🤖 自动化脚本目录

项目开发和运维过程中使用的PowerShell自动化脚本集合。

## 📁 脚本列表

| 脚本文件 | 功能描述 | 使用场景 |
|---------|----------|----------|
| `feature_finish.ps1` | 完成功能开发的自动化流程 | 功能开发完成时 |
| `log_status.ps1` | 记录项目状态日志 | 每日状态更新 |
| `release_to_main.ps1` | 发布到主分支的自动化流程 | 版本发布时 |
| `smoke_test.ps1` | 冒烟测试自动化脚本 | 部署后验证 |
| `sync_env.ps1` | 环境同步脚本 | 环境配置更新 |
| `_smoke_cert.py` | 冒烟测试证书验证工具 | SSL证书验证 |

## 🚀 使用方法

### 前置条件
1. **PowerShell 5.1+** 或 **PowerShell Core 7+**
2. **Git** 命令行工具
3. **Python 3.8+** (用于 _smoke_cert.py)
4. 项目根目录执行权限

### 基本用法

#### 1. 功能开发完成
```powershell
# 在项目根目录执行
.\scripts\feature_finish.ps1
```

#### 2. 记录状态日志
```powershell
# 记录当前开发状态
.\scripts\log_status.ps1
```

#### 3. 发布到主分支
```powershell
# 发布当前分支到main
.\scripts\release_to_main.ps1
```

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
