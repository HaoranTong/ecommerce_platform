"""
测试数据工厂模块初始化

统一导入所有Factory类和管理器，提供标准化访问接口
符合[CHECK:TEST-002]测试数据工厂标准
"""

# 从data_factory导入通用工厂
from .data_factory import StandardTestDataFactory

# 为兼容性提供别名映射
TestDataFactory = StandardTestDataFactory  # 别名映射

# 导出所有工厂类
__all__ = [
    "StandardTestDataFactory",
    "TestDataFactory",  # 别名
]
