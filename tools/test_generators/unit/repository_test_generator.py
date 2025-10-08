"""
Repository测试生成器 - 符合testing-standards.md v2.0.0

职责：
生成Repository层的完整CRUD测试代码，包括：
1. Create测试 - 最小字段/完整字段/事务提交/事务回滚
2. Read测试 - found/not_found，支持联合主键
3. Update测试 - 单字段/多字段/事务提交/专用方法
4. Delete测试 - 物理删除/软删除/级联删除/批量删除
5. Count测试 - 基础计数测试
6. Query测试 - 自定义查询测试

测试策略：
- 使用unit_test_db fixture（SQLite内存数据库）
- 使用Factory Boy生成测试数据
- 验证SQL正确性和数据持久化

版本: v1.0
创建时间: 2025-10-08
从generate_test_template.py提取
"""
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from ..core import FieldInfo, ModelInfo, RepositoryMethodInfo, RepositoryInfo


class RepositoryTestGenerator:
    """Repository测试生成器
    
    重构策略：
    - 阶段A: 创建框架，保持对主程序方法的引用
    - 阶段B: 逐步迁移方法实现到此类
    - 阶段C: 移除对主程序的依赖
    
    当前阶段：A（框架完成，使用主程序方法）
    """
    
    def __init__(self, project_root: Path, config: Dict, main_generator=None):
        """初始化生成器
        
        Args:
            project_root: 项目根目录
            config: 配置字典
            main_generator: 主生成器实例（用于调用现有方法）
        """
        self.project_root = project_root
        self.config = config
        self.main_generator = main_generator  # 临时：引用主程序的方法
    
    def generate_repository_tests(
        self,
        module_name: str,
        models: Dict[str, ModelInfo],
        repositories: Dict[str, RepositoryInfo]
    ) -> str:
        """生成Repository测试代码（主入口）
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            repositories: Repository信息字典
            
        Returns:
            生成的测试代码字符串
        """
        # 使用主程序的实现（阶段A）
        if self.main_generator:
            return self.main_generator._generate_repository_tests(module_name, repositories, models)
        
        # 如果没有主程序引用，返回占位符
        return f"""
# Repository测试生成器占位符
# 待从generate_test_template.py迁移实现
# 模块: {module_name}
# Repositories: {len(repositories)}
"""
    
    def generate_repository_create_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Create测试（4种测试）
        
        1. test_create_minimal_fields - 最小必填字段
        2. test_create_full_fields - 完整字段
        3. test_create_transaction_commit - 事务提交
        4. test_create_transaction_rollback - 事务回滚
        """
        # TODO: 从主程序迁移实现
        return ""
    
    def generate_repository_read_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Read测试（2种测试）
        
        1. test_read_found - 查询到数据
        2. test_read_not_found - 数据不存在
        """
        # TODO: 从主程序迁移实现
        return ""
    
    def generate_repository_update_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Update测试（4种测试）
        
        1. test_update_single_field - 单字段更新
        2. test_update_multiple_fields - 多字段更新
        3. test_update_transaction_commit - 事务提交
        4. test_update_specialized_method - 专用方法
        """
        # TODO: 从主程序迁移实现
        return ""
    
    def generate_repository_delete_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Delete测试（3-6种测试）
        
        软删除:
        1. test_delete_soft_delete - 软删除验证
        2. test_delete_cascade_soft_delete - 级联软删除
        3. test_delete_batch_soft_delete - 批量软删除
        
        物理删除:
        1. test_delete_physical_delete - 物理删除验证
        2. test_delete_cascade_delete - 级联物理删除
        3. test_delete_batch_delete - 批量物理删除
        """
        # TODO: 从主程序迁移实现
        return ""
    
    def generate_repository_count_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Count测试"""
        # TODO: 从主程序迁移实现
        return ""
    
    def generate_repository_query_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Query测试"""
        # TODO: 从主程序迁移实现
        return ""
    
    # ========== 辅助方法 ==========
    
    def _get_minimal_test_value(self, field: FieldInfo) -> str:
        """获取字段的最小测试值(用于最小实体创建)
        
        策略:
        - 字符串: 最小长度 (如果有MinLength约束)
        - 数字: 最小值 (如果有Min约束)
        - 布尔: False
        - 枚举: 第一个值
        """
        field_type = field.column_type.lower()
        
        # 字符串类型
        if 'str' in field_type or 'varchar' in field_type or 'text' in field_type:
            # 检查是否有长度约束
            if hasattr(field, 'length') and field.length:
                return f'"{field.name[:1]}"'  # 单字符
            return f'"{field.name}"'  # 使用字段名作为值
        
        # 整数类型
        if 'int' in field_type:
            return '1'
        
        # 浮点数类型
        if 'float' in field_type or 'decimal' in field_type:
            return '0.01'
        
        # 布尔类型
        if 'bool' in field_type:
            return 'False'
        
        # 日期时间类型
        if 'datetime' in field_type:
            return 'datetime.now()'
        if 'date' in field_type:
            return 'date.today()'
        
        # 默认值
        return f'"{field.name}"'
    
    def _get_test_value_for_field(self, field: FieldInfo, suffix: str = "测试") -> str:
        """为字段生成测试值
        
        Args:
            field: 字段信息
            suffix: 值的后缀
            
        Returns:
            str: 测试值的字符串表示
        """
        field_name = field.name.lower()
        
        # 修复: 先按字段类型判断(类型优先),再按字段名模式匹配(语义推断)
        # 这样可以避免 email_verified 等 Boolean 字段被错误地当作 email 类型处理
        
        # 1. 明确的类型判断(优先级最高)
        if field.python_type == 'bool':
            return 'True'
        elif field.python_type == 'int':
            return '1'
        elif field.python_type == 'Decimal':
            return 'Decimal("10.00")'
        elif field.python_type == 'datetime':
            return 'datetime.now()'
        
        # 2. 字符串类型的语义推断(通过字段名)
        elif field.python_type == 'str':
            if 'email' in field_name:
                return f'"test_{suffix.lower()}@example.com"'
            elif 'slug' in field_name:
                return f'"test-{suffix.lower()}"'
            elif 'code' in field_name or 'sku' in field_name:
                return f'"TEST{suffix.upper()}"'
            elif 'url' in field_name:
                return f'"https://example.com/{suffix.lower()}"'
            elif field_name == 'status':
                return '"active"'
            elif field_name == 'role':
                return '"user"'
            elif 'name' in field_name:
                return f'"{suffix}"'
            else:
                return f'"{suffix}"'
        
        # 3. 兜底默认值
        else:
            return f'"{suffix}"'
    
    def _generate_minimal_entity_creation(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        module_name: str
    ) -> str:
        """生成最小实体创建代码(仅必填字段,符合testing-standards.md 2.1节)
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            module_name: 模块名称
            
        Returns:
            str: 最小实体创建代码(多行,含缩进)
        """
        if model_name not in models:
            return f'        entity = {model_name}()  # TODO: 补充必填字段'
        
        model_info = models[model_name]
        
        # 提取必填字段(nullable=False 且无default)
        auto_fields = {'id', 'created_at', 'updated_at', 'is_deleted'}
        required_fields = [
            f for f in model_info.fields 
            if not f.nullable 
            and f.name not in auto_fields 
            and not (f.primary_key and f.name == 'id')
            and not f.server_default  # 排除有数据库默认值的字段
            # 注意: 如果field有default参数,仍然包括(用于测试默认值)
        ]
        
        if not required_fields:
            return f'        entity = {model_name}()\n        # 注意: 该模型所有字段均为可选或有默认值'
        
        # 分离外键和普通字段
        fk_fields = [f for f in required_fields if f.foreign_key]
        normal_fields = [f for f in required_fields if not f.foreign_key]
        
        lines = []
        
        # 先创建外键依赖
        fk_var_names = {}
        for field in fk_fields:
            fk_target = field.foreign_key
            fk_table = fk_target.split('.')[0]
            fk_model_name = self._table_name_to_model_name(fk_table)
            fk_var_name = fk_model_name.lower()
            
            # 使用Factory Boy创建依赖实体(简化)
            lines.append(f'from tests.factories.{module_name}_factories import {fk_model_name}Factory')
            lines.append(f'{fk_var_name} = {fk_model_name}Factory.create()')
            fk_var_names[field.name] = f'{fk_var_name}.id'
        
        if fk_fields:
            lines.append('')  # 空行分隔
        
        # 构造最小实体
        field_assignments = []
        for field in normal_fields:
            test_value = self._get_minimal_test_value(field)
            field_assignments.append(f'{field.name}={test_value}')
        
        # 添加外键字段
        for field in fk_fields:
            field_assignments.append(f'{field.name}={fk_var_names[field.name]}')
        
        if field_assignments:
            lines.append(f'entity = {model_name}(')
            for i, assignment in enumerate(field_assignments):
                comma = ',' if i < len(field_assignments) - 1 else ''
                lines.append(f'    {assignment}{comma}')
            lines.append(')')
        else:
            lines.append(f'entity = {model_name}()')
        
        # 添加缩进
        return '\n        '.join(lines)
    
    def _generate_test_entity_creation(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        suffix: str = "测试数据",
        with_dependencies: bool = False
    ) -> str:
        """生成测试实体创建代码,自动包含必填字段和外键依赖
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            suffix: 名称后缀
            with_dependencies: 是否生成外键依赖的完整代码(多行)
            
        Returns:
            str: 实体创建代码(可能是多行的依赖创建+主实体创建)
        """
        if model_name not in models:
            # 如果模型信息不存在,返回简单的创建代码并添加TODO
            return f'{model_name}(name="{suffix}")  # TODO: 根据实际字段调整'
        
        model_info = models[model_name]
        
        # 提取所有非nullable的字段(排除id和自动字段)
        auto_fields = {'id', 'created_at', 'updated_at', 'is_deleted'}
        required_fields = [
            f for f in model_info.fields 
            # 修复: 不排除作为外键的主键字段(如UserRole的联合主键)
            # 只排除自增主键(field.name == 'id')
            if not f.nullable and f.name not in auto_fields and not (f.primary_key and f.name == 'id')
        ]
        
        # 分离外键字段和普通字段
        fk_fields = [f for f in required_fields if f.foreign_key]
        normal_fields = [f for f in required_fields if not f.foreign_key]
        
        if not required_fields:
            # 如果没有必填字段,使用简单形式
            return f'{model_name}()'
        
        # 如果不需要生成依赖,或没有外键字段,生成简单单行形式
        if not with_dependencies or not fk_fields:
            field_assignments = []
            for field in required_fields:
                test_value = self._get_test_value_for_field(field, suffix)
                field_assignments.append(f'{field.name}={test_value}')
            # 返回不带变量赋值的表达式(用于单行赋值: entity = XXX())
            return f'{model_name}({", ".join(field_assignments)})'
        
        # 生成完整的依赖创建代码(多行)
        lines = []
        fk_var_names = {}
        
        # 为每个外键字段创建依赖实体
        for field in fk_fields:
            # 解析外键目标: 'products.id' -> table='products', column='id'
            fk_target = field.foreign_key
            fk_table = fk_target.split('.')[0]
            
            # 推断模型名(表名转模型名: products -> Product, categories -> Category)
            fk_model_name = self._table_name_to_model_name(fk_table)
            # 使用相同的单数化逻辑作为变量名(小写)
            fk_var_name = self._table_name_to_model_name(fk_table).lower()
            
            # 递归生成依赖实体(不再生成依赖的依赖,避免无限递归)
            fk_entity_code = self._generate_test_entity_creation(fk_model_name, models, f"依赖{suffix}", with_dependencies=False)
            lines.append(f'{fk_var_name} = {fk_entity_code}')
            lines.append(f'unit_test_db.add({fk_var_name})')
            lines.append(f'unit_test_db.commit()')
            
            # 记录变量名,用于后续引用
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
    
    def _get_minimal_test_value(self, field: FieldInfo) -> str:
        """获取字段的最小测试值"""
        # TODO: 从主程序迁移实现
        return '""'
    
    def _get_test_value_for_field(self, field: FieldInfo, suffix: str) -> str:
        """获取字段的测试值"""
        # TODO: 从主程序迁移实现
        return '""'
    
    def _has_composite_primary_key(
        self,
        model_name: str,
        models: Dict[str, ModelInfo]
    ) -> bool:
        """检查模型是否使用联合主键(多个primary_key字段)"""
        if model_name not in models:
            return False
        model_info = models[model_name]
        primary_key_count = sum(1 for f in model_info.fields if f.primary_key)
        return primary_key_count > 1
    
    def _get_primary_key_fields(
        self,
        model_name: str,
        models: Dict[str, ModelInfo]
    ) -> List[FieldInfo]:
        """获取模型的主键字段列表"""
        if model_name not in models:
            return []
        model_info = models[model_name]
        return [f for f in model_info.fields if f.primary_key]
    
    def _infer_query_parameter(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        models: Dict[str, ModelInfo]
    ) -> Tuple[str, str, bool]:
        """推断自定义查询方法需要的参数(通用化改进版)
        
        通过分析方法签名自动推断参数:
        - get_by_username -> entity.username
        - get_user_roles(user_id: int) -> 需要创建User,传入user.id
        - get_role_users(role_id: int) -> 需要创建Role,传入role.id
        - get (联合主键) -> 需要所有主键字段
        
        Args:
            method_info: 方法信息(包含参数签名)
            model_name: 模型名称
            models: 所有模型信息
            
        Returns:
            tuple: (准备代码, 参数字符串, 是否需要TODO注释)
                - setup_code: 创建依赖实体的代码(如创建User)
                - param_str: 调用方法时的参数字符串(如user.id)
                - needs_todo: 是否需要TODO注释
        """
        method_name = method_info.name
        
        # 提取方法参数(排除self, db, cls)
        method_params = [p for p in method_info.parameters if p[0] not in ['self', 'db', 'cls']]
        
        # 特殊处理check_exists方法(可选参数组合)
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
        
        # 智能推断: 分析方法参数,自动生成依赖实体
        if method_params:
            setup_code_lines = []
            param_parts = []
            
            for param_name, param_type in method_params:
                # 推断参数对应的实体类型
                # user_id: int -> User
                # role_id: int -> Role
                # permission_id: int -> Permission
                entity_name = self._infer_entity_from_param(param_name, param_type, models)
                
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
                    # 无法推断实体,尝试从方法名推断字段
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
                        # 复杂类型,需要TODO
                        return ('', '', True)
            
            setup_code = '\n        '.join(setup_code_lines) if setup_code_lines else ''
            param_str = ', '.join(param_parts)
            return (setup_code, param_str, False)
        
        # 提取方法名中的字段名(兼容老逻辑)
        if method_name.startswith('get_by_'):
            field_part = method_name[7:]  # 移除'get_by_'
            # 特殊处理复合查询(如username_or_email)
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
            # 默认使用id(如果有的话)
            has_composite_pk = self._has_composite_primary_key(model_name, models)
            if has_composite_pk:
                # 联合主键模型需要TODO
                return ('', '', True)
            return ('', 'entity.id', False)
    
    def _infer_entity_from_param(
        self,
        param_name: str,
        param_type: str,
        models: Dict[str, ModelInfo]
    ) -> Optional[str]:
        """从参数名和类型推断对应的实体类型(通用化推断)
        
        推断规则:
        1. user_id: int -> User (ID参数)
        2. user: User -> User (对象参数)
        3. role_id: int -> Role (ID参数)
        4. role: Role -> Role (对象参数)
        
        Args:
            param_name: 参数名(如user_id或user)
            param_type: 参数类型(如int或User)
            models: 所有模型信息
            
        Returns:
            str: 实体名称(如User),如果无法推断返回None
        """
        # 情况1: 对象类型参数(如user: User)
        # 检查参数类型是否直接是模型名
        if param_type in models:
            return param_type
        
        # 情况2: ID参数(如user_id: int)
        if param_type == 'int' and param_name.endswith('_id'):
            # 提取实体名: user_id -> user -> User
            entity_base = param_name[:-3]  # 移除'_id'
            
            # 尝试各种命名变体
            candidates = [
                entity_base.title(),  # user -> User
                entity_base.capitalize(),  # user -> User
                entity_base.upper(),  # user -> USER
                ''.join(word.capitalize() for word in entity_base.split('_'))  # user_role -> UserRole
            ]
            
            for candidate in candidates:
                if candidate in models:
                    return candidate
        
        # 情况3: 对象参数但类型名不标准(如user: 'User'带引号)
        # 尝试从参数名推断
        candidates = [
            param_name.title(),  # user -> User
            param_name.capitalize(),  # user -> User
            ''.join(word.capitalize() for word in param_name.split('_'))  # user_role -> UserRole
        ]
        
        for candidate in candidates:
            if candidate in models:
                return candidate
        
        return None
    
    def _table_name_to_model_name(self, table_name: str) -> str:
        """表名转模型名: products -> Product, categories -> Category"""
        # 移除复数s
        if table_name.endswith('ies'):
            singular = table_name[:-3] + 'y'  # categories -> category
        elif table_name.endswith('s'):
            singular = table_name[:-1]  # products -> product
        else:
            singular = table_name
        
        # 首字母大写
        return singular.capitalize()
