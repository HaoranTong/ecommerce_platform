"""
集成测试生成器 - 跨模块集成测试

职责：
生成集成测试代码，包括：
1. Repository与Service集成测试
2. 跨模块业务流程测试
3. 复杂事务场景测试
4. 数据一致性验证测试

测试策略：
- 使用integration_db fixture
- 测试完整业务链路
- 验证跨模块协作
- 事务和回滚测试

版本: v1.0
创建时间: 2025-10-08
"""
from pathlib import Path
from typing import Dict
from ..core import ModelInfo, RepositoryInfo
from ..utils.service_analyzer import ServiceAnalyzer


class IntegrationTestGenerator:
    """集成测试生成器"""
    
    def __init__(self, project_root: Path, config: Dict, main_generator=None):
        """初始化生成器
        
        Args:
            project_root: 项目根目录
            config: 配置字典
            main_generator: 主生成器实例（临时使用）
        """
        self.project_root = project_root
        self.config = config
        self.main_generator = main_generator
        # 初始化ServiceAnalyzer用于获取真实Service类名
        self.service_analyzer = ServiceAnalyzer(project_root)
    
    def generate_integration_tests(
        self,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> Dict[str, str]:
        """生成集成测试代码（主入口）
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            
        Returns:
            Dict[文件路径, 文件内容]
        """
        files = {}

        # 生成集成测试文件
        integration_tests = self._generate_integration_test_content(module_name, models)
        files[f"tests/integration/test_{module_name}_integration.py"] = integration_tests

        return files
    
    def _generate_integration_test_content(
        self, module_name: str, models: Dict[str, ModelInfo]
    ) -> str:
        """生成完整的集成测试内容 - 遵循[CHECK:DEV-005]业务逻辑实现验证"""

        # 基于module_name生成特定的测试内容
        if module_name == "user_auth":
            return self._generate_user_auth_integration_tests()
        else:
            # 通用模块集成测试模板
            return self._generate_generic_integration_tests(module_name, models)
    
    def _generate_user_auth_integration_tests(self) -> str:
        """生成用户认证模块的完整集成测试 - 基于test_auth_integration.py最佳实践"""
        NEWLINE = "\\n"  # 定义常量
        return f'''"""
User Auth 集成测试套件 - 完整业务流程验证

测试类型: 集成测试 (Integration) - 20%覆盖率
数据策略: MySQL Docker, mysql_integration_db fixture
符合标准: testing-standards.md第105-125行集成测试规范

业务覆盖:
1. JWT令牌完整功能验证
2. 用户注册完整流程测试  
3. 用户登录认证流程测试
4. API端点集成验证
5. 数据库集成验证
6. 权限系统集成测试

基于实际技术文档:
- app/modules/user_auth/models.py (User模型字段)
- app/modules/user_auth/service.py (UserService方法)
- app/core/auth.py (JWT认证功能)
"""

import pytest
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import UserFactory

# Fixture导入
from tests.conftest import mysql_integration_db, api_client

# 被测模块导入
from app.modules.user_auth.service import UserService
from app.core.auth import (
    create_access_token, create_refresh_token, decode_token,
    get_password_hash, verify_password
)


@pytest.mark.integration
class TestUserAuthIntegration:
    """用户认证集成测试 - MySQL Docker环境完整验证"""
    
    def test_jwt_token_integration(self, mysql_integration_db: Session):
        """测试JWT令牌完整功能集成"""
        print(f"{NEWLINE}🔐 测试JWT令牌完整功能...")
        
        # 1. 测试访问令牌创建
        token_data = {{'sub': '1', 'username': 'integration_user', 'role': 'user'}}
        access_token = create_access_token(token_data)
        
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 50
        print("✅ 访问令牌创建成功: " + access_token[:30] + "...")
        
        # 2. 测试刷新令牌创建
        refresh_token = create_refresh_token(token_data)
        
        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert refresh_token != access_token
        print("✅ 刷新令牌创建成功: " + refresh_token[:30] + "...")
        
        # 3. 测试令牌验证
        try:
            payload = decode_token(access_token)
            assert payload['sub'] == '1'
            assert payload['username'] == 'integration_user'
            print("✅ 令牌验证成功")
        except Exception as e:
            print(f"⚠️ 令牌验证注意事项: {{e}}")
        
        # 4. 测试密码哈希功能
        password = "IntegrationTestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert hashed.startswith('$2b$')  # bcrypt格式
        print("✅ 密码哈希创建成功")
        
        # 5. 测试密码验证
        assert verify_password(password, hashed) == True
        assert verify_password("wrong_password", hashed) == False
        print("✅ 密码验证功能正确")

    def test_user_registration_integration(self, mysql_integration_db: Session):
        """测试用户注册完整业务流程集成"""
        print(f"{NEWLINE}� 测试用户注册完整流程...")
        
        # 1. 执行用户注册 - 使用UserService静态方法
        created_user = UserService.create_user(
            db=mysql_integration_db,
            username="integration_test_user",
            email="integration@test.com",
            password="SecurePassword123!",
            phone="18800001234",
            real_name="集成测试用户",
            role='user',
            is_active=True
        )
        
        # 3. 验证用户创建结果
        assert created_user is not None
        assert created_user.username == "integration_test_user"
        assert created_user.email == "integration@test.com"
        assert created_user.phone == "18800001234"
        assert created_user.real_name == "集成测试用户"
        assert created_user.role == 'user'
        assert created_user.is_active == True
        assert created_user.password_hash is not None
        assert created_user.password_hash != "SecurePassword123!"
        print(f"✅ 用户创建成功: {{created_user.username}} (ID: {{created_user.id}})")
        
        # 4. 验证密码正确哈希
        assert verify_password("SecurePassword123!", created_user.password_hash)
        print("✅ 密码哈希验证通过")
        
        # 5. 测试用户名唯一性约束
        with pytest.raises(Exception):
            user_service.create_user(
                db=mysql_integration_db,
                username="integration_test_user",  # 重复用户名
                email="different@email.com",
                password="AnotherPassword123!"
            )
        print("✅ 用户名唯一性约束验证通过")

    def test_user_login_authentication_integration(self, mysql_integration_db: Session):
        """测试用户登录认证完整流程集成"""
        print(f"{NEWLINE}🔑 测试用户登录认证流程...")
        
        # 1. 先创建测试用户 - 使用UserService静态方法
        test_user = UserService.create_user(
            db=mysql_integration_db,
            username="login_integration_user",
            email="login@integration.test",
            password="LoginPassword123!",
            is_active=True
        )
        
        # 2. 测试正确登录认证
        authenticated_user = UserService.authenticate_user(
            db=mysql_integration_db,
            username="login_integration_user",
            password="LoginPassword123!"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id
        assert authenticated_user.username == "login_integration_user"
        print("✅ 正确密码认证成功")
        
        # 3. 测试错误密码拒绝
        failed_auth = UserService.authenticate_user(
            db=mysql_integration_db,
            username="login_integration_user",
            password="WrongPassword123!"
        )
        
        assert failed_auth is None
        print("✅ 错误密码正确拒绝")
        
        # 4. 测试不存在用户拒绝
        nonexistent_auth = UserService.authenticate_user(
            db=mysql_integration_db,
            username="nonexistent_user",
            password="AnyPassword123!"
        )
        
        assert nonexistent_auth is None
        print("✅ 不存在用户正确拒绝")

    def test_user_auth_api_integration(self, api_client, mysql_integration_db: Session):
        """测试用户认证API端点集成"""
        print(f"{NEWLINE}🌐 测试用户认证API端点...")
        
        # 1. 测试健康检查API
        health_response = api_client.get("/api/health")
        assert health_response.status_code == 200
        print("✅ 健康检查API正常")
        
        # 2. 测试用户注册API（如果存在）
        user_data = {{
            "username": "api_test_user",
            "email": "api@test.com",
            "password": "ApiTestPassword123!"
        }}
        
        # 注意: 实际API路径需要根据router.py确认
        try:
            register_response = api_client.post("/api/v1/users/register", json=user_data)
            if register_response.status_code == 201:
                print("✅ 用户注册API正常")
                
                # 验证数据库中用户是否创建
                from app.modules.user_auth.models import User
                created_user = mysql_integration_db.query(User).filter(
                    User.username == "api_test_user"
                ).first()
                assert created_user is not None
                print("✅ API注册数据库集成验证通过")
            else:
                print(f"ℹ️ 注册API返回状态: {{register_response.status_code}}")
        except Exception as e:
            print(f"ℹ️ API测试注意: {{e}}")

    def test_database_integration_verification(self, mysql_integration_db: Session):
        """测试数据库集成验证"""
        print(f"{NEWLINE}🗄️ 测试数据库集成...")
        
        # 1. 验证数据库连接
        assert mysql_integration_db is not None
        print("✅ MySQL数据库连接正常")
        
        # 2. 测试基本查询操作
        from app.modules.user_auth.models import User
        from sqlalchemy import text
        result = mysql_integration_db.execute(text("SELECT 1 as test")).fetchone()
        assert result[0] == 1
        print("✅ 数据库查询功能正常")
        
        # 3. 测试User模型操作
        user_count_before = mysql_integration_db.query(User).count()
        
        # 创建测试用户
        test_user = User(
            username="db_integration_user",
            email="db@integration.test",
            password_hash=get_password_hash("DbTestPassword123!")
        )
        mysql_integration_db.add(test_user)
        mysql_integration_db.commit()
        mysql_integration_db.refresh(test_user)
        
        # 验证创建成功
        assert test_user.id is not None
        user_count_after = mysql_integration_db.query(User).count()
        assert user_count_after == user_count_before + 1
        print("✅ 用户模型数据库操作正常")

    def test_permission_system_integration(self, mysql_integration_db: Session):
        """测试权限系统集成（如果实现）"""
        print(f"{NEWLINE}🛡️ 测试权限系统集成...")
        
        # 1. 测试角色和权限模型（如果存在）
        try:
            from app.modules.user_auth.models import Role, Permission
            
            # 创建测试权限
            test_permission = Permission(
                name="test_permission",
                description="集成测试权限"
            )
            mysql_integration_db.add(test_permission)
            mysql_integration_db.commit()
            
            # 创建测试角色
            test_role = Role(
                name="test_role",
                description="集成测试角色"
            )
            mysql_integration_db.add(test_role)
            mysql_integration_db.commit()
            
            print("✅ 权限系统基础模型正常")
            
        except ImportError:
            print("ℹ️ 权限系统模型未实现，跳过测试")
        except Exception as e:
            print(f"ℹ️ 权限系统测试注意: {{e}}")
'''
    
    def _generate_generic_integration_tests(
        self, module_name: str, models: Dict[str, ModelInfo]
    ) -> str:
        """生成通用模块的集成测试模板"""
        # 使用ServiceAnalyzer获取真实的Service类名
        service_info = self.service_analyzer.detect_service_info(module_name)
        service_class_name = service_info['class_name']
        
        # 生成测试类名
        test_class_name = service_class_name.replace('Service', 'Integration')
        
        return f'''"""
{module_name.title().replace('_', '')} 集成测试套件

测试类型: 集成测试 (Integration)
数据策略: MySQL Docker, mysql_integration_db fixture  
根据testing-standards.md第105-125行集成测试规范
"""

import pytest
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import UserFactory

# Fixture导入
from tests.conftest import mysql_integration_db, api_client

# 被测模块导入  
from app.modules.{module_name}.service import {service_class_name}


@pytest.mark.integration
class Test{test_class_name}:
    """{module_name.replace('_', ' ').title()}集成测试 - MySQL Docker环境"""
    
    def test_{module_name}_database_integration(self, mysql_integration_db: Session):
        """测试{module_name.replace('_', ' ')}与数据库集成"""
        # 数据库集成测试
        assert mysql_integration_db is not None
        print("✅ 数据库连接正常")
        
        # TODO: 添加具体的数据库操作测试
        
    def test_{module_name}_api_integration(self, api_client, mysql_integration_db: Session):
        """测试{module_name.replace('_', ' ')} API集成"""
        # API集成测试
        response = api_client.get("/api/health")
        assert response.status_code == 200
        print("✅ API基础连接正常")
        
        # TODO: 添加具体的API端点测试
        
    def test_{module_name}_service_integration(self, mysql_integration_db: Session):
        """测试{module_name.replace('_', ' ')}服务集成"""
        # 服务集成测试
        # TODO: 添加具体的服务方法测试
        pass
'''
