"""
基础测试生成器

功能: 为所有专业测试生成器提供共享的基础功能和工具类
使用方法: 作为抽象基类被各专业生成器继承，不直接使用
使用场景: FastAPI模块路由分析、SQLAlchemy模型信息提取、业务域名识别

核心功能:
1. 路由文件AST解析 - 支持async和sync函数识别
2. 模型信息提取 - 解析数据库表结构和字段信息
3. 业务域名推断 - 基于模块名称推断业务领域
4. 共享工具方法 - 提供文件操作、路径处理等通用功能

技术特点:
- 支持FastAPI AsyncFunctionDef路由解析
- 智能识别SQLAlchemy模型关系
- 标准化测试文件路径生成

版本: v1.0.0
作者: AI Assistant
创建时间: 2025-10-01
"""

import ast
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FieldInfo:
    """数据模型字段信息"""
    name: str
    column_type: str
    python_type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str]
    unique: bool
    default: Any
    constraints: List[str]


@dataclass
class RelationshipInfo:
    """数据模型关系信息"""
    name: str
    related_model: str
    relationship_type: str
    back_populates: Optional[str]
    cascade: Optional[str]
    foreign_keys: List[str]


@dataclass
class ModelInfo:
    """完整的数据模型信息"""
    name: str
    tablename: str
    fields: List[FieldInfo]
    relationships: List[RelationshipInfo]
    mixins: List[str]
    docstring: Optional[str]
    primary_keys: List[str]
    unique_constraints: List[List[str]]


@dataclass
class RouterInfo:
    """路由信息"""
    path: str
    method: str
    function_name: str
    parameters: List[Dict[str, Any]]
    response_model: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    tags: List[str]
    auth_required: bool


