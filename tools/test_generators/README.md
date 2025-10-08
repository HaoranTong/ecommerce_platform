---
title: "Test Generators Tools"
version: "v1.0.1"
status: "Active"
created: "2025-10-02"
updated: "2025-10-08"
owner: "QA Lead"
category: "A5"
dependencies:
  - "../../docs/standards/document-management-standards.md"
  - "../../docs/standards/testing-standards.md"
  - "../../docs/standards/code-standards.md"
labels:
  - "testing"
  - "automation"
  - "unit-tests"
  - "code-generation"
---

# 智能测试代码生成器

> **工具概要**: 智能单元测试代码自动生成工具，支持Model/Repository/Service/业务流程的全覆盖测试生成  
> **适用场景**: 为新模块快速生成完整的单元测试代码骨架，提升测试覆盖率和开发效率  
> **技术架构**: 基于AST+运行时双重分析的智能生成架构，模块化设计，支持多种测试策略（Mock/真实数据库）

## 工具概要

### 核心能力
本工具采用智能分析引擎 + 模块化生成器的架构，通过双重分析策略（AST静态分析 + 运行时动态分析）准确提取代码结构信息，生成符合testing-standards.md v2.0.0规范的高质量单元测试代码。

**核心特性**:
- 🔍 **智能分析**: AST+运行时双重分析，准确提取模型/Repository/Service信息
- 🎯 **精准生成**: 基于分析结果生成针对性测试代码，覆盖CRUD全场景
- ✅ **质量保证**: 自动验证生成代码（语法检查、pytest收集、依赖检查），确保100%可运行
- 📊 **可视化报告**: 生成详细的质量验证报告，提供改进建议
- 🔧 **高度优化**: 主程序从7159行优化至661行（-90.8%），模块化清晰

### 适用场景
- ✅ **新模块开发**: 为新业务模块快速生成完整测试代码骨架（节省80%时间）
- ✅ **测试覆盖率提升**: 自动生成全场景测试用例，确保CRUD和业务流程全覆盖
- ✅ **测试标准化**: 生成符合项目标准的测试代码，统一测试风格和质量
- ✅ **回归测试维护**: 模块变更后快速重新生成测试，保持同步
- ✅ **学习最佳实践**: 生成的测试代码可作为pytest、Factory Boy、Mock的最佳实践参考

### 工具架构

#### 主程序
| 组件 | 文件名 | 代码行数 | 功能职责 |
|------|-------|---------|----------|
| **智能测试生成器** | `generate_test_template.py` | 661行 | 主入口程序，编排分析和生成流程 |

#### 核心模块

**1. 测试生成器 (unit/)** - 4个生成器
| 生成器 | 文件名 | 代码行数 | 测试策略 | 功能职责 |
|--------|-------|---------|----------|----------|
| Model生成器 | `model_test_generator.py` | 286行 | 100% Mock | 生成Model层单元测试 |
| Repository生成器 | `repository_test_generator.py` | 1674行 | SQLite内存库 | 生成Repository层CRUD测试 |
| Service生成器 | `service_test_generator.py` | 407行 | Mock Repository | 生成Service层业务逻辑测试 |
| 业务流程生成器 | `standalone_test_generator.py` | 420行 | SQLite内存库 | 生成业务流程端到端测试 |

**2. 通用工具 (utils/)** - 8个工具类
| 工具类型 | 工具类 | 文件名 | 功能职责 |
|---------|--------|-------|----------|
| **分析器** | ModelAnalyzer | `model_analyzer.py` | SQLAlchemy模型智能分析 |
| | RepositoryAnalyzer | `repository_analyzer.py` | Repository方法分析和分类 |
| | ServiceAnalyzer | `service_analyzer.py` | Service类检测和识别 |
| **验证器** | EnvironmentValidator | `environment_validator.py` | 测试环境配置验证 |
| | PytestChecker | `pytest_checker.py` | Pytest兼容性和依赖检查 |
| | ValidationReporter | `validation_reporter.py` | 质量验证报告生成 |
| **工具类** | TestUtils | `test_utils.py` | 测试代码生成辅助方法 |
| | TestFileWriter | `file_writer.py` | 测试文件持久化和目录管理 |

**3. 数据模型 (core/)** - 数据结构定义
| 文件名 | 功能职责 |
|-------|----------|
| `schema.py` | 定义ModelInfo、RepositoryInfo等数据模型 |

## 使用前提

