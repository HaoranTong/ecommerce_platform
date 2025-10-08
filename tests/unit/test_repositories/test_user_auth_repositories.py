"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/unit/test_repositories/test_user_auth_repositories.py
生成时间: 2025-10-08 14:53:06
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
    - 15 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
    
    def setup_method(self, unit_test_db: Session):
        """测试准备 - 初始化Factory Manager"""
        from tests.factories.user_auth_factories import UserAuthFactoryManager
        self.factory_manager = UserAuthFactoryManager()
        self.factory_manager.setup_factories(unit_test_db)
        
    def teardown_method(self):
        """测试清理"""
        pass
        
    def test_create_minimal_fields(self, unit_test_db: Session):
        """测试create - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
        # 创建最小实体（只填必填字段）
        entity = User()  # TODO: 补充必填字段
        
        # 执行Repository方法
        result = UserRepository.create(unit_test_db, entity)
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(User).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_full_fields(self, unit_test_db: Session):
        """测试create - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用Factory Boy
        """
        # 使用Factory Boy创建完整实体
        from tests.factories.user_auth_factories import UserFactory
        entity = UserFactory.build()  # build不自动保存到数据库
        
        # 执行Repository方法
        result = UserRepository.create(unit_test_db, entity)
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query(User).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction_commit(self, unit_test_db: Session):
        """测试create - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证数据真正写入数据库
        """
        from tests.factories.user_auth_factories import UserFactory
        entity = UserFactory.build()
        
        result = UserRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=result.id).first()
        assert db_entity is not None
        
    def test_create_transaction_rollback(self, unit_test_db: Session):
        """测试create - 事务回滚验证
        
        符合标准: testing-standards.md 第2.5节 - 验证错误时回滚
        """
        from tests.factories.user_auth_factories import UserFactory
        
        initial_count = unit_test_db.query(User).count()
        
        try:
            entity = UserFactory.build()
            result = UserRepository.create(unit_test_db, entity)
            unit_test_db.flush()
            
            # 模拟错误，触发回滚
            raise Exception("Simulated error")
        except Exception:
            unit_test_db.rollback()
        
        # 验证回滚后数据未增加
        final_count = unit_test_db.query(User).count()
        assert final_count == initial_count

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备测试数据
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_id(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = UserRepository.get_by_id(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_username_found(self, unit_test_db: Session):
        """测试get_by_username - 查询到数据"""
        # 准备测试数据
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
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

    def test_get_by_phone_found(self, unit_test_db: Session):
        """测试get_by_phone - 查询到数据"""
        # 准备测试数据
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRepository.get_by_phone(unit_test_db, entity.phone)
        
        # 验证结果
        assert result is not None
        assert result.phone == entity.phone
    
    def test_get_by_phone_not_found(self, unit_test_db: Session):
        """测试get_by_phone - 数据不存在"""
        result = UserRepository.get_by_phone(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_wx_openid_found(self, unit_test_db: Session):
        """测试get_by_wx_openid - 查询到数据"""
        # 准备测试数据
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = User(name="查询测试")  # TODO: 根据实际字段调整
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
        entity0 = User(name="测试数据0")  # TODO: 根据实际字段调整
        unit_test_db.add(entity0)
        entity1 = User(name="测试数据1")  # TODO: 根据实际字段调整
        unit_test_db.add(entity1)
        entity2 = User(name="测试数据2")  # TODO: 根据实际字段调整
        unit_test_db.add(entity2)
        entity3 = User(name="测试数据3")  # TODO: 根据实际字段调整
        unit_test_db.add(entity3)
        entity4 = User(name="测试数据4")  # TODO: 根据实际字段调整
        unit_test_db.add(entity4)
        unit_test_db.commit()
        
        # 执行Repository方法
        count = UserRepository.count(unit_test_db)
        
        # 验证计数
        assert isinstance(count, int)
        assert count >= 0

    def test_update_single_field(self, unit_test_db: Session):
        """测试update - 单字段更新
        
        符合标准: testing-standards.md 第2.3节 - 只更新一个字段，验证其他字段不变
        """
        # 准备测试数据
        from tests.factories.user_auth_factories import UserFactory
        entity = UserFactory.create()
        original_description = entity.description
        
        # 执行Repository方法（只更新name）
        update_data = {"name": "更新后数据"}
        result = UserRepository.update(unit_test_db, entity, update_data)  # TODO: 根据实际方法签名调整
        
        # 验证目标字段已更新
        assert result.name == "更新后数据"
        
        # ✅ 验证其他字段未变化
        assert result.description == original_description
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据"
        assert db_entity.description == original_description
    
    def test_update_multiple_fields(self, unit_test_db: Session):
        """测试update - 多字段更新
        
        符合标准: testing-standards.md 第2.3节 - 同时更新多个字段
        """
        from tests.factories.user_auth_factories import UserFactory
        entity = UserFactory.create()
        
        # 执行Repository方法（同时更新多个字段）
        update_data = {
            "name": "更新后数据1",
            "description": "更新后数据2"
        }
        result = UserRepository.update(unit_test_db, entity, update_data)
        
        # 验证所有字段已更新
        assert result.name == "更新后数据1"
        assert result.description == "更新后数据2"
        
        # 验证持久化
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据1"
        assert db_entity.description == "更新后数据2"
    
    def test_update_transaction_commit(self, unit_test_db: Session):
        """测试update - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证更新真正写入数据库
        """
        from tests.factories.user_auth_factories import UserFactory
        entity = UserFactory.create()
        
        update_data = {"name": "事务测试数据"}
        result = UserRepository.update(unit_test_db, entity, update_data)
        
        # 验证事务已提交
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(User).filter_by(id=entity.id).first()
        assert db_entity.name == "事务测试数据"
    
    def test_update_specialized_method(self, unit_test_db: Session):
        """测试update - 专用方法测试（如有）
        
        符合标准: testing-standards.md 第2.3节 - 测试特殊更新方法
        示例: update_status, update_password, activate, deactivate等
        """
        # TODO: 如果有专用更新方法，在这里测试
        # 例如:
        # entity = UserFactory.create(status='active')
        # result = UserRepository.update_status(unit_test_db, entity.id, 'inactive')
        # assert result.status == 'inactive'
        pass

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
        entity = User(name="待删除数据")  # TODO: 根据实际字段调整
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
        entity = User(name="待删除数据")  # TODO: 根据实际字段调整
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
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
    
    def setup_method(self, unit_test_db: Session):
        """测试准备 - 初始化Factory Manager"""
        from tests.factories.user_auth_factories import UserAuthFactoryManager
        self.factory_manager = UserAuthFactoryManager()
        self.factory_manager.setup_factories(unit_test_db)
        
    def teardown_method(self):
        """测试清理"""
        pass
        
    def test_create_minimal_fields(self, unit_test_db: Session):
        """测试create - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
        # 创建最小实体（只填必填字段）
        entity = Role()  # TODO: 补充必填字段
        
        # 执行Repository方法
        result = RoleRepository.create(unit_test_db, entity)
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(Role).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_full_fields(self, unit_test_db: Session):
        """测试create - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用Factory Boy
        """
        # 使用Factory Boy创建完整实体
        from tests.factories.user_auth_factories import RoleFactory
        entity = RoleFactory.build()  # build不自动保存到数据库
        
        # 执行Repository方法
        result = RoleRepository.create(unit_test_db, entity)
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query(Role).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction_commit(self, unit_test_db: Session):
        """测试create - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证数据真正写入数据库
        """
        from tests.factories.user_auth_factories import RoleFactory
        entity = RoleFactory.build()
        
        result = RoleRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=result.id).first()
        assert db_entity is not None
        
    def test_create_transaction_rollback(self, unit_test_db: Session):
        """测试create - 事务回滚验证
        
        符合标准: testing-standards.md 第2.5节 - 验证错误时回滚
        """
        from tests.factories.user_auth_factories import RoleFactory
        
        initial_count = unit_test_db.query(Role).count()
        
        try:
            entity = RoleFactory.build()
            result = RoleRepository.create(unit_test_db, entity)
            unit_test_db.flush()
            
            # 模拟错误，触发回滚
            raise Exception("Simulated error")
        except Exception:
            unit_test_db.rollback()
        
        # 验证回滚后数据未增加
        final_count = unit_test_db.query(Role).count()
        assert final_count == initial_count

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备测试数据
        entity = Role(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RoleRepository.get_by_id(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = RoleRepository.get_by_id(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_name_found(self, unit_test_db: Session):
        """测试get_by_name - 查询到数据"""
        # 准备测试数据
        entity = Role(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = Role(name="查询测试")  # TODO: 根据实际字段调整
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

    def test_update_single_field(self, unit_test_db: Session):
        """测试update - 单字段更新
        
        符合标准: testing-standards.md 第2.3节 - 只更新一个字段，验证其他字段不变
        """
        # 准备测试数据
        from tests.factories.user_auth_factories import RoleFactory
        entity = RoleFactory.create()
        original_description = entity.description
        
        # 执行Repository方法（只更新name）
        update_data = {"name": "更新后数据"}
        result = RoleRepository.update(unit_test_db, entity, update_data)  # TODO: 根据实际方法签名调整
        
        # 验证目标字段已更新
        assert result.name == "更新后数据"
        
        # ✅ 验证其他字段未变化
        assert result.description == original_description
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据"
        assert db_entity.description == original_description
    
    def test_update_multiple_fields(self, unit_test_db: Session):
        """测试update - 多字段更新
        
        符合标准: testing-standards.md 第2.3节 - 同时更新多个字段
        """
        from tests.factories.user_auth_factories import RoleFactory
        entity = RoleFactory.create()
        
        # 执行Repository方法（同时更新多个字段）
        update_data = {
            "name": "更新后数据1",
            "description": "更新后数据2"
        }
        result = RoleRepository.update(unit_test_db, entity, update_data)
        
        # 验证所有字段已更新
        assert result.name == "更新后数据1"
        assert result.description == "更新后数据2"
        
        # 验证持久化
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据1"
        assert db_entity.description == "更新后数据2"
    
    def test_update_transaction_commit(self, unit_test_db: Session):
        """测试update - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证更新真正写入数据库
        """
        from tests.factories.user_auth_factories import RoleFactory
        entity = RoleFactory.create()
        
        update_data = {"name": "事务测试数据"}
        result = RoleRepository.update(unit_test_db, entity, update_data)
        
        # 验证事务已提交
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Role).filter_by(id=entity.id).first()
        assert db_entity.name == "事务测试数据"
    
    def test_update_specialized_method(self, unit_test_db: Session):
        """测试update - 专用方法测试（如有）
        
        符合标准: testing-standards.md 第2.3节 - 测试特殊更新方法
        示例: update_status, update_password, activate, deactivate等
        """
        # TODO: 如果有专用更新方法，在这里测试
        # 例如:
        # entity = RoleFactory.create(status='active')
        # result = RoleRepository.update_status(unit_test_db, entity.id, 'inactive')
        # assert result.status == 'inactive'
        pass

    def test_delete_success(self, unit_test_db: Session):
        """测试delete - 删除成功"""
        # 准备测试数据
        entity = Role(name="待删除数据")  # TODO: 根据实际字段调整
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
        entity0 = Role(name="测试数据0")  # TODO: 根据实际字段调整
        unit_test_db.add(entity0)
        entity1 = Role(name="测试数据1")  # TODO: 根据实际字段调整
        unit_test_db.add(entity1)
        entity2 = Role(name="测试数据2")  # TODO: 根据实际字段调整
        unit_test_db.add(entity2)
        entity3 = Role(name="测试数据3")  # TODO: 根据实际字段调整
        unit_test_db.add(entity3)
        entity4 = Role(name="测试数据4")  # TODO: 根据实际字段调整
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
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
    
    def setup_method(self, unit_test_db: Session):
        """测试准备 - 初始化Factory Manager"""
        from tests.factories.user_auth_factories import UserAuthFactoryManager
        self.factory_manager = UserAuthFactoryManager()
        self.factory_manager.setup_factories(unit_test_db)
        
    def teardown_method(self):
        """测试清理"""
        pass
        
    def test_create_minimal_fields(self, unit_test_db: Session):
        """测试create - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
        # 创建最小实体（只填必填字段）
        entity = Permission()  # TODO: 补充必填字段
        
        # 执行Repository方法
        result = PermissionRepository.create(unit_test_db, entity)
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(Permission).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_full_fields(self, unit_test_db: Session):
        """测试create - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用Factory Boy
        """
        # 使用Factory Boy创建完整实体
        from tests.factories.user_auth_factories import PermissionFactory
        entity = PermissionFactory.build()  # build不自动保存到数据库
        
        # 执行Repository方法
        result = PermissionRepository.create(unit_test_db, entity)
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query(Permission).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction_commit(self, unit_test_db: Session):
        """测试create - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证数据真正写入数据库
        """
        from tests.factories.user_auth_factories import PermissionFactory
        entity = PermissionFactory.build()
        
        result = PermissionRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=result.id).first()
        assert db_entity is not None
        
    def test_create_transaction_rollback(self, unit_test_db: Session):
        """测试create - 事务回滚验证
        
        符合标准: testing-standards.md 第2.5节 - 验证错误时回滚
        """
        from tests.factories.user_auth_factories import PermissionFactory
        
        initial_count = unit_test_db.query(Permission).count()
        
        try:
            entity = PermissionFactory.build()
            result = PermissionRepository.create(unit_test_db, entity)
            unit_test_db.flush()
            
            # 模拟错误，触发回滚
            raise Exception("Simulated error")
        except Exception:
            unit_test_db.rollback()
        
        # 验证回滚后数据未增加
        final_count = unit_test_db.query(Permission).count()
        assert final_count == initial_count

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备测试数据
        entity = Permission(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = PermissionRepository.get_by_id(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = PermissionRepository.get_by_id(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_name_found(self, unit_test_db: Session):
        """测试get_by_name - 查询到数据"""
        # 准备测试数据
        entity = Permission(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = Permission(name="查询测试")  # TODO: 根据实际字段调整
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

    def test_update_single_field(self, unit_test_db: Session):
        """测试update - 单字段更新
        
        符合标准: testing-standards.md 第2.3节 - 只更新一个字段，验证其他字段不变
        """
        # 准备测试数据
        from tests.factories.user_auth_factories import PermissionFactory
        entity = PermissionFactory.create()
        original_description = entity.description
        
        # 执行Repository方法（只更新name）
        update_data = {"name": "更新后数据"}
        result = PermissionRepository.update(unit_test_db, entity, update_data)  # TODO: 根据实际方法签名调整
        
        # 验证目标字段已更新
        assert result.name == "更新后数据"
        
        # ✅ 验证其他字段未变化
        assert result.description == original_description
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据"
        assert db_entity.description == original_description
    
    def test_update_multiple_fields(self, unit_test_db: Session):
        """测试update - 多字段更新
        
        符合标准: testing-standards.md 第2.3节 - 同时更新多个字段
        """
        from tests.factories.user_auth_factories import PermissionFactory
        entity = PermissionFactory.create()
        
        # 执行Repository方法（同时更新多个字段）
        update_data = {
            "name": "更新后数据1",
            "description": "更新后数据2"
        }
        result = PermissionRepository.update(unit_test_db, entity, update_data)
        
        # 验证所有字段已更新
        assert result.name == "更新后数据1"
        assert result.description == "更新后数据2"
        
        # 验证持久化
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=entity.id).first()
        assert db_entity.name == "更新后数据1"
        assert db_entity.description == "更新后数据2"
    
    def test_update_transaction_commit(self, unit_test_db: Session):
        """测试update - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证更新真正写入数据库
        """
        from tests.factories.user_auth_factories import PermissionFactory
        entity = PermissionFactory.create()
        
        update_data = {"name": "事务测试数据"}
        result = PermissionRepository.update(unit_test_db, entity, update_data)
        
        # 验证事务已提交
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Permission).filter_by(id=entity.id).first()
        assert db_entity.name == "事务测试数据"
    
    def test_update_specialized_method(self, unit_test_db: Session):
        """测试update - 专用方法测试（如有）
        
        符合标准: testing-standards.md 第2.3节 - 测试特殊更新方法
        示例: update_status, update_password, activate, deactivate等
        """
        # TODO: 如果有专用更新方法，在这里测试
        # 例如:
        # entity = PermissionFactory.create(status='active')
        # result = PermissionRepository.update_status(unit_test_db, entity.id, 'inactive')
        # assert result.status == 'inactive'
        pass

    def test_delete_success(self, unit_test_db: Session):
        """测试delete - 删除成功"""
        # 准备测试数据
        entity = Permission(name="待删除数据")  # TODO: 根据实际字段调整
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
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
    
    def setup_method(self, unit_test_db: Session):
        """测试准备 - 初始化Factory Manager"""
        from tests.factories.user_auth_factories import UserAuthFactoryManager
        self.factory_manager = UserAuthFactoryManager()
        self.factory_manager.setup_factories(unit_test_db)
        
    def teardown_method(self):
        """测试清理"""
        pass
        
    def test_create_minimal_fields(self, unit_test_db: Session):
        """测试create - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
        # 创建最小实体（只填必填字段）
        entity = UserRole()  # TODO: 补充必填字段
        
        # 执行Repository方法
        result = UserRoleRepository.create(unit_test_db, entity)
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(UserRole).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_full_fields(self, unit_test_db: Session):
        """测试create - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用Factory Boy
        """
        # 使用Factory Boy创建完整实体
        from tests.factories.user_auth_factories import UserRoleFactory
        entity = UserRoleFactory.build()  # build不自动保存到数据库
        
        # 执行Repository方法
        result = UserRoleRepository.create(unit_test_db, entity)
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query(UserRole).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction_commit(self, unit_test_db: Session):
        """测试create - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证数据真正写入数据库
        """
        from tests.factories.user_auth_factories import UserRoleFactory
        entity = UserRoleFactory.build()
        
        result = UserRoleRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(UserRole).filter_by(id=result.id).first()
        assert db_entity is not None
        
    def test_create_transaction_rollback(self, unit_test_db: Session):
        """测试create - 事务回滚验证
        
        符合标准: testing-standards.md 第2.5节 - 验证错误时回滚
        """
        from tests.factories.user_auth_factories import UserRoleFactory
        
        initial_count = unit_test_db.query(UserRole).count()
        
        try:
            entity = UserRoleFactory.build()
            result = UserRoleRepository.create(unit_test_db, entity)
            unit_test_db.flush()
            
            # 模拟错误，触发回滚
            raise Exception("Simulated error")
        except Exception:
            unit_test_db.rollback()
        
        # 验证回滚后数据未增加
        final_count = unit_test_db.query(UserRole).count()
        assert final_count == initial_count

    def test_get_found(self, unit_test_db: Session):
        """测试get - 查询到数据"""
        # 准备测试数据
        entity = UserRole(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get(unit_test_db, 1, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_get_not_found(self, unit_test_db: Session):
        """测试get - 数据不存在"""
        result = UserRoleRepository.get(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_user_roles_found(self, unit_test_db: Session):
        """测试get_user_roles - 查询到数据"""
        # 准备测试数据
        entity = UserRole(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get_user_roles(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_get_user_roles_not_found(self, unit_test_db: Session):
        """测试get_user_roles - 数据不存在"""
        result = UserRoleRepository.get_user_roles(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_role_users_found(self, unit_test_db: Session):
        """测试get_role_users - 查询到数据"""
        # 准备测试数据
        entity = UserRole(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.get_role_users(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_get_role_users_not_found(self, unit_test_db: Session):
        """测试get_role_users - 数据不存在"""
        result = UserRoleRepository.get_role_users(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_delete_found(self, unit_test_db: Session):
        """测试delete - 查询到数据"""
        # 准备测试数据
        entity = UserRole(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.delete(unit_test_db, 1, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_delete_not_found(self, unit_test_db: Session):
        """测试delete - 数据不存在"""
        result = UserRoleRepository.delete(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_delete_all_user_roles_found(self, unit_test_db: Session):
        """测试delete_all_user_roles - 查询到数据"""
        # 准备测试数据
        entity = UserRole(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = UserRoleRepository.delete_all_user_roles(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_delete_all_user_roles_not_found(self, unit_test_db: Session):
        """测试delete_all_user_roles - 数据不存在"""
        result = UserRoleRepository.delete_all_user_roles(unit_test_db, "nonexistent_value_12345")
        
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
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
    
    def setup_method(self, unit_test_db: Session):
        """测试准备 - 初始化Factory Manager"""
        from tests.factories.user_auth_factories import UserAuthFactoryManager
        self.factory_manager = UserAuthFactoryManager()
        self.factory_manager.setup_factories(unit_test_db)
        
    def teardown_method(self):
        """测试清理"""
        pass
        
    def test_create_minimal_fields(self, unit_test_db: Session):
        """测试create - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
        # 创建最小实体（只填必填字段）
        entity = RolePermission()  # TODO: 补充必填字段
        
        # 执行Repository方法
        result = RolePermissionRepository.create(unit_test_db, entity)
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(RolePermission).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_full_fields(self, unit_test_db: Session):
        """测试create - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用Factory Boy
        """
        # 使用Factory Boy创建完整实体
        from tests.factories.user_auth_factories import RolePermissionFactory
        entity = RolePermissionFactory.build()  # build不自动保存到数据库
        
        # 执行Repository方法
        result = RolePermissionRepository.create(unit_test_db, entity)
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query(RolePermission).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction_commit(self, unit_test_db: Session):
        """测试create - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证数据真正写入数据库
        """
        from tests.factories.user_auth_factories import RolePermissionFactory
        entity = RolePermissionFactory.build()
        
        result = RolePermissionRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(RolePermission).filter_by(id=result.id).first()
        assert db_entity is not None
        
    def test_create_transaction_rollback(self, unit_test_db: Session):
        """测试create - 事务回滚验证
        
        符合标准: testing-standards.md 第2.5节 - 验证错误时回滚
        """
        from tests.factories.user_auth_factories import RolePermissionFactory
        
        initial_count = unit_test_db.query(RolePermission).count()
        
        try:
            entity = RolePermissionFactory.build()
            result = RolePermissionRepository.create(unit_test_db, entity)
            unit_test_db.flush()
            
            # 模拟错误，触发回滚
            raise Exception("Simulated error")
        except Exception:
            unit_test_db.rollback()
        
        # 验证回滚后数据未增加
        final_count = unit_test_db.query(RolePermission).count()
        assert final_count == initial_count

    def test_get_found(self, unit_test_db: Session):
        """测试get - 查询到数据"""
        # 准备测试数据
        entity = RolePermission(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get(unit_test_db, 1, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_get_not_found(self, unit_test_db: Session):
        """测试get - 数据不存在"""
        result = RolePermissionRepository.get(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_role_permissions_found(self, unit_test_db: Session):
        """测试get_role_permissions - 查询到数据"""
        # 准备测试数据
        entity = RolePermission(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get_role_permissions(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_get_role_permissions_not_found(self, unit_test_db: Session):
        """测试get_role_permissions - 数据不存在"""
        result = RolePermissionRepository.get_role_permissions(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_user_permissions_found(self, unit_test_db: Session):
        """测试get_user_permissions - 查询到数据"""
        # 准备测试数据
        entity = RolePermission(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.get_user_permissions(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_get_user_permissions_not_found(self, unit_test_db: Session):
        """测试get_user_permissions - 数据不存在"""
        result = RolePermissionRepository.get_user_permissions(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_delete_found(self, unit_test_db: Session):
        """测试delete - 查询到数据"""
        # 准备测试数据
        entity = RolePermission(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.delete(unit_test_db, 1, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_delete_not_found(self, unit_test_db: Session):
        """测试delete - 数据不存在"""
        result = RolePermissionRepository.delete(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_delete_all_role_permissions_found(self, unit_test_db: Session):
        """测试delete_all_role_permissions - 查询到数据"""
        # 准备测试数据
        entity = RolePermission(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = RolePermissionRepository.delete_all_role_permissions(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_delete_all_role_permissions_not_found(self, unit_test_db: Session):
        """测试delete_all_role_permissions - 数据不存在"""
        result = RolePermissionRepository.delete_all_role_permissions(unit_test_db, "nonexistent_value_12345")
        
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
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
    
    def setup_method(self, unit_test_db: Session):
        """测试准备 - 初始化Factory Manager"""
        from tests.factories.user_auth_factories import UserAuthFactoryManager
        self.factory_manager = UserAuthFactoryManager()
        self.factory_manager.setup_factories(unit_test_db)
        
    def teardown_method(self):
        """测试清理"""
        pass
        
    def test_create_minimal_fields(self, unit_test_db: Session):
        """测试create - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
        # 创建最小实体（只填必填字段）
        entity = Session()  # TODO: 补充必填字段
        
        # 执行Repository方法
        result = SessionRepository.create(unit_test_db, entity)
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query(Session).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_full_fields(self, unit_test_db: Session):
        """测试create - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用Factory Boy
        """
        # 使用Factory Boy创建完整实体
        from tests.factories.user_auth_factories import SessionFactory
        entity = SessionFactory.build()  # build不自动保存到数据库
        
        # 执行Repository方法
        result = SessionRepository.create(unit_test_db, entity)
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query(Session).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_create_transaction_commit(self, unit_test_db: Session):
        """测试create - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证数据真正写入数据库
        """
        from tests.factories.user_auth_factories import SessionFactory
        entity = SessionFactory.build()
        
        result = SessionRepository.create(unit_test_db, entity)
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Session).filter_by(id=result.id).first()
        assert db_entity is not None
        
    def test_create_transaction_rollback(self, unit_test_db: Session):
        """测试create - 事务回滚验证
        
        符合标准: testing-standards.md 第2.5节 - 验证错误时回滚
        """
        from tests.factories.user_auth_factories import SessionFactory
        
        initial_count = unit_test_db.query(Session).count()
        
        try:
            entity = SessionFactory.build()
            result = SessionRepository.create(unit_test_db, entity)
            unit_test_db.flush()
            
            # 模拟错误，触发回滚
            raise Exception("Simulated error")
        except Exception:
            unit_test_db.rollback()
        
        # 验证回滚后数据未增加
        final_count = unit_test_db.query(Session).count()
        assert final_count == initial_count

    def test_get_by_id_found(self, unit_test_db: Session):
        """测试get_by_id - 查询到数据"""
        # 准备测试数据
        entity = Session(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.get_by_id(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_get_by_id_not_found(self, unit_test_db: Session):
        """测试get_by_id - 数据不存在"""
        result = SessionRepository.get_by_id(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_get_by_token_hash_found(self, unit_test_db: Session):
        """测试get_by_token_hash - 查询到数据"""
        # 准备测试数据
        entity = Session(name="查询测试")  # TODO: 根据实际字段调整
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
        # 准备测试数据
        entity = Session(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.get_user_active_sessions(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(item.id == entity.id for item in result)
    
    def test_get_user_active_sessions_not_found(self, unit_test_db: Session):
        """测试get_user_active_sessions - 数据不存在"""
        result = SessionRepository.get_user_active_sessions(unit_test_db)  # TODO: 根据实际方法签名调整参数
        
        assert isinstance(result, list)
        assert len(result) == 0

    # TODO: 测试专用更新方法 update_last_accessed
    # 这是一个专用更新方法，只修改特定字段，需要根据业务逻辑手动编写测试
    # 方法签名: [('db', 'Session'), ('session', 'UserSession')]
    # 返回类型: UserSession
    

    def test_deactivate_success(self, unit_test_db: Session):
        """测试deactivate - 删除成功"""
        # 准备测试数据
        entity = Session(name="待删除数据")  # TODO: 根据实际字段调整
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
        # 准备测试数据
        entity = Session(name="查询测试")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = SessionRepository.deactivate_user_sessions(unit_test_db, 1)
        
        # 验证结果
        assert result is not None
        assert result.1 == entity.1
    
    def test_deactivate_user_sessions_not_found(self, unit_test_db: Session):
        """测试deactivate_user_sessions - 数据不存在"""
        result = SessionRepository.deactivate_user_sessions(unit_test_db, "nonexistent_value_12345")
        
        assert result is None

    def test_delete_expired_sessions_found(self, unit_test_db: Session):
        """测试delete_expired_sessions - 查询到数据"""
        # 准备测试数据
        entity = Session(name="查询测试")  # TODO: 根据实际字段调整
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
        entity = Session(name="待删除数据")  # TODO: 根据实际字段调整
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        SessionRepository.delete(unit_test_db, entity)
        
        # 验证硬删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query(Session).filter_by(id=entity_id).first()
        assert db_entity is None  # 记录已物理删除

