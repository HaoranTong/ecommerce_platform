# 开发脚本使用手册

> 🤖 **AI优化文档**: 本文档专为AI使用优化，采用结构化信息模板，便于AI快速解析和执行脚本命令。

## 🎯 AI使用指南

### 快速定位脚本
- **按功能查找** → 使用章节2-6的分类导航，每个脚本都有标准化的功能描述
- **按场景查找** → 使用章节7的AI场景索引，直接获取工作流程
- **获取详细参数** → 每个脚本都有标准化的参数表格，便于构建命令

### AI操作模式
- **直接执行**: 使用 `run_in_terminal` 工具执行脚本命令
- **参数构建**: 使用参数表格构建完整命令行
- **组合使用**: 参考AI工作流程章节的脚本组合模式

### 标准化信息模板
每个脚本包含以下标准化信息：
- 功能描述 (一句话概述)
- 执行时机 (何时使用)
- 参数表格 (完整参数信息)
- AI使用模式 (具体命令示例)
- 关联文档 (相关文档路径)
- 触发场景 (使用场景说明)

## 🔧 AI开发辅助脚本

### ai_checkpoint.ps1 - AI检查点验证

**功能描述**: 验证AI开发流程中的检查点完成情况，确保开发规范遵循  
**执行时机**: AI开发任务完成后强制验证  
**输出格式**: 标准化检查结果，包含通过/失败状态  
**错误处理**: 返回具体失败项目和修复建议

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-CardType` | String | ✓ | 无 | 检查点类型编号 | 使用MASTER文档中的检查点编号如"DEV-001" |
| `-Verbose` | Switch | ✗ | false | 详细输出模式 | 调试时启用，获取更多验证详情 |
| `-Force` | Switch | ✗ | false | 强制执行模式 | 跳过交互确认，适合自动化流程 |

**AI使用模式**:
```powershell
# 标准用法 - 验证开发检查点
.\scripts\ai_checkpoint.ps1 -CardType "DEV-001"

# 详细模式 - 获取详细验证信息
.\scripts\ai_checkpoint.ps1 -CardType "DOC-005" -Verbose

# 自动化模式 - 批量验证多个检查点
.\scripts\ai_checkpoint.ps1 -CardType "TEST-001" -Force
```

**关联文档**: `docs/standards/checkpoint-cards.md`, `MASTER.md`  
**触发场景**: AI完成代码开发、文档更新、测试编写后必须执行  
**下游脚本**: 通常与 `dev_checkpoint.ps1` 组合使用验证开发质量

---

### dev_checkpoint.ps1 - 开发检查点验证

**功能描述**: 执行代码质量、规范遵循、测试覆盖等开发检查点验证  
**执行时机**: 代码提交前、功能完成后的质量验证  
**输出格式**: 检查项目列表和通过状态，失败项目的修复建议  
**错误处理**: 详细的错误信息和修复步骤指导

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-Module` | String | ✗ | "all" | 检查的模块名称 | 指定单个模块如"user_auth"或"all"检查全部 |
| `-SkipTests` | Switch | ✗ | false | 跳过测试检查 | 仅检查代码质量，跳过测试相关验证 |
| `-Quick` | Switch | ✗ | false | 快速检查模式 | 只执行核心检查项，适合快速验证 |
| `-Verbose` | Switch | ✗ | false | 详细输出模式 | 显示详细的检查过程和结果 |

**AI使用模式**:
```powershell
# 全项目检查
.\scripts\dev_checkpoint.ps1

# 单模块检查
.\scripts\dev_checkpoint.ps1 -Module "user_auth" -Verbose

# 快速检查（跳过测试）
.\scripts\dev_checkpoint.ps1 -Quick -SkipTests
```

**关联文档**: `docs/standards/code-standards.md`, `docs/development/workflow-guide.md`  
**触发场景**: 代码开发完成、准备提交前、功能测试前  
**下游脚本**: 检查通过后可执行 `smoke_test.ps1` 进行功能验证

