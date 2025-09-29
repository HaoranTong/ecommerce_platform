# 开发工具集

> 🎯 **一站式开发工具导航** - 涵盖环境管理、测试执行、质量检查、项目管理的完整工具链

## 💡 快速使用指南

所有工具都内置详细帮## 📖 相关文档

- **开发环境配置**: `docs/development/dev-env-setup.md`
- **测试环境配置**: `docs/development/test-env-setup.md`
- **测试工厂指南**: `docs/development/test-factory-guide.md`
- **开发问题解决**: `docs/development/dev-troubleshooting.md`
- **工具故障排查**: `tools/troubleshooting.md`
- **AI检查点卡片**: `tools/checkpoint-cards.md`以下命令查看：
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

- **开发环境配置**: `docs/development/environment-setup.md`
- **测试环境配置**: `docs/development/testing-environment.md`
- **故障排查手册**: `docs/development/troubleshooting.md`
- **AI检查点卡片**: `tools/checkpoint-cards.md`

## 🚨 注意事项

1. **权限要求**: 部分工具需要管理员权限执行
2. **环境依赖**: 确保已安装Python 3.8+和PowerShell 5.1+
3. **Docker服务**: full模式测试需要Docker Desktop运行
4. **虚拟环境**: 建议在Python虚拟环境中执行相关脚本

---

> 💡 **提示**: 所有工具都支持 `-Verbose` 参数获取详细执行信息