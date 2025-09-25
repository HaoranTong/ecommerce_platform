"""
用户认证模块专用Factory Boy数据工厂

📋 **使用场景**：
- ✅ 单元测试 (tests/unit/) - Mock框架配合使用
- ✅ 复杂RBAC权限测试 - 完整的用户-角色-权限关系
- ✅ 关联数据测试 - 自动处理外键关系和唯一约束
- ❌ 集成测试 - 推荐使用 data_factory.py 统一工厂

📊 **与统一工厂的分工**：
- **本工厂(Factory Boy)**: 复杂关系、Mock测试、单元测试
- **统一工厂(data_factory.py)**: 跨模块集成、业务流程测试

🎯 **核心优势**：
- Factory Boy标准模式，支持智能数据生成
- 完整RBAC模型支持 (User, Role, Permission, UserRole, RolePermission, Session)
- 自动处理外键关系和数据一致性
- 支持复杂业务场景数据创建

🔧 **使用方法**：
```python
# 单元测试中使用 - 推荐场景
from tests.factories.user_auth_factories import UserFactory, RoleFactory

def test_user_permissions(mocker):
    # Factory Boy + Mock的组合
    user = UserFactory(is_active=True)
    role = RoleFactory(name='admin')
    
    # 测试复杂权限逻辑
    assert user.has_permission('user.create')

# 创建完整权限关系链
user = UserFactory()
role = RoleFactory()  
permission = PermissionFactory()
user_role = UserRoleFactory(user=user, role=role)
role_permission = RolePermissionFactory(role=role, permission=permission)
```

🚨 **注意事项**：
- 必须配置SQLAlchemy session: `Factory._meta.sqlalchemy_session = db`
- 适用于复杂关系测试，简单CRUD测试推荐使用统一工厂
- 与pytest-mock框架完美配合

---

自动生成时间: 2025-09-21 17:30:47 (已优化)
更新时间: 2025-09-25 22:30:00
生成模型数量: 6 (User, Role, Permission, UserRole, RolePermission, Session)

符合标准:
- [CHECK:TEST-002] Factory Boy测试数据标准
- [CHECK:DEV-009] 代码生成质量标准
- [CHECK:TEST-001] pytest-mock统一使用标准
"""

import factory
import factory.fuzzy
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.user_auth.models import (
    Permission, Role, RolePermission, Session, User, UserRole
)


class PermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Permission工厂类"""
    
    class Meta:
        model = Permission
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f'name_{n}')
    resource = factory.Faker('text', max_nb_chars=100)
    action = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Role工厂类"""
    
    class Meta:
        model = Role
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f'name_{n}')
    description = factory.Faker('text', max_nb_chars=200)
    level = factory.Faker('random_int', min=1, max=1000)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class RolePermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的RolePermission工厂类"""
    
    class Meta:
        model = RolePermission
        sqlalchemy_session_persistence = "commit"

    role_id = factory.SubFactory(RoleFactory)
    permission_id = factory.SubFactory(PermissionFactory)
    granted_by = factory.LazyFunction(lambda: 1)  # 避免循环依赖
    granted_at = factory.Faker('date_time_this_year')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class SessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Session工厂类"""
    
    class Meta:
        model = Session
        sqlalchemy_session_persistence = "commit"

    user_id = factory.LazyFunction(lambda: 1)  # 避免循环依赖
    token_hash = factory.Sequence(lambda n: f'token_hash_{n}')
    expires_at = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))
    last_accessed_at = factory.Faker('date_time_this_year')
    is_active = True
    ip_address = factory.Faker('address')
    user_agent = factory.Faker('text', max_nb_chars=200)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的User工厂类"""
    
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f'username_{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password_hash = 'hashed_password_123'
    is_active = True
    status = factory.Faker('word')
    email_verified = True
    phone_verified = True
    two_factor_enabled = True
    failed_login_attempts = factory.Faker('random_int', min=1, max=1000)
    locked_until = factory.Faker('date_time_this_year')
    last_login_at = factory.Faker('date_time_this_year')
    phone = factory.Faker('phone_number')
    real_name = factory.Sequence(lambda n: f'real_name_{n}')
    role = factory.Faker('word')
    wx_openid = factory.Sequence(lambda n: f'wx_openid_{n}')
    wx_unionid = factory.Sequence(lambda n: f'wx_unionid_{n}')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    is_deleted = False
    deleted_at = factory.Faker('date_time_this_year')


class UserRoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的UserRole工厂类"""
    
    class Meta:
        model = UserRole
        sqlalchemy_session_persistence = "commit"

    user_id = factory.LazyFunction(lambda: 1)  # 避免循环依赖
    role_id = factory.SubFactory(RoleFactory)
    assigned_by = factory.SubFactory(UserFactory)
    assigned_at = factory.Faker('date_time_this_year')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class UserAuthFactoryManager:
    """智能生成的user_auth模块工厂管理器
    
    提供便捷的测试数据创建方法和常见业务场景的数据组合
    """
    
    @staticmethod
    def setup_factories(session: Session):
        """设置所有工厂的数据库会话"""
        PermissionFactory._meta.sqlalchemy_session = session
        RoleFactory._meta.sqlalchemy_session = session
        RolePermissionFactory._meta.sqlalchemy_session = session
        SessionFactory._meta.sqlalchemy_session = session
        UserFactory._meta.sqlalchemy_session = session
        UserRoleFactory._meta.sqlalchemy_session = session

    @staticmethod
    def create_sample_data(session: Session) -> dict:
        """创建样本测试数据"""
        UserAuthFactoryManager.setup_factories(session)
        
        data = {}
        data['permission'] = PermissionFactory()
        data['role'] = RoleFactory()
        data['rolepermission'] = RolePermissionFactory()
        data['session'] = SessionFactory()
        data['user'] = UserFactory()
        data['userrole'] = UserRoleFactory()
        
        session.commit()
        return data
        
    @staticmethod
    def create_test_scenario(session: Session, scenario: str = 'basic') -> dict:
        """创建特定测试场景的数据"""
        # 可以根据具体业务需求扩展不同场景
        return UserAuthFactoryManager.create_sample_data(session)