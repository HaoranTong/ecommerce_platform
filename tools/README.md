---
title: "开发工具集 - 使用指南"
version: "2.0.0"
status: "active"
created: "2025-10-10"
updated: "2025-10-10"
maintainer: "开发团队"
dependencies:
  - "../docs/standards/document-management-standards.md"
  - "../docs/development/dev-env-setup.md"
labels:
  - category: tools
  - type: guide
---

# 开发工具集

> 🎯 **一站式开发工具集合**: 提供从环境搭建到测试验证的完整工具支撑

## 📋 概述

本工具集为ecommerce_platform项目提供完整的开发、测试、部署和维护工具链，确保开发流程标准化和自动化。所有工具遵循项目文档管理规范和开发标准。

## 📁 工具分类

### 🔧 环境管理工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `setup_test_env.ps1` | 测试环境配置和验证 | 项目初始化、环境变更后 | `.\tools\setup_test_env.ps1 -TestMode lite` |
| `setup_dev_env.ps1` | 开发环境初始化配置 | 新环境搭建、依赖安装 | `.\tools\setup_dev_env.ps1` |
| `check_test_env.ps1` | 环境状态快速检查 | 测试前环境确认 | `.\tools\check_test_env.ps1` |
| `dev_tools.ps1` | 开发环境工具集合 | 日常开发辅助操作 | `.\tools\dev_tools.ps1 check-db` |

### 🧪 测试执行工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `run_module_tests.ps1` | 模块测试执行 | 单个模块完整测试 | `.\tools\run_module_tests.ps1 -ModuleName user_auth` |
| `smoke_test.ps1` | API快速验证 | 功能开发后快速验证 | `.\tools\smoke_test.ps1` |
| `integration_test.ps1` | 集成测试执行 | 多模块协作验证 | `.\tools\integration_test.ps1` |
| `e2e_test_verification.py` | E2E测试验证 | 端到端测试流程验证 | `python .\tools\e2e_test_verification.py` |
| `validate_test_config.py` | 测试配置验证 | 测试环境配置检查 | `python .\tools\validate_test_config.py` |
| `validate_test_structure.py` | 测试结构验证 | 测试文件结构合规检查 | `python .\tools\validate_test_structure.py` |

### ⚡ 质量保证工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `check_quality.py` | **代码质量综合检查** | **硬编码检查、重复代码检查、质量门禁** | `python .\tools\check_quality.py --all` |
| `ai_checkpoint.ps1` | AI检查点验证 | AI开发任务完成验证 | `.\tools\ai_checkpoint.ps1 -CardType DEV-001` |

### 🔍 分析工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `model_analyzer.py` | SQLAlchemy模型结构分析 | 模型审计、测试自动化、文档生成 | `python .\tools\model_analyzer.py user_auth` |
| `api_service_mapping_analyzer.py` | API/Service映射分析 | 测试代码生成、代码审查、文档生成 | `python .\tools\api_service_mapping_analyzer.py --analyze user_auth` |
| `extract_entity_schema.py` | 模型实体结构提取 | 文档生成、数据库设计对比、测试辅助 | `python .\tools\extract_entity_schema.py ./app/modules/user_auth/models.py` |
| `extract_frontend_rules.py` | 前端规则提取 | 前端开发、自动化构建、文档同步 | `python .\tools\extract_frontend_rules.py --batch` |
| `extract_models_jsonschema.py` | 模型JSON Schema提取 | 前端表单生成、API文档、AI辅助开发 | `python .\tools\extract_models_jsonschema.py ./app/modules/user_auth/models.py > schema.json` |

### 🛠️ 维护工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `check_code_standards.ps1` | 代码规范检查 | 提交前代码审查 | `.\tools\check_code_standards.ps1` |
| `check_naming_compliance.ps1` | 命名规范检查 | 项目一致性检查 | `.\tools\check_naming_compliance.ps1` |
| `sync_documentation.ps1` | 文档同步 | 文档更新后同步 | `.\tools\sync_documentation.ps1` |

