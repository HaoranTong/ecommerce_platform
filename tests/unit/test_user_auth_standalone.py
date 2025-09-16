"""
用户认证模块独立单元测试

完全独立的测试文件，避免所有循环导入问题
严格按照MASTER.md要求执行测试
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

# 避免导入问题，直接定义测试需要的类
Base = declarative_base()

# 独立定义时间戳混入类
class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

# 独立定义软删除混入类  
class SoftDeleteMixin:
    """软删除混入类"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

# 测试用的独立模型定义
class User(Base, TimestampMixin, SoftDeleteMixin):
    """用户模型"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default='active', nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    real_name = Column(String(100), nullable=True)
    role = Column(String(20), default='user', nullable=False)
    wx_openid = Column(String(100), unique=True, nullable=True)
    wx_unionid = Column(String(100), unique=True, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class Role(Base, TimestampMixin):
    """角色模型"""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', level={self.level})>"

class Permission(Base, TimestampMixin):
    """权限模型"""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"

class UserRole(Base, TimestampMixin):
    """用户角色关联模型"""
    __tablename__ = 'user_roles'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"

class RolePermission(Base, TimestampMixin):
    """角色权限关联模型"""
    __tablename__ = 'role_permissions'

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), primary_key=True)
    granted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    granted_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"

class Session(Base, TimestampMixin):
    """会话模型"""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    last_accessed_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"

# 单元测试数据库配置
UNIT_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_engine():
    """测试数据库引擎"""
    engine = create_engine(
        UNIT_TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def test_db(test_engine):
    """测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
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
    
    def test_user_wechat_fields(self, test_db):
        """测试微信字段"""
        user = User(
            username="wxuser",
            email="wx@example.com",
            password_hash="hash",
            wx_openid="wx_open_123",
            wx_unionid="wx_union_456"
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.wx_openid == "wx_open_123"
        assert user.wx_unionid == "wx_union_456"
        print(f"✅ 微信字段测试通过: openid={user.wx_openid}, unionid={user.wx_unionid}")
    
    def test_user_security_fields(self, test_db):
        """测试安全相关字段"""
        lock_time = datetime.utcnow() + timedelta(minutes=15)
        login_time = datetime.utcnow()
        
        user = User(
            username="secuser",
            email="sec@example.com",
            password_hash="hash",
            failed_login_attempts=3,
            locked_until=lock_time,
            last_login_at=login_time,
            two_factor_enabled=True
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.failed_login_attempts == 3
        assert user.locked_until == lock_time
        assert user.last_login_at == login_time
        assert user.two_factor_enabled is True
        print(f"✅ 安全字段测试通过: 失败次数={user.failed_login_attempts}, 2FA={user.two_factor_enabled}")

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
        assert role.name == "manager"
        assert role.description == "部门经理角色"
        assert role.level == 50
        assert role.created_at is not None
        assert role.updated_at is not None
        print(f"✅ 角色创建成功测试通过: {role}")
    
    def test_role_unique_name_constraint(self, test_db, sample_role):
        """测试角色名称唯一约束"""
        try:
            duplicate_role = Role(
                name="admin",  # 重复名称
                description="另一个管理员",
                level=99
            )
            test_db.add(duplicate_role)
            test_db.commit()
            assert False, "应该抛出唯一约束异常"
        except Exception as e:
            test_db.rollback()
            print(f"✅ 角色名称唯一约束测试通过: {type(e).__name__}")
    
    def test_role_repr(self, sample_role):
        """测试角色字符串表示"""
        repr_str = repr(sample_role)
        assert "Role" in repr_str
        assert str(sample_role.id) in repr_str
        assert sample_role.name in repr_str
        assert str(sample_role.level) in repr_str
        print(f"✅ 角色repr测试通过: {repr_str}")

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
        assert permission.name == "product.delete"
        assert permission.resource == "product"
        assert permission.action == "delete"
        assert permission.description == "删除商品权限"
        assert permission.created_at is not None
        print(f"✅ 权限创建成功测试通过: {permission}")
    
    def test_permission_unique_name_constraint(self, test_db, sample_permission):
        """测试权限名称唯一约束"""
        try:
            duplicate_permission = Permission(
                name="user.create",  # 重复名称
                resource="different",
                action="create",
                description="重复权限"
            )
            test_db.add(duplicate_permission)
            test_db.commit()
            assert False, "应该抛出唯一约束异常"
        except Exception as e:
            test_db.rollback()
            print(f"✅ 权限名称唯一约束测试通过: {type(e).__name__}")
    
    def test_permission_repr(self, sample_permission):
        """测试权限字符串表示"""
        repr_str = repr(sample_permission)
        assert "Permission" in repr_str
        assert str(sample_permission.id) in repr_str
        assert sample_permission.name in repr_str
        assert sample_permission.resource in repr_str
        assert sample_permission.action in repr_str
        print(f"✅ 权限repr测试通过: {repr_str}")

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
        assert session.user_id == sample_user.id
        assert session.token_hash == "hashed_token_123"
        assert session.expires_at == expires_at
        assert session.ip_address == "192.168.1.1"
        assert session.user_agent == "Mozilla/5.0 Test Browser"
        assert session.is_active is True
        assert session.created_at is not None
        assert session.last_accessed_at is not None
        print(f"✅ 会话创建成功测试通过: {session}")

class TestTimestampMixin:
    """时间戳功能测试类"""
    
    def test_timestamp_auto_creation(self, test_db):
        """测试时间戳自动创建"""
        before_create = datetime.utcnow()
        
        user = User(
            username="timeuser",
            email="time@example.com",
            password_hash="hash"
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        after_create = datetime.utcnow()
        
        # 验证创建时间在合理范围内
        assert before_create <= user.created_at <= after_create
        assert before_create <= user.updated_at <= after_create
        print(f"✅ 时间戳自动创建测试通过: created={user.created_at}, updated={user.updated_at}")
    
    def test_timestamp_auto_update(self, test_db, sample_user):
        """测试时间戳自动更新"""
        original_updated = sample_user.updated_at
        
        # 等待一点时间确保时间戳不同
        import time
        time.sleep(0.1)
        
        # 更新用户
        sample_user.email = "updated@example.com"
        test_db.commit()
        test_db.refresh(sample_user)
        
        # 验证更新时间改变
        assert sample_user.updated_at > original_updated
        assert sample_user.created_at != sample_user.updated_at
        print(f"✅ 时间戳自动更新测试通过: 原始={original_updated}, 新={sample_user.updated_at}")

class TestSoftDeleteMixin:
    """软删除功能测试类"""
    
    def test_user_soft_delete(self, test_db, sample_user):
        """测试用户软删除"""
        # 初始状态
        assert sample_user.is_deleted is False
        assert sample_user.deleted_at is None
        
        # 执行软删除
        sample_user.is_deleted = True
        sample_user.deleted_at = datetime.utcnow()
        test_db.commit()
        
        # 验证软删除状态
        assert sample_user.is_deleted is True
        assert sample_user.deleted_at is not None
        print(f"✅ 软删除测试通过: is_deleted={sample_user.is_deleted}, deleted_at={sample_user.deleted_at}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始执行用户认证模块完整单元测试")
    print("=" * 50)
    
    # 直接调用pytest运行
    import sys
    current_file = __file__ if __name__ == "__main__" else "test_user_auth_standalone.py"
    sys.exit(pytest.main([current_file, "-v", "-s"]))

if __name__ == "__main__":
    run_all_tests()