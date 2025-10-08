---
title: "Unit Test Generators"
version: "1.0.0"
status: "Active"
created: "2025-10-08"
updated: "2025-10-08"
owner: "QA Lead"
category: "A5"
parent: "../README.md"
labels:
  - "testing"
  - "generators"
  - "unit-tests"
---

# 测试生成器 - 单元测试生成器模块

> **模块概要**: 智能生成各层单元测试代码，覆盖Model/Repository/Service/业务流程  
> **适用场景**: 为新模块快速生成完整的单元测试代码骨架  
> **技术架构**: 模块化生成器设计，每个生成器专注于一层的测试代码生成

## 模块组成

### 核心生成器 (4个)

#### 1. ModelTestGenerator - Model测试生成器
**文件**: `model_test_generator.py`  
**职责**: 生成SQLAlchemy模型层单元测试代码  
**测试策略**: 100% Mock，无数据库依赖

**生成的测试类型**:
- ✅ 模型实例化测试
- ✅ 字段约束验证测试
- ✅ 模型方法测试（\_\_str\_\_、to_dict等）
- ✅ 关系映射验证测试

**技术栈**:
- pytest (测试框架)
- unittest.mock (Mock对象)

**生成示例**:
```python
class TestUserModel:
    """User模型单元测试"""
    
    def test_model_instantiation(self):
        """测试模型实例化"""
        user = User(username="test", email="test@example.com")
        assert user.username == "test"
    
    def test_field_constraints(self):
        """测试字段约束"""
        # 验证nullable、unique等
```

**使用方式**:
```python
from tools.test_generators.unit.model_test_generator import ModelTestGenerator

generator = ModelTestGenerator(project_root=Path.cwd(), config={})
test_code = generator.generate_model_tests("user_auth", models)
```

**性能指标**:
- 生成速度: 约20-50ms（取决于模型数量）
- 测试执行: <10ms/测试（无I/O）

---

#### 2. RepositoryTestGenerator - Repository测试生成器
**文件**: `repository_test_generator.py` (1673行)  
**职责**: 生成Repository层完整CRUD测试代码  
**测试策略**: 使用SQLite内存数据库，真实SQL验证

**生成的测试类型**:
- ✅ Create测试（最小字段/完整字段/事务提交/事务回滚）
- ✅ Read测试（单主键/联合主键/found/not_found）
- ✅ Update测试（单字段/批量/事务/专用方法）
- ✅ Delete测试（物理删除/软删除/级联/批量）
- ✅ Count测试（基础计数/条件计数）
- ✅ Query测试（自定义查询/复杂条件/分页）
- ✅ 关系测试（一对多/多对一/多对多）

**技术栈**:
- pytest (测试框架)
- Factory Boy (测试数据生成)
- SQLite (内存数据库)
- unit_test_db fixture

**生成示例**:
```python
class TestUserRepository:
    """UserRepository单元测试"""
    
    def test_create_with_minimal_fields(self, unit_test_db):
        """测试最小字段创建"""
        session, repo = unit_test_db("UserRepository")
        
        user = User(username="test", email="test@example.com")
        created = repo.create(session, user)
        
        assert created.id is not None
        assert created.username == "test"
    
    def test_get_by_id_found(self, unit_test_db):
        """测试按ID查询 - 存在情况"""
        session, repo = unit_test_db("UserRepository")
        
        # 先创建
        user = UserFactory.create(session=session)
        
        # 再查询
        found = repo.get_by_id(session, user.id)
        assert found is not None
        assert found.id == user.id
```

**使用方式**:
```python
from tools.test_generators.unit.repository_test_generator import RepositoryTestGenerator

generator = RepositoryTestGenerator(project_root=Path.cwd(), config={})
test_code = generator.generate_repository_tests("user_auth", repositories, models)
```

**性能指标**:
- 生成速度: 约100-200ms（取决于方法数量）
- 测试执行: <50ms/测试（SQLite内存数据库）
- 代码长度: 可能>2000行（建议分文件）

**特殊功能**:
- 自动识别联合主键
- 自动处理软删除字段
- 支持级联删除测试
- 支持事务回滚测试

---

#### 3. ServiceTestGenerator - Service测试生成器
**文件**: `service_test_generator.py`  
**职责**: 生成Service层Mock测试代码  
**测试策略**: 100% Mock Repository，专注业务逻辑

**生成的测试类型**:
- ✅ Service初始化测试
- ✅ Mock Repository测试
- ✅ 业务逻辑验证测试
- ✅ 异常处理测试
- ✅ Repository调用验证测试

**技术栈**:
- pytest (测试框架)
- pytest-mock (Mock功能)
- unittest.mock

