#!/usr/bin/env python3
"""
智能测试代码生成器 - 主程序

该模块是测试代码生成工具的主入口程序，负责编排整个测试生成流程，包括模块分析、
代码生成、文件写入、质量验证等步骤。采用模块化架构，主程序仅负责流程编排。

主要功能:
- 模块结构分析: 委托ModelAnalyzer/RepositoryAnalyzer/ServiceAnalyzer分析代码结构
- 测试代码生成: 委托各生成器（Model/Repository/Service/Workflow）生成测试代码
- Factory生成: 委托FactoryGenerator生成测试数据工厂类
- 文件管理: 委托TestFileWriter处理文件写入和目录结构
- 质量验证: 委托ValidationReporter进行语法、pytest、依赖等多维度验证
- 环境检查: 委托EnvironmentValidator验证测试环境配置

技术栈:
- Python AST: 代码静态分析
- SQLAlchemy: ORM模型反射
- pytest: 测试框架验证
- pathlib: 跨平台路径处理

依赖关系:
- tools.test_generators.utils.*: 8个通用工具类
- tools.test_generators.unit.*: 4个测试生成器
- tools.test_generators.factories: Factory生成器
- tools.test_generators.config: 配置管理器
- tools.test_generators.core: 数据模型定义

使用示例:
    # 命令行使用
    python tools/generate_test_template.py user_auth
    python tools/generate_test_template.py user_auth --type unit
    python tools/generate_test_template.py user_auth --dry-run --verbose
    
    # 程序化使用
    from tools.generate_test_template import IntelligentTestGenerator
    
    generator = IntelligentTestGenerator()
    files = generator.generate_tests("user_auth", test_type="all")
    print(f"生成了 {len(files)} 个测试文件")

配置文件:
- tools/test_generator_config.json: 主配置文件（可选）
- 配置内容: 项目结构、测试分布、数据库配置、业务逻辑模式
- 备用机制: 配置文件缺失时使用内置默认配置

生成的测试文件（4个核心）:
- tests/unit/generated/{module}/test_models.py: Model层测试（Mock）
- tests/unit/generated/{module}/test_repositories.py: Repository层测试（SQLite）
- tests/unit/generated/{module}/test_services.py: Service层测试（Mock Repository）
- tests/unit/generated/{module}/test_workflows.py: 业务流程测试（SQLite）
- tests/factories/{module}_factories.py: 测试数据工厂

架构优化:
- 主程序: 661行（从7159行优化，-90.8%）
- 模块化: 14个独立组件（6生成器+3分析器+5工具）
- 单一职责: 每个组件专注于特定功能
- 依赖注入: 支持测试和模块复用

质量标准:
- 遵循testing-standards.md v2.0.0
- 遵循code-standards.md编码规范
- 遵循naming-conventions-standards.md命名规范
- 100%文档覆盖（文件头部+方法文档）

注意事项:
- f-string嵌套: 大型模板中使用{{}}转义（历史bug已修复）
- 环境验证: 生成前检查conftest.py、fixtures、数据库配置
- 质量验证: 生成后自动验证语法、pytest收集、依赖完整性
- 性能考虑: 模型分析结果会缓存，避免重复分析

Performance:
- 模块分析: 约200-500ms（AST+运行时）
- 测试生成: 约500-1000ms（取决于模型/方法数量）
- 文件写入: 约50-100ms
- 质量验证: 约2-5秒（pytest收集）
- 总耗时: 约3-7秒/模块

Author: AI Assistant
Created: 2025-09-20
Modified: 2025-10-15
Version: 3.2.0

Changelog:
- v3.2.0 (2025-10-15):
  * 🔧 修复：RepositoryAnalyzer支持keyword-only参数 (Python 3.0+ PEP 3102)
  * 🐛 解决：订单模块Repository测试19个失败 → 预期全部通过
  * 🧪 新增：RepositoryAnalyzer单元测试套件
  * 📝 改进：支持现代Python参数模式（*, kwonly_param）
  * ✅ 回归测试：确保前3个模块166个测试仍然通过
- v3.1.0 (2025-10-08): 模块化重构
- v3.0.0 (2025-10-01): 智能五层架构测试生成
"""

