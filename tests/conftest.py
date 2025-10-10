import sys
from pathlib import Path
import os

# 在任何应用导入之前设置测试数据库环境变量
os.environ["DATABASE_URL"] = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"

import pytest
import pytest_mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ensure project root is on sys.path for tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import Base, get_db
from app.main import app
# 库存管理模块模型
from app.modules.inventory_management.models import (InventoryReservation,
                                                     InventoryStock,
                                                     InventoryTransaction)
# 订单管理模块模型
from app.modules.order_management.models import (Order, OrderItem,
                                                 OrderStatusHistory)
# 支付服务模块模型
from app.modules.payment_service.models import Payment, Refund
# 导入模型以确保表被创建
# 产品目录模块模型
from app.modules.product_catalog.models import (SKU, Brand, Category, Product,
                                                ProductAttribute, ProductImage,
                                                ProductTag, SKUAttribute)
# 用户认证模块模型（API路由需要User模型）
from app.modules.user_auth.models import (Permission, Role, RolePermission,
                                          Session, User, UserRole)
# 恢复通用数据工厂 - 双工厂模式的重要组成部分
from tests.factories.data_factory import (StandardTestDataFactory,
                                          TestDataValidator)

# 测试数据库配置 - 根据环境动态选择

# ========== 共同认证辅助函数 ==========
import uuid

def create_test_admin_user():
    """创建测试管理员用户的共同函数"""
    unique_id = str(uuid.uuid4())[:8]
    return User(
        username=f"test_admin_{unique_id}",
        email=f"admin_{unique_id}@test.com", 
        password_hash="$2b$12$dummy_hash_for_testing",
        role="admin",
        is_active=True,
        email_verified=True
    )

def create_test_regular_user():
    """创建测试普通用户的共同函数"""
    unique_id = str(uuid.uuid4())[:8]
    return User(
        username=f"test_user_{unique_id}",
        email=f"user_{unique_id}@test.com", 
        password_hash="$2b$12$dummy_hash_for_testing",
        role="user",
        is_active=True,
        email_verified=True
    )

def create_and_save_test_user(db, user_func, **kwargs):
    """创建并保存测试用户到数据库的通用函数"""
    from datetime import datetime
    
    user = user_func()
    
    # 应用额外的属性
    for key, value in kwargs.items():
        setattr(user, key, value)
    
    # 设置时间戳
    if not hasattr(user, 'created_at') or user.created_at is None:
        user.created_at = datetime.utcnow()
    if not hasattr(user, 'updated_at') or user.updated_at is None:
        user.updated_at = datetime.utcnow()
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_smoke_test_config():
    """根据环境变量动态选择烟雾测试配置"""
    mode = os.getenv("SMOKE_TEST_MODE", "development")
    
    if mode == "post_deployment":
        # 部署后测试：使用现有数据库连接，不创建测试数据库
        return {
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
            "scope": "session",
            "cleanup_mode": "none",  # 不清理生产数据
            "create_tables": False,  # 不创建表结构
            "description": "部署后验证模式：测试现有生产环境"
        }
    elif mode == "ci_pipeline":
        # CI管道测试：临时文件数据库
        return {
            "database_url": "sqlite:///./tests/smoke_test_ci.db",
            "scope": "session", 
            "cleanup_mode": "file_cleanup",
            "create_tables": True,
            "description": "CI管道模式：使用临时文件数据库"
        }
    else:  # development (默认)
        # 开发测试：内存数据库，快速清理
        return {
            "database_url": "sqlite:///:memory:",
            "scope": "function",
            "cleanup_mode": "immediate",
            "create_tables": True,
            "description": "开发模式：使用内存数据库"
        }

# 获取当前烟雾测试配置
SMOKE_CONFIG = get_smoke_test_config()
print(f"🔍 烟雾测试配置: {SMOKE_CONFIG['description']}")

UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"  # 单元测试：内存数据库
SMOKE_TEST_DATABASE_URL = SMOKE_CONFIG["database_url"]  # 动态烟雾测试数据库
# Integration Test Database Configuration (MySQL Docker) - 与setup_test_env.ps1一致
INTEGRATION_TEST_DATABASE_URL = (
    "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"
)


