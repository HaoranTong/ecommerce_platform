import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure project root is on sys.path for tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.core.database import Base, get_db

# 测试数据库配置
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"
SMOKE_TEST_DATABASE_URL = "sqlite:///./tests/smoke_test.db"
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://test_user:test_pass@localhost:3307/test_ecommerce"

# ========== 单元测试配置 ==========
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

@pytest.fixture(scope="function")
def unit_test_client(unit_test_db):
    """单元测试客户端"""
    def override_get_db():
        yield unit_test_db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ========== 烟雾测试配置 ==========
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

@pytest.fixture(scope="function")
def smoke_test_client(smoke_test_db):
    """烟雾测试客户端"""
    def override_get_db():
        yield smoke_test_db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ========== 集成测试配置 ==========
@pytest.fixture(scope="session")
def integration_test_engine():
    """集成测试数据库引擎（MySQL）"""
    # 这里假设MySQL测试容器已经启动
    # 实际使用时需要docker-compose或脚本管理
    try:
        engine = create_engine(INTEGRATION_TEST_DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        yield engine
    except Exception as e:
        pytest.skip(f"MySQL测试数据库不可用: {e}")

@pytest.fixture(scope="function")
def integration_test_db(integration_test_engine):
    """集成测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=integration_test_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.rollback()
        database.close()

@pytest.fixture(scope="function")
def integration_test_client(integration_test_db):
    """集成测试客户端"""
    def override_get_db():
        yield integration_test_db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ========== 通用测试工具 ==========
@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }

@pytest.fixture  
def sample_product_data():
    """示例商品数据"""
    return {
        "name": "测试商品",
        "description": "这是一个测试商品",
        "price": 99.99,
        "sku": "TEST001",
        "stock_quantity": 100
    }
