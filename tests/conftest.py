import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text
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

# 订单管理模块模型
from app.modules.order_management.models import Order, OrderItem, OrderStatusHistory

# 支付服务模块模型  
from app.modules.payment_service.models import Payment, Refund

# 测试数据库配置 - 符合testing-standards.md标准
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"  # 单元测试：内存数据库
SMOKE_TEST_DATABASE_URL = "sqlite:///./tests/smoke_test.db"  # 烟雾测试：文件数据库
# Integration Test Database Configuration (MySQL Docker)
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"

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

# 添加测试隔离机制 - 符合testing-standards.md第896-902行要求
@pytest.fixture(autouse=True)
def clean_database_after_test(unit_test_db):
    """每个测试后自动清理数据库 - 确保测试隔离"""
    yield
    # 清理所有测试数据，按照外键依赖顺序删除
    try:
        # 1. 先清理关联表
        unit_test_db.query(OrderItem).delete()
        unit_test_db.query(OrderStatusHistory).delete()
        unit_test_db.query(Refund).delete()
        unit_test_db.query(Payment).delete()
        unit_test_db.query(Order).delete()
        
        # 2. 清理用户相关
        unit_test_db.query(RolePermission).delete()
        unit_test_db.query(UserRole).delete()
        unit_test_db.query(Session).delete()
        
        # 3. 清理基础数据
        unit_test_db.query(User).delete()
        unit_test_db.query(Permission).delete()
        unit_test_db.query(Role).delete()
        
        # 4. 清理产品相关
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
    except Exception as e:
        unit_test_db.rollback()
        # 忽略清理错误，避免影响测试结果
        pass

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
    """集成测试数据库引擎（使用现有MySQL Docker容器）"""
    print("🐳 使用现有MySQL容器进行集成测试...")
    
    try:
        engine = create_engine(INTEGRATION_TEST_DATABASE_URL)
        
        # 确保导入所有模型以创建完整的数据库schema
        from app.modules.user_auth.models import User, Role, Permission, UserRole, RolePermission, Session
        from app.modules.product_catalog.models import Category, Brand, Product, SKU, ProductAttribute, SKUAttribute, ProductImage, ProductTag
        from app.modules.shopping_cart.models import Cart, CartItem
        from app.modules.order_management.models import Order, OrderItem
        from app.modules.payment_service.models import Payment, Refund
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ MySQL集成测试数据库已准备完成")
        yield engine
    finally:
        # 清理测试数据但保留表结构
        print("🧹 清理测试数据...")
        try:
            with engine.begin() as conn:
                # 禁用外键检查
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                
                # 删除所有表的数据，但保留表结构
                for table in reversed(Base.metadata.sorted_tables):
                    conn.execute(table.delete())
                    # 重置MySQL自增ID
                    conn.execute(text(f"ALTER TABLE {table.name} AUTO_INCREMENT = 1"))
                
                # 重新启用外键检查
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                
        except Exception as e:
            print(f"清理数据时出错: {e}")
        engine.dispose()

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

# 添加集成测试数据隔离机制
@pytest.fixture(autouse=True)
def clean_integration_test_data(request, integration_test_engine):
    """集成测试每个测试后自动清理数据库 - 确保测试隔离"""
    # 只对集成测试生效
    if not any(marker.name == 'integration' for marker in request.node.iter_markers()):
        yield
        return
    
    yield  # 运行测试
    
    # 测试后清理数据
    try:
        with integration_test_engine.begin() as conn:
            # 禁用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 按照依赖顺序清理数据
            cleanup_tables = [
                'order_items', 'order_status_history', 'refunds', 'payments', 'orders',
                'role_permissions', 'user_roles', 'sessions', 'users', 'permissions', 'roles',
                'inventory_transactions', 'inventory_reservations', 'inventory_stocks',
                'sku_attributes', 'product_attributes', 'product_images', 'product_tags',
                'skus', 'products', 'brands', 'categories'
            ]
            
            for table_name in cleanup_tables:
                try:
                    conn.execute(text(f"DELETE FROM {table_name}"))
                    conn.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"))
                except Exception as table_error:
                    # 表可能不存在，忽略错误
                    pass
            
            # 重新启用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
    except Exception as e:
        print(f"集成测试数据清理出错: {e}")
        # 不抛出异常，避免影响测试结果

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