# ========== Mock框架配置 [CHECK:TEST-001] ==========
@pytest.fixture(autouse=True)
def mock_setup(request, mocker):
    """
    全局Mock配置，为所有测试提供统一的Mock环境
    符合testing-standards.md第113-200行pytest-mock统一使用标准
    
    重要：集成测试（@pytest.mark.integration）不使用Mock，使用真实服务
    单元测试使用AsyncMock支持异步操作
    """
    # 检测是否是集成测试
    is_integration_test = any(marker.name == "integration" for marker in request.node.iter_markers())
    
    if is_integration_test:
        # 集成测试：不使用Mock，直接返回
        return mocker
    
    # 单元测试：设置Mock的默认行为和最佳实践
    # 确保Mock对象有明确的spec，避免AttributeError
    # 注意：不直接修改__defaults__，而是在使用时指定autospec

    # 为常用的外部依赖创建AsyncMock（支持异步操作）
    # Redis Mock（避免测试时依赖外部Redis）
    mock_redis = mocker.AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True  # 支持验证码服务的setex操作
    mock_redis.delete.return_value = 1
    mocker.patch("app.core.redis_client.get_redis_connection", return_value=mock_redis)

    # 日志Mock（避免测试时产生真实日志）
    # mock_logger = mocker.Mock()
    # mocker.patch('app.core.security_logger.security_logger', mock_logger)  # 暂时注释，避免AttributeError

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
        poolclass=None,  # Disable connection pooling for test
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
        autocommit=False, autoflush=False, bind=unit_test_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


# 添加测试隔离机制 - 符合testing-standards.md第896-902行要求
@pytest.fixture(autouse=True)
def clean_database_after_test(request):
    """每个测试后自动清理数据库 - 确保测试隔离 [CHECK:TEST-002]"""
    # 只对单元测试生效 - 避免与集成测试fixture冲突
    if any(marker.name == "integration" for marker in request.node.iter_markers()):
        yield
        return

    # 为单元测试获取unit_test_db fixture - 仅当需要时
    try:
        unit_test_db_session = request.getfixturevalue("unit_test_db")
    except Exception:
        # 如果无法获取fixture（例如集成测试），跳过清理
        yield
        return

    yield
    # 清理所有测试数据，按照外键依赖顺序删除
    try:
        # 1. 先清理关联表
        unit_test_db_session.query(OrderItem).delete()
        unit_test_db_session.query(OrderStatusHistory).delete()
        unit_test_db_session.query(Refund).delete()
        unit_test_db_session.query(Payment).delete()
        unit_test_db_session.query(Order).delete()

        # 2. 清理用户相关
        unit_test_db_session.query(RolePermission).delete()
        unit_test_db_session.query(UserRole).delete()
        unit_test_db_session.query(Session).delete()

        # 3. 清理基础数据
        unit_test_db_session.query(User).delete()
        unit_test_db_session.query(Permission).delete()
        unit_test_db_session.query(Role).delete()

        # 4. 清理产品相关
        unit_test_db_session.query(InventoryTransaction).delete()
        unit_test_db_session.query(InventoryReservation).delete()
        unit_test_db_session.query(InventoryStock).delete()
        unit_test_db_session.query(SKUAttribute).delete()
        unit_test_db_session.query(ProductAttribute).delete()
        unit_test_db_session.query(ProductImage).delete()
        unit_test_db_session.query(ProductTag).delete()
        unit_test_db_session.query(SKU).delete()
        unit_test_db_session.query(Product).delete()
        unit_test_db_session.query(Brand).delete()
        unit_test_db_session.query(Category).delete()

        unit_test_db_session.commit()
    except Exception as e:
        unit_test_db_session.rollback()
        # 忽略清理错误，避免影响测试结果
        pass


