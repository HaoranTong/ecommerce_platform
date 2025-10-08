"""
Repository分析工具 - 提取和分析Repository类信息

职责：
1. AST分析Repository类结构
2. 提取Repository方法签名和参数
3. 分类Repository方法类型（CRUD, 查询, 批量操作等）
4. 推断方法的查询参数和返回类型

版本: v1.0
创建时间: 2025-10-08
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
            
            # 查找所有Repository类
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
            docstring=ast.get_docstring(class_node)
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
        # 提取方法签名
        params: List[Tuple[str, str]] = []
        for arg in method_node.args.args:
            if arg.arg != 'self' and arg.arg != 'db':
                param_type = 'Any'
                if arg.annotation:
                    param_type = self._extract_type_annotation(arg.annotation)
                params.append((arg.arg, param_type))
        
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
        
        return RepositoryMethodInfo(
            name=method_node.name,
            method_type=method_type,
            parameters=params,
            return_type=return_type,
            is_static=False,  # Python Repository通常不使用静态方法
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
        
        # 批量操作（最高优先级）
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
        
        # 4. 特殊方法
        if name_lower.startswith('count'):
            return 'count'
        if name_lower.startswith('exists') or name_lower.startswith('has'):
            return 'exists'
        
        # 默认为自定义方法
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
