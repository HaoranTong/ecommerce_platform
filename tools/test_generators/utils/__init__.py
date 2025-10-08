"""
通用工具模块 - 测试代码生成器的基础设施

该模块提供测试代码生成过程中所需的所有分析器、验证器、工具类等基础组件。
这些组件被各个测试生成器共享使用，提供代码分析、质量验证、文件写入等核心功能。

模块组成:
- 分析器 (Analyzers):
  * ModelAnalyzer: SQLAlchemy模型智能分析（AST+运行时双重分析）
  * RepositoryAnalyzer: Repository层方法分析和分类
  * ServiceAnalyzer: Service类检测和实例化模式识别

- 验证器 (Validators):
  * EnvironmentValidator: 测试环境配置完整性检查
  * PytestChecker: Pytest兼容性和依赖完整性验证
  * ValidationReporter: 质量验证结果汇总和报告生成

- 工具类 (Utilities):
  * TestUtils: 测试代码生成通用辅助方法（实体创建、测试值生成等）
  * TestFileWriter: 测试文件持久化和目录结构管理

架构设计:
- 单一职责: 每个类专注于一个特定的分析或工具功能
- 依赖注入: 通过构造函数注入配置，支持测试和复用
- 无状态设计: 工具类使用静态方法，分析器保持轻量级状态

使用示例:
    from tools.test_generators.utils import (
        ModelAnalyzer,
        RepositoryAnalyzer,
        ValidationReporter
    )
    from pathlib import Path
    
    # 初始化分析器
    model_analyzer = ModelAnalyzer(project_root=Path.cwd())
    repo_analyzer = RepositoryAnalyzer(project_root=Path.cwd())
    
    # 分析模块
    models = model_analyzer.analyze_module_models("user_auth")
    repositories = repo_analyzer.analyze_module_repositories("user_auth")
    
    # 验证生成的测试
    reporter = ValidationReporter()
    results = reporter.validate_generated_tests("user_auth")

注意事项:
- 所有分析器需要项目根目录（project_root）进行初始化
- 分析器会导入目标模块代码，确保模块可正常导入
- 验证器需要pytest已安装并可用

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-08
Version: 1.0.0
"""

from .model_analyzer import ModelAnalyzer
from .repository_analyzer import RepositoryAnalyzer
from .service_analyzer import ServiceAnalyzer
from .file_writer import TestFileWriter
from .validation_reporter import ValidationReporter
from .pytest_checker import PytestChecker
from .test_utils import TestUtils
from .environment_validator import EnvironmentValidator

__all__ = [
    'ModelAnalyzer',
    'RepositoryAnalyzer',
    'ServiceAnalyzer',
    'TestFileWriter',
    'ValidationReporter',
    'PytestChecker',
    'TestUtils',
    'EnvironmentValidator'
]
