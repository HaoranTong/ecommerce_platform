# 测试策略与实施指南

## 文档说明
- **内容**：测试策略、测试框架、测试实施指南和最佳实践
- **使用者**：开发人员、测试人员、DevOps工程师
- **更新频率**：随测试需求变化和框架升级更新
- **关联文档**：[开发工作流程](workflow.md)、[编码标准](standards.md)、[MASTER工作流程](../MASTER.md)

---

## 测试策略概览

### 测试金字塔
```
     /\    E2E Tests (10%)
    /  \   
   /____\  Integration Tests (20%)
  /______\  Unit Tests (70%)
```

### 测试层级定义
- **单元测试 (Unit Tests)**：测试单个函数或类的功能
- **集成测试 (Integration Tests)**：测试模块间的交互
- **端到端测试 (E2E Tests)**：测试完整的用户场景

## 测试脚本组织管理

### 测试脚本分类规范

| 测试类型 | 存放位置 | 命名规范 | 执行方式 | 生命周期 |
|---------|---------|---------|---------|---------|
| **单元测试** | `tests/` | `test_*.py` | `pytest tests/` | 长期维护 |
| **集成测试** | `tests/integration/` | `test_*_integration.py` | `pytest tests/integration/` | 长期维护 |
| **端到端测试** | `tests/e2e/` | `test_*_e2e.py` | `pytest tests/e2e/` | 长期维护 |
| **系统测试脚本** | `scripts/` | `*_test.ps1` | `.\scripts\*_test.ps1` | 长期维护 |
| **临时调试脚本** | 根目录 | `test_*.py` | `python test_*.py` | 临时使用 |

### 根目录测试脚本管理

#### 临时测试脚本使用规范
```powershell
# ✅ 允许的临时测试脚本
test_auth_integration.py     # 认证功能调试
test_inventory_api.py        # 库存API调试  
test_inventory_integration.py # 库存集成调试

# ❌ 禁止的命名方式
temp_test.py                 # 命名不明确
debug.py                     # 功能不清晰
my_test.py                   # 个人化命名
```

#### 清理规则
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
```
tests/
├── unit/                    # 单元测试
│   ├── test_models/         # 模型测试
│   ├── test_services/       # 服务测试
│   └── test_utils/          # 工具测试
├── integration/             # 集成测试
│   ├── test_api/            # API集成测试
│   ├── test_database/       # 数据库集成测试
│   └── test_cart_system.ps1 # 购物车系统测试脚本
├── e2e/                     # 端到端测试
│   ├── test_user_journey.py # 用户流程测试
│   └── test_order_journey.py # 订单流程测试
└── conftest.py              # pytest配置
```

## 测试框架和工具

### 主要测试框架
```bash
# 测试框架
pytest              # 主要测试框架
pytest-asyncio      # 异步测试支持
pytest-cov          # 覆盖率报告
pytest-mock         # Mock支持

# API测试
httpx               # HTTP客户端
fastapi.testclient  # FastAPI测试客户端

# 数据库测试
pytest-alembic      # 数据库迁移测试
sqlalchemy-utils    # 数据库测试工具
```

## 测试数据库配置策略

### 🎯 数据库分离策略
根据测试复杂度和环境需求，采用不同的数据库配置：

| 测试类型 | 数据库类型 | 配置方式 | 优势 | 使用场景 |
|----------|-----------|----------|------|----------|
| **单元测试** | SQLite内存 | `:memory:` | 速度极快，隔离性好 | 模型、服务逻辑测试 |
| **烟雾测试** | SQLite文件 | `test.db` | 快速，无外部依赖 | 基础功能验证 |
| **集成测试** | MySQL测试库 | Docker容器 | 真实环境，完整功能 | API、数据库交互测试 |
| **E2E测试** | MySQL测试库 | Docker容器 | 生产环境模拟 | 完整业务流程测试 |

### 🔧 测试环境配置

#### 单元测试 - SQLite内存数据库
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app

