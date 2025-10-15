"""
Factory生成器 - 测试数据工厂类

职责：
生成Factory Boy工厂类代码，包括：
1. 标准测试数据工厂
2. 模块专用工厂
3. 关联关系处理
4. 懒惰属性和序列

双工厂架构：
- StandardTestDataFactory: 通用标准工厂（所有模块）
- 模块专用Factory: 特定业务场景（可选）

版本: v1.0
创建时间: 2025-10-08
"""
from pathlib import Path
from typing import Dict, List, Tuple
from ..core import ModelInfo, FieldInfo


class FactoryGenerator:
    """Factory Boy工厂类生成器"""
    
    def __init__(self, project_root: Path, config: Dict, main_generator=None):
        """初始化生成器
        
        Args:
            project_root: 项目根目录
            config: 配置字典
            main_generator: 主生成器实例（临时使用）
        """
        self.project_root = project_root
        self.config = config
        self.main_generator = main_generator
    
    def generate_factories(
        self,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Factory类代码（主入口）- 智能工厂生成器
        
        基于模型分析结果自动生成Factory Boy工厂类，包括：
        1. 智能推断字段数据类型和合理测试值
        2. 处理外键关系和唯一约束
        3. 生成完整的测试数据工厂
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            
        Returns:
            生成的Factory代码字符串
        """
        from datetime import datetime
        
        print(f"🏭 开始生成智能测试数据工厂: {module_name}")

        # 获取模型导入路径
        module_import_path = f"app.modules.{module_name}.models"

        # 生成模型导入列表
        model_imports = ', '.join(models.keys()) if models else ""

        # 生成工厂文件头部
        factory_code = f'''"""
智能生成的Factory Boy测试数据工厂 - {module_name}模块

自动生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
生成模型数量: {len(models)}
智能特性: 
- 自动推断字段类型和合理测试值
- 处理外键关系和唯一约束  
- 支持复杂业务场景数据创建

符合标准:
- [CHECK:TEST-002] Factory Boy测试数据标准
- [CHECK:DEV-009] 代码生成质量标准

使用示例:
    from tests.factories.{module_name}_factories import *
    
    # 创建测试数据
    # (具体示例依据实际生成的Factory类)
"""

import factory
import factory.fuzzy
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

# 处理表重定义警告的配置
import warnings
warnings.filterwarnings('ignore', message='.*declarative base.*')
warnings.filterwarnings('ignore', message='.*Table.*already defined.*')

from {module_import_path} import (
    {model_imports}
)


'''

        # 按依赖关系排序模型，确保被依赖的先生成
        sorted_models = self._sort_models_by_dependencies(models)
        
        # 为每个模型生成Factory类
        # 维护已生成的Factory列表，用于检测前向引用
        generated_factories = set()
        for model_name, model_info in sorted_models:
            factory_class = self._generate_single_factory(
                model_name, model_info, models, generated_factories
            )
            factory_code += factory_class + "\n\n"
            generated_factories.add(model_name)

        # 生成工厂管理器类
        manager_class = self._generate_factory_manager(module_name, models)
        factory_code += manager_class

        print(f"✅ 工厂生成完成，共{len(models)}个Factory类")
        return factory_code
    
    def _sort_models_by_dependencies(self, models: Dict[str, ModelInfo]) -> List:
        """按依赖关系对模型排序，确保被依赖的模型先生成工厂类"""
        from typing import Tuple
        
        # 构建依赖图
        dependencies = {}
        print(f"🔍 开始分析模型依赖关系...")
        
        for model_name, model_info in models.items():
            deps = []
            for field in model_info.fields:
                if field.foreign_key:
                    target_model = self._extract_fk_target_model(field.foreign_key, models)
                    # 排除自引用：如果目标模型就是当前模型，不视为依赖
                    if target_model in models and target_model != model_name:
                        deps.append(target_model)
                        print(f"  📎 {model_name}.{field.name} → {target_model} (外键依赖)")
                    elif target_model == model_name:
                        print(f"  🔄 {model_name}.{field.name} → {target_model} (自引用，工厂中将设为None)")
            dependencies[model_name] = deps
            
        print(f"📊 依赖图构建完成: {len(dependencies)} 个模型")
        
        # 拓扑排序
        result = []
        visited = set()
        visiting = set()
        
        def visit(model):
            if model in visiting:
                print(f"⚠️  检测到循环依赖: {model} (跳过以避免无限递归)")
                return
            if model in visited:
                return
            
            visiting.add(model)
            for dep in dependencies.get(model, []):
                if dep in models:
                    visit(dep)
            visiting.remove(model)
            visited.add(model)
            result.append((model, models[model]))
            print(f"  ✅ {model} 添加到创建序列 (位置 {len(result)})")
        
        print(f"🚀 开始拓扑排序...")
        for model_name in models:
            visit(model_name)
        
        print(f"🎯 拓扑排序完成，最终创建顺序:")
        for i, (model_name, _) in enumerate(result, 1):
            print(f"  {i}. {model_name}")
            
        return result
    
    def _extract_fk_target_model(self, foreign_key: str, models: Dict[str, ModelInfo] = None) -> str:
        """从外键字符串提取目标模型名"""
        # foreign_key格式：table_name.column_name
        if '.' in foreign_key:
            table_name = foreign_key.split('.')[0]
            return self._infer_model_name_from_table(table_name, models)
        return foreign_key
    
    def _infer_model_name_from_table(self, table_name: str, models: Dict[str, ModelInfo] = None) -> str:
        """从表名推导模型名 - 纯动态映射版本"""
        # 优先使用动态映射：从models字典中查找表名对应的模型名
        if models:
            for model_name, model_info in models.items():
                if model_info.tablename == table_name:
                    return model_name
        
        # 如果没有找到动态映射，使用通用推导逻辑
        if table_name.endswith('ies'):
            singular = table_name[:-3] + 'y'
        elif table_name.endswith('s'):
            singular = table_name[:-1]
        else:
            singular = table_name
        return ''.join(word.capitalize() for word in singular.split('_'))
    
    def _generate_single_factory(
        self, model_name: str, model_info: ModelInfo, all_models: Dict[str, ModelInfo],
        generated_factories: set = None
    ) -> str:
        """生成单个模型的Factory类"""
        if generated_factories is None:
            generated_factories = set()
        
        factory_name = f"{model_name}Factory"
        
        # 检测是否为联合主键模型
        is_composite_key = len(model_info.primary_keys) > 1
        has_id_field = 'id' in model_info.primary_keys

        # 生成类定义
        class_def = f'''class {factory_name}(factory.alchemy.SQLAlchemyModelFactory):
    """智能生成的{model_name}工厂类"""
    
    class Meta:
        model = {model_name}
        sqlalchemy_session_persistence = "commit"
'''
        
        # 不使用sqlalchemy_get_or_create，因为它与动态session（unit_test_db fixture）不兼容
        # Factory.create(unit_test_db)的方式需要在运行时传入session

        # 生成字段定义
        field_definitions = []
        for field in model_info.fields:
            if field.name in ["id"] and field.primary_key and not is_composite_key:
                continue
            field_def = self._generate_field_definition(field, model_info, all_models, generated_factories)
            if field_def:
                field_definitions.append(f"    {field_def}")

        if field_definitions:
            class_def += "\n" + "\n".join(field_definitions) + "\n"
        else:
            class_def += "\n    pass\n"

        return class_def
    
    def _generate_field_definition(
        self, field: FieldInfo, model_info: ModelInfo, all_models: Dict[str, ModelInfo],
        generated_factories: set = None
    ) -> str:
        """生成单个字段的Factory定义"""
        if generated_factories is None:
            generated_factories = set()
            
        # 处理外键关系
        if field.foreign_key:
            return self._generate_foreign_key_definition(field, all_models, generated_factories)

        # 根据字段类型生成合适的Factory定义
        if field.column_type.upper().startswith("VARCHAR") or field.python_type == "str":
            return self._generate_string_field_definition(field)
        elif field.column_type.upper().startswith("INTEGER") or field.python_type == "int":
            return self._generate_integer_field_definition(field)
        elif field.column_type.upper().startswith("BOOLEAN") or field.python_type == "bool":
            return self._generate_boolean_field_definition(field)
        elif field.column_type.upper().startswith("DECIMAL") or field.python_type == "Decimal":
            return self._generate_decimal_field_definition(field)
        elif field.column_type.upper().startswith("DATETIME") or field.python_type == "datetime":
            return self._generate_datetime_field_definition(field)
        elif field.column_type.upper() == "TEXT":
            return self._generate_text_field_definition(field)
        elif field.column_type.upper() == "JSON" or field.python_type == "dict":
            return self._generate_json_field_definition(field)
        elif field.column_type.upper() == "UUID" or field.python_type == "UUID":
            return self._generate_uuid_field_definition(field)
        else:
            return self._generate_default_field_definition(field)
    
    def _generate_foreign_key_definition(
        self, field: FieldInfo, all_models: Dict[str, ModelInfo],
        generated_factories: set = None
    ) -> str:
        """生成外键字段定义"""
        if not field.foreign_key:
            return f"{field.name} = factory.Sequence(lambda n: n + 1)"
            
        fk_parts = field.foreign_key.split(".")
        if len(fk_parts) != 2:
            return f"{field.name} = factory.Sequence(lambda n: n + 1)"
            
        target_table, target_column = fk_parts
        
        # 查找目标模型
        target_model = None
        for model_name, model_info in all_models.items():
            if model_info.tablename == target_table:
                target_model = model_name
                break
        
        if not target_model:
            target_model = self._infer_model_name_from_table(target_table, all_models)
            
        # 检测自引用
        is_self_reference = self._is_self_reference_field(field.name, target_table)
        
        if is_self_reference:
            return f"{field.name} = None  # 自引用字段，避免循环依赖"
        
        # 检测跨模块依赖
        is_cross_module = self._is_cross_module_dependency(target_model, all_models)
        
        if is_cross_module:
            # 跨模块依赖：使用None或序列ID，避免复杂的跨模块导入
            if field.nullable:
                return f"{field.name} = None  # 跨模块外键，使用None避免导入复杂性 (目标: {target_model})"
            else:
                return f"{field.name} = factory.Sequence(lambda n: n + 1)  # 跨模块外键，使用序列ID"
        
        # 检测前向引用（同模块内）
        is_forward_reference = (generated_factories is not None and 
                               target_model not in generated_factories)
        
        if is_forward_reference and field.nullable:
            return f"{field.name} = None  # 可空外键，避免前向引用错误 (目标: {target_model}Factory)"
        else:
            if field.name.endswith('_id'):
                relation_field = field.name[:-3]
                return f"{relation_field} = factory.SubFactory({target_model}Factory)"
            else:
                return f"{field.name} = factory.SubFactory({target_model}Factory)"
    
    def _is_cross_module_dependency(self, target_model: str, all_models: Dict[str, ModelInfo]) -> bool:
        """检测是否为跨模块依赖
        
        Args:
            target_model: 目标模型名称
            all_models: 当前模块的所有模型
            
        Returns:
            True if target_model is not in current module
        """
        # 如果目标模型不在当前模块的模型列表中，则为跨模块依赖
        return target_model not in all_models
    
    def _is_self_reference_field(self, field_name: str, target_table: str) -> bool:
        """判断是否为自引用字段"""
        self_ref_patterns = [
            'granted_by', 'assigned_by', 'created_by', 'updated_by',
            'parent_id', 'manager_id', 'supervisor_id', 'approved_by',
            'modified_by', 'reviewed_by'
        ]
        return field_name.lower() in self_ref_patterns
    
    def _generate_string_field_definition(self, field: FieldInfo) -> str:
        """生成字符串字段定义"""
        field_name = field.name.lower()

        if "email" in field_name:
            return f"{field.name} = factory.Sequence(lambda n: f'user{{n}}@example.com')"
        elif "username" in field_name or "name" in field_name:
            return f"{field.name} = factory.Sequence(lambda n: f'{field_name}_{{n}}')"
        elif "code" in field_name:
            return f"{field.name} = factory.Sequence(lambda n: f'{field.name.upper()}_{{n:06d}}')"
        elif "description" in field_name:
            return f"{field.name} = factory.Faker('text', max_nb_chars=200)"
        elif "title" in field_name:
            return f"{field.name} = factory.Faker('sentence', nb_words=4)"
        elif "url" in field_name or "link" in field_name:
            return f"{field.name} = factory.Faker('url')"
        elif "phone" in field_name:
            return f"{field.name} = factory.Faker('phone_number')"
        elif "address" in field_name:
            return f"{field.name} = factory.Faker('address')"
        elif "password" in field_name:
            return f"{field.name} = 'hashed_password_123'"
        elif field.unique:
            return f"{field.name} = factory.Sequence(lambda n: f'{field_name}_{{n}}')"
        else:
            max_length = self._extract_string_length(field.column_type)
            if max_length and max_length <= 50:
                return f"{field.name} = factory.Faker('word')"
            else:
                return f"{field.name} = factory.Faker('text', max_nb_chars={min(max_length or 200, 200)})"

    def _generate_integer_field_definition(self, field: FieldInfo) -> str:
        """生成整数字段定义"""
        if field.unique:
            return f"{field.name} = factory.Sequence(lambda n: n + 1)"
        else:
            # 检查是否有 CHECK 约束来确定范围
            min_val, max_val = 1, 1000
            
            for constraint in field.constraints:
                if constraint.get('type') == 'check':
                    expression = constraint.get('expression', '').lower()
                    # 解析类似 "quantity > 0 AND quantity <= 999" 的约束
                    import re
                    
                    # 提取下限：field > min 或 field >= min
                    min_match = re.search(rf'{field.name}\s*>=?\s*(\d+)', expression)
                    if min_match:
                        min_val = int(min_match.group(1))
                        if '>' in expression and '>=' not in expression:
                            min_val += 1  # > 转换为 >=
                    
                    # 提取上限：field < max 或 field <= max
                    max_match = re.search(rf'{field.name}\s*<=?\s*(\d+)', expression)
                    if max_match:
                        max_val = int(max_match.group(1))
                        if '<' in expression and '<=' not in expression:
                            max_val -= 1  # < 转换为 <=
            
            return f"{field.name} = factory.Faker('random_int', min={min_val}, max={max_val})"

    def _generate_boolean_field_definition(self, field: FieldInfo) -> str:
        """生成布尔字段定义"""
        field_name = field.name.lower()
        if any(word in field_name for word in ["active", "enabled", "verified", "valid"]):
            return f"{field.name} = True"
        elif any(word in field_name for word in ["deleted", "disabled", "hidden"]):
            return f"{field.name} = False"
        else:
            return f"{field.name} = factory.Faker('boolean')"

    def _generate_decimal_field_definition(self, field: FieldInfo) -> str:
        """生成Decimal字段定义"""
        field_name = field.name.lower()
        if "price" in field_name or "cost" in field_name or "amount" in field_name:
            return f"{field.name} = factory.LazyAttribute(lambda obj: Decimal('99.99'))"
        elif "rate" in field_name or "ratio" in field_name:
            return f"{field.name} = factory.LazyAttribute(lambda obj: Decimal('0.1'))"
        else:
            return f"{field.name} = factory.LazyAttribute(lambda obj: Decimal('10.00'))"

    def _generate_datetime_field_definition(self, field: FieldInfo) -> str:
        """生成datetime字段定义"""
        field_name = field.name.lower()
        if "created" in field_name:
            return f"{field.name} = factory.LazyFunction(datetime.now)"
        elif "updated" in field_name or "modified" in field_name:
            return f"{field.name} = factory.LazyFunction(datetime.now)"
        elif "expired" in field_name or "expires" in field_name:
            return f"{field.name} = factory.LazyFunction(lambda: datetime.now() + timedelta(days=30))"
        else:
            return f"{field.name} = factory.Faker('date_time_this_year')"

    def _generate_text_field_definition(self, field: FieldInfo) -> str:
        """生成TEXT字段定义"""
        field_name = field.name.lower()
        if "description" in field_name or "content" in field_name:
            return f"{field.name} = factory.Faker('text', max_nb_chars=200)"
        elif "note" in field_name or "comment" in field_name:
            return f"{field.name} = factory.Faker('sentence', nb_words=10)"
        else:
            return f"{field.name} = factory.Faker('text', max_nb_chars=100)"

    def _generate_json_field_definition(self, field: FieldInfo) -> str:
        """生成JSON字段定义"""
        field_name = field.name.lower()
        if "config" in field_name or "setting" in field_name:
            return f"{field.name} = factory.LazyAttribute(lambda obj: {{'enabled': True, 'timeout': 30}})"
        elif "metadata" in field_name or "meta" in field_name:
            return f"{field.name} = factory.LazyAttribute(lambda obj: {{'version': '1.0', 'source': 'test'}})"
        elif "attribute" in field_name or "attrs" in field_name:
            return f"{field.name} = factory.LazyAttribute(lambda obj: {{'color': 'blue', 'size': 'M'}})"
        else:
            return f"{field.name} = factory.LazyAttribute(lambda obj: {{'key': 'value'}})"

    def _generate_uuid_field_definition(self, field: FieldInfo) -> str:
        """生成UUID字段定义"""
        return f"{field.name} = factory.LazyFunction(uuid.uuid4)"

    def _generate_default_field_definition(self, field: FieldInfo) -> str:
        """生成默认字段定义"""
        if field.nullable:
            return f"{field.name} = None"
        else:
            return f"{field.name} = factory.Faker('word')"

    def _extract_string_length(self, column_type: str) -> int:
        """从列类型字符串中提取长度限制"""
        try:
            column_type_upper = column_type.upper()
            if "VARCHAR(" in column_type_upper:
                start = column_type_upper.find("VARCHAR(") + 8
                remaining = column_type[start:]
                if ")" in remaining:
                    end_pos = remaining.find(")")
                    if "," in remaining[:end_pos]:
                        length_str = remaining[: remaining.find(",")]
                    else:
                        length_str = remaining[:end_pos]
                    length_str = length_str.strip()
                    if length_str.isdigit():
                        return int(length_str)
        except (ValueError, IndexError, AttributeError):
            pass
        return None
    
    def _generate_factory_manager(
        self, module_name: str, models: Dict[str, ModelInfo]
    ) -> str:
        """生成工厂管理器类"""
        sorted_models = self._sort_models_by_dependencies(models)
        
        manager_class = f'''class {module_name.title().replace("_", "")}FactoryManager:
    """智能生成的{module_name}模块工厂管理器
    
    提供便捷的测试数据创建方法和常见业务场景的数据组合
    """
    
    @staticmethod
    def setup_factories(session):
        """设置所有工厂的数据库会话"""
'''

        for model_name, _ in sorted_models:
            factory_name = f"{model_name}Factory"
            manager_class += f"        {factory_name}._meta.sqlalchemy_session = session\n"

        manager_class += f'''
    @staticmethod
    def create_sample_data(session) -> dict:
        """创建样本测试数据 - 按依赖顺序创建避免外键约束失败"""
        {module_name.title().replace("_", "")}FactoryManager.setup_factories(session)
        
        data = {{}}
'''

        # 检测所有模型的跨模块外键依赖
        cross_module_deps = self._detect_cross_module_dependencies(models)
        
        # 生成跨模块依赖创建代码
        if cross_module_deps:
            manager_class += "        \n"
            manager_class += "        # 导入所有跨模块依赖的Factory\n"
            
            # 按模块分组收集所有Factory
            deps_by_module = {}
            for dep_module, dep_factory, dep_key in cross_module_deps:
                if dep_module not in deps_by_module:
                    deps_by_module[dep_module] = []
                deps_by_module[dep_module].append((dep_factory, dep_key))
            
            # 生成import语句
            for dep_module, factories in deps_by_module.items():
                factory_names = [f for f, _ in factories]
                manager_class += f"        from tests.factories.{dep_module}_factories import {', '.join(factory_names)}\n"
            
            manager_class += "        \n"
            manager_class += "        # 设置所有Factory的session\n"
            for dep_module, factories in deps_by_module.items():
                for factory_name, _ in factories:
                    manager_class += f"        {factory_name}._meta.sqlalchemy_session = session\n"
            
            manager_class += "        \n"
            manager_class += "        data = {}\n"
            manager_class += "        \n"
            
            # 按依赖顺序生成创建代码
            ordered_deps = self._order_dependencies_by_chain(cross_module_deps)
            
            for step_num, (dep_module, dep_factory, dep_key, params) in enumerate(ordered_deps, 1):
                manager_class += f"        # {step_num}. 创建{dep_key.capitalize()}，满足外键约束\n"
                if params:
                    manager_class += f"        data['{dep_key}'] = {dep_factory}({params})\n"
                else:
                    manager_class += f"        data['{dep_key}'] = {dep_factory}()\n"
            
            manager_class += "        \n"

        # 计算起始步骤号
        start_step = len(cross_module_deps) + 1 if cross_module_deps else 1
        
        for idx, (model_name, _) in enumerate(sorted_models, start=start_step):
            factory_name = f"{model_name}Factory"
            # 检查是否需要传入跨模块外键ID或同模块依赖
            fk_params = self._get_factory_fk_params(model_name, models, cross_module_deps)
            
            manager_class += f"        # {idx}. 创建{model_name}\n"
            if fk_params:
                manager_class += f"        data['{model_name.lower()}'] = {factory_name}({fk_params})\n"
            else:
                manager_class += f"        data['{model_name.lower()}'] = {factory_name}()\n"

        manager_class += '''        
        session.commit()
        return data
        
    @staticmethod
    def create_test_scenario(session, scenario: str = 'basic') -> dict:
        """创建特定测试场景的数据"""
        return ''' + f"{module_name.title().replace('_', '')}FactoryManager.create_sample_data(session)"

        return manager_class
    
    def _detect_cross_module_dependencies(self, models: Dict[str, ModelInfo]) -> List[Tuple[str, str, str]]:
        """检测所有模块的跨模块外键依赖
        
        Returns:
            List[Tuple[module_name, factory_name, data_key]]
            例如: [('user_auth', 'UserFactory', 'user'), ('product_catalog', 'SKUFactory', 'sku')]
        """
        dependencies = []
        seen_deps = set()
        
        # 从配置获取表→模块映射和依赖链配置
        table_to_module = self.config.get('business_logic_patterns', {}).get('table_to_module_mapping', {})
        dependency_chains = self.config.get('business_logic_patterns', {}).get('cross_module_dependency_chains', {})
        
        # 获取当前模块名（从models推断）
        current_module = None
        for model_name in models.keys():
            # 简单推断：从第一个模型推断模块（shopping_cart有Cart模型）
            # 更好的方式是从project_root推断
            pass
        
        for model_name, model_info in models.items():
            for field in model_info.fields:
                if field.foreign_key:
                    target_table = field.foreign_key.split('.')[0]
                    target_model = self._infer_model_name_from_table(target_table, models)
                    
                    # 检查是否跨模块
                    is_cross_module = self._is_cross_module_dependency(target_model, models)
                    
                    if is_cross_module:
                        # 使用配置查找模块名
                        dep_module = table_to_module.get(target_table)
                        
                        if not dep_module:
                            # 如果配置中没有，尝试从表名推断
                            print(f"⚠️ 警告: 表 '{target_table}' 未在配置中找到模块映射，跳过")
                            continue
                        
                        # Factory名和data_key从target_model推断
                        dep_factory = f"{target_model}Factory"
                        dep_key = target_model.lower()
                        
                        dep_tuple = (dep_module, dep_factory, dep_key)
                        if dep_tuple not in seen_deps:
                            dependencies.append(dep_tuple)
                            seen_deps.add(dep_tuple)
        
        # 扩展依赖链（例如：如果需要SKU，也需要Product、Brand、Category）
        dependencies = self._expand_dependency_chain(dependencies, table_to_module)
        
        return dependencies
    
    def _expand_dependency_chain(self, dependencies: List[Tuple[str, str, str]], 
                                 table_to_module: Dict[str, str]) -> List[Tuple[str, str, str]]:
        """扩展依赖链，添加间接依赖
        
        例如：SKU需要Product，Product需要Category和Brand
        """
        expanded = list(dependencies)
        seen = set(dependencies)
        
        # 定义依赖链规则
        dependency_rules = {
            'sku': ['product', 'category', 'brand'],  # SKU需要完整的Product链
            'product': ['category', 'brand'],  # Product需要Category和Brand
            'orderitem': ['user', 'sku', 'product', 'category', 'brand'],  # OrderItem需要完整链
            'cartitem': ['user', 'sku', 'product', 'category', 'brand'],  # CartItem需要完整链
        }
        
        # 检查每个依赖是否需要扩展
        for dep_module, dep_factory, dep_key in dependencies:
            if dep_key in dependency_rules:
                required_deps = dependency_rules[dep_key]
                
                for required_key in required_deps:
                    # 查找这个required_key对应的模块
                    # 从table_to_module反向推断
                    found = False
                    for table_name, module_name in table_to_module.items():
                        model_name = self._infer_model_name_from_table(table_name, {})
                        if model_name.lower() == required_key:
                            req_tuple = (module_name, f"{model_name}Factory", required_key)
                            if req_tuple not in seen:
                                expanded.append(req_tuple)
                                seen.add(req_tuple)
                            found = True
                            break
                    
                    if not found:
                        print(f"⚠️ 警告: 无法找到依赖 '{required_key}' 的模块")
        
        return expanded
    
    def _order_dependencies_by_chain(self, dependencies: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str, str]]:
        """按依赖链顺序排序依赖，并添加创建参数
        
        Returns:
            List[Tuple[module, factory, key, params]]
            例如: [('product_catalog', 'CategoryFactory', 'category', ''),
                   ('product_catalog', 'BrandFactory', 'brand', ''),
                   ('product_catalog', 'ProductFactory', 'product', 'category_id=data["category"].id, brand_id=data["brand"].id')]
        """
        # 定义创建顺序和参数依赖
        creation_order = {
            'user': (1, ''),
            'category': (2, ''),
            'brand': (3, ''),
            'product': (4, 'category_id=data["category"].id, brand_id=data["brand"].id'),
            'sku': (5, 'product_id=data["product"].id'),
        }
        
        ordered = []
        for dep_module, dep_factory, dep_key in dependencies:
            order, params = creation_order.get(dep_key, (999, ''))
            ordered.append((order, dep_module, dep_factory, dep_key, params))
        
        # 按order排序
        ordered.sort(key=lambda x: x[0])
        
        # 返回时去掉order
        return [(m, f, k, p) for _, m, f, k, p in ordered]
    
    def _get_factory_fk_params(self, model_name: str, models: Dict[str, ModelInfo], 
                                cross_module_deps: List[Tuple[str, str, str]]) -> str:
        """获取Factory创建时需要传入的外键参数
        
        Args:
            model_name: 当前模型名
            models: 所有模型信息
            cross_module_deps: 跨模块依赖列表
            
        Returns:
            参数字符串，如 "user_id=data['user'].id, sku_id=data['sku'].id"
        """
        if model_name not in models:
            return ""
        
        model_info = models[model_name]
        params = []
        
        for field in model_info.fields:
            if field.foreign_key:
                target_table = field.foreign_key.split('.')[0]
                target_model = self._infer_model_name_from_table(target_table, models)
                
                # 检查是否跨模块
                is_cross_module = self._is_cross_module_dependency(target_model, models)
                
                if is_cross_module:
                    # 查找对应的依赖key（从target_model生成）
                    dep_key = target_model.lower()
                    
                    # 验证这个key是否在依赖列表中
                    found = False
                    for dep_module, dep_factory, check_key in cross_module_deps:
                        if check_key == dep_key:
                            params.append(f"{field.name}=data['{dep_key}'].id")
                            found = True
                            break
                    
                    if not found:
                        print(f"⚠️ 警告: 未找到 {target_model} 的依赖，字段 {field.name} 可能需要手动处理")
                        
                elif field.name.endswith('_id'):
                    # 同模块内的外键，使用SubFactory或前置创建的实体
                    relation_name = field.name[:-3]  # user_id -> user
                    relation_model = relation_name.capitalize()
                    if relation_model in [m.capitalize() for m in models.keys()]:
                        params.append(f"{relation_name}=data['{relation_name.lower()}']")
        
        return ", ".join(params)
