# 脚本使用说明（中文）

下面列出仓库中常用的本地自动化脚本，包含示例命令，可直接复制粘贴到 PowerShell（pwsh）中运行。

## scripts/feature_finish.ps1
用途：完成一个本地 feature 分支的合并到 `dev` 并运行 smoke tests；支持 dry-run（不推送远端）。

常用参数：
- -FeatureBranch <name>：要完成的 feature 分支（可省略，脚本会尝试从当前分支推断）。
- -NoPush：只在本地合并和测试，不推送到远端（用于演练或 CI 回放）。

示例：

# 直接在 feature 分支上完成并推送到 origin/dev
pwsh ./scripts/feature_finish.ps1 -FeatureBranch feature/awesome

# 在本地演练合并但不推送远端
pwsh ./scripts/feature_finish.ps1 -FeatureBranch feature/awesome -NoPush


## scripts/release_to_main.ps1
用途：将 `dev` 合并到 `main`（在本地执行），支持 dry-run 和回滚。

常用参数：
- -DryRun：仅生成合并计划（git --no-commit --no-ff），不会提交。用于审阅将要发生的变更。
- -RunNow：在确认后执行真正的合并、测试并推送 `main` 到远端。

示例：

# 生成合并计划（仅查看）
pwsh ./scripts/release_to_main.ps1 -DryRun

# 执行合并并在本地测试，测试通过后推送 main
pwsh ./scripts/release_to_main.ps1 -RunNow


## 额外说明
- 本仓库设计为单人开发友好流程：feature -> dev -> main。CI 在 `dev` 上运行测试并创建 PR（dev -> main），但合并 `main` 的动作建议在本地由开发者执行以便回退和审查。
- 若需要，脚本可以配合 `GIT` 环境变量或为企业流程增加 `--no-ff`/签名等参数；当前实现保持简单以便易于阅读和调试。

若需把这些文档同步到仓库其它地方或添加英文版，请告诉我能否继续提交并推送变更。
