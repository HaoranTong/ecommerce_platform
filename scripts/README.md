<!--
文档说明：
- 内容：自动化脚本目录说明和使用指南
- 使用方法：开发者了解和使用项目自动化脚本
- 更新方法：新增或修改脚本时更新
- 更新频率：脚本变化时
-->

# 🤖 开发工具脚本

自动化开发工具集合，支持代码检查、测试执行、项目管理等功能。

## 📁 脚本分类

### 🔍 代码质量检查
| 脚本 | 功能 | 使用场景 | 自动触发 |
|------|------|----------|----------|
| `check_naming_compliance.ps1` | 命名规范合规性检查 | 代码提交前 | ✅ MASTER检查点 |
| `check_docs.ps1` | 文档结构完整性检查 | 文档更新后 | ✅ MASTER检查点 |

### 🧪 测试执行
| 脚本 | 功能 | 数据库 | 使用场景 | 自动触发 |
|------|------|--------|----------|----------|
| `check_test_env.ps1` | 快速测试环境检查 | - | 测试前环境验证 | ⚠️ **必须** |
| `validate_test_config.py` | 完整测试配置验证 | SQLite内存/文件/MySQL | 详细环境诊断 | ⚠️ **推荐** |
| `setup_test_env.ps1` | 测试环境设置和启动 | 按测试类型 | 标准测试流程 | ✅ **标准** |
| `smoke_test.ps1` | 快速烟雾测试 | SQLite文件 | 快速验证基础功能 | - |
| `integration_test.ps1` | 完整集成测试 | MySQL Docker | 模块集成验证 | - |

### 🔄 项目管理  
| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `dev-checkpoint.ps1` | 开发检查点 | 重要节点记录 |
| `feature_finish.ps1` | 功能完成流程 | 功能开发完成 |
| `release_to_main.ps1` | 发布到主分支 | 版本发布 |

## 📁 脚本目录结构

```
scripts/
├── 🧪 测试环境和执行脚本
│   ├── check_test_env.ps1           # ⚠️ 快速测试环境检查（必须）
│   ├── setup_test_env.ps1           # 🎯 测试环境设置启动（标准流程）
│   ├── validate_test_config.py      # 🔍 完整测试配置验证（推荐）
│   ├── smoke_test.ps1               # 💨 烟雾测试执行
│   └── integration_test.ps1         # 🔗 集成测试执行
├── 🔍 代码质量检查脚本  
│   ├── check_naming_compliance.ps1  # 命名规范检查脚本
│   ├── check_docs.ps1               # 文档状态检查脚本
│   └── doc_basic_check.ps1          # 基础文档检查脚本
├── 🔄 项目管理脚本
│   ├── dev-checkpoint.ps1           # 开发检查点脚本
│   ├── feature_finish.ps1           # 功能完成流程脚本
│   ├── log_status.ps1               # 状态日志记录脚本
│   ├── release_to_main.ps1          # 发布到主分支脚本
│   └── sync_env.ps1                 # 环境同步脚本
├── 🛠️ 辅助工具
│   └── _smoke_cert.py               # SSL证书验证工具
└── README.md                        # 本文档
```

## 📋 核心规范检查脚本

### 🔍 命名规范合规性检查 (必须)
```powershell
# 全面检查所有命名规范
.\scripts\check_naming_compliance.ps1

# 只检查API命名
.\scripts\check_naming_compliance.ps1 -CheckType api

# 只检查数据库命名
.\scripts\check_naming_compliance.ps1 -CheckType database

# 只检查文档命名
.\scripts\check_naming_compliance.ps1 -CheckType docs

# 只检查代码命名
.\scripts\check_naming_compliance.ps1 -CheckType code

# 尝试自动修复（谨慎使用）
.\scripts\check_naming_compliance.ps1 -Fix
```

**使用场景**：
- ✅ **开发前必须检查** - 确保环境命名规范
- ✅ **编码后必须检查** - 验证代码命名合规
- ✅ **提交前必须检查** - 确保符合规范才能提交
- ✅ **CI/CD集成** - 自动化检查流程

## 📚 文档检查脚本

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

## 🔧 开发环境脚本

### 3. 环境变量管理
```powershell
# 创建.env文件
.\scripts\sync_env.ps1 -Action create

# 检查环境
.\scripts\sync_env.ps1 -Action check
```

## 🚀 强制执行工作流程

### 📋 开发阶段必须执行的检查
```powershell
# 1. 开发前环境检查
.\scripts\check_naming_compliance.ps1
.\scripts\check_docs.ps1

# 2. 开发过程中持续检查
.\scripts\check_naming_compliance.ps1 -CheckType code

# 3. 提交前最终检查
.\scripts\check_naming_compliance.ps1
```

### 🚨 检查结果处理
- **✅ 检查通过**: 可以继续开发/提交
- **❌ 检查失败**: 必须修复所有问题后重新检查
- **⚠️ 警告信息**: 建议修复，记录原因

## 🔄 快速开始

**第一次使用**:
1. 打开PowerShell，进入项目目录
2. 检查执行策略: `Get-ExecutionPolicy`
3. 如果受限，运行: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. 运行初始检查: `.\scripts\check_naming_compliance.ps1`

**日常开发工作流**:
```powershell
# 每日开始工作前
.\scripts\check_naming_compliance.ps1

# 编写代码后
.\scripts\check_naming_compliance.ps1 -CheckType code

# Git提交前
.\scripts\check_naming_compliance.ps1
```

## 📊 脚本执行结果说明

### 退出码含义
- `0`: 检查通过，无问题
- `1`: 发现违规问题，需要修复
- `2`: 脚本执行错误

