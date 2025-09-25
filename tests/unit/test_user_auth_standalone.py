"""
User Auth 独立业务流程测试套件

测试类型: 单元测试 (Standalone Business Flow)
数据策略: SQLite内存数据库, unit_test_db fixture
生成时间: 2025-09-25 更新

根据testing-standards.md业务流程测试规范
"""

import pytest
from sqlalchemy.orm import Session

# 被测模块导入
from app.modules.user_auth.service import UserService
from app.modules.user_auth.models import User
from app.modules.user_auth.schemas import UserCreate, UserRegister

# Fixture导入  
from tests.conftest import unit_test_db


class TestUserAuthBusinessFlow:
    """用户认证独立业务流程测试"""
    
    def setup_method(self):
        """测试准备"""
        self.user_register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123456",
            "verification_code": "123456"
        }
        
    def test_complete_user_registration_workflow(self, unit_test_db: Session):
        """测试完整用户注册业务流程"""
        
        # 步骤1: 创建用户
        created_user = UserService.create_user(
            db=unit_test_db,
            username=self.user_register_data["username"],
            email=self.user_register_data["email"],
            password=self.user_register_data["password"]
        )
        assert created_user is not None
        assert created_user.id is not None
        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"
        
        # 步骤2: 查询验证
        found_user = UserService.get_user_by_id(unit_test_db, created_user.id)
        assert found_user is not None
        assert found_user.id == created_user.id
        
        # 步骤3: 用户认证测试
        authenticated_user = UserService.authenticate_user(
            db=unit_test_db,
            username="testuser",
            password="Test123456"
        )
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        
        # 步骤4: 错误密码测试
        wrong_password_result = UserService.authenticate_user(
            db=unit_test_db,
            username="testuser",
            password="WrongPassword"
        )
        assert wrong_password_result is None
        
    def test_user_password_change_workflow(self, unit_test_db: Session):
        """测试用户密码修改业务流程"""
        
        # 准备：创建用户
        user = UserService.create_user(
            db=unit_test_db,
            username="changeuser",
            email="change@example.com",
            password="OldPassword123"
        )
        
        # 步骤1: 修改密码
        password_changed = UserService.change_password(
            db=unit_test_db,
            user_id=user.id,
            old_password="OldPassword123",
            new_password="NewPassword456"
        )
        assert password_changed is True
        
        # 步骤2: 用新密码登录
        auth_result = UserService.authenticate_user(
            db=unit_test_db,
            username="changeuser",
            password="NewPassword456"
        )
        assert auth_result is not None
        
        # 步骤3: 旧密码不能登录
        old_auth_result = UserService.authenticate_user(
            db=unit_test_db,
            username="changeuser",
            password="OldPassword123"
        )
        assert old_auth_result is None
        
        # 步骤4: 最终验证
        final_check = service.get_by_id(created.id)
        assert final_check.status == "processed"
        
    def test_user_auth_error_handling_flow(self, unit_test_db: Session):
        """测试user_auth错误处理流程"""
        service = User_AuthService(unit_test_db)
        
        # 测试无效数据处理
        with pytest.raises((ValueError, TypeError)):
            service.create({"invalid": "data"})
            
        # 测试不存在ID处理
        result = service.get_by_id(99999)
        assert result is None
        
        # 测试删除不存在项目
        delete_result = service.delete(99999)
        assert delete_result is False
        
    @pytest.mark.parametrize("test_scenario,expected_result", [
        ("valid_create", True),
        ("valid_update", True),
        ("valid_delete", True),
    ])
    def test_user_auth_scenarios(self, test_scenario, expected_result, unit_test_db: Session):
        """参数化测试user_auth场景"""
        service = User_AuthService(unit_test_db)
        
        if test_scenario == "valid_create":
            result = service.create(self.user_auth_data)
            assert (result is not None) == expected_result
            
        elif test_scenario == "valid_update":
            created = service.create(self.user_auth_data)
            result = service.update(created.id, {"status": "updated"})
            assert (result is not None) == expected_result
            
        elif test_scenario == "valid_delete":
            created = service.create(self.user_auth_data)
            result = service.delete(created.id)
            assert result == expected_result