**生成示例**:
```python
class TestUserService:
    """UserService单元测试"""
    
    def test_create_user_success(self, mocker):
        """测试创建用户 - 成功场景"""
        # Mock repository
        mock_repo = mocker.Mock()
        mock_repo.create.return_value = User(id=1, username="test")
        
        # 调用service
        service = UserService(repository=mock_repo)
        result = service.create_user(data)
        
        # 验证调用
        mock_repo.create.assert_called_once_with(data)
        assert result.username == "test"
    
    def test_create_user_duplicate(self, mocker):
        """测试创建用户 - 重复场景"""
        mock_repo = mocker.Mock()
        mock_repo.create.side_effect = ValueError("Duplicate")
        
        service = UserService(repository=mock_repo)
        with pytest.raises(ValueError):
            service.create_user(data)
```

**使用方式**:
```python
from tools.test_generators.unit.service_test_generator import ServiceTestGenerator

generator = ServiceTestGenerator(project_root=Path.cwd(), config={})
test_code = generator.generate_service_tests("user_auth", models, repositories)
```

**性能指标**:
- 生成速度: 约50-100ms
- 测试执行: <5ms/测试（无I/O）

**测试重点**:
- 业务规则验证
- 异常处理逻辑
- Repository调用参数
- Repository调用次数

---

#### 4. StandaloneTestGenerator - 业务流程测试生成器
**文件**: `standalone_test_generator.py`  
**职责**: 生成独立的业务流程端到端测试  
**测试策略**: 使用SQLite内存数据库，测试完整业务流程

**生成的测试类型**:
- ✅ 完整业务生命周期测试（创建→查询→更新→删除）
- ✅ 跨Repository协作测试
- ✅ 复杂业务场景测试
- ✅ 多表关联测试
- ✅ 边界和异常场景测试

**技术栈**:
- pytest (测试框架)
- Factory Boy (测试数据)
- SQLite (内存数据库)
- unit_test_db fixture

**生成示例**:
```python
class TestUserAuthWorkflow:
    """用户认证完整业务流程测试"""
    
    def test_complete_user_lifecycle(self, unit_test_db):
        """测试用户完整生命周期"""
        session, repos = unit_test_db()
        user_repo = repos["UserRepository"]
        
        # 1. 创建用户
        user = UserFactory.create(session=session)
        assert user.id is not None
        
        # 2. 查询用户
        found = user_repo.get_by_id(session, user.id)
        assert found.username == user.username
        
        # 3. 更新用户
        user_repo.update(session, user.id, {"email": "new@example.com"})
        updated = user_repo.get_by_id(session, user.id)
        assert updated.email == "new@example.com"
        
        # 4. 删除用户
        user_repo.delete(session, user.id)
        deleted = user_repo.get_by_id(session, user.id)
        assert deleted is None
    
    def test_user_role_association(self, unit_test_db):
        """测试用户-角色关联"""
        session, repos = unit_test_db()
        
        # 跨Repository协作
        user = UserFactory.create(session=session)
        role = RoleFactory.create(session=session)
        
        user_role_repo = repos["UserRoleRepository"]
        user_role_repo.add_role_to_user(session, user.id, role.id)
        
        roles = user_role_repo.get_user_roles(session, user.id)
        assert role.id in [r.id for r in roles]
```

**使用方式**:
```python
from tools.test_generators.unit.standalone_test_generator import StandaloneTestGenerator

generator = StandaloneTestGenerator(project_root=Path.cwd(), config={})
test_code = generator.generate_workflow_tests("user_auth", models)
```

**性能指标**:
- 生成速度: 约50-100ms
- 测试执行: <200ms/测试（完整流程）

**适用场景**:
- 验证完整业务流程正确性
- 测试多表数据一致性
- 验证复杂业务规则
- 端到端场景回归测试

---

## 生成器对比

| 维度 | Model | Repository | Service | Standalone |
|------|-------|------------|---------|-----------|
| **测试层次** | 模型层 | 数据访问层 | 业务逻辑层 | 业务流程层 |
| **数据库依赖** | 无（Mock） | 有（SQLite） | 无（Mock） | 有（SQLite） |
| **测试速度** | 极快(<10ms) | 快(<50ms) | 极快(<5ms) | 中等(<200ms) |
| **测试范围** | 模型定义 | CRUD操作 | 业务逻辑 | 完整流程 |
| **Mock策略** | 100% Mock | 真实数据库 | Mock Repository | 真实数据库 |
| **代码长度** | 短(~200行) | 长(>2000行) | 中等(~500行) | 中等(~500行) |
| **主要依赖** | unittest.mock | Factory Boy | pytest-mock | Factory Boy |

---

## 使用流程

### 1. 分析模块
```python
from pathlib import Path
from tools.test_generators.utils import (
    ModelAnalyzer,
    RepositoryAnalyzer
)

# 分析目标模块
model_analyzer = ModelAnalyzer(project_root=Path.cwd())
repo_analyzer = RepositoryAnalyzer(project_root=Path.cwd())

models = model_analyzer.analyze_module_models("user_auth")
repositories = repo_analyzer.analyze_module_repositories("user_auth")
```