@pytest.fixture(scope="function")
def unit_test_client(unit_test_engine, mock_admin_user):
    """单元测试客户端"""
    # 导入认证函数
    from app.core.auth import (get_current_active_user, get_current_admin_user,
                               get_current_user)

    def override_get_db():
        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=unit_test_engine
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
@pytest.fixture(scope=SMOKE_CONFIG["scope"])
def smoke_test_engine():
    """环境感知的烟雾测试数据库引擎[CHECK:TEST-001]"""
    from sqlalchemy import event
    
    print(f"🔍 烟雾测试引擎配置: {SMOKE_CONFIG['description']}")
    
    # 创建数据库引擎
    if SMOKE_CONFIG["database_url"].startswith("sqlite:///:memory:"):
        # 内存数据库配置
        engine = create_engine(
            SMOKE_CONFIG["database_url"],
            connect_args={"check_same_thread": False},
        )
    elif SMOKE_CONFIG["database_url"].startswith("sqlite:///"):
        # 文件数据库配置
        engine = create_engine(
            SMOKE_CONFIG["database_url"],
            connect_args={
                "check_same_thread": False,
                "isolation_level": None,  # 启用autocommit模式以支持WAL
            },
        )
        
        # SQLite性能优化
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA optimize")
            cursor.close()
    else:
        # MySQL/PostgreSQL等其他数据库
        engine = create_engine(SMOKE_CONFIG["database_url"])

    # 根据配置决定是否创建表结构
    if SMOKE_CONFIG["create_tables"]:
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ 数据库表结构创建完成")
        except Exception as e:
            print(f"⚠️  数据库表创建失败: {e}")
    else:
        print("ℹ️  跳过表创建（部署后模式）")
    
    yield engine
    
    # 根据清理模式执行不同的清理策略
    cleanup_mode = SMOKE_CONFIG["cleanup_mode"]
    if cleanup_mode == "file_cleanup":
        # CI模式：删除临时数据库文件
        try:
            engine.dispose()
            db_file = SMOKE_CONFIG["database_url"].replace("sqlite:///./", "")
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"🧹 已清理临时数据库: {db_file}")
        except Exception as e:
            print(f"⚠️  清理临时数据库失败: {e}")
    elif cleanup_mode == "immediate":
        # 开发模式：立即清理（内存数据库自动清理）
        engine.dispose()
        print("🧹 内存数据库已自动清理")
    else:
        # 部署后模式：不清理生产数据
        engine.dispose()
        print("ℹ️  保持生产环境数据不变")


@pytest.fixture(scope="function")
def smoke_test_db(smoke_test_engine):
    """烟雾测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=smoke_test_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.rollback()  # 回滚事务，保持数据清洁
        database.close()


@pytest.fixture(scope="function")
def smoke_test_client(smoke_test_db, mock_admin_user):
    """烟雾测试客户端 - 使用Mock认证（方案1）"""
    # 导入认证函数
    from app.core.auth import (get_current_active_user, get_current_admin_user,
                               get_current_user)

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


# 为了向后兼容，提供一个mock_api_client fixture
@pytest.fixture(scope="function") 
def mock_api_client(mysql_integration_db, mock_admin_user):
    """Mock认证的API客户端（向后兼容）"""
    
    # 导入认证函数
    from app.core.auth import (get_current_active_user, get_current_admin_user,
                               get_current_user)

    def override_get_db():
        yield mysql_integration_db

    async def override_get_current_user():
        return mock_admin_user

    async def override_get_current_active_user():
        return mock_admin_user

    async def override_get_current_admin_user():
        return mock_admin_user

    # 保存原始环境变量
    original_database_url = os.environ.get("DATABASE_URL")

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
        # 恢复原始环境变量
        if original_database_url is not None:
            os.environ["DATABASE_URL"] = original_database_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        app.dependency_overrides.clear()


# ========== 集成测试配置 ==========
@pytest.fixture(scope="session")
def mysql_integration_engine():
    """集成测试数据库引擎（使用现有MySQL Docker容器）"""
    print("🐳 使用现有MySQL容器进行集成测试...")

    try:
        engine = create_engine(INTEGRATION_TEST_DATABASE_URL)
        
        # 所有模型已在文件顶部导入，SQLAlchemy会自动处理表创建

        # 创建所有表（先删除再创建，确保表结构是最新的）
        with engine.begin() as conn:
            # 禁用外键检查以允许删除表
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
        # 删除并重新创建所有表
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        with engine.begin() as conn:
            # 重新启用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
        print("✅ MySQL集成测试数据库已准备完成（表结构已更新）")
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
def mysql_integration_db(mysql_integration_engine):
    """集成测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=mysql_integration_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.rollback()
        database.close()


