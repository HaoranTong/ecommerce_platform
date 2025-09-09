# 技术文档索引（定制化电商平台）

本目录列出当前主要技术方案与参考文档。请以下列主文档为基准并在迭代中持续更新。

主文档：

- `docs/technical/定制化电商平台功能需求方案-1.0.md` — 功能需求定稿（由用户维护）。
- `docs/technical/定制化电商平整体实施方案-1.0.md` — 整体实施计划（由用户维护）。

核心契约文件：

- `docs/openapi.yaml` — API 契约规范（v1.1.0，完整电商核心 API）
- `docs/event-schemas/` — 事件 Schema 注册表（JSON Schema 格式）

开发状态：

- `docs/status/status.md` — 项目开发状态和里程碑记录
- `docs/technical/architecture_changelog.md` — 架构变更历史记录

**最新更新 (2025-09-09)**:
- ✅ 产品管理完整CRUD功能实现 
- ✅ 分类管理层级功能实现
- ✅ 数据库连接和迁移问题彻底解决
- ✅ Docker开发环境标准化配置
- ✅ API功能验证和测试数据创建
- `docs/technical/directory_standards.md` — 目录架构与命名规范
- `docs/technical/data_models.md` — 数据模型架构文档（v1.0，电商核心模型）
- `docs/technical/automation_scripts.md` — 自动化脚本使用指南（v1.1.1）

架构状态：

- **当前版本**: v1.1.1 - 自动化脚本修复与分支架构优化
- **后端框架**: FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2
- **数据库**: MySQL 8.0 (Docker 容器)
- **缓存**: Redis 7 (Docker 容器)  
- **迁移状态**: 0001_initial.py (干净的电商核心模型迁移)
- **兼容性**: 已完成 Pydantic v2 全面兼容
- **自动化**: PowerShell 脚本修复完成，独立日志分支架构建立


辅助文档与状态：

- `docs/status/status.md` — 实时工作状态与每日更新（用于记录每日进展、阻碍与下一步；仅包含短时态信息、行动项与决策日志）。
- `docs/status/automation_logs.md` — 自动化操作日志（仅存在于 `status/logs` 分支，记录发布、合并等自动化操作）
- `scripts/` — PowerShell 自动化脚本集
  - `start.ps1` — 统一启动脚本（Docker + FastAPI 服务）
  - `scripts/release_to_main.ps1` — 自动化发布脚本（dev → main）
  - `scripts/smoke_test.ps1` — API 烟雾测试脚本
  - `scripts/log_status.ps1` — 状态日志记录脚本

建议工作流程：
- 所有接口/事件/DDL 变更先更新对应文档并在 PR 中标注变更点。
- 对重要变更（OpenAPI / DB schema / 事件 schema）使用文件版本号并保留历史副本。


若需我将主文档拆分成更细分的 OpenAPI / DDL / 事件 Schema 文件，请列出目标清单，我会逐条生成并保存到 `docs/technical/`。

文档体系说明（简要）:
- `docs/technical/index.md` 作为索引与指南，列出主文档与长期参考资料。由产品或架构负责人维护文档结构变更。
- `docs/technical/` 下的主技术文档（OpenAPI、DDL、实施方案）保存正式版本与历史，任何变更应在 PR 中同时更新 `index.md` 的版本引用。
- `docs/status/status.md` 仅用于日常状态与进展记录，不作为规范或设计的唯一信源。长期或规范性变更应写入 `docs/technical/` 下对应文件并在 `status.md` 中引用变更条目。
- 避免冗余：请不要在 `status.md` 中复制设计规范的全文，改为摘要 + 链接。