### 系统要求
- **Python版本**: 3.11+
- **操作系统**: Windows/Linux/macOS
- **项目框架**: FastAPI + SQLAlchemy
- **测试框架**: pytest + pytest-mock + Factory Boy

### 依赖环境
```bash
# 核心依赖
pip install pytest pytest-mock factory-boy sqlalchemy

# 开发依赖（可选）
pip install pytest-cov pytest-html
```

### 目录结构要求
```bash
项目根目录/
├── app/modules/{module_name}/     # 待测试的业务模块
│   ├── models.py                  # 必需：数据模型定义
│   ├── repository.py              # 可选：数据访问层
│   └── service.py                 # 可选：业务逻辑层
├── tests/                         # 测试目录（自动创建）
│   ├── conftest.py               # 必需：pytest配置和fixture
│   ├── factories/                 # Factory类（自动生成）
│   └── unit/generated/            # 生成的测试（自动创建）
└── tools/test_generators/         # 本工具
```

### 必需配置
```bash
# 1. 确保测试环境配置正确
# tests/conftest.py 必须定义 unit_test_db fixture
# 参考项目中的 conftest.py 示例

# 2. 验证模块路径可访问
ls app/modules/{module_name}/models.py  # 应存在

# 3. 检查主生成器可执行
python tools/generate_test_template.py --help
```

## 快速开始

### 最简单的使用方式
```bash
# 一行命令生成所有测试
python tools/generate_test_template.py user_auth
```

**执行流程**:
1. 🔍 分析模块代码（models/repository/service）
2. ⚙️ 生成测试代码（4个测试文件）
3. 💾 保存到tests/unit/generated/user_auth/
4. ✅ 自动验证（语法/pytest/依赖）
5. 📊 生成质量报告

**预期输出**:
```
🚀 开始生成测试代码: user_auth
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 配置信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 - 目标模块: user_auth
 - 项目根目录: E:\ecommerce_platform
 - 测试输出: tests/unit/generated/user_auth/

🔍 开始智能分析模块: user_auth
✅ 分析完成，共识别 3 个数据模型
✅ 分析完成，共识别 3 个Repository

📝 生成测试代码
✅ Model测试生成完成
✅ Repository测试生成完成
✅ Service测试生成完成
✅ 业务流程测试生成完成

💾 保存测试文件
✅ 已保存: tests/unit/generated/user_auth/test_models.py
✅ 已保存: tests/unit/generated/user_auth/test_repositories.py
✅ 已保存: tests/unit/generated/user_auth/test_services.py
✅ 已保存: tests/unit/generated/user_auth/test_workflows.py

📊 测试质量验证报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 语法检查通过: 4/4
✅ pytest收集测试: 206个
✅ 依赖检查通过: 0个缺失
✅ 整体质量评分: 100分（优秀）

✨ 测试代码生成完成！
```

### 详细使用步骤

#### 步骤1: 选择目标模块
```bash
# 查看可用的业务模块
ls app/modules/
# 输出: user_auth  product_catalog  shopping_cart  order_management

# 检查模块是否满足要求
ls app/modules/user_auth/models.py      # ✅ 必需存在
ls app/modules/user_auth/repository.py  # ⚠️ 可选
ls app/modules/user_auth/service.py     # ⚠️ 可选
```

#### 步骤2: 执行生成命令
```bash
# 基本命令
python tools/generate_test_template.py user_auth

# PowerShell（Windows）
.\tools\generate_test_template.py user_auth

# 指定项目根目录（可选）
python tools/generate_test_template.py user_auth --project-root=/path/to/project
```

#### 步骤3: 验证生成结果
```bash
# 检查生成的文件
tree tests/unit/generated/user_auth/
# 预期输出:
# tests/unit/generated/user_auth/
# ├── test_models.py           (Model层测试)
# ├── test_repositories.py     (Repository层测试)
# ├── test_services.py         (Service层测试)
# └── test_workflows.py        (业务流程测试)

# 检查文件大小（确保不是空文件）
ls -lh tests/unit/generated/user_auth/
```

#### 步骤4: 运行生成的测试
```bash
# 运行所有生成的测试
pytest tests/unit/generated/user_auth/ -v

# 运行特定层的测试
pytest tests/unit/generated/user_auth/test_models.py -v
pytest tests/unit/generated/user_auth/test_repositories.py -v
pytest tests/unit/generated/user_auth/test_services.py -v
pytest tests/unit/generated/user_auth/test_workflows.py -v

# 查看测试覆盖率
pytest tests/unit/generated/user_auth/ --cov=app.modules.user_auth
```

