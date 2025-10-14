"""
基础测试生成器

所有测试生成器通用格式化错误预防指南

这些规则适用于所有继承此基类的测试生成器:

1. Python字符串模板中的变量引用:
   错误模式: 双重花括号导致字面量输出
   正确模式: 直接变量引用，简单变量替换

2. f-string模板生成规则:
   - 当生成的代码本身需要使用f-string时，使用单层花括号
   - 避免在返回的字符串模板中使用双花括号转义
   - 确保变量在作用域内可用

3. **代码模板调试技巧**:
   - 生成后立即检查输出代码的语法正确性
   - 使用临时打印验证变量替换是否正确
   - 避免过度复杂的嵌套字符串模板

4. **常见错误位置**:
   - JSON数据模板生成
   - API端点路径拼接
   - 测试方法名生成
   - HTTP请求参数模板

记住: 生成的代码应该是有效的Python代码，变量应该被正确替换而不是显示为字面量。

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
更新时间: 2025-10-06 (添加通用模板格式化错误预防指南)
"""

import ast
import os
import re
import secrets
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from faker import Faker


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
    dependencies: List[Dict[str, Any]] = None  # 依赖注入信息
    require_admin: bool = False  # 是否需要管理员权限
    
    def __post_init__(self):
        """初始化默认值"""
        if self.dependencies is None:
            self.dependencies = []


