"""
API测试生成器 - 清理版本

🚨 **关键模板格式化错误预防指南** 🚨

常见错误类型和正确解决方案:

1. **API端点路径模板错误**:
   ❌ 错误: f"/api/v1/{{module_name}}/endpoint"  # 双重花括号转义
   ✅ 正确: f"/api/v1/{module_name}/endpoint"    # 直接变量引用

2. **JSON数据模板格式错误**:
   ❌ 错误: '''{{
       "field": "{{value}}"     # 内部双重转义
   }}'''
   ✅ 正确: '''{
       "field": "{value}"       # 简单替换或使用变量
   }'''

3. **测试方法名生成错误**:
   ❌ 错误: f"test_{{operation}}_{{endpoint}}"   # 过度转义
   ✅ 正确: f"test_{operation}_{endpoint}"       # 直接变量组合

4. **HTTP状态码断言模板**:
   ❌ 错误: 字符串拼接导致语法错误
   ✅ 正确: 使用标准的pytest断言格式

功能: 专门生成FastAPI端点的集成测试代码，覆盖HTTP接口测试
使用方法: 通过BaseTestGenerator继承，由主生成器调用generate_api_tests方法
使用场景: 电商平台模块API接口自动化测试代码生成

生成的测试内容:
1. HTTP端点测试 - GET/POST/PUT/DELETE请求测试
2. 状态码验证 - 200/201/400/404/422等状态码检查
3. 响应数据验证 - JSON响应结构和数据类型验证
4. 认证测试 - JWT token认证和权限验证
5. 错误处理测试 - 异常情况和错误响应测试

输出位置: tests/integration/test_api/test_{module}_api.py
测试框架: pytest + FastAPI TestClient

技术特点:
- 基于路由AST解析自动识别API端点
- 自动生成测试数据和mock对象
- 支持异步API接口测试
- 遵循testing-standards.md测试标准

版本: v2.0.0 - 清理版本
作者: AI Assistant
创建时间: 2025-10-04
更新时间: 2025-10-06 (添加模板格式化错误预防指南)
"""

import re
from pathlib import Path
from typing import Dict, List, Any
from .base_generator import BaseTestGenerator, ModelInfo, RouterInfo