### 命令行参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `module_name` | str | ✅ | - | 目标模块名称（app/modules/下的目录名） |
| `--project-root` | path | ❌ | 当前目录 | 项目根目录路径 |
| `--output-dir` | path | ❌ | tests/unit/generated | 测试文件输出目录 |
| `--skip-validation` | flag | ❌ | False | 跳过质量验证（不推荐） |
| `--verbose` | flag | ❌ | False | 显示详细日志 |

**示例**:
```bash
# 完整参数示例
python tools/generate_test_template.py \
    user_auth \
    --project-root=/path/to/project \
    --output-dir=tests/custom_output \
    --verbose
```

## 输出结果

### 生成文件清单

每次执行将生成4个核心测试文件：

```
tests/unit/generated/{module_name}/
├── test_models.py          # Model层单元测试（100% Mock）
├── test_repositories.py    # Repository层CRUD测试（SQLite内存数据库）
├── test_services.py        # Service层业务逻辑测试（Mock Repository）
└── test_workflows.py       # 业务流程端到端测试（SQLite内存数据库）
```

### 文件内容说明

#### 1. test_models.py - Model层测试
**测试策略**: 100% Mock，无数据库依赖  
**测试内容**:
- 模型实例化测试
- 字段约束验证
- 模型方法测试（\_\_str\_\_、to_dict等）
- 关系映射验证

**典型代码量**: 约200-500行  
**测试数量**: 约5-15个测试/模型

**示例**:
```python
class TestUserModel:
    """User模型单元测试"""
    
    def test_model_instantiation(self):
        """测试模型实例化"""
        user = User(username="test", email="test@example.com")
        assert user.username == "test"
```

---

#### 2. test_repositories.py - Repository层测试
**测试策略**: SQLite内存数据库，测试真实SQL执行  
**测试内容**:
- Create测试（最小字段/完整字段/事务）
- Read测试（单主键/联合主键/found/not_found）
- Update测试（单字段/批量/事务）
- Delete测试（物理删除/软删除/级联）
- Count测试
- Query测试（自定义查询/分页）
- 关系测试（一对多/多对一/多对多）

**典型代码量**: 约1000-3000行  
**测试数量**: 约20-50个测试/Repository

**示例**:
```python
class TestUserRepository:
    """UserRepository单元测试"""
    
    def test_create_with_minimal_fields(self, unit_test_db):
        """测试最小字段创建"""
        session, repo = unit_test_db("UserRepository")
        user = User(username="test", email="test@example.com")
        created = repo.create(session, user)
        assert created.id is not None
```

---

#### 3. test_services.py - Service层测试
**测试策略**: Mock Repository，专注业务逻辑  
**测试内容**:
- Service初始化测试
- 业务逻辑验证
- 异常处理测试
- Repository调用验证

**典型代码量**: 约300-800行  
**测试数量**: 约10-30个测试/Service

**示例**:
```python
class TestUserService:
    """UserService单元测试"""
    
    def test_create_user_success(self, mocker):
        """测试创建用户 - 成功场景"""
        mock_repo = mocker.Mock()
        mock_repo.create.return_value = User(id=1)
        service = UserService(repository=mock_repo)
        result = service.create_user(data)
        mock_repo.create.assert_called_once()
```

---

#### 4. test_workflows.py - 业务流程测试
**测试策略**: SQLite内存数据库，端到端业务流程  
**测试内容**:
- 完整业务生命周期（创建→查询→更新→删除）
- 跨Repository协作测试
- 复杂业务场景测试
- 多表关联测试

**典型代码量**: 约300-800行  
**测试数量**: 约5-15个测试/模块

**示例**:
```python
class TestUserAuthWorkflow:
    """用户认证完整业务流程测试"""
    
    def test_complete_user_lifecycle(self, unit_test_db):
        """测试用户完整生命周期"""
        session, repos = unit_test_db()
        # 创建→查询→更新→删除完整流程
```

---

### 文件头部信息

每个生成的测试文件都包含标准头部：
```python
"""
本文件由测试代码生成器自动生成
生成时间: 2025-10-08 12:00:00
生成工具版本: v1.0.1
模块: user_auth

⚠️ 警告: 请勿手动修改本文件
如需修改测试，请：
1. 修改业务代码后重新生成
2. 或在tests/unit/custom/目录下创建自定义测试
"""
```

---

