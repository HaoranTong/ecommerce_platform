"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/unit/test_repositories/test_user_auth_repositories.py
生成时间: 2025-10-08 08:00:23
生成工具: tools/generate_test_template.py v2.0
状态: GENERATED - 需要经过代码审查和测试验证

说明: 此文件已生成到正式目录，请进行代码审查和测试验证。
     审查通过后即可直接用于项目测试。
     
流程: 生成 -> 审查 -> 验证 -> 提交版本控制
"""


import pytest
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from decimal import Decimal

# 导入测试基础设施
from tests.conftest import unit_test_db

# 导入Repository类
from app.modules.user_auth.repository import (
    UserRepository, RoleRepository, PermissionRepository, UserRoleRepository, RolePermissionRepository, SessionRepository
)

# 导入模型类
from app.modules.user_auth.models import (
    Permission, Role, RolePermission, Session, User, UserRole
)


@pytest.mark.unit
@pytest.mark.repositories
class TestUserRepository:
    """
    UserRepository 数据访问层测试
    
    测试范围:
    - 14 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库，无Mock依赖
    """
    
    def setup_method(self):
        """测试准备 - 每个测试方法执行前调用"""
        pass
        
    def teardown_method(self):
        """测试清理 - 每个测试方法执行后调用"""
        pass
        
    def test_create_success(self, unit_test_db: Session):
        """测试create - 成功创建"""
        # 准备测试数据（包括外键依赖）
        entity = User(username="测试数据", email="test_测试数据@example.com", password_hash="测试数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        
        # 执行Repository方法
        result = UserRepository.create(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(User).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction(self, unit_test_db: Session):
        """测试create - 事务提交"""
        entity = User(username="事务测试", email="test_事务测试@example.com", password_hash="事务测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        
        result = UserRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（可以在新会话中查询到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=result.id).first()
        assert db_entity is not None

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备依赖实体
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_id(unit_test_db, user.id)
        
        # 验证结果
        assert result is not None

    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = UserRepository.get_by_id(unit_test_db, 99999)
        
        # 验证结果
        assert result is None

    def test_get_by_username_found(self, unit_test_db: Session):
        """测试get_by_username - 查询到数据"""
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_username(unit_test_db, entity.username)
        
        # 验证结果
        assert result is not None
        assert result.username == entity.username
    
    def test_get_by_username_not_found(self, unit_test_db: Session):
        """测试get_by_username - 数据不存在"""
        result = UserRepository.get_by_username(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_email_found(self, unit_test_db: Session):
        """测试get_by_email - 查询到数据"""
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_email(unit_test_db, entity.email)
        
        # 验证结果
        assert result is not None
        assert result.email == entity.email
    
    def test_get_by_email_not_found(self, unit_test_db: Session):
        """测试get_by_email - 数据不存在"""
        result = UserRepository.get_by_email(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_username_or_email_found(self, unit_test_db: Session):
        """测试get_by_username_or_email - 查询到数据"""
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_username_or_email(unit_test_db, entity.username)
        
        # 验证结果
        assert result is not None
        assert result.username == entity.username
    
    def test_get_by_username_or_email_not_found(self, unit_test_db: Session):
        """测试get_by_username_or_email - 数据不存在"""
        result = UserRepository.get_by_username_or_email(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_wx_openid_found(self, unit_test_db: Session):
        """测试get_by_wx_openid - 查询到数据"""
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_wx_openid(unit_test_db, entity.wx_openid)
        
        # 验证结果
        assert result is not None
        assert result.wx_openid == entity.wx_openid
    
    def test_get_by_wx_openid_not_found(self, unit_test_db: Session):
        """测试get_by_wx_openid - 数据不存在"""
        result = UserRepository.get_by_wx_openid(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_check_exists_found(self, unit_test_db: Session):
        """测试check_exists - 查询到数据"""
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.check_exists(unit_test_db, username=entity.username, email=entity.email)
        
        # 验证结果
        assert result is True
    
    def test_check_exists_not_found(self, unit_test_db: Session):
        """测试check_exists - 数据不存在"""
        result = UserRepository.check_exists(unit_test_db, username="nonexistent", email="nonexistent@test.com")
        
        assert result is False

    def test_list_found(self, unit_test_db: Session):
        """测试list - 查询到数据"""
        # 准备测试数据
        entity = User(username="查询测试", email="test_查询测试@example.com", password_hash="查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.list(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_list_not_found(self, unit_test_db: Session):
        """测试list - 数据不存在"""
        result = UserRepository.list(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_count_count(self, unit_test_db: Session):
        """测试count - 计数功能"""
        # 准备测试数据
        entity0 = User(username="测试数据0", email="test_测试数据0@example.com", password_hash="测试数据0", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity0)
        entity1 = User(username="测试数据1", email="test_测试数据1@example.com", password_hash="测试数据1", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity1)
        entity2 = User(username="测试数据2", email="test_测试数据2@example.com", password_hash="测试数据2", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity2)
        entity3 = User(username="测试数据3", email="test_测试数据3@example.com", password_hash="测试数据3", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity3)
        entity4 = User(username="测试数据4", email="test_测试数据4@example.com", password_hash="测试数据4", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity4)
        unit_test_db.commit()
        
        # 执行Repository方法
        count = UserRepository.count(unit_test_db)
        
        # 验证计数
        assert isinstance(count, int)
        assert count >= 0

    def test_update_success(self, unit_test_db: Session):
        """测试update - 更新成功"""
        # 准备测试数据
        entity = User(username="原始数据", email="test_原始数据@example.com", password_hash="原始数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        update_data = {"real_name": "更新后数据"}
        result = UserRepository.update(unit_test_db, entity, update_data)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert result.real_name == "更新后数据"
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=entity.id).first()
        assert db_entity.real_name == "更新后数据"

    # TODO: 测试专用更新方法 update_login_info
    # 这是一个专用更新方法，只修改特定字段，需要根据业务逻辑手动编写测试
    # 方法签名: [('db', 'Session'), ('user', 'User'), ('ip_address', 'Optional[str]')]
    # 返回类型: User
    

    # TODO: 测试专用更新方法 increment_failed_login
    # 这是一个专用更新方法，只修改特定字段，需要根据业务逻辑手动编写测试
    # 方法签名: [('db', 'Session'), ('user', 'User')]
    # 返回类型: User
    

    def test_soft_delete_success(self, unit_test_db: Session):
        """测试soft_delete - 删除成功"""
        # 准备测试数据
        entity = User(username="待删除数据", email="test_待删除数据@example.com", password_hash="待删除数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        UserRepository.soft_delete(unit_test_db, entity)
        
        # 验证软删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=entity_id).first()
        assert db_entity is not None  # 记录仍存在
        # 验证软删除标记（根据模型字段选择）
        if hasattr(db_entity, 'is_deleted'):
            assert db_entity.is_deleted == True
        if hasattr(db_entity, 'is_active'):
            assert db_entity.is_active == False

    def test_hard_delete_success(self, unit_test_db: Session):
        """测试hard_delete - 删除成功"""
        # 准备测试数据
        entity = User(username="待删除数据", email="test_待删除数据@example.com", password_hash="待删除数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        UserRepository.hard_delete(unit_test_db, entity)
        
        # 验证硬删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=entity_id).first()
        assert db_entity is None  # 记录已物理删除




@pytest.mark.unit
@pytest.mark.repositories
class TestRoleRepository:
    """
    RoleRepository 数据访问层测试
    
    测试范围:
    - 7 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库，无Mock依赖
    """
    
    def setup_method(self):
        """测试准备 - 每个测试方法执行前调用"""
        pass
        
    def teardown_method(self):
        """测试清理 - 每个测试方法执行后调用"""
        pass
        
    def test_create_success(self, unit_test_db: Session):
        """测试create - 成功创建"""
        # 准备测试数据（包括外键依赖）
        entity = Role(name="测试数据", level=1)
        
        # 执行Repository方法
        result = RoleRepository.create(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(Role).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction(self, unit_test_db: Session):
        """测试create - 事务提交"""
        entity = Role(name="事务测试", level=1)
        
        result = RoleRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（可以在新会话中查询到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=result.id).first()
        assert db_entity is not None

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备依赖实体
        role = Role(name="Role数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = Role(name="查询测试", level=1)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RoleRepository.get_by_id(unit_test_db, role.id)
        
        # 验证结果
        assert result is not None

    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = RoleRepository.get_by_id(unit_test_db, 99999)
        
        # 验证结果
        assert result is None

    def test_get_by_name_found(self, unit_test_db: Session):
        """测试get_by_name - 查询到数据"""
        # 准备测试数据
        entity = Role(name="查询测试", level=1)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RoleRepository.get_by_name(unit_test_db, entity.name)
        
        # 验证结果
        assert result is not None
        assert result.name == entity.name
    
    def test_get_by_name_not_found(self, unit_test_db: Session):
        """测试get_by_name - 数据不存在"""
        result = RoleRepository.get_by_name(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_list_found(self, unit_test_db: Session):
        """测试list - 查询到数据"""
        # 准备测试数据
        entity = Role(name="查询测试", level=1)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RoleRepository.list(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_list_not_found(self, unit_test_db: Session):
        """测试list - 数据不存在"""
        result = RoleRepository.list(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_update_success(self, unit_test_db: Session):
        """测试update - 更新成功"""
        # 准备测试数据
        entity = Role(name="原始数据", level=1)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        update_data = {"name": "更新后数据"}
        result = RoleRepository.update(unit_test_db, entity, update_data)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert result.name == "更新后数据"
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据"

    def test_delete_success(self, unit_test_db: Session):
        """测试delete - 删除成功"""
        # 准备测试数据
        entity = Role(name="待删除数据", level=1)
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        RoleRepository.delete(unit_test_db, entity)
        
        # 验证硬删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=entity_id).first()
        assert db_entity is None  # 记录已物理删除

    def test_get_user_count_count(self, unit_test_db: Session):
        """测试get_user_count - 计数功能"""
        # 准备测试数据
        entity0 = Role(name="测试数据0", level=1)
        unit_test_db.add(entity0)
        entity1 = Role(name="测试数据1", level=1)
        unit_test_db.add(entity1)
        entity2 = Role(name="测试数据2", level=1)
        unit_test_db.add(entity2)
        entity3 = Role(name="测试数据3", level=1)
        unit_test_db.add(entity3)
        entity4 = Role(name="测试数据4", level=1)
        unit_test_db.add(entity4)
        unit_test_db.commit()
        
        # 执行Repository方法
        count = RoleRepository.get_user_count(unit_test_db, entity0.id)
        
        # 验证计数
        assert isinstance(count, int)
        assert count >= 0




@pytest.mark.unit
@pytest.mark.repositories
class TestPermissionRepository:
    """
    PermissionRepository 数据访问层测试
    
    测试范围:
    - 6 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库，无Mock依赖
    """
    
    def setup_method(self):
        """测试准备 - 每个测试方法执行前调用"""
        pass
        
    def teardown_method(self):
        """测试清理 - 每个测试方法执行后调用"""
        pass
        
    def test_create_success(self, unit_test_db: Session):
        """测试create - 成功创建"""
        # 准备测试数据（包括外键依赖）
        entity = Permission(name="测试数据", resource="测试数据", action="测试数据")
        
        # 执行Repository方法
        result = PermissionRepository.create(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(Permission).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction(self, unit_test_db: Session):
        """测试create - 事务提交"""
        entity = Permission(name="事务测试", resource="事务测试", action="事务测试")
        
        result = PermissionRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（可以在新会话中查询到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=result.id).first()
        assert db_entity is not None

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备依赖实体
        permission = Permission(name="Permission数据", resource="Permission数据", action="Permission数据")
        unit_test_db.add(permission)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = Permission(name="查询测试", resource="查询测试", action="查询测试")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = PermissionRepository.get_by_id(unit_test_db, permission.id)
        
        # 验证结果
        assert result is not None

    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = PermissionRepository.get_by_id(unit_test_db, 99999)
        
        # 验证结果
        assert result is None

    def test_get_by_name_found(self, unit_test_db: Session):
        """测试get_by_name - 查询到数据"""
        # 准备测试数据
        entity = Permission(name="查询测试", resource="查询测试", action="查询测试")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = PermissionRepository.get_by_name(unit_test_db, entity.name)
        
        # 验证结果
        assert result is not None
        assert result.name == entity.name
    
    def test_get_by_name_not_found(self, unit_test_db: Session):
        """测试get_by_name - 数据不存在"""
        result = PermissionRepository.get_by_name(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_list_found(self, unit_test_db: Session):
        """测试list - 查询到数据"""
        # 准备测试数据
        entity = Permission(name="查询测试", resource="查询测试", action="查询测试")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = PermissionRepository.list(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_list_not_found(self, unit_test_db: Session):
        """测试list - 数据不存在"""
        result = PermissionRepository.list(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_update_success(self, unit_test_db: Session):
        """测试update - 更新成功"""
        # 准备测试数据
        entity = Permission(name="原始数据", resource="原始数据", action="原始数据")
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        update_data = {"name": "更新后数据"}
        result = PermissionRepository.update(unit_test_db, entity, update_data)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert result.name == "更新后数据"
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据"

    def test_delete_success(self, unit_test_db: Session):
        """测试delete - 删除成功"""
        # 准备测试数据
        entity = Permission(name="待删除数据", resource="待删除数据", action="待删除数据")
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        PermissionRepository.delete(unit_test_db, entity)
        
        # 验证硬删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=entity_id).first()
        assert db_entity is None  # 记录已物理删除




@pytest.mark.unit
@pytest.mark.repositories
class TestUserRoleRepository:
    """
    UserRoleRepository 数据访问层测试
    
    测试范围:
    - 6 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库，无Mock依赖
    """
    
    def setup_method(self):
        """测试准备 - 每个测试方法执行前调用"""
        pass
        
    def teardown_method(self):
        """测试清理 - 每个测试方法执行后调用"""
        pass
        
    def test_create_success(self, unit_test_db: Session):
        """测试create - 成功创建"""
        # 准备测试数据（包括外键依赖）
        user = User(username="依赖测试数据", email="test_依赖测试数据@example.com", password_hash="依赖测试数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖测试数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        
        # 执行Repository方法
        result = UserRoleRepository.create(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        # 联合主键模型没有单独的id字段
        
        # 验证数据已持久化（使用联合主键查询）
        db_entity = unit_test_db.query(UserRole).filter_by(user_id=result.user_id, role_id=result.role_id).first()
        assert db_entity is not None
    
    def test_create_transaction(self, unit_test_db: Session):
        """测试create - 事务提交"""
        user = User(username="依赖事务测试", email="test_依赖事务测试@example.com", password_hash="依赖事务测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖事务测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        
        result = UserRoleRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（可以在新会话中查询到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(UserRole).filter_by(user_id=result.user_id, role_id=result.role_id).first()
        assert db_entity is not None

    def test_get_found(self, unit_test_db: Session):
        """测试get - 查询到数据"""
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖查询测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get(unit_test_db, entity.user_id, entity.role_id)
        
        # 验证结果
        assert result is not None
        assert result.user_id == entity.user_id
    
    def test_get_not_found(self, unit_test_db: Session):
        """测试get - 数据不存在"""
        result = UserRoleRepository.get(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_user_roles_found(self, unit_test_db: Session):
        """测试get_user_roles - 查询到数据"""
        # 准备依赖实体和关联数据
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 准备关联数据（如UserRole关联User和Role）
        entity = user = User(username="依赖关联数据", email="test_依赖关联数据@example.com", password_hash="依赖关联数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖关联数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get_user_roles(unit_test_db, user.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_user_roles_not_found(self, unit_test_db: Session):
        """测试get_user_roles - 数据不存在"""
        # 准备依赖实体（但不创建关联数据）
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get_user_roles(unit_test_db, user.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_role_users_found(self, unit_test_db: Session):
        """测试get_role_users - 查询到数据"""
        # 准备依赖实体和关联数据
        role = Role(name="Role数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        
        # 准备关联数据（如UserRole关联User和Role）
        entity = user = User(username="依赖关联数据", email="test_依赖关联数据@example.com", password_hash="依赖关联数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖关联数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get_role_users(unit_test_db, role.id, 1, 1)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_role_users_not_found(self, unit_test_db: Session):
        """测试get_role_users - 数据不存在"""
        # 准备依赖实体（但不创建关联数据）
        role = Role(name="Role数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get_role_users(unit_test_db, role.id, 1, 1)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0

    def test_delete_found(self, unit_test_db: Session):
        """测试delete - 查询到数据"""
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖查询测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.delete(unit_test_db, entity.user_id, entity.role_id)
        
        # 验证结果
        assert result is not None
        assert result.user_id == entity.user_id
    
    def test_delete_not_found(self, unit_test_db: Session):
        """测试delete - 数据不存在"""
        result = UserRoleRepository.delete(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_delete_all_user_roles_found(self, unit_test_db: Session):
        """测试delete_all_user_roles - 查询到数据"""
        # 准备依赖实体
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        role = Role(name="依赖查询测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        entity = UserRole(assigned_at=datetime.now(), user_id=user.id, role_id=role.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.delete_all_user_roles(unit_test_db, user.id)
        
        # 验证结果
        assert result is not None

    def test_delete_all_user_roles_not_found(self, unit_test_db: Session):
        """测试delete_all_user_roles - 数据不存在"""
        result = UserRoleRepository.delete_all_user_roles(unit_test_db, 99999)
        
        # 验证结果
        assert result is None




@pytest.mark.unit
@pytest.mark.repositories
class TestRolePermissionRepository:
    """
    RolePermissionRepository 数据访问层测试
    
    测试范围:
    - 6 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库，无Mock依赖
    """
    
    def setup_method(self):
        """测试准备 - 每个测试方法执行前调用"""
        pass
        
    def teardown_method(self):
        """测试清理 - 每个测试方法执行后调用"""
        pass
        
    def test_create_success(self, unit_test_db: Session):
        """测试create - 成功创建"""
        # 准备测试数据（包括外键依赖）
        role = Role(name="依赖测试数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖测试数据", resource="依赖测试数据", action="依赖测试数据")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        
        # 执行Repository方法
        result = RolePermissionRepository.create(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        # 联合主键模型没有单独的id字段
        
        # 验证数据已持久化（使用联合主键查询）
        db_entity = unit_test_db.query(RolePermission).filter_by(role_id=result.role_id, permission_id=result.permission_id).first()
        assert db_entity is not None
    
    def test_create_transaction(self, unit_test_db: Session):
        """测试create - 事务提交"""
        role = Role(name="依赖事务测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖事务测试", resource="依赖事务测试", action="依赖事务测试")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        
        result = RolePermissionRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（可以在新会话中查询到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(RolePermission).filter_by(role_id=result.role_id, permission_id=result.permission_id).first()
        assert db_entity is not None

    def test_get_found(self, unit_test_db: Session):
        """测试get - 查询到数据"""
        # 准备测试数据
        entity = role = Role(name="依赖查询测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖查询测试", resource="依赖查询测试", action="依赖查询测试")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get(unit_test_db, entity.role_id, entity.permission_id)
        
        # 验证结果
        assert result is not None
        assert result.role_id == entity.role_id
    
    def test_get_not_found(self, unit_test_db: Session):
        """测试get - 数据不存在"""
        result = RolePermissionRepository.get(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_role_permissions_found(self, unit_test_db: Session):
        """测试get_role_permissions - 查询到数据"""
        # 准备依赖实体和关联数据
        role = Role(name="Role数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        
        # 准备关联数据（如UserRole关联User和Role）
        entity = role = Role(name="依赖关联数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖关联数据", resource="依赖关联数据", action="依赖关联数据")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get_role_permissions(unit_test_db, role.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_role_permissions_not_found(self, unit_test_db: Session):
        """测试get_role_permissions - 数据不存在"""
        # 准备依赖实体（但不创建关联数据）
        role = Role(name="Role数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get_role_permissions(unit_test_db, role.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_user_permissions_found(self, unit_test_db: Session):
        """测试get_user_permissions - 查询到数据"""
        # 准备依赖实体和关联数据
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 准备关联数据（如UserRole关联User和Role）
        entity = role = Role(name="依赖关联数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖关联数据", resource="依赖关联数据", action="依赖关联数据")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get_user_permissions(unit_test_db, user.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_user_permissions_not_found(self, unit_test_db: Session):
        """测试get_user_permissions - 数据不存在"""
        # 准备依赖实体（但不创建关联数据）
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get_user_permissions(unit_test_db, user.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0

    def test_delete_found(self, unit_test_db: Session):
        """测试delete - 查询到数据"""
        # 准备测试数据
        entity = role = Role(name="依赖查询测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖查询测试", resource="依赖查询测试", action="依赖查询测试")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.delete(unit_test_db, entity.role_id, entity.permission_id)
        
        # 验证结果
        assert result is not None
        assert result.role_id == entity.role_id
    
    def test_delete_not_found(self, unit_test_db: Session):
        """测试delete - 数据不存在"""
        result = RolePermissionRepository.delete(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_delete_all_role_permissions_found(self, unit_test_db: Session):
        """测试delete_all_role_permissions - 查询到数据"""
        # 准备依赖实体
        role = Role(name="Role数据", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = role = Role(name="依赖查询测试", level=1)
        unit_test_db.add(role)
        unit_test_db.commit()
        permission = Permission(name="依赖查询测试", resource="依赖查询测试", action="依赖查询测试")
        unit_test_db.add(permission)
        unit_test_db.commit()
        entity = RolePermission(granted_at=datetime.now(), role_id=role.id, permission_id=permission.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.delete_all_role_permissions(unit_test_db, role.id)
        
        # 验证结果
        assert result is not None

    def test_delete_all_role_permissions_not_found(self, unit_test_db: Session):
        """测试delete_all_role_permissions - 数据不存在"""
        result = RolePermissionRepository.delete_all_role_permissions(unit_test_db, 99999)
        
        # 验证结果
        assert result is None




@pytest.mark.unit
@pytest.mark.repositories
class TestSessionRepository:
    """
    SessionRepository 数据访问层测试
    
    测试范围:
    - 9 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库，无Mock依赖
    """
    
    def setup_method(self):
        """测试准备 - 每个测试方法执行前调用"""
        pass
        
    def teardown_method(self):
        """测试清理 - 每个测试方法执行后调用"""
        pass
        
    def test_create_success(self, unit_test_db: Session):
        """测试create - 成功创建"""
        # 准备测试数据（包括外键依赖）
        user = User(username="依赖测试数据", email="test_依赖测试数据@example.com", password_hash="依赖测试数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="测试数据", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        
        # 执行Repository方法
        result = SessionRepository.create(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(Session).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction(self, unit_test_db: Session):
        """测试create - 事务提交"""
        user = User(username="依赖事务测试", email="test_依赖事务测试@example.com", password_hash="依赖事务测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="事务测试", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        
        result = SessionRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（可以在新会话中查询到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Session).filter_by(id=result.id).first()
        assert db_entity is not None

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备依赖实体
        session = user = User(username="依赖Session数据", email="test_依赖session数据@example.com", password_hash="依赖Session数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="Session数据", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(session)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="查询测试", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.get_by_id(unit_test_db, session.id)
        
        # 验证结果
        assert result is not None

    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = SessionRepository.get_by_id(unit_test_db, 99999)
        
        # 验证结果
        assert result is None

    def test_get_by_token_hash_found(self, unit_test_db: Session):
        """测试get_by_token_hash - 查询到数据"""
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="查询测试", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.get_by_token_hash(unit_test_db, entity.token_hash)
        
        # 验证结果
        assert result is not None
        assert result.token_hash == entity.token_hash
    
    def test_get_by_token_hash_not_found(self, unit_test_db: Session):
        """测试get_by_token_hash - 数据不存在"""
        result = SessionRepository.get_by_token_hash(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_user_active_sessions_found(self, unit_test_db: Session):
        """测试get_user_active_sessions - 查询到数据"""
        # 准备依赖实体和关联数据
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 准备关联数据（如UserRole关联User和Role）
        entity = user = User(username="依赖关联数据", email="test_依赖关联数据@example.com", password_hash="依赖关联数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="关联数据", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.get_user_active_sessions(unit_test_db, user.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_user_active_sessions_not_found(self, unit_test_db: Session):
        """测试get_user_active_sessions - 数据不存在"""
        # 准备依赖实体（但不创建关联数据）
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.get_user_active_sessions(unit_test_db, user.id)
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0

    # TODO: 测试专用更新方法 update_last_accessed
    # 这是一个专用更新方法，只修改特定字段，需要根据业务逻辑手动编写测试
    # 方法签名: [('db', 'Session'), ('session', 'UserSession')]
    # 返回类型: UserSession
    

    def test_deactivate_success(self, unit_test_db: Session):
        """测试deactivate - 删除成功"""
        # 准备测试数据
        entity = user = User(username="依赖待删除数据", email="test_依赖待删除数据@example.com", password_hash="依赖待删除数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="待删除数据", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        result = SessionRepository.deactivate(unit_test_db, entity)
        
        # 验证结果
        assert result is not None
        
        # 验证软删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Session).filter_by(id=entity_id).first()
        assert db_entity is not None  # 记录仍存在
        # 验证软删除标记（根据模型字段选择）
        if hasattr(db_entity, 'is_deleted'):
            assert db_entity.is_deleted == True
        if hasattr(db_entity, 'is_active'):
            assert db_entity.is_active == False

    def test_deactivate_user_sessions_found(self, unit_test_db: Session):
        """测试deactivate_user_sessions - 查询到数据"""
        # 准备依赖实体
        user = User(username="User数据", email="test_user数据@example.com", password_hash="User数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="查询测试", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.deactivate_user_sessions(unit_test_db, user.id)
        
        # 验证结果
        assert result is not None

    def test_deactivate_user_sessions_not_found(self, unit_test_db: Session):
        """测试deactivate_user_sessions - 数据不存在"""
        result = SessionRepository.deactivate_user_sessions(unit_test_db, 99999)
        
        # 验证结果
        assert result is None

    def test_delete_expired_sessions_found(self, unit_test_db: Session):
        """测试delete_expired_sessions - 查询到数据"""
        # 准备测试数据
        entity = user = User(username="依赖查询测试", email="test_依赖查询测试@example.com", password_hash="依赖查询测试", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="查询测试", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.delete_expired_sessions(unit_test_db, entity.id)
        
        # 验证结果
        assert result is not None
        assert result.id == entity.id
    
    def test_delete_expired_sessions_not_found(self, unit_test_db: Session):
        """测试delete_expired_sessions - 数据不存在"""
        result = SessionRepository.delete_expired_sessions(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_delete_success(self, unit_test_db: Session):
        """测试delete - 删除成功"""
        # 准备测试数据
        entity = user = User(username="依赖待删除数据", email="test_依赖待删除数据@example.com", password_hash="依赖待删除数据", is_active=True, status="active", email_verified=True, phone_verified=True, two_factor_enabled=True, failed_login_attempts=1, role="user")
        unit_test_db.add(user)
        unit_test_db.commit()
        entity = Session(token_hash="待删除数据", expires_at=datetime.now(), last_accessed_at=datetime.now(), is_active=True, user_id=user.id)
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        SessionRepository.delete(unit_test_db, entity)
        
        # 验证硬删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Session).filter_by(id=entity_id).first()
        assert db_entity is None  # 记录已物理删除