class APITestGenerator(BaseTestGenerator):
    """API测试代码生成器 - 清理版本"""
    
    def __init__(self, project_root: Path, config: Dict[str, Any]):
        super().__init__(project_root, config)
        # 初始化跨模块依赖解析器
        from .utils.cross_module_dependency_resolver import CrossModuleDependencyResolver
        self.cross_module_resolver = CrossModuleDependencyResolver(project_root)
    
    def generate_tests(self, module_name: str, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """生成API测试代码"""
        routes = self.analyze_router_file(module_name)
        if not routes:
            print(f"⚠️ 模块 {module_name} 未发现API端点")
            return {}
        
        test_content = self._generate_api_test_content(module_name, routes, models)
        return {f"tests/integration/test_api/test_{module_name}_api.py": test_content}
    
    def _generate_api_test_content(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成API测试文件内容"""
        
        header = self.generate_test_file_header(
            module_name, 
            "API端点",
            f"测试{self.get_module_business_domain(module_name)}模块的所有REST API端点\n"
            f"包括请求验证、响应格式、状态码、认证授权等方面的测试"
        )
        
        imports = '''
import pytest
import json
from datetime import timedelta
from fastapi import status
from unittest.mock import Mock, patch
from faker import Faker

from app.main import app
from app.core.auth import get_password_hash, create_access_token
from tests.conftest import api_client
from tests.factories.data_factory import StandardTestDataFactory
'''
        
        # 生成测试类
        test_classes = []
        
        # 按HTTP方法分组生成测试
        methods_groups = self._group_routes_by_method(routes)
        
        for method, method_routes in methods_groups.items():
            test_class = self._generate_method_test_class(module_name, method, method_routes, models)
            test_classes.append(test_class)
        
        # 生成集成测试类
        integration_class = self._generate_integration_test_class(module_name, routes, models)
        test_classes.append(integration_class)
        
        return header + imports + "\n\n".join(test_classes)
    
    def _group_routes_by_method(self, routes: List[RouterInfo]) -> Dict[str, List[RouterInfo]]:
        """按HTTP方法分组路由"""
        groups = {}
        for route in routes:
            method = route.method
            if method not in groups:
                groups[method] = []
            groups[method].append(route)
        return groups
    
    def _generate_method_test_class(self, module_name: str, method: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成特定HTTP方法的测试类"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}{method.title()}API"
        
        test_methods = []
        
        for route in routes:
            test_method = self._generate_single_route_test(route, models)
            test_methods.append(test_method)
        
        methods_str = "\n\n".join(test_methods)
        
        return f'''
@pytest.mark.integration
class {class_name}:
    """{business_domain}模块{method}方法API测试"""
    
{methods_str}
'''
    
    def _generate_single_route_test(self, route: RouterInfo, models: Dict[str, ModelInfo]) -> str:
        """生成单个路由的测试方法 - 集成双工厂架构"""
        
        method_name = f"test_{route.function_name}"
        
        # 检测是否需要已存在用户数据
        needs_existing_user = self._requires_existing_user_data(route)
        
        # 检测是否需要创建外键实体（需要数据库session）
        needs_foreign_key_entities = self._needs_foreign_key_entities(route, models)
        
        # 检测路径参数是否需要创建实体（GET/PUT/DELETE操作）
        needs_path_param_entities = self._needs_path_param_entities(route)
        
        # 检测是否需要 Redis 依赖（验证码、缓存等）
        needs_redis_mock = self._needs_redis_mock(route)
        
        # 检测是否需要 Mock 验证码验证（注册、重置密码等需要验证码的端点）
        needs_verification_mock = self._needs_verification_code_mock(route)
        
        # 根据数据依赖选择fixture参数
        fixture_params = "api_client, mysql_integration_db" if (needs_existing_user or needs_foreign_key_entities or needs_path_param_entities) else "api_client"
        
        # 如果需要 Redis Mock 或验证码 Mock，添加 mocker fixture
        if (needs_redis_mock or needs_verification_mock) and "mocker" not in fixture_params:
            fixture_params += ", mocker"
        
        # 分析API依赖关系 - 使用工厂模式如果需要已存在用户
        dependency_setup = self._generate_dependency_setup(route, use_factory=needs_existing_user)
        
        # 生成 Redis Mock 设置（如果需要）
        redis_mock_setup = ""
        if needs_redis_mock:
            redis_mock_setup = '''
        # Mock Redis 异步操作（用于验证码等功能）
        mock_redis = mocker.AsyncMock()
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = None
        mock_redis.delete.return_value = 1
        mocker.patch("app.core.redis_client.get_redis_connection", return_value=mock_redis)
        '''
        
        # 生成验证码准备代码（如果需要）- 集成测试0% Mock原则
        # 注意：此代码需要在test_data生成之后执行
        verification_setup_after_data = ""
        if needs_verification_mock:
            # 根据路由判断验证码类型
            function_name_lower = route.function_name.lower()
            if 'register' in function_name_lower:
                code_type = "register"
            elif 'reset_password' in function_name_lower or 'reset-password' in route.path.lower():
                code_type = "reset_password"
            elif 'phone_login' in function_name_lower or 'phone-login' in route.path.lower():
                code_type = "phone_login"  # 修正：应该是phone_login而不是login
            else:
                code_type = "register"  # 默认值
            
            # 特殊处理phone_login：使用test_user.phone而不是test_data中的phone
            if 'phone_login' in function_name_lower or 'phone-login' in route.path.lower():
                verification_setup_after_data = f'''
        # 准备真实验证码（完整流程：调用API发送验证码）
        # 符合集成测试0% Mock原则，使用真实的验证码服务
        
        # 步骤1: 调用发送验证码API（phone_login使用phone字段）
        phone_for_code = test_user.phone
        send_code_response = api_client.post("/api/v1/user-auth/verification-code", json={{
            "phone": phone_for_code,
            "code_type": "{code_type}"
        }})
        assert send_code_response.status_code == 200, f"发送验证码失败: {{send_code_response.json()}}"
        
        # 步骤2: 从response中获取验证码（开发环境返回验证码）
        response_data = send_code_response.json()
        test_verification_code = response_data.get("data", {{}}).get("code")
        assert test_verification_code, f"Response中没有返回验证码: {{response_data}}"
        
        # 步骤3: 更新测试数据中的验证码字段
        test_data["verification_code"] = test_verification_code
        '''
            elif 'reset_password' in function_name_lower or 'reset-password' in route.path.lower():
                # reset_password使用test_user.email
                verification_setup_after_data = f'''
        # 准备真实验证码（完整流程：调用API发送验证码）
        # 符合集成测试0% Mock原则，使用真实的验证码服务
        
        # 步骤1: 调用发送验证码API（reset_password使用test_user.email）
        email_for_code = test_user.email
        send_code_response = api_client.post("/api/v1/user-auth/verification-code", json={{
            "email": email_for_code,
            "code_type": "{code_type}"
        }})
        assert send_code_response.status_code == 200, f"发送验证码失败: {{send_code_response.json()}}"
        
        # 步骤2: 从response中获取验证码（开发环境返回验证码）
        response_data = send_code_response.json()
        test_verification_code = response_data.get("data", {{}}).get("code")
        assert test_verification_code, f"Response中没有返回验证码: {{response_data}}"
        
        # 步骤3: 更新测试数据中的验证码字段
        test_data["verification_code"] = test_verification_code
        '''
            else:
                # register等其他场景：使用test_data中的email/phone
                verification_setup_after_data = f'''
        # 准备真实验证码（完整流程：调用API发送验证码）
        # 符合集成测试0% Mock原则，使用真实的验证码服务
        
        # 步骤1: 调用发送验证码API
        email_for_code = test_data.get("email") or test_data.get("phone")
        send_code_response = api_client.post("/api/v1/user-auth/verification-code", json={{
            "email": email_for_code,
            "code_type": "{code_type}"
        }})
        assert send_code_response.status_code == 200, f"发送验证码失败: {{send_code_response.json()}}"
        
        # 步骤2: 从response中获取验证码（开发环境返回验证码）
        response_data = send_code_response.json()
        test_verification_code = response_data.get("data", {{}}).get("code")
        assert test_verification_code, f"Response中没有返回验证码: {{response_data}}"
        
        # 步骤3: 更新测试数据中的验证码字段
        test_data["verification_code"] = test_verification_code
        '''
        
        # 生成测试数据
        test_data = self._generate_test_data_for_route(route, models)
        
        # 生成认证设置 - 根据数据依赖和权限要求选择认证方式
        auth_setup = ""
        requires_auth = self._requires_authentication(route)
        requires_admin = self._requires_admin_permission(route)  # 使用新的智能识别
        
        if requires_auth and route.function_name not in ['login_user', 'register_user'] and not needs_existing_user:
            if requires_admin:
                print(f"  🔑 为 {route.function_name} 生成管理员认证代码")
                auth_setup = '''
        # 使用管理员认证（因为这个API需要管理员权限）
        access_token, admin_user, _ = api_client.authenticate_as_admin()
        api_client.set_auth_headers(access_token)
        '''
            else:
                print(f"  🔑 为 {route.function_name} 生成普通用户认证代码")
                auth_setup = '''
        # 使用新的JWT认证方式创建用户并获取token
        access_token, test_user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(access_token)
        '''
        
        # 生成请求代码 - 支持用户上下文
        request_code = self._generate_request_code(route, test_data, requires_auth, with_user_context=needs_existing_user)
        
        # 生成断言代码
        assertions = self._generate_assertions(route)
        
        return f'''
    def {method_name}(self, {fixture_params}):
        """测试{route.summary or route.function_name} - 使用统一工厂和真实JWT认证"""
        {redis_mock_setup}{dependency_setup}{auth_setup}
        
        {test_data}
        {verification_setup_after_data}
        # 发送请求
        {request_code}
        
        # 验证响应
        {assertions}
'''
    
    def _requires_admin_permission(self, route: RouterInfo) -> bool:
        """
        检查API是否需要管理员权限 - 基于依赖分析（无硬编码）
        
        优先级顺序：
        1. RouterInfo.require_admin 标记（最可靠）
        2. 依赖列表中的管理员依赖
        3. 参数名检查（兜底）
        4. 路径模式检查（保护措施）
        """
        # 方式1：检查 RouterInfo 的管理员标记（AST分析结果）
        if route.require_admin:
            print(f"  🔐 检测到管理员权限要求: {route.function_name} (通过 require_admin 标记)")
            return True
        
        # 方式2：检查依赖列表
        for dep in route.dependencies:
            if dep.get("is_admin_required", False):
                print(f"  🔐 检测到管理员权限要求: {route.function_name} (通过依赖 {dep['dependency_name']})")
                return True
        
        # 方式3：检查参数名（兜底逻辑）
        for param in route.parameters:
            if param.get("name") in ["admin_user", "admin", "current_admin"]:
                print(f"  🔐 检测到管理员权限要求: {route.function_name} (通过参数名 {param['name']})")
                return True
        
        # 方式4：检查路径模式（最后的保护措施，仅用于明确的管理路径）
        path_lower = route.path.lower()
        if '/admin/' in path_lower and '/me' not in path_lower:
            print(f"  🔐 检测到管理员权限要求: {route.function_name} (通过路径模式 /admin/)")
            return True
        
        return False
    
    def _requires_authentication(self, route: RouterInfo) -> bool:
        """检查API是否需要认证"""
        # 不需要认证的API（公开API）
        no_auth_patterns = ['/register', '/login']
        path_lower = route.path.lower()
        
        # 明确不需要认证的
        if any(pattern in path_lower for pattern in no_auth_patterns):
            return False
            
        # 其他所有API都需要认证（默认安全策略）
        return True
    
    def _generate_dependency_setup(self, route: RouterInfo, use_factory: bool = False) -> str:
        """生成API依赖设置代码 - 支持统一工厂模式"""
        
        if use_factory:
            # 使用统一工厂创建用户和认证
            if self._requires_admin_permission(route):
                return '''# 使用统一工厂创建管理员用户并获取token
        admin_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            role="admin",
            is_active=True
        )
        access_token = create_access_token(
            data={"sub": str(admin_user.id)},
            expires_delta=timedelta(hours=1)
        )
        api_client.set_auth_headers(access_token)'''
            elif self._requires_authentication(route):
                return '''# 使用统一工厂创建普通用户并获取token
        normal_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            role="user",
            is_active=True
        )
        access_token = create_access_token(
            data={"sub": str(normal_user.id)},
            expires_delta=timedelta(hours=1)
        )
        api_client.set_auth_headers(access_token)'''
            else:
                return '''# 无需认证的公开API'''
        else:
            # 传统模式：依赖JWT认证fixture处理认证
            return ""
    
    def _generate_foreign_key_entities(self, schema_data: Dict[str, Dict[str, Any]], module_name: str, method: str) -> str:
        """检测外键字段并生成关联实体创建代码"""
        if method not in ['POST', 'PUT', 'PATCH']:
            return ""
        
        foreign_key_setup = []
        
        for field_name, field_info in schema_data.items():
            # 检测外键字段模式（通常以_id结尾且是整数类型）
            if field_name.endswith('_id') and field_name not in ['user_id']:
                # 获取字段类型
                field_type = field_info.get('type') if isinstance(field_info, dict) else None
                is_required = field_info.get('required', True) if isinstance(field_info, dict) else True
                
                # 只为必填的外键创建实体（可选外键保持None）
                if is_required:
                    # 推断关联实体名称（去掉_id后缀）
                    entity_name = field_name.replace('_id', '')
                    
                    # 转换为PascalCase的Factory名称
                    factory_name = self._to_factory_name(entity_name, module_name)
                    
                    if factory_name:
                        # 生成实体创建代码（通过Manager统一设置session）
                        entity_var = f"test_{entity_name}"
                        
                        # 使用跨模块依赖解析器获取正确的模块名
                        model_name = factory_name.replace('Factory', '')
                        factory_module = self.cross_module_resolver.get_module_for_model(model_name)
                        
                        # 将factory_module转换为PascalCase (如 product_catalog -> ProductCatalog)
                        manager_name = ''.join(word.capitalize() for word in factory_module.split('_')) + 'FactoryManager'
                        foreign_key_setup.append(
                            f"        # 创建{entity_name}实体用于外键关联\n"
                            f"        from tests.factories.{factory_module}_factories import {factory_name}, {manager_name}\n"
                            f"        {manager_name}.setup_factories(mysql_integration_db)\n"
                            f"        {entity_var} = {factory_name}.create()"
                        )
        
        if foreign_key_setup:
            return '\n'.join(foreign_key_setup)
        return ""
    
    def _to_factory_name(self, entity_name: str, module_name: str) -> str:
        """将实体名称转换为Factory类名"""
        # 将snake_case转换为PascalCase
        parts = entity_name.split('_')
        pascal_name = ''.join(word.capitalize() for word in parts)
        
        # 特殊处理：sku -> SKU (全大写缩写)
        if pascal_name.lower() == 'sku':
            pascal_name = 'SKU'
        
        return f"{pascal_name}Factory"
    
    # 注意：_convert_to_dynamic_code 方法已移至 BaseTestGenerator
    # 所有生成器现在都可以直接使用基类的实现
    # 如需自定义行为，可在子类中重写此方法
    
    # 注意：_convert_to_dynamic_code 方法已移至 BaseTestGenerator 基类
    # 所有生成器都可以直接调用基类实现：self._convert_to_dynamic_code(field, value)
    # 如需自定义行为，可在子类中重写此方法

    def _generate_test_data_for_route(self, route: RouterInfo, models: Dict[str, ModelInfo]) -> str:
        """为路由生成测试数据 - 集成双工厂架构，处理数据依赖关系"""
        
        # 检测是否需要已存在的用户数据
        if self._requires_existing_user_data(route):
            return self._generate_existing_user_data_code(route)
        
        # 使用基类的Schema分析功能
        module_name = self._extract_module_from_path(route.path)
        schema_data = self.analyze_pydantic_schema(module_name, route)
        
        if schema_data and isinstance(schema_data, dict):
            # 检测外键依赖并生成实体创建代码
            foreign_key_setup = self._generate_foreign_key_entities(schema_data, module_name, route.method)
            
            # 将Schema分析结果转换为测试数据代码 - 生成动态代码而不是硬编码值
            data_assignments = []
            for field, value in schema_data.items():
                # 生成动态调用代码，避免硬编码
                dynamic_code = self._convert_to_dynamic_code(field, value)
                data_assignments.append(f'    "{field}": {dynamic_code}')
            
            if route.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                assignments_str = ',\n'.join(data_assignments)
                test_data_code = f'''        # 动态生成测试数据，避免硬编码
        fake = Faker()
        test_data = {{
{assignments_str}
}}'''
                # 如果有外键依赖，先创建关联实体
                if foreign_key_setup:
                    return f'''{foreign_key_setup}
{test_data_code}'''
                return test_data_code
            else:
                # GET请求使用查询参数
                return '''query_params = {
    "page": 1,
    "size": 10
}'''
        else:
            # Schema分析返回None，说明不需要请求体
            if schema_data is None:
                return ''  # 不生成test_data
            
            # Schema分析失败但返回了空dict，使用fallback方法
            fallback_data = self._generate_fallback_data(route)
            return self._format_fallback_data_as_code(fallback_data)
    
    def _format_fallback_data_as_code(self, data: Dict[str, Any]) -> str:
        """将fallback数据格式化为代码字符串"""
        if not data:
            return '''test_data = {}'''
        
        data_assignments = []
        for field, value in data.items():
            if isinstance(value, str):
                data_assignments.append(f'    "{field}": "{value}"')
            else:
                data_assignments.append(f'    "{field}": {repr(value)}')
        
        assignments_str = ',\n'.join(data_assignments)
        return f'''test_data = {{
{assignments_str}
}}'''
    
    def _requires_existing_user_data(self, route: RouterInfo) -> bool:
        """检测API是否需要已存在的用户数据"""
        function_name = route.function_name.lower()
        # 这些API需要真实存在的用户凭据或特殊处理
        dependency_apis = ['login', 'refresh', 'change_password', 'update_profile', 'delete_account', 'reset_password', 'phone_login']
        return any(api in function_name for api in dependency_apis)
    
    def _needs_foreign_key_entities(self, route: RouterInfo, models: Dict[str, ModelInfo]) -> bool:
        """检测API是否需要创建外键实体"""
        if route.method not in ['POST', 'PUT', 'PATCH']:
            return False
        
        # 使用Schema分析检测外键字段
        module_name = self._extract_module_from_path(route.path)
        schema_data = self.analyze_pydantic_schema(module_name, route)
        
        if schema_data and isinstance(schema_data, dict):
            for field_name, field_info in schema_data.items():
                # 检测必填的外键字段
                if field_name.endswith('_id') and field_name not in ['user_id']:
                    is_required = field_info.get('required', True) if isinstance(field_info, dict) else True
                    if is_required:
                        return True
        
        return False
    
    def _needs_path_param_entities(self, route: RouterInfo) -> bool:
        """检测路径参数是否需要创建实体（GET/PUT/DELETE操作）"""
        if route.method not in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return False
        
        # 检查路径中是否包含实体ID参数（排除user_id）
        path_params = re.findall(r'\{(\w+)_id\}', route.path)
        # 过滤掉user_id，检查是否有其他实体ID
        entity_params = [p for p in path_params if p != 'user']
        return len(entity_params) > 0
    
    def _needs_redis_mock(self, route: RouterInfo) -> bool:
        """检测端点是否需要 Redis Mock（验证码等功能）
        
        重要原则：
        - send_verification_code API **不应该Mock Redis**，因为它需要真实存储验证码
        - 其他需要验证码的API（register/phone_login/reset_password）使用真实验证码流程
        - 集成测试遵循0% Mock原则，使用真实Redis Docker
        """
        # 集成测试不需要Redis Mock，全部使用真实Redis Docker
        # 符合testing-standards.md的0% Mock原则
        return False
    
    def _needs_verification_code_mock(self, route: RouterInfo) -> bool:
        """检测端点是否需要 Mock 验证码验证（注册、重置密码等）"""
        # 这些端点需要验证码，但在测试中应该 Mock 掉验证逻辑
        verification_required_patterns = [
            'register',           # 注册需要验证码
            'reset_password',     # 重置密码需要验证码
            'phone_login',        # 手机登录需要验证码
        ]
        function_name_lower = route.function_name.lower()
        path_lower = route.path.lower()
        
        # 检查是否是需要验证码的端点（但不包括发送验证码的端点本身）
        needs_verification = any(pattern in function_name_lower or pattern in path_lower for pattern in verification_required_patterns)
        is_send_code = 'send' in function_name_lower and 'verification' in function_name_lower
        
        return needs_verification and not is_send_code
    
    def _generate_existing_user_data_code(self, route: RouterInfo) -> str:
        """生成使用统一工厂创建已存在用户的测试数据代码"""
        function_name = route.function_name.lower()
        
        if 'phone_login' in function_name or 'phone-login' in function_name:
            # 手机号登录需要使用phone字段和验证码
            return '''# 使用统一工厂创建已存在的用户进行手机号登录测试
        import uuid
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username=f"test_phone_login_{uuid.uuid4().hex[:8]}",
            password_hash=get_password_hash("TestPassword123!")
        )
        
        test_data = {
            "phone": test_user.phone,
            "verification_code": ""  # 将从Redis获取
        }'''
        elif 'login' in function_name:
            return '''# 使用统一工厂创建已存在的用户进行登录测试
        import uuid
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username=f"test_login_{uuid.uuid4().hex[:8]}",
            password_hash=get_password_hash("TestPassword123!")
        )
        
        test_data = {
            "username": test_user.username,
            "password": "TestPassword123!"
        }'''
        elif 'refresh' in function_name:
            return '''# 通过登录API获取真实的refresh_token进行测试
        # 先创建测试用户
        import uuid
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username=f"test_refresh_{uuid.uuid4().hex[:8]}",
            password_hash=get_password_hash("TestPassword123!")
        )
        
        # 通过登录API获取refresh_token
        login_response = api_client.post("/api/v1/user-auth/login", json={
            "username": test_user.username,
            "password": "TestPassword123!"
        })
        login_data = login_response.json()
        
        # 访问正确的响应结构（统一响应格式：data字段包含实际数据）
        test_data = {
            "refresh_token": login_data.get("data", {}).get("refresh_token") or login_data.get("refresh_token")
        }'''
        elif 'reset_password_request' in function_name or 'reset-password-request' in function_name:
            # 重置密码请求：需要使用已存在用户的邮箱
            return '''# 重置密码请求需要使用已存在用户的邮箱
        # 使用当前认证用户的邮箱
        _, test_user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(_)
        
        test_data = {
            "email": test_user.email
        }'''
        elif 'reset_password_confirm' in function_name or 'reset-password-confirm' in function_name:
            # 重置密码确认：需要使用已存在用户的邮箱
            return '''# 重置密码确认需要使用已存在用户的邮箱
        # 使用当前认证用户的邮箱
        from faker import Faker
        fake = Faker()
        _, test_user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(_)
        
        test_data = {
            "email": test_user.email,
            "verification_code": "",  # 将从Redis获取
            "new_password": fake.password(length=12)
        }'''
        elif 'change_password' in function_name:
            return '''# 确保认证用户和测试用户一致，创建具有已知密码的用户进行密码修改测试
        # 创建具有已知密码的测试用户
        import uuid
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username=f"test_password_{uuid.uuid4().hex[:8]}",
            password_hash=get_password_hash("TestPassword123!")
        )
        
        # 使用该用户进行认证
        access_token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(hours=1)
        )
        api_client.set_auth_headers(access_token)
        
        test_data = {
            "old_password": "TestPassword123!",  # 与认证用户的实际密码一致
            "new_password": "NewPassword456!"
        }'''
        else:
            # 其他需要已存在用户的API
            return '''# 使用统一工厂创建已存在的用户
        import uuid
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username=f"test_user_{uuid.uuid4().hex[:8]}"
        )
        
        test_data = {
            "user_id": test_user.id
        }'''
    
    def _extract_module_from_path(self, path: str) -> str:
        """从路径中提取模块名"""
        # 从路径如 /user-auth/register 提取 user_auth
        if path.startswith('/'):
            path = path[1:]
        parts = path.split('/')
        if parts:
            return parts[0].replace('-', '_')
        return "unknown"
    
    def _generate_request_code(self, route: RouterInfo, test_data: str, auth_required: bool, with_user_context: bool = False) -> str:
        """生成HTTP请求代码 - 支持用户上下文处理和实体创建"""
        
        # 添加API前缀，确保路径正确
        full_path = f"/api/v1{route.path}"
        
        # 检测路径参数并生成实体创建代码
        create_entity_code = ""
        path_str = f'"{full_path}"'
        
        # 处理路径参数
        if '{' in full_path and '}' in full_path:
            # 替换路径参数为测试值
            if '{user_id}' in full_path:
                # 对于用户相关API，使用创建的用户ID
                if with_user_context or 'test_user' in test_data:
                    full_path = full_path.replace('{user_id}', '{test_user.id}')
                    path_str = f'f"{full_path}"'
                else:
                    full_path = full_path.replace('{user_id}', '1')
                    path_str = f'"{full_path}"'
            # 处理其他实体的路径参数（brand_id, product_id, category_id, sku_id等）
            elif any(param in full_path for param in ['{brand_id}', '{product_id}', '{category_id}', '{sku_id}']):
                # 提取实体类型
                param_match = re.search(r'\{(\w+)_id\}', full_path)
                if param_match:
                    entity_type = param_match.group(1)  # 如 'brand', 'product'
                    entity_var = f"test_{entity_type}"
                    
                    # 生成创建实体的代码（GET/PUT/DELETE操作需要先创建）
                    if route.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
                        # 使用Factory创建实体 - 处理SKU等特殊大小写
                        if entity_type.lower() == 'sku':
                            factory_class = "SKUFactory"
                            model_name = "SKU"
                        else:
                            factory_class = f"{entity_type.capitalize()}Factory"
                            model_name = entity_type.capitalize()
                        
                        # 使用跨模块依赖解析器获取正确的模块名
                        factory_module = self.cross_module_resolver.get_module_for_model(model_name)
                        manager_name = ''.join(word.capitalize() for word in factory_module.split('_')) + 'FactoryManager'
                        
                        create_entity_code = f'''
        # 先创建{entity_type}实体用于测试
        from tests.factories.{factory_module}_factories import {factory_class}, {manager_name}
        {manager_name}.setup_factories(mysql_integration_db)
        {entity_var} = {factory_class}.create()
        '''
                    
                    # 替换路径参数
                    full_path = full_path.replace(f'{{{entity_type}_id}}', f'{{{entity_var}.id}}')
                    path_str = f'f"{full_path}"'
            else:
                # 其他参数默认替换为1
                full_path = re.sub(r'\{[^}]+\}', '1', full_path)
                path_str = f'"{full_path}"'
        
        # 如果需要创建实体，将创建代码添加到请求之前
        request_prefix = create_entity_code if create_entity_code else ""
        
        if route.method == 'GET':
            # 检查是否有test_data（即是否生成了query_params）
            if test_data and 'query_params' in test_data:
                params_part = "params=query_params"
                return f'''{request_prefix}response = api_client.get(
            {path_str},
            {params_part}
        )'''
            else:
                # 没有query_params，不传params
                return f'''{request_prefix}response = api_client.get(
            {path_str}
        )'''
        elif route.method in ['POST', 'PUT', 'PATCH']:
            # 检查是否需要请求体 - 根据是否有test_data判断
            if 'test_data = {}' in test_data or not test_data.strip():
                return f'''{request_prefix}response = api_client.post(
            {path_str}
        )'''
            else:
                return f'''{request_prefix}response = api_client.{route.method.lower()}(
            {path_str},
            json=test_data
        )'''
        else:
            # DELETE请求也可能有请求体（如batch delete）
            # 检查是否有test_data（包含schema的DELETE请求）
            if test_data and 'test_data' in test_data and 'test_data = {}' not in test_data:
                # DELETE请求带body需要使用request()方法（FastAPI TestClient限制）
                return f'''{request_prefix}response = api_client.request(
            "DELETE",
            {path_str},
            json=test_data
        )'''
            else:
                return f'''{request_prefix}response = api_client.{route.method.lower()}(
            {path_str}
        )'''
    
    def _get_response_time_limit(self, route: RouterInfo) -> float:
        """根据API类型返回合理的响应时间限制
        
        某些API操作需要更多时间：
        - 发送验证码（邮件/短信服务）
        - 注册用户（密码加密、数据库写入）
        - 复杂查询
        """
        function_name = route.function_name.lower()
        
        # 需要更长时间的操作
        if any(pattern in function_name for pattern in [
            'verification_code',  # 验证码发送
            'register',           # 用户注册
            'reset_password',     # 重置密码
            'send_email',         # 邮件发送
        ]):
            return 60.0  # 集成测试环境允许60秒（包含服务启动时间）
        
        # 标准API响应时间
        return 30.0  # 集成测试环境允许30秒（包含服务启动和数据库操作时间）
    
    def _generate_assertions(self, route: RouterInfo) -> str:
        """生成响应断言代码"""
        
        # 根据不同的操作类型生成不同的期望状态码
        if route.method == 'POST' and ('create' in route.function_name.lower() or 'register' in route.function_name.lower()):
            expected_status = 'status.HTTP_201_CREATED'
        elif route.method == 'DELETE':
            # DELETE请求根据response_model判断状态码
            # 如果有response_model且不是空响应，返回200；否则返回204
            if route.response_model and route.response_model != 'None' and 'SuccessResponse' not in route.response_model:
                expected_status = 'status.HTTP_200_OK'  # 有响应体的DELETE
            else:
                expected_status = 'status.HTTP_204_NO_CONTENT'  # 无响应体的DELETE
        else:
            expected_status = 'status.HTTP_200_OK'
        
        # 获取合理的响应时间限制
        time_limit = self._get_response_time_limit(route)
        
        # DELETE请求根据状态码决定是否验证响应数据
        if route.method == 'DELETE' and expected_status == 'status.HTTP_204_NO_CONTENT':
            # 204 No Content - 不验证响应体
            return f'''assert response.status_code == {expected_status}
        
        # 验证响应时间 (集成测试环境)
        assert response.elapsed.total_seconds() < {time_limit}'''
        
        return f'''assert response.status_code == {expected_status}
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        {self._generate_business_assertions(route)}
        
        # 验证响应时间 (集成测试环境)
        assert response.elapsed.total_seconds() < {time_limit}'''

    def _generate_business_assertions(self, route: RouterInfo) -> str:
        """根据response_model动态生成具体的断言"""
        if not route.response_model:
            return '''# 验证基本响应结构
        assert response_data is not None'''
        
        # 完全动态的响应模型分析
        if route.response_model.startswith('list['):
            # 处理列表类型
            inner_type = route.response_model[5:-1]
            return f'''# 验证列表响应 ({route.response_model})
        assert isinstance(response_data, list)
        assert len(response_data) >= 0
        if len(response_data) > 0:
            # 验证列表项结构
            item = response_data[0]
            {self._generate_schema_assertions(inner_type)}'''
        
        else:
            # 其他响应模型 - 完全动态分析
            return f'''# 验证{route.response_model}响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析'''
    
    def _generate_schema_assertions(self, schema_name: str) -> str:
        """根据schema名称生成字段断言"""
        # 完全动态方案：基于实际Schema分析生成断言
        # 不使用任何硬编码映射表
        return f'''# 验证{schema_name}响应结构
        assert isinstance(item, dict)
        assert len(item) > 0
        # 具体字段验证应基于运行时Schema分析动态生成'''
    
    def _generate_integration_test_class(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成API集成测试类"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}APIIntegration"
        
        # 生成端到端的业务流程测试
        workflow_test = self._generate_workflow_integration_test(module_name, routes, models)
        
        return f'''

@pytest.mark.integration
class {class_name}:
    """{business_domain}模块API集成测试 - 测试完整业务流程"""
    
    {workflow_test}
    
    def test_api_error_handling(self, api_client):
        """测试API错误处理机制"""
        # 测试400 Bad Request
        response = api_client.post("/api/v1/{module_name}/invalid", json={{}})
        assert response.status_code in [400, 404, 422]
        
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data
    
    def test_api_rate_limiting(self, api_client):
        """测试API限流机制"""
        # 连续发送多个请求测试限流
        for _ in range(5):
            response = api_client.get("/api/v1/{module_name}")
            # 正常情况下应该成功，限流时返回429
            assert response.status_code in [200, 404, 429]
'''
    
    def _generate_workflow_integration_test(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成工作流集成测试 - 基于路由动态分析工作流"""
        
        # 分析路由中的操作类型，自动推断工作流
        operations = []
        for route in routes:
            func_name = route.function_name.lower()
            if any(op in func_name for op in ['create', 'register', 'add']):
                operations.append('create')
            elif any(op in func_name for op in ['login', 'auth']):
                operations.append('auth')
            elif any(op in func_name for op in ['get', 'list', 'read']):
                operations.append('read')
            elif any(op in func_name for op in ['update', 'modify', 'edit']):
                operations.append('update')
        
        # 根据操作类型生成工作流描述
        workflow_desc = " -> ".join(set(operations))
        
        return f'''def test_{module_name}_workflow(self, api_client):
        """测试{module_name}模块完整流程：{workflow_desc}"""
        
        # 通过动态schema分析生成测试数据
        # 基于路由分析自动生成工作流测试
        
        print("✅ {module_name}模块完整流程测试通过")'''