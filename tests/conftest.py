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

# 导入模型以确保表被创建
# 产品目录模块模型
from app.modules.product_catalog.models import (
    Category, Brand, Product, SKU, ProductAttribute, 
    SKUAttribute, ProductImage, ProductTag
)
# 用户认证模块模型（API路由需要User模型）
from app.modules.user_auth.models import User, Role, Permission, UserRole, RolePermission, Session

# 库存管理模块模型
from app.modules.inventory_management.models import InventoryStock, InventoryReservation, InventoryTransaction

# 测试数据库配置
import tempfile
import os
# Create a temporary file for the test database to ensure shared connection
_temp_db_fd, _temp_db_path = tempfile.mkstemp(suffix='.db')
os.close(_temp_db_fd)  # Close the file descriptor but keep the path
UNIT_TEST_DATABASE_URL = f"sqlite:///{_temp_db_path}"
SMOKE_TEST_DATABASE_URL = "sqlite:///./tests/smoke_test.db"
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://test_user:test_pass@localhost:3307/test_ecommerce"

# ========== 单元测试配置 ==========
@pytest.fixture(scope="function")
def unit_test_engine():
    """单元测试数据库引擎（内存数据库）"""
    # 使用内存数据库避免索引冲突问题
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=None  # Disable connection pooling for test
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
def unit_test_client(unit_test_engine, mock_admin_user):
    """单元测试客户端"""
    # 导入认证函数
    from app.core.auth import get_current_user, get_current_active_user, get_current_admin_user
    
    def override_get_db():
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
        
    async def override_get_current_user():
        return mock_admin_user
        
    async def override_get_current_active_user():
        return mock_admin_user
        
    async def override_get_current_admin_user():
        return mock_admin_user
    
    # 清除现有依赖覆盖
    app.dependency_overrides.clear()
    
    # 设置依赖覆盖 - 覆盖整个认证链条
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
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
def smoke_test_client(smoke_test_db, mock_admin_user):
    """烟雾测试客户端"""
    # 导入认证函数
    from app.core.auth import get_current_user, get_current_active_user, get_current_admin_user
    
    def override_get_db():
        yield smoke_test_db
        
    async def override_get_current_user():
        return mock_admin_user
        
    async def override_get_current_active_user():
        return mock_admin_user
        
    async def override_get_current_admin_user():
        return mock_admin_user
    
    # 清除现有依赖覆盖
    app.dependency_overrides.clear()
    
    # 设置依赖覆盖 - 覆盖整个认证链条
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
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
def integration_test_client(integration_test_db, mock_admin_user):
    """集成测试客户端"""
    # 导入认证函数
    from app.core.auth import get_current_user, get_current_active_user, get_current_admin_user
    
    def override_get_db():
        yield integration_test_db
        
    async def override_get_current_user():
        return mock_admin_user
        
    async def override_get_current_active_user():
        return mock_admin_user
        
    async def override_get_current_admin_user():
        return mock_admin_user
    
    # 清除现有依赖覆盖
    app.dependency_overrides.clear()
    
    # 设置依赖覆盖 - 覆盖整个认证链条
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

# ========== 通用测试配置 ==========
@pytest.fixture
def test_client(unit_test_client):
    """通用测试客户端（默认使用单元测试配置）"""
    return unit_test_client

# ========== 通用测试工具 ==========
@pytest.fixture
def mock_admin_user():
    """模拟管理员用户"""
    from app.modules.user_auth.models import User
    mock_user = User(
        id=1,
        username="admin",
        email="admin@test.com",
        password_hash="mock_password_hash",
        role="admin",
        is_active=True,
        email_verified=True
    )
    return mock_user

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