# 添加集成测试数据隔离机制
@pytest.fixture(autouse=True)
def clean_integration_test_data(request):
    """集成测试每个测试后自动清理数据库 - 确保测试隔离 [CHECK:TEST-002]"""
    # 只对集成测试生效
    if not any(marker.name == "integration" for marker in request.node.iter_markers()):
        yield
        return

    # 只在集成测试时获取mysql_integration_engine
    try:
        mysql_integration_engine = request.getfixturevalue("mysql_integration_engine")
    except Exception:
        # 如果无法获取fixture，跳过清理
        yield
        return

    yield  # 运行测试

    # 测试后清理数据
    try:
        with mysql_integration_engine.begin() as conn:
            # 禁用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

            # 按照依赖顺序清理数据
            cleanup_tables = [
                "order_items",
                "order_status_history",
                "refunds",
                "payments",
                "orders",
                "role_permissions",
                "user_roles",
                "sessions",
                "users",
                "permissions",
                "roles",
                "inventory_transactions",
                "inventory_reservations",
                "inventory_stocks",
                "sku_attributes",
                "product_attributes",
                "product_images",
                "product_tags",
                "skus",
                "products",
                "brands",
                "categories",
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
def api_client(mysql_integration_db):
    """集成测试客户端 - 使用真实JWT认证（方案2）"""
    from datetime import datetime, timedelta
    from app.core.auth import create_access_token
    from app.modules.user_auth.models import User
    
    def override_get_db():
        yield mysql_integration_db

    # 保存原始环境变量
    original_database_url = os.environ.get("DATABASE_URL")
    
    # 清除现有依赖覆盖，只覆盖数据库连接
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            # 为测试客户端添加认证帮助方法
            def authenticate_as_admin():
                """创建管理员用户并返回JWT token"""
                # 使用共同的辅助函数创建管理员用户
                admin_user = create_test_admin_user()
                admin_user.created_at = datetime.utcnow()
                admin_user.updated_at = datetime.utcnow()
                admin_user.email_verified = True
                admin_user.status = "active"
                admin_user.phone_verified = True
                admin_user.two_factor_enabled = False
                
                mysql_integration_db.add(admin_user)
                mysql_integration_db.commit()
                mysql_integration_db.refresh(admin_user)
                
                # 生成真实JWT token - 使用统一工具
                from tests.utils.token_utils import create_test_token
                access_token = create_test_token(
                    user_id=admin_user.id,
                    expires_delta=timedelta(hours=1)
                )
                return access_token, admin_user

            def authenticate_as_user():
                """创建普通用户并返回JWT token"""
                from app.core.auth import get_password_hash
                
                # 使用真实的密码和hash
                test_password = "TestPassword123!"
                password_hash = get_password_hash(test_password)
                
                # 使用共同的辅助函数创建普通用户
                normal_user = create_test_regular_user()
                normal_user.password_hash = password_hash
                normal_user.created_at = datetime.utcnow()
                normal_user.updated_at = datetime.utcnow()
                normal_user.email_verified = True
                normal_user.status = "active"
                normal_user.phone_verified = True
                normal_user.two_factor_enabled = False
                
                mysql_integration_db.add(normal_user)
                mysql_integration_db.commit()
                mysql_integration_db.refresh(normal_user)
                
                # 生成真实JWT token - 使用统一工具
                from tests.utils.token_utils import create_test_token
                access_token = create_test_token(
                    user_id=normal_user.id,
                    expires_delta=timedelta(hours=1)
                )
                
                # 返回token, user和密码
                return access_token, normal_user, test_password

            def set_auth_headers(token: str):
                """设置认证头"""
                test_client.headers.update({"Authorization": f"Bearer {token}"})

            def clear_auth_headers():
                """清除认证头"""
                if "Authorization" in test_client.headers:
                    del test_client.headers["Authorization"]

            # 添加认证帮助方法到测试客户端
            test_client.authenticate_as_admin = authenticate_as_admin
            test_client.authenticate_as_user = authenticate_as_user
            test_client.set_auth_headers = set_auth_headers
            test_client.clear_auth_headers = clear_auth_headers
            
            yield test_client
    finally:
        # 恢复原始环境变量
        if original_database_url is not None:
            os.environ["DATABASE_URL"] = original_database_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")  
async def async_api_client(mysql_integration_db):
    """异步API客户端 - 用于性能和安全测试
    
    专门为需要真实并发能力的测试提供AsyncClient：
    - 性能测试：测试并发性能和吞吐量
    - 安全测试：测试在并发攻击下的防护能力
    
    使用httpx.AsyncClient以支持真正的异步HTTP请求
    """
    from httpx import AsyncClient
    from app.core.database import get_db
    
    def override_get_db():
        yield mysql_integration_db

    # 清除现有依赖覆盖，只覆盖数据库连接
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://testserver") as async_client:
            # 为异步客户端添加认证帮助方法
            async def authenticate_as_admin():
                """创建管理员用户并返回JWT token"""
                from datetime import datetime, timedelta
                
                # 使用共同的辅助函数创建管理员用户
                admin_user = create_test_admin_user()
                admin_user.created_at = datetime.now()
                admin_user.updated_at = datetime.now()
                
                mysql_integration_db.add(admin_user)
                mysql_integration_db.commit()
                mysql_integration_db.refresh(admin_user)
                
                # 创建JWT token - 使用统一工具确保格式标准
                from tests.utils.token_utils import create_test_token
                access_token = create_test_token(
                    user_id=admin_user.id,
                    expires_delta=timedelta(hours=1)
                )
                
                return access_token, admin_user

            async def authenticate_as_user():
                """创建普通用户并返回JWT token"""
                from datetime import datetime, timedelta
                from app.core.auth import get_password_hash
                
                # 使用真实的密码和hash
                test_password = "TestPassword123!"
                password_hash = get_password_hash(test_password)
                
                # 使用共同的辅助函数创建普通用户
                normal_user = create_test_regular_user()
                normal_user.password_hash = password_hash
                normal_user.email_verified = True
                normal_user.status = "active"
                normal_user.phone_verified = True
                normal_user.two_factor_enabled = False
                normal_user.created_at = datetime.now()
                normal_user.updated_at = datetime.now()
                
                mysql_integration_db.add(normal_user)
                mysql_integration_db.commit()
                mysql_integration_db.refresh(normal_user)
                
                # 生成真实JWT token - 使用统一工具
                from tests.utils.token_utils import create_test_token
                access_token = create_test_token(
                    user_id=normal_user.id,
                    expires_delta=timedelta(hours=1)
                )
                
                return access_token, normal_user

            # 添加认证方法到客户端
            async_client.authenticate_as_admin = authenticate_as_admin
            async_client.authenticate_as_user = authenticate_as_user
            yield async_client
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
        email_verified=True,
    )
    return mock_user


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }


@pytest.fixture
def sample_product_data():
    """示例商品数据"""
    return {
        "name": "测试商品",
        "description": "这是一个测试商品",
        "price": 99.99,
        "sku": "TEST001",
        "stock_quantity": 100,
    }


# ========== E2E和专项测试配置 [CHECK:TEST-001] [CHECK:TEST-004] ==========

# E2E测试数据库配置（专用MySQL实例）- 使用独立数据库名
E2E_TEST_DATABASE_URL = (
    "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"
)


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
        echo=False,  # E2E测试不需要SQL日志
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
        echo=False,  # 性能测试关闭SQL日志以减少开销
    )

    # 为性能测试优化SQLite配置
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_performance_sqlite_pragma(dbapi_connection, connection_record):
        """性能测试专用SQLite优化配置"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=MEMORY")  # 最快的日志模式
        cursor.execute("PRAGMA synchronous=OFF")  # 关闭同步以提升性能
        cursor.execute("PRAGMA cache_size=10000")  # 增大缓存
        cursor.execute("PRAGMA temp_store=MEMORY")  # 临时表存储在内存中
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
        "rate_limiter": mocker.Mock(),
        "auth_validator": mocker.Mock(),
        "input_sanitizer": mocker.Mock(),
        "csrf_protection": mocker.Mock(),
    }

    # 设置安全测试的默认行为
    security_mocks["rate_limiter"].is_allowed.return_value = True
    security_mocks["auth_validator"].validate_token.return_value = True
    security_mocks["input_sanitizer"].sanitize.side_effect = lambda x: x
    security_mocks["csrf_protection"].verify.return_value = True

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