### 2. 生成测试代码
```python
from tools.test_generators.unit import (
    ModelTestGenerator,
    RepositoryTestGenerator,
    ServiceTestGenerator,
    StandaloneTestGenerator
)

# 初始化生成器
config = {"project_root": Path.cwd()}
model_gen = ModelTestGenerator(Path.cwd(), config)
repo_gen = RepositoryTestGenerator(Path.cwd(), config)
service_gen = ServiceTestGenerator(Path.cwd(), config)
workflow_gen = StandaloneTestGenerator(Path.cwd(), config)

# 生成测试代码
model_tests = model_gen.generate_model_tests("user_auth", models)
repo_tests = repo_gen.generate_repository_tests("user_auth", repositories, models)
service_tests = service_gen.generate_service_tests("user_auth", models, repositories)
workflow_tests = workflow_gen.generate_workflow_tests("user_auth", models)
```

### 3. 保存测试文件
```python
from tools.test_generators.utils import TestFileWriter

writer = TestFileWriter(project_root=Path.cwd())

test_files = {
    "tests/unit/generated/user_auth/test_models.py": model_tests,
    "tests/unit/generated/user_auth/test_repositories.py": repo_tests,
    "tests/unit/generated/user_auth/test_services.py": service_tests,
    "tests/unit/generated/user_auth/test_workflows.py": workflow_tests
}

writer.write_test_files(test_files)
```

### 4. 验证测试质量
```python
from tools.test_generators.utils import ValidationReporter

reporter = ValidationReporter()

# 执行验证
validation_results = reporter.validate_generated_tests("user_auth")

# 生成报告
reporter.generate_validation_report(validation_results, "user_auth")
reporter.summarize_validation_results(validation_results)
```

---

## 生成的测试文件结构

```
tests/unit/generated/{module_name}/
├── test_models.py          # Model层测试（100% Mock）
├── test_repositories.py    # Repository层测试（SQLite）
├── test_services.py        # Service层测试（Mock Repository）
└── test_workflows.py       # 业务流程测试（SQLite）
```

每个文件包含：
- 文件头部（生成时间、工具版本、警告信息）
- 导入语句（pytest、模型、Repository、Factory等）
- 多个测试类（每个模型/Repository/Service一个类）
- 每个类包含多个测试方法（覆盖各种场景）

---

## 测试标准符合性

所有生成的测试代码严格遵循：
- ✅ `testing-standards.md v2.0.0` - 测试标准
- ✅ `code-standards.md` - 编码标准
- ✅ `naming-conventions-standards.md` - 命名规范

具体体现：
- 测试方法命名：`test_{operation}_{scenario}`
- Fixture使用：`unit_test_db` (Repository/Workflow)
- Mock策略：Service层必须Mock Repository
- Factory使用：使用Factory Boy生成测试数据
- 断言风格：使用pytest的assert语句

---

## 扩展开发

### 添加新生成器
1. 创建新的生成器类（继承BaseGenerator或独立实现）
2. 实现`generate_*_tests()`方法
3. 在`__init__.py`中导出
4. 更新本README文档
5. 编写单元测试

### 扩展现有生成器
- 在生成器类中添加新方法
- 遵循现有代码结构和命名约定
- 更新测试覆盖

---

## 已知限制

1. **Model测试**: 仅测试模型定义，不测试SQLAlchemy框架功能
2. **Repository测试**: 代码长度可能>2000行，建议优化或分文件
3. **Service测试**: 对于复杂的Service方法，Mock配置可能需要手动调整
4. **Workflow测试**: 仅生成基础流程，复杂业务规则需要手动补充

---

## 故障排查

### 问题1: 生成的测试无法导入模块
**原因**: 模块路径不在sys.path中  
**解决**: 确保从项目根目录运行生成器

### 问题2: Factory类缺失错误
**原因**: tests/factories/目录下缺少对应的Factory  
**解决**: 先生成或手动创建Factory类

### 问题3: unit_test_db fixture不可用
**原因**: tests/conftest.py未定义fixture  
**解决**: 检查conftest.py配置，确保定义了unit_test_db

---

## 版本历史

- **v1.0.0** (2025-10-08): 初始版本
  - 新增4个核心生成器
  - 支持Model/Repository/Service/Workflow测试生成
  - 遵循testing-standards.md v2.0.0

---

## 相关文档

- [主README](../README.md) - 测试生成器总体介绍
- [工具模块](../utils/README.md) - 通用工具文档
- [测试标准](../../../docs/standards/testing-standards.md) - 测试规范
- [代码标准](../../../docs/standards/code-standards.md) - 编码规范
