"""
User_Auth 服务层测试套件

测试类型: 单元测试 (Service)
数据策略: SQLite内存数据库, unit_test_db fixture
生成时间: 2025-09-20 21:34:33

根据testing-standards.md第54-68行服务测试规范
"""

import pytest
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import User_AuthFactory, UserFactory

# Fixture导入
from tests.conftest import unit_test_db

# 被测模块导入
from app.modules.user_auth.service import User_AuthService
from app.modules.user_auth.models import User_Auth


class TestUser_AuthService:
    """服务层业务逻辑测试"""
    
    def setup_method(self):
        """测试准备"""
        self.test_data = User_AuthFactory.build_dict()
        
    def test_create_user_auth_with_valid_data(self, unit_test_db: Session):
        """测试创建user_auth - 有效数据"""
        # Arrange
        service = User_AuthService(unit_test_db)
        create_data = self.test_data
        
        # Act
        created_user_auth = service.create(create_data)
        
        # Assert
        assert created_user_auth is not None
        assert created_user_auth.id is not None
        assert hasattr(created_user_auth, 'created_at')
        
        # 验证数据库存储
        db_user_auth = unit_test_db.query(User_Auth).filter_by(
            id=created_user_auth.id
        ).first()
        assert db_user_auth is not None
        
    def test_get_user_auth_by_id_exists(self, unit_test_db: Session):
        """测试按ID查询user_auth - 存在"""
        # 准备测试数据
        user_auth_data = User_AuthFactory.create_dict()
        service = User_AuthService(unit_test_db)
        created = service.create(user_auth_data)
        
        # 执行查询
        found_user_auth = service.get_by_id(created.id)
        
        # 验证结果
        assert found_user_auth is not None
        assert found_user_auth.id == created.id
        
    def test_get_user_auth_by_id_not_exists(self, unit_test_db: Session):
        """测试按ID查询user_auth - 不存在"""
        service = User_AuthService(unit_test_db)
        
        # 查询不存在的ID
        result = service.get_by_id(99999)
        
        # 验证返回None
        assert result is None
        
    def test_update_user_auth_success(self, unit_test_db: Session):
        """测试更新user_auth - 成功"""
        # 创建测试数据
        service = User_AuthService(unit_test_db)
        created = service.create(self.test_data)
        
        # 准备更新数据
        update_data = {"status": "updated"}
        
        # 执行更新
        updated = service.update(created.id, update_data)
        
        # 验证更新结果
        assert updated is not None
        assert updated.status == "updated"
        assert hasattr(updated, 'updated_at')
        
    def test_delete_user_auth_success(self, unit_test_db: Session):
        """测试删除user_auth - 成功"""
        # 创建测试数据
        service = User_AuthService(unit_test_db)
        created = service.create(self.test_data)
        
        # 执行删除
        result = service.delete(created.id)
        
        # 验证删除结果
        assert result is True
        
        # 验证数据库中已删除
        deleted = service.get_by_id(created.id)
        assert deleted is None
