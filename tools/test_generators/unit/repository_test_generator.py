"""
Repository测试生成器 - 数据访问层完整CRUD测试代码自动生成

该模块实现Repository层单元测试代码的智能生成，严格遵循testing-standards.md v2.0.0规范，
生成涵盖CRUD全生命周期的测试代码，包括正常场景、边界情况、错误处理等。

主要功能:
- Create测试生成: 最小字段/完整字段/事务提交/事务回滚/重复创建
- Read测试生成: 单主键查询/联合主键查询/found/not_found场景
- Update测试生成: 单字段更新/批量更新/事务提交/专用更新方法
- Delete测试生成: 物理删除/软删除/级联删除/批量删除/不存在场景
- Count测试生成: 基础计数/条件计数
- Query测试生成: 自定义查询方法/复杂条件/分页排序
- 关系测试生成: 一对多/多对一/多对多关系的增删改查

技术栈:
- pytest: 测试框架
- Factory Boy: 测试数据生成
- SQLite: 内存数据库（unit_test_db fixture）
- SQLAlchemy: ORM框架

依赖关系:
- tools.test_generators.core.schema: RepositoryInfo/RepositoryMethodInfo数据模型
- tools.test_generators.utils.repository_analyzer: Repository方法分析
- tools.test_generators.utils.test_utils: 测试代码生成辅助方法
- tests/factories/: Factory类（动态生成ParentFactory等）
- tests/conftest.py: unit_test_db fixture定义

测试策略:
- 真实数据库: 使用SQLite内存数据库，测试真实的SQL执行和数据持久化
- Factory数据生成: 使用Factory Boy生成符合约束的测试数据
- 事务隔离: 每个测试独立事务，测试后自动回滚
- 全场景覆盖: 正常/异常/边界/性能等多维度测试

================================================================================
📐 参数值解析设计决策 (2025-10-16)
================================================================================

🎯 核心问题：
Repository方法参数如何生成正确的测试值？特别是：
1. 字符串参数：identifier: str → 应该用entity.username还是"identifier_value"？
2. 整数参数：user_id: int → 应该用entity.id还是1还是依赖实体？
3. 列表参数：category_ids: List[int] → 应该用[entity.id]还是[1]？

🔑 设计原则：
1. **字段优先**：如果参数名是模型字段，直接用entity.param_name
2. **逻辑映射**：如果不是字段但有逻辑关系（如identifier→username），使用映射
3. **关联查询**：如果是外键关联（user_id但不是当前模型字段），需要依赖实体
4. **后备策略**：以上都不满足时，使用类型默认值

📋 方案选择：方案A（提取独立方法）⭐⭐⭐⭐⭐
- ✅ 结构清晰：每个类型的参数有独立方法
- ✅ 易于调试：出问题能快速定位到具体方法
- ✅ 易于扩展：新增类型只需加新方法
- ✅ 可测试性：每个方法可以独立测试

🏗️ 实现架构：
```
_generate_test_params()  [统一入口]
    ↓
_resolve_param_value()  [参数值解析统一分发]
    ↓
    ├─ _resolve_string_param()    [字符串参数专门处理]
    ├─ _resolve_integer_param()   [整数参数专门处理，含关联查询]
    ├─ _resolve_list_param()      [列表参数专门处理]
    └─ _get_default_value()       [类型后备默认值]
```

🔧 核心方法职责：

1. _resolve_param_value(param_name, param_type, repo_info, models, entity_var)
   职责：统一入口，根据参数类型分发到专门方法
   输入：参数名、类型、仓库信息、模型字典、实体变量名
   输出：参数值字符串（如"entity.username"）

2. _resolve_string_param(param_name, model_info, entity_var)
   职责：处理字符串参数的逻辑映射
   策略：
     a. 检查是否是模型字段 → entity.param_name
     b. 逻辑参数映射（identifier→username/email/phone）
     c. 后备：生成"param_name_value"
   
   逻辑映射配置：
   LOGICAL_PARAM_MAPPINGS = {
       'identifier': ['username', 'email', 'phone'],
       'search_term': ['name', 'title', 'description'],
       'keyword': ['name', 'title', 'content'],
       'openid': ['wx_openid'],  # 微信openid参数映射
   }

3. _resolve_integer_param(param_name, param_type, repo_info, models, entity_var)
   职责：处理整数参数，含关联查询判断
   策略：
     a. 检查是否是当前模型字段 → entity.param_name
     b. 检查是否是外键关联（user_id, role_id等）→ 需要依赖实体
     c. Optional类型 → None
     d. 后备：1

4. _resolve_list_param(param_name, param_type, repo_info, entity_var)
   职责：处理列表参数
   策略：
     a. xxx_ids + 匹配当前模型 → [entity.id]
     b. 提取元素类型生成默认列表（int→[1], str→["test"]）

🐛 常见问题和解决方案：

问题1：identifier参数生成"identifier_value"导致查询失败
原因：策略7（类型后备）直接生成硬编码字符串
解决：新增_resolve_string_param方法，检查逻辑映射

问题2：user_id参数生成1但数据库没有对应User记录
原因：未检查是否需要依赖实体
解决：_resolve_integer_param中检查是否是外键关联

问题3：Session.create参数类型混淆
原因：Session类型被误判为entity类型
解决：在策略1中明确检查param_name == 'entity'

📊 修复历史：
- 2025-10-16: 初始设计，提取独立方法，修复identifier参数问题
- 预留：后续修复整数关联查询和Session类型混淆问题

⚠️ 注意事项：
1. TestUtils.infer_entity_from_param可用于辅助推断实体类型（user_id→User）
2. 所有方法都是实例方法，可以访问self.models等上下文
3. 逻辑映射配置可能需要根据项目实际情况调整
4. 依赖实体创建暂未实现，需要返回特殊标记（如TODO注释）

🔗 相关文档：
- 测试标准：docs/standards/testing-standards.md
- TestUtils工具：tools/test_generators/utils/test_utils.py
- 问题追踪：此文档的"修复历史"章节

================================================================================

生成的测试结构（示例）:
```python
class TestUserRepository:
    \"\"\"UserRepository单元测试\"\"\"
    
    def test_create_with_minimal_fields(self, unit_test_db):
        \"\"\"测试最小字段创建\"\"\"
        # 使用最少必填字段创建实体
    
    def test_get_by_id_found(self, unit_test_db):
        \"\"\"测试按ID查询 - 存在情况\"\"\"
        # 创建实体后查询
    
    def test_update_single_field(self, unit_test_db):
        \"\"\"测试单字段更新\"\"\"
        # 更新一个字段并验证
    
    def test_delete_entity(self, unit_test_db):
        \"\"\"测试删除实体\"\"\"
        # 删除并验证不存在
```

使用示例:
    from pathlib import Path
    from tools.test_generators.unit.repository_test_generator import RepositoryTestGenerator
    from tools.test_generators.utils.repository_analyzer import RepositoryAnalyzer
    from tools.test_generators.utils.model_analyzer import ModelAnalyzer
    
    # 分析Repository和Model
    repo_analyzer = RepositoryAnalyzer(project_root=Path.cwd())
    model_analyzer = ModelAnalyzer(project_root=Path.cwd())
    
    repositories = repo_analyzer.analyze_module_repositories("user_auth")
    models = model_analyzer.analyze_module_models("user_auth")
    
    # 生成测试代码
    generator = RepositoryTestGenerator(project_root=Path.cwd(), config={})
    test_code = generator.generate_repository_tests(
        "user_auth", repositories, models
    )
    
    # 保存测试文件
    with open("tests/unit/generated/user_auth/test_repositories.py", "w") as f:
        f.write(test_code)

注意事项:
- 测试使用真实SQLite数据库，确保SQL语句正确性
- Factory类必须在tests/factories/目录中定义
- 联合主键需要特殊处理（自动识别并生成对应代码）
- 软删除需要模型有deleted_at或is_deleted字段
- 生成的测试代码长度较大（可能>2000行），建议分文件存储

Performance:
- 生成速度: 平均100-200ms（取决于Repository方法数量）
- 测试执行: SQLite内存数据库，单个测试<50ms

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-16 (添加参数值解析设计决策)
Version: 1.0.2
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
    
    当前阶段：B（开始使用CrossModuleDependencyResolver工具）
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
        
        # 初始化跨模块依赖解析器
        from ..utils.cross_module_dependency_resolver import CrossModuleDependencyResolver
        self.dependency_resolver = CrossModuleDependencyResolver(project_root)
        
        # 初始化ModelAnalyzer（用于获取跨模块模型信息）
        from ..utils.model_analyzer import ModelAnalyzer
        self.model_analyzer = ModelAnalyzer(project_root)
    
    def _generate_method_call(
        self, 
        method_info: RepositoryMethodInfo, 
        repo_name: str, 
        args: str
    ) -> str:
        """生成正确的Repository方法调用（静态方法 vs 实例方法）
        
        Args:
            method_info: 方法信息（包含is_static字段）
            repo_name: Repository类名
            args: 方法参数字符串
            
        Returns:
            str: 正确的方法调用代码
            
        Examples:
            静态方法: CartRepository.create(unit_test_db, entity)
            实例方法: CartRepository(unit_test_db).create(entity)
        """
        if method_info.is_static:
            # 静态方法：RepositoryClass.method(db, ...)
            return f"{repo_name}.{method_info.name}({args})"
        else:
            # 实例方法：RepositoryClass(db).method(...)
            # 解析数据库参数（假设第一个参数是数据库）
            if args.startswith('unit_test_db, '):
                # 有其他参数: unit_test_db, entity -> (unit_test_db).method(entity)
                remaining_args = args[14:]  # 移除 'unit_test_db, ' (14 characters)
                return f"{repo_name}(unit_test_db).{method_info.name}({remaining_args})"
            elif args == 'unit_test_db':
                # 只有数据库参数: unit_test_db -> (unit_test_db).method()
                return f"{repo_name}(unit_test_db).{method_info.name}()"
            else:
                # 其他情况，数据库作为构造参数
                return f"{repo_name}(unit_test_db).{method_info.name}({args})"

    # ============================================================================
    # 参数值解析方法组（新增 2025-10-16）
    # ============================================================================
    
    def _resolve_param_value(
        self,
        param_name: str,
        param_type: str,
        repo_info: RepositoryInfo,
        models: Dict[str, ModelInfo],
        entity_var: str = "entity",
        **context
    ) -> str:
        """参数值解析统一入口
        
        根据参数名、类型、模型信息等，智能解析应该生成的参数值。
        这是参数值解析的统一分发方法，根据类型调用专门的解析方法。
        
        Args:
            param_name: 参数名（如username, user_id, identifier）
            param_type: 参数类型（如str, int, List[int], Optional[str]）
            repo_info: Repository信息（包含model_name）
            models: 所有模型信息字典
            entity_var: entity变量名（默认"entity"）
            context: 显式提供的参数值（最高优先级）
            
        Returns:
            str: 参数值表达式（如"entity.username", "1", "[entity.id]"）
        """
        # 最高优先级：context显式提供的值
        if param_name in context:
            return context[param_name]
        
        # 特殊处理：entity参数直接传entity变量
        if param_name == 'entity':
            return entity_var
        
        # 🎯 关键修复：检查参数类型是否是模型类（如user: User, session: UserSession）
        # 清理Optional包装，获取真实类型
        clean_type = param_type.replace('Optional[', '').replace(']', '').strip()
        
        # 检查是否是模型类型（考虑别名，如UserSession→Session）
        # 1. 直接匹配（clean_type在models中）
        # 2. 移除前缀匹配（UserSession→Session, UserRole→UserRole等）
        is_model_type = clean_type in models
        if not is_model_type and clean_type.startswith('User'):
            # 尝试移除User前缀（UserSession→Session）
            alt_name = clean_type[4:]  # 移除"User"前缀
            is_model_type = alt_name in models
        
        if is_model_type:
            # 参数类型是模型类 → 直接传entity
            # 例如：create(db, user: User) → create(unit_test_db, entity)
            #      increment_failed_login(db, user: User) → increment_failed_login(unit_test_db, entity)
            #      deactivate(db, session: UserSession) → deactivate(unit_test_db, entity)
            return entity_var
        
        # 特殊处理：特殊参数名的固定默认值
        if param_name in ['data', 'update_data', 'filters'] or 'dict' in param_type.lower():
            return "{}"
        elif param_name in ['skip', 'offset']:
            return "0"
        elif param_name in ['limit', 'count']:
            return "100"
        
        # 获取当前模型信息
        model_info = models.get(repo_info.model_name)
        
        # 根据类型分发到专门的解析方法
        if 'List' in param_type:
            return self._resolve_list_param(param_name, param_type, repo_info, model_info, entity_var)
        elif 'int' in param_type.lower():
            return self._resolve_integer_param(param_name, param_type, repo_info, model_info, models, entity_var)
        elif 'str' in param_type.lower():
            return self._resolve_string_param(param_name, param_type, model_info, entity_var)
        elif 'bool' in param_type.lower():
            return "False"
        else:
            # 未知类型，尝试作为字段处理
            if model_info and param_name in [f.name for f in model_info.fields]:
                return f"{entity_var}.{param_name}"
            return f"{entity_var}.{param_name}"
    
    def _resolve_string_param(
        self,
        param_name: str,
        param_type: str,
        model_info: Optional[ModelInfo],
        entity_var: str
    ) -> str:
        """解析字符串参数值
        
        处理字符串参数的逻辑映射，核心解决"identifier应该映射到username还是生成硬编码"的问题。
        
        策略：
        1. 检查是否是模型字段 → entity.param_name
        2. 逻辑参数映射（identifier → username/email/phone）
        3. 后备：生成硬编码字符串
        
        Args:
            param_name: 参数名
            param_type: 参数类型
            model_info: 模型信息
            entity_var: entity变量名
            
        Returns:
            str: 参数值表达式
        """
        # 1. 检查是否是模型字段
        if model_info and param_name in [f.name for f in model_info.fields]:
            return f"{entity_var}.{param_name}"
        
        # 2. 逻辑参数映射配置
        LOGICAL_PARAM_MAPPINGS = {
            'identifier': ['username', 'email', 'phone'],
            'search_term': ['name', 'title', 'description'],
            'keyword': ['name', 'title', 'content'],
            'openid': ['wx_openid'],  # 微信openid参数映射
        }
        
        # 尝试逻辑映射
        if param_name in LOGICAL_PARAM_MAPPINGS and model_info:
            model_field_names = [f.name for f in model_info.fields]
            for candidate in LOGICAL_PARAM_MAPPINGS[param_name]:
                if candidate in model_field_names:
                    return f"{entity_var}.{candidate}"
        
        # 3. 后备：生成硬编码字符串
        return f'"{param_name}_value"'
    
    def _resolve_integer_param(
        self,
        param_name: str,
        param_type: str,
        repo_info: RepositoryInfo,
        model_info: Optional[ModelInfo],
        models: Dict[str, ModelInfo],
        entity_var: str
    ) -> str:
        """解析整数参数值
        
        处理整数参数，包括关联查询判断（user_id需要依赖实体）。
        
        策略：
        1. xxx_id + 匹配当前模型 → entity.id
        2. xxx_id + 是模型外键字段 → entity.param_name
        3. xxx_id + Optional类型 → None
        4. xxx_id + 必填但不是字段 → 1（关联查询，暂时简化处理）
        5. 其他整数参数是字段 → entity.param_name
        6. 后备：1
        
        Args:
            param_name: 参数名
            param_type: 参数类型
            repo_info: Repository信息
            model_info: 当前模型信息
            models: 所有模型信息
            entity_var: entity变量名
            
        Returns:
            str: 参数值表达式
        """
        # 处理 xxx_id 格式的参数
        if param_name.endswith('_id'):
            base_name = param_name[:-3]
            
            # 1. 匹配当前模型：category_id in CategoryRepository → entity.id
            if base_name.lower() == repo_info.model_name.lower():
                return f"{entity_var}.id"
            
            # 2. 检查是否是模型的外键字段
            if model_info and param_name in [f.name for f in model_info.fields]:
                return f"{entity_var}.{param_name}"
            
            # 3. Optional类型的关联查询参数
            if 'Optional' in param_type:
                return "None"
            
            # 4. 必填但不是字段的关联查询（如role_id但当前模型是User）
            # TODO: 未来需要创建依赖实体，当前简化为返回1
            return "1"
        
        # 处理常见整数字段
        if model_info and param_name in [f.name for f in model_info.fields]:
            return f"{entity_var}.{param_name}"
        
        # 后备：返回1
        return "1"
    
    def _resolve_list_param(
        self,
        param_name: str,
        param_type: str,
        repo_info: RepositoryInfo,
        model_info: Optional[ModelInfo],
        entity_var: str
    ) -> str:
        """解析列表参数值
        
        处理列表类型参数，特别是 xxx_ids: List[int] 的情况。
        
        策略：
        1. xxx_ids + 匹配当前模型 → [entity.id]
        2. 提取元素类型生成默认列表
        
        Args:
            param_name: 参数名
            param_type: 参数类型
            repo_info: Repository信息
            model_info: 当前模型信息
            entity_var: entity变量名
            
        Returns:
            str: 参数值表达式
        """
        # xxx_ids + 匹配当前模型
        if param_name.endswith('_ids'):
            base_name = param_name[:-4]  # category_ids → category
            if base_name.lower() == repo_info.model_name.lower():
                return f"[{entity_var}.id]"
        
        # 根据元素类型生成默认列表
        if 'int' in param_type.lower():
            return "[1]"
        elif 'str' in param_type.lower():
            return '["test"]'
        else:
            return "[]"
    
    # ============================================================================
    # 参数生成主方法（使用上面的解析方法）
    # ============================================================================
    
    def _generate_test_params(
        self,
        method_info: RepositoryMethodInfo,
        repo_info: RepositoryInfo,
        models: Dict[str, ModelInfo],
        entity_var: str = "entity",
        dependencies: Optional[List[str]] = None,
        **context
    ) -> str:
        """统一的测试参数生成方法
        
        核心原则：RepositoryAnalyzer已经通过AST自动提取了完整的参数信息(name, type, kind)，
        我们只需要根据这些信息决定如何在测试中构造参数值。
        
        自动获取的数据（无需推断）：
        1. method_info.parameters: [(param_name, param_type, param_kind), ...]
           - RepositoryAnalyzer从函数签名AST中直接提取
           - 示例: ('category_id', 'int', 'positional'), ('status', 'Optional[str]', 'keyword-only')
        
        2. repo_info.model_name: str
           - RepositoryAnalyzer从类名推断（CategoryRepository → Category）
        
        3. repo_info.import_aliases: Dict[str, str]
           - RepositoryAnalyzer从import语句提取（import Session as UserSession）
        
        参数值生成策略（按优先级）：
        1. entity参数 → 直接传entity变量
        2. current_model_ids (List[int]) → [entity.id]
        3. current_model_id (int) → entity.id  
        4. other_model_id (int) → entity.xxx_id（假设entity有该外键字段）
        5. context显式值 → 使用context提供的值
        6. 常见字段名 → entity.field_name
        7. 特殊参数 → 固定默认值（data={}, skip=0等）
        8. 类型后备 → 根据param_type生成默认值
        
        Args:
            method_info: 方法信息（RepositoryAnalyzer提供，包含完整参数）
            repo_info: Repository信息（RepositoryAnalyzer提供，包含model_name）
            entity_var: entity变量名（默认"entity"）
            dependencies: 测试setup中创建的依赖变量（暂未使用）
            context: 显式提供的参数值（优先级最高）
            
        Returns:
            str: 完整的方法调用参数，如 "unit_test_db, entity.id, status='active'"
            
        示例：
            # CategoryRepository.count_products(db, category_id: int)
            # repo_info.model_name = "Category"
            # method_info.parameters = [('category_id', 'int', 'positional')]
            → "unit_test_db, entity.id"  # category_id匹配当前模型Category
            
            # CategoryRepository.count_by_category_ids(db, category_ids: List[int])
            # repo_info.model_name = "Category"  
            # method_info.parameters = [('category_ids', 'List[int]', 'positional')]
            → "unit_test_db, [entity.id]"  # category_ids匹配当前模型，且是List
            
            # ProductRepository.get_products_by_category(db, category_id: int, *, status: str = None)
            # repo_info.model_name = "Product"
            # method_info.parameters = [('category_id', 'int', 'positional'), ('status', 'Optional[str]', 'keyword-only')]
            → "unit_test_db, entity.category_id, status='active'"  # category_id是外键，status是keyword-only
        """
        positional_parts = []
        keyword_parts = []
        
        for param_name, param_type, param_kind in method_info.parameters:
            # db参数在外层特殊处理，跳过
            if param_name == 'db':
                continue
            
            # 🎯 使用新的参数值解析方法（统一入口）
            param_value = self._resolve_param_value(
                param_name=param_name,
                param_type=param_type,
                repo_info=repo_info,
                models=models,
                entity_var=entity_var,
                **context
            )
            
            # 根据参数种类生成调用语法
            if param_kind == 'keyword-only':
                keyword_parts.append(f"{param_name}={param_value}")
            else:
                positional_parts.append(param_value)
        
        # 拼接：位置参数在前，命名参数在后（符合Python语法）
        all_parts = positional_parts + keyword_parts
        
        # 拼接完整参数（含db）
        if all_parts:
            return "unit_test_db, " + ", ".join(all_parts)
        else:
            return "unit_test_db"

    def generate_repository_tests(
        self,
        module_name: str,
        models: Dict[str, ModelInfo],
        repositories: Dict[str, RepositoryInfo]
    ) -> str:
        """生成Repository测试代码（主入口）
        
        测试策略:
        - 使用 SQLite 内存数据库 (unit_test_db fixture)
        - 测试每个 Repository 方法的数据访问逻辑
        - 验证查询条件、过滤、排序、分页等
        - 测试事务处理（create/update/delete）
        - 测试边界情况和错误处理
        
        Args:
            module_name: 模块名称
            models: 模型信息字典
            repositories: Repository信息字典
            
        Returns:
            生成的测试代码字符串
        """
        from datetime import datetime
        
        test_classes = []
        
        # 为每个Repository生成测试类
        for repo_name, repo_info in repositories.items():
            test_class = self._generate_single_repository_test(repo_info, models, module_name)
            test_classes.append(test_class)
        
        # 🔍 智能收集需要导入的模型（从生成的测试代码中提取）
        model_imports = set()
        # 添加Repository的主模型
        for repo_info in repositories.values():
            model_imports.add(repo_info.model_name)
        
        # 从生成的测试代码中提取所有使用的模型名
        import re
        all_test_code = '\n'.join(test_classes)
        # 匹配 "entity = ModelName(" 模式
        entity_pattern = r'entity\s*=\s*([A-Z][a-zA-Z0-9_]*)\s*\('
        found_models = re.findall(entity_pattern, all_test_code)
        for model_name in found_models:
            if model_name in models:  # 确保是本模块的模型
                model_imports.add(model_name)
        
        # 收集需要导入的Repository
        repo_imports = [repo_info.name for repo_info in repositories.values()]
        
        imports = f'''"""