class BaseTestGenerator(ABC):
    """测试生成器基类"""
    
    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = project_root
        self.config = config
        # Schema分析缓存 - 避免重复打印
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        # 路由分析缓存 - 避免重复分析和打印
        self._router_cache: Dict[str, List[RouterInfo]] = {}
        
    @abstractmethod
    def generate_tests(self, module_name: str, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """生成测试代码 - 子类必须实现此方法"""
        pass
    
    def analyze_router_file(self, module_name: str) -> List[RouterInfo]:
        """分析模块的router.py文件，提取API端点信息（带缓存机制避免重复分析）"""
        # 检查缓存
        if module_name in self._router_cache:
            return self._router_cache[module_name]
        
        router_path = self.project_root / f"app/modules/{module_name}/router.py"
        
        if not router_path.exists():
            print(f"⚠️ 路由文件不存在: {router_path}")
            self._router_cache[module_name] = []
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
                    try:
                        route_info = self._extract_route_info(node, content)
                        if route_info:
                            routes.append(route_info)
                    except Exception as e:
                        print(f"❌ 提取路由信息失败 [{node.name}]: {e}")
                        traceback.print_exc()
                        continue
            
            print(f"📡 分析到 {len(routes)} 个API端点")
            # 缓存结果
            self._router_cache[module_name] = routes
            return routes
            
        except Exception as e:
            print(f"❌ 分析路由文件失败: {e}")
            traceback.print_exc()
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
        dependencies, require_admin = self._extract_function_dependencies(func_node)
        
        return RouterInfo(
            path=f"/{func_node.name}",  # 默认路径
            method=decorator.attr.upper(),
            function_name=func_node.name,
            parameters=self._extract_function_parameters(func_node),
            response_model=None,
            summary=None,
            description=ast.get_docstring(func_node),
            tags=[],
            auth_required=self._check_auth_required(func_node),
            dependencies=dependencies,
            require_admin=require_admin
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
        
        # 提取依赖信息
        dependencies, require_admin = self._extract_function_dependencies(func_node)
        
        return RouterInfo(
            path=path,
            method=decorator.func.attr.upper(),
            function_name=func_node.name,
            parameters=self._extract_function_parameters(func_node),
            response_model=response_model,
            summary=summary,
            description=ast.get_docstring(func_node),
            tags=tags,
            auth_required=self._check_auth_required(func_node),
            dependencies=dependencies,
            require_admin=require_admin
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
    
    def _extract_function_dependencies(self, func_node: ast.FunctionDef) -> tuple[List[Dict[str, Any]], bool]:
        """
        提取函数的依赖注入信息
        
        Returns:
            tuple: (dependencies列表, 是否需要管理员权限)
        """
        dependencies = []
        require_admin = False
        
        for arg in func_node.args.args:
            # 检查参数名是否指示管理员权限
            if arg.arg in ['admin_user', 'admin', 'current_admin']:
                require_admin = True
            
            # 检查类型注解中的 Depends() 表达式
            if arg.annotation:
                dep_info = self._analyze_depends_annotation(arg, arg.annotation)
                if dep_info:
                    dependencies.append(dep_info)
                    # 检查依赖是否需要管理员权限
                    if dep_info.get('is_admin_required', False):
                        require_admin = True
        
        return dependencies, require_admin
    
    def _analyze_depends_annotation(self, arg, annotation) -> Optional[Dict[str, Any]]:
        """分析 Depends() 注解"""
        # 检查是否是 Depends() 调用
        if isinstance(annotation, ast.Call):
            if isinstance(annotation.func, ast.Name) and annotation.func.id == 'Depends':
                # 提取 Depends 的参数
                if annotation.args:
                    dep_func = annotation.args[0]
                    dep_name = self._get_dependency_name(dep_func)
                    is_admin = self._is_admin_dependency(dep_func, dep_name)
                    
                    return {
                        'param_name': arg.arg,
                        'dependency_name': dep_name,
                        'is_admin_required': is_admin
                    }
        
        return None
    
    def _get_dependency_name(self, dep_expr) -> str:
        """获取依赖函数名"""
        if isinstance(dep_expr, ast.Call):
            if isinstance(dep_expr.func, ast.Name):
                return dep_expr.func.id
        elif isinstance(dep_expr, ast.Name):
            return dep_expr.id
        elif isinstance(dep_expr, ast.Attribute):
            return dep_expr.attr
        return "unknown"
    
    def _is_admin_dependency(self, dep_expr, dep_name: str) -> bool:
        """检查依赖是否需要管理员权限"""
        # 检查依赖名称中是否包含 admin
        admin_keywords = ['admin', 'require_admin', 'admin_only', 'admin_required']
        return any(keyword in dep_name.lower() for keyword in admin_keywords)
    
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
        """分析路由的Pydantic Schema，生成正确的测试数据（带缓存机制避免重复打印）"""
        # 生成缓存key
        cache_key = f"{module_name}:{route.function_name}:{route.method}"
        
        # 检查缓存
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        # 优先尝试从路由参数中提取Schema类型（避免推断错误）
        schema_from_params = self._extract_schema_from_parameters(route)
        if schema_from_params:
            print(f"✅ 从参数提取Schema: {schema_from_params}")
            # 继续使用这个Schema名称进行后续分析
        
        try:
            # 添加警告过滤器，避免SQLAlchemy表重定义警告
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning, message='.*Table.*already defined.*')
            warnings.filterwarnings('ignore', message='.*declarative base.*')
            
            # 直接导入schemas.py文件，避免通过__init__.py导入models
            import importlib.util
            import sys
            
            schema_file_path = self.project_root / f"app/modules/{module_name}/schemas.py"
            if not schema_file_path.exists():
                print(f"⚠️ Schema文件不存在: {schema_file_path}")
                result = self._generate_fallback_data(route)
                self._schema_cache[cache_key] = result
                return result
            
            # 使用spec加载，避免导入__init__.py
            spec = importlib.util.spec_from_file_location(f"{module_name}_schemas", schema_file_path)
            if spec is None or spec.loader is None:
                print(f"⚠️ 无法创建Schema模块spec")
                result = self._generate_fallback_data(route)
                self._schema_cache[cache_key] = result
                return result
            
            schema_module = importlib.util.module_from_spec(spec)
            
            # 临时添加到sys.modules，避免重复导入
            temp_module_name = f"temp_{module_name}_schemas"
            sys.modules[temp_module_name] = schema_module
            
            try:
                spec.loader.exec_module(schema_module)
                
                # 优先使用从参数提取的Schema名称，其次才推断
                schema_class_name = schema_from_params or self._infer_schema_class(route)
                if not schema_class_name:
                    # 检查是否是正常不需要Schema的情况
                    if self._should_have_schema(route):
                        print(f"⚠️ 无法推断Schema类名，使用fallback数据")
                    else:
                        print(f"📋 {route.function_name} 无需Schema (GET请求或无参数POST)")
                    result = self._generate_fallback_data(route)
                    self._schema_cache[cache_key] = result
                    return result
                
                # 获取Schema类
                schema_class = getattr(schema_module, schema_class_name, None)
                if not schema_class:
                    print(f"⚠️ Schema类 {schema_class_name} 不存在，使用fallback数据")
                    result = self._generate_fallback_data(route)
                    self._schema_cache[cache_key] = result
                    return result
                
                # 分析Schema字段
                schema_data = self._extract_schema_fields(schema_class)
                print(f"✅ Schema分析成功: {schema_class_name} -> {len(schema_data)} 个字段")
                
                # 缓存结果
                self._schema_cache[cache_key] = schema_data
                return schema_data
                
            finally:
                # 清理临时模块
                if temp_module_name in sys.modules:
                    del sys.modules[temp_module_name]
            
        except Exception as e:
            print(f"⚠️ Schema分析失败: {e}, 使用fallback数据")
            print(f"📋 详细错误: {traceback.format_exc()}")
            result = self._generate_fallback_data(route)
            self._schema_cache[cache_key] = result
            return result
    
    def _should_have_schema(self, route: RouterInfo) -> bool:
        """判断路由是否应该有Schema"""
        # GET请求通常不需要请求体Schema
        if route.method == 'GET':
            return False
        
        # 某些特殊的POST请求不需要Schema
        function_name = route.function_name.lower()
        no_schema_functions = ['logout', 'health_check', 'ping']
        if any(func in function_name for func in no_schema_functions):
            return False
        
        # 其他POST、PUT、PATCH请求通常需要Schema
        return route.method in ['POST', 'PUT', 'PATCH']
    
    def _extract_schema_from_parameters(self, route: RouterInfo) -> Optional[str]:
        """从路由参数中提取Schema类型信息
        
        优先从路由定义的参数类型中获取Schema类名，避免使用硬编码推断。
        
        Args:
            route: 路由信息对象
            
        Returns:
            Schema类名（如果找到），否则返回None
        """
        if not route.parameters:
            return None
        
        # 遍历参数列表，查找Pydantic Schema类型
        for param in route.parameters:
            # 参数类型通常在 'type' 字段中
            param_type = param.get('type')
            if not param_type:
                continue
            
            # 提取类名（可能是字符串或类型对象）
            schema_name = None
            if isinstance(param_type, str):
                # 如果是字符串形式，提取最后一个点号后的类名
                schema_name = param_type.split('.')[-1] if '.' in param_type else param_type
            elif hasattr(param_type, '__name__'):
                # 如果是类型对象，直接获取名称
                schema_name = param_type.__name__
            
            # 验证是否是有效的Schema类名（通常以Create/Update/Base等结尾）
            if schema_name and any(suffix in schema_name for suffix in 
                ['Create', 'Update', 'Base', 'Request', 'Send', 'Reset', 'Verify', 'Refresh']):
                return schema_name
        
        return None
    
    def _infer_schema_class(self, route: RouterInfo) -> Optional[str]:
        """根据路由功能推断Schema类名 - 动态推断，无硬编码"""
        function_name = route.function_name.lower()
        
        # 无需Schema的端点
        if any(word in function_name for word in ['logout', 'get_current', 'get_user', 'list']):
            return None
        
        # 创建操作
        if 'create' in function_name:
            return self._infer_create_schema(route)
        
        # 更新操作
        elif 'update' in function_name:
            return self._infer_update_schema(route)
        
        # 登录相关 - 基于路径和功能名动态推断
        elif 'login' in function_name:
            if 'phone' in function_name:
                return 'PhoneLogin'
            return 'UserLogin'
        
        # 注册相关
        elif 'register' in function_name:
            return 'UserRegister'
            
        # Token相关
        elif 'refresh' in function_name and 'token' in function_name:
            return 'TokenRefresh'
        
        # 密码相关
        elif 'reset' in function_name:
            if 'confirm' in function_name:
                return 'PasswordResetConfirm'
            elif 'request' in function_name:
                return 'PasswordResetRequest'
        elif 'change' in function_name and 'password' in function_name:
            return 'UserChangePassword'
        
        # 验证码相关
        elif 'verification_code' in function_name or 'send_verification' in function_name:
            return 'SendVerificationCode'
        
        # 基于路径的通用推断
        return self._infer_schema_from_path(route)
    
    def _infer_update_schema(self, route: RouterInfo) -> str:
        """推断更新操作的Schema名称"""
        path_parts = route.path.strip('/').split('/')
        if len(path_parts) >= 2:
            resource = path_parts[-1] if '{' not in path_parts[-1] else path_parts[-2]
            # 智能单数化
            resource = self._singularize(resource)
            # 处理常见缩写词
            resource = self._handle_abbreviations(resource)
            return f"{resource}Update"
        return "UpdateSchema"
    
    def _infer_schema_from_path(self, route: RouterInfo) -> Optional[str]:
        """基于路径推断Schema类名"""
        path_parts = route.path.strip('/').split('/')
        if len(path_parts) >= 2:
            resource = path_parts[-1] if '{' not in path_parts[-1] else path_parts[-2]
            resource = self._singularize(resource)
            resource = self._handle_abbreviations(resource)
            # 基于HTTP方法推断操作类型
            if route.method.upper() == 'POST':
                return f"{resource}Create"
            elif route.method.upper() in ['PUT', 'PATCH']:
                return f"{resource}Update"
        return None
    
    def _singularize(self, word: str) -> str:
        """智能单数化"""
        if word.endswith('ies'):
            return word[:-3] + 'y'  # categories -> category
        elif word.endswith('es') and len(word) > 3:
            return word[:-2]  # boxes -> box, wishes -> wish
        elif word.endswith('s') and not word.endswith('ss'):
            return word[:-1]  # products -> product, users -> user
        return word
    
    def _handle_abbreviations(self, word: str) -> str:
        """处理常见缩写词的大小写"""
        # 常见的缩写词映射
        abbreviations = {
            'sku': 'SKU',
            'api': 'API',
            'url': 'URL',
            'id': 'ID',
            'seo': 'SEO',
            'uuid': 'UUID',
            'xml': 'XML',
            'json': 'JSON',
            'http': 'HTTP',
            'oauth': 'OAuth',
            'jwt': 'JWT',
            'sms': 'SMS',
            'qr': 'QR',
            'pdf': 'PDF',
        }
        
        lower_word = word.lower()
        if lower_word in abbreviations:
            return abbreviations[lower_word]
        
        # 如果不是缩写词，使用普通的首字母大写
        return word.title()
    
    def _infer_create_schema(self, route: RouterInfo) -> str:
        """推断创建操作的Schema名称"""
        # 基于路径推断资源类型
        path_parts = route.path.strip('/').split('/')
        if len(path_parts) >= 1:
            resource = path_parts[-1]
            # 智能单数化：处理常见复数形式
            resource = self._singularize(resource)
            return f"{resource.title()}Create"
        return "CreateSchema"
    
    def _extract_schema_fields(self, schema_class) -> Dict[str, Dict[str, Any]]:
        """提取Pydantic Schema的字段信息（返回类型元信息而非默认值）"""
        try:
            # 获取模型字段
            model_fields = schema_class.model_fields if hasattr(schema_class, 'model_fields') else {}
            
            fields_info = {}
            for field_name, field_info in model_fields.items():
                # 提取字段的类型信息而非生成测试值
                field_data = {
                    'type': field_info.annotation,  # 类型注解 (如 Optional[int], str, bool)
                    'default': field_info.default if hasattr(field_info, 'default') else None,
                    'required': field_info.is_required() if hasattr(field_info, 'is_required') else True,
                    'field_name': field_name
                }
                
                # 提取 Pydantic Field 约束信息（pattern, max_length, min_length 等）
                if hasattr(field_info, 'metadata') and field_info.metadata:
                    for metadata in field_info.metadata:
                        if hasattr(metadata, 'pattern'):
                            field_data['pattern'] = metadata.pattern
                        if hasattr(metadata, 'max_length'):
                            field_data['max_length'] = metadata.max_length
                        if hasattr(metadata, 'min_length'):
                            field_data['min_length'] = metadata.min_length
                        if hasattr(metadata, 'ge'):  # greater than or equal
                            field_data['ge'] = metadata.ge
                        if hasattr(metadata, 'le'):  # less than or equal
                            field_data['le'] = metadata.le
                
                fields_info[field_name] = field_data
            
            return fields_info
            
        except Exception as e:
            print(f"⚠️ 字段提取失败: {e}")
            return {}
    
    def _generate_field_value(self, field_name: str, field_info) -> Any:
        """根据字段信息生成测试值 - 动态生成"""
        fake = Faker()
        field_name_lower = field_name.lower()
        
        # 通用字段类型推断 - 基于常见模式，不限于特定业务
        field_patterns = {
            'email': lambda: fake.email(),
            'username': lambda: fake.user_name(),
            'password': lambda: secrets.token_hex(4),
            'phone': lambda: f"1{fake.random_element(elements=[3,4,5,6,7,8,9])}{fake.random_number(digits=9)}",
            'code': lambda: str(fake.random_int(100000, 999999)),
            'verification': lambda: str(fake.random_int(100000, 999999)),
            'name': lambda: fake.name(),
            'title': lambda: fake.text(max_nb_chars=50),
            'description': lambda: fake.text(max_nb_chars=200),
            'url': lambda: fake.url(),
            'address': lambda: fake.address(),
            'city': lambda: fake.city(),
            'country': lambda: fake.country(),
            'currency': lambda: fake.currency_code(),
            'color': lambda: fake.color_name(),
            'size': lambda: fake.random_element(['S', 'M', 'L', 'XL']),
            'weight': lambda: fake.random_int(1, 1000),
            'height': lambda: fake.random_int(1, 200),
            'width': lambda: fake.random_int(1, 200),
            'length': lambda: fake.random_int(1, 200),
            'age': lambda: fake.random_int(18, 80),
            'count': lambda: fake.random_int(1, 100),
            'quantity': lambda: fake.random_int(1, 1000),
            'price': lambda: fake.random_int(10, 1000),
            'amount': lambda: fake.random_int(10, 10000),
            'discount': lambda: fake.random_int(5, 50),
            'rate': lambda: fake.random_int(1, 10),
            'rating': lambda: fake.random_int(1, 5),
            'active': lambda: fake.boolean(),
            'enabled': lambda: fake.boolean(),
            'status': lambda: fake.boolean(),
            'available': lambda: fake.boolean(),
            'visible': lambda: fake.boolean(),
        }
        
        # 查找匹配的模式
        for pattern, generator in field_patterns.items():
            if pattern in field_name_lower:
                return generator()
        
        # 如果没有匹配的模式，根据字段类型推断
        return self._generate_by_type(field_info)
    
    def _generate_by_type(self, field_info) -> Any:
        """根据字段类型生成默认值"""
        fake = Faker()  # Create Faker instance in this method scope
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
                    return fake.boolean()
                elif hasattr(field_type, '__name__'):
                    # 处理其他类型
                    type_name = field_type.__name__.lower()
                    if 'datetime' in type_name:
                        return fake.date_time().isoformat()
                    elif 'date' in type_name:
                        return fake.date().isoformat()
                    elif 'uuid' in type_name:
                        return str(fake.uuid4())
            
            # 默认动态字符串值
            return fake.word()
            
        except Exception:
            return fake.word()
    
    def _generate_fallback_data(self, route: RouterInfo) -> Dict[str, Any]:
        """生成fallback测试数据 - 动态生成"""
        fake = Faker()
        
        function_name = route.function_name.lower()
        
        if 'register' in function_name:
            return {
                "username": fake.user_name(),
                "email": fake.email(), 
                "password": secrets.token_hex(4),
                "phone": f"1{fake.random_element(elements=[3,4,5,6,7,8,9])}{fake.random_number(digits=9)}",
                "verification_code": str(fake.random_int(100000, 999999)),
                "real_name": fake.name()
            }
        elif 'login' in function_name:
            return {
                "username": fake.user_name(),
                "password": secrets.token_hex(4)
            }
        else:
            return {"data": fake.word()}
    
    def _convert_to_dynamic_code(self, field: str, value: Any) -> str:
        """
        将Schema字段信息转换为动态Faker生成代码
        
        这是一个通用工具方法，供所有测试生成器使用，用于将Pydantic Schema字段
        转换为相应的Faker代码字符串，支持类型推断和智能字段名匹配。
        
        Args:
            field: 字段名称（用于推断生成策略）
            value: 字段值信息（dict包含type和default，或直接值）
            
        Returns:
            str: Faker代码字符串（如 'fake.email()' 或 'fake.name()[:50]'）
            
        Examples:
            >>> _convert_to_dynamic_code('email', {'type': str, 'default': None})
            'fake.email()'
            
            >>> _convert_to_dynamic_code('phone', {'type': Optional[str]})
            'f"1{fake.random_int(min=3, max=9)}{fake.random_int(min=100000000, max=999999999)}"'
            
            >>> _convert_to_dynamic_code('code_type', {'type': Literal["register", "login"], 'default': 'register'})
            '"register"'
        """
        import typing
        from typing_extensions import Literal, get_origin, get_args
        
        # 获取字段类型信息
        if isinstance(value, dict) and 'type' in value:
            field_type = value['type']
            field_name_lower = field.lower()
            field_default = value.get('default')
            
            # 优先检查 pattern 约束（如 Field(pattern='^(register|login)$')）
            if 'pattern' in value and value['pattern']:
                pattern = value['pattern']
                # 尝试从 pattern 中提取枚举值（如 ^(register|login|reset_password)$ -> ['register', 'login', 'reset_password']）
                # 匹配模式：^(value1|value2|value3)$ 或 (value1|value2|value3)
                match = re.search(r'\^?\(([^)]+)\)\$?', pattern)
                if match:
                    enum_values = [v.strip() for v in match.group(1).split('|')]
                    if enum_values:
                        # 如果有默认值且在枚举中，使用默认值
                        if field_default is not None and field_default in enum_values:
                            return f'"{field_default}"'
                        # 否则使用第一个选项
                        return f'"{enum_values[0]}"'
            
            # 检查Literal类型
            if hasattr(field_type, '__origin__'):
                origin = get_origin(field_type) if hasattr(typing, 'get_origin') else getattr(field_type, '__origin__', None)
                
                # 处理Literal类型
                if origin is Literal or (hasattr(typing, 'Literal') and origin is getattr(typing, 'Literal', None)):
                    literal_values = get_args(field_type) if hasattr(typing, 'get_args') else getattr(field_type, '__args__', ())
                    if literal_values:
                        # 如果有默认值且在Literal选项中，使用默认值
                        if field_default is not None and field_default in literal_values:
                            return f'"{field_default}"'
                        # 否则使用第一个选项
                        return f'"{literal_values[0]}"'
            
            # 解析Optional类型
            is_optional = False
            actual_type = field_type
            if hasattr(field_type, '__origin__'):
                if field_type.__origin__ is typing.Union:
                    # Optional[T] 等价于 Union[T, None]
                    args = field_type.__args__
                    if type(None) in args:
                        is_optional = True
                        # 获取非None的类型
                        actual_type = next((arg for arg in args if arg is not type(None)), str)
                elif field_type.__origin__ in (list, typing.List):
                    actual_type = list
                elif field_type.__origin__ in (dict, typing.Dict):
                    actual_type = dict
            
            # 重新检查actual_type是否是Literal（处理Optional[Literal]的情况）
            if hasattr(actual_type, '__origin__'):
                origin = get_origin(actual_type) if hasattr(typing, 'get_origin') else getattr(actual_type, '__origin__', None)
                if origin is Literal or (hasattr(typing, 'Literal') and origin is getattr(typing, 'Literal', None)):
                    literal_values = get_args(actual_type) if hasattr(typing, 'get_args') else getattr(actual_type, '__args__', ())
                    if literal_values:
                        # 如果有默认值且在Literal选项中，使用默认值
                        if field_default is not None and field_default in literal_values:
                            return f'"{field_default}"'
                        # 否则使用第一个选项
                        return f'"{literal_values[0]}"'
            
            # 根据字段名称和类型生成代码
            # 字符串类型
            if actual_type in (str, type(str)):
                if any(keyword in field_name_lower for keyword in ['phone', 'mobile', 'tel']):
                    return 'f"1{fake.random_int(min=3, max=9)}{fake.random_int(min=100000000, max=999999999)}"'
                elif any(keyword in field_name_lower for keyword in ['verification_code', 'code', 'verify']):
                    return 'fake.numerify("######")'
                elif any(keyword in field_name_lower for keyword in ['email', 'mail']):
                    return 'fake.email()'
                elif any(keyword in field_name_lower for keyword in ['username', 'user_name']):
                    return 'fake.user_name().replace(".", "_")[:20]'
                elif any(keyword in field_name_lower for keyword in ['password', 'pwd']):
                    return 'fake.password(length=12)'
                elif field_name_lower == 'name' and 'username' not in field_name_lower:
                    # 根据上下文推断name字段类型
                    # 对于产品、分类、品牌等实体，生成合适的名称
                    return 'fake.company()[:50]'  # 使用公司名作为产品/品牌名更合适
                elif field_name_lower in ['real_name', 'full_name', 'display_name']:
                    return 'fake.name()[:50]'  # 只有明确的人名字段才使用fake.name()
                elif field_name_lower in ['status'] and is_optional:
                    # 对于状态字段，即使是Optional，也应该提供默认的有效值
                    return '"published"'  # 或其他合理的默认状态
                elif any(keyword in field_name_lower for keyword in ['seo_keywords', 'keywords']):
                    return '", ".join(fake.words(nb=5))'  # SEO关键词应该是逗号分隔的字符串
                elif any(keyword in field_name_lower for keyword in ['title']) and 'seo' in field_name_lower:
                    return 'fake.sentence(nb_words=5)[:200]'  # SEO标题应该是句子格式
                elif any(keyword in field_name_lower for keyword in ['address', 'addr']):
                    return 'fake.address()'
                else:
                    return 'fake.text(max_nb_chars=50)'
            
            # 整数类型
            elif actual_type in (int, type(int)):
                # 外键ID字段 - 使用创建的实体ID
                if field_name_lower.endswith('_id') and field_name_lower not in ['user_id']:
                    if is_optional:
                        return 'None'  # Optional外键可以为None
                    else:
                        # 推断实体变量名（去掉_id后缀）
                        entity_name = field.replace('_id', '')
                        entity_var = f"test_{entity_name}"
                        return f'{entity_var}.id'
                # 排序字段
                elif any(keyword in field_name_lower for keyword in ['sort', 'order', 'sequence']):
                    return 'fake.random_int(min=0, max=100)'
                else:
                    # 使用schema中定义的约束（如果有）
                    min_val = value.get('ge', value.get('gt', 1)) if isinstance(value, dict) else 1
                    max_val = value.get('le', value.get('lt', 999999)) if isinstance(value, dict) else 999999
                    # gt (greater than) 和 lt (less than) 需要调整
                    if isinstance(value, dict):
                        if 'gt' in value:
                            min_val = value['gt'] + 1
                        if 'lt' in value:
                            max_val = value['lt'] - 1
                    return f'fake.random_int(min={min_val}, max={max_val})'
            
            # 浮点数类型
            elif actual_type in (float, type(float)):
                return 'round(fake.random.uniform(0.0, 999.99), 2)'
            
            # Decimal类型（价格、金额等）
            elif hasattr(actual_type, '__name__') and actual_type.__name__ == 'Decimal':
                # 根据字段名生成合理的Decimal值
                if any(keyword in field_name_lower for keyword in ['price', 'cost', 'amount', 'fee']):
                    return 'round(fake.random.uniform(10.0, 999.99), 2)'
                elif any(keyword in field_name_lower for keyword in ['weight']):
                    return 'round(fake.random.uniform(0.1, 10.0), 2)'
                elif any(keyword in field_name_lower for keyword in ['volume']):
                    return 'round(fake.random.uniform(0.01, 1.0), 3)'
                else:
                    return 'round(fake.random.uniform(0.0, 999.99), 2)'
            
            # 布尔类型
            elif actual_type in (bool, type(bool)):
                return 'True'
            
            # 列表类型
            elif actual_type is list:
                return '[]' if is_optional else '["test_item"]'
            
            # 字典类型
            elif actual_type is dict:
                return 'None' if is_optional else '{}'
            
            # 其他类型
            else:
                return 'None'
        
        # 兼容旧的基于值的调用（向后兼容）
        elif isinstance(value, str):
            if any(keyword in field.lower() for keyword in ['phone', 'mobile', 'tel']):
                return 'f"1{fake.random_int(min=3, max=9)}{fake.random_int(min=100000000, max=999999999)}"'
            elif any(keyword in field.lower() for keyword in ['email', 'mail']):
                return 'fake.email()'
            elif any(keyword in field.lower() for keyword in ['name']):
                return 'fake.name()[:50]'
            else:
                return 'fake.text(max_nb_chars=50)'
        elif isinstance(value, int):
            if any(keyword in field.lower() for keyword in ['parent_id', 'category_id', 'brand_id']):
                return 'None'
            return 'fake.random_int(min=1, max=999999)'
        elif isinstance(value, bool):
            return 'True'
        
        # 其他情况保持原样
        else:
            return repr(value)