# 单元测试：SQLite内存数据库
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def unit_test_engine():
    """单元测试数据库引擎（内存）"""
    engine = create_engine(
        UNIT_TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def unit_test_db(unit_test_engine):
    """单元测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=unit_test_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()
```

#### 烟雾测试 - SQLite文件数据库
```python
# 烟雾测试：SQLite文件数据库
SMOKE_TEST_DATABASE_URL = "sqlite:///./tests/smoke_test.db"

@pytest.fixture(scope="module")
def smoke_test_engine():
    """烟雾测试数据库引擎（文件）"""
    engine = create_engine(
        SMOKE_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    # 清理测试数据但保留结构
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def smoke_test_db(smoke_test_engine):
    """烟雾测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False, 
        bind=smoke_test_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.rollback()  # 回滚事务，保持数据清洁
        database.close()
```

#### 集成测试 - MySQL Docker容器
```python
# 集成测试：MySQL Docker数据库
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://test_user:test_pass@localhost:3307/test_ecommerce"

@pytest.fixture(scope="session")
def integration_test_engine():
    """集成测试数据库引擎（MySQL）"""
    # 确保Docker容器已启动
    import subprocess
    subprocess.run([
        "docker", "run", "-d", "--name", "mysql_test",
        "-e", "MYSQL_ROOT_PASSWORD=test_root_pass",
        "-e", "MYSQL_DATABASE=test_ecommerce", 
        "-e", "MYSQL_USER=test_user",
        "-e", "MYSQL_PASSWORD=test_pass",
        "-p", "3307:3306",
        "mysql:8.0"
    ], check=False)
    
    # 等待数据库启动
    import time
    time.sleep(10)
    
    engine = create_engine(INTEGRATION_TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    
    # 清理Docker容器
    subprocess.run(["docker", "stop", "mysql_test"], check=False)
    subprocess.run(["docker", "rm", "mysql_test"], check=False)
```

### 🚀 测试执行命令

#### 单元测试（快速，无外部依赖）
```bash
# 运行所有单元测试
pytest tests/unit/ -v

# 运行特定模块单元测试
pytest tests/unit/test_services/ -v

# 单元测试覆盖率
pytest tests/unit/ --cov=app/modules --cov-report=html
```

#### 烟雾测试（快速验证）
```bash
# 运行烟雾测试
pytest tests/smoke/ -v

# 或使用专用脚本
.\scripts\smoke_test.ps1
```

#### 集成测试（需要Docker）
```bash
# 启动Docker服务，然后运行集成测试
docker-compose up -d mysql
pytest tests/integration/ -v

# 或使用专用脚本（自动管理Docker）
.\scripts\integration_test.ps1
```

### 🎯 测试策略决策树

```
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
```
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
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
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
    
    def test_create_user_duplicate_email(self, user_service, mock_db):
        # Arrange
        user_data = {"email": "existing@example.com"}
        mock_db.query.return_value.filter.return_value.first.return_value = Mock()
        
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
        """测试用户注册和登录的完整流程"""
        
        # 1. 用户注册
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123"
        }
        
        register_response = client.post("/api/v1/auth/register", json=registration_data)
        assert register_response.status_code == 201
        
        # 2. 用户登录
        login_data = {
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
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
    response = client.post("/api/v1/auth/login", json=login_data)
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
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def get_products(self):
        self.client.get("/api/v1/products")
    
    @task(2)
    def get_user_profile(self):
        self.client.get("/api/v1/users/me")
    
    @task(1)
    def create_order(self):
        self.client.post("/api/v1/orders", json={
            "product_id": 1,
            "quantity": 1
        })
```

## Mock和存根

### Mock外部依赖
```python
# tests/unit/test_external_services.py
import pytest
from unittest.mock import patch, Mock
from app.services.payment_service import PaymentService

class TestPaymentService:
    
    @patch('app.services.payment_service.external_payment_api')
    def test_process_payment_success(self, mock_payment_api):
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

## 相关文档
- [开发工作流程](workflow.md) - 包含测试流程
- [编码标准](standards.md) - 代码质量标准
- [MASTER工作流程](../MASTER.md) - 强制检查点包含测试要求
- [架构概览](../architecture/overview.md) - 系统测试架构
