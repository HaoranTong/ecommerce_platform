<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,../../PROJECT-FOUNDATION.md-->

# 测试标准

## 概述

本文档定义了电商平台项目的完整测试标准和规范，包括五层测试架构、测试类型分布、环境配置、编写规范等。确保代码质量和系统稳定性。

## 依赖标准

本标准依赖以下L1核心标准：

- **[项目基础定义](../../PROJECT-FOUNDATION.md)** - tests/目录五层架构组织（unit/integration/e2e/security/performance）、测试文件存放规则、conftest.py配置管理
- **[命名规范标准](./naming-conventions-standards.md)** - 测试文件命名（test_*前缀规则）、测试类命名（Test*类规则）、测试方法命名（test_*函数规则）、断言方法标准

## 具体标准应用
⬆️ **测试文件结构**: 参见 [PROJECT-FOUNDATION.md](../../PROJECT-FOUNDATION.md#tests目录结构-五层测试架构) - 五层测试架构组织
⬆️ **测试命名约定**: 参见 [naming-conventions-standards.md](naming-conventions-standards.md#测试命名规范) - test_*文件和方法命名

### 五层测试架构

### 编写测试前检查
- 阅读被测试模块文档 (overview.md, models.py, service.py)
- 验证数据模型字段存在性 
- 验证API方法存在性
- 检查方法参数正确性

### 禁止行为
- 猜测字段名称
- 猜测方法名称  
- 假设字段存在
- 简化业务逻辑测试

## 测试层级 (70%, 2%, 20%, 6%, 2%)

### 单元测试 (70%) - 四层架构
- test_models/: 100% Mock测试，无数据库依赖
- test_repositories/: SQLite内存数据库，测试数据访问层
- test_services/: Mock Repository，测试业务逻辑层
- *_standalone.py: SQLite内存，测试完整业务流程

### 烟雾测试 (2%)
- tests/smoke/: SQLite文件数据库

### 集成测试 (20%)
- tests/integration/: MySQL Docker

### E2E测试 (6%)
- tests/e2e/: MySQL Docker

### 专项测试 (2%)
- 性能测试, 安全测试

## 数据库策略（四层架构）

| 测试位置 | Mock | 数据库 | Fixture | 架构层级 |
|---------|------|--------|---------|----------|
| tests/unit/test_models/ | 100% | 无 | pytest-mock | Model层 |
| tests/unit/test_repositories/ | 0% | SQLite内存 | unit_test_db | Repository层 |
| tests/unit/test_services/ | Mock Repo | 无 | pytest-mock | Service层 |
| tests/unit/*_standalone.py | 0% | SQLite内存 | unit_test_db | 完整流程 |
| tests/smoke/ | 0% | SQLite文件 | smoke_test_db | 系统级 |
| tests/integration/ | 0% | MySQL Docker | mysql_integration_db | 系统级 |
| tests/e2e/ | 0% | MySQL Docker | mysql_e2e_db | 系统级 |

## 测试实现示例

### Mock测试 (test_models/)
```python
def test_user_password_validation(mocker):
    mock_user = mocker.Mock()
    mock_user.password = "weak123"
    validator = PasswordValidator(mock_user)
    assert not validator.is_strong()
```

### 数据库测试 (test_services/)
```python
def test_user_service_create(unit_test_db):
    service = UserService(unit_test_db)
    user_data = {"email": "test@example.com"}
    created_user = service.create_user(user_data)
    assert created_user.email == user_data["email"]
```

### 业务流程测试 (*_standalone.py)
```python
def test_cart_workflow(unit_test_db):
    cart_service = ShoppingCartService(unit_test_db)
    result = cart_service.add_item(user_id, product_sku, 2)
    assert result.success is True
```

### 烟雾测试 (tests/smoke/)
```python
def test_health_check():
    """验证应用基本健康状态"""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_database_connection_smoke(smoke_test_db):
    """验证数据库连接正常"""
    # 简单的数据库连接测试
    result = smoke_test_db.execute("SELECT 1 as test")
    assert result.fetchone()[0] == 1
```

### 5. tests/integration/ → MySQL Docker (集成验证)
```python
# ✅ 集成测试：真实环境模拟
def test_user_registration_api_integration(api_client, mysql_integration_db):
    """测试用户注册API完整集成"""
    user_data = {
        "email": "integration@test.com",
        "username": "testuser",
        "password": "SecurePass123"
    }
    
    # HTTP API测试
    response = api_client.post("/api/v1/users/register", json=user_data)
    assert response.status_code == 201
    
    # 数据库验证
    user_in_db = mysql_integration_db.query(User).filter(
        User.email == user_data["email"]
    ).first()
    assert user_in_db is not None
    assert user_in_db.username == user_data["username"]
```

## pytest-mock 统一使用标准

### 强制使用pytest-mock (禁止unittest.mock)
**⚠️ 项目统一使用pytest-mock，严禁混用unittest.mock**

```python
# ✅ 正确：pytest-mock统一语法
def test_user_validation_logic(mocker):
    """在test_models/中使用Mock测试纯逻辑"""
    # 1. 创建Mock对象
    mock_user = mocker.Mock()
    mock_user.email = "test@example.com"
    mock_user.age = 25
    
    # 2. Mock外部依赖
    mock_email_service = mocker.patch('app.services.email_service.EmailService')
    mock_email_service.return_value.is_valid.return_value = True
    
    # 3. 测试业务逻辑
    validator = UserValidator(mock_user, mock_email_service)
    assert validator.is_valid_user() is True

# ❌ 严禁：unittest.mock (禁止导入和使用)  
from unittest.mock import Mock, patch  # 绝对禁止
```

### Mock语法三种标准模式

```python
# 模式1：直接创建Mock对象 (适用于简单对象Mock)
def test_with_mock_object(mocker):
    mock_user = mocker.Mock()
    mock_user.name = "testuser"
    mock_user.get_profile.return_value = {"age": 25}

# 模式2：patch模块/类 (适用于替换外部依赖)  
def test_with_patch(mocker):
    mock_service = mocker.patch('app.services.user_service.UserService')
    mock_service.return_value.create_user.return_value = User(id=1)

# 模式3：上下文管理器 (适用于临时Mock)
def test_with_context_manager(mocker):
    with mocker.patch('app.core.database.get_db') as mock_db:
        mock_db.return_value = mocker.Mock()
        # 测试逻辑
```

### Mock配置最佳实践

```python
# ✅ 正确：精确Mock配置
def test_user_creation_with_email_validation(mocker):
    # Mock外部邮件验证服务
    mock_email_validator = mocker.patch('app.utils.validators.EmailValidator')
    mock_email_validator.return_value.validate.return_value = True
    
    # Mock数据库操作（仅在test_models/中使用）
    mock_db = mocker.Mock()
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    
    # 执行测试
    service = UserService(mock_db)
    result = service.create_user_with_validation("test@example.com")
    
    # 验证Mock调用
    mock_email_validator.return_value.validate.assert_called_once_with("test@example.com")
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

# ❌ 错误：过度Mock或Mock配置错误
def test_with_wrong_mock_usage(mocker):
    # 错误1：Mock路径错误
    mock_service = mocker.patch(some_variable)  # 应该是字符串路径
    
    # 错误2：不必要的Mock
    mock_simple_function = mocker.patch('builtins.len')  # 过度Mock
    
    # 错误3：Mock配置不完整
    mock_db = mocker.Mock()
    # 忘记配置return_value，导致测试不稳定
```

## 数据库Fixture统一标准

### 强制使用统一Fixture配置
**⚠️ 严禁自定义数据库连接，必须使用标准Fixture**

### Fixture使用规范
```python
# ✅ 正确：使用标准Fixture
def test_user_service_database_operations(unit_test_db):
    """测试服务层数据库操作，使用SQLite内存"""
    service = UserService(unit_test_db)
    
    user = User(email="test@example.com", username="testuser")
    unit_test_db.add(user)
    unit_test_db.commit()
    unit_test_db.refresh(user)
    
    assert user.id is not None

def test_integration_with_mysql(mysql_integration_db):
    """集成测试使用MySQL Docker"""
    user = User(email="integration@test.com")
    mysql_integration_db.add(user)
    mysql_integration_db.commit()
    
    assert user.id is not None

# ❌ 严禁：自定义数据库连接
def test_with_custom_database():
    # 禁止自定义引擎
    engine = create_engine("sqlite:///:memory:")  # 绝对禁止
    # 禁止自定义会话
    Session = sessionmaker(bind=engine)  # 绝对禁止
```

### SQLite数据库使用策略

### 数据持久化区别
- **SQLite内存数据库** (:memory:): 用于单元测试，测试间数据自动清理，高性能
- **SQLite文件数据库** (文件路径): 用于烟雾测试，数据持久化便于调试和验证

### 兼容性策略
```python
# ✅ SQLite兼容层配置 (conftest.py中实现)
@pytest.fixture(scope="function")
def unit_test_db():
    """SQLite内存数据库，兼容MySQL特性"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    # 启用SQLite兼容功能
    @event.listens_for(engine, "connect")  
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")  # 外键约束
        cursor.execute("PRAGMA journal_mode=WAL")   # 并发性能
        cursor.close()
    
    # 创建表结构
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
```

### MySQL特定功能测试
```python
# ✅ 条件测试：仅MySQL环境执行
@pytest.mark.skipif(DB_TYPE == "sqlite", reason="MySQL JSON功能测试")
def test_mysql_json_field_operations(mysql_integration_db):
    """测试MySQL JSON字段特定功能"""
    user = User(
        email="json@test.com",
        profile_json={"preferences": {"theme": "dark", "language": "zh-CN"}}
    )
    mysql_integration_db.add(user)
    mysql_integration_db.commit()
    
    # 测试JSON查询 (MySQL特有)
    result = mysql_integration_db.query(User).filter(
        User.profile_json['preferences']['theme'].astext == 'dark'
    ).first()
    assert result is not None
```

## 测试文件组织标准

### 当前目录状态说明
> **重要提示**: 项目目前处于初期阶段，许多测试目录已创建但测试文件尚未完善。以下标记说明各目录的当前状态：
> - ✅ **已存在**: 目录和文件已创建且功能完整
> - 📁 **目录已创建**: 目录已创建但测试文件为空，待开发
> - 📄 **文件已存在**: 具体的测试文件已创建

### 统一目录结构（四层架构）
```text
tests/
├── unit/                           # 单元测试 (70%) 📁
│   ├── README.md                  # 单元测试说明文档 📄
│   ├── test_models/               # Mock测试 - Model层，100% Mock 📁
│   ├── test_repositories/         # SQLite内存 - Repository层，数据访问测试 📁
│   ├── test_services/             # Mock Repository - Service层，业务逻辑测试 📁
│   └── *_standalone.py            # SQLite内存 - 完整业务流程测试 �
├── smoke/                         # 烟雾测试 (2%) ✅
│   ├── README.md                  # 烟雾测试说明文档 📄
│   ├── test_health.py             # 健康检查 📄
│   └── test_basic_api.py          # 基本API验证 📄
├── integration/                   # 集成测试 (20%) 📁
│   ├── README.md                  # 集成测试说明文档 📄
│   └── test_api/                  # HTTP API集成测试 📁
├── e2e/                          # 端到端测试 (6%) 📁
│   └── README.md                  # E2E测试说明文档 📄
├── performance/                   # 性能测试 (1%) 📁
│   └── README.md                  # 性能测试说明文档 📄
├── security/                      # 安全测试 (1%) 📁
│   └── README.md                  # 安全测试说明文档 📄
├── factories/                     # 测试数据工厂 ✅
│   ├── __init__.py               # 工厂包初始化 📄
│   ├── data_factory.py           # 统一测试数据工厂 📄
│   └── README.md                 # 数据工厂使用说明 📄
├── _archive/                      # 测试文件存档目录 📁
├── conftest.py                    # 统一Fixture配置 📄
├── conftest_e2e.py               # E2E测试专用配置 📄
├── README.md                      # 测试目录总体说明 📄
├── smoke_test.db                  # 烟雾测试数据库文件 📄
└── smoke_test_pytest.db          # pytest烟雾测试数据库 📄
```

### 测试文件分类执行规范

| 测试分类 | 存放位置 | 数据库 | 执行命令 | 执行时机 | 时间要求 | 架构层级 |
|---------|---------|--------|---------|---------|----------|----------|
| **Mock单元测试** | `tests/unit/test_models/` | 无 | `pytest tests/unit/test_models/` | 代码提交前 | <30秒 | Model层 |
| **Repository测试** | `tests/unit/test_repositories/` | SQLite内存 | `pytest tests/unit/test_repositories/` | 代码提交前 | <1分钟 | Repository层 |
| **Service测试** | `tests/unit/test_services/` | Mock Repo | `pytest tests/unit/test_services/` | 代码提交前 | <1分钟 | Service层 |
| **业务流程测试** | `tests/unit/*_standalone.py` | SQLite内存 | `pytest tests/unit/*_standalone.py` | 代码提交前 | <2分钟 | 完整流程 |
| **烟雾测试** | `tests/smoke/` | SQLite文件 | `pytest tests/smoke/` | 部署后立即 | <30秒 |
| **集成测试** | `tests/integration/` | MySQL Docker | `pytest tests/integration/` | 提交到主分支前 | <5分钟 |
| **E2E测试** | `tests/e2e/` | MySQL Docker | `pytest tests/e2e/` | 发布前 | <10分钟 |

### 根目录测试脚本管理

### 临时测试脚本使用规范
```powershell
# ✅ 允许的临时测试脚本
test_auth_integration.py     # 认证功能调试
test_inventory_api.py        # 库存API调试  
test_inventory_integration.py # 库存集成调试

# ❌ 禁止的命名方式
temp_test.py                 # 命名不明确
debug.py                     # 功能不清晰
my_test.py                   # 个人化命名
```text

**清理规则**：
- **开发完成**：移至对应的tests子目录
- **功能废弃**：直接删除
- **需要保留**：移至tools/目录并规范化
- **提交前**：必须在README.md中说明临时脚本的用途

### 测试文件命名规范
| 测试类型 | 命名规则 | 示例 |
|---------|---------|------|
| **单元测试** | `test_{module}.py` | `test_users.py`, `test_products.py` |
| **集成测试** | `test_{module}_integration.py` | `test_cart_integration.py` |
| **端到端测试** | `test_{scenario}_e2e.py` | `test_order_flow_e2e.py` |
| **系统测试** | `test_{module}_complete.py` | `test_cart_complete.py` |

### 测试函数命名规范
```python
# 命名模式: test_{功能}_{场景}[_{预期结果}]
def test_create_user_success()           # 成功创建用户
def test_create_user_duplicate_email()   # 重复邮箱创建用户
def test_login_invalid_password()        # 无效密码登录
def test_add_to_cart_out_of_stock()     # 添加无库存商品到购物车
```
`$language

## pytest.ini 标准配置

```ini
# pyproject.toml - [tool.pytest.ini_options] 节
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--tb=short", 
    "--disable-warnings",
    "--timeout=300",  # 全局测试超时5分钟
    "--timeout-method=thread"
]
markers = [
    "unit: Unit tests - 70% coverage target (fast, isolated, no external dependencies)",
    "smoke: Smoke tests - 2% coverage (basic functionality verification)",
    "integration: Integration tests - 20% coverage (module interaction testing)", 
    "e2e: End-to-end tests - 6% coverage (complete user workflow testing)",
    "performance: Performance tests - 2% coverage (load and stress testing)",
    "security: Security tests (authentication, authorization, input validation)",
    "services: Service layer tests (business logic and service integration)",
    "workflow: Business workflow tests (complete business process testing)",
    "standalone: Standalone module tests (independent module functionality)",
    "critical: Critical path tests (core business logic validation)",
    "slow: Slow running tests (can be skipped for quick feedback)",
    "api: API endpoint tests (REST/GraphQL interface testing)",
    "database: Database dependent tests (require database connection)",
    "external: External service dependent tests (require network/third-party services)"
]
```

## 覆盖率配置

由于项目使用 pyproject.toml 配置，覆盖率配置通过 pytest 命令行选项控制：

```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html:htmlcov --cov-report=term-missing --cov-fail-under=85

# 排除目录配置（通过命令行选项）
pytest --cov=app --cov-report=html --cov-omit="*/tests/*,*/venv/*,*/__pycache__/*,*/migrations/*,*/conftest.py,app/main.py"
```

如需创建 .coveragerc 文件，推荐配置：

```ini
# .coveragerc - 覆盖率配置
[run]
source = app
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*
    */conftest.py
    app/main.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
```

## 测试框架技术栈

### 核心测试框架 (强制使用)
```bash
pytest>=7.0.0              
pytest-mock>=3.10.0        
pytest-asyncio>=0.21.0     
pytest-cov>=4.0.0          
httpx>=0.24.0              
fastapi.testclient
SQLAlchemy>=2.0.0          
pymysql>=1.0.0             
factory-boy>=3.2.0         
Faker>=18.0.0              
```

## 双工厂架构测试数据策略

### 🏭 工厂架构概览

本项目采用**双工厂架构**，根据测试类型和场景选择不同的数据工厂：

| 工厂类型 | 文件位置 | 适用测试 | 主要特点 |
|---------|---------|---------|---------|
| **Factory Boy工厂** | `tests/factories/user_auth_factories.py` | 单元测试<br/>Mock测试 | 内存创建<br/>复杂关系<br/>智能推断 |
| **统一工厂** | `tests/factories/data_factory.py` | 集成测试<br/>E2E测试 | 真实数据库<br/>跨模块链<br/>类型安全 |

### 📋 Factory Boy工厂标准 (单元测试专用)

```python
# tests/factories/user_auth_factories.py
import factory
from faker import Faker
from app.modules.user_auth.models import User, Role, Permission

fake = Faker('zh_CN')

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"

    email = factory.LazyFunction(lambda: fake.email())
    username = factory.LazyFunction(lambda: fake.user_name())
    password_hash = "hashed_password_123"
    is_active = True
    created_at = factory.LazyFunction(lambda: fake.date_time())

class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role
        sqlalchemy_session_persistence = "flush"

    name = factory.Sequence(lambda n: f"role_{n}")
    description = factory.LazyFunction(lambda: fake.sentence())

# 使用示例 - 单元测试
def test_user_permission_logic(mocker):
    user = UserFactory(is_active=True)  # 仅在内存创建
    role = RoleFactory(name='admin')
    
    # Mock外部依赖
    mock_auth = mocker.patch('app.services.AuthService')
    mock_auth.get_user_roles.return_value = [role]
    
    # 测试纯业务逻辑
    assert user.has_role('admin') is True
```

### 🌐 统一工厂标准 (集成测试专用)

```python
# tests/factories/data_factory.py
from sqlalchemy.orm import Session
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Category, Product

class StandardTestDataFactory:
    @staticmethod
    def create_user_data(db: Session, **overrides) -> User:
        """创建用户数据 - 真实数据库操作"""
        user_data = {
            'username': f'testuser_{fake.random_int()}',
            'email': fake.email(),
            'password_hash': 'hashed_password',
            'is_active': True,
            **overrides
        }
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_complete_chain(db: Session):
        """创建完整业务数据链"""
        user = StandardTestDataFactory.create_user_data(db)
        category = StandardTestDataFactory.create_category_data(db)
        brand = StandardTestDataFactory.create_brand_data(db)
        product = StandardTestDataFactory.create_product_data(
            db, category_id=category.id, brand_id=brand.id
        )
        sku = StandardTestDataFactory.create_sku_data(
            db, product_id=product.id
        )
        return user, category, brand, product, sku

# 使用示例 - 集成测试
def test_order_creation_workflow(integration_test_db):
    # 创建真实的完整业务数据
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(
        integration_test_db
    )
    
    # 测试跨模块集成
    order_service = OrderService(integration_test_db)
    result = order_service.create_order(user.id, sku.id, quantity=2)
    assert result.success is True
```

### ⚠️ 工厂使用强制规范

#### ✅ **正确使用模式**
```python
# 单元测试 - 使用Factory Boy
def test_user_logic(mocker):
    user = UserFactory()  # ✅ 快速、轻量、Mock友好

# 集成测试 - 使用统一工厂
def test_order_integration(integration_test_db):
    user, _, _, _, sku = StandardTestDataFactory.create_complete_chain(
        integration_test_db
    )  # ✅ 完整、真实、类型安全
```

#### ❌ **禁止的错误用法**
```python
# ❌ 错误1：单元测试使用统一工厂 (太重)
def test_user_logic():
    user, _, _, _, _ = StandardTestDataFactory.create_complete_chain(db)  # ❌ 过度

# ❌ 错误2：集成测试使用Factory Boy (Mock不适用)
def test_order_integration():
    user = UserFactory()  # ❌ Mock数据不适用于真实集成

# ❌ 错误3：硬编码测试数据 (维护困难)
def test_user_creation():
    user = User(name="test", email="test@test.com")  # ❌ CI警告
```

### Docker环境配置 (集成测试必需)

### 方法1：docker-compose.yml配置 (推荐)
```yaml
# docker-compose.yml - MySQL测试数据库配置
services:
  mysql_test:
    image: mysql:8.0
    container_name: mysql_test_container
    environment:
      MYSQL_ROOT_PASSWORD: test_root_pass
      MYSQL_DATABASE: ecommerce_platform_test  
      MYSQL_USER: test_user
      MYSQL_PASSWORD: test_pass
    ports:
      - "3308:3306"  # 测试专用端口，避免与生产MySQL(3306)冲突
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: --default-authentication-plugin=mysql_native_password
    tmpfs:
      - /tmp  # 临时文件系统，提高测试性能
    volumes:
      - /tmp/mysql_test_data:/var/lib/mysql  # 临时数据，测试后清理

# 启动命令
# docker-compose up -d mysql_test
```

### 方法2：直接Docker命令 (快速测试)
```bash
# 启动MySQL测试容器
docker run -d --name mysql_integration_test \
  -e MYSQL_ROOT_PASSWORD=test_root_pass \
  -e MYSQL_DATABASE=ecommerce_platform_test \
  -e MYSQL_USER=test_user \
  -e MYSQL_PASSWORD=test_pass \
  -p 3308:3306 \
  --health-cmd "mysqladmin ping -h localhost" \
  --health-interval 10s \
  --health-timeout 5s \
  --health-retries 5 \
  mysql:8.0

# 清理命令
docker stop mysql_integration_test && docker rm mysql_integration_test
```

## 统一数据库配置策略

### 数据库选择决策树
```text
测试需要数据库? 
├── NO → test_models/ (100% Mock测试)
└── YES → 选择数据库类型
    ├── 快速单元测试 → SQLite内存 (test_services/, *_standalone.py)
    ├── 部署验证测试 → SQLite文件 (smoke/)
    └── 真实环境测试 → MySQL Docker (integration/, e2e/)
```

### 标准数据库配置矩阵

| 测试层级 | 数据库选择 | 连接配置 | 数据持久化 | 性能特点 | 适用场景 |
|---------|-----------|----------|------------|----------|----------|
| **Mock测试** | 无数据库 | N/A | 不适用 | 极快 (<1ms) | 纯逻辑验证 |
| **SQLite内存** | `:memory:` | `sqlite:///:memory:` | 进程内隔离 | 很快 (<10ms) | 数据交互测试 |
| **SQLite文件** | 临时文件 | `sqlite:///temp.db` | 会话内持久 | 快 (<50ms) | 部署验证 |
| **MySQL Docker** | 容器数据库 | `mysql://root:test_password@localhost:3308/ecommerce_platform_test` | 测试间清理 | 中等 (<200ms) | 集成测试 |

## conftest.py 配置

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from app.core.database import Base

@pytest.fixture(scope="function") 
def unit_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    # 返回会话...
        cursor.execute("PRAGMA journal_mode=WAL")   # 改善并发性能  
        cursor.close()
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        engine.dispose()

# ========== 2. 烟雾测试Fixture (SQLite文件) ==========  
@pytest.fixture(scope="session")
def smoke_test_db():
    """SQLite文件数据库，用于tests/smoke/"""
    db_file = "tests/smoke_test.db"
    engine = create_engine(f"sqlite:///{db_file}")
    
    # 创建表结构
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        # 清理文件
        if os.path.exists(db_file):
            os.remove(db_file)

# ========== 3. 集成测试Fixture (MySQL Docker) ==========
@pytest.fixture(scope="session") 
def mysql_integration_db():
    """MySQL Docker数据库，用于tests/integration/"""
    import subprocess
    import time
    
    # 启动MySQL Docker容器
    container_result = subprocess.run([
        "docker", "run", "-d", "--name", "mysql_integration_test",
        "-e", "MYSQL_ROOT_PASSWORD=test_root_pass",
        "-e", "MYSQL_DATABASE=ecommerce_platform_test",
        "-e", "MYSQL_USER=test_user", 
        "-e", "MYSQL_PASSWORD=test_pass",
        "-p", "3308:3306",  # 测试专用端口，避免与生产环境冲突
        "--health-cmd", "mysqladmin ping -h localhost",
        "--health-interval", "10s",
        "--health-timeout", "5s",
        "--health-retries", "5",
        "mysql:8.0"
    ], check=False, capture_output=True, text=True)
    
    if container_result.returncode != 0:
        print(f"容器启动失败: {container_result.stderr}")
        raise RuntimeError("MySQL Docker容器启动失败")
    
    # 等待MySQL健康检查通过
    max_wait = 60  # 最大等待60秒
    wait_time = 0
    while wait_time < max_wait:
        health_check = subprocess.run([
            "docker", "inspect", "--format", "{{.State.Health.Status}}", 
            "mysql_integration_test"
        ], capture_output=True, text=True, check=False)
        
        if health_check.stdout.strip() == "healthy":
            break
        time.sleep(2)
        wait_time += 2
    else:
        raise TimeoutError("MySQL Docker容器健康检查超时")
    
    # 创建数据库连接
    engine = create_engine(
        "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test",
        pool_pre_ping=True,  # 连接前检查有效性
        pool_recycle=300     # 5分钟回收连接
    )
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        # 清理Docker容器
        subprocess.run(["docker", "stop", "mysql_integration_test"], check=False)
        subprocess.run(["docker", "rm", "mysql_integration_test"], check=False)

# ========== 4. API测试客户端 ==========
@pytest.fixture
def api_client():
    """FastAPI测试客户端，用于API集成测试"""
    return TestClient(app)

# ========== 5. 数据清理Fixture (自动执行) ==========
@pytest.fixture(autouse=True)  
def clean_database_after_test(unit_test_db):
    """每个测试后自动清理数据库，确保测试隔离"""
    yield
    # 清理所有测试数据，按外键依赖顺序删除
    try:
        # 导入所有模型进行清理 
        from app.modules.order_management.models import OrderItem, OrderStatusHistory, Order
        from app.modules.payment_service.models import Refund, Payment  
        from app.modules.user_auth.models import Session, UserRole, RolePermission, User, Role, Permission
        from app.modules.inventory_management.models import InventoryTransaction, InventoryReservation, InventoryStock
        from app.modules.product_catalog.models import SKUAttribute, ProductAttribute, ProductImage, ProductTag, SKU, Product, Brand, Category
        
        # 按依赖顺序清理
        unit_test_db.query(OrderItem).delete()
        unit_test_db.query(OrderStatusHistory).delete() 
        unit_test_db.query(Refund).delete()
        unit_test_db.query(Payment).delete()
        unit_test_db.query(Order).delete()
        
        unit_test_db.query(RolePermission).delete()
        unit_test_db.query(UserRole).delete()
        unit_test_db.query(Session).delete()
        unit_test_db.query(User).delete()
        unit_test_db.query(Permission).delete()
        unit_test_db.query(Role).delete()
        
        unit_test_db.query(InventoryTransaction).delete()
        unit_test_db.query(InventoryReservation).delete()
        unit_test_db.query(InventoryStock).delete()
        
        unit_test_db.query(SKUAttribute).delete()
        unit_test_db.query(ProductAttribute).delete()
        unit_test_db.query(ProductImage).delete()
        unit_test_db.query(ProductTag).delete()
        unit_test_db.query(SKU).delete()
        unit_test_db.query(Product).delete()
        unit_test_db.query(Brand).delete()
        unit_test_db.query(Category).delete()
        
        unit_test_db.commit()
    except Exception:
        unit_test_db.rollback()
```

## 测试执行

### 基本命令
```bash
pytest tests/unit/test_models/     # Mock测试
pytest tests/unit/test_services/   # 数据库测试  
pytest tests/unit/*_standalone.py  # 业务流程测试
pytest tests/smoke/                # 烟雾测试
pytest tests/integration/          # 集成测试
pytest tests/e2e/                  # E2E测试
```

### 使用标记选择测试
```bash
# 按标记运行测试
pytest -m unit                     # 仅运行单元测试
pytest -m smoke                    # 仅运行烟雾测试  
pytest -m integration              # 仅运行集成测试
pytest -m "unit and services"      # 仅运行服务层单元测试
pytest -m "workflow or standalone" # 仅运行业务流程测试
pytest -m critical                 # 仅运行关键路径测试
pytest -m "not external"           # 排除外部依赖测试
pytest -m "not slow"               # 排除慢速测试
```

**3. 集成测试执行 (提交前验证)**：
```bash
# 需要先启动MySQL Docker (端口3308)
docker-compose up -d mysql_test

# API集成测试
pytest tests/integration/test_api/ -v --tb=short
# 预期时间: <3分钟

# 所有集成测试
pytest tests/integration/ -v
# 预期时间: <5分钟, 必须100%通过
```

pytest tests/ --cov=app                # 全部测试
.\tools\integration_test.ps1       # 使用脚本
`$language

## 测试工具

### 环境检查
```bash
.\tools\check_test_env.ps1         # 测试前检查
.\tools\setup_test_env.ps1         # 环境设置  
python tools/validate_test_config.py  # 配置验证
```

**输出标准**：
- ✅ 所有检查通过 → 可以进行测试
- ❌ 发现问题 → 显示修复建议，禁止继续测试

### 🎯 setup_test_env.ps1 (标准测试流程)
**用途**：标准化测试环境设置和执行流程
**功能**：自动环境验证、数据库准备、测试执行、环境清理
**依赖**：内部会调用 check_test_env.ps1 进行前置验证

**参数说明**：
- `-TestType <unit|smoke|integration|all>`：测试类型
- `-SetupOnly`：仅设置环境，不执行测试
- `-SkipValidation`：跳过环境验证 (不推荐)

**标准执行流程**：
```powershell
# 单元测试 (推荐方式)
.\tools\setup_test_env.ps1 -TestType unit

# 集成测试 (自动管理Docker)
.\tools\setup_test_env.ps1 -TestType integration

# 完整测试套件
.\tools\setup_test_env.ps1 -TestType all
```

### 🔍 validate_test_config.py (详细诊断工具)
**用途**：深度测试配置验证，问题排查时使用
**执行时间**：约60秒
**验证范围**：7个验证步骤，全面诊断配置问题
**依赖**：独立工具，可单独使用，不依赖其他脚本

**执行顺序建议**：
1. 首先运行：check_test_env.ps1 (快速检查)
2. 通过后运行：setup_test_env.ps1 (标准流程)
3. 问题排查时：validate_test_config.py (深度诊断)

```powershell
# 详细配置验证 (问题排查时使用)
python tools/validate_test_config.py
```

## � 测试工作流程总纲

### 文档驱动开发原则 (Document-Driven Development)

**核心理念**：发现问题时，先文档后代码，从根源解决问题

#### 问题排查层次结构
```mermaid
graph TD
    A[发现问题] --> B[停止修改代码]
    B --> C{检查文档层级}
    C -->|L0层| D[PROJECT-FOUNDATION.md<br/>架构设计问题]
    C -->|L1层| E[standards/文档<br/>规范标准问题]
    C -->|L2层| F[具体设计文档<br/>详细设计缺失]
    C -->|L3层| G[实施文档<br/>操作步骤错误]
    D --> H[修正架构设计]
    E --> I[更新规范标准]
    F --> J[补充详细设计]
    G --> K[修正操作文档]
    H --> L[更新下级文档]
    I --> L
    J --> L
    K --> L
    L --> M[按文档要求修改代码]
    M --> N[执行测试验证]
```

#### 问题根因分析流程
1. **架构层面** → 检查 `PROJECT-FOUNDATION.md`，确认设计理念是否正确
2. **标准层面** → 检查 `docs/standards/` 相关规范，确认标准是否完善
3. **设计层面** → 检查具体设计文档，确认详细设计是否缺失
4. **实施层面** → 检查操作文档，确认步骤是否准确
5. **代码层面** → 最后检查代码是否严格按照文档要求实现

### 标准测试工作流程选择

#### 新功能开发流程
```
设计文档 → 测试设计 → 环境验证 → 生成测试 → 编写代码 → 执行验证
```

#### Bug修复流程  
```
文档检查 → 根因分析 → 文档修正 → 复现测试 → 代码修复 → 回归验证
```

#### 重构优化流程
```
文档审查 → 影响评估 → 文档更新 → 全量测试 → 执行重构 → 回归测试
```

### 测试执行决策矩阵

| 开发阶段 | 推荐测试类型 | 执行命令 | 检查点 |
|---------|-------------|---------|-------|
| **功能开发** | 单元测试 | `setup_test_env.ps1 -TestType unit` | TEST-002 |
| **模块集成** | 集成测试 | `setup_test_env.ps1 -TestType integration` | TEST-004 |
| **系统验证** | 完整测试 | `setup_test_env.ps1 -TestType all` | TEST-005 |
| **问题排查** | 环境诊断 | `validate_test_config.py` | TEST-003 |

### 文档优先原则实施

#### 强制检查顺序
1. **问题发现** → 立即停止代码修改
2. **文档检查** → 按层级检查相关文档
3. **根因确认** → 确定是文档问题还是代码问题  
4. **文档修正** → 先修正文档（如需要）
5. **代码修正** → 按修正后的文档要求修改代码
6. **测试验证** → 执行对应的测试流程

#### 禁止的问题处理方式
- ❌ 直接修改代码而不检查文档
- ❌ 绕过文档标准自定义实现
- ❌ 修改代码后不更新相关文档
- ❌ 不按照文档层级进行根因分析

## �📋 强制性测试流程 (MASTER规范)

### 环境验证 (强制) [CHECK:TEST-001]
```powershell
# 必须通过的环境检查
.\tools\check_test_env.ps1
```

### 选择测试类型并执行 [CHECK:TEST-002]

### 单元测试流程 (推荐)
```powershell
# 标准单元测试 - 使用SQLite内存数据库
.\tools\setup_test_env.ps1 -TestType unit
```

### 集成测试流程
```powershell
# 自动设置MySQL Docker环境并执行测试
.\tools\setup_test_env.ps1 -TestType integration
```

### 完整测试流程
```powershell
# 执行所有类型测试
.\tools\setup_test_env.ps1 -TestType all
```

### 问题排查 (如需要) [CHECK:TEST-003]
```powershell
# 如果遇到环境问题，执行详细诊断
python tools/validate_test_config.py
```

## 🚫 禁止的测试方式

根据MASTER规范，**禁止**以下测试执行方式：
- ❌ 直接运行 `pytest` 而不进行环境验证
- ❌ 在未激活虚拟环境情况下运行测试
- ❌ 跳过环境检查步骤
- ❌ 混用不同测试类型的数据库配置
- ❌ 手动管理Docker容器而非使用标准工具

---

## 📋 标准测试执行流程 [CHECK:TEST-001]

### 阶段1: 测试工作流程说明 [CHECK:TEST-001]

#### 1.1 虚拟环境激活验证
```powershell
# 激活项目虚拟环境
.\.venv\Scripts\Activate.ps1

# 验证Python路径
python -c "import sys; print('Python环境:', sys.executable)"
# 期望输出: E:\ecommerce_platform\.venv\Scripts\python.exe
```

#### 1.2 依赖包环境检查
```powershell
# 验证核心测试依赖
pip list | findstr -i "pytest pytest-mock pytest-asyncio pytest-cov"
# 必须显示: pytest>=7.0.0, pytest-mock>=3.10.0, pytest-asyncio>=0.21.0, pytest-cov>=4.0.0

# 验证数据库依赖
pip list | findstr -i "sqlalchemy pymysql factory-boy faker"
# 必须显示: SQLAlchemy>=2.0.0, pymysql>=1.0.0, factory-boy>=3.2.0, Faker>=18.0.0
```

#### 1.3 测试工具可用性验证
```powershell
# 检查测试生成工具
python tools\generate_test_template.py --version
# 期望输出: Test Template Generator v2.1.0

# 检查测试环境验证工具
.\tools\check_test_env.ps1
# 期望输出: ✅ 所有环境检查通过
```

### 阶段2: 测试环境配置 [CHECK:TEST-002]

#### 2.1 单元测试模式 (推荐日常开发)
**适用场景**: 日常开发、代码提交前验证
**执行时间**: <3分钟
**数据库要求**: SQLite内存数据库 (无外部依赖)

```powershell
# 标准单元测试流程
.\tools\setup_test_env.ps1 -TestType unit

# 或者手动执行步骤
.\tools\check_test_env.ps1                    # 环境验证
pytest tests/unit/test_models/ -v               # Mock测试
pytest tests/unit/test_services/ -v             # SQLite内存测试
pytest tests/unit/*_standalone.py -v            # 业务流程测试
```

**预期结果**:
- ✅ 所有单元测试通过 (100%)
- ✅ 测试覆盖率 ≥90%
- ✅ 执行时间 <3分钟

#### 2.2 烟雾测试模式 (部署验证)
**适用场景**: 部署后快速验证、基础功能检查
**执行时间**: <30秒
**数据库要求**: SQLite文件数据库

```powershell
# 烟雾测试流程
.\tools\smoke_test.ps1

# 或者手动执行
pytest tests/smoke/ -v --tb=short
```

**预期结果**:
- ✅ 应用健康检查通过
- ✅ 数据库连接正常
- ✅ 基础API响应正常

#### 2.3 集成测试模式 (提交前验证)
**适用场景**: 提交到主分支前、模块集成验证
**执行时间**: <5分钟
**数据库要求**: MySQL Docker容器

```powershell
# 集成测试流程 (自动管理Docker)
.\tools\setup_test_env.ps1 -TestType integration

# 或者手动管理
docker-compose up -d mysql_test                 # 启动MySQL Docker
pytest tests/integration/ -v --tb=short         # 执行集成测试
docker-compose down mysql_test                  # 清理Docker容器
```

**预期结果**:
- ✅ MySQL Docker容器健康运行
- ✅ 所有集成测试通过
- ✅ 跨模块API调用正常
- ✅ 数据库事务完整性验证通过

#### 2.4 完整测试模式 (发布前验证)
**适用场景**: 发布前完整验证、重要功能回归测试
**执行时间**: <10分钟
**数据库要求**: 完整数据库环境 + Docker服务

```powershell
# 完整测试流程
.\tools\setup_test_env.ps1 -TestType all

# 相当于顺序执行:
# 1. .\tools\setup_test_env.ps1 -TestType unit
# 2. .\tools\setup_test_env.ps1 -TestType integration  
# 3. pytest tests/e2e/ -v
# 4. pytest tests/performance/ -v (如果存在)
```

**预期结果**:
- ✅ 单元测试覆盖率 ≥90%
- ✅ 集成测试全部通过
- ✅ E2E用户流程验证通过
- ✅ 性能基准测试达标

### 阶段3: 测试环境检查 [CHECK:TEST-003]

#### 3.1 智能测试生成工具使用
```powershell
# 为新功能生成测试模板
python tools\generate_test_template.py --module user_auth --feature password_reset

# 生成的测试文件位置
# tests/unit/test_services/test_user_auth_password_reset.py
```

**生成内容包含**:
- ✅ 标准测试类结构
- ✅ 必要的fixture配置
- ✅ 成功和失败场景模板
- ✅ Mock配置示例
- ✅ 断言检查模板

#### 3.2 测试模板定制和迁移
```powershell
# 1. 检查生成的测试模板
code tests\unit\test_services\test_user_auth_password_reset.py

# 2. 根据具体业务逻辑定制测试
# - 修改测试数据
# - 添加边界条件测试
# - 完善异常场景测试

# 3. 运行测试验证
pytest tests\unit\test_services\test_user_auth_password_reset.py -v
```

#### 3.3 测试数据工厂使用指南 [CHECK:TEST-011]

**Factory Boy工厂 (单元测试专用)**:
```python
# tests/unit/test_user_service.py
from tests.factories.user_auth_factories import UserFactory, RoleFactory

def test_user_permission_check(mocker):
    """使用Factory Boy快速生成Mock测试数据"""
    # 内存创建，无数据库IO
    user = UserFactory(is_active=True)
    role = RoleFactory(name='admin')
    
    # Mock外部服务
    mock_auth = mocker.patch('app.services.AuthService')
    mock_auth.get_user_roles.return_value = [role]
    
    # 测试业务逻辑
    assert user.has_admin_privileges() is True
```

**统一工厂 (集成测试专用)**:
```python
# tests/integration/test_order_flow.py
from tests.factories.data_factory import StandardTestDataFactory

def test_complete_order_workflow(integration_test_db):
    """使用统一工厂创建完整业务数据链"""
    # 真实数据库操作，创建关联数据
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(
        integration_test_db
    )
    
    # 测试跨模块集成
    order_service = OrderService(integration_test_db)
    result = order_service.create_order(user.id, sku.id, quantity=2)
    
    assert result.success is True
    assert result.order.user_id == user.id
```

### 阶段4: 测试工具配置 [CHECK:TEST-004]

#### 4.1 自动测试生成策略
- **生成策略**: 测试代码直接生成到正式目录（tests/unit/, tests/integration/等）
- **文件管理**: 生成的测试文件立即可用，无需迁移步骤
- **质量控制**: 通过工具内置验证确保生成代码质量

#### 4.2 自动生成测试文件审查流程
```powershell
# 1. 使用自动生成工具直接生成到正式目录
python tools/generate_test_template.py user_auth --type all --validate

# 2. 审查生成的测试文件
# 检查factories目录
code tests/factories/user_auth_factories.py

# 检查单元测试
code tests/unit/test_models/test_user_auth_models.py
code tests/unit/test_services/test_user_auth_services.py
code tests/unit/test_user_auth_standalone.py

# 3. 运行测试验证
pytest tests/unit/test_models/test_user_auth_models.py -v
pytest tests/unit/test_services/test_user_auth_services.py -v
```

#### 4.3 自动生成测试质量监控
```powershell
# 验证生成测试的语法和导入
python tools/generate_test_template.py user_auth --validate-only

# 检查测试覆盖率
pytest tests/unit/ --cov=app/modules/user_auth --cov-report=term

# 代码质量检查
flake8 tests/unit/test_models/test_user_auth_models.py
black --check tests/unit/test_services/test_user_auth_services.py
```

### 阶段5: Mock数据统一 [CHECK:TEST-005]

#### 5.1 覆盖率验证
```powershell
# 单元测试覆盖率
pytest tests/unit/ --cov=app --cov-report=term --cov-report=html --cov-fail-under=90

# 集成测试覆盖率  
pytest tests/integration/ --cov=app --cov-report=term --cov-append --cov-fail-under=80

# 总体覆盖率
pytest tests/ --cov=app --cov-report=html:htmlcov --cov-fail-under=85
```

#### 5.2 测试性能验证
```powershell
# 测试执行时间监控
pytest tests/unit/ --durations=10           # 显示最慢的10个测试
pytest tests/integration/ --durations=0     # 显示所有测试执行时间
```

#### 5.3 测试质量报告生成
```powershell
# 生成综合测试报告
pytest tests/ --html=reports/test_report.html --self-contained-html
pytest tests/ --junitxml=reports/junit.xml

# 报告文件位置
# - HTML报告: reports/test_report.html
# - JUnit XML: reports/junit.xml  
# - 覆盖率报告: htmlcov/index.html
```

### 阶段6: 数据工厂准备 [CHECK:TEST-006]

#### 6.1 标准问题诊断流程
```powershell
# 1. 环境诊断 (60秒详细检查)
python tools\validate_test_config.py

# 2. 特定测试失败诊断
pytest tests/path/to/failed_test.py -vv -s --tb=long

# 3. 数据库连接问题诊断
python -c "
from app.core.database import get_db_engine
engine = get_db_engine()
print('数据库连接测试:', engine.execute('SELECT 1').fetchone())
"

# 4. Docker服务问题诊断
docker ps -a | findstr mysql
docker logs mysql_test_container
```

#### 6.2 常见问题快速修复
```powershell
# 问题1: 虚拟环境未激活
if (-not $env:VIRTUAL_ENV) {
    Write-Error "虚拟环境未激活，执行: .\.venv\Scripts\Activate.ps1"
    exit 1
}

# 问题2: Docker容器状态异常
docker stop mysql_integration_test; docker rm mysql_integration_test
docker-compose up -d mysql_test

# 问题3: 测试数据残留
pytest tests/ --db-reset  # 如果支持
# 或手动清理数据库
```

### 阶段7: 单元测试执行 [CHECK:TEST-007]

#### 7.1 测试通过标准
- **单元测试**: 100%通过率，覆盖率≥90%
- **集成测试**: 100%通过率，覆盖率≥80%
- **端到端测试**: 100%通过率，关键用户流程全覆盖
- **性能测试**: 响应时间符合基准要求

#### 7.2 测试失败处理
```powershell
# 测试失败时的标准处理流程

# 1. 收集失败信息
pytest tests/ --tb=short | Tee-Object -FilePath "test_failure_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 2. 按优先级分类失败
# P0: 阻塞性失败 (环境、配置)
# P1: 功能性失败 (业务逻辑)  
# P2: 性能失败 (超时、性能不达标)

# 3. 立即修复P0问题
if ($LASTEXITCODE -ne 0) {
    Write-Error "发现阻塞性测试失败，必须立即修复后才能继续"
    exit 1
}
```

#### 7.3 测试报告存档
```powershell
# 创建测试报告存档
$reportDate = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDir = "reports\archive\test_$reportDate"
New-Item -ItemType Directory -Path $reportDir -Force

# 归档报告文件
Copy-Item reports\test_report.html $reportDir\
Copy-Item reports\junit.xml $reportDir\
Copy-Item htmlcov\* $reportDir\coverage\ -Recurse
```

### 工作流程检查点总结

| 检查点 | 验证内容 | 通过条件 | 失败处理 |
|-------|----------|---------|----------|
| **TEST-001** | 环境准备 | 虚拟环境激活，依赖完整 | 修复环境后重试 |
| **TEST-002** | 测试类型选择 | 选择合适的测试模式 | 重新评估测试需求 |
| **TEST-003** | 问题诊断 | 快速定位问题根因 | 使用诊断工具深入分析 |
| **TEST-005** | 质量验证 | 覆盖率和通过率达标 | 补充测试或修复失败 |
| **TEST-006** | 结果验证 | 所有测试通过 | 按优先级修复失败项 |
| **TEST-010** | 测试工具使用 | 工具正常工作 | 检查工具配置和依赖 |
| **TEST-011** | 数据工厂使用 | 数据创建正确 | 检查工厂配置和数据库 |
| **TEST-012** | 自动测试生成管理 | 测试代码质量验证 | 语法检查、导入验证、功能测试 |

## 单元测试标准执行步骤

### 环境准备要求
在执行单元测试前，必须满足以下环境条件：

1. **虚拟环境激活**：使用项目专用虚拟环境
2. **依赖包安装**：确保测试框架和相关依赖已安装
3. **无外部依赖**：单元测试使用SQLite内存数据库，无需Docker或外部服务

### 标准执行步骤
```powershell
# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 验证环境
python -c "import sys; print('Python环境:', sys.executable)"
# 输出应为: E:\ecommerce_platform\.venv\Scripts\python.exe

# 确认依赖包
pip list | findstr pytest
# 应显示: pytest, pytest-asyncio, pytest-cov 等

# 第四步：执行单元测试
pytest tests/test_user_auth.py -v
```

### 测试环境验证清单
在运行测试前，使用以下清单确认环境：

- [ ] ✅ 虚拟环境已激活 (`.venv\Scripts\python.exe`)
- [ ] ✅ pytest已安装 (`pytest --version`)
- [ ] ✅ 测试文件存在 (`tests/test_*.py`)
- [ ] ❌ 无需Docker容器运行
- [ ] ❌ 无需数据库服务启动
- [ ] ❌ 无需应用服务运行

### 测试执行命令

### 单元测试（快速，无外部依赖）
```bash
# 运行所有单元测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_user_auth.py -v

# 运行特定测试类
pytest tests/test_user_auth.py::TestAccountLocking -v

# 运行特定测试方法
pytest tests/test_user_auth.py::TestAccountLocking::test_account_locked_after_max_attempts -v

# 单元测试覆盖率
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### 烟雾测试（快速验证）
```bash
# 运行烟雾测试
pytest tests/smoke/ -v

# 或使用专用脚本
.\tools\smoke_test.ps1
```

### 集成测试（需要Docker）
```bash
# 启动Docker服务，然后运行集成测试
docker-compose up -d mysql
pytest tests/integration/ -v

# 或使用专用脚本（自动管理Docker）
.\tools\integration_test.ps1
```

### 🎯 测试策略决策树

```text
开始测试
├── 测试单个函数/类？
│   └── Yes → 使用单元测试 + SQLite内存
├── 验证基础功能？
│   └── Yes → 使用烟雾测试 + SQLite文件
├── 测试模块集成？
│   └── Yes → 使用集成测试 + MySQL Docker
└── 测试完整流程？
    └── Yes → 使用E2E测试 + MySQL Docker
```

## 单元测试指南

### 测试文件组织
```text
tests/
├── unit/
│   ├── README.md                  # 单元测试说明
│   ├── test_models/               # Mock测试目录（当前为空，待创建）
│   └── test_services/             # SQLite内存测试目录（当前为空，待创建）
├── integration/
│   ├── README.md                  # 集成测试说明
│   └── test_api/                  # API集成测试目录（当前为空，待创建）
├── e2e/
│   └── README.md                  # E2E测试说明（测试文件待创建）
├── smoke/
│   ├── README.md                  # 烟雾测试说明
│   ├── test_health.py             # 健康检查测试（已存在）
│   └── test_basic_api.py          # 基本API验证（已存在）
├── factories/
│   ├── __init__.py               # 工厂包初始化
│   ├── data_factory.py           # 统一测试数据工厂（已存在）
│   └── README.md                 # 数据工厂使用说明
└── _archive/                      # 测试文件存档目录
    └── README.md                 # 存档管理说明
```

### 单元测试示例
```python
# tests/unit/test_services/test_user_service.py
import pytest
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    
    @pytest.fixture
    def mock_db(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def user_service(self, mock_db):
        return UserService(db=mock_db)
    
    def test_create_user_success(self, user_service, mock_db):
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        mock_user = User(id=1, **user_data)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Act
        result = user_service.create_user(user_data)
        
        # Assert
        assert result.email == user_data["email"]
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_create_user_duplicate_email(self, user_service, mock_db, mocker):
        # Arrange
        user_data = {"email": "existing@example.com"}
        mock_db.query.return_value.filter.return_value.first.return_value = mocker.Mock()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(user_data)
```

## 集成测试指南

### API集成测试
```python
# tests/integration/test_api/test_user_routes.py
import pytest
from fastapi.testclient import TestClient

class TestUserRoutes:
    
    def test_create_user_success(self, client: TestClient, db):
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/v1/users", json=user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
    
    def test_get_user_by_id(self, client: TestClient, db):
        # Arrange - 先创建用户
        user_data = {"email": "test@example.com", "username": "testuser"}
        create_response = client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/v1/users/{user_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == user_data["email"]
```

### API集成测试示例
```python
# tests/integration/test_api/test_user_api.py (待创建)
import pytest
from fastapi.testclient import TestClient

class TestUserApiIntegration:
    
    def test_create_and_get_user_via_api(self, api_client, mysql_integration_db):
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
        
        # Act - 通过API创建用户
        create_response = api_client.post("/api/v1/users/register", json=user_data)
        user_id = create_response.json()["id"]
        
        # Get用户信息
        get_response = api_client.get(f"/api/v1/users/{user_id}")
        
        # Assert
        assert create_response.status_code == 201
        assert get_response.status_code == 200
        assert get_response.json()["email"] == user_data["email"]
        assert get_response.json()["id"] == user_id
```

## 端到端测试指南

### E2E测试示例
```python
# tests/e2e/test_user_journey.py (待创建)
import pytest
from fastapi.testclient import TestClient

class TestUserJourney:
    
    def test_complete_user_registration_and_login(self, api_client):
        """测试跨模块用户注册和登录的完整端到端流程"""
        
        # 1. 用户注册
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123"
        }
        
        register_response = api_client.post("/api/v1/user-auth/register", json=registration_data)
        assert register_response.status_code == 201
        
        # 2. 用户登录
        login_data = {
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        login_response = client.post("/api/v1/user-auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        assert token is not None
        
        # 3. 使用token访问受保护的资源
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/v1/users/me", headers=headers)
        assert profile_response.status_code == 200
        
        profile_data = profile_response.json()
        assert profile_data["email"] == registration_data["email"]
```

## 测试数据管理

### 双工厂架构数据策略

根据测试类型选择合适的数据工厂：

```python
# 单元测试 - 使用Factory Boy工厂
# tests/unit/user_auth/test_user_service.py
from tests.factories.user_auth_factories import UserFactory, RoleFactory

def test_user_permission_check(mocker):
    # 快速创建测试数据，无数据库I/O
    user = UserFactory(is_active=True)
    role = RoleFactory(name='admin')
    
    # Mock外部依赖
    mock_service = mocker.patch('app.services.PermissionService')
    mock_service.get_user_roles.return_value = [role]
    
    # 测试纯逻辑
    assert user.has_admin_access() is True

# 集成测试 - 使用统一工厂
# tests/integration/test_order_workflow.py
from tests.factories.data_factory import StandardTestDataFactory

def test_complete_order_process(integration_test_db):
    # 创建完整业务数据链，真实数据库操作
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(
        integration_test_db
    )
    
    # 测试跨模块集成
    order_service = OrderService(integration_test_db)
    result = order_service.create_order(user.id, sku.id, quantity=2)
    
    assert result.success is True
    assert result.order.user_id == user.id
```

### 工厂选择指南

| 测试类型 | 推荐工厂 | 理由 | 示例场景 |
|---------|---------|-----|---------|
| **单元测试** | Factory Boy<br/>`user_auth_factories.py` | 快速、轻量<br/>Mock友好<br/>专业关系处理 | 权限检查<br/>密码验证<br/>业务规则 |
| **集成测试** | 统一工厂<br/>`data_factory.py` | 真实数据库<br/>跨模块支持<br/>类型安全 | 订单流程<br/>用户注册<br/>库存管理 |
| **E2E测试** | 统一工厂<br/>`data_factory.py` | 完整数据链<br/>业务完整性 | 购物流程<br/>支付流程 |

### Fixture使用
```python
# tests/conftest.py
@pytest.fixture
def sample_user(db):
    """创建样本用户"""
    user = UserFactory()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def authenticated_client(client, sample_user):
    """认证客户端"""
    login_data = {"email": sample_user.email, "password": "password"}
    response = client.post("/api/v1/user-auth/login", json=login_data)
    token = response.json()["access_token"]
    
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
```

## 测试覆盖率

### 覆盖率配置
```ini
# .coveragerc
[run]
source = app
omit = 
    */venv/*
    */tests/*
    */alembic/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

### 覆盖率报告
```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term

# 覆盖率要求
# - 单元测试覆盖率：>= 90%
# - 集成测试覆盖率：>= 80%
# - 总体覆盖率：>= 85%
```

## 性能测试

### 负载测试配置
```python
# tests/performance/test_load.py
import pytest
from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        # 登录获取token
        response = self.client.post("/api/v1/user-auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def get_products(self):
        self.client.get("/api/v1/product-catalog/products")
    
    @task(2)
    def get_user_profile(self):
        self.client.get("/api/v1/user-auth/me")
    
    @task(1)
    def create_order(self):
        self.client.post("/api/v1/order-management/orders", json={
            "product_id": 1,
            "quantity": 1
        })
```

## Mock和存根

### Mock外部依赖
```python
# tests/unit/test_external_services.py
import pytest
from app.services.payment_service import PaymentService

class TestPaymentService:
    
    def test_process_payment_success(self, mocker):
        # Arrange
        mock_payment_api.charge.return_value = {
            "status": "success",
            "transaction_id": "txn_123"
        }
        
        payment_service = PaymentService()
        payment_data = {"amount": 100.00, "currency": "USD"}
        
        # Act
        result = payment_service.process_payment(payment_data)
        
        # Assert
        assert result["status"] == "success"
        mock_payment_api.charge.assert_called_once_with(payment_data)
```

## 测试环境管理

### 多环境配置
```python
# tests/conftest.py
import os
import pytest

@pytest.fixture(scope="session")
def test_env():
    """设置测试环境变量"""
    os.environ.update({
        "ENVIRONMENT": "testing",
        "DATABASE_URL": "sqlite:///./test.db",
        "REDIS_URL": "redis://localhost:6379/1",
        "SECRET_KEY": "test-secret-key"
    })
```

### CI/CD集成
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 测试最佳实践

### 1. 测试命名约定
```python
# 好的测试命名
def test_create_user_with_valid_data_should_return_user_object():
    pass

def test_create_user_with_duplicate_email_should_raise_validation_error():
    pass

def test_get_user_by_nonexistent_id_should_return_none():
    pass
```

### 2. AAA模式 (Arrange-Act-Assert)
```python
def test_calculate_order_total():
    # Arrange
    order_items = [
        {"price": 10.0, "quantity": 2},
        {"price": 5.0, "quantity": 1}
    ]
    tax_rate = 0.1
    
    # Act
    total = calculate_order_total(order_items, tax_rate)
    
    # Assert
    assert total == 27.5  # (20 + 5) * 1.1
```

### 3. 测试隔离
```python
@pytest.fixture(autouse=True)
def clean_database(db):
    """每个测试后清理数据库"""
    yield
    db.query(User).delete()
    db.query(Product).delete()
    db.commit()
```

### 4. 测试数据最小化
```python
def test_user_authentication():
    # 只创建测试所需的最少数据
    user = User(email="test@example.com", hashed_password="hashed")
    # 避免创建不必要的关联数据
```

## 调试和故障排除

### 测试调试技巧
```python
# 使用pytest的调试功能
pytest -s -vv test_file.py::test_function  # 详细输出
pytest --pdb test_file.py                  # 调试模式
pytest --lf                                # 只运行上次失败的测试
pytest -k "test_user"                      # 运行匹配的测试
```

### 常见问题解决
```python
# 1. 异步测试问题
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

# 2. 数据库事务问题
@pytest.fixture
def db_transaction(db):
    transaction = db.begin()
    yield db
    transaction.rollback()

# 3. 时间相关测试
from freezegun import freeze_time

@freeze_time("2023-01-01")
def test_time_dependent_function():
    result = get_current_timestamp()
    assert result == "2023-01-01T00:00:00"
```

## 测试文档和报告

### 测试报告生成
```bash
# 生成HTML测试报告
pytest --html=reports/report.html --self-contained-html

# 生成JUnit XML报告
pytest --junitxml=reports/junit.xml

# 生成覆盖率报告
pytest --cov=app --cov-report=html:reports/coverage
```

### 测试文档
- 为复杂的测试场景编写文档
- 记录测试数据的含义和用途
- 维护测试用例的变更历史
- 提供测试环境搭建指南

---

## 测试框架问题诊断与修复

### 🚨 常见测试架构问题

**1. 导入架构违规问题**：

**❌ 错误的导入方式** - 违反模块化架构：
```python
# 这种导入方式在当前项目中不存在
from app.models import Base, User, Product, Order, OrderItem, Cart
from app.database import DATABASE_URL
```

**问题分析：**
1. **违反模块边界**: 项目采用模块化架构，不存在统一的 `app.models`
2. **架构不一致**: 各模块有独立的 models.py 文件
3. **依赖混乱**: 跨模块导入破坏了架构设计

**✅ 正确的模块化导入**：
```python
from app.core.database import Base, get_db_engine
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Product  
from app.modules.order_management.models import Order, OrderItem
from app.modules.shopping_cart.models import Cart, CartItem
```

**2. 测试环境配置冲突**：

**问题**: SQLAlchemy关系配置冲突导致测试失败

**解决方案**: 使用隔离的测试配置
```python
# 正确的测试配置
@pytest.fixture(scope="function")
def isolated_test_db():
    """完全隔离的测试数据库"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
```

**3. 字段名称验证失败**：

**强制验证流程**:
1. **模型验证**: 使用 `read_file` 检查实际模型定义
2. **字段验证**: 确认每个测试用到的字段都实际存在
3. **方法验证**: 使用 `grep_search` 确认方法签名

**验证示例**:
```python
# 测试前必须验证
def test_payment_model_fields(self, test_db):
    """测试前验证 - 确保字段存在"""
    # 验证过的字段列表：
    # id, payment_no, order_id, user_id, amount, payment_method, 
    # status, external_payment_id, callback_data, description, expires_at
    
    payment = Payment(
        payment_no="PAY_20241201_001",  # ✅ 已验证存在
        order_id=1,                     # ✅ 已验证存在
        user_id=1,                      # ✅ 已验证存在
        amount=Decimal("99.99"),        # ✅ 已验证存在
        payment_method="wechat_pay",    # ✅ 已验证存在
        status="pending"                # ✅ 已验证存在
    )
```

### 修复工作流程

### 问题识别
1. 运行测试识别失败项目
2. 分析错误信息，区分导入错误vs逻辑错误
3. 使用工具验证当前架构状态

### 架构验证
```bash
# 检查模块结构
find app/modules -name "*.py" -type f | grep models

# 验证导入路径
python -c "from app.modules.user_auth.models import User; print('导入成功')"
```

### 逐项修复
1. 修复导入路径为模块化路径
2. 验证模型字段的实际存在性
3. 更新测试配置以避免关系冲突
4. 逐个运行测试确保修复生效

### 第四步：系统验证
```bash
# 运行全部测试验证修复效果
pytest tests/ -v --tb=short

# 确保100%测试通过
pytest tests/ --tb=no -q
```

### 预防措施

1. **强制文档验证**: 编写测试前必须读取相关模块文档
2. **字段验证工具**: 使用自动化工具验证字段存在性
3. **导入路径标准**: 建立并遵守模块化导入规范
4. **测试隔离**: 使用独立数据库配置避免冲突

## CI/CD 测试配置

### GitHub Actions 配置模板
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test_root_pass
          MYSQL_DATABASE: ecommerce_platform_test
          MYSQL_USER: test_user
          MYSQL_PASSWORD: test_pass
        ports:
          - 3308:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          python tools/validate_test_config.py
          pytest tests/unit/ --cov=app --cov-report=xml
          pytest tests/integration/ --cov=app --cov-append
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 测试失败处理标准

### 失败诊断流程
1. **错误分类**: 语法错误 > 导入错误 > 逻辑错误 > 环境错误
2. **优先级**: P0(阻塞) > P1(重要) > P2(一般) > P3(优化)
3. **处理时限**: P0立即修复, P1当日修复, P2本周修复, P3下版本修复

### 标准修复程序
```bash
# 1. 错误定位
pytest tests/ --tb=line | grep FAILED
# 2. 详细诊断  
pytest tests/path/to/failed_test.py -vv
# 3. 环境验证
.\tools\check_test_env.ps1
# 4. 修复验证
pytest tests/path/to/failed_test.py
```

## 测试数据管理

### 数据生命周期
- **创建**: 使用Factory模式生成标准测试数据
- **使用**: 仅在测试范围内有效
- **清理**: 测试结束自动清理，集成测试Docker容器重置

### 敏感数据处理
```python
# 使用假数据，禁止真实敏感信息
TEST_USER_EMAIL = "test@example.com"  # ✅
REAL_USER_EMAIL = "john@company.com"  # ❌

# 密码使用固定测试值
TEST_PASSWORD = "TestPass123"
TEST_HASH = "$2b$12$..."  # 预计算的测试哈希值
```

## 测试质量控制

### 覆盖率要求
- 单元测试: ≥90%
- 集成测试: ≥80% 
- 端到端测试: ≥70%
- 关键业务流程: 100%

### 质量门禁
```bash
# 提交前强制检查
pytest tests/ --cov=app --cov-fail-under=85
# 覆盖率不足 → 阻止提交
# 测试失败 → 阻止提交
```

### 测试审查标准
1. **命名规范**: 测试函数名清晰描述测试场景
2. **结构规范**: AAA模式 (Arrange-Act-Assert)
3. **独立性**: 测试间无依赖，可单独执行
4. **完整性**: 正常和异常场景全覆盖

## 问题查找索引

### 按问题类型查找
- **环境问题**: 查看"测试工具"章节
- **配置问题**: 查看"pytest.ini配置"和"conftest.py配置"章节  
- **数据库问题**: 查看"数据库策略"章节
- **Mock问题**: 查看"pytest-mock统一使用标准"章节
- **架构问题**: 查看"五层测试架构"章节
- **执行问题**: 查看"测试执行"章节

### 按测试类型查找
- **单元测试**: 查看"测试实现示例"章节
- **集成测试**: 查看"Docker环境配置"章节
- **E2E测试**: 查看"端到端测试指南"章节
- **烟雾测试**: 查看"测试层级"章节

---

## 相关文档
- [测试环境配置指南](../development/testing-setup.md) - 环境配置和故障排除
- [项目基础定义](../../PROJECT-FOUNDATION.md) - 测试目录组织
- [MASTER工作流程](../../MASTER.md) - 强制检查点


