# 测试环境配置指南

## 文档说明
- **内容**：测试环境搭建、CI/CD配置、自动化测试、测试数据管理
- **使用者**：测试工程师、DevOps工程师、开发人员
- **更新频率**：测试流程和工具变更时更新
- **关联文档**：[开发环境配置](development-setup.md)、[生产环境配置](production-config.md)、[环境变量管理](environment-variables.md)

**[CHECK:TEST-001]** 测试环境配置必须支持自动化部署

---

## 🎯 测试环境概览

### 测试环境类型
```
单元测试环境 → 本地开发机器
集成测试环境 → Docker容器环境  
E2E测试环境 → 独立测试服务器
性能测试环境 → 生产规模的测试集群
```

### 测试数据流
```
开发数据 → 清理脚本 → 测试数据 → 自动化测试 → 结果报告
```

**[CHECK:ARCH-004]** 测试环境架构必须与生产环境保持一致

---

## 🐳 Docker测试环境

### 测试用Docker Compose
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      - ENVIRONMENT=testing
      - DATABASE_URL=mysql+pymysql://root:testpass@mysql-test:3306/ecommerce_test
      - REDIS_URL=redis://redis-test:6379/1
      - LOG_LEVEL=INFO
      - TESTING=true
    depends_on:
      - mysql-test
      - redis-test
    networks:
      - test-network
      
  mysql-test:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: testpass
      MYSQL_DATABASE: ecommerce_test
      MYSQL_USER: testuser
      MYSQL_PASSWORD: testpass
    tmpfs:
      - /var/lib/mysql  # 内存数据库，测试完自动清理
    networks:
      - test-network
      
  redis-test:
    image: redis:7-alpine
    networks:
      - test-network
    
  # 测试执行器
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    volumes:
      - .:/app
      - test-results:/app/test-results
    environment:
      - ENVIRONMENT=testing
      - DATABASE_URL=mysql+pymysql://root:testpass@mysql-test:3306/ecommerce_test
      - REDIS_URL=redis://redis-test:6379/1
    depends_on:
      - app
      - mysql-test
      - redis-test
    command: >
      sh -c "
        wait-for-it mysql-test:3306 -t 30 &&
        wait-for-it redis-test:6379 -t 30 &&
        wait-for-it app:8000 -t 30 &&
        pytest tests/ -v --cov=app --cov-report=html --cov-report=xml --junitxml=test-results/junit.xml
      "
    networks:
      - test-network

networks:
  test-network:
    driver: bridge

volumes:
  test-results:
```

### 测试Dockerfile
```dockerfile
# Dockerfile.test
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖和测试工具
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements*.txt ./

# 安装Python依赖（包括测试依赖）
RUN pip install --no-cache-dir -r requirements-dev.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TESTING=true

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 默认测试命令
CMD ["pytest", "tests/", "-v", "--cov=app"]
```

---

## 🔧 CI/CD集成配置

### GitHub Actions测试工作流
```yaml
# .github/workflows/test.yml
name: 测试工作流

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: 3.11

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpass
          MYSQL_DATABASE: ecommerce_test
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
          
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3

    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      
    - name: 设置Python环境
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
        
    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        
    - name: 代码格式检查
      run: |
        black --check app/ tests/
        isort --check-only app/ tests/
        
    - name: 代码质量检查
      run: |
        pylint app/
        mypy app/
        
    - name: 运行单元测试
      env:
        DATABASE_URL: mysql+pymysql://root:testpass@127.0.0.1:3306/ecommerce_test
        REDIS_URL: redis://127.0.0.1:6379/1
        ENVIRONMENT: testing
      run: |
        pytest tests/unit/ -v --cov=app --cov-report=xml
        
    - name: 运行集成测试
      env:
        DATABASE_URL: mysql+pymysql://root:testpass@127.0.0.1:3306/ecommerce_test
        REDIS_URL: redis://127.0.0.1:6379/1
        ENVIRONMENT: testing
      run: |
        pytest tests/integration/ -v
        
    - name: 上传覆盖率报告
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        
    - name: 生成测试报告
      if: always()
      run: |
        pytest tests/ --html=report.html --self-contained-html
        
    - name: 上传测试报告
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: report.html
```

### GitLab CI测试配置
```yaml
# .gitlab-ci.yml
stages:
  - test
  - integration
  - performance

