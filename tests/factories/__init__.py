"""
测试数据工厂模块初始化

统一导入所有Factory类和管理器，提供标准化访问接口
符合[CHECK:TEST-002]测试数据工厂标准
"""

# 从user_auth_factories导入所有工厂类
from .user_auth_factories import (
    UserFactory,
    RoleFactory, 
    PermissionFactory,
    RolePermissionFactory,
    SessionFactory,
    UserRoleFactory,
    UserAuthFactoryManager
)

# 从test_data_factory导入通用工厂
from .test_data_factory import StandardTestDataFactory

# 为兼容性提供别名映射
User_AuthFactory = UserAuthFactoryManager  # 别名映射
TestDataFactory = StandardTestDataFactory   # 别名映射

# 导出所有工厂类
__all__ = [
    'UserFactory',
    'RoleFactory', 
    'PermissionFactory',
    'RolePermissionFactory',
    'SessionFactory',
    'UserRoleFactory',
    'UserAuthFactoryManager',
    'User_AuthFactory',  # 别名
    'StandardTestDataFactory',
    'TestDataFactory'   # 别名
]