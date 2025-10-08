"""
测试工具模块 - 测试代码生成辅助方法

职责：
1. 生成测试实体创建代码
2. 生成最小实体创建代码
3. 推断查询参数
4. 生成测试值

版本: v1.0
创建时间: 2025-10-08
"""
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

from ..core.schema import ModelInfo, FieldInfo


class TestUtils:
    """测试代码生成工具类"""
    
    @staticmethod
    def generate_test_entity_creation(
        model: ModelInfo,
        entity_var: str = "entity",
        indent: str = "        "
    ) -> str:
        """生成测试实体创建代码
        
        Args:
            model: 模型信息
            entity_var: 实体变量名
            indent: 缩进字符串
            
        Returns:
            str: 实体创建代码
        """
        lines = []
        lines.append(f"{indent}{entity_var} = {model.name}(")
        
        # 生成必需字段
        for field in model.fields:
            if not field.nullable and not field.primary_key and field.default is None:
                test_value = TestUtils._get_test_value_for_field(field)
                lines.append(f"{indent}    {field.name}={test_value},")
        
        # 生成可选但常用的字段
        for field in model.fields:
            if field.nullable and field.name in ['name', 'title', 'description', 'status']:
                test_value = TestUtils._get_test_value_for_field(field)
                lines.append(f"{indent}    {field.name}={test_value},")
        
        lines.append(f"{indent})")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_minimal_entity_creation(
        model: ModelInfo,
        entity_var: str = "entity",
        indent: str = "        "
    ) -> str:
        """生成最小实体创建代码（仅必需字段）
        
        Args:
            model: 模型信息
            entity_var: 实体变量名
            indent: 缩进字符串
            
        Returns:
            str: 最小实体创建代码
        """
        lines = []
        lines.append(f"{indent}{entity_var} = {model.name}(")
        
        # 只生成必需字段
        for field in model.fields:
            if not field.nullable and not field.primary_key and field.default is None:
                test_value = TestUtils._get_test_value_for_field(field)
                lines.append(f"{indent}    {field.name}={test_value},")
        
        lines.append(f"{indent})")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_test_value_for_field(field: FieldInfo) -> str:
        """获取字段的测试值
        
        Args:
            field: 字段信息
            
        Returns:
            str: 测试值的字符串表示
        """
        field_name = field.name.lower()
        python_type = field.python_type.lower()
        
        # 基于字段名的智能推断
        if 'email' in field_name:
            return '"test@example.com"'
        elif 'phone' in field_name:
            return '"18800001234"'
        elif 'password' in field_name:
            return '"hashed_password_123"'
        elif 'username' in field_name or 'user_name' in field_name:
            return '"test_user"'
        elif 'name' in field_name:
            return f'"Test {field.name.replace("_", " ").title()}"'
        elif 'url' in field_name:
            return '"https://example.com"'
        elif 'code' in field_name:
            return '"TEST001"'
        elif 'status' in field_name:
            return '"active"'
        elif 'type' in field_name:
            return '"default"'
        elif 'title' in field_name:
            return '"Test Title"'
        elif 'description' in field_name:
            return '"Test description"'
        elif 'content' in field_name:
            return '"Test content"'
        
        # 基于Python类型的推断
        if 'int' in python_type:
            return '1'
        elif 'float' in python_type or 'decimal' in python_type:
            return '10.0'
        elif 'bool' in python_type:
            return 'True'
        elif 'date' in python_type:
            if 'time' in python_type:
                return 'datetime.now()'
            return 'date.today()'
        elif 'str' in python_type:
            return f'"test_{field.name}"'
        elif 'dict' in python_type:
            return '{}'
        elif 'list' in python_type:
            return '[]'
        
        # 默认值
        return f'"test_{field.name}"'
    
    @staticmethod
    def infer_query_parameter(
        method_name: str,
        parameters: List[tuple],
        model_name: str
    ) -> Optional[str]:
        """推断查询方法的主要查询参数
        
        策略：
        1. 方法名包含字段名 -> 该字段是查询参数
        2. 参数名匹配常见查询字段 -> 选择最相关的
        3. 外键字段优先级高
        
        Args:
            method_name: 方法名
            parameters: 参数列表 [(name, type), ...]
            model_name: 模型名
            
        Returns:
            Optional[str]: 查询参数名，如果无法推断则返回None
        """
        if not parameters:
            return None
        
        method_lower = method_name.lower()
        
        # 常见查询字段优先级
        priority_fields = [
            'id', 'user_id', 'username', 'email', 'phone',
            'name', 'code', 'status', 'type'
        ]
        
        # 1. 检查方法名是否包含字段名
        for param_name, _ in parameters:
            if param_name in ['db', 'self', 'skip', 'limit', 'offset']:
                continue
            if param_name.lower() in method_lower:
                return param_name
        
        # 2. 检查是否有外键字段（通常以_id结尾）
        for param_name, _ in parameters:
            if param_name.endswith('_id') and param_name != 'id':
                return param_name
        
        # 3. 按优先级查找
        for priority in priority_fields:
            for param_name, _ in parameters:
                if param_name.lower() == priority:
                    return param_name
        
        # 4. 返回第一个非系统参数
        for param_name, _ in parameters:
            if param_name not in ['db', 'self', 'skip', 'limit', 'offset']:
                return param_name
        
        return None
    
    @staticmethod
    def get_minimal_test_value(field_type: str) -> str:
        """获取字段类型的最小测试值
        
        Args:
            field_type: 字段类型
            
        Returns:
            str: 最小测试值
        """
        type_lower = field_type.lower()
        
        if 'int' in type_lower:
            return '1'
        elif 'float' in type_lower or 'decimal' in type_lower:
            return '1.0'
        elif 'bool' in type_lower:
            return 'True'
        elif 'str' in type_lower:
            return '"test"'
        elif 'date' in type_lower:
            if 'time' in type_lower:
                return 'datetime.now()'
            return 'date.today()'
        elif 'dict' in type_lower:
            return '{}'
        elif 'list' in type_lower:
            return '[]'
        else:
            return 'None'
    
    @staticmethod
    def generate_factory_field_value(field: FieldInfo, use_faker: bool = True) -> str:
        """生成Factory字段值
        
        Args:
            field: 字段信息
            use_faker: 是否使用Faker生成真实数据
            
        Returns:
            str: Factory字段值表达式
        """
        if not use_faker:
            return TestUtils._get_test_value_for_field(field)
        
        field_name = field.name.lower()
        
        # Faker生成器映射
        faker_mapping = {
            'email': 'fake.email()',
            'phone': 'fake.phone_number()',
            'username': 'fake.user_name()',
            'first_name': 'fake.first_name()',
            'last_name': 'fake.last_name()',
            'name': 'fake.name()',
            'company': 'fake.company()',
            'address': 'fake.address()',
            'city': 'fake.city()',
            'country': 'fake.country()',
            'url': 'fake.url()',
            'text': 'fake.text()',
            'sentence': 'fake.sentence()',
            'paragraph': 'fake.paragraph()',
        }
        
        for key, faker_expr in faker_mapping.items():
            if key in field_name:
                return faker_expr
        
        # 默认使用简单值
        return TestUtils._get_test_value_for_field(field)
