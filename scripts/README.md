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

## 🔄 开发流程脚本

### feature_finish.ps1
**用途**：完成一个本地 feature 分支的合并到 `dev` 并运行 smoke tests

**常用参数**：
- `-FeatureBranch <name>`：要完成的 feature 分支（可省略，脚本会尝试从当前分支推断）
- `-NoPush`：只在本地合并和测试，不推送到远端（用于演练或 CI 回放）

**示例**：
```powershell
# 直接在 feature 分支上完成并推送到 origin/dev
.\scripts\feature_finish.ps1 -FeatureBranch feature/awesome

# 在本地演练合并但不推送远端
.\scripts\feature_finish.ps1 -FeatureBranch feature/awesome -NoPush
```

### release_to_main.ps1
**用途**：将 `dev` 合并到 `main`（在本地执行），支持 dry-run 和回滚

**常用参数**：
- `-DryRun`：仅生成合并计划（git --no-commit --no-ff），不会提交。用于审阅将要发生的变更
- `-RunNow`：在确认后执行真正的合并、测试并推送 `main` 到远端

**示例**：
```powershell
# 生成合并计划（仅查看）
.\scripts\release_to_main.ps1 -DryRun

# 执行合并并在本地测试，测试通过后推送 main
.\scripts\release_to_main.ps1 -RunNow
```

**设计说明**：
- 本仓库设计为单人开发友好流程：feature → dev → main
- CI 在 `dev` 上运行测试并创建 PR（dev → main），但合并 `main` 的动作建议在本地由开发者执行以便回退和审查
- 脚本内置回滚机制，测试失败时自动恢复到合并前状态

### smoke_test.ps1
**用途**：执行系统烟雾测试，验证关键功能是否正常

**示例**：
```powershell
# 运行烟雾测试
.\scripts\smoke_test.ps1
```

### log_status.ps1
**用途**：记录开发状态和重要操作到项目日志

**常用参数**：
- `-Message <string>`：要记录的消息
- `-Files <string>`：相关文件列表
- `-Author <string>`：操作者

**示例**：
```powershell
# 记录状态
.\scripts\log_status.ps1 -Message "完成功能开发" -Files "app/api/routes.py" -Author "developer"
```

## ⚠️ 注意事项

1. **执行权限**: 确保有PowerShell脚本执行权限 (`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`)
2. **环境检查**: 脚本会检查必要的依赖和环境
3. **备份**: 重要操作前脚本会自动备份
4. **日志**: 所有操作都有详细日志记录
5. **回滚**: 支持操作回滚的脚本会提供回滚选项

## 🔗 相关文档

- [开发工作流程](../docs/development/workflow.md)
- [环境配置说明](../docs/operations/environment.md)
- [测试指南](../docs/development/testing.md)
