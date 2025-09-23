<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions.md,project-structure-standards.md-->

# 测试标准

## 概述

本文档定义了电商平台项目的完整测试标准和规范，包括五层测试架构、测试类型分布、环境配置、编写规范等。确保代码质量和系统稳定性。

## 依赖标准

本标准依赖以下L1核心标准：

- **[项目结构标准](./project-structure-standards.md)** - 定义tests/目录结构和测试文件组织
- **[命名规范](./naming-conventions-standards.md)** - 测试文件、类、方法的命名约定

## 具体标准应用
⬆️ **测试文件结构**: 参见 [project-structure-standards.md](project-structure-standards.md#测试目录结构) - 五层测试架构组织
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

### 单元测试 (70%)
- test_models/: Mock测试
- test_services/: SQLite内存
- *_standalone.py: SQLite内存

### 烟雾测试 (2%)
- tests/smoke/: SQLite文件

### 集成测试 (20%)
- tests/integration/: MySQL Docker

### E2E测试 (6%)
- tests/e2e/: MySQL Docker

### 专项测试 (2%)
- 性能测试, 安全测试

## 数据库策略

| 测试位置 | Mock | 数据库 | Fixture |
|---------|------|--------|---------|
| tests/unit/test_models/ | 100% | 无 | pytest-mock |
| tests/unit/test_services/ | 0% | SQLite内存 | unit_test_db |
| tests/unit/*_standalone.py | 0% | SQLite内存 | unit_test_db |
| tests/smoke/ | 0% | SQLite文件 | smoke_test_db |
| tests/integration/ | 0% | MySQL Docker | mysql_integration_db |
| tests/e2e/ | 0% | MySQL Docker | mysql_e2e_db |

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

### 统一目录结构
```text
tests/
├── unit/                           # 单元测试 (70%)
│   ├── test_models/               # Mock测试 - 纯业务逻辑
│   ├── test_services/             # SQLite内存 - 数据交互
│   ├── test_utils/                # Mock测试 - 工具函数
│   └── *_standalone.py            # SQLite内存 - 业务流程
├── smoke/                         # 烟雾测试 (2%)
│   ├── test_health.py             # 健康检查
│   └── test_basic_api.py          # 基本API验证
├── integration/                   # 集成测试 (20%) 
│   ├── test_api/                  # HTTP API集成测试
│   └── test_database/             # 跨模块数据库测试
├── e2e/                          # 端到端测试 (6%)
│   ├── test_user_journey.py       # 用户完整流程
│   └── test_order_journey.py      # 订单完整流程
├── performance/                   # 性能测试 (1%)
├── security/                      # 安全测试 (1%)
└── conftest.py                    # 统一Fixture配置
```

### 测试文件分类执行规范

| 测试分类 | 存放位置 | 数据库 | 执行命令 | 执行时机 | 时间要求 |
|---------|---------|--------|---------|---------|----------|
| **Mock单元测试** | `tests/unit/test_models/` | 无 | `pytest tests/unit/test_models/` | 代码提交前 | <30秒 |
| **数据库单元测试** | `tests/unit/test_services/` | SQLite内存 | `pytest tests/unit/test_services/` | 代码提交前 | <1分钟 |
| **业务流程测试** | `tests/unit/*_standalone.py` | SQLite内存 | `pytest tests/unit/*_standalone.py` | 代码提交前 | <2分钟 |
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
- **需要保留**：移至scripts/目录并规范化
- **提交前**：必须在README.md中说明临时脚本的用途

### 测试文件命名规范
| 测试类型 | 命名规则 | 示例 |
|---------|---------|------|
| **单元测试** | `test_{module}.py` | `test_users.py`, `test_products.py` |
| **集成测试** | `test_{module}_integration.py` | `test_cart_integration.py` |
| **端到端测试** | `test_{scenario}_e2e.py` | `test_order_flow_e2e.py` |
| **系统测试脚本** | `test_{system}.ps1` | `test_cart_system.ps1` |

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
# pytest.ini - 项目根目录
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=app
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=85
    --cov-config=.coveragerc
markers =
    unit: 单元测试标记
    smoke: 烟雾测试标记  
    integration: 集成测试标记
    e2e: 端到端测试标记
    slow: 慢速测试标记
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

## .coveragerc 覆盖率配置

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

## Factory Boy 测试数据工厂

### 数据工厂标准结构
```python
# tests/factories/__init__.py
from .user_factory import UserFactory
from .product_factory import ProductFactory

# tests/factories/user_factory.py
import factory
from faker import Faker
from app.modules.user_auth.models import User

fake = Faker('zh_CN')

class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.LazyFunction(lambda: fake.email())
    username = factory.LazyFunction(lambda: fake.user_name())
    password_hash = "hashed_password_123"
    is_active = True
    created_at = factory.LazyFunction(lambda: fake.date_time())

# 使用示例
def test_user_creation(unit_test_db):
    user = UserFactory.build()  # 创建对象但不保存
    unit_test_db.add(user)
    unit_test_db.commit()
    assert user.email is not None
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
| **MySQL Docker** | 容器数据库 | `mysql://test_user:test_pass@localhost:3308/test_db` | 测试间清理 | 中等 (<200ms) | 集成测试 |

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
        "mysql+pymysql://test_user:test_pass@localhost:3308/ecommerce_platform_test",
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

**3. 集成测试执行 (提交前验证)**：
```bash
# 需要先启动MySQL Docker (端口3308)
docker-compose up -d mysql_test

# API集成测试
pytest tests/integration/test_api/ -v --tb=short
# 预期时间: <3分钟

# 数据库集成测试  
pytest tests/integration/test_database/ -v --tb=short
# 预期时间: <2分钟

# 所有集成测试
pytest tests/integration/ -v
# 预期时间: <5分钟, 必须100%通过
```

pytest tests/ --cov=app                # 全部测试
.\scripts\integration_test.ps1       # 使用脚本
`$language

## 测试工具

### 环境检查
```bash
.\scripts\check_test_env.ps1         # 测试前检查
.\scripts\setup_test_env.ps1         # 环境设置  
python scripts/validate_test_config.py  # 配置验证
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
.\scripts\setup_test_env.ps1 -TestType unit

# 集成测试 (自动管理Docker)
.\scripts\setup_test_env.ps1 -TestType integration

# 完整测试套件
.\scripts\setup_test_env.ps1 -TestType all
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
python scripts/validate_test_config.py
```

## 📋 强制性测试流程 (MASTER规范)

### 环境验证 (强制) [CHECK:TEST-001]
```powershell
# 必须通过的环境检查
.\scripts\check_test_env.ps1
```

### 选择测试类型并执行 [CHECK:TEST-002]

### 单元测试流程 (推荐)
```powershell
# 标准单元测试 - 使用SQLite内存数据库
.\scripts\setup_test_env.ps1 -TestType unit
```

### 集成测试流程
```powershell
# 自动设置MySQL Docker环境并执行测试
.\scripts\setup_test_env.ps1 -TestType integration
```

### 完整测试流程
```powershell
# 执行所有类型测试
.\scripts\setup_test_env.ps1 -TestType all
```

### 问题排查 (如需要) [CHECK:TEST-003]
```powershell
# 如果遇到环境问题，执行详细诊断
python scripts/validate_test_config.py
```

## 🚫 禁止的测试方式

根据MASTER规范，**禁止**以下测试执行方式：
- ❌ 直接运行 `pytest` 而不进行环境验证
- ❌ 在未激活虚拟环境情况下运行测试
- ❌ 跳过环境检查步骤
- ❌ 混用不同测试类型的数据库配置
- ❌ 手动管理Docker容器而非使用标准工具

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
.\scripts\smoke_test.ps1
```

### 集成测试（需要Docker）
```bash
# 启动Docker服务，然后运行集成测试
docker-compose up -d mysql
pytest tests/integration/ -v

# 或使用专用脚本（自动管理Docker）
.\scripts\integration_test.ps1
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
│   ├── test_models/
│   │   ├── test_user.py
│   │   ├── test_product.py
│   │   └── test_order.py
│   ├── test_services/
│   │   ├── test_auth_service.py
│   │   ├── test_user_service.py
│   │   └── test_order_service.py
│   └── test_utils/
│       ├── test_validators.py
│       └── test_helpers.py
├── integration/
│   ├── test_api/
│   │   ├── test_auth_routes.py
│   │   ├── test_user_routes.py
│   │   └── test_order_routes.py
│   └── test_database/
│       ├── test_user_repository.py
│       └── test_order_repository.py
└── e2e/
    ├── test_user_journey.py
    ├── test_order_journey.py
    └── test_admin_journey.py
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

### 数据库集成测试
```python
# tests/integration/test_database/test_user_repository.py
import pytest
from app.repositories.user_repository import UserRepository
from app.models.user import User

class TestUserRepository:
    
    @pytest.fixture
    def user_repo(self, db):
        return UserRepository(db)
    
    def test_create_and_get_user(self, user_repo, db):
        # Arrange
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password"
        }
        
        # Act
        created_user = user_repo.create(user_data)
        retrieved_user = user_repo.get_by_id(created_user.id)
        
        # Assert
        assert retrieved_user is not None
        assert retrieved_user.email == user_data["email"]
        assert retrieved_user.id == created_user.id
```

## 端到端测试指南

### E2E测试示例
```python
# tests/e2e/test_user_journey.py
import pytest
from fastapi.testclient import TestClient

class TestUserJourney:
    
    def test_complete_user_registration_and_login(self, client: TestClient):
        """测试跨模块用户注册和登录的完整端到端流程"""
        
        # 1. 用户注册
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123"
        }
        
        register_response = client.post("/api/v1/user-auth/register", json=registration_data)
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

### 测试数据工厂
```python
# tests/factories.py
from factory import Factory, Faker, SubFactory
from app.models.user import User
from app.models.product import Product

class UserFactory(Factory):
    class Meta:
        model = User
    
    email = Faker('email')
    username = Faker('user_name')
    hashed_password = Faker('password')
    is_active = True

class ProductFactory(Factory):
    class Meta:
        model = Product
    
    name = Faker('word')
    description = Faker('text')
    price = Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    stock_quantity = Faker('random_int', min=0, max=100)
```

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
          python scripts/validate_test_config.py
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
.\scripts\check_test_env.ps1
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
- [项目结构标准](project-structure-standards.md) - 测试目录组织
- [MASTER工作流程](../../MASTER.md) - 强制检查点


