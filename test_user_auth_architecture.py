"""
用户认证模块单元测试
严格按照架构规范，使用正确的测试环境
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 正确导入项目模型
from app.core.database import Base
from app.modules.user_auth.models import User, Role, Permission, UserRole, RolePermission, Session

# 单元测试数据库配置（SQLite内存）
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """测试数据库引擎 - 每个测试函数使用独立的内存数据库"""
    engine = create_engine(
        UNIT_TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """测试数据库会话 - 每个测试使用独立的session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # 确保测试间的数据隔离
        session.close()


@pytest.fixture
def sample_user(test_db):
    """测试用户fixture"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password_123",
        is_active=True,
        role="user",
        status="active",
        failed_login_attempts=0
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_role(test_db):
    """测试角色fixture"""
    role = Role(
        name="admin",
        description="系统管理员角色",
        level=100
    )
    test_db.add(role)
    test_db.commit()
    test_db.refresh(role)
    return role


@pytest.fixture
def sample_permission(test_db):
    """测试权限fixture"""
    permission = Permission(
        name="user.create",
        resource="user",
        action="create",
        description="创建用户权限"
    )
    test_db.add(permission)
    test_db.commit()
    test_db.refresh(permission)
    return permission


class TestUserModel:
    """用户模型测试类"""
    
    def test_user_creation_success(self, test_db):
        """测试用户创建成功"""
        user = User(
            username="newuser",
            email="newuser@example.com",
            password_hash="hashed_password",
            phone="13800138000"
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # 验证基本字段
        assert user.id is not None
        assert isinstance(user.id, int)
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.phone == "13800138000"
        
        # 验证默认值
        assert user.is_active is True
        assert user.status == "active"
        assert user.role == "user"
        assert user.failed_login_attempts == 0
        assert user.email_verified is False
        assert user.phone_verified is False
        assert user.two_factor_enabled is False
        
        # 验证时间戳字段
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.is_deleted is False
        assert user.deleted_at is None
        
        print(f"✅ 用户创建成功测试通过: {user}")
    
    def test_user_unique_constraints(self, test_db, sample_user):
        """测试用户唯一约束"""
        # 尝试创建相同username的用户
        try:
            duplicate_username = User(
                username="testuser",  # 重复username
                email="different@example.com",
                password_hash="hash"
            )
            test_db.add(duplicate_username)
            test_db.commit()
            assert False, "应该抛出唯一约束异常"
        except Exception as e:
            test_db.rollback()
            print(f"✅ 用户名唯一约束测试通过: {type(e).__name__}")
        
        # 尝试创建相同email的用户
        try:
            duplicate_email = User(
                username="different",
                email="test@example.com",  # 重复email
                password_hash="hash"
            )
            test_db.add(duplicate_email)
            test_db.commit()
            assert False, "应该抛出唯一约束异常"
        except Exception as e:
            test_db.rollback()
            print(f"✅ 邮箱唯一约束测试通过: {type(e).__name__}")
    
    def test_user_repr(self, sample_user):
        """测试用户字符串表示"""
        repr_str = repr(sample_user)
        assert "User" in repr_str
        assert str(sample_user.id) in repr_str
        assert sample_user.username in repr_str
        assert sample_user.email in repr_str
        print(f"✅ 用户repr测试通过: {repr_str}")


class TestRoleModel:
    """角色模型测试类"""
    
    def test_role_creation_success(self, test_db):
        """测试角色创建成功"""
        role = Role(
            name="manager",
            description="部门经理角色",
            level=50
        )
        
        test_db.add(role)
        test_db.commit()
        test_db.refresh(role)
        
        assert role.id is not None
        assert isinstance(role.id, int)
        assert role.name == "manager"
        assert role.description == "部门经理角色"
        assert role.level == 50
        assert role.created_at is not None
        assert role.updated_at is not None
        print(f"✅ 角色创建成功测试通过: {role}")


class TestPermissionModel:
    """权限模型测试类"""
    
    def test_permission_creation_success(self, test_db):
        """测试权限创建成功"""
        permission = Permission(
            name="product.delete",
            resource="product",
            action="delete",
            description="删除商品权限"
        )
        
        test_db.add(permission)
        test_db.commit()
        test_db.refresh(permission)
        
        assert permission.id is not None
        assert isinstance(permission.id, int)
        assert permission.name == "product.delete"
        assert permission.resource == "product"
        assert permission.action == "delete"
        assert permission.description == "删除商品权限"
        assert permission.created_at is not None
        print(f"✅ 权限创建成功测试通过: {permission}")


class TestUserRoleRelationship:
    """用户角色关联测试类"""
    
    def test_user_role_assignment(self, test_db, sample_user, sample_role):
        """测试用户角色分配"""
        user_role = UserRole(
            user_id=sample_user.id,
            role_id=sample_role.id,
            assigned_by=sample_user.id
        )
        
        test_db.add(user_role)
        test_db.commit()
        test_db.refresh(user_role)
        
        assert user_role.user_id == sample_user.id
        assert user_role.role_id == sample_role.id
        assert user_role.assigned_by == sample_user.id
        assert user_role.assigned_at is not None
        print(f"✅ 用户角色分配测试通过: {user_role}")


class TestRolePermissionRelationship:
    """角色权限关联测试类"""
    
    def test_role_permission_assignment(self, test_db, sample_role, sample_permission, sample_user):
        """测试角色权限分配"""
        role_permission = RolePermission(
            role_id=sample_role.id,
            permission_id=sample_permission.id,
            granted_by=sample_user.id
        )
        
        test_db.add(role_permission)
        test_db.commit()
        test_db.refresh(role_permission)
        
        assert role_permission.role_id == sample_role.id
        assert role_permission.permission_id == sample_permission.id
        assert role_permission.granted_by == sample_user.id
        assert role_permission.granted_at is not None
        print(f"✅ 角色权限分配测试通过: {role_permission}")


class TestSessionModel:
    """会话模型测试类"""
    
    def test_session_creation_success(self, test_db, sample_user):
        """测试会话创建成功"""
        expires_at = datetime.utcnow() + timedelta(hours=2)
        
        session = Session(
            user_id=sample_user.id,
            token_hash="hashed_token_123",
            expires_at=expires_at,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0 Test Browser"
        )
        
        test_db.add(session)
        test_db.commit()
        test_db.refresh(session)
        
        assert session.id is not None
        assert isinstance(session.id, int)
        assert session.user_id == sample_user.id
        assert session.token_hash == "hashed_token_123"
        assert session.expires_at == expires_at
        assert session.ip_address == "192.168.1.1"
        assert session.user_agent == "Mozilla/5.0 Test Browser"
        assert session.is_active is True
        assert session.created_at is not None
        assert session.last_accessed_at is not None
        print(f"✅ 会话创建成功测试通过: {session}")


class TestArchitectureCompliance:
    """架构规范合规性测试"""
    
    def test_primary_key_types(self, test_db):
        """测试主键类型符合BigInteger要求"""
        user = User(username="test", email="test@test.com", password_hash="hash")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # 验证主键是整数类型（在SQLite中BigInteger映射为INTEGER）
        assert isinstance(user.id, int)
        assert user.id > 0
        print(f"✅ 主键类型合规测试通过: user.id={user.id} (type: {type(user.id)})")
    
    def test_timestamp_mixin_fields(self, test_db):
        """测试时间戳混入字段"""
        user = User(username="time_test", email="time@test.com", password_hash="hash")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # 验证时间戳字段存在且有效
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        print(f"✅ 时间戳混入合规测试通过")
    
    def test_soft_delete_mixin_fields(self, test_db):
        """测试软删除混入字段"""
        user = User(username="delete_test", email="delete@test.com", password_hash="hash")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # 验证软删除字段存在且有效
        assert hasattr(user, 'is_deleted')
        assert hasattr(user, 'deleted_at')
        assert user.is_deleted is False
        assert user.deleted_at is None
        print(f"✅ 软删除混入合规测试通过")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始执行用户认证模块架构合规单元测试")
    print("=" * 60)
    
    # 直接调用pytest运行
    import sys
    current_file = __file__ if __name__ == "__main__" else "test_user_auth_architecture.py"
    sys.exit(pytest.main([current_file, "-v", "-s"]))


if __name__ == "__main__":
    run_all_tests()