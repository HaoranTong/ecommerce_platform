# 开发工具集

> 🎯 **一站式开发工具集合**: 提供从环境搭建到测试验证的完整工具支撑

## 📁 目录结构

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
| `enforce_doc_reading.ps1` | 强制文档阅读验证 | 确保AI实际阅读文档内容 | `.\tools\enforce_doc_reading.ps1 -DocumentPath "docs\standards\api-standards.md"` |
| `dev_checkpoint.ps1` | 开发质量检查 | 代码提交前质量验证 | `.\tools\dev_checkpoint.ps1 -Phase PRE_COMMIT` |
| `validate_standards.ps1` | 标准文档验证 | 文档修改后合规检查 | `.\tools\validate_standards.ps1` |
| `check_code_standards.ps1` | 代码规范检查 | 代码质量持续检查 | `.\tools\check_code_standards.ps1` |
| `maintain_standards.ps1` | 标准维护工具 | 标准文档维护和更新 | `.\tools\maintain_standards.ps1` |
| `check_naming_compliance.ps1` | 命名规范检查 | 文件和代码命名合规验证 | `.\tools\check_naming_compliance.ps1` |
| `validate_pydantic_v2.py` | Pydantic V2验证 | 数据模型验证合规检查 | `python .\tools\validate_pydantic_v2.py` |

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
```powershell
# 1. 环境准备
.\tools\setup_test_env.ps1 -TestMode lite

# 2. 开发过程
.\tools\ai_checkpoint.ps1 -CardType DEV-001 -ModuleName <module_name>

# 3. 质量检查 (推荐使用新工具)
python .\tools\check_quality.py --all
.\tools\dev_checkpoint.ps1 -Module <module_name>

# 4. 测试验证
.\tools\run_module_tests.ps1 -ModuleName <module_name>

# 5. 文档同步
.\tools\sync_readme.ps1 -Path docs/design/modules/<module_name>
```

### 代码质量检查流程
```powershell
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
```powershell
# 1. 环境检查
.\tools\check_test_env.ps1 -TestMode full

# 2. 集成测试
.\tools\integration_test.ps1

# 3. 烟雾测试
.\tools\smoke_test.ps1

