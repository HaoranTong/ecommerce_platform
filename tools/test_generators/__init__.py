"""
测试生成器模块包 - 重构版 v3.0

功能: 提供模块化测试代码自动生成功能，支持完整的五层测试架构
使用方法: 通过主生成器 generate_test_template.py 调用各专业生成器
使用场景: 电商平台模块测试代码自动化生成，提升测试覆盖率和标准化

架构说明:
核心模块:
- config/: 配置管理（test_generator_config.json + ConfigLoader）
- core/: 数据模型定义（FieldInfo, ModelInfo, RepositoryInfo等）

生成器:
- factories/: Factory Boy工厂生成器
- unit/: 单元测试生成器（Repository/Model/Service/Standalone）
- integration/: 集成测试生成器
- APITestGenerator: API端点测试生成器
- E2ETestGenerator: 端到端测试生成器
- SecurityTestGenerator: 安全测试生成器
- PerformanceTestGenerator: 性能测试生成器

工具模块:
- utils/: 通用工具（类型推断、测试数据生成、模板格式化）

版本: v3.0.0 (重构版)
作者: AI Assistant
创建时间: 2025-10-01
重构时间: 2025-10-08

使用方法:
    from tools.test_generators import APITestGenerator, ConfigLoader
    from tools.test_generators.core import ModelInfo, RepositoryInfo
"""

# 核心模块
from .config import ConfigLoader
from .core import (
    FieldInfo,
    RelationshipInfo,
    ModelInfo,
    RepositoryMethodInfo,
    RepositoryInfo,
    ModuleStructure
)

# 单元测试生成器
from .unit import (
    RepositoryTestGenerator,
    ModelTestGenerator,
    ServiceTestGenerator,
    StandaloneTestGenerator
)

# Factory生成器
from .factories import FactoryGenerator

# 集成测试生成器
from .integration import IntegrationTestGenerator

# 已有的专项测试生成器
from .base_generator import BaseTestGenerator
from .api_test_generator import APITestGenerator
from .e2e_test_generator import E2ETestGenerator
from .security_test_generator import SecurityTestGenerator
from .performance_test_generator import PerformanceTestGenerator

__all__ = [
    # 配置和数据模型
    'ConfigLoader',
    'FieldInfo',
    'RelationshipInfo',
    'ModelInfo',
    'RepositoryMethodInfo',
    'RepositoryInfo',
    'ModuleStructure',
    
    # 单元测试生成器
    'RepositoryTestGenerator',
    'ModelTestGenerator',
    'ServiceTestGenerator',
    'StandaloneTestGenerator',
    
    # Factory生成器
    'FactoryGenerator',
    
    # 集成测试生成器
    'IntegrationTestGenerator',
    
    # 专项测试生成器
    'BaseTestGenerator',
    'APITestGenerator', 
    'E2ETestGenerator',
    'SecurityTestGenerator',
    'PerformanceTestGenerator'
]