"""
Repository分析器 - 数据访问层智能分析与方法提取

该模块实现测试代码生成工具中的Repository层分析功能，通过AST静态分析提取Repository类的
完整方法信息，包括方法签名、参数类型、返回类型、操作类型等，为生成精准的Repository测试代码提供基础数据。

主要功能:
- Repository类识别: 自动识别模块中的所有Repository类
- 方法签名提取: 提取方法名称、参数列表、参数类型注解、返回类型注解
- 操作类型分类: 自动识别方法类型（CRUD操作、查询操作、批量操作、事务操作等）
- 参数推断: 根据方法名和参数名推断查询条件和过滤参数
- 依赖关系分析: 识别Repository之间的调用关系和依赖关系

技术栈:
- Python AST: 抽象语法树解析和分析
- typing: 类型注解解析和处理
- re: 正则表达式模式匹配

依赖关系:
- tools.test_generators.core.schema: RepositoryInfo/RepositoryMethodInfo数据模型
- app.modules.{module}.repository: 待分析的业务模块Repository定义
- tools.test_generators.generate_test_template: IntelligentTestGenerator主程序调用
- tools.test_generators.unit.repository_test_generator: RepositoryTestGenerator使用分析结果

使用示例:
    from pathlib import Path
    from tools.test_generators.utils.repository_analyzer import RepositoryAnalyzer
    
    # 初始化分析器
    analyzer = RepositoryAnalyzer(project_root=Path.cwd())
    
    # 分析user_auth模块的所有Repository
    repositories = analyzer.analyze_module_repositories("user_auth")
    
    # 遍历Repository信息
    for repo_name, repo_info in repositories.items():
        print(f"Repository: {repo_name}")
        print(f"  模型: {repo_info.model_name}")
        print(f"  方法数: {len(repo_info.methods)}")
        for method in repo_info.methods:
            print(f"    - {method.name}({', '.join(method.params)}): {method.operation_type}")

注意事项:
- 仅支持AST静态分析，无法获取运行时动态生成的方法
- 方法类型推断基于命名约定（get_*, create_*, update_*, delete_*等）
- 对于复杂的类型注解（如Union、Optional），会尽可能解析但可能不完整
- 分析结果的准确性依赖于代码的规范性和类型注解的完整性

Author: AI Assistant
Created: 2025-10-08
Modified: 2025-10-15
Version: 1.1.0

Changelog:
- v1.1.0 (2025-10-15): 
  * 🔧 修复：添加keyword-only参数支持 (Python 3.0+ PEP 3102)
  * ✅ 现在正确提取位置参数 + keyword-only参数
  * 📝 修复订单模块Repository测试失败问题
  * 🧪 添加单元测试覆盖
- v1.0.0 (2025-10-08): 初始版本
"""
import ast
import inspect
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.schema import RepositoryInfo, RepositoryMethodInfo


