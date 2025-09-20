# 开发工具脚本目录

## 📁 脚本分类概览

### 🔧 AI开发辅助脚本 (3个)
| 脚本名称 | 功能 | 使用场景 | 详细文档 |
|---------|------|----------|----------|
| `ai_checkpoint.ps1` | AI检查点验证 | AI开发流程验证 | [📖](../docs/development/scripts-usage-manual.md#ai_checkpoint) |
| `dev_checkpoint.ps1` | 开发检查点 | 代码质量检查 | [📖](../docs/development/scripts-usage-manual.md#dev_checkpoint) |
| `smoke_test.ps1` | 冒烟测试 | 快速功能验证 | [📖](../docs/development/scripts-usage-manual.md#smoke_test) |

### 📋 项目管理脚本 (6个)
| 脚本名称 | 功能 | 使用场景 | 详细文档 |
|---------|------|----------|----------|
| `feature_finish.ps1` | 功能完成流程 | 功能开发完成后 | [📖](../docs/development/scripts-usage-manual.md#feature_finish) |
| `release_to_main.ps1` | 发布到主分支 | 版本发布流程 | [📖](../docs/development/scripts-usage-manual.md#release_to_main) |
| `sync_env.ps1` | 环境状态同步 | 环境配置同步 | [📖](../docs/development/scripts-usage-manual.md#sync_env) |
| `sync_readme.ps1` | 文档同步 | 文档更新后同步 | [📖](../docs/development/scripts-usage-manual.md#sync_readme) |
| `log_status.ps1` | 状态日志记录 | 工作状态记录 | [📖](../docs/development/scripts-usage-manual.md#log_status) |
| `update_module_status.ps1` | 模块状态更新 | 模块开发状态维护 | [📖](../docs/development/scripts-usage-manual.md#update_module_status) |

### 🔍 代码质量检查脚本 (5个)
| 脚本名称 | 功能 | 使用场景 | 详细文档 |
|---------|------|----------|----------|
| `check_code_standards.ps1` | 代码规范检查 | 提交前代码质量验证 | [📖](../docs/development/scripts-usage-manual.md#check_code_standards) |
| `check_docs.ps1` | 文档检查 | 文档质量验证 | [📖](../docs/development/scripts-usage-manual.md#check_docs) |
| `check_naming_compliance.ps1` | 命名规范检查 | 命名标准验证 | [📖](../docs/development/scripts-usage-manual.md#check_naming_compliance) |
| `quick_structure_check.ps1` | 快速结构检查 | 项目结构验证 | [📖](../docs/development/scripts-usage-manual.md#quick_structure_check) |
| `validate_pydantic_v2.py` | Pydantic验证 | 数据模型验证 | [📖](../docs/development/scripts-usage-manual.md#validate_pydantic_v2) |

### 🧪 测试与验证脚本 (7个)
| 脚本名称 | 功能 | 使用场景 | 详细文档 |
|---------|------|----------|----------|
| `integration_test.ps1` | 集成测试 | 模块集成验证 | [📖](../docs/development/scripts-usage-manual.md#integration_test) |
| `run_module_tests.ps1` | 模块测试运行 | 单模块测试执行 | [📖](../docs/development/scripts-usage-manual.md#run_module_tests) |
| `test_product_system.ps1` | 产品系统测试 | 产品模块专项测试 | [📖](../docs/development/scripts-usage-manual.md#test_product_system) |
| `check_test_env.ps1` | 测试环境检查 | 测试环境验证 | [📖](../docs/development/scripts-usage-manual.md#check_test_env) |
| `setup_test_env.ps1` | 测试环境搭建 | 初始化测试环境 | [📖](../docs/development/scripts-usage-manual.md#setup_test_env) |
| `validate_test_config.py` | 测试配置验证 | 测试配置检查 | [📖](../docs/development/scripts-usage-manual.md#validate_test_config) |
| `validate_test_structure.py` | 测试结构验证 | 测试代码结构检查 | [📖](../docs/development/scripts-usage-manual.md#validate_test_structure) |

### ⚙️ 系统维护脚本 (7个)
| 脚本名称 | 功能 | 使用场景 | 详细文档 |
|---------|------|----------|----------|
| `check_database_schema.ps1` | 数据库schema检查 | 数据库结构验证 | [📖](../docs/development/scripts-usage-manual.md#check_database_schema) |
| `rebuild_database.ps1` | 数据库重建 | 数据库结构重置 | [📖](../docs/development/scripts-usage-manual.md#rebuild_database) |
| `create_module_docs.ps1` | 模块文档创建 | 新模块文档生成 | [📖](../docs/development/scripts-usage-manual.md#create_module_docs) |
| `generate_test_template.py` | 测试模板生成 | 自动测试代码生成 | [📖](../docs/development/scripts-usage-manual.md#generate_test_template) |
| `api_service_mapping_analyzer.py` | API映射分析 | API服务关系分析 | [📖](../docs/development/scripts-usage-manual.md#api_service_mapping_analyzer) |
| `verify_inventory_module.py` | 库存模块验证 | 库存模块专项检查 | [📖](../docs/development/scripts-usage-manual.md#verify_inventory_module) |

## 🚀 快速开始

### 新手必读
1. **开发环境准备** → 参考 [`docs/development/environment-setup.md`](../docs/development/environment-setup.md)
2. **脚本详细使用** → 参考 [`docs/development/scripts-usage-manual.md`](../docs/development/scripts-usage-manual.md)  
3. **工作流程指南** → 参考 [`docs/development/workflow-guide.md`](../docs/development/workflow-guide.md)

### 常用工作流程

#### 🤖 AI开发流程
```powershell
# 开发前环境检查
.\ai_checkpoint.ps1 -CardType "DEV-001"
.\dev_checkpoint.ps1

# 开发中质量检查 
.\check_code_standards.ps1
.\smoke_test.ps1

# 开发完成验证
.\ai_checkpoint.ps1 -CardType "DEV-008"
```

#### 📝 文档维护流程
```powershell
# 文档检查与同步
.\check_docs.ps1
.\check_naming_compliance.ps1
.\sync_readme.ps1
```

#### 🧪 测试验证流程
```powershell  
# 测试环境准备
.\setup_test_env.ps1
.\check_test_env.ps1

# 执行测试
.\run_module_tests.ps1 -Module "user_auth"
.\integration_test.ps1
```

## 📚 完整使用文档

### 🔗 文档导航
- **脚本详细使用手册** → [`docs/development/scripts-usage-manual.md`](../docs/development/scripts-usage-manual.md)
- **开发环境配置指南** → [`docs/development/environment-setup.md`](../docs/development/environment-setup.md)
- **开发工作流程指南** → [`docs/development/workflow-guide.md`](../docs/development/workflow-guide.md)

### 🆘 获取帮助
- 每个脚本都支持 `-Help` 参数获取详细帮助
- 遇到问题请先查看对应脚本的详细文档
- 参数不确定时可以先用 `-WhatIf` 模式预览

---
> 📝 **维护说明**: 此文档为脚本目录导航，专注于快速定位和基础使用。详细的使用说明、参数配置、故障排除等信息请参考对应的详细文档。