# 测试环境配置指南

📝 **文档说明**：
- **内容**：详细的测试环境配置、工具使用、故障排除指南
- **使用者**：开发人员、测试人员、AI助手
- **更新频率**：测试工具或环境配置变更时更新
- **关联文档**：[测试标准](../standards/testing-standards.md)、[工作流程规范](../standards/workflow-standards.md)

## 🎯 快速测试执行

> **测试类型和执行策略**: 详见 [测试标准文档](../standards/testing-standards.md)  
> **测试执行命令**: 详见 [工具脚本使用指南](../tools/README.md)

## 🎯 测试环境配置说明

> **权威参考**: 完整的测试架构、策略和标准定义详见 [测试标准文档](../standards/testing-standards.md)  
> **本文档职责**: 基于标准规范的具体环境配置步骤、工具安装和故障排除

### 📊 **环境配置模式对照**

根据 [测试标准文档](../standards/testing-standards.md) 中定义的五层测试架构，本配置指南支持以下环境模式：

| **配置模式** | **对应测试层级** | **数据库配置** | **使用场景** |
|-------------|----------------|-------------|-------------|
| **lite模式** | 单元测试层级 | SQLite内存/文件 | 日常开发测试 |
| **full模式** | 集成测试层级 | MySQL Docker | 集成验证测试 |

> � **重要**: 具体的测试分层定义、数据库策略和架构设计请参考 [测试标准文档](../standards/testing-standards.md) 第53-65行

## 📋 标准测试执行流程模板

### 🚀 完整测试执行检查清单

**测试执行标准流程**：详见 [测试标准文档](../standards/testing-standards.md)

**脚本使用步骤**：详见 [工具脚本使用指南](../tools/README.md)

## 🛠️ 测试工具使用指南

### 🤖 `check_test_env.ps1` - 智能测试环境检查工具

**功能描述**: 电商平台专用的智能化测试环境验证工具，支持分层检查和模式分离。

#### 核心特性
- **分层验证**: 虚拟环境 → 基础依赖 → 项目结构 → 模式特定检查
- **快速失败**: 关键步骤失败立即停止，提供明确修复建议
- **双模式支持**: lite模式（单元测试）和full模式（集成测试）
- **智能检测**: 自动识别Docker状态和服务运行情况

#### 使用方法
```powershell
# 轻量模式检查（默认）- 适用于单元测试
.\tools\check_test_env.ps1
.\tools\check_test_env.ps1 -TestMode lite

# 完整模式检查 - 适用于集成测试  
.\tools\check_test_env.ps1 -TestMode full
```

#### 检查流程

**第1步: 虚拟环境激活与验证**
- 自动激活.venv虚拟环境
- 验证Python版本（3.8+）
- 确认虚拟环境路径正确

**第2步: 基础依赖验证**
- pytest (测试框架)
- sqlalchemy (数据库ORM)
- fastapi (Web框架)
- httpx (HTTP客户端)
- pydantic (数据验证)

**第3步: 项目结构验证**
- 测试目录结构 (tests/, tests/unit/, tests/factories/)
- 配置文件 (pyproject.toml, tests/conftest.py)
- pytest配置验证

**第4步: 模式特定检查**
- **lite模式**: pytest-mock, factory_boy, SQLite内存数据库
- **full模式**: Docker环境, docker-compose服务, MySQL/Redis连接

#### 输出示例
```powershell
# 基本使用
.\scripts\check_test_env.ps1

# 输出示例 (成功)
🔍 快速测试环境检查
========================================
✅ Python虚拟环境
✅ Python包: pytest
✅ Python包: sqlalchemy
✅ Python包: fastapi
✅ Python包: httpx
✅ 测试目录: tests
✅ 测试目录: tests/unit
✅ 测试目录: tests/integration
✅ 测试目录: tests/e2e
✅ pytest配置文件
✅ SQLite数据库
✅ Docker (集成测试可选)

```powershell
# lite模式成功输出
ℹ️  🔍 测试环境检查 - lite 模式
==================================================

📋 第1步：虚拟环境激活与验证
==================================================
✅ 虚拟环境激活
   Python路径: E:\ecommerce_platform\.venv\Scripts\python.exe
✅ Python版本
   Python 3.11.9

📋 第2步：基础依赖验证
==================================================
✅ 数据验证 - Python包: pydantic
✅ 测试框架 - Python包: pytest
✅ 数据库ORM - Python包: sqlalchemy
✅ HTTP客户端 - Python包: httpx
✅ Web框架 - Python包: fastapi

📋 第3步：项目结构验证
==================================================
✅ 测试根目录 - tests
✅ 单元测试目录 - tests/unit
✅ 测试工厂目录 - tests/factories
✅ 项目配置文件 - pyproject.toml
✅ pytest配置 - pyproject.toml中的[tool.pytest.ini_options]