class RepositoryAnalyzer:
    """Repository层分析器"""
    
    def __init__(self, project_root: Path):
        """初始化分析器
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
        self.import_aliases: Dict[str, str] = {}  # {别名: 真实类名} 如 {"UserSession": "Session"}
    
    def analyze_module_repositories(self, module_name: str) -> Dict[str, RepositoryInfo]:
        """分析模块中的所有Repository类
        
        Args:
            module_name: 模块名称，如 'user_auth'
            
        Returns:
            Dict[str, RepositoryInfo]: Repository名称到Repository信息的映射
            
        Raises:
            FileNotFoundError: 当Repository文件不存在时
        """
        repository_file = self.project_root / f"app/modules/{module_name}/repository.py"
        
        if not repository_file.exists():
            print(f"⚠️ Repository文件不存在: {repository_file}")
            return {}
        
        print(f"🔍 分析Repository层: {repository_file}")
        
        repositories = {}
        
        try:
            # 读取并解析Repository文件
            with open(repository_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 🔍 步骤1：提取import语句中的别名映射
            self.import_aliases = self._extract_import_aliases(tree)
            if self.import_aliases:
                print(f"  📝 检测到import别名: {self.import_aliases}")
            
            # 🔍 步骤2：查找所有Repository类
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.endswith('Repository'):
                        repo_info = self._analyze_repository_class(node, module_name)
                        repositories[node.name] = repo_info
                        print(f"  ✅ 发现Repository: {node.name} ({len(repo_info.methods)}个方法)")
            
            print(f"✅ Repository分析完成，共 {len(repositories)} 个Repository类\n")
            return repositories
            
        except Exception as e:
            print(f"❌ Repository分析失败: {e}")
            return {}
    
    def _analyze_repository_class(self, class_node: ast.ClassDef, module_name: str) -> RepositoryInfo:
        """分析单个Repository类
        
        Args:
            class_node: AST类节点
            module_name: 模块名称
            
        Returns:
            RepositoryInfo: Repository信息
        """
        methods = []
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                # 跳过私有方法和特殊方法
                if item.name.startswith('_'):
                    continue
                
                method_info = self._analyze_repository_method(item, class_node.name, module_name)
                methods.append(method_info)
        
        return RepositoryInfo(
            name=class_node.name,
            model_name=self._infer_model_name(class_node.name),
            methods=methods,
            docstring=ast.get_docstring(class_node),
            import_aliases=self.import_aliases  # 传递别名映射
        )
    
    def _analyze_repository_method(
        self, 
        method_node: ast.FunctionDef, 
        repo_class_name: str,
        module_name: str
    ) -> RepositoryMethodInfo:
        """分析Repository方法
        
        Args:
            method_node: 方法AST节点
            repo_class_name: Repository类名
            module_name: 模块名称
            
        Returns:
            RepositoryMethodInfo: 方法信息
        """
        # 提取方法签名（支持位置参数 + keyword-only参数）
        params: List[Tuple[str, str, str]] = []
        
        # 1. 提取位置参数
        for arg in method_node.args.args:
            if arg.arg != 'self' and arg.arg != 'db':
                param_type = 'Any'
                if arg.annotation:
                    param_type = self._extract_type_annotation(arg.annotation)
                params.append((arg.arg, param_type, 'positional'))
        
        # 2. 提取keyword-only参数 (Python 3.0+ PEP 3102)
        for arg in method_node.args.kwonlyargs:
            param_type = 'Any'
            if arg.annotation:
                param_type = self._extract_type_annotation(arg.annotation)
            params.append((arg.arg, param_type, 'keyword-only'))
        
        # 推断返回类型
        return_type = 'Any'
        if method_node.returns:
            return_type = self._extract_type_annotation(method_node.returns)
        
        # 分类方法类型
        method_type = self._classify_repository_method(method_node.name, method_node, repo_class_name)
        
        # 检查是否需要事务
        has_transaction = method_type in ['create', 'update', 'delete', 'bulk']
        
        # 检查是否是软删除
        is_soft_delete = 'soft_delete' in method_node.name.lower() or (
            method_type == 'delete' and 'is_deleted' in ast.unparse(method_node) if hasattr(ast, 'unparse') else False
        )
        
        # 检查是否是专用更新方法
        is_specialized_update = (
            method_type == 'update' and 
            method_node.name not in ['update', 'update_by_id'] and
            'update_' in method_node.name
        )
        
        # 检测是否为静态方法
        is_static = any(
            isinstance(decorator, ast.Name) and decorator.id == 'staticmethod'
            for decorator in method_node.decorator_list
        )
        
        return RepositoryMethodInfo(
            name=method_node.name,
            method_type=method_type,
            parameters=params,
            return_type=return_type,
            is_static=is_static,
            docstring=ast.get_docstring(method_node),
            has_transaction=has_transaction,
            is_soft_delete=is_soft_delete,
            is_specialized_update=is_specialized_update
        )
    
    def _classify_repository_method(
        self, 
        method_name: str, 
        method_node: ast.FunctionDef,
        repo_class_name: str
    ) -> str:
        """分类Repository方法类型
        
        识别策略：
        1. 方法名模式匹配（create, get, update, delete等）
        2. 方法体SQL操作分析（add, query, update, delete）
        3. 返回类型推断（单个对象 vs 列表）
        
        Args:
            method_name: 方法名
            method_node: 方法AST节点
            repo_class_name: Repository类名
            
        Returns:
            str: 方法类型（create, read, update, delete, query, list, search, bulk, custom）
        """
        name_lower = method_name.lower()

        # 1. 基于方法名的精确匹配
        create_patterns = ['create', 'add', 'insert', 'register', 'save']
        read_patterns = ['get', 'find', 'fetch', 'retrieve', 'load']
        update_patterns = ['update', 'modify', 'edit', 'change', 'set']
        delete_patterns = ['delete', 'remove', 'drop', 'destroy']
        list_patterns = ['list', 'get_all', 'find_all', 'get_many']
        search_patterns = ['search', 'filter', 'query']
        bulk_patterns = ['bulk', 'batch', 'multi', 'mass']
        
        # 批量操作（高优先级）
        for pattern in bulk_patterns:
            if pattern in name_lower:
                return 'bulk'
        
        # CRUD操作
        for pattern in create_patterns:
            if name_lower.startswith(pattern) or name_lower.endswith(pattern):
                return 'create'
        
        for pattern in delete_patterns:
            if pattern in name_lower:
                return 'delete'
        
        # ⚠️ 排除SQL锁机制（for_update不是update操作）
        if 'for_update' not in name_lower:
            for pattern in update_patterns:
                if pattern in name_lower:
                    return 'update'
        
        # 查询操作（需要区分单个 vs 列表）
        for pattern in search_patterns:
            if pattern in name_lower:
                return 'search'
        
        for pattern in list_patterns:
            if pattern in name_lower:
                return 'list'
        
        for pattern in read_patterns:
            if pattern in name_lower:
                # 进一步判断：是否返回列表
                if 'all' in name_lower or 'many' in name_lower or 'list' in name_lower:
                    return 'list'
                return 'read'
        
        # 2. 基于方法体的SQL操作分析
        method_body_str = ast.unparse(method_node) if hasattr(ast, 'unparse') else ''
        
        if 'db.add' in method_body_str or 'session.add' in method_body_str:
            return 'create'
        elif 'db.delete' in method_body_str or 'session.delete' in method_body_str:
            return 'delete'
        elif '.update(' in method_body_str or 'db.commit' in method_body_str:
            # 有update操作或者只有commit（通常是更新）
            if 'query' not in method_body_str:
                return 'update'
        
        # 3. 查询操作默认分类
        if 'query' in method_body_str or 'filter' in method_body_str:
            if '.all()' in method_body_str or '.limit(' in method_body_str:
                return 'list'
            elif '.first()' in method_body_str or '.one()' in method_body_str:
                return 'read'
            return 'query'
        
        # 4. 默认为自定义方法
        return 'custom'
    
    def _extract_query_parameters(
        self, 
        method_node: ast.FunctionDef,
        params: List[Dict[str, Any]]
    ) -> List[str]:
        """提取查询方法的查询参数
        
        Args:
            method_node: 方法AST节点
            params: 方法参数列表
            
        Returns:
            List[str]: 查询参数列表
        """
        query_params = []
        
        # 1. 从方法参数推断
        for param in params:
            param_name = param['name']
            # 跳过明显的分页参数
            if param_name in ['skip', 'limit', 'offset', 'page', 'page_size']:
                continue
            # 其他参数视为查询参数
            query_params.append(param_name)
        
        # 2. 从方法体中的filter语句提取
        for node in ast.walk(method_node):
            if isinstance(node, ast.Attribute):
                if node.attr == 'filter':
                    # 尝试提取filter的参数
                    parent = node
                    if hasattr(parent, 'value'):
                        # 这里可以进一步分析filter的条件
                        pass
        
        return query_params
    
    def _infer_model_name(self, repo_class_name: str) -> str:
        """从Repository类名推断对应的Model名
        
        Args:
            repo_class_name: Repository类名，如 'UserRepository'
            
        Returns:
            str: Model名，如 'User'
        """
        # 移除'Repository'后缀
        if repo_class_name.endswith('Repository'):
            return repo_class_name[:-10]  # len('Repository') = 10
        return repo_class_name
    
    def _extract_import_aliases(self, tree: ast.AST) -> Dict[str, str]:
        """提取import语句中的别名映射
        
        解析形如 `from .models import Session as UserSession` 的语句，
        建立别名到真实类名的映射关系。
        
        Args:
            tree: AST树
            
        Returns:
            Dict[str, str]: {别名: 真实类名} 如 {"UserSession": "Session"}
            
        Example:
            >>> # 源码: from .models import Session as UserSession
            >>> aliases = self._extract_import_aliases(tree)
            >>> aliases
            {"UserSession": "Session"}
        """
        aliases = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # 检查是否从.models导入（可扩展到其他模块）
                if node.module and 'models' in node.module:
                    for alias in node.names:
                        if alias.asname:  # 有别名: import X as Y
                            # alias.name = 真实类名 (Session)
                            # alias.asname = 别名 (UserSession)
                            aliases[alias.asname] = alias.name
                            
        return aliases
    
    def _extract_type_annotation(self, annotation_node: ast.AST) -> str:
        """提取类型注解
        
        Args:
            annotation_node: 类型注解AST节点
            
        Returns:
            str: 类型字符串
        """
        try:
            if hasattr(ast, 'unparse'):
                return ast.unparse(annotation_node)
            elif isinstance(annotation_node, ast.Name):
                return annotation_node.id
            elif isinstance(annotation_node, ast.Subscript):
                # 处理List[User], Optional[str]等
                if isinstance(annotation_node.value, ast.Name):
                    return annotation_node.value.id
            return 'Any'
        except Exception:
            return 'Any'
