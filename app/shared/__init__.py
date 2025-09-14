"""
共享组件模块

包含：
- 共享数据模型
- 共享Pydantic模式  
- 工具函数
- 统一异常处理
"""

# 只导出基础类，避免循环导入和表重复定义
from .base_models import Base, TimestampMixin, BaseModel