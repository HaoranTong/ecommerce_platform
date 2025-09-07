# 发布与回滚建议

本文件描述推荐的 CI gate、回滚策略与如何在合并时保持 `docs/status/status.md` 的自动记录。

1. CI Gate（推荐）
   - 在将 `dev` 合并到 `main` 前，CI 应在 `dev` 上完成全部测试（单元、集成、烟雾）。
   - 只有当 CI 返回绿色且关键端点烟雾测试通过后，才允许自动合并到 `main`（可以由 release 脚本或 GitHub Action 执行）。

2. 回滚策略（快速回滚）
   - 当主分支在 smoke 测试或生产运行中发现关键缺陷：
     1. 使用 `git revert <merge-commit>` 还原主分支上的合并提交并推送。
     2. 在 `status.md` 记录回滚事件与原因，并通知相关人员。

3. 自动化记录（使用 `scripts/log_status.ps1`）
   - 在 release 脚本或 CI job 的最后一步，调用：
     - `pwsh .\scripts\log_status.ps1 -Message "Merged dev into main" -Files "docs/technical/release_and_rollback.md" -PrUrl "$PR_URL" -Author "release-bot"`
   - 该脚本会追加一条结构化的记录到 `docs/status/status.md`，便于审计与回溯。

4. 手动检查点
   - 在合并到 `main` 之前，人工确认：重要变更（DB、事件 schema、兼容性）是否已记录在 `docs/technical/`。

5. 示例流程
   - 开发完成 feature → PR 到 `dev` → CI 在 `dev` 上运行 → 在 PR 合并时，CI/脚本调用 `log_status.ps1` 追加记录 → 等 CI 绿灯并通过烟雾后，release 脚本合并 `dev` 到 `main` 并再次调用 `log_status.ps1`。

此策略保证文档记录自动化、变更有迹可循，同时避免将大量规范文本写入 `status.md`。如需我将 `scripts/log_status.ps1` 集成到现有 `scripts/release_to_main.ps1`，我可以继续修改并提交。 
