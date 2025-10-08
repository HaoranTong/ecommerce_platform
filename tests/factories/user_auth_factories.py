"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/factories/user_auth_factories.py
生成时间: 2025-10-08 14:53:06
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
    
)


class UserAuthFactoryManager:
    """智能生成的user_auth模块工厂管理器
    
    提供便捷的测试数据创建方法和常见业务场景的数据组合
    
    双工厂模式中的Factory Boy工厂管理器：
    - 适用于单元测试(test_services/、*_standalone.py)
    - 轻量级内存创建，不依赖真实数据库连接
    - 智能处理外键依赖，避免FOREIGN KEY constraint failed
    
    关键方法：
    - setup_factories(): 设置数据库会话
    - create_sample_data(): 按依赖顺序创建完整测试数据集
    - create_test_scenario(): 创建特定业务场景的数据
    """
    
    @staticmethod
    def setup_factories(session: Session):
        """设置所有工厂的数据库会话
        
        重要说明：
        - 必须在创建Factory实例之前调用
        - 确保所有Factory使用相同的数据库会话
        - 支持事务回滚和数据隔离
        """

    @staticmethod
    def create_sample_data(session: Session) -> dict:
        """创建样本测试数据 - 按依赖顺序创建避免外键约束失败
        
        核心算法说明：
        1. 使用_sort_models_by_dependencies()的拓扑排序结果
        2. 按依赖顺序逐个创建Factory实例
        3. 确保被依赖模型(如User)在依赖模型(如RolePermission)之前创建
        
        解决的关键问题：
        - FOREIGN KEY constraint failed错误
        - 例如：RolePermission.granted_by引用User.id，必须先创建User
        
        返回结果：
        - dict: 包含所有创建的模型实例，key为模型名小写
        - 可以通过data['user']、data['role']等方式访问
        
        使用示例：
        >>> sample_data = factory_manager.create_sample_data(unit_test_db)
        >>> user = sample_data['user']  # 获取创建的User实例
        >>> role = sample_data['role']  # 获取创建的Role实例
        """
        UserAuthFactoryManager.setup_factories(session)
        
        data = {}
        
        session.commit()  # 提交所有创建的数据
        return data
        
    @staticmethod
    def create_test_scenario(session: Session, scenario: str = 'basic') -> dict:
        """创建特定测试场景的数据
        
        扩展点说明：
        - 目前默认调用create_sample_data()
        - 未来可以根据scenario参数创建不同的业务场景
        - 例如：'admin_user'、'guest_user'、'complex_permissions'等
        """
        # 可以根据具体业务需求扩展不同场景
        return UserAuthFactoryManager.create_sample_data(session)