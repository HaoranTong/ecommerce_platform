# 自动化脚本使用指南

## 概述

本文档描述电商平台项目的 PowerShell 自动化脚本使用方法和架构设计。

## 脚本架构

### 分支日志架构

```
main / dev (主开发分支)
├── docs/status/status.md (人工状态记录)
└── (不包含 automation_logs.md)

status/logs (独立日志分支)
├── docs/status/status.md (从主分支同步)
├── docs/status/automation_logs.md (自动化日志)
└── scripts/ (脚本修复版本)
```

**设计原则**:
- 自动化日志与人工状态记录完全分离
- 避免自动化操作在主开发分支产生文件变更
- 防止发布脚本与日志脚本的死循环冲突

## 核心脚本

### 1. start.ps1 - 统一启动脚本

**功能**: 一键启动 Docker 服务和 FastAPI 应用

**使用方法**:
```powershell
# 默认后台模式（推荐）
.\start.ps1

# 前台模式（调试用）
.\start.ps1 -Foreground
```

**主要功能**:
- 检查并启动 Docker 服务
- 启动 MySQL 和 Redis 容器
- 等待数据库服务就绪
- 激活 Python 虚拟环境
- 启动 FastAPI 应用
- 后台模式避免终端占用

### 2. scripts/release_to_main.ps1 - 自动化发布脚本

**功能**: 自动化 dev → main 分支发布流程

**使用方法**:
```powershell
# 确保在 dev 分支上有待发布的更改
git checkout dev
git add .
git commit -m "feature: 新功能描述"

# 运行发布脚本
.\scripts\release_to_main.ps1
```

**发布流程**:
1. 检查当前分支状态
2. 拉取最新远程更新
3. 在 dev 分支运行烟雾测试
4. 合并 dev → main
5. 推送到远程仓库（GitHub + Gitee）
6. 记录发布日志到独立分支
7. 在 main 分支运行最终验证
8. 记录完成状态

**错误处理**:
- 烟雾测试失败时自动回滚
- 合并冲突时暂停并提示手动解决
- 推送失败时显示详细错误信息

### 3. scripts/smoke_test.ps1 - API 烟雾测试

**功能**: 验证 FastAPI 应用核心功能正常

**使用方法**:
```powershell
# 直接运行
.\scripts\smoke_test.ps1

# 检查退出码
$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Output "测试通过"
} else {
    Write-Output "测试失败"
}
```

**测试内容**:
- FastAPI 服务可用性检查
- 用户创建 API 测试
- 用户列表 API 测试
- 数据库连接验证

**退出码**:
- `0`: 所有测试通过
- `1`: 测试失败

### 4. scripts/log_status.ps1 - 状态日志脚本

**功能**: 记录自动化操作日志到独立分支

**使用方法**:
```powershell
# 记录操作日志
.\scripts\log_status.ps1 -message "发布版本 v1.2.0" -branch "main"

# 记录错误日志
.\scripts\log_status.ps1 -message "部署失败：数据库连接超时" -branch "dev"
```

**参数**:
- `-message`: 日志消息内容
- `-branch`: 当前操作分支

**架构特点**:
- 日志写入独立的 `status/logs` 分支
- 不影响主开发分支的文件状态
- 自动创建和维护日志分支

## 使用场景

### 日常开发流程

1. **启动环境**:
   ```powershell
   .\start.ps1
   ```

2. **开发功能** (在 dev 分支):
   ```powershell
   git checkout dev
   # 进行代码开发...
   git add .
   git commit -m "feature: 新功能"
   ```

3. **发布到生产**:
   ```powershell
   .\scripts\release_to_main.ps1
   ```

### 测试和验证

1. **手动测试**:
   ```powershell
   .\scripts\smoke_test.ps1
   ```

2. **查看自动化日志**:
   ```powershell
   git checkout status/logs
   cat docs/status/automation_logs.md
   ```

## 故障排除

### 常见问题

1. **PowerShell 执行策略错误**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Docker 服务未启动**:
   - 确保 Docker Desktop 正在运行
   - 检查端口 3307 和 6379 是否被占用

3. **虚拟环境问题**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Git 推送失败**:
   - 检查网络连接
   - 验证 GitHub/Gitee 凭据
   - 解决可能的合并冲突

### 调试模式

所有脚本支持详细输出，可以通过查看终端输出来诊断问题：

```powershell
# 启用详细输出
$VerbosePreference = "Continue"
.\scripts\release_to_main.ps1
```

## 最佳实践

1. **定期更新**: 保持脚本和依赖项最新
2. **测试优先**: 发布前总是运行烟雾测试
3. **分支清洁**: 确保 dev 分支状态干净再发布
4. **日志查看**: 定期检查自动化日志排查问题
5. **备份恢复**: 发布失败时使用 Git 恢复到之前状态

## 版本历史

- **v1.1.1** (2025-09-08): 修复 PowerShell 语法错误，建立独立日志分支架构
- **v1.1.0** (2025-09-08): 初始脚本集成，统一启动脚本
- **v1.0.0** (2025-09-08): 基础项目结构建立