### 📁 项目管理工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `sync_readme.ps1` | 文档同步维护 | 文件结构变更后 | `.\tools\sync_readme.ps1 -Path docs/design` |
| `sync_documentation.ps1` | AI文档同步检查 | AI工作流程文档一致性检查 | `.\tools\sync_documentation.ps1` |
| `update_module_status.ps1` | 模块状态跟踪 | 开发进度管理 | `.\tools\update_module_status.ps1` |
| `release_to_main.ps1` | 版本发布管理 | 功能完成后发布 | `.\tools\release_to_main.ps1` |
| `feature_finish.ps1` | 功能分支完成 | 分支合并和清理 | `.\tools\feature_finish.ps1 -FeatureBranch feature-name` |
| `log_status.ps1` | 状态日志记录 | 开发状态记录和跟踪 | `.\tools\log_status.ps1` |
| `create_module_docs.ps1` | 模块文档生成 | 新模块文档创建 | `.\tools\create_module_docs.ps1 -ModuleName new_module` |

### 🔍 分析调试工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `model_analyzer.py` | 数据模型分析 | 模型设计验证 | `python .\tools\model_analyzer.py` |
| `api_service_mapping_analyzer.py` | API服务映射分析 | 接口关系梳理 | `python .\tools\api_service_mapping_analyzer.py` |

### 🗄️ 数据库调试工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `check_tables.py` | **数据库表结构检查** | **集成测试数据库模式验证、软删除字段检查** | `python check_tables.py` |

### 🏗️ 构建部署工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `rebuild_database.ps1` | 数据库重建 | 数据库结构变更 | `.\tools\rebuild_database.ps1` |
| `check_database_schema.ps1` | 数据库模式检查 | 数据库完整性验证 | `.\tools\check_database_schema.ps1` |

### 🧰 代码生成工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `generate_test_template.py` | 智能测试模板生成 | 模块测试代码自动生成 | `python .\tools\generate_test_template.py user_auth --type all` |
| `test_generators/` | 模块化测试生成器工具集 | 专业化测试代码生成(API/E2E/安全/性能) | 详见 `.\tools\test_generators\README.md` |

### 🤖 AI工作流程工具

| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `task_classification/` | AI任务分类配置和算法 | AI智能任务分类的配置参考 | 详见 `.\tools\task_classification\README.md` |
| `checkpoint-cards.md` | AI检查点卡片系统 | AI工作流程的检查点定义 | AI执行时自动引用 |

## 🔄 工具协作流程

### 典型开发流程

``powershell
# 1. 环境准备
.\tools\setup_test_env.ps1 -TestMode lite

# 2. 开发过程
.\tools\ai_checkpoint.ps1 -CardType DEV-001 -ModuleName <module_name>

# 3. 数据库检查 (集成测试前)
python check_tables.py

# 4. 质量检查
python .\tools\check_quality.py --all
.\tools\dev_checkpoint.ps1 -Module <module_name>

# 5. 测试验证
.\tools\run_module_tests.ps1 -ModuleName <module_name>

# 6. 文档同步
.\tools\sync_readme.ps1 -Path docs/design/modules/<module_name>
```

### 代码质量检查流程

``powershell
# 综合质量检查 (推荐)
python .\tools\check_quality.py --all

# 单独检查硬编码问题
python .\tools\check_quality.py --hardcode

# 检查重复代码问题
python .\tools\check_quality.py --duplication

# 检查指定文件
python .\tools\check_quality.py --all --file api_test_generator.py

# 检查指定目录
python .\tools\check_quality.py --all --dir tools/test_generators/
```

### 完整测试流程

``powershell
# 1. 环境检查
.\tools\check_test_env.ps1 -TestMode full

# 2. 数据库表结构验证
python check_tables.py

# 3. 集成测试
.\tools\integration_test.ps1

# 4. 烟雾测试
.\tools\smoke_test.ps1

