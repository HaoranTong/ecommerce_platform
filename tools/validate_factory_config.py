#!/usr/bin/env python3
"""
工厂配置验证工具

功能：
1. 检查工厂方法签名与模型字段的一致性
2. 验证外键依赖是否有对应的create方法
3. 检查映射表的完整性
4. 发现缺失的工厂方法
5. 识别参数类型错误

使用方法：
    python tools/validate_factory_config.py
    python tools/validate_factory_config.py --fix  # 生成修复建议
"""

import ast
import importlib
import inspect
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import class_mapper


class FactoryConfigValidator:
    """工厂配置验证器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.suggestions: List[Dict[str, Any]] = []
        
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """执行所有验证检查
        
        Returns:
            (是否通过, 详细报告)
        """
        print("🔍 开始工厂配置全面验证...\n")
        
        # 1. 分析模型字段
        print("📋 步骤1: 分析所有模型字段...")
        models_info = self._analyze_models()
        print(f"   ✅ 发现 {len(models_info)} 个模型\n")
        
        # 2. 分析工厂方法
        print("📋 步骤2: 分析工厂方法...")
        factory_methods = self._analyze_factory_methods()
        print(f"   ✅ 发现 {len(factory_methods)} 个工厂方法\n")
        
        # 3. 验证方法签名
        print("📋 步骤3: 验证方法签名与模型字段一致性...")
        self._validate_method_signatures(models_info, factory_methods)
        
        # 4. 验证外键依赖
        print("📋 步骤4: 验证外键依赖的工厂方法...")
        self._validate_foreign_key_factories(models_info, factory_methods)
        
        # 5. 验证映射表
        print("📋 步骤5: 验证路由映射表完整性...")
        self._validate_route_mappings(models_info)
        
        # 6. 检查缺失的工厂方法
        print("📋 步骤6: 检查缺失的工厂方法...")
        self._check_missing_factories(models_info, factory_methods)
        
        # 生成报告
        return self._generate_report()
    
    def _analyze_models(self) -> Dict[str, Dict[str, Any]]:
        """分析所有模型的字段和外键"""
        models_info = {}
        
        # 添加项目根目录到sys.path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        modules_path = self.project_root / "app" / "modules"
        for module_dir in modules_path.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith('_'):
                continue
                
            models_file = module_dir / "models.py"
            if not models_file.exists():
                continue
            
            try:
                # 使用importlib直接导入
                module_name = f"app.modules.{module_dir.name}.models"
                module = importlib.import_module(module_name)
                    
                # 查找所有模型类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, '__tablename__'):
                        model_info = self._extract_model_info(obj, module_dir.name)
                        models_info[name] = model_info
            except Exception as e:
                self.warnings.append({
                    'type': 'model_import_error',
                    'module': module_dir.name,
                    'error': str(e)
                })
        
        return models_info
    
    def _extract_model_info(self, model_class: Any, module_name: str) -> Dict[str, Any]:
        """提取模型的字段和外键信息"""
        try:
            mapper = class_mapper(model_class)
            columns = sa_inspect(model_class).columns
            
            fields = {}
            foreign_keys = {}
            
            for column in columns:
                field_info = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                }
                
                # 检查是否是外键
                if column.foreign_keys:
                    fk = list(column.foreign_keys)[0]
                    target_table = fk.column.table.name
                    field_info['is_foreign_key'] = True
                    field_info['target_table'] = target_table
                    foreign_keys[column.name] = {
                        'target_table': target_table,
                        'target_column': fk.column.name
                    }
                
                fields[column.name] = field_info
            
            return {
                'module': module_name,
                'table_name': model_class.__tablename__,
                'fields': fields,
                'foreign_keys': foreign_keys
            }
        except Exception as e:
            return {
                'module': module_name,
                'error': str(e),
                'fields': {},
                'foreign_keys': {}
            }
    
    def _analyze_factory_methods(self) -> Dict[str, Dict[str, Any]]:
        """分析工厂方法的签名和参数"""
        factory_methods = {}
        
        factory_file = self.project_root / "tests" / "factories" / "data_factory.py"
        if not factory_file.exists():
            self.errors.append({
                'type': 'factory_file_missing',
                'message': 'data_factory.py 文件不存在'
            })
            return factory_methods
        
        try:
            # 解析AST
            with open(factory_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            # 查找所有 create_xxx 方法
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('create_'):
                    method_info = self._extract_method_info(node)
                    factory_methods[node.name] = method_info
        
        except Exception as e:
            self.errors.append({
                'type': 'factory_parse_error',
                'error': str(e)
            })
        
        return factory_methods
    
    def _extract_method_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """提取方法的参数信息"""
        params = []
        creates_fields = {}
        
        # 提取参数
        for arg in node.args.args:
            if arg.arg not in ['self', 'cls']:
                params.append(arg.arg)
        
        # 查找方法体中的字段赋值
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Dict):
                for key, value in zip(stmt.keys, stmt.values):
                    if isinstance(key, ast.Constant):
                        field_name = key.value
                        # 尝试推断值的来源
                        if isinstance(value, ast.Name):
                            creates_fields[field_name] = {
                                'source': 'parameter',
                                'param': value.id
                            }
                        else:
                            creates_fields[field_name] = {
                                'source': 'literal',
                                'value': None
                            }
        
        return {
            'parameters': params,
            'creates_fields': creates_fields
        }
    
    def _validate_method_signatures(
        self, 
        models_info: Dict[str, Dict[str, Any]], 
        factory_methods: Dict[str, Dict[str, Any]]
    ):
        """验证工厂方法签名与模型字段的一致性"""
        for method_name, method_info in factory_methods.items():
            # 从方法名推断模型名
            model_name = self._method_name_to_model_name(method_name)
            
            if model_name not in models_info:
                continue
            
            model_info = models_info[model_name]
            model_fields = model_info['fields']
            created_fields = method_info['creates_fields']
            
            # 检查必需字段是否都有
            for field_name, field_info in model_fields.items():
                # 跳过自动生成的字段
                if field_name in ['id', 'created_at', 'updated_at', 'deleted_at']:
                    continue
                
                # 必需字段检查
                if not field_info.get('nullable', True) and not field_info.get('primary_key', False):
                    if field_name not in created_fields:
                        self.errors.append({
                            'type': 'missing_required_field',
                            'method': method_name,
                            'model': model_name,
                            'field': field_name,
                            'message': f'{method_name} 未设置必需字段 {field_name}'
                        })
            
            # 检查字段名是否正确
            for field_name, field_source in created_fields.items():
                if field_name not in model_fields:
                    self.errors.append({
                        'type': 'invalid_field',
                        'method': method_name,
                        'model': model_name,
                        'field': field_name,
                        'message': f'{method_name} 设置了不存在的字段 {field_name}',
                        'suggestion': f'模型 {model_name} 没有字段 {field_name}，请检查是否拼写错误'
                    })
    
    def _validate_foreign_key_factories(
        self, 
        models_info: Dict[str, Dict[str, Any]], 
        factory_methods: Dict[str, Dict[str, Any]]
    ):
        """验证外键依赖是否有对应的工厂方法"""
        table_to_model = {
            info['table_name']: name 
            for name, info in models_info.items() 
            if 'table_name' in info and not info.get('error')
        }
        
        for model_name, model_info in models_info.items():
            if model_info.get('error'):
                continue
                
            for fk_field, fk_info in model_info.get('foreign_keys', {}).items():
                target_table = fk_info['target_table']
                target_model = table_to_model.get(target_table)
                
                if target_model:
                    expected_method = f"create_{self._to_snake_case(target_model)}"
                    if expected_method not in factory_methods:
                        self.warnings.append({
                            'type': 'missing_dependency_factory',
                            'model': model_name,
                            'depends_on': target_model,
                            'missing_method': expected_method,
                            'message': f'{model_name} 依赖 {target_model}，但缺少 {expected_method} 方法'
                        })
    
    def _validate_route_mappings(self, models_info: Dict[str, Dict[str, Any]]):
        """验证路由映射表的完整性"""
        config_file = self.project_root / "tools" / "test_generators" / "config" / "test_generator_config.json"
        
        if not config_file.exists():
            self.warnings.append({
                'type': 'config_missing',
                'message': 'test_generator_config.json 不存在'
            })
            return
        
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        mappings = config.get('business_logic_patterns', {}).get('route_parameter_to_model_mapping', {})
        
        # 检查映射的模型是否存在
        for module_name, entity_mappings in mappings.items():
            if isinstance(entity_mappings, dict):
                for entity_type, model_name in entity_mappings.items():
                    if model_name not in models_info:
                        self.errors.append({
                            'type': 'invalid_mapping',
                            'module': module_name,
                            'entity_type': entity_type,
                            'model': model_name,
                            'message': f'映射表中的模型 {model_name} 不存在'
                        })
    
    def _check_missing_factories(
        self, 
        models_info: Dict[str, Dict[str, Any]], 
        factory_methods: Dict[str, Dict[str, Any]]
    ):
        """检查哪些模型缺少工厂方法"""
        for model_name, model_info in models_info.items():
            expected_method = f"create_{self._to_snake_case(model_name)}"
            if expected_method not in factory_methods:
                # 跳过关联表
                if not any(x in model_name.lower() for x in ['role', 'permission', 'attribute']):
                    self.suggestions.append({
                        'type': 'create_factory_method',
                        'model': model_name,
                        'method': expected_method,
                        'message': f'建议为 {model_name} 创建工厂方法 {expected_method}'
                    })
    
    def _method_name_to_model_name(self, method_name: str) -> str:
        """从方法名推断模型名: create_cart_item -> CartItem"""
        name = method_name.replace('create_', '')
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _to_snake_case(self, name: str) -> str:
        """驼峰转蛇形: CartItem -> cart_item"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _generate_report(self) -> Tuple[bool, Dict[str, Any]]:
        """生成验证报告"""
        print("\n" + "="*70)
        print("📊 工厂配置验证报告")
        print("="*70 + "\n")
        
        # 错误
        if self.errors:
            print(f"❌ 发现 {len(self.errors)} 个错误:\n")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. [{error['type']}]")
                print(f"   {error['message']}")
                if 'model' in error:
                    print(f"   模型: {error['model']}")
                if 'method' in error:
                    print(f"   方法: {error['method']}")
                if 'field' in error:
                    print(f"   字段: {error['field']}")
                if 'suggestion' in error:
                    print(f"   💡 建议: {error['suggestion']}")
                print()
        
        # 警告
        if self.warnings:
            print(f"⚠️  发现 {len(self.warnings)} 个警告:\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. [{warning['type']}]")
                if 'message' in warning:
                    print(f"   {warning['message']}")
                if 'error' in warning:
                    print(f"   错误: {warning['error']}")
                if 'missing_method' in warning:
                    print(f"   缺少: {warning['missing_method']}")
                print()
        
        # 建议
        if self.suggestions:
            print(f"💡 {len(self.suggestions)} 条改进建议:\n")
            for i, suggestion in enumerate(self.suggestions[:10], 1):  # 只显示前10条
                print(f"{i}. {suggestion['message']}")
            if len(self.suggestions) > 10:
                print(f"   ... 还有 {len(self.suggestions) - 10} 条建议")
            print()
        
        # 总结
        passed = len(self.errors) == 0
        print("="*70)
        if passed:
            print("✅ 验证通过！工厂配置正确。")
        else:
            print("❌ 验证失败！请修复上述错误。")
        print("="*70 + "\n")
        
        return passed, {
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='验证工厂配置')
    parser.add_argument('--fix', action='store_true', help='生成修复建议')
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    validator = FactoryConfigValidator(project_root)
    
    passed, report = validator.validate_all()
    
    if args.fix and report['errors']:
        print("📝 生成修复建议...\n")
        for error in report['errors']:
            if error['type'] == 'invalid_field':
                print(f"# 修复 {error['method']}")
                print(f"# 移除字段: {error['field']}")
                print(f"# 或添加到模型 {error['model']}\n")
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