📋 第4步：轻量模式特定检查
==================================================
✅ Mock功能 - Python包: pytest-mock
✅ 测试数据工厂 - Python包: factory_boy
✅ SQLite内存数据库 - 轻量模式数据库
✅ 🎉 轻量模式环境检查通过！

ℹ️  可以运行以下测试命令:
  pytest tests/unit/ -v           # 单元测试
  pytest tests/unit/ --cov=app    # 单元测试 + 覆盖率
```

---

### `setup_test_env.ps1` - 统一测试环境管理工具

**功能描述**: 电商平台测试环境的统一管理入口，支持环境检查和设置的完整工作流程。

#### 核心特性
- **统一入口**: 所有测试环境操作的单一入口点
- **职责分离**: 委托专业脚本进行环境检查
- **双工作模式**: CheckOnly（仅检查）和Setup（检查+设置）
- **参数标准化**: 使用TestMode参数替代旧版TestType

#### 参数说明
```powershell
-TestMode <模式>    # lite|full (默认: lite)
-CheckOnly         # 仅检查环境，不进行设置
-AutoFix          # 自动修复发现的问题
-Verbose          # 显示详细信息
```

#### 使用方法

**基础使用**
```powershell
# 默认lite模式，进行环境设置
.\scripts\setup_test_env.ps1

# 仅检查lite环境状态
.\scripts\setup_test_env.ps1 -CheckOnly

# 仅检查full环境状态（包括Docker）
.\scripts\setup_test_env.ps1 -TestMode full -CheckOnly
```

**高级使用**
```powershell
# 设置完整测试环境
.\scripts\setup_test_env.ps1 -TestMode full

# 自动修复环境问题
.\scripts\setup_test_env.ps1 -TestMode full -AutoFix

# 详细模式显示更多信息
.\scripts\setup_test_env.ps1 -TestMode full -Verbose
```

#### 工作流程

**CheckOnly模式（仅检查）**:
1. 调用check_test_env.ps1进行专业检查
2. 返回详细的环境状态报告
3. 不进行任何修改或设置操作

**Setup模式（检查+设置）**:
1. 首先执行完整环境检查
2. 根据TestMode启动相应服务
3. 进行必要的环境配置
4. 验证设置结果

#### 环境模式对比

| 特性 | lite模式 | full模式 |
|------|---------|----------|
| **用途** | 单元测试 | 集成测试 |
| **数据库** | SQLite内存 | MySQL (Docker) |
| **Mock** | pytest-mock | 真实服务 |
| **Docker** | 不需要 | 必需 |
| **启动时间** | < 5秒 | 30-60秒 |
| **资源占用** | 低 | 中等 |

#### 使用场景

**场景1：快速单元测试** 
```powershell
.\scripts\setup_test_env.ps1 -TestMode lite

```bash
.\scripts\setup_test_env.ps1 -TestMode lite           # 轻量测试（单元测试）
.\scripts\setup_test_env.ps1 -TestMode full          # 完整测试（集成测试）
.\scripts\setup_test_env.ps1 -TestMode full           # 全部测试（推荐full模式）
.\scripts\setup_test_env.ps1 -TestMode lite -CheckOnly      # 仅检查环境，不进行设置
```

### validate_test_config.py 诊断工具

> **基本用法**: 详见 [测试标准文档](../standards/testing-standards.md)

#### 详细验证内容
```powershell
.\scripts\setup_test_env.ps1 -TestMode full

# 执行流程：
# 1-5. 同上环境准备
# 6. 执行集成测试 (pytest tests/integration/ -v)
# 7. 清理Docker容器
# 8. 生成测试报告
```

**场景4：完整测试套件**
```powershell
.\scripts\setup_test_env.ps1 -TestMode full

# 执行流程：
# 1. 准备所有测试环境
# 2. 依次执行：单元测试 → 集成测试 → E2E测试
# 3. 清理所有环境
# 4. 生成综合测试报告
```

### 3. validate_test_config.py - 深度配置验证

#### 功能说明
7步详细验证，深度诊断测试配置问题，用于故障排查。

#### 验证步骤
```python
1. Python环境验证       # Python版本、虚拟环境状态
2. 测试依赖包验证       # 所有必需包的安装状态
3. 应用模块导入验证     # 核心模块导入能力测试
4. 单元测试配置验证     # SQLite内存数据库功能测试
5. 烟雾测试配置验证     # SQLite文件数据库功能测试
6. 集成测试配置验证     # MySQL连接测试 (可选)
7. pytest配置验证      # pytest配置文件和目录结构
```

#### 使用示例
```powershell
python scripts/validate_test_config.py

# 输出示例 (部分)
🔍 测试环境配置验证开始
==================================================
=== Python环境验证 ===
✅ Python版本: 3.11.9
✅ 虚拟环境已激活: E:\ecommerce_platform\.venv
✅ 项目根目录: E:\ecommerce_platform

=== 测试依赖包验证 ===
✅ pytest - 已安装
✅ sqlalchemy - 已安装
✅ fastapi - 已安装

=== 单元测试配置验证 ===
✅ SQLite内存数据库连接成功
✅ 数据库会话创建成功

📊 验证结果: 7个通过, 0个失败
🎉 所有测试环境配置验证通过！可以开始运行测试。
```