---

### smoke_test.ps1 - 冒烟测试执行

**功能描述**: 执行快速冒烟测试，验证核心功能是否正常工作  
**执行时机**: 代码变更后的快速验证，部署前的基础功能确认  
**输出格式**: 测试结果摘要，失败测试的详细信息  
**错误处理**: 测试失败时提供具体的失败原因和调试建议

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-Module` | String | ✗ | "all" | 测试的模块范围 | 指定模块名如"product_catalog"或"all" |
| `-Environment` | String | ✗ | "dev" | 测试环境 | dev/test/staging，确保环境配置正确 |
| `-Timeout` | Int | ✗ | 300 | 测试超时时间(秒) | 根据系统性能调整，避免超时失败 |
| `-Parallel` | Switch | ✗ | false | 并行执行测试 | 提高测试速度，但可能影响资源竞争 |

**AI使用模式**:
```powershell
# 标准冒烟测试
.\scripts\smoke_test.ps1

# 指定模块测试
.\scripts\smoke_test.ps1 -Module "order_management" -Environment "dev"

# 快速并行测试
.\scripts\smoke_test.ps1 -Parallel -Timeout 180
```

**关联文档**: `docs/development/testing-setup.md`, `tests/README.md`  
**触发场景**: 代码变更后、部署前、定期健康检查  
**下游脚本**: 测试通过后可执行 `integration_test.ps1` 进行更全面的测试

## 📋 项目管理脚本

### feature_finish.ps1 - 功能完成流程

**功能描述**: 执行功能开发完成后的标准流程，包括测试、文档、代码检查  
**执行时机**: 功能开发完成，准备合并到主分支前  
**输出格式**: 流程执行步骤和结果，完成确认清单  
**错误处理**: 流程中断时提供继续执行的建议和修复步骤

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-FeatureName` | String | ✓ | 无 | 功能名称 | 使用清晰的功能描述如"user-authentication" |
| `-SkipDocs` | Switch | ✗ | false | 跳过文档生成 | 文档已完备时使用，但不推荐 |
| `-AutoMerge` | Switch | ✗ | false | 自动合并分支 | 所有检查通过后自动执行合并 |
| `-Force` | Switch | ✗ | false | 强制完成流程 | 忽略部分检查失败，谨慎使用 |

**AI使用模式**:
```powershell
# 标准功能完成流程
.\scripts\feature_finish.ps1 -FeatureName "shopping-cart-api"

# 快速完成（跳过文档）
.\scripts\feature_finish.ps1 -FeatureName "bug-fix-inventory" -SkipDocs

# 自动化流程
.\scripts\feature_finish.ps1 -FeatureName "payment-integration" -AutoMerge
```

**关联文档**: `docs/development/workflow-guide.md`, `docs/standards/document-standards.md`  
**触发场景**: 功能开发完成、准备代码审查、分支合并前  
**下游脚本**: 完成后通常执行 `release_to_main.ps1` 进行发布准备

---

### sync_readme.ps1 - 文档同步更新

**功能描述**: 自动同步更新README文档，确保文档与代码结构一致  
**执行时机**: 文件结构变更后、新增脚本后强制执行  
**输出格式**: 同步的文件列表和更新内容摘要  
**错误处理**: 文档冲突时提供合并建议和手动处理指导

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-Path` | String | ✗ | "." | 同步的根目录 | 指定需要同步的目录路径 |
| `-DryRun` | Switch | ✗ | false | 预览模式 | 只显示将要更新的内容，不实际修改 |
| `-Force` | Switch | ✗ | false | 强制覆盖 | 忽略冲突警告，直接覆盖现有内容 |
| `-Backup` | Switch | ✗ | true | 备份原文件 | 更新前创建备份，建议保持启用 |

**AI使用模式**:
```powershell
# 标准文档同步
.\scripts\sync_readme.ps1

# 预览更新内容
.\scripts\sync_readme.ps1 -DryRun

