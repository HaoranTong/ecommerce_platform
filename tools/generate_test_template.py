#!/usr/bin/env python3
"""
🧪 智能测试模板生成器 v2.0 - 全面优化版

🚨 **关键f-string嵌套错误警告** 🚨
此文件曾多次出现 "name 'model_name' is not defined" 错误，主要原因:

1. **嵌套f-string问题**: 在大的f-string模板内部使用{variable}
2. **注释中的花括号**: 在f-string内部的注释中使用{}
3. **模板变量替换错误**: .format()传入字符串字面量而不是变量

🔧 **修复策略和预防措施**:
- 在所有大型f-string模板中使用双大括号{{}}转义
- 注释中绝对不使用{}花括号，改用文字描述
- .format()调用中传入实际变量而不是"{variable_name}"
- 在关键位置添加明确的修复说明和警告

📚 **参考历史修复**: git commit 3a4387a 系统性修复F-string格式化错误
📖 **详细指南**: docs/development/f_string_error_prevention_guide.md

智能五层架构测试生成器

配置文件依赖:
- 主配置文件: tools/test_generator_config.json
- 配置内容: 项目结构、测试分布比例、数据库配置、业务逻辑模式等
- 备用机制: 配置文件缺失时自动使用内置默认配置
- 配置更新: 修改JSON文件即可自定义生成行为，无需重启

功能特性:
- 智能模型分析：基于AST和运行时双重分析
- 五层测试架构：单元/集成/API/端到端/专项测试
- 自适应生成：根据模型复杂度调整测试深度
- 配置驱动：通过JSON配置文件控制所有生成行为

使用方法:
    python tools/generate_test_template.py user_auth
    python tools/generate_test_template.py user_auth --type all
    python tools/generate_test_template.py user_auth --dry-run

配置文件结构:
- project_structure: 项目路径配置
- test_distributions: 各类测试比例分配  
- test_paths: 测试文件输出路径
- database_config: 数据库连接和清理配置
- business_logic_patterns: 业务逻辑识别模式
- error_handling: 错误处理和重试策略

集成模块化测试生成器架构，支持AST+运行时双重分析
自动生成完整测试架构：包含传统测试(5个)和专业化测试(4个)

主要功能：
1. 智能模型分析 - 自动解析SQLAlchemy模型结构
2. 智能数据工厂生成 - 基于模型自动生成Factory Boy类
3. 分层测试生成 - 单元+集成+E2E测试架构自动生成
4. 模块化测试生成器架构 - API/E2E/安全/性能专业测试生成
5. 质量自动验证 - 语法、导入、执行验证

生成的测试文件(9个):
- 传统测试: factories, unit/models, unit/services, unit/standalone, integration
- 专业测试: API测试, E2E测试, 安全测试, 性能测试

模块化架构:
- BaseTestGenerator: 提供共享功能(路由分析、模型提取)
- APITestGenerator: HTTP端点测试生成
- E2ETestGenerator: 端到端业务流程测试生成
- SecurityTestGenerator: OWASP安全测试生成
- PerformanceTestGenerator: 性能基准测试生成

符合标准:
- MASTER.md强制检查点规范 [CHECK:DEV-009] [CHECK:TEST-001]
- docs/standards/testing-standards.md五层测试架构
- docs/standards/checkpoint-cards.md验证流程

作者: AI Assistant (遵循MASTER文档规范)
版本: 3.0 (模块化架构版 + 配置文件驱动)
创建时间: 2025-09-20
更新时间: 2025-10-02
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
    ) -> Dict[str, str]:
        """生成测试文件
        
        🚨 **f-string错误已修复但需持续注意** 🚨
        
        关键修复点（历史错误参考）:
        1. _generate_single_factory: 第918行 - 模板字符串用.format()而不是嵌套f-string
        2. _generate_service_tests: 第2725行 - 注释中的花括号被f-string解析
        3. _generate_smart_crud_test: 模板变量替换传入实际变量而不是字符串字面量
        4. StandardTestDataFactory依赖已移除 - 它不存在且未被使用
        
        🔧 预防措施:
        - 所有大型f-string模板使用双大括号{{}}转义
        - 注释中不使用{}花括号
        - .format()传入实际变量: variable而不是"{variable}"

        Args:
            module_name: 模块名称
            test_type: 测试类型 ('all', 'unit', 'integration', 'e2e', 'smoke', 'specialized')
            dry_run: 是否为试运行（不写入文件）
            validate: 是否验证生成的代码

        Returns:
            Dict[str, str]: 文件路径到内容的映射
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
        models = self.analyze_module_models(module_name)
        repositories = self.analyze_module_repositories(module_name)  # 强制要求Repository层
        
        print(f"\n📊 结构分析完成:")
        print(f"   Models: {len(models)} 个")
        print(f"   Repositories: {len(repositories)} 个")

        # 2. 生成智能数据工厂
        from tools.test_generators.factories import FactoryGenerator
        factory_generator = FactoryGenerator(self.project_root, self.config)
        factory_code = factory_generator.generate_factories(module_name, models)

        # 3. 生成测试文件
        generated_files = {}

        # 添加工厂文件到生成结果
        factory_file_path = f"tests/factories/{module_name}_factories.py"
        generated_files[factory_file_path] = factory_code

        if test_type in ["all", "unit"]:
            unit_files = self._generate_unit_tests(module_name, models, repositories)
            generated_files.update(unit_files)

        if test_type in ["all", "integration"]:
            from tools.test_generators.integration import IntegrationTestGenerator
            integration_generator = IntegrationTestGenerator(self.project_root, self.config)
            integration_files = integration_generator.generate_integration_tests(module_name, models)
            generated_files.update(integration_files)
        
        if test_type in ["all", "api"]:
            from tools.test_generators.api_test_generator import APITestGenerator
            api_generator = APITestGenerator(self.project_root, self.config)
            api_files = api_generator.generate_tests(module_name, models)
            generated_files.update(api_files)
        
        if test_type in ["all", "e2e"]:
            from tools.test_generators.e2e_test_generator import E2ETestGenerator
            e2e_generator = E2ETestGenerator(self.project_root, self.config)
            e2e_files = e2e_generator.generate_tests(module_name, models)
            generated_files.update(e2e_files)

        if test_type in ["all", "smoke"]:
            # 烟雾测试使用通用脚本，不生成模块特定文件
            print(f"ℹ️  烟雾测试使用通用脚本 tools/smoke_test.ps1，跳过 {module_name} 模块特定生成")

        if test_type in ["all", "specialized"]:
            # 生成专项测试（安全测试和性能测试）
            from tools.test_generators import SecurityTestGenerator, PerformanceTestGenerator
            
            security_generator = SecurityTestGenerator(self.project_root, self.config)
            performance_generator = PerformanceTestGenerator(self.project_root, self.config)
            
            security_tests = security_generator.generate_tests(module_name, models)
            generated_files.update(security_tests)
            
            performance_tests = performance_generator.generate_tests(module_name, models)
            generated_files.update(performance_tests)
            
            print(f"✅ 生成专项测试: 安全测试 + 性能测试")

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
        self, module_name: str, models: Dict[str, ModelInfo], repositories: Dict[str, RepositoryInfo]
    ) -> Dict[str, str]:
        """生成单元测试 (70%) - 四种独立脚本（四层架构）[CHECK:TEST-001]

        根据testing-standards.md标准和四层架构要求生成四个独立的单元测试脚本：
        1. test_models/ - 100% Mock测试，无数据库依赖
        2. test_repositories/ - SQLite内存数据库测试数据访问层（新增）
        3. test_services/ - SQLite内存数据库测试，Mock Repository依赖
        4. *_standalone.py - SQLite内存数据库业务流程测试

        Args:
            module_name: 模块名称
            models: 模型信息字典
            repositories: Repository信息字典（四层架构必需）

        Returns:
            Dict[str, str]: 四个测试脚本的文件路径到内容映射
        """
        files = {}

        # 1. 生成Mock模型测试
        from tools.test_generators.unit import ModelTestGenerator
        model_generator = ModelTestGenerator(self.project_root, self.config)
        model_tests = model_generator.generate_model_tests(module_name, models)
        files[f"test_models/test_{module_name}_models"] = model_tests

        # 2. 生成Repository测试
        from tools.test_generators.unit import RepositoryTestGenerator
        repo_generator = RepositoryTestGenerator(self.project_root, self.config, main_generator=self)
        repository_tests = repo_generator.generate_repository_tests(module_name, models, repositories)
        files[f"test_repositories/test_{module_name}_repositories"] = repository_tests

        # 3. 生成服务测试
        from tools.test_generators.unit import ServiceTestGenerator
        service_generator = ServiceTestGenerator(self.project_root, self.config)
        service_tests = service_generator.generate_service_tests(module_name, models, repositories)
        files[f"test_services/test_{module_name}_services"] = service_tests

        # 4. 生成业务流程测试
        from tools.test_generators.unit.standalone_test_generator import StandaloneTestGenerator
        workflow_generator = StandaloneTestGenerator(self.project_root, self.config)
        workflow_tests = workflow_generator.generate_workflow_tests(module_name, models)
        files[f"tests/unit/test_{module_name}_standalone.py"] = workflow_tests

        print(f"✅ 生成三个独立单元测试脚本:")
        print(f"   📋 Mock模型测试: test_models/test_{module_name}_models.py")
        print(f"   🔧 服务测试: test_services/test_{module_name}_services.py")
        print(f"   🔄 业务流程测试: {module_name}_standalone.py")

        return files
    
    def _generate_test_entity_creation(self, model_name: str, models: Dict[str, ModelInfo], suffix: str = "测试数据", with_dependencies: bool = False) -> str:
        """生成测试实体创建代码，自动包含必填字段和外键依赖
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            suffix: 名称后缀
            with_dependencies: 是否生成外键依赖的完整代码（多行）
            
        Returns:
            str: 实体创建代码（可能是多行的依赖创建+主实体创建）
        """
        if model_name not in models:
            # 如果模型信息不存在，返回简单的创建代码并添加TODO
            return f'{model_name}(name="{suffix}")  # TODO: 根据实际字段调整'
        
        model_info = models[model_name]
        
        # 提取所有非nullable的字段（排除id和自动字段）
        auto_fields = {'id', 'created_at', 'updated_at', 'is_deleted'}
        required_fields = [
            f for f in model_info.fields 
            # 🔥 修复：不排除作为外键的主键字段（如UserRole的联合主键）
            # 只排除自增主键（field.name == 'id'）
            if not f.nullable and f.name not in auto_fields and not (f.primary_key and f.name == 'id')
        ]
        
        # 分离外键字段和普通字段
        fk_fields = [f for f in required_fields if f.foreign_key]
        normal_fields = [f for f in required_fields if not f.foreign_key]
        
        if not required_fields:
            # 如果没有必填字段，使用简单形式
            return f'{model_name}()'
        
        # 如果不需要生成依赖，或没有外键字段，生成简单单行形式
        if not with_dependencies or not fk_fields:
            field_assignments = []
            for field in required_fields:
                test_value = self._get_test_value_for_field(field, suffix)
                field_assignments.append(f'{field.name}={test_value}')
            # 返回不带变量赋值的表达式（用于单行赋值：entity = XXX()）
            return f'{model_name}({", ".join(field_assignments)})'
        
        # 生成完整的依赖创建代码（多行）
        lines = []
        fk_var_names = {}
        
        # 为每个外键字段创建依赖实体
        for field in fk_fields:
            # 解析外键目标：'products.id' -> table='products', column='id'
            fk_target = field.foreign_key
            fk_table = fk_target.split('.')[0]
            
            # 推断模型名（表名转模型名：products -> Product, categories -> Category）
            fk_model_name = self.test_utils.table_name_to_model_name(fk_table)
            # 使用相同的单数化逻辑作为变量名（小写）
            fk_var_name = self.test_utils.table_name_to_model_name(fk_table).lower()
            
            # 递归生成依赖实体（不再生成依赖的依赖，避免无限递归）
            fk_entity_code = self._generate_test_entity_creation(fk_model_name, models, f"依赖{suffix}", with_dependencies=False)
            lines.append(f'{fk_var_name} = {fk_entity_code}')
            lines.append(f'unit_test_db.add({fk_var_name})')
            lines.append(f'unit_test_db.commit()')
            
            # 记录变量名，用于后续引用
            fk_var_names[field.name] = f'{fk_var_name}.id'
        
        # 生成主实体的字段赋值
        field_assignments = []
        for field in normal_fields:
            test_value = self._get_test_value_for_field(field, suffix)
            field_assignments.append(f'{field.name}={test_value}')
        
        # 添加外键字段赋值
        for field in fk_fields:
            field_assignments.append(f'{field.name}={fk_var_names[field.name]}')
        
        # 添加主实体创建
        lines.append(f'entity = {model_name}({", ".join(field_assignments)})')
        
        return '\n        '.join(lines)
    
    def _has_composite_primary_key(self, model_name: str, models: Dict[str, ModelInfo]) -> bool:
        """检查模型是否使用联合主键（多个primary_key字段）"""
        if model_name not in models:
            return False
        return self.test_utils.has_composite_primary_key(models[model_name])
    
    def _get_primary_key_fields(self, model_name: str, models: Dict[str, ModelInfo]) -> List['FieldInfo']:
        """获取模型的主键字段列表"""
        if model_name not in models:
            return []
        return self.test_utils.get_primary_key_fields(models[model_name])
    
    # 注意：_infer_query_parameter等方法已废弃，RepositoryTestGenerator有自己的实现
    
    def _get_test_value_for_field(self, field: 'FieldInfo', suffix: str = "测试") -> str:
        """推断自定义查询方法需要的参数（通用化改进版）
        
        通过分析方法签名自动推断参数：
        - get_by_username -> entity.username
        - get_user_roles(user_id: int) -> 需要创建User，传入user.id
        - get_role_users(role_id: int) -> 需要创建Role，传入role.id
        - get (联合主键) -> 需要所有主键字段
        
        Args:
            method_info: 方法信息（包含参数签名）
            model_name: 模型名称
            models: 所有模型信息
            
        Returns:
            tuple: (准备代码, 参数字符串, 是否需要TODO注释)
                - setup_code: 创建依赖实体的代码（如创建User）
                - param_str: 调用方法时的参数字符串（如user.id）
                - needs_todo: 是否需要TODO注释
        """
        method_name = method_info.name
        
        # 🔥 提取方法参数（排除self, db, cls）
        method_params = [p for p in method_info.parameters if p[0] not in ['self', 'db', 'cls']]
        
        # 特殊处理check_exists方法（可选参数组合）
        if method_name == 'check_exists':
            return ('', 'username=entity.username, email=entity.email', False)
        
        # 特殊处理联合主键的get方法
        if method_name == 'get' and self._has_composite_primary_key(model_name, models):
            pk_fields = self._get_primary_key_fields(model_name, models)
            param_str = ', '.join([f'entity.{f.name}' for f in pk_fields])
            return ('', param_str, False)
        
        # 特殊处理联合主键的delete方法
        if method_name == 'delete' and self._has_composite_primary_key(model_name, models):
            pk_fields = self._get_primary_key_fields(model_name, models)
            param_str = ', '.join([f'entity.{f.name}' for f in pk_fields])
            return ('', param_str, False)
        
        # 🔥 智能推断：分析方法参数，自动生成依赖实体
        if method_params:
            setup_code_lines = []
            param_parts = []
            
            for param_name, param_type in method_params:
                # 推断参数对应的实体类型
                # user_id: int -> User
                # role_id: int -> Role
                # permission_id: int -> Permission
                entity_name = self.test_utils.infer_entity_from_param(param_name, param_type, models)
                
                if entity_name and entity_name in models:
                    # 生成创建实体的代码
                    var_name = entity_name.lower()
                    entity_creation = self._generate_test_entity_creation(entity_name, models, f"{entity_name}数据", with_dependencies=True)
                    setup_code_lines.append(f"{var_name} = {entity_creation}")
                    setup_code_lines.append(f"unit_test_db.add({var_name})")
                    setup_code_lines.append(f"unit_test_db.commit()")
                    setup_code_lines.append("")
                    
                    # 参数使用实体的ID
                    if param_name.endswith('_id'):
                        param_parts.append(f"{var_name}.id")
                    else:
                        param_parts.append(f"{var_name}")
                else:
                    # 无法推断实体，尝试从方法名推断字段
                    # get_by_username(username: str) -> entity.username
                    # get_by_email(email: str) -> entity.email
                    if method_name.startswith('get_by_') and param_type == 'str':
                        field_name = method_name[7:]  # 移除'get_by_'
                        if '_or_' in field_name:
                            field_name = field_name.split('_or_')[0]  # 使用第一个字段
                        param_parts.append(f'entity.{field_name}')
                    elif param_type == 'int':
                        param_parts.append('1')
                    elif param_type == 'str':
                        param_parts.append('"test_value"')
                    elif param_type == 'bool':
                        param_parts.append('True')
                    else:
                        # 复杂类型，需要TODO
                        return ('', '', True)
            
            setup_code = '\n        '.join(setup_code_lines) if setup_code_lines else ''
            param_str = ', '.join(param_parts)
            return (setup_code, param_str, False)
        
        # 提取方法名中的字段名（兼容老逻辑）
        if method_name.startswith('get_by_'):
            field_part = method_name[7:]  # 移除'get_by_'
            # 特殊处理复合查询（如username_or_email）
            if '_or_' in field_part:
                # 使用第一个字段
                field_name = field_part.split('_or_')[0]
                return ('', f'entity.{field_name}', False)
            else:
                return ('', f'entity.{field_part}', False)
        elif method_name == 'check_exists':
            # check_exists通常接受多个可选参数
            return ('', 'username=entity.username, email=entity.email', False)
        else:
            # 默认使用id（如果有的话）
            has_composite_pk = self._has_composite_primary_key(model_name, models)
            if has_composite_pk:
                # 联合主键模型需要TODO
                return ('', '', True)
            return ('', 'entity.id', False)
    
    def _validate_generated_tests(self, files: Dict[str, str]) -> Dict[str, Any]:
        """委托给ValidationReporter进行测试验证"""
        reporter = ValidationReporter()
        return reporter.validate_generated_tests(files, self.project_root)