variables:
  MYSQL_ROOT_PASSWORD: testpass
  MYSQL_DATABASE: ecommerce_test
  REDIS_URL: redis://redis:6379/1
  
services:
  - mysql:8.0
  - redis:7-alpine

before_script:
  - pip install -r requirements-dev.txt
  - export DATABASE_URL=mysql+pymysql://root:${MYSQL_ROOT_PASSWORD}@mysql:3306/${MYSQL_DATABASE}

test:unit:
  stage: test
  script:
    - pytest tests/unit/ -v --cov=app --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    expire_in: 1 week

test:integration:
  stage: integration
  script:
    - pytest tests/integration/ -v --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
    expire_in: 1 week

test:performance:
  stage: performance
  script:
    - pytest tests/performance/ -v --benchmark-json=benchmark.json
  artifacts:
    reports:
      performance: benchmark.json
    expire_in: 1 week
  only:
    - main
```

**[CHECK:TEST-004]** CI/CD流水线必须包含完整的测试阶段

---

## 📊 测试数据管理

### 测试数据工厂
```python
# tests/factories/test_data_factory.py
import factory
from datetime import datetime, timedelta
from app.models import User, Product, Category, Order

class CategoryFactory(factory.Factory):
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f"测试分类{n}")
    description = factory.Faker('text', max_nb_chars=100)
    is_active = True

class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    
    name = factory.Sequence(lambda n: f"测试产品{n}")
    description = factory.Faker('text', max_nb_chars=200)
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    stock_quantity = factory.Faker('random_int', min=0, max=1000)
    category = factory.SubFactory(CategoryFactory)
    is_active = True

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    username = factory.Sequence(lambda n: f"testuser{n}")
    hashed_password = factory.LazyAttribute(lambda obj: f"hashed_{obj.username}")
    is_active = True
    is_superuser = False

class TestDataBuilder:
    """测试数据构建器"""
    
    @staticmethod
    def create_test_scenario(scenario_name: str):
        """创建特定测试场景的数据"""
        if scenario_name == "basic_ecommerce":
            return TestDataBuilder._create_basic_ecommerce_data()
        elif scenario_name == "inventory_management":
            return TestDataBuilder._create_inventory_test_data()
        elif scenario_name == "user_permissions":
            return TestDataBuilder._create_user_permission_data()
    
    @staticmethod
    def _create_basic_ecommerce_data():
        # 创建基础电商测试数据
        categories = CategoryFactory.create_batch(3)
        products = []
        for category in categories:
            products.extend(ProductFactory.create_batch(5, category=category))
        users = UserFactory.create_batch(10)
        
        return {
            'categories': categories,
            'products': products,
            'users': users
        }
```

### 测试数据清理
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

@pytest.fixture(scope="session")
def test_engine():
    """测试数据库引擎"""
    DATABASE_URL = "mysql+pymysql://root:testpass@localhost:3306/ecommerce_test"
    engine = create_engine(DATABASE_URL)
    return engine

@pytest.fixture(scope="session")
def setup_database(test_engine):
    """设置测试数据库"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_engine, setup_database):
    """数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    # 重写依赖
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # 清理
    session.rollback()
    session.close()
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """自动清理测试数据"""
    yield
    
    # 清理所有表数据
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
```

### 测试环境变量
```bash
# .env.testing
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=INFO
TESTING=true

# 测试数据库配置
DATABASE_URL=mysql+pymysql://root:testpass@mysql-test:3306/ecommerce_test
TEST_DATABASE_URL=sqlite:///./test.db  # 快速测试用SQLite

# 测试Redis配置
REDIS_URL=redis://redis-test:6379/1
TEST_REDIS_URL=redis://localhost:6379/15  # 使用不同的数据库

# JWT配置（测试专用）
JWT_SECRET_KEY=test-secret-key-for-testing-only
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 测试专用配置
TEST_USER_EMAIL=testuser@example.com
TEST_USER_PASSWORD=testpass123
TEST_ADMIN_EMAIL=admin@example.com
TEST_ADMIN_PASSWORD=adminpass123

# 外部服务Mock配置
MOCK_EXTERNAL_SERVICES=true
MOCK_PAYMENT_SERVICE=true
MOCK_EMAIL_SERVICE=true

# 测试文件上传配置
TEST_UPLOAD_DIR=/tmp/test_uploads/
TEST_MAX_FILE_SIZE=1048576  # 1MB for testing
```

