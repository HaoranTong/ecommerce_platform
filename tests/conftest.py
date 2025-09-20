import sys
from pathlib import Path
import pytest
import pytest_mock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure project root is on sys.path for tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
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

# 测试数据库配置 - 符合testing-standards.md标准和脚本配置
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"  # 单元测试：内存数据库
SMOKE_TEST_DATABASE_URL = "sqlite:///./tests/smoke_test.db"  # 烟雾测试：文件数据库
# Integration Test Database Configuration (MySQL Docker) - 与setup_test_env.ps1一致
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://test_user:test_pass@localhost:3308/test_ecommerce"

# ========== Mock框架配置 [CHECK:TEST-001] ==========
@pytest.fixture(autouse=True)
def mock_setup(mocker):
    """
    全局Mock配置，为所有测试提供统一的Mock环境
    符合testing-standards.md第113-200行pytest-mock统一使用标准
    """
    # 设置Mock的默认行为和最佳实践
    # 确保Mock对象有明确的spec，避免AttributeError
    mocker.patch.object.__defaults__ = (None, True)  # 默认启用autospec
    
    # 为常用的外部依赖创建Mock
    # Redis Mock（避免测试时依赖外部Redis）
    mock_redis = mocker.Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1
    mocker.patch('app.core.redis_client.redis_client', mock_redis)
    
    # 日志Mock（避免测试时产生真实日志）
    mock_logger = mocker.Mock()
    mocker.patch('app.core.security_logger.security_logger', mock_logger)
    
    return mocker

# ========== 单元测试配置 ==========
@pytest.fixture(scope="function")
def unit_test_engine():
    """单元测试数据库引擎（内存数据库）[CHECK:TEST-001]"""
    from sqlalchemy import event
    
    # SQLite配置优化 - 启用外键约束和性能优化
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={
            "check_same_thread": False,
            "isolation_level": None,  # 启用autocommit模式以支持WAL
        },
        poolclass=None  # Disable connection pooling for test
    )
    
    # 启用SQLite外键约束和性能优化
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """为每个SQLite连接设置PRAGMA优化选项"""
        cursor = dbapi_connection.cursor()
        # 启用外键约束（确保数据完整性）
        cursor.execute("PRAGMA foreign_keys=ON")
        # 启用WAL模式（提高并发性能）
        cursor.execute("PRAGMA journal_mode=WAL")
        # 设置同步模式为NORMAL（平衡性能和安全性）
        cursor.execute("PRAGMA synchronous=NORMAL")
        # 启用查询优化器
        cursor.execute("PRAGMA optimize")
        cursor.close()
    
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
    """烟雾测试数据库引擎（文件）[CHECK:TEST-001]"""
    from sqlalchemy import event
    
    # SQLite文件数据库配置优化
    engine = create_engine(
        SMOKE_TEST_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "isolation_level": None,  # 启用autocommit模式以支持WAL
        }
    )
    
    # 为烟雾测试SQLite连接启用外键约束和性能优化
    @event.listens_for(engine, "connect")
    def set_smoke_sqlite_pragma(dbapi_connection, connection_record):
        """为烟雾测试SQLite连接设置PRAGMA优化选项"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA optimize")
        cursor.close()
    
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

# ========== E2E和专项测试配置 [CHECK:TEST-001] [CHECK:TEST-004] ==========

# E2E测试数据库配置（专用MySQL实例）- 使用独立数据库名
E2E_TEST_DATABASE_URL = "mysql+pymysql://test_user:test_pass@localhost:3308/test_ecommerce_e2e"

@pytest.fixture(scope="session")
def mysql_e2e_db():
    """
    E2E测试专用MySQL数据库配置
    符合testing-standards.md第598-645行E2E测试要求
    """
    from sqlalchemy import event
    
    engine = create_engine(
        E2E_TEST_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False  # E2E测试不需要SQL日志
    )
    
    # 创建E2E测试专用数据库
    try:
        Base.metadata.create_all(bind=engine)
        print("🔄 E2E测试数据库已准备完成")
        yield engine
    except Exception as e:
        print(f"❌ E2E测试数据库连接失败: {e}")
        pytest.skip("E2E测试需要MySQL数据库支持")
    finally:
        # E2E测试完成后清理数据
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture(scope="function")
def performance_test_db():
    """
    性能测试专用数据库配置
    符合testing-standards.md第646-691行性能测试要求
    """
    # 性能测试使用独立的内存数据库以避免IO影响
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=None,
        echo=False  # 性能测试关闭SQL日志以减少开销
    )
    
    # 为性能测试优化SQLite配置
    from sqlalchemy import event
    
    @event.listens_for(engine, "connect")
    def set_performance_sqlite_pragma(dbapi_connection, connection_record):
        """性能测试专用SQLite优化配置"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=MEMORY")  # 最快的日志模式
        cursor.execute("PRAGMA synchronous=OFF")      # 关闭同步以提升性能
        cursor.execute("PRAGMA cache_size=10000")     # 增大缓存
        cursor.execute("PRAGMA temp_store=MEMORY")    # 临时表存储在内存中
        cursor.close()
    
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def security_test_setup(mocker):
    """
    安全测试专用配置
    符合testing-standards.md第692-737行安全测试要求
    """
    # Mock安全相关组件以进行安全测试
    security_mocks = {
        'rate_limiter': mocker.Mock(),
        'auth_validator': mocker.Mock(),
        'input_sanitizer': mocker.Mock(),
        'csrf_protection': mocker.Mock(),
    }
    
    # 设置安全测试的默认行为
    security_mocks['rate_limiter'].is_allowed.return_value = True
    security_mocks['auth_validator'].validate_token.return_value = True
    security_mocks['input_sanitizer'].sanitize.side_effect = lambda x: x
    security_mocks['csrf_protection'].verify.return_value = True
    
    return security_mocks

# ========== 测试超时配置 [CHECK:TEST-001] ==========

@pytest.fixture(autouse=True)
def configure_test_timeouts(request):
    """
    根据测试标记自动配置测试超时时间
    符合testing-standards.md第830-877行超时管理要求
    """
    # 根据测试类型标记设置合适的超时时间
    if request.node.get_closest_marker("unit"):
        # 单元测试：2秒超时
        request.node.add_marker(pytest.mark.timeout(2))
    elif request.node.get_closest_marker("smoke"):  
        # 烟雾测试：10秒超时
        request.node.add_marker(pytest.mark.timeout(10))
    elif request.node.get_closest_marker("integration"):
        # 集成测试：30秒超时
        request.node.add_marker(pytest.mark.timeout(30))
    elif request.node.get_closest_marker("e2e"):
        # E2E测试：120秒超时
        request.node.add_marker(pytest.mark.timeout(120))
    elif request.node.get_closest_marker("performance"):
        # 性能测试：300秒超时
        request.node.add_marker(pytest.mark.timeout(300))
    # 如果没有特定标记，使用全局默认超时（pyproject.toml中的300秒）