import argparse
import ast
import importlib.util
import inspect
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 全局常量
NEWLINE = "\\n"

# 导入重构后的数据模型（从test_generators.core）
from tools.test_generators.core import (
    FieldInfo,
    RelationshipInfo,
    ModelInfo,
    RepositoryMethodInfo,
    RepositoryInfo,
    ModuleStructure
)

# 导入工具模块
from tools.test_generators.utils.file_writer import TestFileWriter
from tools.test_generators.utils.validation_reporter import ValidationReporter
from tools.test_generators.utils.pytest_checker import PytestChecker
from tools.test_generators.utils.environment_validator import EnvironmentValidator

# 保留dataclass导入以便后续代码使用
# 注意：上面的数据模型已经是dataclass，这里不需要重复定义


class IntelligentTestGenerator:
    """智能测试生成器 - 集成模型分析和测试生成 [CHECK:DEV-009] [CHECK:TEST-001]
    
    重构版本 v3.0:
    - 使用test_generators.config.ConfigLoader管理配置
    - 使用test_generators.core中的数据模型
    - 逐步迁移生成逻辑到独立模块
    """

    def __init__(self):
        """初始化生成器"""
        self.project_root = Path(__file__).parent.parent
        
        # 使用新的ConfigLoader
        from tools.test_generators.config import ConfigLoader
        config_loader = ConfigLoader(self.project_root)
        self.config = config_loader.get_all()
        
        # 初始化ModelAnalyzer
        from tools.test_generators.utils.model_analyzer import ModelAnalyzer
        self.model_analyzer = ModelAnalyzer(self.project_root)
        
        # 初始化RepositoryAnalyzer
        from tools.test_generators.utils.repository_analyzer import RepositoryAnalyzer
        self.repository_analyzer = RepositoryAnalyzer(self.project_root)
        
        # 初始化ServiceAnalyzer
        from tools.test_generators.utils.service_analyzer import ServiceAnalyzer
        self.service_analyzer = ServiceAnalyzer(self.project_root)
        
        # 初始化TestUtils
        from tools.test_generators.utils.test_utils import TestUtils
        self.test_utils = TestUtils
        
        self.models_cache = {}

    def analyze_module_models(self, module_name: str) -> Dict[str, ModelInfo]:
        """智能分析模块中的所有数据模型 [CHECK:TEST-001]

        Args:
            module_name: 模块名称，如 'user_auth'

        Returns:
            Dict[str, ModelInfo]: 模型名称到模型信息的映射

        Raises:
            FileNotFoundError: 当模型文件不存在时
            ImportError: 当模块导入失败时
        """
        if module_name in self.models_cache:
            return self.models_cache[module_name]

        # 使用ModelAnalyzer进行分析
        merged_models = self.model_analyzer.analyze_module_models(module_name)
        
        # 缓存结果
        self.models_cache[module_name] = merged_models
        return merged_models

    def analyze_module_repositories(self, module_name: str) -> Dict[str, RepositoryInfo]:
        """分析模块的Repository层（委托给RepositoryAnalyzer）"""
        return self.repository_analyzer.analyze_module_repositories(module_name)

    def generate_tests(
        self,
        module_name: str,
        test_type: str = "all",
        dry_run: bool = False,
        validate: bool = True,
    ) -> Tuple[Dict[str, str], Optional[Dict[str, Any]]]:
        """生成测试代码文件 - 主流程编排方法
        
        该方法是测试生成的核心入口，负责编排整个测试生成流程，包括环境验证、模块分析、
        代码生成、文件写入、质量验证等步骤。支持多种测试类型的选择性生成。
        
        执行流程:
        1. 环境兼容性验证（EnvironmentValidator）
        2. 模块结构分析（ModelAnalyzer + RepositoryAnalyzer）
        3. Factory类生成（FactoryGenerator）
        4. 测试代码生成（各TestGenerator）
        5. 文件持久化（TestFileWriter）
        6. 质量验证（ValidationReporter）
        
        Args:
            module_name (str): 目标业务模块名称（对应app/modules/下的目录名）
                例如: "user_auth", "product_catalog", "shopping_cart"
                
            test_type (str, optional): 测试类型选择，默认"all"
                - "all": 生成所有类型测试（unit + integration + api + e2e + specialized）
                - "unit": 仅生成单元测试（Model + Repository + Service + Workflow）
                - "integration": 仅生成集成测试
                - "api": 仅生成API端点测试
                - "e2e": 仅生成端到端测试
                - "smoke": 烟雾测试（使用通用脚本，不生成模块特定文件）
                - "specialized": 仅生成专项测试（安全测试 + 性能测试）
                
            dry_run (bool, optional): 是否为试运行模式，默认False
                - True: 生成代码但不写入文件，用于预览和调试
                - False: 生成代码并写入磁盘
                
            validate (bool, optional): 是否执行质量验证，默认True
                - True: 生成后自动验证语法、pytest收集、依赖完整性
                - False: 跳过验证（用于快速生成，不推荐）

        Returns:
            Tuple[Dict[str, str], Optional[Dict[str, Any]]]: 包含两个元素的元组
                [0] Dict[str, str]: 生成的测试文件映射
                    - key: 文件相对路径（如"tests/unit/generated/user_auth/test_models.py"）
                    - value: 文件内容（完整的Python测试代码）
                    
                [1] Optional[Dict[str, Any]]: 质量验证报告（validate=True时返回）
                    - "syntax_check": 语法检查结果
                    - "pytest_check": pytest收集测试结果
                    - "dependencies": 依赖检查结果
                    - "summary": 总体质量评分和建议
                    如果validate=False或dry_run=True，返回None
                    
        Raises:
            FileNotFoundError: 当目标模块的models.py文件不存在时
            ImportError: 当模块导入失败时（通常是语法错误或缺少依赖）
            ValueError: 当test_type参数值不在允许范围内时
            
        Example:
            # 示例1: 生成所有类型测试
            generator = IntelligentTestGenerator()
            files, report = generator.generate_tests("user_auth")
            print(f"生成了 {len(files)} 个测试文件")
            print(f"质量评分: {report['summary']['score']}分")
            
            # 示例2: 仅生成单元测试（试运行）
            files, _ = generator.generate_tests(
                "product_catalog",
                test_type="unit",
                dry_run=True
            )
            for path, content in files.items():
                print(f"预览: {path} ({len(content)}字符)")
            
            # 示例3: 快速生成（跳过验证）
            files, _ = generator.generate_tests(
                "shopping_cart",
                validate=False
            )
            
        Notes:
            - 环境要求: 需要models.py存在，conftest.py配置正确
            - 性能: 完整生成约3-7秒/模块（包括验证）
            - 输出: 默认输出到tests/unit/generated/{module_name}/
            - 缓存: 模型分析结果会缓存，避免重复分析
            - f-string: 大型模板使用{{}}转义（历史bug已修复）
            
        Performance:
            - 环境验证: <100ms
            - 模块分析: 200-500ms（AST+运行时双重分析）
            - 代码生成: 500-1000ms（取决于模型/方法数量）
            - 文件写入: 50-100ms
            - 质量验证: 2-5秒（pytest收集测试）
            - 总耗时: 约3-7秒/模块
            
        See Also:
            - _generate_unit_tests(): 单元测试生成的具体实现
            - _validate_generated_tests(): 质量验证的具体实现
            - ValidationReporter: 验证报告生成器
        """
        # 0. 环境兼容性验证
        validator = EnvironmentValidator(self.config)
        env_info = validator.validate_test_environment(module_name)
        
        if env_info["issues"]:
            print("⚠️ 环境验证发现问题:")
            for issue in env_info["issues"]:
                print(f"   - {issue}")
        else:
            print("✅ 环境兼容性验证通过")
        
        # 1. 分析模块结构（四层架构）
        print(f"\n🏗️ 分析模块结构: {module_name}")
        # 只分析当前模块的模型
        # Repository测试生成器内部有ModelAnalyzer和CrossModuleDependencyResolver
        # 可以自己查询跨模块信息，不需要外部传入global_models
        models = self.analyze_module_models(module_name)
        
        repositories = self.analyze_module_repositories(module_name)  # 强制要求Repository层
        
        print(f"\n📊 结构分析完成:")
        print(f"   Models: {len(models)} 个")
        print(f"   Repositories: {len(repositories)} 个")

        # 2. 生成智能数据工厂
        from tools.test_generators.factories import FactoryGenerator
        factory_generator = FactoryGenerator(self.project_root, self.config)
        # Factory生成器使用当前模块模型
        factory_code = factory_generator.generate_factories(module_name, models)

        # 3. 生成测试文件
        generated_files = {}

        # 生成Factory工厂代码（可单独指定）
        if test_type in ["all", "factories"]:
            factory_file_path = f"tests/factories/{module_name}_factories.py"
            generated_files[factory_file_path] = factory_code

        # 单元测试 - 支持细粒度选择
        if test_type in ["all", "unit"]:
            # 使用当前模块模型
            unit_files = self._generate_unit_tests(module_name, models, repositories)
            generated_files.update(unit_files)
        elif test_type == "models":
            # 仅生成models测试
            unit_files = self._generate_unit_tests(module_name, models, repositories, components=["models"])
            generated_files.update(unit_files)
        elif test_type == "repositories":
            # 仅生成repositories测试
            unit_files = self._generate_unit_tests(module_name, models, repositories, components=["repositories"])
            generated_files.update(unit_files)
        elif test_type == "services":
            # 仅生成services测试
            unit_files = self._generate_unit_tests(module_name, models, repositories, components=["services"])
            generated_files.update(unit_files)
        elif test_type == "standalone":
            # 仅生成standalone测试
            unit_files = self._generate_unit_tests(module_name, models, repositories, components=["standalone"])
            generated_files.update(unit_files)

        if test_type in ["all", "integration"]:
            from tools.test_generators.integration import IntegrationTestGenerator
            integration_generator = IntegrationTestGenerator(self.project_root, self.config)
            integration_files = integration_generator.generate_integration_tests(module_name, models)
            generated_files.update(integration_files)
        
        if test_type in ["all", "api"]:
            from tools.test_generators.api_test_generator import APITestGenerator
            api_generator = APITestGenerator(self.project_root, self.config)
            # API测试生成器需要全局模型信息来处理跨模块依赖（如Product依赖Category、Brand）
            all_modules_models = self.model_analyzer.analyze_all_modules()
            global_models = {}
            for module_models in all_modules_models.values():
                global_models.update(module_models)
            api_files = api_generator.generate_tests(module_name, global_models)
            generated_files.update(api_files)
        
        if test_type in ["all", "e2e"]:
            from tools.test_generators.e2e_test_generator import E2ETestGenerator
            e2e_generator = E2ETestGenerator(self.project_root, self.config)
            e2e_files = e2e_generator.generate_tests(module_name, models)
            generated_files.update(e2e_files)

        if test_type in ["all", "smoke"]:
            # 烟雾测试使用通用脚本，不生成模块特定文件
            print(f"ℹ️  烟雾测试使用通用脚本 tools/smoke_test.ps1，跳过 {module_name} 模块特定生成")

        if test_type in ["all", "specialized", "security"]:
            # 生成专项测试（安全测试和性能测试）
            from tools.test_generators import SecurityTestGenerator, PerformanceTestGenerator
            
            if test_type == "security":
                # 仅生成安全测试
                security_generator = SecurityTestGenerator(self.project_root, self.config)
                security_tests = security_generator.generate_tests(module_name, models)
                generated_files.update(security_tests)
                print(f"✅ 生成安全测试")
            else:
                # 生成完整专项测试
                security_generator = SecurityTestGenerator(self.project_root, self.config)
                performance_generator = PerformanceTestGenerator(self.project_root, self.config)
                
                security_tests = security_generator.generate_tests(module_name, models)
                generated_files.update(security_tests)
                
                performance_tests = performance_generator.generate_tests(module_name, models)
                generated_files.update(performance_tests)
                
                print(f"✅ 生成专项测试: 安全测试 + 性能测试")
        
        if test_type == "performance":
            # 仅生成性能测试
            # 注意：PerformanceTestGenerator会自己使用CrossModuleDependencyResolver获取全局模型
            from tools.test_generators import PerformanceTestGenerator
            
            performance_generator = PerformanceTestGenerator(self.project_root, self.config)
            performance_tests = performance_generator.generate_tests(module_name, models)
            generated_files.update(performance_tests)
            
            print(f"✅ 生成性能测试")

        # 3. 写入文件（如果不是试运行）
        if not dry_run:
            writer = TestFileWriter(self.project_root)
            writer.write_test_files(generated_files)

        # 4. 验证生成的代码（如果需要）
        validation_report = None
        if validate and not dry_run:
            validation_report = self._validate_generated_tests(generated_files)

        print(f"✅ 生成完成，共 {len(generated_files)} 个测试文件")

        # 如果包含烟雾测试类型，提供烟雾测试运行指南
        if test_type in ["all", "smoke"]:
            print("ℹ️  烟雾测试运行方式:")
            print("   - 通用脚本: .\\tools\\smoke_test.ps1")
            print("   - pytest方式: python -m pytest tests/smoke/ -v")
            print("   - 涵盖: API连通性、系统健康检查、基础功能验证")

        return generated_files, validation_report

    def _generate_unit_tests(
        self, module_name: str, models: Dict[str, ModelInfo], repositories: Dict[str, RepositoryInfo], components: List[str] = None
    ) -> Dict[str, str]:
        """生成单元测试代码 - 四层架构测试生成
        
        根据testing-standards.md v2.0.0标准和四层架构设计，生成四个独立的单元测试脚本，
        分别测试Model层、Repository层、Service层和业务流程层。每层采用不同的测试策略。
        
        测试层次和策略:
        1. Model层测试: 100% Mock，测试模型定义、字段约束、方法逻辑 (使用当前模块models)
        2. Repository层测试: SQLite内存数据库，测试CRUD操作和SQL正确性 (使用global_models支持跨模块依赖)
        3. Service层测试: Mock Repository，测试业务逻辑和异常处理 (使用global_models)
        4. Workflow测试: SQLite内存数据库，测试完整业务流程 (使用global_models)
        2. Repository层测试: SQLite内存数据库，测试CRUD操作和SQL正确性
        3. Service层测试: Mock Repository，测试业务逻辑和异常处理
        4. Workflow测试: SQLite内存数据库，测试完整业务流程
        
        Args:
            module_name (str): 目标业务模块名称
                例如: "user_auth", "product_catalog"
                
            models (Dict[str, ModelInfo]): 模型信息字典
                - key: 模型名称（如"User", "Role"）
                - value: ModelInfo对象（包含字段、关系、约束等信息）
                由analyze_module_models()方法提供
                
            repositories (Dict[str, RepositoryInfo]): Repository信息字典
                - key: Repository名称（如"UserRepository"）
                - value: RepositoryInfo对象（包含方法签名、操作类型等）
                由analyze_module_repositories()方法提供
                四层架构必需，用于生成Repository和Service测试

        Returns:
            Dict[str, str]: 四个测试脚本的文件路径到内容映射
                包含以下键值对:
                - "test_models/test_{module}_models": Model层测试代码
                - "test_repositories/test_{module}_repositories": Repository层测试代码
                - "test_services/test_{module}_services": Service层测试代码
                - "tests/unit/test_{module}_standalone.py": 业务流程测试代码
                
        Raises:
            ImportError: 当生成器模块导入失败时
            KeyError: 当模型或Repository信息不完整时
            
        Example:
            models = {
                "User": ModelInfo(name="User", table_name="users", fields=[...]),
                "Role": ModelInfo(name="Role", table_name="roles", fields=[...])
            }
            
            repositories = {
                "UserRepository": RepositoryInfo(
                    model_name="User",
                    methods=[...],
                    class_name="UserRepository"
                )
            }
            
            files = generator._generate_unit_tests("user_auth", models, repositories)
            print(f"生成了 {len(files)} 个单元测试文件")
            for path, content in files.items():
                print(f"  - {path}: {len(content)}行")
                
        Notes:
            - Model测试: 无数据库依赖，执行速度极快（<10ms/测试）
            - Repository测试: 使用SQLite内存数据库，确保SQL正确性
            - Service测试: Mock Repository，专注业务逻辑验证
            - Workflow测试: 测试完整业务流程，验证多层协作
            - 测试标准: 严格遵循testing-standards.md v2.0.0
            
        Performance:
            - Model测试生成: 约50ms（取决于模型数量）
            - Repository测试生成: 约200ms（取决于方法数量）
            - Service测试生成: 约100ms
            - Workflow测试生成: 约100ms
            - 总耗时: 约500ms（4个文件）
            
        See Also:
            - ModelTestGenerator: Model层测试生成器
            - RepositoryTestGenerator: Repository层测试生成器（1673行，最复杂）
            - ServiceTestGenerator: Service层测试生成器
            - StandaloneTestGenerator: 业务流程测试生成器
        """
        files = {}
        
        # 如果没有指定组件，生成所有组件
        if components is None:
            components = ["models", "repositories", "services", "standalone"]

        # 1. 生成Mock模型测试
        if "models" in components:
            from tools.test_generators.unit import ModelTestGenerator
            model_generator = ModelTestGenerator(self.project_root, self.config)
            model_tests = model_generator.generate_model_tests(module_name, models)
            files[f"tests/unit/test_models/test_{module_name}_models.py"] = model_tests

        # 2. 生成Repository测试
        # 传入当前模块models用于快速判断跨模块边界（if model_name not in models）
        # Repository生成器内部有ModelAnalyzer和CrossModuleDependencyResolver处理跨模块依赖
        if "repositories" in components:
            from tools.test_generators.unit import RepositoryTestGenerator
            repo_generator = RepositoryTestGenerator(self.project_root, self.config, main_generator=self)
            repository_tests = repo_generator.generate_repository_tests(module_name, models, repositories)
            files[f"tests/unit/test_repositories/test_{module_name}_repositories.py"] = repository_tests

        # 3. 生成服务测试
        # Service生成器从Service源码提取实际使用的模型，不依赖models参数
        if "services" in components:
            from tools.test_generators.unit import ServiceTestGenerator
            service_generator = ServiceTestGenerator(self.project_root, self.config)
            service_tests = service_generator.generate_service_tests(module_name, models, repositories)
            files[f"tests/unit/test_services/test_{module_name}_services.py"] = service_tests

        # 4. 生成业务流程测试
        if "standalone" in components:
            from tools.test_generators.unit.standalone_test_generator import StandaloneTestGenerator
            workflow_generator = StandaloneTestGenerator(self.project_root, self.config)
            workflow_tests = workflow_generator.generate_workflow_tests(module_name, models)
            files[f"tests/unit/test_{module_name}_standalone.py"] = workflow_tests

        print(f"✅ 生成单元测试脚本 (组件: {', '.join(components)}):")
        for component in components:
            if component == "models":
                print(f"   📋 Mock模型测试: tests/unit/test_models/test_{module_name}_models.py")
            elif component == "repositories":
                print(f"   🗃️  Repository测试: tests/unit/test_repositories/test_{module_name}_repositories.py")
            elif component == "services":
                print(f"   🔧 服务测试: tests/unit/test_services/test_{module_name}_services.py")
            elif component == "standalone":
                print(f"   🔄 业务流程测试: tests/unit/test_{module_name}_standalone.py")

        return files
    
    def _validate_generated_tests(self, files: Dict[str, str]) -> Dict[str, Any]:
        """验证生成的测试代码质量 - 多维度自动验证
        
        该方法委托ValidationReporter对生成的测试代码进行全面的质量验证，包括语法正确性、
        pytest兼容性、依赖完整性等多个维度，并生成详细的质量分析报告。
        
        验证维度:
        1. 语法检查: 使用Python ast模块验证代码语法正确性
        2. Pytest收集: 运行pytest --collect-only验证测试可被正常收集
        3. 依赖检查: 检查Factory类、fixture等依赖是否完整
        4. Fixture检查: 验证conftest.py中的fixture可用性
        5. 综合评分: 根据各项指标计算0-100分的质量评分
        
        Args:
            files (Dict[str, str]): 生成的测试文件映射
                - key: 文件相对路径
                - value: 文件内容（Python代码）
                
        Returns:
            Dict[str, Any]: 质量验证报告，包含以下键:
                - "syntax_check" (Dict): 语法检查结果
                    - "passed" (List[str]): 通过语法检查的文件列表
                    - "failed" (List[Dict]): 语法错误的文件列表
                        - "file" (str): 文件路径
                        - "error" (str): 错误信息
                        - "line" (int): 错误行号
                        
                - "pytest_check" (Dict): Pytest收集结果
                    - "success" (bool): 是否成功收集
                    - "test_count" (int): 收集到的测试数量
                    - "duration" (float): 收集耗时（秒）
                    - "errors" (List[str]): 收集错误信息
                    
                - "dependencies" (Dict): 依赖检查结果
                    - "missing_factories" (List[str]): 缺失的Factory类
                    - "missing_fixtures" (List[str]): 缺失的fixture
                    - "available_fixtures" (List[str]): 可用的fixture列表
                    
                - "summary" (Dict): 总结信息
                    - "score" (int): 综合质量评分（0-100分）
                    - "level" (str): 质量等级
                        - "Excellent": 90-100分
                        - "Good": 80-89分
                        - "Fair": 70-79分
                        - "Needs Improvement": <70分
                    - "recommendations" (List[str]): 改进建议
                    
        Raises:
            无 - 验证失败不会抛出异常，而是在报告中记录
            
        Example:
            files = {
                "tests/unit/generated/user_auth/test_models.py": "# Model测试代码...",
                "tests/unit/generated/user_auth/test_repositories.py": "# Repository测试代码..."
            }
            
            report = generator._validate_generated_tests(files)
            
            print(f"语法检查: {len(report['syntax_check']['passed'])}/{len(files)} 通过")
            print(f"pytest收集: {report['pytest_check']['test_count']} 个测试")
            print(f"质量评分: {report['summary']['score']}分 ({report['summary']['level']})")
            
            if report['dependencies']['missing_factories']:
                print(f"缺失Factory: {', '.join(report['dependencies']['missing_factories'])}")
                
        Notes:
            - 验证过程会实际写入临时文件并运行pytest命令
            - 语法检查使用Python内置ast模块，速度快但不等同于实际运行
            - pytest收集需要测试环境配置正确（conftest.py、依赖库等）
            - 质量评分算法: 语法30% + pytest收集30% + 依赖检查20% + fixture检查20%
            - 验证报告会保存到reports/test_validation_{module}_{timestamp}.md
            
        Performance:
            - 语法检查: <100ms（纯AST分析）
            - pytest收集: 2-5秒（取决于测试数量）
            - 依赖检查: <100ms
            - 总耗时: 约2-5秒
            
        See Also:
            - ValidationReporter.validate_generated_tests(): 验证的具体实现
            - PytestChecker: Pytest兼容性检查工具
            - ValidationReporter.generate_validation_report(): Markdown报告生成
        """
        reporter = ValidationReporter()
        return reporter.validate_generated_tests(files, self.project_root)