### 输出颜色说明
- 🔴 **红色**: 错误和违规问题
- 🟢 **绿色**: 成功和建议修复
- 🔵 **蓝色**: 信息和进度
- 🟡 **黄色**: 警告和分隔线
- 🔵 **青色**: 标题和分类

## ⚙️ 脚本配置

### 命名规范配置文件
脚本使用内置配置，包含：
- 模块名称映射表
- API命名规范模式
- 数据库命名规范
- 代码命名规范

如需修改配置，编辑 `.\scripts\check_naming_compliance.ps1` 中的 `$NamingConfig` 变量。

## 🐛 故障排除

### 常见问题
1. **执行策略限制**
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **路径找不到**
   - 确保在项目根目录执行
   - 检查文件路径是否正确

3. **权限不足**
   - 以管理员身份运行PowerShell
   - 检查文件访问权限

### 获取帮助
```powershell
# 查看脚本帮助
Get-Help .\scripts\check_naming_compliance.ps1 -Full
```

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

## 🧪 测试环境工具详细说明

### ⚠️ check_test_env.ps1 (必须使用)
**用途**：快速检查测试环境是否就绪，**必须在运行任何测试前执行**

**功能**：
- 检查Python虚拟环境状态
- 验证测试依赖包完整性
- 检查测试目录结构
- 验证数据库连接能力
- 30秒快速诊断

**示例**：
```powershell
# 测试前必须执行的环境检查
.\scripts\check_test_env.ps1
```

**输出示例**：
```
🎉 所有检查通过！测试环境就绪。
您可以运行以下命令开始测试:
  pytest tests/unit/ -v           # 单元测试
  pytest tests/integration/ -v    # 集成测试
  pytest tests/ -v                # 全部测试
```

### 🎯 setup_test_env.ps1 (标准流程)
**用途**：标准测试环境设置和启动流程，**推荐的测试执行方式**

**参数**：
- `-TestType <unit|smoke|integration|all>`：测试类型
- `-SetupOnly`：只设置环境，不运行测试
- `-SkipValidation`：跳过环境验证

**示例**：
```powershell
# 标准单元测试流程（推荐）
.\scripts\setup_test_env.ps1 -TestType unit

# 只设置集成测试环境，不运行测试
.\scripts\setup_test_env.ps1 -TestType integration -SetupOnly

# 运行全部测试
.\scripts\setup_test_env.ps1 -TestType all
```

**自动功能**：
- 虚拟环境检查和激活
- 测试配置验证
- 数据库环境准备（SQLite内存/文件/MySQL Docker）
- 测试执行和结果报告
- 环境清理（集成测试）

### 🔍 validate_test_config.py (推荐使用)
**用途**：完整的测试配置功能验证，深度诊断配置问题

**功能**：
- 7个验证步骤全面检查
- Python环境、依赖包、应用模块导入
- SQLite内存/文件数据库测试
- MySQL连接测试（可选）
- pytest配置验证

**示例**：
```powershell
# 详细的测试配置验证
python scripts/validate_test_config.py
```

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

## 🎯 快速使用指南

### 测试环境工具
```powershell
# 环境检查
.\scripts\check_test_env.ps1

# 测试环境设置
.\scripts\setup_test_env.ps1 -TestType <unit|integration|all>

# 详细配置验证
python scripts/validate_test_config.py
```

**详细使用流程**: 请参考 [测试标准文档](../docs/standards/testing-standards.md)

## ⚠️ 注意事项和最佳实践

### 强制性要求 (MASTER规范)
1. **测试前环境检查**：任何测试前必须运行 `.\scripts\check_test_env.ps1`
2. **使用标准工具**：推荐使用 `setup_test_env.ps1` 而非直接运行 pytest
3. **虚拟环境验证**：确保在正确的虚拟环境中执行

### 技术要求
1. **执行权限**: 确保有PowerShell脚本执行权限 (`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`)
2. **Docker要求**: 集成测试需要Docker Desktop运行
3. **环境隔离**: 不同测试类型使用不同数据库配置
3. **备份**: 重要操作前脚本会自动备份
4. **日志**: 所有操作都有详细日志记录
5. **回滚**: 支持操作回滚的脚本会提供回滚选项

## 🔗 相关文档

- [开发工作流程](../docs/development/workflow.md)
- [环境配置说明](../docs/operations/environment.md)
- [测试指南](../docs/development/testing.md)

## 新增文件

- `ai-checkpoint.ps1` - AI检查点辅助验证脚本，支持29种检查卡片类型
- `check_code_standards.ps1` - 代码标准验证工具，检查文件头、函数文档、注释密度
- `check_database_schema.ps1` - 数据库模式检查脚本
- `check_sku_id_types.ps1` - SKU ID数据类型检查工具
- `create_module_docs.ps1` - 模块文档创建脚本
- `create_module_files.ps1` - 模块文件结构创建脚本
- `create_module_readme.ps1` - 模块README文档创建脚本
- `fix_sku_id_errors.ps1` - SKU ID错误修复工具
- `fix_sku_id_types.ps1` - SKU ID类型修复工具
- `generate_test_template.py` - 测试模板生成工具
- `quick_structure_check.ps1` - 快速项目结构检查脚本
- `rebuild_database.ps1` - 数据库重建脚本
- `reset_database.ps1` - 数据库重置脚本
- `sync_readme.ps1` - README文档同步自动化工具
- `test_product_system.ps1` - 产品系统测试脚本
- `validate_pydantic_v2.py` - Pydantic V2合规性验证工具
- `verify_inventory_module.py` - 库存管理模块验证脚本

*注: 以上工具均包含完整的PowerShell帮助块或Python文档字符串*