### 成功标准

✅ **生成成功的标志**:
- 4个测试文件全部创建完成
- 文件内容包含有效的Python测试代码
- 语法检查100%通过
- pytest可以成功收集所有测试
- 依赖检查无缺失

✅ **质量验证标准**:
```bash
# 1. 语法检查（必须通过）
python -m py_compile tests/unit/generated/user_auth/*.py

# 2. pytest收集测试（必须成功）
pytest tests/unit/generated/user_auth/ --collect-only

# 3. 导入测试（必须无错误）
python -c "
import tests.unit.generated.user_auth.test_models
import tests.unit.generated.user_auth.test_repositories
"

# 4. 整体质量评分（目标≥95分）
# 自动生成的验证报告
```

---

### 质量验证报告

工具会自动生成质量验证报告，保存在：
```
reports/test_validation_user_auth_{timestamp}.md
```

**报告内容**:
- 📊 语法检查结果（通过/失败文件列表）
- 🧪 pytest收集结果（测试数量、收集时间）
- 🔗 依赖检查结果（缺失的Factory类、fixture）
- ⭐ 整体质量评分（0-100分）
- 💡 改进建议

**评分标准**:
- 90-100分：优秀（Excellent）
- 80-89分：良好（Good）
- 70-79分：合格（Fair）
- <70分：需要改进（Needs Improvement）

---

### 日志和调试

**控制台输出**:
- 🔍 分析进度（模型/Repository分析）
- ✅ 生成进度（各层测试生成状态）
- 💾 保存进度（文件写入确认）
- 📊 验证结果（质量评分和建议）

**日志文件**:
- `logs/test_generation_{timestamp}.log` - 详细生成日志
- `reports/test_validation_{module}_{timestamp}.md` - 质量验证报告

**调试模式**:
```bash
# 开启详细日志
python tools/generate_test_template.py user_auth --verbose

# 跳过验证（快速生成）
python tools/generate_test_template.py user_auth --skip-validation
```

## 故障排查

### 常见问题

#### 🔴 问题1: 模块路径不存在
**错误信息**:
```
⚠️ 模型文件不存在: E:\ecommerce_platform\app\modules\xxx\models.py
```

**原因分析**:
- 模块名称拼写错误
- 模块目录不存在
- models.py文件缺失

**解决方案**:
```bash
# 1. 检查模块是否存在
ls app/modules/ | grep {module_name}

# 2. 检查必需文件
ls app/modules/{module_name}/models.py

# 3. 确认模块名称拼写（区分大小写）
# 正确: user_auth
# 错误: UserAuth, user-auth
```

---

#### 🔴 问题2: pytest收集测试失败
**错误信息**:
```
ERROR collecting tests/unit/generated/user_auth/test_repositories.py
ImportError: cannot import name 'UserFactory' from 'tests.factories'
```

**原因分析**:
- Factory类未定义
- conftest.py配置错误
- 依赖包未安装

**解决方案**:
```bash
# 1. 检查Factory类是否存在
ls tests/factories/{module}_factory.py

# 2. 检查conftest.py中的unit_test_db fixture
cat tests/conftest.py | grep "unit_test_db"

# 3. 安装必需依赖
pip install pytest pytest-mock factory-boy

# 4. 手动创建缺失的Factory类（如需要）
```

---

#### 🔴 问题3: 生成的测试代码有语法错误
**错误信息**:
```
SyntaxError: invalid syntax
  File "tests/unit/generated/user_auth/test_repositories.py", line 123
```

**原因分析**:
- 生成器bug（缩进错误、括号不匹配等）
- 模型定义不规范（如字段名为Python关键字）

**解决方案**:
```bash
# 1. 检查语法
python -m py_compile tests/unit/generated/user_auth/test_repositories.py

# 2. 查看具体错误行
cat tests/unit/generated/user_auth/test_repositories.py | sed -n '120,125p'

# 3. 如果是生成器bug，清理并重新生成
rm tests/unit/generated/user_auth/*
python tools/generate_test_template.py user_auth

# 4. 如果问题持续，请报告bug并附带：
#    - 错误日志
#    - models.py内容
#    - 生成的测试代码片段
```

---

#### 🔴 问题4: 缺失依赖错误
**错误信息**:
```
ModuleNotFoundError: No module named 'factory'
ModuleNotFoundError: No module named 'pytest_mock'
```

**原因分析**:
- 测试环境依赖未安装