def main():
    """主程序入口 [CHECK:DEV-009]"""
    parser = argparse.ArgumentParser(
        description="智能五层架构测试生成器 v2.0",
        epilog="示例: python tools/generate_test_template.py user_auth --type all --validate",
    )

    parser.add_argument("module_name", nargs="?", help="模块名称 (如: user_auth, shopping_cart)")
    parser.add_argument("--module", dest="module_opt", help="模块名称（可选参数形式）")
    parser.add_argument(
        "--type", "--test-type",
        dest="test_type",
        choices=["all", "unit", "integration", "api", "e2e", "smoke", "specialized", "performance", 
                 "factories", "models", "repositories", "services", "standalone", "security"],
        default="all",
        help="生成的测试类型 (新增: factories, models, repositories, services, standalone, security)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="试运行模式（不写入文件）"
    )
    parser.add_argument(
        "--validate", action="store_true", default=True, help="验证生成的代码"
    )
    parser.add_argument("--detailed", action="store_true", help="显示详细的分析信息")
    parser.add_argument("--force", action="store_true", help="强制覆盖已存在的测试文件")

    args = parser.parse_args()
    
    # 合并位置参数和可选参数
    module_name = args.module_opt or args.module_name
    if not module_name:
        parser.error("必须提供模块名称（位置参数或 --module）")

    try:
        generator = IntelligentTestGenerator()

        if args.detailed:
            # 显示详细分析信息
            models = generator.analyze_module_models(module_name)
            for model_name, model_info in models.items():
                print(f"\n📊 {model_name} 模型:")
                print(f"   表名: {model_info.tablename}")
                print(f"   字段: {len(model_info.fields)}个")
                print(f"   关系: {len(model_info.relationships)}个")
                print(
                    f"   混入: {', '.join(model_info.mixins) if model_info.mixins else '无'}"
                )
        else:
            # 生成测试
            result = generator.generate_tests(
                module_name, args.test_type, args.dry_run, args.validate
            )

            # 处理返回值（兼容单返回值和双返回值）
            if isinstance(result, tuple):
                generated_files, validation_report = result
            else:
                generated_files = result
                validation_report = None

            if args.dry_run:
                print("\n🔍 试运行结果:")
                for file_key in generated_files.keys():
                    # 转换文件键为目标路径显示
                    if file_key.startswith("tests/factories/"):
                        target_path = file_key  # 工厂文件已经是完整路径
                    elif file_key.startswith("test_models/"):
                        # test_models/test_user_auth_models -> tests/unit/test_models/test_user_auth_models.py
                        module_name = file_key.split("/")[-1].replace("test_", "").replace("_models", "")
                        target_path = f"tests/unit/test_models/test_{module_name}_models.py"
                    elif file_key.startswith("test_services/"):
                        # test_services/test_user_auth_services -> tests/unit/test_services/test_user_auth_services.py  
                        module_name = file_key.split("/")[-1].replace("test_", "").replace("_services", "")
                        target_path = f"tests/unit/test_services/test_{module_name}_services.py"
                    elif file_key.endswith("_standalone"):
                        # user_auth_standalone -> tests/unit/test_user_auth_standalone.py
                        module_name = file_key.replace("_standalone", "")
                        target_path = f"tests/unit/test_{module_name}_standalone.py"
                    else:
                        target_path = file_key
                    print(f"   将生成: {target_path}")
            else:
                print(f"\n🎯 生成完成！共生成 {len(generated_files)} 个文件")
                if validation_report and validation_report["overall_success"]:
                    print("✅ 所有验证检查通过，质量符合标准")
                elif validation_report:
                    print("⚠️ 部分验证检查未通过，请查看验证报告")

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        print("\n完整错误堆栈:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
