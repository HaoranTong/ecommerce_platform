"""
性能测试专用配置模块
用于避免修改全局conftest.py，专门为性能测试提供优化配置
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db


@pytest.fixture(scope="session")
def performance_mysql_engine():
    """性能测试专用MySQL引擎，优化连接池配置"""
    INTEGRATION_TEST_DATABASE_URL = (
        "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"
    )
    
    # 性能测试专用的连接池配置
    engine = create_engine(
        INTEGRATION_TEST_DATABASE_URL,
        pool_size=50,          # 增大连接池到50个连接
        max_overflow=100,      # 允许额外100个溢出连接  
        pool_timeout=60,       # 连接超时60秒
        pool_recycle=3600,     # 连接回收时间1小时
        pool_pre_ping=True,    # 连接前ping检查可用性
        echo=False             # 关闭SQL日志以提升性能
    )
    
    # 导入并创建所有模型表
    from app.core.database import Base
    from app.modules.user_auth.models import User, Role, Permission
    
    Base.metadata.create_all(bind=engine)
    print("✅ 性能测试专用MySQL数据库已准备完成")
    yield engine
    
    # 清理但不删除表结构
    engine.dispose()


@pytest.fixture(scope="function")
def performance_mysql_db(performance_mysql_engine):
    """性能测试专用数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=performance_mysql_engine
    )
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.rollback()
        database.close()


@pytest.fixture(scope="function")  
async def performance_async_client(performance_mysql_engine):
    """性能测试专用异步客户端，避免影响全局配置"""
    
    # 创建会话工厂以支持并发请求
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=performance_mysql_engine
    )
    
    def override_get_db():
        """为Every API request提供独立的数据库会话，但共享同一个引擎"""
        # 每个请求都获得一个新的会话，但共享数据库引擎，确保数据一致性
        database = TestingSessionLocal()
        try:
            yield database
        finally:
            database.close()

    # 清除现有依赖覆盖，只覆盖数据库连接
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(app=app, base_url="http://testserver") as async_client:
            # 为异步客户端添加认证帮助方法
            async def authenticate_as_admin():
                """创建管理员用户并返回JWT token"""
                import uuid
                from datetime import datetime, timedelta
                from app.core.auth import create_access_token
                from app.modules.user_auth.models import User
                
                # 创建唯一的测试管理员用户
                unique_id = str(uuid.uuid4())[:8]
                admin_user = User(
                    username=f"perf_admin_{unique_id}",
                    email=f"perf_admin_{unique_id}@test.com", 
                    password_hash="$2b$12$dummy_hash_for_testing",
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # 使用临时会话创建用户
                temp_session = TestingSessionLocal()
                try:
                    temp_session.add(admin_user)
                    temp_session.commit()
                    temp_session.refresh(admin_user)
                finally:
                    temp_session.close()
                
                # 创建JWT token
                access_token = create_access_token(
                    data={"sub": admin_user.username, "user_id": admin_user.id},
                    expires_delta=timedelta(hours=1)
                )
                
                return access_token, admin_user

            # 添加认证方法到客户端
            async_client.authenticate_as_admin = authenticate_as_admin
            yield async_client
    finally:
        app.dependency_overrides.clear()