**解决方案**:
```bash
# 安装完整依赖
pip install pytest pytest-mock factory-boy sqlalchemy

# 或使用项目requirements
pip install -r requirements_dev.txt

# 验证安装
python -c "import pytest, pytest_mock, factory; print('✅ 依赖已安装')"
```

---

#### 🔴 问题5: unit_test_db fixture不可用
**错误信息**:
```
fixture 'unit_test_db' not found
```

**原因分析**:
- conftest.py中未定义unit_test_db fixture
- conftest.py路径错误

**解决方案**:
```bash
# 1. 检查conftest.py是否存在
ls tests/conftest.py

# 2. 检查unit_test_db fixture定义
cat tests/conftest.py | grep -A 10 "def unit_test_db"

# 3. 如果缺失，参考项目中的conftest.py示例
# 或手动添加fixture定义
```

---

### 环境验证

在生成测试之前，可以运行环境检查：

```bash
# 检查Python版本
python --version  # 应显示 3.11+

# 检查依赖安装
pip list | grep -E "pytest|factory|sqlalchemy"

# 检查项目结构
ls -la app/modules/{module_name}/models.py
ls -la tests/conftest.py

# 验证可以导入模块
python -c "from app.modules.{module_name}.models import *; print('✅ 模块可导入')"
```

---

### 清理和重新生成

如果生成出现问题，可以清理并重新生成：

```bash
# 方案1: 仅清理目标模块的生成文件
rm -rf tests/unit/generated/{module_name}/

# 方案2: 清理所有generated目录
rm -rf tests/unit/generated/

# 重新生成
python tools/generate_test_template.py {module_name}
```

---

### 调试技巧

#### 开启详细日志
```bash
python tools/generate_test_template.py user_auth --verbose
```

#### 逐步验证
```bash
# 1. 验证分析阶段
python -c "
from pathlib import Path
from tools.test_generators.utils import ModelAnalyzer
analyzer = ModelAnalyzer(Path.cwd())
models = analyzer.analyze_module_models('user_auth')
print(f'分析到 {len(models)} 个模型')
"

# 2. 验证生成阶段（跳过保存）
# 修改generate_test_template.py，添加--dry-run参数

# 3. 验证保存阶段
ls -la tests/unit/generated/user_auth/
```

---

### 获取帮助

#### 文档资源
- [工具总体README](README.md) - 本文档
- [工具模块文档](utils/README.md) - 通用工具详细说明
- [生成器文档](unit/README.md) - 生成器详细说明
- [测试标准](../../docs/standards/testing-standards.md) - 测试规范
- [代码标准](../../docs/standards/code-standards.md) - 编码规范

#### 问题报告
如遇到无法解决的问题，请提交issue并包含：
1. **错误信息**: 完整的错误堆栈
2. **环境信息**: Python版本、OS、依赖版本
3. **重现步骤**: 导致错误的命令和操作
4. **相关代码**: models.py等相关代码片段
5. **生成日志**: 工具的完整输出

**提交方式**:
- GitHub Issue: https://github.com/{org}/{repo}/issues
- 内部Jira: 项目测试工具类别

---

## 工具架构说明

### 模块依赖关系

```
主程序 (generate_test_template.py)
  │
  ├─ 分析器 (Analyzers)
  │  ├─ ModelAnalyzer      → 分析SQLAlchemy模型
  │  ├─ RepositoryAnalyzer → 分析Repository方法
  │  └─ ServiceAnalyzer    → 分析Service类
  │
  ├─ 生成器 (Generators)
  │  ├─ ModelTestGenerator          → 生成Model测试
  │  ├─ RepositoryTestGenerator     → 生成Repository测试
  │  ├─ ServiceTestGenerator        → 生成Service测试
  │  └─ StandaloneTestGenerator     → 生成业务流程测试
  │
  ├─ 验证器 (Validators)
  │  ├─ EnvironmentValidator  → 环境配置验证
  │  ├─ PytestChecker         → Pytest兼容性检查
  │  └─ ValidationReporter    → 质量报告生成
  │
  └─ 工具类 (Utilities)
     ├─ TestUtils      → 测试代码生成辅助
     └─ TestFileWriter → 文件持久化管理
```

### 代码优化历程

| 阶段 | 版本 | 代码行数 | 优化内容 |
|------|------|---------|----------|
| 初始版本 | v0.1 | 7159行 | 单体程序，所有功能耦合 |
| 第一轮优化 | v0.5 | 3500行 | 提取生成器类 |
| 第二轮优化 | v0.8 | 1500行 | 提取分析器和工具类 |
| **当前版本** | **v1.0.1** | **661行** | 完全模块化，主程序仅编排 |
| 优化成果 | - | **-6498行** | **-90.8%代码量** |

