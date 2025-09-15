"""
库存管理模块测试配置

提供测试所需的fixture和配置
"""

import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# 确保项目根目录在路径中
ROOT = Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.core.database import Base, get_db

# 导入所有必要的模型
from app.modules.inventory_management.models import (
    InventoryStock, InventoryReservation, InventoryTransaction
)
from app.modules.user_auth.models import User

# 测试数据库配置
_temp_db_fd, _temp_db_path = tempfile.mkstemp(suffix='_inventory_test.db')
os.close(_temp_db_fd)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{_temp_db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_test_database():
    """设置测试数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield
    # 清理
    Base.metadata.drop_all(bind=engine)
    try:
        os.unlink(_temp_db_path)
    except:
        pass


@pytest.fixture
def db_session(setup_test_database):
    """数据库会话fixture"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_client(db_session):
    """测试客户端fixture"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """管理员用户fixture"""
    user = User(
        id=1001,
        username="admin_test",
        email="admin@test.com",
        hashed_password="fake_hashed_password",
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session):
    """普通用户fixture"""
    user = User(
        id=1002,
        username="user_test", 
        email="user@test.com",
        hashed_password="fake_hashed_password",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_sku_inventory(db_session):
    """测试SKU库存fixture"""
    inventory = InventoryStock(
        sku_id="SKU001001",
        total_quantity=100,
        available_quantity=100,
        reserved_quantity=0,
        warning_threshold=10,
        critical_threshold=5,
        is_active=True
    )
    db_session.add(inventory)
    db_session.commit()
    db_session.refresh(inventory)
    return inventory


@pytest.fixture
def multiple_test_inventories(db_session):
    """多个测试SKU库存fixture"""
    inventories = [
        InventoryStock(
            sku_id="SKU002001",
            total_quantity=50,
            available_quantity=50,
            reserved_quantity=0,
            warning_threshold=15,
            critical_threshold=8,
            is_active=True
        ),
        InventoryStock(
            sku_id="SKU002002",
            total_quantity=8,  # 低库存
            available_quantity=8,
            reserved_quantity=0,
            warning_threshold=10,
            critical_threshold=5,
            is_active=True
        ),
        InventoryStock(
            sku_id="SKU002003",
            total_quantity=3,  # 严重不足
            available_quantity=3,
            reserved_quantity=0,
            warning_threshold=10,
            critical_threshold=5,
            is_active=True
        )
    ]
    
    for inventory in inventories:
        db_session.add(inventory)
    
    db_session.commit()
    
    for inventory in inventories:
        db_session.refresh(inventory)
    
    return inventories