def main():
    """主程序入口 [CHECK:DEV-009]"""
    parser = argparse.ArgumentParser(
        description="智能五层架构测试生成器 v2.0",
        epilog="示例: python tools/generate_test_template.py user_auth --type all --validate",
    )

    parser.add_argument("module_name", help="模块名称 (如: user_auth, shopping_cart)")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "api", "e2e", "smoke", "specialized"],
        default="all",
        help="生成的测试类型",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="试运行模式（不写入文件）"
    )
    parser.add_argument(
        "--validate", action="store_true", default=True, help="验证生成的代码"
    )
    parser.add_argument("--detailed", action="store_true", help="显示详细的分析信息")

    args = parser.parse_args()

    try:
        generator = IntelligentTestGenerator()

        if args.detailed:
            # 显示详细分析信息
            models = generator.analyze_module_models(args.module_name)
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
                args.module_name, args.type, args.dry_run, args.validate
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
        sys.exit(1)


class EnvironmentValidator:
    """测试环境兼容性验证器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def validate_test_environment(self, module_name: str) -> Dict[str, Any]:
        """验证测试环境配置并返回环境信息"""
        env_info = {
            "module_exists": False,
            "fixtures_available": [],
            "database_config": {},
            "issues": []
        }
        
        # 检查模块是否存在
        module_path = os.path.join(
            self.config["project_structure"]["modules_path"], 
            module_name
        )
        env_info["module_exists"] = os.path.exists(module_path)
        if not env_info["module_exists"]:
            env_info["issues"].append(f"模块路径不存在: {module_path}")
        
        # 检查conftest.py并获取可用fixture
        conftest_path = os.path.join(self.config["project_structure"]["tests_path"], "conftest.py")
        if os.path.exists(conftest_path):
            try:
                with open(conftest_path, 'r', encoding='utf-8') as f:
                    conftest_content = f.read()
                
                # 解析可用的fixture
                import re
                fixture_pattern = r'@pytest\.fixture[^\n]*\ndef\s+(\w+)'
                fixtures = re.findall(fixture_pattern, conftest_content)
                env_info["fixtures_available"] = fixtures
                
            except Exception as e:
                env_info["issues"].append(f"无法读取conftest.py: {e}")
        else:
            env_info["issues"].append(f"conftest.py不存在: {conftest_path}")
        
        # 设置数据库配置信息
        db_config = self.config["database_config"]
        env_info["database_config"] = {
            "unit_fixture": db_config["unit_test_fixture"],
            "integration_fixture": db_config["integration_test_fixture"],
            "e2e_fixture": db_config["e2e_test_fixture"],
        }
        
        return env_info


if __name__ == "__main__":
    main()
