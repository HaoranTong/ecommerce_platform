"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/factories/user_auth_factories.py
生成时间: 2025-10-04 11:06:33
生成工具: tools/generate_test_template.py v2.0
状态: GENERATED - 需要经过代码审查和测试验证

说明: 此文件已生成到正式目录，请进行代码审查和测试验证。
     审查通过后即可直接用于项目测试。
     
流程: 生成 -> 审查 -> 验证 -> 提交版本控制
"""


import factory
import factory.fuzzy
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

# 处理表重定义警告的配置
import warnings
warnings.filterwarnings('ignore', message='.*declarative base.*')
warnings.filterwarnings('ignore', message='.*Table.*already defined.*')

from app.modules.user_auth.models import (
    Permission, Role, RolePermission, Session, User, UserRole
)


class PermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Permission工厂类"""
    
    class Meta:
        model = Permission
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(Permission, "name") else None

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
        sqlalchemy_get_or_create = ("name",) if hasattr(Role, "name") else None

    name = factory.Sequence(lambda n: f'name_{n}')
    description = factory.Faker('text', max_nb_chars=200)
    level = factory.Faker('random_int', min=1, max=1000)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的User工厂类"""
    
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(User, "name") else None

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


class RolePermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的RolePermission工厂类"""
    
    class Meta:
        model = RolePermission
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(RolePermission, "name") else None

    role_id = factory.Sequence(lambda n: n + 1)
    permission_id = factory.Sequence(lambda n: n + 1)
    granted_by = factory.Sequence(lambda n: n + 1)
    granted_at = factory.Faker('date_time_this_year')
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class SessionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的Session工厂类"""
    
    class Meta:
        model = Session
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(Session, "name") else None

    user_id = factory.Sequence(lambda n: n + 1)
    token_hash = factory.Sequence(lambda n: f'token_hash_{n}')
    expires_at = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))
    last_accessed_at = factory.Faker('date_time_this_year')
    is_active = True
    ip_address = factory.Faker('address')
    user_agent = factory.Faker('text', max_nb_chars=200)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class UserRoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的UserRole工厂类"""
    
    class Meta:
        model = UserRole
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_get_or_create = ("name",) if hasattr(UserRole, "name") else None

    user_id = factory.Sequence(lambda n: n + 1)
    role_id = factory.Sequence(lambda n: n + 1)
    assigned_by = factory.Sequence(lambda n: n + 1)
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