# 5. 状态更新
.\tools\update_module_status.ps1
```

## 🆕 版本更新记录

### v2.0.0 (2025-10-10)

#### 新增工具
- `check_tables.py` - 数据库表结构检查工具，解决集成测试数据库模式同步问题
- `model_analyzer.py` - SQLAlchemy模型结构分析工具，用于自动化分析模型字段、关系和混入
- `api_service_mapping_analyzer.py` - API/Service映射分析工具，帮助生成准确的测试代码
- `extract_entity_schema.py` - 模型实体结构提取工具，可生成Markdown或JSON格式的模型文档
- `extract_frontend_rules.py` - 前端规则提取工具，从design.md文档中提取前端配置规则
- `extract_models_jsonschema.py` - 模型JSON Schema提取工具，生成标准JSON Schema供前端使用

#### 文档优化
- 重构文档结构，符合文档管理规范标准
- 清理重复内容，统一工具分类
- 优化工具协作流程说明
- 添加版本管理和更新记录

### v1.1.0 (历史版本)

#### 工具优化更新
- `generate_test_template.py` v1.1.0 - 修复pytest collection超时问题
- `test_generators/performance_test_generator.py` v1.1.0 - 移除硬编码，实现智能endpoint选择
- `test_generators/security_test_generator.py` v1.1.0 - 修复内容损坏，添加错误预防文档
- `test_generators/api_test_generator.py` v1.1.0 - 添加模板格式化指南
- `test_generators/e2e_test_generator.py` v1.1.0 - 添加错误预防文档
- `test_generators/base_generator.py` v1.1.0 - 添加通用格式化错误预防指南

## 🎯 使用建议

- **数据库调试**: 在集成测试失败时，首先运行 `python check_tables.py` 检查数据库表结构与模型定义是否一致
- **质量门禁**: 建议在每次代码提交前运行 `python .\tools\check_quality.py --all`
- **测试代码生成**: 使用更新后的生成器，自动避免常见的模板格式化错误
- **命名规范**: 使用 `check_naming_compliance.ps1` 确保项目命名一致性
- **模型分析**: 使用 `model_analyzer.py` 分析模型结构，辅助测试和文档生成
- **API映射**: 使用 `api_service_mapping_analyzer.py` 确保API和服务层方法一致性
- **文档生成**: 使用 `extract_entity_schema.py` 自动生成模型文档
- **前端开发**: 使用 `extract_frontend_rules.py` 和 `extract_models_jsonschema.py` 为前端提供数据模型和配置规则

## 📖 相关文档

- **开发环境配置**: [docs/development/dev-env-setup.md](../docs/development/dev-env-setup.md)
- **测试环境配置**: [docs/development/test-env-setup.md](../docs/development/test-env-setup.md)
- **测试工厂指南**: [docs/development/test-factory-guide.md](../docs/development/test-factory-guide.md)
- **开发问题解决**: [docs/development/dev-troubleshooting.md](../docs/development/dev-troubleshooting.md)
- **工具故障排查**: [troubleshooting.md](./troubleshooting.md)
- **AI检查点卡片**: [checkpoint-cards.md](./checkpoint-cards.md)
- **文档管理规范**: [docs/standards/document-management-standards.md](../docs/standards/document-management-standards.md)

## 🚨 注意事项

1. **权限要求**: 部分工具需要管理员权限执行
2. **环境依赖**: 确保已安装Python 3.8+和PowerShell 5.1+
3. **Docker服务**: full模式测试需要Docker Desktop运行
4. **虚拟环境**: 建议在Python虚拟环境中执行相关脚本
5. **数据库连接**: 数据库调试工具需要MySQL测试容器运行在localhost:3308

## 🔧 故障排查

常见问题和解决方案请参考：
- [tools/troubleshooting.md](./troubleshooting.md)
- [docs/development/dev-troubleshooting.md](../docs/development/dev-troubleshooting.md)

---

> 💡 **提示**: 所有工具都支持 `-Verbose` 参数获取详细执行信息  
> 🏷️ **标签**: #tools #development #testing #quality-assurance  
> 📅 **更新**: 2025-10-10 | **版本**: v2.0.0 | **维护者**: 开发团队