### 质量保证

**代码质量**:
- ✅ 符合code-standards.md规范
- ✅ 符合naming-conventions-standards.md命名规范
- ✅ 所有文件包含完整的文档字符串
- ✅ 每个工具类包含使用示例

**生成质量**:
- ✅ 生成的测试代码100%符合testing-standards.md v2.0.0
- ✅ 自动语法检查（Python ast模块）
- ✅ 自动pytest收集验证
- ✅ 自动依赖完整性检查
- ✅ 综合质量评分（0-100分）

**已修复的Bug**:
1. ✅ RepositoryTestGenerator缩进错误（严重bug，已修复）
2. ✅ PytestChecker误报依赖（中等bug，已修复）

---

## 版本历史

### v1.0.1 (2025-10-08) - 当前版本
**新增**:
- ✅ 完整的文件头部文档（符合code-standards.md）
- ✅ utils/和unit/子目录README文档
- ✅ 规范符合性检查报告

**修复**:
- ✅ RepositoryTestGenerator缩进错误
- ✅ PytestChecker误报依赖问题
- ✅ ValidationReporter引用错误

**优化**:
- ✅ 主README更新（反映当前架构）
- ✅ 所有工具类添加使用示例
- ✅ 完善故障排查指南

### v1.0.0 (2025-10-06)
**初始发布**:
- 🎉 模块化架构完成
- 🎉 4个核心生成器
- 🎉 8个通用工具类
- 🎉 完整的质量验证流程

**代码优化**:
- 主程序从7159行优化至661行（-90.8%）
- 提取14个模块化组件
- 消除代码重复和未使用方法

### v0.x - 历史版本
- v0.8: 第二轮优化，提取分析器和工具类
- v0.5: 第一轮优化，提取生成器类
- v0.1: 初始版本，单体程序

---

## 未来规划

### 短期计划 (v1.1.x)
- [ ] 支持选择性生成（仅生成特定层的测试）
- [ ] 支持自定义测试模板
- [ ] 支持增量生成（仅更新变更的测试）
- [ ] 添加交互式模式（引导式生成）

### 中期计划 (v1.2.x)
- [ ] 支持更多ORM框架（Tortoise ORM、Peewee）
- [ ] 支持GraphQL API测试生成
- [ ] 支持gRPC服务测试生成
- [ ] 添加测试覆盖率分析

### 长期计划 (v2.0.x)
- [ ] 集成AI辅助测试用例生成
- [ ] 智能识别边界条件和异常场景
- [ ] 自动生成测试数据生成器
- [ ] 支持多语言测试生成（TypeScript、Go等）

---

## 维护信息

### 维护责任
- **主要维护人**: QA Lead
- **协作维护人**: Tech Lead（架构变更时）
- **代码审核**: 各模块负责人

### 维护频率
- **日常维护**: 每周检查issue和bug报告
- **月度验证**: 每月验证工具可用性和生成质量
- **季度优化**: 每季度代码优化和性能提升
- **年度升级**: 每年大版本升级（新特性）

### 标准同步
- 测试标准更新时，同步更新生成模板
- 代码标准更新时，同步更新生成代码风格
- 框架升级时，同步更新分析和生成逻辑

### 贡献指南
欢迎贡献代码和建议！贡献方式：
1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

**贡献要求**:
- ✅ 遵循项目代码规范
- ✅ 添加单元测试
- ✅ 更新相关文档
- ✅ 通过所有质量检查

---

## 许可证
本工具遵循项目整体许可证。

---

## 相关文档

### 工具文档
- [通用工具模块](utils/README.md) - 8个工具类详细说明
- [单元测试生成器](unit/README.md) - 4个生成器详细说明
- [规范符合性报告](COMPLIANCE_CHECK_REPORT.md) - 工具规范性检查

### 项目标准
- [测试标准](../../docs/standards/testing-standards.md) - testing-standards.md v2.0.0
- [代码标准](../../docs/standards/code-standards.md) - 编码规范
- [命名规范](../../docs/standards/naming-conventions-standards.md) - 命名约定
- [文档标准](../../docs/standards/document-management-standards.md) - 文档管理

---

**最后更新**: 2025-10-08  
**文档维护**: QA Lead