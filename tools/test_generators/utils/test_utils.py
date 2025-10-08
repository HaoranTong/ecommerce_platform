"""
测试工具类 - 测试代码生成通用辅助方法

该模块提供测试代码生成过程中的通用辅助方法，包括实体创建代码生成、测试值生成、
参数推断、命名转换等功能，被各个测试生成器共享使用。

主要功能:
- 实体创建代码生成: 根据模型信息生成完整的实体创建代码（包含所有必填字段）
- 最小实体创建代码: 生成仅包含必填字段的精简实体创建代码
- 测试值生成: 根据字段类型和约束生成合适的测试值
- 查询参数推断: 根据Repository方法名推断可能的查询参数
- 命名转换: 表名/模型名互转，支持多种命名约定
- Factory名称推断: 根据模型名生成对应的Factory类名

技术栈:
- Python typing: 类型注解和类型检查
- pathlib: 路径处理

依赖关系:
- tools.test_generators.core.schema: ModelInfo/FieldInfo数据模型
- tools.test_generators.unit.*: 各测试生成器调用工具方法
- tests/factories/: Factory类命名约定参考

使用示例:
    from tools.test_generators.utils.test_utils import TestUtils
    from tools.test_generators.core.schema import ModelInfo, FieldInfo
    
    # 生成实体创建代码
    model_info = ModelInfo(
        name="User",
        table_name="users",
        fields=[
            FieldInfo(name="username", type="String", nullable=False),
            FieldInfo(name="email", type="String", nullable=False)
        ]
    )
    code = TestUtils.generate_test_entity_creation(model_info)
    print(code)
    # 输出:
    # entity = User(
    #     username="test_username",
    #     email="test@example.com"
    # )
    
    # 表名转模型名
    model_name = TestUtils.table_name_to_model_name("user_roles")
    print(model_name)  # "UserRole"

注意事项:
- 测试值生成基于字段类型和命名约定，可能不完全符合业务规则
- 外键字段会自动生成1或None，具体取决于nullable属性
- 对于复杂类型（JSON、ARRAY等），生成默认值或空值
- 所有方法都是静态方法，无需实例化即可使用

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-08
Version: 1.0.0
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
    
    @staticmethod
    def table_name_to_model_name(table_name: str) -> str:
        """表名转模型名：products -> Product, categories -> Category"""
        if table_name.endswith('ies'):
            singular = table_name[:-3] + 'y'
        elif table_name.endswith('s'):
            singular = table_name[:-1]
        else:
            singular = table_name
        return singular.capitalize()
    
    @staticmethod
    def has_composite_primary_key(model_info: ModelInfo) -> bool:
        """检查模型是否使用联合主键"""
        return sum(1 for f in model_info.fields if f.primary_key) > 1
    
    @staticmethod
    def get_primary_key_fields(model_info: ModelInfo) -> List[FieldInfo]:
        """获取模型的主键字段列表"""
        return [f for f in model_info.fields if f.primary_key]
    
    @staticmethod
    def infer_entity_from_param(param_name: str, param_type: str, models: Dict[str, ModelInfo]) -> Optional[str]:
        """从参数名和类型推断对应的实体类型
        
        推断规则：
        1. user_id: int -> User (ID参数)
        2. user: User -> User (对象参数)
        3. role_id: int -> Role (ID参数)
        """
        # 情况1：对象类型参数（如user: User）
        if param_type in models:
            return param_type
        
        # 情况2：ID参数（如user_id: int）
        if param_type == 'int' and param_name.endswith('_id'):
            entity_base = param_name[:-3]
            candidates = [
                entity_base.title(),
                entity_base.capitalize(),
                ''.join(word.capitalize() for word in entity_base.split('_'))
            ]
            for candidate in candidates:
                if candidate in models:
                    return candidate
        
        # 情况3：从参数名推断
        candidates = [
            param_name.title(),
            param_name.capitalize(),
            ''.join(word.capitalize() for word in param_name.split('_'))
        ]
        for candidate in candidates:
            if candidate in models:
                return candidate
        
        return None