class BaseTestGenerator(ABC):
    """测试生成器基类"""
    
    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.config = config
        
    @abstractmethod
    def generate_tests(self, module_name: str, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """生成测试代码 - 子类必须实现此方法"""
        pass
    
    def analyze_router_file(self, module_name: str) -> List[RouterInfo]:
        """分析模块的router.py文件，提取API端点信息"""
        router_path = self.project_root / f"app/modules/{module_name}/router.py"
        
        if not router_path.exists():
            print(f"⚠️ 路由文件不存在: {router_path}")
            return []
        
        try:
            with open(router_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用AST分析路由定义
            tree = ast.parse(content)
            routes = []
            
            for node in ast.walk(tree):
                # 检查同步和异步函数定义
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 查找带有@router装饰器的函数
                    route_info = self._extract_route_info(node, content)
                    if route_info:
                        routes.append(route_info)
            
            print(f"📡 分析到 {len(routes)} 个API端点")
            return routes
            
        except Exception as e:
            print(f"❌ 分析路由文件失败: {e}")
            return []
    
    def _extract_route_info(self, func_node: ast.FunctionDef, content: str) -> Optional[RouterInfo]:
        """从函数节点提取路由信息"""
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                # @router.post, @router.get等形式
                if (isinstance(decorator.value, ast.Name) and 
                    decorator.value.id == 'router' and
                    decorator.attr in ['get', 'post', 'put', 'delete', 'patch']):
                    
                    return self._parse_route_decorator(decorator, func_node, content)
            
            elif isinstance(decorator, ast.Call):
                # @router.post("/path")形式
                if (isinstance(decorator.func, ast.Attribute) and
                    isinstance(decorator.func.value, ast.Name) and
                    decorator.func.value.id == 'router'):
                    
                    return self._parse_route_decorator_with_args(decorator, func_node, content)
        
        return None
    
    def _parse_route_decorator(self, decorator: ast.Attribute, func_node: ast.FunctionDef, content: str) -> RouterInfo:
        """解析简单的路由装饰器"""
        return RouterInfo(
            path=f"/{func_node.name}",  # 默认路径
            method=decorator.attr.upper(),
            function_name=func_node.name,
            parameters=self._extract_function_parameters(func_node),
            response_model=None,
            summary=None,
            description=ast.get_docstring(func_node),
            tags=[],
            auth_required=self._check_auth_required(func_node)
        )
    
    def _parse_route_decorator_with_args(self, decorator: ast.Call, func_node: ast.FunctionDef, content: str) -> RouterInfo:
        """解析带参数的路由装饰器"""
        path = "/"
        response_model = None
        summary = None
        tags = []
        
        # 解析路径参数
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            path = decorator.args[0].value
        
        # 解析关键字参数
        for keyword in decorator.keywords:
            if keyword.arg == "response_model" and isinstance(keyword.value, ast.Name):
                response_model = keyword.value.id
            elif keyword.arg == "summary" and isinstance(keyword.value, ast.Constant):
                summary = keyword.value.value
            elif keyword.arg == "tags" and isinstance(keyword.value, ast.List):
                tags = [item.value for item in keyword.value.elts if isinstance(item, ast.Constant)]
        
        return RouterInfo(
            path=path,
            method=decorator.func.attr.upper(),
            function_name=func_node.name,
            parameters=self._extract_function_parameters(func_node),
            response_model=response_model,
            summary=summary,
            description=ast.get_docstring(func_node),
            tags=tags,
            auth_required=self._check_auth_required(func_node)
        )
    
    def _extract_function_parameters(self, func_node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """提取函数参数信息"""
        parameters = []
        
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": None,
                "default": None,
                "annotation": None
            }
            
            # 提取类型注解
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    param_info["type"] = arg.annotation.id
                elif isinstance(arg.annotation, ast.Attribute):
                    param_info["type"] = f"{arg.annotation.value.id}.{arg.annotation.attr}"
            
            parameters.append(param_info)
        
        return parameters
    
    def _check_auth_required(self, func_node: ast.FunctionDef) -> bool:
        """检查函数是否需要认证"""
        # 检查参数中是否有current_user或类似的依赖注入
        for arg in func_node.args.args:
            if 'user' in arg.arg.lower() or 'auth' in arg.arg.lower():
                return True
        
        # 检查依赖注入装饰器
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                if (isinstance(decorator.func, ast.Name) and 
                    'auth' in decorator.func.id.lower()):
                    return True
        
        return False
    
    def get_module_business_domain(self, module_name: str) -> str:
        """获取模块的业务领域"""
        domain_mapping = {
            'user_auth': '用户认证',
            'product_catalog': '商品管理', 
            'shopping_cart': '购物车',
            'order_management': '订单管理',
            'payment_service': '支付服务',
            'inventory_management': '库存管理',
            'member_system': '会员系统',
            'logistics_management': '物流管理',
            'notification_service': '通知服务',
            'quality_control': '质量控制',
            'batch_traceability': '批次溯源',
            'customer_service_system': '客服系统',
            'data_analytics_platform': '数据分析',
            'distributor_management': '经销商管理',
            'marketing_campaigns': '营销活动',
            'recommendation_system': '推荐系统',
            'risk_control_system': '风控系统',
            'social_features': '社交功能',
            'supplier_management': '供应商管理'
        }
        return domain_mapping.get(module_name, module_name.replace('_', ' ').title())
    
    def generate_test_file_header(self, module_name: str, test_type: str, description: str) -> str:
        """生成测试文件头部注释"""
        business_domain = self.get_module_business_domain(module_name)
        
        return f'''"""
{business_domain}模块{test_type}测试

{description}

依赖标准:
- docs/standards/testing-standards.md - 五层测试架构标准
- docs/standards/api-standards.md - API设计规范
- 遵循pytest-mock强制使用要求

创建时间: 2025-10-01
工具版本: 智能测试生成器 v2.0
"""
'''
    
    def analyze_pydantic_schema(self, module_name: str, route: RouterInfo) -> Dict[str, Any]:
        """分析路由的Pydantic Schema，生成正确的测试数据"""
        try:
            # 添加警告过滤器，避免SQLAlchemy表重定义警告
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning, message='.*Table.*already defined.*')
            warnings.filterwarnings('ignore', message='.*declarative base.*')
            
            # 直接导入schemas.py文件，避免通过__init__.py导入models
            import importlib.util
            import sys
            from pathlib import Path
            
            schema_file_path = self.project_root / f"app/modules/{module_name}/schemas.py"
            if not schema_file_path.exists():
                print(f"⚠️ Schema文件不存在: {schema_file_path}")
                return self._generate_fallback_data(route)
            
            # 使用spec加载，避免导入__init__.py
            spec = importlib.util.spec_from_file_location(f"{module_name}_schemas", schema_file_path)
            if spec is None or spec.loader is None:
                print(f"⚠️ 无法创建Schema模块spec")
                return self._generate_fallback_data(route)
            
            schema_module = importlib.util.module_from_spec(spec)
            
            # 临时添加到sys.modules，避免重复导入
            temp_module_name = f"temp_{module_name}_schemas"
            sys.modules[temp_module_name] = schema_module
            
            try:
                spec.loader.exec_module(schema_module)
                
                # 根据路由功能推断Schema类名
                schema_class_name = self._infer_schema_class(route)
                if not schema_class_name:
                    print(f"⚠️ 无法推断Schema类名，使用fallback数据")
                    return self._generate_fallback_data(route)
                
                # 获取Schema类
                schema_class = getattr(schema_module, schema_class_name, None)
                if not schema_class:
                    print(f"⚠️ Schema类 {schema_class_name} 不存在，使用fallback数据")
                    return self._generate_fallback_data(route)
                
                # 分析Schema字段
                schema_data = self._extract_schema_fields(schema_class)
                print(f"✅ Schema分析成功: {schema_class_name} -> {len(schema_data)} 个字段")
                return schema_data
                
            finally:
                # 清理临时模块
                if temp_module_name in sys.modules:
                    del sys.modules[temp_module_name]
            
        except Exception as e:
            print(f"⚠️ Schema分析失败: {e}, 使用fallback数据")
            import traceback
            print(f"📋 详细错误: {traceback.format_exc()}")
            return self._generate_fallback_data(route)
    
    def _infer_schema_class(self, route: RouterInfo) -> Optional[str]:
        """根据路由功能推断Schema类名"""
        function_name = route.function_name.lower()
        
        if 'register' in function_name:
            return 'UserRegister'
        elif 'login' in function_name:
            return 'UserLogin'
        elif 'update' in function_name:
            return 'UserUpdate'
        elif 'create' in function_name:
            # 根据模块推断创建Schema
            return self._infer_create_schema(route)
        
        return None
    
    def _infer_create_schema(self, route: RouterInfo) -> str:
        """推断创建操作的Schema名称"""
        # 基于路径推断资源类型
        path_parts = route.path.strip('/').split('/')
        if len(path_parts) >= 2:
            resource = path_parts[-1].rstrip('s')  # 去掉复数s
            return f"{resource.title()}Create"
        return "CreateSchema"
    
    def _extract_schema_fields(self, schema_class) -> Dict[str, Any]:
        """提取Pydantic Schema的字段信息"""
        try:
            # 获取模型字段
            model_fields = schema_class.model_fields if hasattr(schema_class, 'model_fields') else {}
            
            test_data = {}
            for field_name, field_info in model_fields.items():
                test_data[field_name] = self._generate_field_value(field_name, field_info)
            
            return test_data
            
        except Exception as e:
            print(f"⚠️ 字段提取失败: {e}")
            return {}
    
    def _generate_field_value(self, field_name: str, field_info) -> Any:
        """根据字段信息生成测试值"""
        # 根据字段名称生成合适的测试值
        field_name_lower = field_name.lower()
        
        if 'email' in field_name_lower:
            return "test@example.com"
        elif 'username' in field_name_lower:
            return "test_user"
        elif 'password' in field_name_lower:
            return "test_password123"
        elif 'phone' in field_name_lower:
            return "13800138000"
        elif 'verification_code' in field_name_lower or 'code' in field_name_lower:
            return "123456"
        elif 'name' in field_name_lower:
            return "测试用户"
        elif field_name_lower in ['age', 'count', 'quantity']:
            return 25
        elif field_name_lower in ['price', 'amount']:
            return 99.99
        elif field_name_lower in ['is_active', 'enabled', 'status']:
            return True
        else:
            # 根据字段类型推断
            return self._generate_by_type(field_info)
    
    def _generate_by_type(self, field_info) -> Any:
        """根据字段类型生成默认值"""
        try:
            # 尝试从field_info获取类型信息
            if hasattr(field_info, 'annotation'):
                field_type = field_info.annotation
                
                # 处理常见的类型
                if field_type == str:
                    return "test_string"
                elif field_type == int:
                    return 123
                elif field_type == float:
                    return 99.99
                elif field_type == bool:
                    return True
                elif hasattr(field_type, '__name__'):
                    # 处理其他类型
                    type_name = field_type.__name__.lower()
                    if 'datetime' in type_name:
                        return "2024-01-01T00:00:00"
                    elif 'date' in type_name:
                        return "2024-01-01"
                    elif 'uuid' in type_name:
                        return "12345678-1234-1234-1234-123456789012"
            
            # 默认字符串值
            return "test_value"
            
        except Exception:
            return "test_value"
    
    def _generate_fallback_data(self, route: RouterInfo) -> Dict[str, Any]:
        """生成fallback测试数据"""
        function_name = route.function_name.lower()
        
        if 'register' in function_name:
            return {
                "username": "test_user",
                "email": "test@example.com", 
                "password": "test_password123",
                "phone": "13800138000",
                "verification_code": "123456",
                "real_name": "测试用户"
            }
        elif 'login' in function_name:
            return {
                "username": "test_user",
                "password": "test_password123"
            }
        else:
            return {"data": "test_value"}