**[CHECK:TEST-002]** 测试数据必须与生产数据完全隔离

---

## 🧪 自动化测试配置

### pytest配置
```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    -q
    --strict-markers
    --strict-config
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
testpaths = tests
python_files = test_*.py *_test.py
python_functions = test_*
python_classes = Test*
markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    performance: 性能测试
    slow: 慢速测试
    smoke: 烟雾测试
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
```

### 测试配置管理
```python
# tests/config.py
import os
from typing import Dict, Any

class TestConfig:
    """测试配置管理"""
    
    # 数据库配置
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    # Redis配置  
    REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/15")
    
    # 测试用户配置
    TEST_USERS = {
        "regular_user": {
            "email": "user@test.com",
            "password": "testpass123"
        },
        "admin_user": {
            "email": "admin@test.com", 
            "password": "adminpass123"
        }
    }
    
    # Mock服务配置
    MOCK_SERVICES = {
        "payment_service": True,
        "email_service": True,
        "sms_service": True
    }
    
    # 测试超时配置
    TIMEOUTS = {
        "unit_test": 10,      # 单元测试超时10秒
        "integration_test": 30, # 集成测试超时30秒
        "e2e_test": 120       # E2E测试超时2分钟
    }

    @classmethod
    def get_database_url(cls) -> str:
        """获取测试数据库URL"""
        return cls.DATABASE_URL
    
    @classmethod
    def is_mock_enabled(cls, service: str) -> bool:
        """检查是否启用Mock服务"""
        return cls.MOCK_SERVICES.get(service, False)
```

### 并行测试配置
```bash
# 安装pytest-xdist用于并行测试
pip install pytest-xdist

# 并行运行测试
pytest tests/ -n auto  # 自动检测CPU核数
pytest tests/ -n 4     # 使用4个进程并行

# 分布式测试配置
pytest tests/ --dist=loadscope  # 按作用域分发
pytest tests/ --dist=loadfile   # 按文件分发
```

---

## 🔍 测试监控和报告

### 测试覆盖率监控
```python
# 覆盖率配置 .coveragerc
[run]
source = app
omit = 
    app/migrations/*
    app/tests/*
    app/venv/*
    app/.venv/*
    */site-packages/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

### 测试报告生成
```python
# tests/report_generator.py
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, results_dir: str = "test-results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def generate_summary_report(self):
        """生成测试摘要报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self._parse_junit_xml(),
            "coverage": self._parse_coverage_xml(),
            "performance": self._parse_benchmark_json()
        }
        
        report_file = self.results_dir / "test_summary.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def _parse_junit_xml(self):
        """解析JUnit XML报告"""
        junit_file = self.results_dir / "junit.xml"
        if not junit_file.exists():
            return {}
        
        tree = ET.parse(junit_file)
        root = tree.getroot()
        
        return {
            "total": int(root.get("tests", 0)),
            "passed": int(root.get("tests", 0)) - int(root.get("failures", 0)) - int(root.get("errors", 0)),
            "failed": int(root.get("failures", 0)),
            "errors": int(root.get("errors", 0)),
            "time": float(root.get("time", 0))
        }

# 生成测试报告的脚本
#!/bin/bash
# scripts/generate_test_report.sh
echo "生成测试报告..."

# 运行测试并生成报告
pytest tests/ \
  --cov=app \
  --cov-report=html \
  --cov-report=xml \
  --junitxml=test-results/junit.xml \
  --html=test-results/report.html \
  --self-contained-html

# 生成摘要报告
python tests/report_generator.py

echo "测试报告生成完成，查看 test-results/ 目录"
```

### 性能基准测试
```python
# tests/performance/test_benchmarks.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.performance
@pytest.mark.asyncio
async def test_api_performance():
    """API性能基准测试"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # 测试单个请求响应时间
        start_time = time.time()
        response = await client.get("/api/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # 响应时间小于100ms
        
        # 测试并发请求
        tasks = []
        for _ in range(100):
            task = client.get("/api/products")
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 验证所有请求都成功
        for response in responses:
            assert response.status_code == 200
        
        # 验证总耗时
        total_time = end_time - start_time
        assert total_time < 5.0  # 100个并发请求5秒内完成

@pytest.mark.benchmark
def test_database_query_performance(benchmark, db_session):
    """数据库查询性能测试"""
    
    def query_products():
        return db_session.query(Product).filter(Product.is_active == True).all()
    
    # 基准测试
    result = benchmark(query_products)
    assert len(result) >= 0
```

**[CHECK:TEST-006]** 性能测试必须设置明确的基准指标

---

## 🚀 E2E测试环境

### Playwright配置
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/e2e-results.xml' }]
  ],
  
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox', 
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'npm run start',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E测试脚本
```python
# tests/e2e/conftest.py
import pytest
from playwright.sync_api import sync_playwright
from app.main import app
import uvicorn
import threading
import time

@pytest.fixture(scope="session")
def test_server():
    """启动测试服务器"""
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8000)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    yield "http://127.0.0.1:8000"