# 指定目录同步
.\scripts\sync_readme.ps1 -Path "app/modules" -Verbose
```

**关联文档**: `docs/standards/document-standards.md`, `MASTER.md`  
**触发场景**: 创建新文件、删除文件、重命名文件后强制执行  
**下游脚本**: 同步完成后建议执行 `check_docs.ps1` 验证文档质量

## 🔍 代码质量检查脚本

### check_code_standards.ps1 - 代码规范检查

**功能描述**: 检查代码是否遵循项目编码规范，包括格式、命名、结构等  
**执行时机**: 代码提交前、代码审查前的质量验证  
**输出格式**: 规范违反项目列表，修复建议和自动修复选项  
**错误处理**: 提供详细的违规位置和标准修复方法

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-Path` | String | ✗ | "app" | 检查的代码路径 | 可指定具体模块路径如"app/modules/user_auth" |
| `-Fix` | Switch | ✗ | false | 自动修复模式 | 自动修复可修复的规范问题 |
| `-Standard` | String | ✗ | "pep8" | 检查标准 | pep8/black/flake8，选择检查工具 |
| `-Exclude` | String[] | ✗ | @() | 排除的文件模式 | 排除特定文件如"*_test.py" |

**AI使用模式**:
```powershell
# 全项目代码检查
.\scripts\check_code_standards.ps1

# 检查并自动修复
.\scripts\check_code_standards.ps1 -Fix -Path "app/modules/user_auth"

# 使用特定标准检查
.\scripts\check_code_standards.ps1 -Standard "black" -Exclude "*_test.py"
```

**关联文档**: `docs/standards/code-standards.md`, `docs/development/code-style-guide.md`  
**触发场景**: 提交代码前、代码审查前、持续集成流程中  
**下游脚本**: 检查通过后执行 `check_naming_compliance.ps1` 验证命名规范

---

### check_docs.ps1 - 文档质量检查

**功能描述**: 检查文档完整性、格式正确性、链接有效性等文档质量问题  
**执行时机**: 文档更新后、发布前的文档质量验证  
**输出格式**: 文档问题清单，修复优先级和具体修复建议  
**错误处理**: 提供文档问题的分类和标准化修复方法

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-Path` | String | ✗ | "docs" | 检查的文档路径 | 可指定特定文档目录 |
| `-CheckLinks` | Switch | ✗ | true | 检查链接有效性 | 验证内外部链接是否可访问 |
| `-Format` | String | ✗ | "markdown" | 文档格式 | markdown/rst/html等 |
| `-Deep` | Switch | ✗ | false | 深度检查模式 | 包括语法、拼写等详细检查 |

**AI使用模式**:
```powershell
# 标准文档检查
.\scripts\check_docs.ps1

# 深度检查（包括拼写）
.\scripts\check_docs.ps1 -Deep -CheckLinks

# 检查特定目录
.\scripts\check_docs.ps1 -Path "docs/modules" -Format "markdown"
```

**关联文档**: `docs/standards/document-standards.md`, `docs/development/documentation-guide.md`  
**触发场景**: 文档更新后、发布准备、文档审查前  
**下游脚本**: 检查通过后可执行 `sync_readme.ps1` 确保文档同步

## 🧪 测试与验证脚本

### generate_test_template.py - 智能五层架构测试生成器 v2.0

**功能描述**: 基于SQLAlchemy模型自动生成Factory Boy工厂、单元测试、集成测试等完整测试套件，包含AST+运行时双重分析和自动质量验证  
**执行时机**: 新模块开发完成后、需要标准化测试时、测试覆盖率不足时  
**输出格式**: 生成到tests/generated/暂存目录，需人工审查后移动到正式目录  
**关键特性**: 智能模型分析、自动关系处理、完整业务逻辑覆盖、质量自动验证

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `module_name` | String | ✓ | 无 | 目标模块名称 | 使用app/modules/下的模块名如"user_auth","shopping_cart" |
| `--type` | Enum | ✗ | "all" | 测试类型选择 | all, unit, integration, e2e, smoke, specialized |
| `--dry-run` | Switch | ✗ | false | 预览模式不写文件 | 用于预览生成内容，不实际创建文件 |
| `--validate` | Switch | ✗ | true | 自动质量验证 | 执行语法检查、导入验证、依赖检查 |
| `--detailed` | Switch | ✗ | false | 显示详细分析 | 显示模型分析详情和生成过程信息 |

**AI使用模式**:
```powershell
# 生成完整测试套件（推荐，包含工厂+单元+集成）
python scripts/generate_test_template.py user_auth --type all --validate