# 4. 状态更新
.\tools\update_module_status.ps1
```

## 📖 相关文档

- **开发环境配置**: `docs/development/dev-env-setup.md`
- **测试环境配置**: `docs/development/test-env-setup.md`
- **测试工厂指南**: `docs/development/test-factory-guide.md`
- **开发问题解决**: `docs/development/dev-troubleshooting.md`
- **工具故障排查**: `tools/troubleshooting.md`
- **AI检查点卡片**: `tools/checkpoint-cards.md`

## 🚨 注意事项

1. **权限要求**: 部分工具需要管理员权限执行
2. **环境依赖**: 确保已安装Python 3.8+和PowerShell 5.1+
3. **Docker服务**: full模式测试需要Docker Desktop运行
4. **虚拟环境**: 建议在Python虚拟环境中执行相关脚本
5. **质量门禁**: 建议在每次代码提交前运行 `check_quality.py --all`

---

> 💡 **提示**: 所有工具都支持 `-Verbose` 参数获取详细执行信息  
> 🔥 **新功能**: `check_quality.py` 提供统一的代码质量检查，支持硬编码检查、重复代码检查和批量文件处理
|------|----------|----------|----------|
| `model_analyzer.py` | 数据模型分析 | 模型设计验证 | `python .\tools\model_analyzer.py` |
| `api_service_mapping_analyzer.py` | API服务映射分析 | 接口关系梳理 | `python .\tools\api_service_mapping_analyzer.py` |
| `verify_inventory_module.py` | 库存模块验证 | 库存管理模块完整性检查 | `python .\tools\verify_inventory_module.py` |

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
| `checkpoint-cards.md` | AI检查点卡片系统 | AI工作流程的检查点定义 | AI执行时自动引用 |### 🔧 环境管理工具
| 工具 | 功能描述 ### 🧰 代码生成工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `generate_test_template.py` | 智能测试模板生成 | 模块测试代码自动生成 | `python .\tools\generate_test_template.py user_auth` |
| `test_generators/` | 模块化测试生成器工具集 | 专业化测试代码生成(API/E2E/安全/性能) | 详见 `.\tools\test_generators\README.md` |场景 | 快速命令 |
|------|----------|----------|----------|
| `setup_test_env.ps1` | 测试环境配置和验证 | 项目初始化、环境变更后 | `.	ools\setup_test_env.ps1 -TestMode lite` |
| `setup_dev_env.ps1` | 开发环境初始化配置 | 新环境搭建、依赖安装 | `.	ools\setup_dev_env.ps1` |
| `check_test_env.ps1` | 环境状态快速检查 | 测试前环境确认 | `.	ools\check_test_env.ps1` |
| `check_test_env_legacy.ps1` | 旧版环境检查（兼容性） | 特殊情况下的环境检查 | `.	ools\check_test_env_legacy.ps1` |
| `dev_tools.ps1` | 开发环境工具集合 | 日常开发辅助操作 | `.	ools\dev_tools.ps1 check-db` |航### 🧪 测试执行工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `run_module_tests.ps1` | 模块测试执行 | 单个模块完整测试 | `.	ools\run_module_tests.ps1 -ModuleName user_auth` |
| `smoke_test.ps1` | API快速验证 | 功能开发后快速验证 | `.	ools\smoke_test.ps1` |
| `integration_test.ps1` | 集成测试执行 | 多模块协作验证 | `.	ools\integration_test.ps1` |
| `e2e_test_verification.py` | E2E测试验证 | 端到端测试流程验证 | `python .	ools\e2e_test_verification.py` |
| `validate_test_config.py` | 测试配置验证 | 测试环境配置检查 | `python .	ools\validate_test_config.py` |
| `validate_test_structure.py` | 测试结构验证 | 测试文件结构合规检查 | `python .	ools\validate_test_structure.py` |盖### ⚡ 质量保证工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `ai_checkpoint.ps1` | AI检查点验证 | AI开发任务完成验证 | `.	ools\ai_checkpoint.ps1 -CardType DEV-001` |
| `enforce_doc_reading.ps1` | 强制文档阅读验证 | 确保AI实际阅读文档内容 | `.	ools\enforce_doc_reading.ps1 -DocumentPath "docs\standards\api-standards.md"` |
| `dev_checkpoint.ps1` | 开发质量检查 | 代码提交前质量验证 | `.	ools\dev_checkpoint.ps1 -Phase PRE_COMMIT` |
| `validate_standards.ps1` | 标准文档验证 | 文档修改后合规检查 | `.	ools\validate_standards.ps1` |
| `check_code_standards.ps1` | 代码规范检查 | 代码质量持续检查 | `.	ools\check_code_standards.ps1` |
| `maintain_standards.ps1` | 标准维护工具 | 标准文档维护和更新 | `.	ools\maintain_standards.ps1` |
| `check_naming_compliance.ps1` | 命名规范检查 | 文件和代码命名合规验证 | `.	ools\check_naming_compliance.ps1` |
| `validate_pydantic_v2.py` | Pydantic V2验证 | 数据模型验证合规检查 | `python .	ools\validate_pydantic_v2.py` |行### 📁 项目管理工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `sync_readme.ps1` | 文档同步维护 | 文件结构变更后 | `.	ools\sync_readme.ps1 -Path docs/design` |
| `update_module_status.ps1` | 模块状态跟踪 | 开发进度管理 | `.	ools\update_module_status.ps1` |
| `release_to_main.ps1` | 版本发布管理 | 功能完成后发布 | `.	ools\release_to_main.ps1` |
| `feature_finish.ps1` | 功能分支完成 | 分支合并和清理 | `.	ools\feature_finish.ps1 -FeatureBranch feature-name` |
| `log_status.ps1` | 状态日志记录 | 开发状态记录和跟踪 | `.	ools\log_status.ps1` |
| `create_module_docs.ps1` | 模块文档生成 | 新模块文档创建 | `.	ools\create_module_docs.ps1 -ModuleName new_module` |项### 🔍 分析调试工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `model_analyzer.py` | 数据模型分析 | 模型设计验证 | `python .	ools\model_analyzer.py` |
| `api_service_mapping_analyzer.py` | API服务映射分析 | 接口关系梳理 | `python .	ools\api_service_mapping_analyzer.py` |
| `analyze_simple_markers.ps1` | 简单标记分析 | 代码标记和注释分析 | `.	ools\analyze_simple_markers.ps1` |
| `verify_inventory_module.py` | 库存模块验证 | 库存管理模块完整性检查 | `python .	ools\verify_inventory_module.py` |整### 🏗️ 构建部署工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `rebuild_database.ps1` | 数据库重建 | 数据库结构变更 | `.	ools\rebuild_database.ps1` |
| `check_database_schema.ps1` | 数据库模式检查 | 数据库完整性验证 | `.	ools\check_database_schema.ps1` |

### 🧰 代码生成工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `generate_test_template.py` | 智能测试模板生成 | 模块测试代码自动生成 | `python .	ools\generate_test_template.py user_auth --type all` |
## 💡 快速使用指南

所有工具都内置详细帮## 📖 相关文档

所有工具都内置详细帮助，可通过以下命令查看：
```powershell
Get-Help .\tools\<script_name>.ps1 -Full
```

## 🎯 使用场景导航

### 🔧 环境管理工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `setup_test_env.ps1` | 测试环境配置和验证 | 项目初始化、环境变更后 | `.\tools\setup_test_env.ps1 -TestMode lite` |
| `check_test_env.ps1` | 环境状态快速检查 | 测试前环境确认 | `.\tools\check_test_env.ps1` |
| `dev_tools.ps1` | 开发环境工具集合 | 日常开发辅助操作 | `.\tools\dev_tools.ps1 check-db` |

### 🧪 测试执行工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `run_module_tests.ps1` | 模块测试执行 | 单个模块完整测试 | `.\tools\run_module_tests.ps1 -ModuleName user_auth` |
| `smoke_test.ps1` | API快速验证 | 功能开发后快速验证 | `.\tools\smoke_test.ps1` |
| `integration_test.ps1` | 集成测试执行 | 多模块协作验证 | `.\tools\integration_test.ps1` |

### ⚡ 质量保证工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `ai_checkpoint.ps1` | AI检查点验证 | AI开发任务完成验证 | `.\tools\ai_checkpoint.ps1 -CardType DEV-001` |
| `enforce_doc_reading.ps1` | 强制文档阅读验证 | 确保AI实际阅读文档内容 | `.\tools\enforce_doc_reading.ps1 -DocumentPath "docs\standards\api-standards.md"` |
| `dev_checkpoint.ps1` | 开发质量检查 | 代码提交前质量验证 | `.\tools\dev_checkpoint.ps1` |
| `validate_standards.ps1` | 标准文档验证 | 文档修改后合规检查 | `.\tools\validate_standards.ps1` |
| `check_code_standards.ps1` | 代码规范检查 | 代码质量持续检查 | `.\tools\check_code_standards.ps1` |

### 📁 项目管理工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `sync_readme.ps1` | 文档同步维护 | 文件结构变更后 | `.\tools\sync_readme.ps1 -Path docs/design` |
| `update_module_status.ps1` | 模块状态跟踪 | 开发进度管理 | `.\tools\update_module_status.ps1` |
| `release_to_main.ps1` | 版本发布管理 | 功能完成后发布 | `.\tools\release_to_main.ps1` |

### 🔍 分析调试工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `model_analyzer.py` | 数据模型分析 | 模型设计验证 | `python .\tools\model_analyzer.py` |
| `api_service_mapping_analyzer.py` | API服务映射分析 | 接口关系梳理 | `python .\tools\api_service_mapping_analyzer.py` |

### 🏗️ 构建部署工具
| 工具 | 功能描述 | 使用场景 | 快速命令 |
|------|----------|----------|----------|
| `rebuild_database.ps1` | 数据库重建 | 数据库结构变更 | `.\tools\rebuild_database.ps1` |
| `check_database_schema.ps1` | 数据库模式检查 | 数据库完整性验证 | `.\tools\check_database_schema.ps1` |

## 🔄 工具协作流程

### 典型开发流程
```powershell
# 1. 环境准备
.\tools\setup_test_env.ps1 -TestMode lite