@pytest.fixture
def browser():
    """浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser, test_server):
    """页面实例"""
    page = browser.new_page()
    page.goto(test_server)
    yield page
    page.close()
```

---

## 📋 测试环境检查清单

### 环境准备检查清单
- [ ] **数据库连接**: 测试数据库可正常连接
- [ ] **Redis连接**: 测试Redis实例可正常访问
- [ ] **环境变量**: 所有测试环境变量已正确配置
- [ ] **依赖安装**: 测试依赖包已完整安装
- [ ] **数据清理**: 测试数据自动清理机制正常
- [ ] **Mock服务**: 外部服务Mock配置正确
- [ ] **网络隔离**: 测试环境与生产环境完全隔离

### CI/CD集成检查清单
- [ ] **流水线配置**: CI/CD配置文件语法正确
- [ ] **测试阶段**: 单元测试、集成测试、E2E测试都已配置
- [ ] **并行执行**: 测试可以并行执行以提高效率
- [ ] **报告生成**: 测试报告和覆盖率报告自动生成
- [ ] **失败通知**: 测试失败时能及时通知相关人员
- [ ] **制品管理**: 测试报告等制品能正确保存和访问

**[CHECK:TEST-001]** 测试环境检查清单必须定期验证

---

## 🔧 故障排除

### 常见测试问题
| 问题类型 | 症状 | 解决方案 |
|----------|------|----------|
| 数据库连接失败 | 测试无法连接数据库 | 检查数据库服务状态和连接配置 |
| 测试数据污染 | 测试结果不稳定 | 确保测试间数据清理完整 |
| 并发测试冲突 | 并行测试失败 | 使用事务隔离或独立测试数据库 |
| Mock服务异常 | 外部依赖调用失败 | 检查Mock配置和服务状态 |
| 超时问题 | 测试执行超时 | 调整超时配置或优化测试性能 |

### 测试环境重置
```bash
#!/bin/bash
# scripts/reset_test_env.sh
echo "重置测试环境..."

# 停止测试服务
docker-compose -f docker-compose.test.yml down

# 清理测试数据
docker volume prune -f

# 重启测试环境
docker-compose -f docker-compose.test.yml up -d

# 等待服务启动
sleep 10

# 验证服务状态
docker-compose -f docker-compose.test.yml ps

echo "测试环境重置完成"
```

---

## 相关文档
- [开发环境配置](development-setup.md) - 本地开发环境搭建
- [生产环境配置](production-config.md) - 生产环境部署配置
- [环境变量管理](environment-variables.md) - 环境变量详细管理  
- [测试工具使用](../tools/testing-tools.md) - 测试工具详细说明
