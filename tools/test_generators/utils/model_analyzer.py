"""
模型分析工具 - 提取和分析SQLAlchemy模型信息

职责：
1. AST静态分析模型结构
2. 运行时动态分析模型信息
3. 合并和验证模型数据
4. 提取字段、关系、约束等信息

版本: v1.0
创建时间: 2025-10-08
"""
import ast
import importlib.util
import inspect
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.schema import FieldInfo, RelationshipInfo, ModelInfo


class ModelAnalyzer:
    """SQLAlchemy模型分析器"""
    
    def __init__(self, project_root: Path):
        """初始化分析器
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
    
    def analyze_module_models(self, module_name: str) -> Dict[str, ModelInfo]:
        """分析模块的所有模型类
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict[模型名, ModelInfo]: 模型信息字典
        """
        print(f"🔍 开始智能分析模块: {module_name}")
        
        models_file = self.project_root / "app" / "modules" / module_name / "models.py"
        
        if not models_file.exists():
            print(f"⚠️ 模型文件不存在: {models_file}")
            return {}
        
        # 双重分析策略
        ast_models = self._analyze_with_ast(models_file)
        runtime_models = self._analyze_with_runtime(module_name)
        
        # 合并分析结果
        merged_models = self._merge_analysis_results(ast_models, runtime_models)
        
        print(f"✅ 分析完成，共识别 {len(merged_models)} 个数据模型")
        return merged_models
    
    def _analyze_with_ast(self, models_file: Path) -> Dict[str, Dict[str, Any]]:
        """使用AST静态分析模型定义
        
        Args:
            models_file: 模型文件路径
            
        Returns:
            Dict[模型名, 模型数据]: AST分析结果
        """
        models = {}
        
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(models_file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否继承自Base或包含__tablename__
                    is_model = any(
                        (isinstance(base, ast.Name) and base.id == 'Base')
                        or (isinstance(base, ast.Attribute) and base.attr == 'Base')
                        for base in node.bases
                    )
                    
                    has_tablename = any(
                        isinstance(item, ast.Assign) and
                        any(isinstance(t, ast.Name) and t.id == '__tablename__' for t in item.targets)
                        for item in node.body
                    )
                    
                    if is_model or has_tablename:
                        model_data = self._extract_ast_model_info(node)
                        models[node.name] = model_data
            
            print(f"📋 AST分析发现 {len(models)} 个模型类")
            return models
            
        except Exception as e:
            print(f"⚠️ AST分析失败: {e}")
            return {}
    
    def _extract_ast_model_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """从AST节点提取模型信息"""
        model_data = {
            'name': node.name,
            'tablename': None,
            'fields': [],
            'relationships': [],
            'mixins': [],
            'docstring': ast.get_docstring(node),
            'primary_keys': [],
            'unique_constraints': []
        }
        
        # 提取基类（mixins）
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id != 'Base':
                model_data['mixins'].append(base.id)
        
        # 分析类体
        for item in node.body:
            # 提取__tablename__
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '__tablename__':
                            if isinstance(item.value, ast.Constant):
                                model_data['tablename'] = item.value.value
                        
                        # 提取字段定义（Column）
                        elif self._is_column_definition(item.value):
                            field_info = self._analyze_ast_column(target.id, item.value)
                            if field_info:
                                model_data['fields'].append(field_info)
                        
                        # 提取关系定义（relationship）
                        elif self._is_relationship_definition(item.value):
                            rel_info = self._analyze_ast_relationship(target.id, item.value)
                            if rel_info:
                                model_data['relationships'].append(rel_info)
        
        return model_data
    
    def _is_column_definition(self, node: ast.AST) -> bool:
        """检查是否是Column定义"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'Column':
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'Column':
                return True
        return False
    
    def _is_relationship_definition(self, node: ast.AST) -> bool:
        """检查是否是relationship定义"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'relationship':
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'relationship':
                return True
        return False
    
    def _analyze_ast_column(self, field_name: str, node: ast.Call) -> Optional[Dict[str, Any]]:
        """分析Column定义"""
        if not isinstance(node, ast.Call):
            return None
        
        field_info = {
            'name': field_name,
            'column_type': 'Unknown',
            'python_type': 'Any',
            'nullable': True,
            'primary_key': False,
            'foreign_key': None,
            'unique': False,
            'default': None,
            'server_default': None,
            'constraints': []
        }
        
        # 提取类型（第一个参数）
        if node.args:
            type_node = node.args[0]
            if isinstance(type_node, ast.Call) and isinstance(type_node.func, ast.Name):
                field_info['column_type'] = type_node.func.id
            elif isinstance(type_node, ast.Name):
                field_info['column_type'] = type_node.id
        
        # 提取关键字参数
        for keyword in node.keywords:
            if keyword.arg == 'nullable' and isinstance(keyword.value, ast.Constant):
                field_info['nullable'] = keyword.value.value
            elif keyword.arg == 'primary_key' and isinstance(keyword.value, ast.Constant):
                field_info['primary_key'] = keyword.value.value
            elif keyword.arg == 'unique' and isinstance(keyword.value, ast.Constant):
                field_info['unique'] = keyword.value.value
            elif keyword.arg == 'default':
                field_info['default'] = ast.unparse(keyword.value) if hasattr(ast, 'unparse') else 'default'
        
        # 推断Python类型
        field_info['python_type'] = self._infer_python_type(field_info['column_type'])
        
        return field_info
    
    def _analyze_ast_relationship(self, rel_name: str, node: ast.Call) -> Optional[Dict[str, Any]]:
        """分析relationship定义"""
        if not isinstance(node, ast.Call):
            return None
        
        rel_info = {
            'name': rel_name,
            'related_model': 'Unknown',
            'relationship_type': 'one-to-many',
            'back_populates': None,
            'cascade': None,
            'foreign_keys': []
        }
        
        # 提取相关模型（第一个参数或字符串）
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant):
                rel_info['related_model'] = arg.value
            elif isinstance(arg, ast.Name):
                rel_info['related_model'] = arg.id
        
        # 提取关键字参数
        for keyword in node.keywords:
            if keyword.arg == 'back_populates' and isinstance(keyword.value, ast.Constant):
                rel_info['back_populates'] = keyword.value.value
            elif keyword.arg == 'cascade' and isinstance(keyword.value, ast.Constant):
                rel_info['cascade'] = keyword.value.value
        
        return rel_info
    
    def _infer_python_type(self, column_type: str) -> str:
        """根据SQLAlchemy类型推断Python类型"""
        type_mapping = {
            'Integer': 'int',
            'BigInteger': 'int',
            'SmallInteger': 'int',
            'String': 'str',
            'Text': 'str',
            'Unicode': 'str',
            'UnicodeText': 'str',
            'Boolean': 'bool',
            'Date': 'datetime.date',
            'DateTime': 'datetime.datetime',
            'Time': 'datetime.time',
            'Float': 'float',
            'Numeric': 'Decimal',
            'Decimal': 'Decimal',
            'JSON': 'dict',
            'JSONB': 'dict',
            'ARRAY': 'list',
            'Enum': 'str',
        }
        return type_mapping.get(column_type, 'Any')
    
    def _analyze_with_runtime(self, module_name: str) -> Dict[str, Dict[str, Any]]:
        """使用运行时反射分析模型
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict[模型名, 模型数据]: 运行时分析结果
        """
        models = {}
        
        try:
            # 动态导入模块
            module_path = self.project_root / "app" / "modules" / module_name / "models.py"
            spec = importlib.util.spec_from_file_location(f"app.modules.{module_name}.models", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找所有模型类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, '__tablename__'):
                        model_data = self._extract_runtime_model_info(obj)
                        models[name] = model_data
                
                print(f"🏃 运行时分析发现 {len(models)} 个模型类")
                
        except Exception as e:
            print(f"⚠️ 运行时分析失败: {e}")
        
        return models
    
    def _extract_runtime_model_info(self, model_class) -> Dict[str, Any]:
        """从运行时模型类提取信息"""
        model_data = {
            'name': model_class.__name__,
            'tablename': getattr(model_class, '__tablename__', None),
            'fields': [],
            'relationships': [],
            'mixins': [base.__name__ for base in model_class.__bases__ if base.__name__ != 'Base'],
            'docstring': model_class.__doc__,
            'primary_keys': [],
            'unique_constraints': []
        }
        
        # 提取字段信息
        if hasattr(model_class, '__table__'):
            table = model_class.__table__
            for column in table.columns:
                field_info = {
                    'name': column.name,
                    'column_type': str(column.type),
                    'python_type': column.type.python_type.__name__ if hasattr(column.type, 'python_type') else 'Any',
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'foreign_key': str(list(column.foreign_keys)[0].target_fullname) if column.foreign_keys else None,
                    'unique': column.unique,
                    'default': column.default,
                    'server_default': column.server_default,
                    'constraints': []
                }
                model_data['fields'].append(field_info)
                
                if column.primary_key:
                    model_data['primary_keys'].append(column.name)
        
        # 提取关系信息
        if hasattr(model_class, '__mapper__'):
            mapper = model_class.__mapper__
            for rel in mapper.relationships:
                rel_info = {
                    'name': rel.key,
                    'related_model': rel.mapper.class_.__name__,
                    'relationship_type': 'one-to-many' if rel.uselist else 'many-to-one',
                    'back_populates': rel.back_populates,
                    'cascade': str(rel.cascade) if rel.cascade else None,
                    'foreign_keys': [str(fk.parent) for fk in rel.local_columns] if hasattr(rel, 'local_columns') else []
                }
                model_data['relationships'].append(rel_info)
        
        return model_data
    
    def _merge_analysis_results(
        self, ast_models: Dict[str, Dict], runtime_models: Dict[str, Dict]
    ) -> Dict[str, ModelInfo]:
        """合并AST和运行时分析结果"""
        merged = {}
        
        # 获取所有模型名
        all_models = set(ast_models.keys()) | set(runtime_models.keys())
        
        for model_name in all_models:
            ast_data = ast_models.get(model_name, {})
            runtime_data = runtime_models.get(model_name, {})
            
            # 优先使用运行时数据，AST数据作为补充
            fields = runtime_data.get('fields', ast_data.get('fields', []))
            relationships = runtime_data.get('relationships', ast_data.get('relationships', []))
            
            # 转换为FieldInfo和RelationshipInfo对象
            field_infos = []
            for field in fields:
                if isinstance(field, dict):
                    field_infos.append(FieldInfo(
                        name=field['name'],
                        column_type=field['column_type'],
                        python_type=field['python_type'],
                        nullable=field['nullable'],
                        primary_key=field['primary_key'],
                        foreign_key=field['foreign_key'],
                        unique=field['unique'],
                        default=field['default'],
                        server_default=field.get('server_default'),
                        constraints=field.get('constraints', [])
                    ))
            
            rel_infos = []
            for rel in relationships:
                if isinstance(rel, dict):
                    rel_infos.append(RelationshipInfo(
                        name=rel['name'],
                        related_model=rel['related_model'],
                        relationship_type=rel['relationship_type'],
                        back_populates=rel.get('back_populates'),
                        cascade=rel.get('cascade'),
                        foreign_keys=rel.get('foreign_keys', [])
                    ))
            
            model_info = ModelInfo(
                name=model_name,
                tablename=runtime_data.get('tablename') or ast_data.get('tablename') or model_name.lower(),
                fields=field_infos,
                relationships=rel_infos,
                mixins=runtime_data.get('mixins', ast_data.get('mixins', [])),
                docstring=runtime_data.get('docstring') or ast_data.get('docstring'),
                primary_keys=runtime_data.get('primary_keys', ast_data.get('primary_keys', [])),
                unique_constraints=runtime_data.get('unique_constraints', ast_data.get('unique_constraints', []))
            )
            
            merged[model_name] = model_info
            
            # 打印合并结果
            field_count = len(field_infos)
            rel_count = len(rel_infos)
            print(f"🔗 合并模型: {model_name} ({field_count}字段, {rel_count}关系)")
        
        return merged
