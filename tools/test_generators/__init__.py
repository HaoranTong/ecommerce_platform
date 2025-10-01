"""
测试生成器模块包

功能: 提供模块化测试代码自动生成功能，支持4种专业化测试类型
使用方法: 通过主生成器 generate_test_template.py 调用各专业生成器
使用场景: 电商平台模块测试代码自动化生成，提升测试覆盖率和标准化

架构说明:
- BaseTestGenerator: 基础生成器，提供共享功能
- APITestGenerator: API端点测试生成器
- E2ETestGenerator: 端到端测试生成器 
- SecurityTestGenerator: 安全测试生成器
- PerformanceTestGenerator: 性能测试生成器

版本: v1.0.0
作者: AI Assistant
创建时间: 2025-10-01
"""

使用方法:
    from tools.test_generators.api_test_generator import APITestGenerator
    from tools.test_generators.security_test_generator import SecurityTestGenerator
"""

from .base_generator import BaseTestGenerator
from .api_test_generator import APITestGenerator
from .e2e_test_generator import E2ETestGenerator
from .security_test_generator import SecurityTestGenerator
from .performance_test_generator import PerformanceTestGenerator

__all__ = [
    'BaseTestGenerator',
    'APITestGenerator', 
    'E2ETestGenerator',
    'SecurityTestGenerator',
    'PerformanceTestGenerator'
]