# 仅生成单元测试
python scripts/generate_test_template.py user_auth --type unit --detailed

# 仅生成集成测试
python scripts/generate_test_template.py shopping_cart --type integration

# 预览模式（不写入文件）
python scripts/generate_test_template.py product_catalog --type all --dry-run

# 生成后验证质量
python scripts/generate_test_template.py payment --type all --validate --detailed
```

**生成的文件结构**:
```
tests/generated/
├── user_auth_factories.py          # Factory Boy数据工厂（6个工厂类）
├── test_user_auth_unit.py          # 单元测试（5个测试类，13个方法）
└── test_user_auth_integration.py   # 集成测试（6个测试方法）
```

**生成的测试内容**: 详见 [测试标准文档](../standards/testing-standards.md)
- ✅ **单元测试**: 完全实现 - 模型测试、密码哈希、JWT、服务层、验证逻辑
- ✅ **集成测试**: 完全实现 - JWT集成、用户注册流程、登录认证、API端点、数据库集成、权限系统
- ✅ **数据工厂**: 完全实现 - Factory Boy智能工厂，处理关系和约束
- ⚠️ **其他测试类型**: 占位符实现，需要手动完善

**质量验证机制**:
1. **Python语法检查** - 确保生成代码语法正确
2. **pytest测试收集** - 验证测试文件可被正确识别
3. **导入依赖验证** - 检查所有导入语句可用性
4. **依赖完整性检查** - 验证工厂和测试文件依赖关系
5. **基础执行测试** - 运行基础验证确保代码可执行

**关联文档**: `docs/development/generated-tests-management.md`（工作流程）, `docs/standards/testing-standards.md`（标准规范）  
**触发场景**: 新模块开发完成、测试覆盖率检查、代码重构需要测试更新  
**下游操作**: 
1. 审查生成文件质量和业务逻辑正确性
2. 根据验证报告修复问题
3. 移动到正式测试目录并提交版本控制

**常见问题处理**:
- **模型重复定义警告**: 正常现象，不影响测试生成
- **Table已定义错误**: 工厂文件执行问题，检查数据库连接
- **导入失败**: 确保模块路径正确，Python环境配置正确

**测试架构和分层**: 详见 [测试标准文档](../standards/testing-standards.md)

---

### integration_test.ps1 - 集成测试执行

**功能描述**: 执行模块间集成测试，验证系统整体功能协作  
**执行时机**: 多模块开发完成后、系统级功能验证  
**输出格式**: 集成测试结果报告，模块间接口测试状态  
**错误处理**: 集成失败时提供接口调试信息和修复建议

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| `-Modules` | String[] | ✗ | @("all") | 参与集成测试的模块 | 指定模块列表如@("user_auth","product_catalog") |
| `-Environment` | String | ✗ | "test" | 测试环境 | test/integration/staging环境选择 |
| `-Parallel` | Switch | ✗ | false | 并行测试模式 | 提高测试速度但需要更多资源 |
| `-Coverage` | Switch | ✗ | true | 生成覆盖率报告 | 分析测试覆盖情况 |

**AI使用模式**:
```powershell
# 全系统集成测试
.\scripts\integration_test.ps1

# 指定模块集成测试
.\scripts\integration_test.ps1 -Modules @("user_auth","order_management") -Environment "test"