# 2. 开发过程
.\tools\ai_checkpoint.ps1 -CardType DEV-001 -ModuleName <module_name>

# 3. 质量检查
.\tools\dev_checkpoint.ps1 -Module <module_name>

# 4. 测试验证
.\tools\run_module_tests.ps1 -ModuleName <module_name>

# 5. 文档同步
.\tools\sync_readme.ps1 -Path docs/design/modules/<module_name>
```

### 完整测试流程
```powershell
# 1. 环境检查
.\tools\check_test_env.ps1 -TestMode full

# 2. 集成测试
.\tools\integration_test.ps1

# 3. 烟雾测试
.\tools\smoke_test.ps1

# 4. 状态更新
.\tools\update_module_status.ps1
```

## 📖 相关文档

- **开发环境配置**: `docs/development/dev-env-setup.md`
- **测试环境配置**: `docs/development/test-env-setup.md`
- **测试工厂指南**: `docs/development/test-factory-guide.md`
- **开发问题解决**: `docs/development/dev-troubleshooting.md`
- **工具故障排查**: `tools/troubleshooting.md`
- **AI检查点卡片**: `tools/checkpoint-cards.md`

## � 新增工具更新 (v1.1.0)

### 🆕 最新添加的工具

| 工具 | 功能描述 | 版本 | 更新内容 |
|------|----------|------|----------|
| `tests/utils/token_utils.py` | **JWT Token统一工具模块** | v1.0.0 | 新增 - 提供测试环境统一的JWT token创建、验证和管理功能 |
| `docs/standards/jwt-token-format-standard.md` | **JWT Token格式标准文档** | v1.0.0 | 新增 - 建立JWT token格式统一标准，确保测试生产环境一致性 |

### 🔧 工具优化更新

| 工具 | 更新版本 | 主要改进 |
|------|----------|----------|
| `generate_test_template.py` | v1.1.0 | 修复pytest collection超时问题，优化复杂测试收集性能 |
| `test_generators/performance_test_generator.py` | v1.1.0 | 移除硬编码，实现智能endpoint选择，修复模板格式化错误 |
| `test_generators/security_test_generator.py` | v1.1.0 | 修复内容损坏，添加comprehensive错误预防文档 |
| `test_generators/api_test_generator.py` | v1.1.0 | 添加模板格式化指南，防止双重转义错误 |
| `test_generators/e2e_test_generator.py` | v1.1.0 | 添加错误预防文档，提高代码生成质量 |
| `test_generators/base_generator.py` | v1.1.0 | 添加通用格式化错误预防指南，适用于所有生成器 |

### 🎯 使用建议

- **JWT Token管理**: 所有新的测试代码应使用 `TestTokenManager` 创建token，确保格式一致性
- **测试代码生成**: 使用更新后的生成器，自动避免常见的模板格式化错误
- **标准合规**: 新增的JWT token必须符合 `jwt-token-format-standard.md` 规范

## �🚨 注意事项

1. **权限要求**: 部分工具需要管理员权限执行
2. **环境依赖**: 确保已安装Python 3.8+和PowerShell 5.1+
3. **Docker服务**: full模式测试需要Docker Desktop运行
4. **虚拟环境**: 建议在Python虚拟环境中执行相关脚本

---

> 💡 **提示**: 所有工具都支持 `-Verbose` 参数获取详细执行信息