## 🚨 故障排除指南

### 常见问题与解决方案

#### 问题1：虚拟环境未激活
```
❌ Python虚拟环境
   当前Python: C:\Python39\python.exe
```
**解决方案**：
```powershell
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 验证激活
python -c "import sys; print(sys.prefix)"
```

#### 问题2：依赖包缺失
```
❌ Python包: pytest - 未安装
```
**解决方案**：
```powershell
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 或安装完整依赖
pip install -r requirements.txt
```

#### 问题3：测试目录结构问题
```
❌ 测试目录: tests/unit
```
**解决方案**：
```powershell
# 检查目录结构
ls tests/

# 创建缺失目录
mkdir tests/unit, tests/integration, tests/e2e
```

#### 问题4：Docker环境问题
```
⚠️ MySQL测试数据库不可用: Can't connect to MySQL
```
**解决方案**：
```powershell
# 检查Docker状态
docker --version

# 启动Docker Desktop
# 然后重新运行测试
.\scripts\setup_test_env.ps1 -TestMode full
```

#### 问题5：SQLAlchemy模型关系错误
```
❌ One or more mappers failed to initialize - can't proceed
```
**解决方案**：
```powershell
# 运行详细验证
python scripts/validate_test_config.py

# 检查模型导入
python -c "from app.modules.user_auth.models import User; print('OK')"

# 重新生成数据库
rm tests/smoke_test.db
.\scripts\setup_test_env.ps1 -TestMode lite  # smoke测试建议使用轻量模式
```

### 环境重置步骤

**完全重置测试环境**：
```powershell
# 第一步：清理测试数据库文件
Remove-Item tests/smoke_test.db -Force -ErrorAction SilentlyContinue

# 第二步：停止并清理Docker容器（如果使用docker-compose）
docker-compose down
docker-compose up -d

# 或者重启特定的测试容器
docker restart ecommerce_platform-mysql-test

# 第三步：重新验证环境
.\scripts\check_test_env.ps1

# 第四步：重新运行测试
.\scripts\setup_test_env.ps1 -TestMode lite
```

## 🏭 测试数据工厂使用指南

> **权威参考**: 双工厂架构设计和使用标准详见 [测试标准文档](../standards/testing-standards.md) 双工厂架构章节  
> **本文档职责**: 基于标准规范的工厂配置和使用步骤

### 📋 **工厂使用快速参考**

根据 [测试标准文档](../standards/testing-standards.md) 中定义的双工厂架构：

| **测试场景** | **推荐工厂** | **配置说明** |
|-------------|-------------|-------------|
| **单元测试** | Factory Boy工厂 | 详见测试标准文档 Factory Boy章节 |
| **集成测试** | 统一工厂 | 详见测试标准文档 统一工厂章节 |

### ⚠️ **环境配置要点**

- **factory_boy包**: 通过 `pip install factory_boy` 安装
- **使用示例**: 参考 [测试标准文档](../standards/testing-standards.md) 中的详细示例
- **避免错误**: 详见测试标准文档中的禁止用法章节

## 📊 测试执行最佳实践

### 开发阶段测试策略
```powershell
# 开发过程中：频繁运行单元测试
.\scripts\setup_test_env.ps1 -TestMode lite

# 功能完成后：运行集成测试
.\scripts\setup_test_env.ps1 -TestMode full

# 提交前：运行完整测试套件
.\scripts\setup_test_env.ps1 -TestMode full
```

### 持续集成环境配置
```yaml
# CI/CD管道中的测试步骤
steps:
  - name: Setup Test Environment
    run: .\scripts\check_test_env.ps1
    
  - name: Run Unit Tests
    run: .\scripts\setup_test_env.ps1 -TestMode lite
    
  - name: Run Integration Tests
    run: .\scripts\setup_test_env.ps1 -TestMode full
```

## 📋 **测试代码生成工具**

> **代码生成标准**: 测试脚本编写规范和命名标准详见 [测试标准文档](../standards/testing-standards.md) 测试文件组织章节  
> **本文档职责**: 测试代码生成工具的配置和使用

### 🛠️ **自动化测试生成**

使用项目提供的测试代码生成工具：

```powershell
# 生成标准测试文件模板
python scripts/generate_test_template.py module_name function_name

# 验证测试文件结构
python scripts/validate_test_structure.py
```

> 💡 **重要**: 生成的测试代码遵循 [测试标准文档](../standards/testing-standards.md) 中定义的命名规范和结构标准

## 相关文档

- **主文档**: [测试标准文档](../standards/testing-standards.md) - 测试规范和标准流程
- [工作流程规范](../standards/workflow-standards.md) - 开发流程中的测试环节
- [MASTER文档](../../MASTER.md) - 强制检查点