# 并行测试（提高速度）
.\scripts\integration_test.ps1 -Parallel -Coverage
```

**关联文档**: `docs/development/testing-setup.md`, `docs/architecture/integration-patterns.md`  
**触发场景**: 多模块功能完成后、系统发布前、回归测试  
**下游脚本**: 测试通过后可执行 `feature_finish.ps1` 完成功能发布流程

## 🎯 AI场景驱动的使用索引

### 场景1: AI开发新功能
```powershell
# 第一步: 开发前检查
.\scripts\ai_checkpoint.ps1 -CardType "DEV-001" 
.\scripts\dev_checkpoint.ps1 -Quick

# 第二步: 开发中验证
.\scripts\check_code_standards.ps1 -Path "app/modules/new_module"
.\scripts\smoke_test.ps1 -Module "new_module"

# 第三步: 开发完成检查
.\scripts\ai_checkpoint.ps1 -CardType "DEV-008"
.\scripts\feature_finish.ps1 -FeatureName "new-feature"
```

### 场景2: AI文档维护
```powershell
# 文档检查和修复
.\scripts\check_docs.ps1 -Deep
.\scripts\check_naming_compliance.ps1
.\scripts\sync_readme.ps1 -DryRun

# 文档同步验证
.\scripts\ai_checkpoint.ps1 -CardType "DOC-005" -Verbose
```

### 场景3: AI测试验证
```powershell
# 测试环境准备
.\scripts\setup_test_env.ps1
.\scripts\check_test_env.ps1

# 执行测试流程
.\scripts\run_module_tests.ps1 -Module "target_module"
.\scripts\integration_test.ps1 -Modules @("module1","module2")
.\scripts\ai_checkpoint.ps1 -CardType "TEST-008"
```

### 场景4: AI工具脚本创建流程
当AI创建新的工具脚本时，必须遵循以下文档同步流程：

```powershell
# 第一步: 创建脚本后立即执行文档同步
.\scripts\sync_readme.ps1

# 第二步: 验证工具文档完整性
.\scripts\ai_checkpoint.ps1 -CardType "DOC-006" -Verbose

# 第三步: 检查文档质量
.\scripts\check_docs.ps1 -Path "scripts"
.\scripts\check_docs.ps1 -Path "docs/development"
```

**🚨 强制检查点说明**:
- **[CHECK:DOC-005]**: 文件操作后必须执行 `sync_readme.ps1`
- **[CHECK:DOC-006]**: 工具创建后必须验证文档完整性
- **[CHECK:DOC-001]**: 代码完成后必须同步相关文档

## 📝 AI脚本创建文档模板

当AI创建新工具脚本时，必须使用以下标准模板更新此文档：

```markdown
### new_script.ps1 - 功能简述

**功能描述**: [AI填充：一句话描述脚本功能]  
**执行时机**: [AI填充：何时使用此脚本]  
**输出格式**: [AI填充：输出内容格式说明]  
**错误处理**: [AI填充：错误处理方式描述]

**参数表格**:
| 参数名 | 类型 | 必需 | 默认值 | 说明 | AI使用提示 |
|--------|------|------|--------|------|------------|
| [AI填充参数表格] |

**AI使用模式**:
```powershell
# [AI填充：标准使用命令]
# [AI填充：常用参数组合示例]
```

**关联文档**: [AI填充：相关文档路径]  
**触发场景**: [AI填充：使用场景描述]  
**下游脚本**: [AI填充：相关脚本组合说明]
```

---

> 📝 **维护说明**: 
> 1. 此文档专为AI优化，所有新增脚本必须遵循标准模板格式
> 2. 参数表格必须完整，包含AI使用提示列
> 3. 使用模式必须提供具体可执行的命令示例  
> 4. 关联文档必须使用相对路径，确保链接有效性
> 5. 文档更新后必须执行 `sync_readme.ps1` 和相关检查点验证