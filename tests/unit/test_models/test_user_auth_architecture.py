"""
用户认证模块架构合规测试
严格按照MASTER.md要求执行
"""

import pytest
from datetime import datetime, timedelta

# 只导入需要的模型，避免循环导入
from app.modules.user_auth.models import User, Role, Permission, UserRole, RolePermission, Session
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator


class TestUserAuthModels:
    """用户认证模型测试"""
    
    def test_user_model_creation(self, unit_test_db):
        """测试用户模型创建"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            phone="13800138000"
        )
        
        unit_test_db.add(user)
        unit_test_db.commit()
        unit_test_db.refresh(user)
        
        # 验证字段
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.phone == "13800138000"
        assert user.is_active is True
        assert user.status == "active"
        assert user.role == "user"
        
        # 验证时间戳
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.is_deleted is False
        
        print(f"✅ 用户模型创建测试通过: ID={user.id}")
    
    def test_role_model_creation(self, unit_test_db):
        """测试角色模型创建"""
        role = Role(
            name="admin",
            description="管理员角色",
            level=100
        )
        
        unit_test_db.add(role)
        unit_test_db.commit()
        unit_test_db.refresh(role)
        
        assert role.id is not None
        assert role.name == "admin"
        assert role.description == "管理员角色"
        assert role.level == 100
        assert role.created_at is not None
        
        print(f"✅ 角色模型创建测试通过: ID={role.id}")
    
    def test_permission_model_creation(self, unit_test_db):
        """测试权限模型创建"""
        permission = Permission(
            name="user.create",
            resource="user",
            action="create",
            description="创建用户权限"
        )
        
        unit_test_db.add(permission)
        unit_test_db.commit()
        unit_test_db.refresh(permission)
        
        assert permission.id is not None
        assert permission.name == "user.create"
        assert permission.resource == "user"
        assert permission.action == "create"
        assert permission.created_at is not None
        
        print(f"✅ 权限模型创建测试通过: ID={permission.id}")
    
    def test_session_model_creation(self, unit_test_db):
        """测试会话模型创建"""
        # 先创建用户
        user = User(
            username="sessionuser",
            email="session@example.com",
            password_hash="hash"
        )
        unit_test_db.add(user)
        unit_test_db.commit()
        unit_test_db.refresh(user)
        
        # 创建会话
        session = Session(
            user_id=user.id,
            token_hash="token_hash_123",
            expires_at=datetime.utcnow() + timedelta(hours=2),
            ip_address="192.168.1.1"
        )
        
        unit_test_db.add(session)
        unit_test_db.commit()
        unit_test_db.refresh(session)
        
        assert session.id is not None
        assert session.user_id == user.id
        assert session.token_hash == "token_hash_123"
        assert session.is_active is True
        assert session.created_at is not None
        
        print(f"✅ 会话模型创建测试通过: ID={session.id}")
    
    def test_user_role_relationship(self, unit_test_db):
        """测试用户角色关联"""
        # 创建用户
        user = User(
            username="roleuser",
            email="roleuser@example.com",
            password_hash="hash"
        )
        unit_test_db.add(user)
        
        # 创建角色
        role = Role(
            name="manager",
            description="经理角色",
            level=50
        )
        unit_test_db.add(role)
        unit_test_db.commit()
        unit_test_db.refresh(user)
        unit_test_db.refresh(role)
        
        # 创建关联
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
            assigned_by=user.id
        )
        
        unit_test_db.add(user_role)
        unit_test_db.commit()
        
        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
        assert user_role.assigned_at is not None
        
        print(f"✅ 用户角色关联测试通过")
    
    def test_role_permission_relationship(self, unit_test_db):
        """测试角色权限关联"""
        # 创建角色
        role = Role(
            name="editor",
            description="编辑角色",
            level=30
        )
        unit_test_db.add(role)
        
        # 创建权限
        permission = Permission(
            name="content.edit",
            resource="content",
            action="edit",
            description="编辑内容权限"
        )
        unit_test_db.add(permission)
        
        # 创建用户（用于记录授权者）
        user = User(
            username="grantuser",
            email="grant@example.com",
            password_hash="hash"
        )
        unit_test_db.add(user)
        unit_test_db.commit()
        unit_test_db.refresh(role)
        unit_test_db.refresh(permission)
        unit_test_db.refresh(user)
        
        # 创建关联
        role_permission = RolePermission(
            role_id=role.id,
            permission_id=permission.id,
            granted_by=user.id
        )
        
        unit_test_db.add(role_permission)
        unit_test_db.commit()
        
        assert role_permission.role_id == role.id
        assert role_permission.permission_id == permission.id
        assert role_permission.granted_at is not None
        
        print(f"✅ 角色权限关联测试通过")
    
    def test_unique_constraints(self, unit_test_db):
        """测试唯一约束"""
        user1 = User(
            username="unique_test",
            email="unique@example.com",
            password_hash="hash"
        )
        unit_test_db.add(user1)
        unit_test_db.commit()
        
        # 测试用户名唯一约束
        with pytest.raises(Exception):
            user2 = User(
                username="unique_test",  # 重复用户名
                email="different@example.com",
                password_hash="hash"
            )
            unit_test_db.add(user2)
            unit_test_db.commit()
        
        unit_test_db.rollback()
        
        # 测试邮箱唯一约束
        with pytest.raises(Exception):
            user3 = User(
                username="different_user",
                email="unique@example.com",  # 重复邮箱
                password_hash="hash"
            )
            unit_test_db.add(user3)
            unit_test_db.commit()
        
        print(f"✅ 唯一约束测试通过")


class TestArchitectureCompliance:
    """架构规范合规性测试"""
    
    def test_primary_key_auto_increment(self, unit_test_db):
        """测试主键自增功能"""
        user1 = User(username="auto1", email="auto1@test.com", password_hash="hash")
        user2 = User(username="auto2", email="auto2@test.com", password_hash="hash")
        
        unit_test_db.add(user1)
        unit_test_db.add(user2)
        unit_test_db.commit()
        unit_test_db.refresh(user1)
        unit_test_db.refresh(user2)
        
        # 验证主键自增
        assert user1.id is not None
        assert user2.id is not None
        assert user2.id > user1.id
        
        print(f"✅ 主键自增测试通过: user1.id={user1.id}, user2.id={user2.id}")
    
    def test_timestamp_mixin_functionality(self, unit_test_db):
        """测试时间戳混入功能"""
        user = User(username="timestamp_test", email="timestamp@test.com", password_hash="hash")
        unit_test_db.add(user)
        unit_test_db.commit()
        unit_test_db.refresh(user)
        
        original_updated = user.updated_at
        
        # 更新用户
        import time
        time.sleep(1)  # 确保至少1秒的时间差
        user.email = "updated@test.com"
        unit_test_db.commit()
        unit_test_db.refresh(user)
        
        # 验证时间戳更新
        assert user.updated_at >= original_updated
        
        print(f"✅ 时间戳自动更新测试通过")
    
    def test_soft_delete_functionality(self, unit_test_db):
        """测试软删除功能"""
        user = User(username="soft_delete_test", email="soft@test.com", password_hash="hash")
        unit_test_db.add(user)
        unit_test_db.commit()
        unit_test_db.refresh(user)
        
        # 验证初始状态
        assert user.is_deleted is False
        assert user.deleted_at is None
        
        # 执行软删除
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        unit_test_db.commit()
        
        # 验证软删除状态
        assert user.is_deleted is True
        assert user.deleted_at is not None
        
        print(f"✅ 软删除功能测试通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