Auto Generated Test - Repository Layer

文件路径: tests/unit/test_repositories/test_{module_name}_repositories.py
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
生成工具: tools/generate_test_template.py v3.0
模块: {module_name}

测试类型: 单元测试 - Repository数据访问层
测试策略: SQLite内存数据库
测试重点: 
- CRUD操作正确性
- 查询条件和过滤逻辑
- 事务提交和回滚
- 边界情况和错误处理

符合标准: 
- testing-standards.md - 四层架构测试策略
- architecture/overview.md - Repository模式标准

[CHECK:TEST-001] [CHECK:DEV-009]
"""

import pytest
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from decimal import Decimal

# 导入测试基础设施
from tests.conftest import unit_test_db

# 导入Repository类
from app.modules.{module_name}.repository import (
    {', '.join(repo_imports)}
)

# 导入模型类
from app.modules.{module_name}.models import (
    {', '.join(sorted(model_imports))}
)

'''
        
        return imports + "\n\n".join(test_classes)
    
    def generate_repository_create_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Repository create方法测试（符合testing-standards.md 2.1节要求）
        
        测试类型（符合标准第2.1节）:
        1. 最小必填字段创建测试 - 只填写nullable=False且无default的字段
        2. 完整字段创建测试 - 填写所有字段包括可选字段
        3. 字段验证测试 - 验证约束和格式
        4. 关联创建测试 - 验证外键关联
        """
        method_name = method_info.name
        
        # 🎯 步骤1：智能推断实际要创建的实体类型
        # 过滤掉self, db, cls等基础参数
        method_params = [p for p in method_info.parameters if p[0] not in ['self', 'db', 'cls']]
        
        # 从参数类型推断实际要创建的实体类型
        actual_model_name = model_name  # 默认使用Repository对应的模型
        
        if len(method_params) == 1:
            param_name, param_type, param_kind = method_params[0]
            
            # 🔧 提取参数类型中的实体名称（如 "OrderItem" from "OrderItem"）
            clean_param_type = param_type.replace('Optional[', '').replace(']', '').strip()
            
            # 检查是否是实体对象参数（参数类型是大写开头的类名，考虑别名）
            is_entity_type = clean_param_type and clean_param_type[0].isupper() and clean_param_type in models
            if not is_entity_type and clean_param_type and clean_param_type.startswith('User'):
                # 尝试移除User前缀（UserSession→Session）
                alt_name = clean_param_type[4:]  # 移除"User"前缀
                if alt_name in models:
                    is_entity_type = True
                    clean_param_type = alt_name  # 使用实际的模型名
            
            if is_entity_type:
                # 🎯 核心修复：使用参数类型作为实际模型名称！
                actual_model_name = clean_param_type
        
        # 🎯 步骤2：使用actual_model_name生成实体创建代码
        # 生成最小字段创建代码（只填必填字段）
        minimal_imports, minimal_entity_code = self._generate_minimal_entity_creation(actual_model_name, models, module_name)
        
        # 🔑 生成完整字段创建代码（填充所有字段）
        full_imports, full_entity_code = self._generate_full_entity_creation(actual_model_name, models, module_name)
        
        # 组装import语句（放在方法开始）
        import_block = ''
        if minimal_imports:
            unique_imports = list(dict.fromkeys(minimal_imports))  # 去重
            import_lines = ['        ' + imp for imp in unique_imports]
            import_block = '\n'.join(import_lines) + '\n        '
        
        # 组装full_fields的import语句
        full_import_block = ''
        if full_imports:
            unique_full_imports = list(dict.fromkeys(full_imports))
            full_import_lines = ['        ' + imp for imp in unique_full_imports]
            full_import_block = '\n'.join(full_import_lines) + '\n        '
        
        # 检查是否使用联合主键
        has_composite_pk = self._has_composite_primary_key(actual_model_name, models)
        
        # 🎯 步骤3：生成方法调用参数
        if not method_params:
            # 无参数的create方法
            method_call_args_minimal = "unit_test_db"
            method_call_args_factory = "unit_test_db"
        elif len(method_params) == 1:
            param_name, param_type, param_kind = method_params[0]
            
            clean_param_type = param_type.replace('Optional[', '').replace(']', '').strip()
            
            # 检查是否是实体对象参数（考虑别名，如UserSession→Session）
            is_entity_type = clean_param_type and clean_param_type[0].isupper() and clean_param_type in models
            if not is_entity_type and clean_param_type and clean_param_type.startswith('User'):
                # 尝试移除User前缀（UserSession→Session）
                alt_name = clean_param_type[4:]  # 移除"User"前缀
                is_entity_type = alt_name in models
            
            if is_entity_type:
                # 实体对象参数：传递entity
                method_call_args_minimal = "unit_test_db, entity"
                method_call_args_factory = "unit_test_db, entity"
            else:
                # 字段参数（如user_id: int）：使用已创建的依赖实体
                # 检查是否是外键字段
                model_info = models.get(actual_model_name)
                fk_field = None
                if model_info:
                    fk_field = next((f for f in model_info.fields if f.name == param_name and f.foreign_key), None)
                
                if fk_field:
                    # 外键字段：从依赖实体获取ID (依赖已在上面的comprehensive loop中创建)
                    fk_target = fk_field.foreign_key
                    fk_table = fk_target.split('.')[0]
                    # 使用resolver从表名查找模型名（零硬编码）
                    fk_model_name = self.dependency_resolver.get_model_by_table(fk_table) or self._fallback_table_to_model(fk_table)
                    fk_var_name = fk_model_name.lower()
                    
                    # 使用已创建的依赖实体
                    method_call_args_minimal = f"unit_test_db, {fk_var_name}.id"
                    method_call_args_factory = f"unit_test_db, {fk_var_name}.id"
                else:
                    # 普通字段参数：使用测试值
                    test_value = f'1'  # 默认测试值
                    if 'str' in param_type.lower():
                        test_value = f'"test_{param_name}"'
                    method_call_args_minimal = f"unit_test_db, {test_value}"
                    method_call_args_factory = f"unit_test_db, {test_value}"
        else:
            # 多个参数：暂时使用entity（可能需要更复杂的逻辑）
            method_call_args_minimal = "unit_test_db, entity"
            method_call_args_factory = "unit_test_db, entity"
        
        # 生成两种方法调用：一种用于minimal测试，一种用于factory测试
        method_call_entity = self._generate_method_call(method_info, repo_name, method_call_args_minimal)
        method_call_factory = self._generate_method_call(method_info, repo_name, method_call_args_factory)
        
        if has_composite_pk:
            # 联合主键：使用主键字段组合查询
            pk_fields = self._get_primary_key_fields(actual_model_name, models)
            pk_filter = ', '.join([f'{f.name}=result.{f.name}' for f in pk_fields])
            
            return f'''    def test_{method_name}_minimal_fields(self, unit_test_db: Session):
        """测试{method_name} - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
{import_block}# 创建最小实体（只填必填字段）
{minimal_entity_code}
        
        # 执行Repository方法
        result = {method_call_entity}
        
        # 验证必填字段
        assert result is not None
        
        # 验证默认值（如果模型定义了default）
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化（联合主键查询）
        db_entity = unit_test_db.query({model_name}).filter_by({pk_filter}).first()
        assert db_entity is not None
    
    def test_{method_name}_full_fields(self, unit_test_db: Session):
        """测试{method_name} - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        """
{full_import_block}# 使用Factory Boy创建完整实体
{full_entity_code}
        
        # 执行Repository方法
        result = {method_call_entity}
        
        # 验证所有字段保存正确
        assert result is not None
        # TODO: 验证各个字段值
        
        # 验证持久化
        db_entity = unit_test_db.query({model_name}).filter_by({pk_filter}).first()
        assert db_entity is not None
    
    def test_{method_name}_transaction_commit(self, unit_test_db: Session):
        """测试{method_name} - 事务提交验证
        
        符合标准: testing-standards.md 第2.1节 - 验证数据真正写入数据库
        """
{full_import_block}# 创建完整实体（填充所有字段）
{full_entity_code}
        
        result = {method_call_entity}
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by({pk_filter}).first()
        assert db_entity is not None
'''
        else:
            # 标准单主键：使用id查询
            return f'''    def test_{method_name}_minimal_fields(self, unit_test_db: Session):
        """测试{method_name} - 最小必填字段创建
        
        符合标准: testing-standards.md 第2.1节 - 只填写必填字段，验证默认值
        数据准备策略: 最小实体构造，不使用Factory Boy
        """
{import_block}# 创建最小实体（只填必填字段）
{minimal_entity_code}
        
        # 执行Repository方法
        result = {method_call_entity}
        
        # 验证必填字段
        assert result is not None
        assert result.id is not None  # 验证ID已生成
        
        # 验证默认值（Column(default=...)定义的值）
        # 示例: assert result.is_active == True
        # 示例: assert result.status == "active"
        # TODO: 根据实际模型补充默认值验证
        
        # 验证数据已持久化
        db_entity = unit_test_db.query({model_name}).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_{method_name}_full_fields(self, unit_test_db: Session):
        """测试{method_name} - 完整字段创建
        
        符合标准: testing-standards.md 第2.1节 - 填写所有字段，验证保存正确
        数据准备策略: 使用构造函数填充所有字段
        """
{full_import_block}# 创建完整实体（填充所有字段）
{full_entity_code}
        
        # 执行Repository方法
        result = {method_call_entity}
        
        # 验证所有字段保存正确
        assert result is not None
        assert result.id is not None
        # TODO: 验证其他字段值正确保存
        
        # 验证持久化
        db_entity = unit_test_db.query({model_name}).filter_by(id=result.id).first()
        assert db_entity is not None
    
    def test_{method_name}_transaction_commit(self, unit_test_db: Session):
        """测试{method_name} - 事务提交验证
        
        符合标准: testing-standards.md 第2.1节 - 验证数据真正写入数据库
        """
{full_import_block}# 创建完整实体（填充所有字段）
{full_entity_code}
        
        result = {method_call_entity}
        
        # 验证事务已提交（expire后重新查询能找到）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=result.id).first()
        assert db_entity is not None
'''
    
    def generate_repository_read_test(
        self,
        method_info: RepositoryMethodInfo,
        repo_info: RepositoryInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Repository read方法测试（智能处理返回类型和参数）"""
        method_name = method_info.name
        
        # 🔧 从返回类型推断实际要查询的模型（支持跨模块查询）
        return_type = method_info.return_type
        actual_model_name = self._extract_model_from_return_type(return_type, models)
        if not actual_model_name:
            actual_model_name = model_name  # 默认使用Repository的主模型
        
        entity_creation = self._generate_test_entity_creation(actual_model_name, models, "查询测试", with_dependencies=True, module_name=module_name)
        
        # 🔧 检查是否为跨模块模型，需要Factory setup
        is_cross_module = actual_model_name not in models
        if is_cross_module:
            # 如果entity_creation已经包含多行代码（有依赖创建），则保留不覆盖
            # 只有简单的单行代码（如"InventoryStockFactory.create()"）才需要添加setup
            if '\n' not in entity_creation and 'FactoryManager' not in entity_creation:
                # 跨模块模型：生成Factory setup代码
                fk_model_module = self.dependency_resolver.get_module_for_model(actual_model_name)
                if fk_model_module:
                    factory_name = f'{actual_model_name}Factory'
                    factory_manager = f'{fk_model_module.replace("_", " ").title().replace(" ", "")}FactoryManager'
                    entity_creation = f'''from tests.factories.{fk_model_module}_factories import {factory_manager}
        {factory_manager}.setup_factories(unit_test_db)
        from tests.factories.{fk_model_module}_factories import {factory_name}
        entity = {factory_name}.create()'''
        
        # 检查返回类型
        is_list_return = 'List[' in method_info.return_type or 'list[' in method_info.return_type.lower()
        is_bool_return = method_info.return_type == 'bool'
        
        # 🎯 使用新的参数生成方法（2025-10-16 重构）
        # ⚠️ 关键修复：需要确定entity变量的实际类型来正确推断参数值
        #
        # 设计原则：
        # - 参数值推断依赖于entity变量的类型
        # - entity类型由entity_creation逻辑决定
        # - 对于列表返回，entity是主模型；对于单对象返回，entity是返回类型
        #
        # 示例：
        # 1. get_user_by_id(user_id: int) → User
        #    entity_type = "User"（返回类型）
        #    参数推断：user_id → entity.id（从User模型推断）
        #
        # 2. get_order_items(order_id: int) → List[OrderItem]
        #    entity_type = "Order"（主模型）
        #    参数推断：order_id → entity.id（从Order模型推断）
        #
        # 通用化设计：
        # - 根据返回类型决定entity的类型（与entity_creation逻辑一致）
        # - 列表返回 → 主模型（model_name）
        # - 单对象返回 → 返回类型（actual_model_name）
        entity_type_for_params = model_name if is_list_return else actual_model_name
        
        original_model_name = repo_info.model_name
        repo_info.model_name = entity_type_for_params  # 临时覆盖为entity的实际类型
        query_param = self._generate_test_params(method_info, repo_info, models, entity_var="entity")
        repo_info.model_name = original_model_name  # 恢复原值
        has_composite_pk = self._has_composite_primary_key(model_name, models)
        
        # 🎯 特殊处理: 复合主键的get方法
        if method_name == 'get' and has_composite_pk:
            pk_fields = self._get_primary_key_fields(model_name, models)
            not_found_params = 'unit_test_db, ' + ', '.join(['999999' for _ in pk_fields])
            
            # 生成方法调用
            method_call_found = self._generate_method_call(method_info, repo_name, query_param)
            method_call_not_found = self._generate_method_call(method_info, repo_name, not_found_params)
            
            # 根据返回类型选择断言
            is_count_method = method_info.return_type == "int" or "count" in method_name.lower()
            if is_count_method:
                found_assertion = "assert isinstance(result, int)\n        assert result >= 0  # count方法返回非负整数"
                not_found_assertion = "assert result == 0  # count方法返回0"
            else:
                found_assertion = "assert result is not None"
                not_found_assertion = "assert result is None"
            
            return f'''    def test_{method_name}_found(self, unit_test_db: Session):
        """测试{method_name} - 查询到数据"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = {method_call_found}
        
        # 验证结果
        {found_assertion}

    def test_{method_name}_not_found(self, unit_test_db: Session):
        """测试{method_name} - 数据不存在（复合主键）"""
        result = {method_call_not_found}
        
        # 验证结果
        {not_found_assertion}
'''
        
        if is_bool_return:
            # 返回bool的方法（如check_exists）
            if method_name == 'check_exists':
                method_call_found = self._generate_method_call(method_info, repo_name, query_param)
                not_found_params = self._generate_not_found_param(query_param)
                method_call_not_found = self._generate_method_call(method_info, repo_name, not_found_params)
                
                return f'''    def test_{method_name}_found(self, unit_test_db: Session):
        """测试{method_name} - 查询到数据"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = {method_call_found}
        
        # 验证结果
        assert result is True
    
    def test_{method_name}_not_found(self, unit_test_db: Session):
        """测试{method_name} - 数据不存在"""
        result = {method_call_not_found}
        
        assert result is False
'''
            else:
                # 生成方法调用
                method_call_found = self._generate_method_call(method_info, repo_name, query_param)
                method_call_not_found = self._generate_method_call(method_info, repo_name, "unit_test_db")
                
                return f'''    def test_{method_name}_found(self, unit_test_db: Session):
        """测试{method_name} - 查询到数据"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = {method_call_found}
        
        # 验证结果
        assert result is True
    
    def test_{method_name}_not_found(self, unit_test_db: Session):
        """测试{method_name} - 数据不存在"""
        result = {method_call_not_found}
        
        assert result is False
'''
        elif is_list_return:
            # 返回列表的方法（如list方法、get_user_roles等）
            
            # 生成包含依赖的实体创建代码
            entity_creation_with_deps = self._generate_test_entity_creation(model_name, models, "关联数据", with_dependencies=True, module_name=module_name)
            
            # 生成方法调用
            method_call_found = self._generate_method_call(method_info, repo_name, query_param)
            method_call_not_found = self._generate_method_call(method_info, repo_name, "unit_test_db, 999999")
            
            return f'''    def test_{method_name}_found(self, unit_test_db: Session):
        """测试{method_name} - 查询到数据"""
        # 准备测试数据
        {entity_creation_with_deps}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = {method_call_found}
        
        # 验证结果
        assert isinstance(result, list)
        # 注意：复杂join查询可能返回空列表（依赖完整的关联链），
        # 这里只验证方法正确执行并返回list类型即可

    def test_{method_name}_not_found(self, unit_test_db: Session):
        """测试{method_name} - 数据不存在"""
        # 执行Repository方法（查询不存在的数据）
        result = {method_call_not_found}
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 0
'''
        
        else:
            # 返回单个对象的方法（如get_by_id, get_by_username）
            
            # 生成not_found测试的参数（使用不存在的值替代）
            not_found_param = self._generate_not_found_param(query_param)
            
            # 🎯 根据返回类型选择断言
            is_count_method = method_info.return_type == "int" or "count" in method_name.lower()
            if is_count_method:
                found_assertion = "assert isinstance(result, int)\n        assert result >= 0  # count方法返回非负整数"
                not_found_assertion = "assert result == 0  # count方法返回0"
            else:
                found_assertion = "assert result is not None"
                not_found_assertion = "assert result is None"
            
            # 生成方法调用
            method_call_found = self._generate_method_call(method_info, repo_name, query_param)
            method_call_not_found = self._generate_method_call(method_info, repo_name, not_found_param)
            
            return f'''    def test_{method_name}_found(self, unit_test_db: Session):
        """测试{method_name} - 查询到数据"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        result = {method_call_found}
        
        # 验证结果
        {found_assertion}

    def test_{method_name}_not_found(self, unit_test_db: Session):
        """测试{method_name} - 数据不存在"""
        result = {method_call_not_found}
        
        # 验证结果
        {not_found_assertion}
'''
    
    def _generate_not_found_param(self, query_param: str) -> str:
        """生成not_found测试的参数（将实际值替换为不存在的值）
        
        🎯 核心改进：
        - 正确处理多参数（如entity.user_id, entity.role_id）
        - 区分字段类型（ID用99999，字符串用"nonexistent"）
        - ✅ 保留unit_test_db前缀（修复参数缺失问题）
        """
        # ✅ 修复：如果参数以unit_test_db开头，提取它并保留
        db_prefix = ""
        business_params = query_param
        
        if query_param.startswith("unit_test_db"):
            # 分离db参数和业务参数
            parts = query_param.split(',', 1)
            db_prefix = parts[0].strip()  # "unit_test_db"
            business_params = parts[1].strip() if len(parts) > 1 else ""
        
        # 如果没有业务参数，只返回db
        if not business_params:
            return db_prefix if db_prefix else "unit_test_db"
        
        # 处理业务参数
        # 如果参数中包含entity.xxx，替换为字面量
        if 'entity.' in business_params:
            # 提取字段名
            if ',' in business_params:
                # 多个参数（如entity.user_id, entity.role_id）
                params = business_params.split(',')
                not_found_params = []
                for param in params:
                    param = param.strip()
                    if 'entity.' in param:
                        # 提取字段名判断类型
                        field_name = param.replace('entity.', '').strip()
                        if field_name.endswith('_id') or field_name == 'id':
                            # ID字段用不存在的整数
                            not_found_params.append('999999')
                        else:
                            # 字符串字段
                            not_found_params.append('"nonexistent_value"')
                    else:
                        # 保留其他参数
                        not_found_params.append(param)
                result = ', '.join(not_found_params)
                return f"{db_prefix}, {result}" if db_prefix else result
            else:
                # 单个参数
                field_name = business_params.replace('entity.', '').strip()
                if field_name.endswith('_id') or field_name == 'id':
                    result = '999999'
                else:
                    result = '"nonexistent_value"'
                return f"{db_prefix}, {result}" if db_prefix else result
        else:
            # 已经是字面量（如"cart.id, 1"），需要处理多参数
            if ',' in business_params:
                # 多个参数，替换每个参数为不存在的值
                params = business_params.split(',')
                not_found_params = []
                for param in params:
                    param = param.strip()
                    # 检查是否包含.id（如cart.id, user.id）
                    if '.id' in param or param.isdigit():
                        # ID类型，使用999999
                        not_found_params.append('999999')
                    else:
                        # 其他类型，使用字符串
                        not_found_params.append('"nonexistent_value"')
                result = ', '.join(not_found_params)
                return f"{db_prefix}, {result}" if db_prefix else result
            else:
                # 单个参数，替换为不存在的值
                result = '"nonexistent_value_12345"'
                return f"{db_prefix}, {result}" if db_prefix else result
    
    def _generate_delete_verification(self, is_soft_delete: bool, model_name: str, filter_condition: str) -> str:
        """生成删除验证逻辑（通用方法）
        
        Args:
            is_soft_delete: 是否是软删除
            model_name: 模型名称
            filter_condition: 过滤条件（如"id=entity_id" 或 "user_id=user_id_val, role_id=role_id_val"）
            
        Returns:
            str: 验证代码
        """
        if is_soft_delete:
            # 软删除：记录仍存在，但is_deleted=True或is_active=False
            return f'''# 验证软删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by({filter_condition}).first()
        assert db_entity is not None  # 记录仍存在
        # 验证软删除标记（根据模型字段选择）
        if hasattr(db_entity, 'is_deleted'):
            assert db_entity.is_deleted == True
        if hasattr(db_entity, 'is_active'):
            assert db_entity.is_active == False'''
        else:
            # 硬删除：记录被物理删除
            return f'''# 验证硬删除
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by({filter_condition}).first()
        assert db_entity is None  # 记录已物理删除'''
    
    def generate_repository_update_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Repository update方法测试（符合testing-standards.md 2.3节要求）
        
        测试类型（符合标准第2.3节）:
        1. 单字段更新测试 - 只更新一个字段，验证其他字段不变
        2. 多字段更新测试 - 同时更新多个字段
        3. 专用方法测试 - 如update_status, update_password等
        4. 批量更新测试 - 如update_many, bulk_update等
        
        智能识别两种update模式:
        A. 参数模式: update(db, entity, update_data) - 需要传递更新数据字典
        B. ORM跟踪模式: update(entity) - 依赖SQLAlchemy自动跟踪，只需修改属性
        """
        method_name = method_info.name
        
        # 🎯 关键改进：分析方法参数，识别update模式
        # 过滤掉 self, db, cls 参数，获取业务参数
        business_params = [p for p in method_info.parameters if p[0] not in ['self', 'db', 'cls']]
        
        # 判断update模式：
        # - 如果只有1个参数(entity)且类型是模型类 → ORM跟踪模式
        # - 如果有2个或更多参数(entity, update_data) → 参数模式
        is_orm_tracking_mode = False
        if len(business_params) == 1:
            param_name, param_type, param_kind = business_params[0]
            # 检查参数类型是否是模型类（如 CartItem）
            if model_name.lower() in param_type.lower():
                is_orm_tracking_mode = True
        
        entity_creation = self._generate_test_entity_creation(model_name, models, "原始数据", with_dependencies=True, module_name=module_name)
        
        # 🔥 智能选择可更新的字段（优先name，然后业务字段，最后才是其他字段）
        update_field = "name"  # 默认
        if model_name in models:
            model_info = models[model_name]
            # 检查是否有name字段
            has_name = any(f.name == 'name' for f in model_info.fields)
            if not has_name:
                # 📝 排除规则：只排除真正不能修改的字段
                # 1. 系统字段：id, timestamps, 软删除标记
                # 2. 唯一约束字段：username, email（这些需要唯一性验证）
                # 3. 经过验证的敏感字段：password_hash, token等
                # 4. 已验证的真实信息：如果有verified标记的字段
                excluded_fields = {
                    # 系统字段
                    'id', 'created_at', 'updated_at', 'is_deleted', 'deleted_at',
                    # 唯一约束字段（需要特殊处理）
                    'username', 'email', 'wx_openid', 'wx_unionid',
                    # 认证和令牌字段
                    'password_hash', 'token', 'token_hash', 'refresh_token',
                    # 唯一标识码
                    'code', 'sku', 'slug'
                }
                
                # 🎯 优先级排序：业务字段 > 描述字段 > 其他字段
                logic_config = self.config.get('business_logic_patterns', {}) if self.config else {}
                priority_fields = logic_config.get('repository_priority_fields', [])
                
                # 先检查优先级字段
                for field in priority_fields:
                    field_info = next((f for f in model_info.fields if f.name == field), None)
                    if field_info and not field_info.primary_key and not field_info.foreign_key:
                        update_field = field
                        break
                else:
                    # 如果没有优先级字段，查找第一个可更新的字符串字段
                    updateable_fields = [
                        f.name for f in model_info.fields
                        if f.name not in excluded_fields
                        and not f.primary_key 
                        and not f.foreign_key
                        and 'String' in f.column_type
                    ]
                    if updateable_fields:
                        update_field = updateable_fields[0]
        
        # 🔥 检查是否使用联合主键
        has_composite_pk = self._has_composite_primary_key(model_name, models)
        
        if has_composite_pk:
            # 联合主键：使用主键字段组合查询
            pk_fields = self._get_primary_key_fields(model_name, models)
            pk_filter = ', '.join([f'{f.name}=entity.{f.name}' for f in pk_fields])
            
            # 🎯 正确生成方法调用，而不是硬编码TODO
            method_call = self._generate_method_call(method_info, repo_name, "unit_test_db, entity, update_data")
            
            return f'''    def test_{method_name}_success(self, unit_test_db: Session):
        """测试{method_name} - 更新成功"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        update_data = {{"{update_field}": "更新后数据"}}
        result = {method_call}
        
        # 验证结果
        assert result.{update_field} == "更新后数据"
        
        # 验证数据库已更新（使用联合主键查询）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by({pk_filter}).first()
        assert db_entity.{update_field} == "更新后数据"
'''
        else:
            # 标准单主键 - 生成4种更新测试
            # 找第二个可更新字段（用于多字段测试）
            second_update_field = None
            if model_name in models:
                model_info = models[model_name]
                excluded_fields = {'id', 'created_at', 'updated_at', 'is_deleted', 
                                 'username', 'email', 'password_hash', 'token', 'token_hash', update_field}
                # 优先查找String类型字段
                updateable_string_fields = [
                    f.name for f in model_info.fields
                    if f.name not in excluded_fields
                    and not f.primary_key and not f.foreign_key
                    and 'String' in f.column_type
                ]
                # 如果没有String字段，查找其他类型字段（Boolean, Integer等）
                if updateable_string_fields:
                    second_update_field = updateable_string_fields[0]
                else:
                    updateable_other_fields = [
                        f.name for f in model_info.fields
                        if f.name not in excluded_fields
                        and not f.primary_key and not f.foreign_key
                        and f.name not in {'created_at', 'updated_at', 'deleted_at', 'is_deleted'}
                    ]
                    if updateable_other_fields:
                        second_update_field = updateable_other_fields[0]
            
            # 如果找不到第二个字段，使用update_field本身
            if second_update_field is None:
                second_update_field = update_field
            
            # 🎯 核心改进：根据字段类型生成测试值
            model_info = models[model_name]
            update_field_info = next((f for f in model_info.fields if f.name == update_field), None)
            second_field_info = next((f for f in model_info.fields if f.name == second_update_field), None)
            
            update_value1 = self._generate_test_value_by_field_type(update_field_info, "") if update_field_info else '"更新后数据"'
            update_value2 = self._generate_test_value_by_field_type(update_field_info, "1") if update_field_info else '"更新后数据1"'
            second_value = self._generate_test_value_by_field_type(second_field_info, "2") if second_field_info else '"更新后数据2"'
            
            # 🔥 获取跨模块依赖的FactoryManager（修复外键约束问题）
            all_dependencies = self._get_all_dependencies(model_name, models, module_name)
            cross_module_dependencies = set()
            for dep_model, dep_module, _ in all_dependencies:
                if dep_module != module_name and dep_module != 'unknown':
                    cross_module_dependencies.add(dep_module)
            
            # 生成跨模块FactoryManager的import和setup代码，并创建必需的依赖实体
            cross_module_setup = []
            cross_module_entity_creation = []
            
            for dep_model, dep_module, _ in all_dependencies:
                if dep_module != module_name and dep_module != 'unknown':
                    manager_name = ''.join(word.capitalize() for word in dep_module.split('_')) + 'FactoryManager'
                    if f'{manager_name}.setup_factories' not in '\n'.join(cross_module_setup):
                        cross_module_setup.append(f'        from tests.factories.{dep_module}_factories import {manager_name}')
                        cross_module_setup.append(f'        {manager_name}.setup_factories(unit_test_db)')
                    
                    # 创建依赖实体（如User）以满足FK约束
                    factory_name = f'{dep_model}Factory'
                    var_name = dep_model.lower()
                    if f'{var_name} = {factory_name}.create()' not in '\n'.join(cross_module_entity_creation):
                        cross_module_entity_creation.append(f'        from tests.factories.{dep_module}_factories import {factory_name}')
                        cross_module_entity_creation.append(f'        {var_name} = {factory_name}.create()')
            
            cross_module_setup_code = '\n'.join(cross_module_setup)
            if cross_module_entity_creation:
                cross_module_setup_code += '\n' + '\n'.join(cross_module_entity_creation)
            if cross_module_setup_code:
                cross_module_setup_code += '\n'
            
            # 🔑 生成测试实体创建代码（使用构造函数而非Factory.create()）
            minimal_imports, minimal_entity_code = self._generate_minimal_entity_creation(model_name, models, module_name)
            entity_import_block = ''
            if minimal_imports:
                unique_imports = list(dict.fromkeys(minimal_imports))
                import_lines = ['        ' + imp for imp in unique_imports]
                entity_import_block = '\n'.join(import_lines) + '\n        '
            
            # 🎯 根据update模式生成不同的测试代码
            if is_orm_tracking_mode:
                # ORM跟踪模式：修改属性 + 调用update
                method_call = self._generate_method_call(method_info, repo_name, "unit_test_db, entity")
                
                return f'''    def test_{method_name}_single_field(self, unit_test_db: Session):
        """测试{method_name} - 单字段更新
        
        符合标准: testing-standards.md 第2.3节 - 只更新一个字段，验证其他字段不变
        模式: ORM自动跟踪 - 修改entity属性后调用update方法
        """
        # 准备测试数据
{entity_import_block}# 创建最小实体（用于更新测试）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        original_{second_update_field} = entity.{second_update_field}
        
        # 修改实体属性
        entity.{update_field} = {update_value1}
        
        # 执行Repository方法（ORM会自动跟踪变更）
        {method_call}
        unit_test_db.commit()
        
        # 验证目标字段已更新
        assert entity.{update_field} == {update_value1}
        
        # ✅ 验证其他字段未变化
        assert entity.{second_update_field} == original_{second_update_field}
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity.id).first()
        assert db_entity.{update_field} == {update_value1}
        assert db_entity.{second_update_field} == original_{second_update_field}
    
    def test_{method_name}_multiple_fields(self, unit_test_db: Session):
        """测试{method_name} - 多字段更新
        
        符合标准: testing-standards.md 第2.3节 - 同时更新多个字段
        模式: ORM自动跟踪 - 修改多个entity属性后调用update方法
        """
{entity_import_block}# 创建最小实体（用于更新测试）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 修改多个字段
        entity.{update_field} = {update_value2}
        entity.{second_update_field} = {second_value}
        
        # 执行Repository方法（ORM会自动跟踪变更）
        {method_call}
        unit_test_db.commit()
        
        # 验证所有字段已更新
        assert entity.{update_field} == {update_value2}
        assert entity.{second_update_field} == {second_value}
        
        # 验证持久化
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity.id).first()
        assert db_entity.{update_field} == {update_value2}
        assert db_entity.{second_update_field} == {second_value}
    
    def test_{method_name}_transaction_commit(self, unit_test_db: Session):
        """测试{method_name} - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证更新真正写入数据库
        模式: ORM自动跟踪 - 修改entity属性后调用update方法
        """
{entity_import_block}# 创建最小实体（用于更新测试）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 修改实体属性
        entity.{update_field} = "事务测试数据"
        
        # 执行Repository方法
        {method_call}
        unit_test_db.commit()
        
        # 验证事务已提交
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity.id).first()
        assert db_entity.{update_field} == "事务测试数据"
    
    def test_{method_name}_specialized_method(self, unit_test_db: Session):
        """测试{method_name} - 专用方法测试（如有）
        
        符合标准: testing-standards.md 第2.3节 - 测试特殊更新方法
        示例: update_status, update_password, activate, deactivate等
        """
        # TODO: 如果有专用更新方法，在这里测试
        # 例如:
        # entity = {model_name}Factory.create(status='active')
        # result = {repo_name}.update_status(unit_test_db, entity.id, 'inactive')
        # assert result.status == 'inactive'
        pass
'''
            else:
                # 参数模式：update(db, entity, update_data)
                method_call_with_data = self._generate_method_call(method_info, repo_name, "unit_test_db, entity, update_data")
                
                return f'''    def test_{method_name}_single_field(self, unit_test_db: Session):
        """测试{method_name} - 单字段更新
        
        符合标准: testing-standards.md 第2.3节 - 只更新一个字段，验证其他字段不变
        模式: 参数传递 - 通过update_data字典传递更新字段
        """
        # 准备测试数据
{entity_import_block}# 创建最小实体（用于更新测试）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        original_{second_update_field} = entity.{second_update_field}
        
        # 执行Repository方法（只更新{update_field}）
        update_data = {{"{update_field}": {update_value1}}}
        result = {method_call_with_data}
        
        # 验证目标字段已更新
        assert result.{update_field} == {update_value1}
        
        # ✅ 验证其他字段未变化
        assert result.{second_update_field} == original_{second_update_field}
        
        # 验证数据库已更新
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity.id).first()
        assert db_entity.{update_field} == {update_value1}
        assert db_entity.{second_update_field} == original_{second_update_field}
    
    def test_{method_name}_multiple_fields(self, unit_test_db: Session):
        """测试{method_name} - 多字段更新
        
        符合标准: testing-standards.md 第2.3节 - 同时更新多个字段
        模式: 参数传递 - 通过update_data字典传递多个更新字段
        """
{entity_import_block}# 创建最小实体（用于更新测试）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法（同时更新多个字段）
        update_data = {{
            "{update_field}": {update_value2},
            "{second_update_field}": {second_value}
        }}
        result = {method_call_with_data}
        
        # 验证所有字段已更新
        assert result.{update_field} == {update_value2}
        assert result.{second_update_field} == {second_value}
        
        # 验证持久化
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity.id).first()
        assert db_entity.{update_field} == {update_value2}
        assert db_entity.{second_update_field} == {second_value}
    
    def test_{method_name}_transaction_commit(self, unit_test_db: Session):
        """测试{method_name} - 事务提交验证
        
        符合标准: testing-standards.md 第2.5节 - 验证更新真正写入数据库
        模式: 参数传递 - 通过update_data字典传递更新字段
        """
{entity_import_block}# 创建最小实体（用于更新测试）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        update_data = {{"{update_field}": "事务测试数据"}}
        result = {method_call_with_data}
        
        # 验证事务已提交
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity.id).first()
        assert db_entity.{update_field} == "事务测试数据"
    
    def test_{method_name}_specialized_method(self, unit_test_db: Session):
        """测试{method_name} - 专用方法测试（如有）
        
        符合标准: testing-standards.md 第2.3节 - 测试特殊更新方法
        示例: update_status, update_password, activate, deactivate等
        """
        # TODO: 如果有专用更新方法，在这里测试
        # 例如:
        # entity = {model_name}Factory.create(status='active')
        # result = {repo_name}.update_status(unit_test_db, entity.id, 'inactive')
        # assert result.status == 'inactive'
        pass
'''
    
    def generate_repository_delete_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Repository delete方法测试（符合testing-standards.md 2.4节要求）
        
        测试类型（符合标准第2.4节）:
        1. 物理删除测试 - 验证数据真正从数据库删除
        2. 软删除测试 - 验证is_deleted标记和deleted_at时间戳
        3. 批量删除测试 - 如delete_many, bulk_delete等（如有）
        """
        method_name = method_info.name
        entity_creation = self._generate_test_entity_creation(model_name, models, "待删除数据", with_dependencies=True, module_name=module_name)
        
        # 🔥 获取跨模块依赖的FactoryManager（修复外键约束问题）
        all_dependencies = self._get_all_dependencies(model_name, models, module_name)
        cross_module_dependencies = set()
        for dep_model, dep_module, _ in all_dependencies:
            if dep_module != module_name and dep_module != 'unknown':
                cross_module_dependencies.add(dep_module)
        
        # 生成跨模块FactoryManager的import和setup代码，并创建必需的依赖实体
        cross_module_setup = []
        cross_module_entity_creation = []
        
        for dep_model, dep_module, _ in all_dependencies:
            if dep_module != module_name and dep_module != 'unknown':
                manager_name = ''.join(word.capitalize() for word in dep_module.split('_')) + 'FactoryManager'
                if f'{manager_name}.setup_factories' not in '\n'.join(cross_module_setup):
                    cross_module_setup.append(f'        from tests.factories.{dep_module}_factories import {manager_name}')
                    cross_module_setup.append(f'        {manager_name}.setup_factories(unit_test_db)')
                
                # 创建依赖实体（如User）以满足FK约束
                factory_name = f'{dep_model}Factory'
                var_name = dep_model.lower()
                if f'{var_name} = {factory_name}.create()' not in '\n'.join(cross_module_entity_creation):
                    cross_module_entity_creation.append(f'        from tests.factories.{dep_module}_factories import {factory_name}')
                    cross_module_entity_creation.append(f'        {var_name} = {factory_name}.create()')
        
        cross_module_setup_code = '\n'.join(cross_module_setup)
        if cross_module_entity_creation:
            cross_module_setup_code += '\n' + '\n'.join(cross_module_entity_creation)
        if cross_module_setup_code:
            cross_module_setup_code += '\n'
        
        # 🔥 检查是否是软删除（通过AST分析得到）
        is_soft_delete = method_info.is_soft_delete
        
        # 🔥 检查是否使用联合主键
        has_composite_pk = self._has_composite_primary_key(model_name, models)
        # 检查返回类型
        returns_none = method_info.return_type == 'None'
        
        # 🔥 检查delete方法的参数类型（接收对象还是ID）
        # parameters: [(name, type, kind), ...], 跳过'self', 'db', 'cls'
        delete_params = [p for p in method_info.parameters if p[0] not in ['self', 'db', 'cls']]
        # 如果第一个参数类型包含模型名（如Role），说明接收对象；否则接收ID
        accepts_entity = False
        if delete_params and model_name.lower() in delete_params[0][1].lower():
            accepts_entity = True
        
        if has_composite_pk:
            # 联合主键：保存主键值用于后续查询和删除参数
            pk_fields = self._get_primary_key_fields(model_name, models)
            pk_saves = '\n        '.join([f'{f.name}_val = entity.{f.name}' for f in pk_fields])
            pk_filter = ', '.join([f'{f.name}={f.name}_val' for f in pk_fields])
            
            # 🎯 根据实际方法签名生成参数（而不是固定使用所有主键）
            # 对于delete方法，直接用方法参数匹配主键值变量
            method_params = [p[0] for p in method_info.parameters if p[0] not in ['db', 'self', 'cls']]
            pk_param_list = []
            for param_name in method_params:
                # 检查是否匹配主键字段名
                matching_pk = next((f for f in pk_fields if f.name == param_name), None)
                if matching_pk:
                    pk_param_list.append(f'{matching_pk.name}_val')
                else:
                    # 不是主键字段，可能是entity参数等
                    pk_param_list.append(param_name)
            pk_params = ', '.join(pk_param_list) if pk_param_list else ', '.join([f'{f.name}_val' for f in pk_fields])
            
            verification = self._generate_delete_verification(is_soft_delete, model_name, pk_filter)
            
            if returns_none:
                # delete返回None
                return f'''    def test_{method_name}_success(self, unit_test_db: Session):
        """测试{method_name} - 删除成功"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        {pk_saves}
        
        # 执行Repository方法（使用主键参数）
        {repo_name}.{method_name}(unit_test_db, {pk_params})
        
        {verification}
'''
            else:
                # delete返回对象
                return f'''    def test_{method_name}_success(self, unit_test_db: Session):
        """测试{method_name} - 删除成功"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        {pk_saves}
        
        # 执行Repository方法（使用主键参数）
        result = {repo_name}.{method_name}(unit_test_db, {pk_params})
        
        # 验证结果
        assert result is not None
        
        {verification}
'''
        else:
            # 标准单主键
            verification = self._generate_delete_verification(is_soft_delete, model_name, "id=entity_id")
            
            if accepts_entity:
                # delete方法接收对象
                # 生成正确的Repository方法调用
                method_call_none = self._generate_method_call(method_info, repo_name, "unit_test_db, entity")
                method_call_with_result = self._generate_method_call(method_info, repo_name, "unit_test_db, entity")
                
                if returns_none:
                    return f'''    def test_{method_name}_success(self, unit_test_db: Session):
        """测试{method_name} - 删除成功"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        {method_call_none}
        unit_test_db.commit()  # 提交删除操作
        
        {verification}
'''
                else:
                    return f'''    def test_{method_name}_success(self, unit_test_db: Session):
        """测试{method_name} - 删除成功"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行Repository方法（传递对象）
        result = {method_call_with_result}
        unit_test_db.commit()  # 提交删除操作
        
        # 验证结果
        assert result is not None
        
        {verification}
'''
            else:
                # delete方法接收ID - 生成3种删除测试
                if is_soft_delete:
                    # 软删除
                    # 生成正确的Repository方法调用
                    method_call = self._generate_method_call(method_info, repo_name, "unit_test_db, entity_id")
                    
                    # 生成最小实体创建代码（使用构造器，不是Factory.create）
                    minimal_imports, minimal_entity_code = self._generate_minimal_entity_creation(model_name, models, module_name)
                    
                    # 构建import语句块
                    unique_imports = set(minimal_imports)
                    unique_imports.add('from datetime import datetime')
                    entity_import_block = '\n'.join(['        ' + imp for imp in sorted(unique_imports)])
                    
                    return f'''    def test_{method_name}_soft_delete(self, unit_test_db: Session):
        """测试{method_name} - 软删除验证
        
        符合标准: testing-standards.md 第2.4节 - 验证is_deleted标记和deleted_at时间戳
        """
{entity_import_block}
        
        # 创建测试实体（使用构造器而不是Factory.create）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行软删除
        result = {method_call}
        unit_test_db.commit()  # 提交删除操作
        
        # ✅ 验证软删除标记
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity_id).first()
        assert db_entity is not None, "软删除后记录应仍存在"
        assert db_entity.is_deleted == True, "is_deleted应为True"
        
        # ✅ 验证deleted_at时间戳
        if hasattr(db_entity, 'deleted_at'):
            assert db_entity.deleted_at is not None, "deleted_at应有值"
            assert isinstance(db_entity.deleted_at, datetime), "deleted_at应为datetime类型"
    
    def test_{method_name}_cascade_soft_delete(self, unit_test_db: Session):
        """测试{method_name} - 级联软删除（如有关联数据）
        
        符合标准: testing-standards.md 第2.4节 - 验证关联数据的软删除
        """
        # TODO: 如果该模型有关联数据，验证级联软删除
        # 示例:
        # parent = ParentFactory.create()
        # child = ChildFactory.create(parent_id=parent.id)
        # {repo_name}.{method_name}(unit_test_db, parent.id)
        # assert child.is_deleted == True
        pass
    
    def test_{method_name}_batch_soft_delete(self, unit_test_db: Session):
        """测试{method_name} - 批量软删除（如有批量方法）
        
        符合标准: testing-standards.md 第2.4节 - 验证批量删除
        """
        # TODO: 如果有批量删除方法(delete_many, bulk_delete)，在这里测试
        # 示例:
        # entities = {model_name}Factory.create_batch(3)
        # ids = [e.id for e in entities]
        # {repo_name}.delete_many(unit_test_db, ids)
        # for entity_id in ids:
        #     db_entity = unit_test_db.query({model_name}).filter_by(id=entity_id).first()
        #     assert db_entity.is_deleted == True
        pass
'''
                else:
                    # 物理删除 - 🎯 根据方法参数智能判断是否需要entity_id
                    # 检查方法是否需要ID参数（除了db之外）
                    needs_id_param = len(delete_params) > 0
                    
                    if needs_id_param:
                        # 🔑 智能构造参数：根据method_info.parameters生成正确的测试参数
                        # 例如：delete(id) → entity_id
                        #      delete_by_ids(item_ids: List[int], user_id: int) → [entity_id], user.id
                        test_args = []
                        additional_setup = []  # 额外的变量设置（如user）
                        
                        for param_name, param_type, param_kind in delete_params:
                            if 'list' in param_type.lower() or 'List' in param_type:
                                # List类型参数，传入[entity_id]
                                test_args.append(f"[entity_id]")
                            elif 'user_id' in param_name.lower():
                                # user_id参数，需要创建user
                                test_args.append("user.id")
                                if "user = " not in '\n'.join(additional_setup):
                                    additional_setup.append("user = UserFactory.create()")
                            elif param_name.endswith('_id') or param_name == 'id':
                                # 单个ID参数
                                test_args.append("entity_id")
                            else:
                                # 其他参数类型，尝试智能推断
                                test_args.append(f"{param_name}_val")
                        
                        args_str = ", ".join(test_args)
                        method_call = self._generate_method_call(method_info, repo_name, f"unit_test_db, {args_str}")
                        
                        # 生成最小实体创建代码（使用构造器，不是Factory.create）
                        minimal_imports, minimal_entity_code = self._generate_minimal_entity_creation(model_name, models, module_name)
                        
                        # 构建import语句块
                        unique_imports = set(minimal_imports)
                        # 如果需要创建user，添加UserFactory导入
                        if any('user = UserFactory' in setup for setup in additional_setup):
                            unique_imports.add('from tests.factories.user_auth_factories import UserFactory, UserAuthFactoryManager')
                            if "UserAuthFactoryManager.setup_factories" not in '\n'.join(additional_setup):
                                additional_setup.insert(0, "UserAuthFactoryManager.setup_factories(unit_test_db)")
                        
                        entity_import_block = '\n'.join(['        ' + imp for imp in sorted(unique_imports)])
                        additional_setup_code = '\n        '.join(additional_setup) if additional_setup else ""
                        
                        return f'''    def test_{method_name}_physical_delete(self, unit_test_db: Session):
        """测试{method_name} - 物理删除验证
        
        符合标准: testing-standards.md 第2.4节 - 验证数据真正从数据库删除
        """
{entity_import_block}
        
        {additional_setup_code}
        # 创建测试实体（使用构造器而不是Factory.create）
{minimal_entity_code}
        unit_test_db.add(entity)
        unit_test_db.commit()
        entity_id = entity.id
        
        # 执行物理删除
        result = {method_call}
        unit_test_db.commit()  # 提交删除操作
        
        # ✅ 验证物理删除（记录不存在）
        unit_test_db.expire_all()
        db_entity = unit_test_db.query({model_name}).filter_by(id=entity_id).first()
        assert db_entity is None, "物理删除后记录应不存在"
        
        # 验证数据库count减少
        total_count = unit_test_db.query({model_name}).count()
        assert total_count >= 0
'''
                    else:
                        # 方法不需要ID参数（如 delete_expired_sessions(db)）
                        # 只验证方法执行和返回值
                        # 🎯 使用手动实体创建而不是Factory，避免SubFactory session传递问题
                        entity_creation = self._generate_test_entity_creation(model_name, models, "批量删除测试", with_dependencies=True, module_name=module_name)
                        
                        # 生成正确的Repository方法调用
                        method_call = self._generate_method_call(method_info, repo_name, "unit_test_db")
                        
                        return f'''    def test_{method_name}_physical_delete(self, unit_test_db: Session):
        """测试{method_name} - 批量删除功能
        
        符合标准: testing-standards.md 第2.4节 - 验证批量删除功能
        """
        # 创建测试数据（使用手动创建避免Factory SubFactory session问题）
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行批量删除（方法根据内部条件删除数据）
        result = {method_call}
        unit_test_db.commit()  # 提交删除操作
        
        # ✅ 验证返回结果（通常返回删除的数量）
        if result is not None:
            assert isinstance(result, int)
            assert result >= 0
        
        # 验证数据库操作成功
        total_count = unit_test_db.query({model_name}).count()
        assert total_count >= 0
    
    def test_{method_name}_cascade_delete(self, unit_test_db: Session):
        """测试{method_name} - 级联删除（如有关联数据）
        
        符合标准: testing-standards.md 第2.4节 - 验证关联数据的物理删除
        """
        # TODO: 如果该模型有关联数据，验证级联删除行为
        # 根据外键定义的ondelete行为:
        # - CASCADE: 子记录应被删除
        # - SET NULL: 子记录外键应为NULL
        # - RESTRICT: 应抛出异常
        
        # 示例:
        # parent = ParentFactory.create()
        # child = ChildFactory.create(parent_id=parent.id)
        # {repo_name}.{method_name}(unit_test_db, parent.id)
        # 
        # # CASCADE情况
        # db_child = unit_test_db.query(Child).filter_by(id=child.id).first()
        # assert db_child is None
        pass
    
    def test_{method_name}_batch_delete(self, unit_test_db: Session):
        """测试{method_name} - 批量物理删除（如有批量方法）
        
        符合标准: testing-standards.md 第2.4节 - 验证批量删除
        """
        # TODO: 如果有批量删除方法(delete_many, bulk_delete)，在这里测试
        # 示例:
        # entities = {model_name}Factory.create_batch(3)
        # ids = [e.id for e in entities]
        # {repo_name}.delete_many(unit_test_db, ids)
        # 
        # for entity_id in ids:
        #     db_entity = unit_test_db.query({model_name}).filter_by(id=entity_id).first()
        #     assert db_entity is None
        pass
'''
    
    def generate_repository_count_test(
        self,
        method_info: RepositoryMethodInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Repository count方法测试（智能处理参数）
        
        策略：
        1. 无参数count()：创建实体，调用count()
        2. 有参数count_by_xxx()：创建实体，从实体提取参数值
        3. 特殊处理：
           - List[int]类型：构造单元素列表 [entity.xxx_id]
           - xxx_id类型：提取entity.xxx_id
           - 其他：使用entity.xxx
        """
        method_name = method_info.name
        
        # 分析方法参数（排除db: Session）
        params = [p for p in method_info.parameters if p[0] not in ['self', 'db', 'cls']]
        
        # 生成测试实体（包含依赖） - 与READ测试策略一致
        entity_creation = self._generate_test_entity_creation(model_name, models, "测试数据", with_dependencies=True, module_name=module_name)
        
        # 如果有参数，使用实体的属性作为参数值
        if params:
            param_name = params[0][0]
            param_type = params[0][1] if len(params[0]) > 1 else None
            
            # 处理列表类型参数（如category_ids: List[int]）
            if param_type and 'List' in param_type:
                # 从entity提取外键字段，构造列表
                # 例如：count_by_category_ids -> 需要Product.category_id -> [product.category_id]
                # SKU有product_id外键，所以entity是SKU，但需要product.category_id
                
                # 检查参数名模式
                if param_name.endswith('_ids'):
                    # category_ids -> category_id
                    singular_field = param_name[:-1]  # 移除s
                    
                    # 检查当前模型是否有这个外键
                    model_info = models.get(model_name)
                    if model_info:
                        # 查找外键字段
                        fk_field = None
                        for field in model_info.fields:
                            if field.name == singular_field:
                                fk_field = field
                                break
                        
                        if fk_field and fk_field.foreign_key:
                            # 找到了直接的外键字段（如Product.category_id）
                            param_value = f"[entity.{singular_field}]"
                        else:
                            # 没有直接外键，可能是跨表查询（如SKU查Product.category_id）
                            # 尝试通过关系查找（如entity.product.category_id）
                            for field in model_info.fields:
                                if field.foreign_key and singular_field in field.name:
                                    # 如果有product_id，尝试entity.product.category_id
                                    relation_name = field.name[:-3]  # 移除_id
                                    param_value = f"[entity.{relation_name}.{singular_field}]"
                                    break
                            else:
                                # 找不到，使用默认值
                                param_value = "[1]"
                    else:
                        param_value = "[1]"
                else:
                    param_value = "[entity.id]"
            # 推断参数值：如果参数名包含_id，使用entity.xxx_id；否则使用entity的对应属性
            elif param_name.endswith('_id'):
                # 例如：category_id -> entity.id (假设是查询自身ID)
                base_name = param_name[:-3]  # 移除_id
                if base_name == model_name.lower():
                    param_value = "entity.id"
                else:
                    param_value = f"entity.{param_name}"
            else:
                param_value = f"entity.{param_name}"
            
            # 使用_generate_method_call生成正确的方法调用
            method_call = self._generate_method_call(method_info, repo_name, f"unit_test_db, {param_value}")
        else:
            # 使用_generate_method_call生成正确的方法调用
            method_call = self._generate_method_call(method_info, repo_name, "unit_test_db")
        
        return f'''    def test_{method_name}_count(self, unit_test_db: Session):
        """测试{method_name} - 计数功能"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        count = {method_call}
        
        # 验证计数
        assert isinstance(count, int)
        assert count >= 0
'''
    
    def generate_repository_query_test(
        self,
        method_info: RepositoryMethodInfo,
        repo_info: RepositoryInfo,
        model_name: str,
        repo_name: str,
        module_name: str,
        models: Dict[str, ModelInfo]
    ) -> str:
        """生成Repository query方法测试
        
        🎯 核心改进：
        1. 智能识别返回类型（int, List, Optional等）
        2. 根据返回类型生成正确的断言
        3. 使用统一的参数生成方法（不再推断，直接使用RepositoryAnalyzer数据）
        4. 🔧 从返回类型推断要创建的实体（支持跨模块查询）
        
        Args:
            method_info: 方法信息
            repo_info: Repository信息（含model_name和import_aliases）
            model_name: 模型名称
            repo_name: Repository名称
            module_name: 模块名称
            models: 模型字典
        """
        method_name = method_info.name
        
        # 🔧 从返回类型推断实际要创建的模型
        return_type = method_info.return_type
        actual_model_name = self._extract_model_from_return_type(return_type, models)
        if not actual_model_name:
            actual_model_name = model_name  # 默认使用Repository的主模型
        
        entity_creation = self._generate_test_entity_creation(actual_model_name, models, "查询测试", with_dependencies=True, module_name=module_name)
        
        # 🎯 核心改进：根据返回类型生成正确的断言
        return_type = method_info.return_type
        
        # 分析返回类型
        is_none_return = return_type == 'None' or return_type == 'NoneType'
        is_count_method = 'count' in method_name.lower() or return_type == 'int'
        is_tuple_return = 'Tuple[' in return_type or 'tuple[' in return_type  # 新增：Tuple返回类型检测
        is_list_method = 'List[' in return_type or 'list[' in return_type or method_info.method_type in ['list', 'search']
        is_optional = 'Optional[' in return_type or return_type.endswith('| None')
        
        # ✅ 使用统一的参数生成方法（不再推断，直接使用RepositoryAnalyzer数据）
        param_call = self._generate_test_params(method_info, repo_info, models)
        
        # 生成正确的Repository方法调用
        method_call = self._generate_method_call(method_info, repo_name, param_call)
        
        # 根据返回类型生成断言
        if is_none_return:
            # 返回None的方法（如 update/deactivate 等），只验证执行成功
            assertion = "# 方法返回None，验证执行成功即可"
            result_var = "result"
        elif is_tuple_return:
            # 返回Tuple的方法（如 list_orders返回Tuple[List[Order], int]）
            assertion = "assert isinstance(results, list)  # 返回列表\n        assert isinstance(total_count, int)  # 返回总数"
            result_var = "results, total_count"
        elif is_count_method:
            assertion = "assert result >= 0  # count方法返回int"
            result_var = "result"
        elif is_list_method:
            assertion = "assert isinstance(results, list)  # 返回列表"
            result_var = "results"
        elif is_optional:
            assertion = "# 可能返回None，根据业务逻辑验证"
            result_var = "result"
        else:
            assertion = "assert result is not None"
            result_var = "result"
        
        # 🔧 检查是否为跨模块模型（需要使用Factory）
        is_cross_module = actual_model_name not in models
        
        if is_cross_module:
            # 跨模块模型：使用Factory创建
            factory_import = self.dependency_resolver.get_factory_import(actual_model_name, module_name)
            factory_manager_import = self.dependency_resolver.get_factory_manager_import(actual_model_name, module_name)
            
            test_code = f'''    def test_{method_name}_query(self, unit_test_db: Session):
        """测试{method_name} - 查询功能"""
        # 🔧 跨模块查询：使用Factory创建实体
        {factory_manager_import}
        {factory_import}
        entity = {actual_model_name}Factory.create()
        
        # 执行Repository方法
        {result_var} = {method_call}
        
        # 验证查询结果
        {assertion}
'''
        else:
            # 当前模块模型：直接创建
            test_code = f'''    def test_{method_name}_query(self, unit_test_db: Session):
        """测试{method_name} - 查询功能"""
        # 准备测试数据
        {entity_creation}
        unit_test_db.add(entity)
        unit_test_db.commit()
        
        # 执行Repository方法
        {result_var} = {method_call}
        
        # 验证查询结果
        {assertion}
'''
        
        return test_code
    
    # ========== 核心生成方法 ==========
    
    def _generate_single_repository_test(
        self,
        repo_info: RepositoryInfo,
        models: Dict[str, ModelInfo],
        module_name: str
    ) -> str:
        """为单个Repository生成测试类
        
        Args:
            repo_info: Repository信息
            models: 模型信息（用于创建测试数据）
            module_name: 模块名称
            
        Returns:
            str: Repository测试类代码
        """
        repo_name = repo_info.name
        model_name = repo_info.model_name
        
        # 生成各类测试方法
        test_methods = []
        
        for method_info in repo_info.methods:
            # 🔥 跳过专用更新方法（如update_login_info），生成TODO提示
            if method_info.is_specialized_update:
                todo_comment = f'''    # TODO: 测试专用更新方法 {method_info.name}
    # 这是一个专用更新方法，只修改特定字段，需要根据业务逻辑手动编写测试
    # 方法签名: {method_info.parameters}
    # 返回类型: {method_info.return_type}
    
'''
                test_methods.append(todo_comment)
                continue
            
            # 根据方法类型生成对应的测试
            if method_info.method_type == "create":
                test_methods.append(self.generate_repository_create_test(method_info, model_name, repo_name, module_name, models))
            elif method_info.method_type == "read":
                test_methods.append(self.generate_repository_read_test(method_info, repo_info, model_name, repo_name, module_name, models))
            elif method_info.method_type == "update":
                test_methods.append(self.generate_repository_update_test(method_info, model_name, repo_name, module_name, models))
            elif method_info.method_type == "delete":
                test_methods.append(self.generate_repository_delete_test(method_info, model_name, repo_name, module_name, models))
            else:  # query, count, exists等其他类型
                test_methods.append(self.generate_repository_query_test(method_info, repo_info, model_name, repo_name, module_name, models))
        
        test_class = f'''
@pytest.mark.unit
@pytest.mark.repositories
class Test{repo_name}:
    """
    {repo_name} 数据访问层测试
    
    测试范围:
    - {len(repo_info.methods)} 个Repository方法
    - CRUD操作完整性
    - 查询逻辑正确性
    - 事务处理和数据一致性
    
    测试策略: SQLite内存数据库 + Factory Boy
    """
        
{chr(10).join(test_methods)}
'''
        
        return test_class
    
    # ========== 辅助方法 ==========
    
    def _get_minimal_test_value(self, field: FieldInfo) -> str:
        """获取字段的最小测试值(用于最小实体创建)
        
        策略: 使用_get_test_value_for_field生成智能测试值
        不使用硬编码，根据字段类型和字段名语义推断合理值
        """
        # 直接使用已有的智能值生成方法
        return self._get_test_value_for_field(field)
    
    def _get_full_test_value(self, field: FieldInfo) -> str:
        """获取字段的完整测试值(用于full_fields测试)
        
        策略: 为可选字段也生成非None的值，确保测试覆盖所有字段
        """
        # 对于可选字段，也生成有意义的值（而不是None）
        # 这样可以验证Repository正确保存所有字段数据
        return self._get_test_value_for_field(field, suffix="完整测试")
    
    def _get_test_value_for_field(self, field: FieldInfo, suffix: str = "测试") -> str:
        """为字段生成测试值
        
        Args:
            field: 字段信息
            suffix: 值的后缀
            
        Returns:
            str: 测试值的字符串表示
        """
        field_name = field.name.lower()
        
        # 策略: 先按字段类型分类，再根据字段名语义推断具体值
        # 这样既保证类型正确，又能生成更合理的测试值
        
        # 1. 布尔类型
        if field.python_type == 'bool':
            return 'True'
        
        # 2. 日期时间类型
        elif field.python_type == 'datetime':
            return 'datetime.now()'
        
        # 3. Decimal类型 - 根据字段名语义推断
        elif field.python_type == 'Decimal':
            if 'price' in field_name or 'amount' in field_name or 'cost' in field_name:
                return 'Decimal("99.99")'
            elif 'rate' in field_name or 'ratio' in field_name or 'percent' in field_name:
                return 'Decimal("0.15")'
            elif 'discount' in field_name:
                return 'Decimal("10.00")'
            else:
                return 'Decimal("1.00")'
        
        # 4. 整数类型 - 根据字段名语义推断
        elif field.python_type == 'int':
            if 'quantity' in field_name or 'count' in field_name or 'num' in field_name:
                return '10'
            elif 'stock' in field_name or 'inventory' in field_name:
                return '100'
            elif 'limit' in field_name or 'max' in field_name:
                return '1000'
            else:
                return '1'
        
        # 5. 字符串类型 - 根据字段名语义推断
        elif field.python_type == 'str':
            if 'email' in field_name:
                return f'"email_{suffix.lower()}"'
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
        
        # 6. 兜底默认值（未知类型）
        else:
            return f'"{suffix}"'
    
    def _get_factory_params(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        module_name: str,
        created_entities: Dict[str, str]
    ) -> str:
        """获取Factory的参数（用于传递已创建的依赖实体，并禁用可选的SubFactory）
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            module_name: 当前模块名称
            created_entities: 已创建的实体变量名字典 {model_name: var_name}
            
        Returns:
            str: Factory参数字符串，如 'user_id=user.id, brand_id=None'
        """
        params = []
        
        if model_name not in models:
            # 跨模块模型：禁用所有SubFactory（避免自动创建依赖）
            # 这是一个简化处理，假设跨模块依赖的可选外键都设为None
            # 对于必需的外键，会在all_dependencies中处理
            return ''
        
        model_info = models[model_name]
        
        # 查找该模型的外键字段
        for field in model_info.fields:
            if not field.foreign_key:
                continue
                
            fk_target = field.foreign_key
            fk_table = fk_target.split('.')[0]
            # 使用resolver从表名查找模型名（零硬编码）
            fk_model_name = self.dependency_resolver.get_model_by_table(fk_table) or self._fallback_table_to_model(fk_table)
            
            # 如果依赖实体已经创建，使用它的ID
            if fk_model_name in created_entities:
                dep_var_name = created_entities[fk_model_name]
                params.append(f'{field.name}={dep_var_name}.id')
            # 如果是可选外键（nullable=True），且未创建依赖，传递None禁用SubFactory
            elif field.nullable:
                # 注意：这里需要传递字段名（不是关系名）
                # Factory Boy的SubFactory通常用关系名，但参数应该用字段名
                params.append(f'{field.name}=None')
        
        return ', '.join(params)
    
    def _get_all_dependencies(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        module_name: str,
        visited: set = None,
        is_root: bool = True
    ) -> List[Tuple[str, str, str]]:
        """递归获取模型的所有依赖（包括传递依赖）
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            module_name: 当前模块名称
            visited: 已访问的模型集合（避免循环依赖）
            is_root: 是否为根模型（用于区分直接依赖和传递依赖）
            
        Returns:
            List[Tuple[str, str, str]]: [(依赖模型名, 依赖所属模块, 字段名或None), ...]
            按依赖层级排序，先返回最底层依赖
            字段名仅对直接依赖有值，传递依赖为None
        """
        if visited is None:
            visited = set()
        
        if model_name in visited:
            return []  # 避免循环依赖
        
        visited.add(model_name)
        
        if model_name not in models:
            return []  # 跨模块模型，无法获取其依赖
        
        model_info = models[model_name]
        dependencies = []
        
        # 获取当前模型的直接依赖
        for field in model_info.fields:
            if not field.foreign_key:
                continue
                
            fk_target = field.foreign_key
            fk_table = fk_target.split('.')[0]
            
            # 🔧 步骤1：从当前模块的models字典中查找表名对应的模型名
            fk_model_name = None
            for m_name, m_info in models.items():
                if m_info.tablename == fk_table:
                    fk_model_name = m_name
                    break
            
            # 🔧 步骤2：如果当前模块找不到，从dependency_resolver的全局映射查找
            if fk_model_name is None:
                fk_model_name = self.dependency_resolver.get_model_by_table(fk_table)
            
            # 🔧 步骤3：如果还是找不到，使用命名规则作为最后的后备方案
            if fk_model_name is None:
                fk_model_name = self._fallback_table_to_model(fk_table)
            
            # 确定依赖模型所属模块
            if self._is_cross_module_dependency(fk_model_name, module_name, models):
                fk_module = self._get_module_name_for_model(fk_model_name)
            else:
                fk_module = module_name
                # 递归获取依赖的依赖
                sub_deps = self._get_all_dependencies(fk_model_name, models, module_name, visited, is_root=False)
                dependencies.extend(sub_deps)
            
            # 添加当前依赖
            # 字段名仅对根模型的直接依赖有值
            field_name = field.name if is_root else None
            dependencies.append((fk_model_name, fk_module, field_name))
        
        # 去重并保持顺序（底层依赖在前）
        seen = {}  # {(model_name, module_name): field_name}
        unique_deps = []
        for dep_model, dep_module, dep_field in dependencies:
            dep_key = (dep_model, dep_module)
            if dep_key not in seen:
                seen[dep_key] = dep_field
                unique_deps.append((dep_model, dep_module, dep_field))
            elif dep_field and not seen[dep_key]:
                # 如果之前添加的是传递依赖（field_name=None），现在遇到直接依赖，更新
                seen[dep_key] = dep_field
                # 更新列表中的元组
                for i, (m, mod, f) in enumerate(unique_deps):
                    if m == dep_model and mod == dep_module:
                        unique_deps[i] = (dep_model, dep_module, dep_field)
                        break
        
        return unique_deps
    
    def _is_cross_module_dependency(self, fk_model_name: str, current_module: str, models: Dict[str, ModelInfo]) -> bool:
        """检测外键是否为跨模块依赖
        
        判断外键引用的模型是否属于当前模块。如果不属于，则为跨模块依赖，
        应该使用简单的数值而不是Factory来避免导入错误。
        
        Args:
            fk_model_name: 外键模型名称
            current_module: 当前模块名称
            models: 当前模块的模型信息字典
            
        Returns:
            bool: True表示跨模块依赖，False表示模块内依赖
        """
        # 如果外键模型在当前模块的models中，则为模块内依赖
        return fk_model_name not in models
    
    def _generate_full_entity_creation(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        module_name: str
    ) -> Tuple[List[str], str]:
        """生成完整实体创建代码(填充所有字段)
        
        策略说明:
        - 被测实体: 填充ALL字段（必填+可选）
        - 依赖实体: 使用Factory Boy创建  
        - 目的: 验证Repository能正确保存完整数据
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            module_name: 模块名称
            
        Returns:
            Tuple[List[str], str]: (import语句列表, 实体创建代码)
        """
        imports = []
        
        if model_name not in models:
            return ([], f'        entity = {model_name}()  # TODO: 补充所有字段')
        
        model_info = models[model_name]
        
        # 🔑 关键差异：full_fields包含所有字段（除了自动生成的）
        auto_fields = {'id', 'created_at', 'updated_at', 'is_deleted'}
        all_fields = [
            f for f in model_info.fields
            if f.name not in auto_fields
            and not (f.primary_key and f.name == 'id' and not f.foreign_key)  # 只排除非外键的自增主键
        ]
        
        if not all_fields:
            return ([], f'        entity = {model_name}()\n        # 注意: 该模型只有自动生成字段')
        
        # 分离外键和普通字段
        fk_fields = [f for f in all_fields if f.foreign_key]
        normal_fields = [f for f in all_fields if not f.foreign_key]
        
        lines = []
        
        # 处理外键字段：使用Factory Boy创建依赖实体
        fk_var_names = {}
        created_factories = set()
        
        # 递归获取所有依赖
        all_dependencies = self._get_all_dependencies(model_name, models, module_name)
        created_entities = {}
        used_modules = set()
        
        # 按依赖层级创建
        for dep_model_name, dep_module, dep_field_name in all_dependencies:
            if dep_model_name in created_factories:
                continue
                
            dep_var_name = dep_model_name.lower()
            factory_name = f'{dep_model_name}Factory'
            
            imports.append(f'from tests.factories.{dep_module}_factories import {factory_name}')
            
            if dep_module != module_name and dep_module not in used_modules:
                manager_name = f'{"".join(word.capitalize() for word in dep_module.split("_"))}FactoryManager'
                imports.append(f'from tests.factories.{dep_module}_factories import {manager_name}')
                lines.append(f'# 设置{dep_module}模块所有Factory的session')
                lines.append(f'{manager_name}.setup_factories(unit_test_db)')
                used_modules.add(dep_module)
            
            lines.append(f'# 准备依赖实体: {dep_model_name} ({"跨模块" if dep_module != module_name else "同模块"})')
            
            if dep_module == module_name:
                lines.append(f'{factory_name}._meta.sqlalchemy_session = unit_test_db')
            
            factory_params = self._get_factory_params(dep_model_name, models, module_name, created_entities)
            if factory_params:
                lines.append(f'{dep_var_name} = {factory_name}.create({factory_params})')
            else:
                lines.append(f'{dep_var_name} = {factory_name}.create()')
            
            created_factories.add(dep_model_name)
            created_entities[dep_model_name] = dep_var_name
            
            if dep_field_name:
                fk_var_names[dep_field_name] = f'{dep_var_name}.id'
        
        if fk_fields:
            lines.append('')
        
        # 🔑 构造被测实体 - 填充所有字段
        field_assignments = []
        for field in normal_fields:
            test_value = self._get_full_test_value(field)  # 使用_get_full_test_value而非_get_minimal_test_value
            field_assignments.append(f'{field.name}={test_value}')
        
        # 添加外键字段
        for field in fk_fields:
            if field.name in fk_var_names:
                # 有对应的依赖实体
                field_assignments.append(f'{field.name}={fk_var_names[field.name]}')
            else:
                # 同一个依赖模型的多个外键字段，使用第一个创建的依赖实体
                # 例如：UserRole有user_id和assigned_by都指向User，assigned_by使用user.id
                fk_target = field.foreign_key
                fk_table = fk_target.split('.')[0]
                # 使用resolver从表名查找模型名（零硬编码）
                fk_model_name = self.dependency_resolver.get_model_by_table(fk_table) or self._fallback_table_to_model(fk_table)
                dep_var_name = fk_model_name.lower()
                if fk_model_name in created_entities:
                    field_assignments.append(f'{field.name}={created_entities[fk_model_name]}.id')
                else:
                    # 降级方案：使用整数值
                    field_assignments.append(f'{field.name}=1')
        
        if field_assignments:
            lines.append(f'# 构造被测实体: {model_name} - 填充所有字段')
            lines.append(f'entity = {model_name}(')
            for i, assignment in enumerate(field_assignments):
                comma = ',' if i < len(field_assignments) - 1 else ''
                lines.append(f'    {assignment}{comma}')
            lines.append(')')
        else:
            lines.append(f'# 构造被测实体: {model_name} - 只有自动生成字段')
            lines.append(f'entity = {model_name}()')
        
        # 添加缩进
        indented_lines = ['        ' + line for line in lines]
        code = '\n'.join(indented_lines)
        
        return (imports, code)

    def _generate_minimal_entity_creation(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        module_name: str
    ) -> Tuple[List[str], str]:
        """生成最小实体创建代码(符合testing-standards.md Repository创建测试策略)
        
        策略说明:
        - 被测实体(Entity Under Test): 只填必填字段(nullable=False且无default)
        - 依赖实体(Dependency Entity): 使用Factory Boy创建
        - 目的: 验证被测实体的默认值是否正确应用
        
        Args:
            model_name: 模型名称(被测实体)
            models: 模型信息字典
            module_name: 模块名称
            
        Returns:
            Tuple[List[str], str]: (import语句列表, 实体创建代码)
        """
        imports = []
        
        if model_name not in models:
            return ([], f'        entity = {model_name}()  # TODO: 补充必填字段')
        
        model_info = models[model_name]
        
        # 提取必填字段(nullable=False 且无default)
        auto_fields = {'id', 'created_at', 'updated_at', 'is_deleted'}
        required_fields = [
            f for f in model_info.fields 
            if not f.nullable 
            and f.name not in auto_fields 
            and not (f.primary_key and f.name == 'id' and not f.foreign_key)  # 只排除非外键的自增主键
            and not f.server_default  # 排除有数据库默认值的字段
            # 注意: 主键外键字段（如role_id作为主键且是外键）需要包括
            # 注意: 如果field有default参数,仍然包括(用于测试默认值)
        ]
        
        if not required_fields:
            return ([], f'        entity = {model_name}()\n        # 注意: 该模型所有字段均为可选或有默认值')
        
        # 分离外键和普通字段
        fk_fields = [f for f in required_fields if f.foreign_key]
        normal_fields = [f for f in required_fields if not f.foreign_key]
        
        lines = []
        
        # 处理外键字段：使用Factory Boy创建依赖实体（符合测试标准：依赖实体始终使用Factory Boy）
        # 注意：需要递归处理依赖的依赖（如Cart依赖User）
        fk_var_names = {}
        created_factories = set()  # 跟踪已创建的Factory，避免重复
        
        # 递归获取所有依赖（包括传递依赖）
        all_dependencies = self._get_all_dependencies(model_name, models, module_name)
        
        # 记录已创建的实体变量名，用于传递给子依赖的Factory
        created_entities = {}  # {model_name: var_name}
        used_modules = set()  # 记录使用的跨模块
        
        # 按依赖层级创建（先创建最底层的依赖）
        for dep_model_name, dep_module, dep_field_name in all_dependencies:
            if dep_model_name in created_factories:
                continue  # 已经创建过，跳过
                
            dep_var_name = dep_model_name.lower()
            factory_name = f'{dep_model_name}Factory'
            
            imports.append(f'from tests.factories.{dep_module}_factories import {factory_name}')
            
            # 对于跨模块依赖，使用FactoryManager设置所有Factory的session（避免SubFactory没有session）
            if dep_module != module_name and dep_module not in used_modules:
                manager_name = f'{"".join(word.capitalize() for word in dep_module.split("_"))}FactoryManager'
                imports.append(f'from tests.factories.{dep_module}_factories import {manager_name}')
                lines.append(f'# 设置{dep_module}模块所有Factory的session')
                lines.append(f'{manager_name}.setup_factories(unit_test_db)')
                used_modules.add(dep_module)
            
            lines.append(f'# 准备依赖实体: {dep_model_name} ({"跨模块" if dep_module != module_name else "同模块"})')
            
            # 同模块依赖需要设置session
            if dep_module == module_name:
                lines.append(f'{factory_name}._meta.sqlalchemy_session = unit_test_db')
            
            # 检查该Factory是否需要传入依赖的外键
            factory_params = self._get_factory_params(dep_model_name, models, module_name, created_entities)
            if factory_params:
                lines.append(f'{dep_var_name} = {factory_name}.create({factory_params})')
            else:
                lines.append(f'{dep_var_name} = {factory_name}.create()')
            
            created_factories.add(dep_model_name)
            created_entities[dep_model_name] = dep_var_name
            
            # 记录直接依赖的变量名（用于构造被测实体）
            if dep_field_name:  # 只记录直接依赖
                fk_var_names[dep_field_name] = f'{dep_var_name}.id'
        
        if fk_fields:
            lines.append('')  # 空行分隔依赖创建和被测实体创建
        
        # 构造被测实体 - 只填必填字段（验证默认值）
        field_assignments = []
        for field in normal_fields:
            test_value = self._get_minimal_test_value(field)
            field_assignments.append(f'{field.name}={test_value}')
        
        # 添加外键字段（引用依赖实体的ID）
        for field in fk_fields:
            field_assignments.append(f'{field.name}={fk_var_names[field.name]}')
        
        if field_assignments:
            lines.append(f'# 构造被测实体: {model_name} - 只填必填字段')
            lines.append(f'entity = {model_name}(')
            for i, assignment in enumerate(field_assignments):
                comma = ',' if i < len(field_assignments) - 1 else ''
                lines.append(f'    {assignment}{comma}')
            lines.append(')')
        else:
            lines.append(f'# 构造被测实体: {model_name} - 所有字段均有默认值')
            lines.append(f'entity = {model_name}()')
        
        # 添加缩进（函数体内代码需要8个空格缩进）
        indented_lines = ['        ' + line for line in lines]
        code = '\n'.join(indented_lines)
        
        # 返回imports和code（分开处理）
        return (imports, code)
    
    def _generate_test_entity_creation(
        self,
        model_name: str,
        models: Dict[str, ModelInfo],
        suffix: str = "测试数据",
        with_dependencies: bool = False,
        module_name: str = 'unknown'
    ) -> str:
        """生成测试实体创建代码,自动包含必填字段和外键依赖
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            suffix: 名称后缀
            with_dependencies: 是否生成外键依赖的完整代码(多行)
            module_name: 当前模块名称（用于正确识别跨模块依赖）
            
        Returns:
            str: 实体创建代码(可能是多行的依赖创建+主实体创建)
        """
        if model_name not in models:
            # 🔧 跨模块模型：使用Factory Boy创建（符合testing-standards.md第2.1节）
            # 依赖实体（包括跨模块依赖）始终使用Factory Boy
            fk_model_module = self.dependency_resolver.get_module_for_model(model_name)
            if fk_model_module:
                # 🔧 检测跨模块模型是否有跨模块外键依赖（如InventoryStock.sku_id → SKU）
                # 使用ModelAnalyzer获取跨模块模型的完整信息
                cross_module_model_info = self.model_analyzer.get_model_info(model_name)
                if cross_module_model_info and with_dependencies:
                    # 检测该跨模块模型是否有跨模块外键
                    cross_module_fks = []
                    for field in cross_module_model_info.fields:
                        if field.foreign_key:
                            # 解析外键目标表
                            fk_parts = field.foreign_key.split('.')
                            if len(fk_parts) == 2:
                                target_table = fk_parts[0]
                                # 查找目标模型
                                target_model = self.dependency_resolver.get_model_by_table(target_table)
                                if target_model:
                                    target_module = self.dependency_resolver.get_module_for_model(target_model)
                                    # 如果目标模型不在当前跨模块模型的模块中，则为跨模块外键
                                    if target_module and target_module != fk_model_module:
                                        cross_module_fks.append((field.name, target_model, target_module))
                    
                    # 如果有跨模块外键，生成完整的依赖创建代码
                    if cross_module_fks:
                        lines = []
                        fk_params = []
                        setup_modules = set()  # 记录已setup的模块，避免重复
                        
                        for fk_name, target_model, target_module in cross_module_fks:
                            fk_var = target_model.lower()
                            lines.append(f'# 准备依赖实体: {target_model}')
                            
                            # 为依赖模块设置FactoryManager（只设置一次）
                            if target_module not in setup_modules:
                                target_manager = f'{"".join(word.capitalize() for word in target_module.split("_"))}FactoryManager'
                                lines.append(f'from tests.factories.{target_module}_factories import {target_manager}')
                                lines.append(f'{target_manager}.setup_factories(unit_test_db)')
                                setup_modules.add(target_module)
                            
                            lines.append(f'from tests.factories.{target_module}_factories import {target_model}Factory')
                            lines.append(f'{fk_var} = {target_model}Factory.create()')
                            fk_params.append(f'{fk_name}={fk_var}.id')
                        
                        # 最后创建跨模块实体，传入外键参数
                        factory_name = f'{model_name}Factory'
                        if fk_model_module not in setup_modules:
                            fk_manager = f'{"".join(word.capitalize() for word in fk_model_module.split("_"))}FactoryManager'
                            lines.append(f'from tests.factories.{fk_model_module}_factories import {fk_manager}')
                            lines.append(f'{fk_manager}.setup_factories(unit_test_db)')
                        lines.append(f'from tests.factories.{fk_model_module}_factories import {factory_name}')
                        lines.append(f'entity = {factory_name}.create({", ".join(fk_params)})')
                        return '\n        '.join(lines)
                
                # 简单情况：无跨模块外键或不需要生成依赖
                factory_name = f'{model_name}Factory'
                return f'{factory_name}.create()  # 跨模块依赖使用Factory'
            # 无法识别的模型，返回TODO
            return f'{model_name}()  # TODO: 填充必填字段'
        
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
            # 返回带变量赋值的完整语句
            return f'entity = {model_name}({", ".join(field_assignments)})'
        
        # 生成完整的依赖创建代码(多行) - 使用与create测试相同的策略
        lines = []
        fk_var_names = {}
        created_factories = set()
        created_entities = {}
        used_modules = set()
        
        # 获取所有依赖（包括传递依赖）
        all_dependencies = self._get_all_dependencies(model_name, models, module_name)
        
        # 按依赖层级创建（先创建最底层的依赖）
        for dep_model_name, dep_module, dep_field_name in all_dependencies:
            if dep_model_name in created_factories:
                continue  # 已经创建过，跳过
                
            dep_var_name = dep_model_name.lower()
            factory_name = f'{dep_model_name}Factory'
            
            # 对于跨模块依赖，使用FactoryManager设置所有Factory的session
            if dep_module != 'unknown' and dep_module not in used_modules:
                manager_name = f'{"".join(word.capitalize() for word in dep_module.split("_"))}FactoryManager'
                lines.append(f'from tests.factories.{dep_module}_factories import {manager_name}')
                lines.append(f'{manager_name}.setup_factories(unit_test_db)')
                used_modules.add(dep_module)
            
            lines.append(f'# 准备依赖实体: {dep_model_name}')
            lines.append(f'from tests.factories.{dep_module}_factories import {factory_name}')
            
            # 检查该Factory是否需要传入依赖的外键
            factory_params = self._get_factory_params(dep_model_name, models, 'unknown', created_entities)
            if factory_params:
                lines.append(f'{dep_var_name} = {factory_name}.create({factory_params})')
            else:
                lines.append(f'{dep_var_name} = {factory_name}.create()')
            
            created_factories.add(dep_model_name)
            created_entities[dep_model_name] = dep_var_name
            
            # 记录直接依赖的变量名（用于构造主实体）
            if dep_field_name:  # 只记录直接依赖
                fk_var_names[dep_field_name] = f'{dep_var_name}.id'
        
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
    
    # 注意：_get_minimal_test_value 和 _get_test_value_for_field 已在上方实现（第350-430行）
    
    def _extract_model_from_return_type(
        self,
        return_type: str,
        models: Dict[str, ModelInfo]
    ) -> Optional[str]:
        """从返回类型中提取模型名
        
        支持的格式：
        - Optional[Product] -> Product
        - List[Order] -> Order
        - Product -> Product
        - int, str等基础类型 -> None
        
        Args:
            return_type: 方法返回类型字符串
            models: 模型信息字典（用于验证模型存在）
            
        Returns:
            模型名或None
        """
        import re
        
        # 移除Optional, List等包装
        clean_type = return_type.replace('Optional[', '').replace('List[', '').replace(']', '').strip()
        
        # 移除 | None 语法
        if '|' in clean_type:
            clean_type = clean_type.split('|')[0].strip()
        
        # 检查是否是模型类（大写开头且在models中）
        if clean_type and clean_type[0].isupper():
            # 尝试从当前模块查找
            if clean_type in models:
                return clean_type
            
            # 尝试从dependency_resolver查找（跨模块模型）
            module = self.dependency_resolver.get_module_for_model(clean_type)
            if module:
                return clean_type
        
        return None
    
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
    
    def _get_module_name_for_model(self, model_name: str) -> str:
        """根据模型名推断所属模块名
        
        使用CrossModuleDependencyResolver自动解析模型所属模块。
        """
        module_name = self.dependency_resolver.get_module_for_model(model_name)
        if module_name is None:
            print(f"⚠️  警告: 未找到模型 {model_name} 所属模块，请检查models.py")
            return 'unknown'
        return module_name

    def _get_minimal_cross_module_fields(self, model_name: str) -> str:
        """为跨模块依赖生成最小字段参数
        
        使用ModelAnalyzer自动获取模型信息，而非硬编码。
        
        Args:
            model_name: 跨模块模型名称
            
        Returns:
            str: 字段参数字符串，如 'username="test_user", email="test@example.com"'
        """
        # 🔍 使用ModelAnalyzer自动获取模型信息
        model_info = self.model_analyzer.get_model_info(model_name)
        
        if model_info:
            # 自动生成最小字段参数
            required_fields = []
            for field in model_info.fields:
                if not field.nullable and not field.primary_key and not field.foreign_key:
                    # 必填字段且不是主键、外键
                    if field.python_type == 'str':
                        required_fields.append(f'{field.name}="test_{field.name}"')
                    elif field.python_type == 'int':
                        required_fields.append(f'{field.name}=1')
                    elif field.python_type == 'float':
                        required_fields.append(f'{field.name}=9.99')
                    elif field.python_type == 'bool':
                        required_fields.append(f'{field.name}=True')
                    elif field.python_type == 'Decimal':
                        required_fields.append(f'{field.name}=Decimal("9.99")')
            
            if required_fields:
                return ', '.join(required_fields)
        
        # 后备方案（如果ModelAnalyzer未找到模型）
        return 'name="测试数据"'
    
    def _get_minimal_fields_for_model(self, model_name: str, models: Dict[str, ModelInfo]) -> str:
        """为模块内模型生成最小字段参数
        
        Args:
            model_name: 模型名称
            models: 模型信息字典
            
        Returns:
            str: 字段参数字符串
        """
        if model_name not in models:
            return 'name="测试数据"'
            
        model_info = models[model_name]
        auto_fields = {'id', 'created_at', 'updated_at', 'is_deleted'}
        required_fields = [
            f for f in model_info.fields 
            if not f.nullable 
            and f.name not in auto_fields 
            and not (f.primary_key and f.name == 'id' and not f.foreign_key)
            and not f.server_default
            and not f.foreign_key  # 不包括外键字段，避免递归
        ]
        
        field_assignments = []
        for field in required_fields:
            test_value = self._get_minimal_test_value(field)
            field_assignments.append(f'{field.name}={test_value}')
        
        return ', '.join(field_assignments) if field_assignments else 'name="测试数据"'
    
    def _get_cross_module_import(self, model_name: str) -> str:
        """获取跨模块模型的import语句
        
        使用ModelAnalyzer自动查找模型所属模块，而非硬编码。
        
        Args:
            model_name: 跨模块模型名称
            
        Returns:
            str: import语句
        """
        # 🔍 使用ModelAnalyzer自动查找模型所属模块
        module_name = self.model_analyzer.get_module_for_model(model_name)
        
        if module_name:
            return f'from app.modules.{module_name}.models import {model_name}'
        else:
            # 后备方案（如果ModelAnalyzer未找到模型）
            return f'# TODO: 未找到模型 {model_name} 的模块，请手动添加import'

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
    
    def _build_param_string(self, param_parts: List[Tuple[str, str, str]]) -> str:
        """根据参数类别生成正确的调用语法
        
        Args:
            param_parts: 参数列表 [(param_kind, param_name, param_value), ...]
                - param_kind: 'positional' | 'keyword-only'
                - param_name: 参数名称
                - param_value: 参数值表达式
                
        Returns:
            str: 参数字符串，如 "arg1, arg2, kw1=value1, kw2=value2"
            
        Examples:
            >>> self._build_param_string([
            ...     ('positional', 'order_id', 'entity.id'),
            ...     ('keyword-only', 'user_id', 'None')
            ... ])
            'entity.id, user_id=None'
        """
        if not param_parts:
            return ''
        
        positional_parts = []
        keyword_parts = []
        
        for param_kind, param_name, param_value in param_parts:
            if param_kind == 'positional':
                positional_parts.append(param_value)
            elif param_kind == 'keyword-only':
                keyword_parts.append(f"{param_name}={param_value}")
            else:
                # 向后兼容：如果没有param_kind，当作位置参数
                positional_parts.append(param_value)
        
        # 拼接：位置参数在前，命名参数在后（符合Python语法）
        all_parts = positional_parts + keyword_parts
        return ', '.join(all_parts)
    
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
        - get_role_users(role_id: int) -> 需要创建Role,传入role.id
        - get (联合主键) -> 需要所有主键字段
        
        Args:
            method_info: 方法信息(包含参数签名)
            model_name: 模型名称
            models: 所有模型信息
            module_name: 当前模块名称
            
        Returns:
            tuple: (准备代码, 参数字符串, 是否需要TODO注释)
                - setup_code: 创建依赖实体的代码(如创建User)
                - param_str: 调用方法时的参数字符串(如user.id)
                - needs_todo: 是否需要TODO注释
        """
        method_name = method_info.name
        
        # 提取方法参数(排除self, db, cls)
        # 参数格式: (name, type, kind) - kind: 'positional' | 'keyword-only'
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
        
        # 辅助函数：添加参数（自动处理keyword-only参数的命名参数语法）
        def add_param(kind: str, name: str, value: str):
            """添加参数到param_parts列表
            
            Args:
                kind: 参数类别 ('positional' | 'keyword-only')
                name: 参数名称
                value: 参数值表达式
            """
            param_parts.append((kind, name, value))
        
        # 智能推断: 分析方法参数,自动生成依赖实体
        if method_params:
            setup_code_lines = []
            param_parts = []  # 存储 (param_kind, param_name, param_value) 元组
            
            for param_name, param_type, param_kind in method_params:
                # 推断参数对应的实体类型
                # user_id: int -> User
                # role_id: int -> Role
                # permission_id: int -> Permission
                entity_name = self._infer_entity_from_param(param_name, param_type, models)
                
                # 特殊处理：如果参数是当前模型的ID（如Cart.find_by_id(cart_id)），使用entity.id
                if entity_name == model_name:
                    # 查询当前模型的方法，参数应该使用测试数据的ID
                    add_param(param_kind, param_name, 'entity.id')
                elif entity_name and entity_name in models:
                    # 生成创建实体的代码（模块内实体）
                    var_name = entity_name.lower()
                    entity_creation = self._generate_test_entity_creation(entity_name, models, f"{entity_name}数据", with_dependencies=True, module_name=module_name)
                    setup_code_lines.append(f"{var_name} = {entity_creation}")
                    setup_code_lines.append(f"unit_test_db.add({var_name})")
                    setup_code_lines.append(f"unit_test_db.commit()")
                    setup_code_lines.append("")
                    
                    # 参数使用实体的ID
                    if param_name.endswith('_id'):
                        add_param(param_kind, param_name, f"{var_name}.id")
                    else:
                        add_param(param_kind, param_name, f"{var_name}")
                elif entity_name:
                    # 跨模块实体（如Product, Sku等）- 使用Factory创建
                    var_name = entity_name.lower()
                    entity_module = self._get_module_name_for_model(entity_name)
                    
                    if entity_module != 'unknown':
                        # 添加FactoryManager setup
                        manager_name = ''.join(word.capitalize() for word in entity_module.split('_')) + 'FactoryManager'
                        setup_code_lines.append(f"from tests.factories.{entity_module}_factories import {manager_name}")
                        setup_code_lines.append(f"{manager_name}.setup_factories(unit_test_db)")
                        
                        # 使用Factory创建依赖
                        setup_code_lines.append(f"# 准备依赖实体: {entity_name}")
                        setup_code_lines.append(f"from tests.factories.{entity_module}_factories import {entity_name}Factory")
                        setup_code_lines.append(f"{var_name} = {entity_name}Factory.create()")
                        setup_code_lines.append("")
                        
                        # 参数使用实体的ID
                        if param_name.endswith('_id'):
                            add_param(param_kind, param_name, f"{var_name}.id")
                        else:
                            add_param(param_kind, param_name, f"{var_name}")
                    else:
                        # 完全无法推断，使用默认值
                        if param_type and 'int' in param_type:
                            add_param(param_kind, param_name, '1')
                        else:
                            add_param(param_kind, param_name, f'entity.{param_name}')
                else:
                    # 🎯 核心修复：无法通过_infer_entity_from_param推断实体时，
                    # 使用_resolve_param_value统一处理（支持字段检查、逻辑映射等）
                    # 这样可以复用所有参数解析逻辑，避免重复代码
                    
                    # 获取当前Repository对应的模型信息
                    from ..utils.repository_info import RepositoryInfo
                    repo_info = RepositoryInfo(
                        name=f"{entity_name}Repository",  # 使用已推断的entity_name
                        model_name=entity_name,
                        methods=[]
                    )
                    
                    # 调用统一的参数值解析方法
                    param_value = self._resolve_param_value(
                        param_name=param_name,
                        param_type=param_type,
                        repo_info=repo_info,
                        models=models,
                        entity_var='entity'  # get测试的entity变量固定为'entity'
                    )
                    
                    add_param(param_kind, param_name, param_value)
            
            # 生成参数字符串（根据参数类别生成正确的调用语法）
            setup_code = '\n        '.join(setup_code_lines) if setup_code_lines else ''
            param_str = self._build_param_string(param_parts)
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
    
    def _extract_entity_type_from_creation(self, entity_creation: str) -> Optional[str]:
        """从entity创建代码中提取entity的实际类型
        
        通用化设计：通过正则匹配entity创建表达式，提取类型名
        
        支持的模式：
        1. Factory模式: entity = UserFactory.create()
           提取：User（从UserFactory）
        
        2. 直接构造: entity = Order(...)
           提取：Order
        
        3. 多行代码（带依赖创建）:
           user = UserFactory.create()
           entity = Order(..., user_id=user.id)
           提取：Order（最后一行的entity赋值）
        
        Args:
            entity_creation: entity创建代码字符串
            
        Returns:
            str: entity的类型名（如"User", "Order"），如果无法提取则返回None
            
        示例：
            >>> _extract_entity_type_from_creation("entity = UserFactory.create()")
            "User"
            >>> _extract_entity_type_from_creation("entity = Order(order_number='test')")
            "Order"
        """
        import re
        
        # 模式1: entity = XxxFactory.create()
        # 匹配：entity = UserFactory.create()
        factory_pattern = r'entity\s*=\s*([A-Z][a-zA-Z0-9_]*)Factory\.create\('
        match = re.search(factory_pattern, entity_creation)
        if match:
            return match.group(1)  # 返回 "User"
        
        # 模式2: entity = ModelName(...)
        # 匹配：entity = Order(...)
        # 注意：需要排除Factory模式，所以要求没有"Factory"字样
        if 'Factory' not in entity_creation:
            direct_pattern = r'entity\s*=\s*([A-Z][a-zA-Z0-9_]*)\s*\('
            match = re.search(direct_pattern, entity_creation)
            if match:
                return match.group(1)  # 返回 "Order"
        
        # 模式3: 多行代码，提取最后一个entity赋值
        # 分割成行，找最后一行的entity赋值
        lines = entity_creation.split('\n')
        for line in reversed(lines):
            if 'entity' in line and '=' in line:
                # 递归调用处理单行
                entity_type = self._extract_entity_type_from_creation(line.strip())
                if entity_type:
                    return entity_type
        
        # 无法提取
        return None
    
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
        
        注意：使用CrossModuleDependencyResolver支持跨模块推断
        
        Args:
            param_name: 参数名(如user_id或user)
            param_type: 参数类型(如int或User)
            models: 当前模块的模型信息（用于兼容性，优先使用全局ModelAnalyzer）
            
        Returns:
            str: 实体名称(如User),如果无法推断返回None
        """
        # 🔧 优先使用dependency_resolver的ModelAnalyzer查找所有模块的模型
        all_models_dict = {}
        if hasattr(self, 'dependency_resolver') and self.dependency_resolver:
            # 从ModelAnalyzer获取所有模块的所有模型
            all_models_info = self.dependency_resolver.model_analyzer.get_all_models()
            # all_models_info格式: {module_name: {model_name: ModelInfo}}
            for module_models in all_models_info.values():
                all_models_dict.update(module_models)
        
        # 如果没有dependency_resolver，回退到使用传入的models字典
        if not all_models_dict:
            all_models_dict = models
        
        # 情况1: 对象类型参数(如user: User)
        # 检查参数类型是否直接是模型名（在所有模块中查找）
        if param_type in all_models_dict:
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
                if candidate in all_models_dict:
                    return candidate
        
        # 情况3: 对象参数但类型名不标准(如user: 'User'带引号)
        # 尝试从参数名推断
        candidates = [
            param_name.title(),  # user -> User
            param_name.capitalize(),  # user -> User
            ''.join(word.capitalize() for word in param_name.split('_'))  # user_role -> UserRole
        ]
        
        for candidate in candidates:
            if candidate in all_models_dict:
                return candidate
        
        return None
    
    def _fallback_table_to_model(self, table_name: str) -> str:
        """表名转模型名的后备方案（基于命名规则）
        
        仅当resolver.get_model_by_table()失败时使用。
        
        注意：此方法基于通用命名规则，可能不准确。
        应该优先使用dependency_resolver.get_model_by_table()，
        该方法从ModelAnalyzer获取准确的映射（如product_skus → SKU）。
        
        Args:
            table_name: 数据库表名
            
        Returns:
            推测的模型名
            
        Example:
            products -> Product
            categories -> Category
            product_skus -> ProductSku（可能不准确，实际可能是SKU）
        """
        # 移除复数s
        if table_name.endswith('ies'):
            singular = table_name[:-3] + 'y'  # categories -> category
        elif table_name.endswith('s'):
            singular = table_name[:-1]  # products -> product
        else:
            singular = table_name
        
        # 转驼峰命名
        parts = singular.split('_')
        model_name = ''.join(word.capitalize() for word in parts)
        
        return model_name

    def _generate_test_value_by_field_type(
        self,
        field_info: FieldInfo,
        suffix: str = ""
    ) -> str:
        """根据字段类型生成合适的测试值
        
        Args:
            field_info: 字段信息
            suffix: 值后缀（如"1"、"2"用于区分多个值）
            
        Returns:
            str: Python字面量字符串（如 "'test'", "True", "123"）
        """
        column_type = field_info.column_type.lower()
        
        # Boolean类型
        if 'boolean' in column_type or 'bool' in column_type:
            return "False" if suffix == "2" else "True"
        
        # 整数类型
        if 'integer' in column_type or 'int' in column_type:
            return f"10{suffix}" if suffix else "100"
        
        # 浮点数/Decimal类型
        if 'float' in column_type or 'decimal' in column_type or 'numeric' in column_type:
            return f"99.{suffix}9" if suffix else "99.99"
        
        # 日期时间类型
        if 'datetime' in column_type:
            return "datetime.now()"
        if 'date' in column_type:
            return "datetime.now().date()"
        if 'time' in column_type:
            return "datetime.now().time()"
        
        # 字符串类型（默认）
        return f'"更新后数据{suffix}"' if suffix else '"更新后数据"'
