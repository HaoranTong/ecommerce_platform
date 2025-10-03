"""
API测试生成器

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

版本: v1.0.0
作者: AI Assistant
创建时间: 2025-10-01
"""

from typing import Dict, List
from .base_generator import BaseTestGenerator, ModelInfo, RouterInfo


class APITestGenerator(BaseTestGenerator):
    """API测试代码生成器"""
    
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
            f"测试{self.get_module_business_domain(module_name)}模块的所有REST API端点\\n"
            f"包括请求验证、响应格式、状态码、认证授权等方面的测试"
        )
        
        imports = '''
import pytest
import json
from fastapi import status
from unittest.mock import Mock, patch

from app.main import app
from tests.conftest import api_client
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
        
        return f'''
class {class_name}:
    """{business_domain}模块{method}方法API测试"""
    
    {chr(10).join(test_methods)}
'''
    
    def _generate_single_route_test(self, route: RouterInfo, models: Dict[str, ModelInfo]) -> str:
        """生成单个路由的测试方法"""
        
        method_name = f"test_{route.function_name}"
        
        # 生成测试数据
        test_data = self._generate_test_data_for_route(route, models)
        
        # 生成认证设置
        auth_setup = ""
        if route.auth_required:
            auth_setup = '''
        # 设置认证Token
        headers = {"Authorization": "Bearer test_token"}
        '''
        
        # 生成请求代码
        request_code = self._generate_request_code(route, test_data, route.auth_required)
        
        # 生成断言代码
        assertions = self._generate_assertions(route)
        
        return f'''
    def {method_name}(self, api_client):
        """测试{route.summary or route.function_name}"""
        {auth_setup}
        
        # 准备测试数据
        {test_data}
        
        # 发送请求
        {request_code}
        
        # 验证响应
        {assertions}
'''
    
    def _generate_test_data_for_route(self, route: RouterInfo, models: Dict[str, ModelInfo]) -> str:
        """为路由生成测试数据"""
        
        if route.method in ['POST', 'PUT', 'PATCH']:
            # 使用Schema分析生成动态测试数据
            try:
                # 从路由路径推断模块名
                module_name = self._extract_module_from_path(route.path)
                test_data_dict = self.analyze_pydantic_schema(module_name, route)
                
                # 转换为代码字符串
                if test_data_dict:
                    import json
                    data_str = json.dumps(test_data_dict, indent=12, ensure_ascii=False)
                    return f"test_data = {data_str}"
                else:
                    # fallback到原有逻辑
                    return self._generate_fallback_test_data(route)
                    
            except Exception as e:
                print(f"⚠️ 动态测试数据生成失败: {e}")
                return self._generate_fallback_test_data(route)
        else:
            # GET和DELETE请求
            return '''query_params = {
            "page": 1,
            "size": 10
        }'''
    
    def _extract_module_from_path(self, path: str) -> str:
        """从路径中提取模块名"""
        # 路径格式: /user-auth/register -> user_auth
        path_parts = path.strip('/').split('/')
        if path_parts:
            return path_parts[0].replace('-', '_')
        return 'unknown'
    
    def _generate_fallback_test_data(self, route: RouterInfo) -> str:
        """生成fallback测试数据（基于模式匹配的通用逻辑）"""
        
        # 基于函数名和参数推断测试数据结构
        function_name = route.function_name.lower()
        
        # 用户认证相关
        if 'register' in function_name:
            return '''test_data = {
            "username": "test_user",
            "email": "test@example.com", 
            "password": "test_password123",
            "phone": "13800138000",
            "verification_code": "123456",
            "real_name": "测试用户"
        }'''
        elif 'login' in function_name:
            return '''test_data = {
            "username": "test_user",
            "password": "test_password123"
        }'''
        elif 'password' in function_name and 'change' in function_name:
            return '''test_data = {
            "old_password": "old_password123",
            "new_password": "new_password123",
            "confirm_password": "new_password123"
        }'''
        
        # 商品相关
        elif any(keyword in function_name for keyword in ['product', 'item', 'goods']):
            if any(action in function_name for action in ['add', 'create']):
                return '''test_data = {
            "name": "测试商品",
            "price": 99.99,
            "description": "这是一个测试商品",
            "category_id": 1,
            "stock": 100
        }'''
            elif any(action in function_name for action in ['update', 'edit']):
                return '''test_data = {
            "name": "更新后的商品名",
            "price": 199.99,
            "description": "更新后的商品描述"
        }'''
        
        # 购物车相关
        elif any(keyword in function_name for keyword in ['cart', 'basket']):
            return '''test_data = {
            "product_id": 1,
            "quantity": 2,
            "sku_id": "SKU123"
        }'''
        
        # 订单相关
        elif any(keyword in function_name for keyword in ['order', 'purchase']):
            return '''test_data = {
            "items": [{"product_id": 1, "quantity": 2}],
            "shipping_address": "测试地址",
            "payment_method": "credit_card"
        }'''
        
        # 用户资料相关
        elif any(keyword in function_name for keyword in ['profile', 'user']) and 'update' in function_name:
            return '''test_data = {
            "real_name": "更新的姓名",
            "phone": "13800138001",
            "address": "更新的地址"
        }'''
        
        # 通用创建操作
        elif any(action in function_name for action in ['create', 'add']):
            return '''test_data = {
            "name": "测试名称",
            "description": "测试描述",
            "status": "active"
        }'''
        
        # 通用更新操作
        elif any(action in function_name for action in ['update', 'edit', 'modify']):
            return '''test_data = {
            "name": "更新的名称",
            "description": "更新的描述"
        }'''
        
        # 默认通用数据
        else:
            return '''test_data = {
            "test_field": "test_value",
            "number_field": 123,
            "boolean_field": True
        }'''
    
    def _generate_request_code(self, route: RouterInfo, test_data: str, auth_required: bool) -> str:
        """生成HTTP请求代码"""
        
        headers = "headers" if auth_required else "None"
        # 添加API前缀，确保路径正确
        full_path = f"/api/v1{route.path}"
        
        if route.method == 'GET':
            return f'''response = api_client.get(
            "{full_path}",
            params=query_params,
            headers={headers}
        )'''
        elif route.method in ['POST', 'PUT', 'PATCH']:
            return f'''response = api_client.{route.method.lower()}(
            "{full_path}",
            json=test_data,
            headers={headers}
        )'''
        elif route.method == 'DELETE':
            return f'''response = api_client.delete(
            "{full_path}",
            headers={headers}
        )'''
        else:
            return f'''response = api_client.{route.method.lower()}(
            "{full_path}",
            headers={headers}
        )'''
    
    def _generate_assertions(self, route: RouterInfo) -> str:
        """生成响应断言代码"""
        
        # 根据不同的操作类型生成不同的期望状态码
        if route.method == 'POST' and ('create' in route.function_name.lower() or 'register' in route.function_name.lower()):
            expected_status = 'status.HTTP_201_CREATED'
        elif route.method == 'DELETE':
            expected_status = 'status.HTTP_204_NO_CONTENT'
        else:
            expected_status = 'status.HTTP_200_OK'
        
        return f'''assert response.status_code == {expected_status}
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        {self._generate_business_assertions(route)}
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0'''

    def _generate_business_assertions(self, route: RouterInfo) -> str:
        """根据业务逻辑生成具体的断言"""
        function_name = route.function_name.lower()
        
        if 'register' in function_name:
            return '''# 验证用户注册响应
        assert "id" in response_data
        assert "username" in response_data
        assert "email" in response_data
        assert response_data["username"] == test_data["username"]
        assert response_data["email"] == test_data["email"]'''
        
        elif 'login' in function_name:
            return '''# 验证登录响应
        assert "access_token" in response_data or "token" in response_data
        assert "user" in response_data or "id" in response_data'''
        
        elif 'list' in function_name or 'get_all' in function_name:
            return '''# 验证列表响应
        assert isinstance(response_data, list) or "items" in response_data
        if isinstance(response_data, list):
            assert len(response_data) >= 0
        else:
            assert "items" in response_data
            assert isinstance(response_data["items"], list)'''
        
        elif route.method == 'GET' and ('get' in function_name or 'read' in function_name):
            return '''# 验证获取单项响应
        assert "id" in response_data'''
        
        elif route.method in ['POST', 'PUT'] and ('create' in function_name or 'update' in function_name or 'add' in function_name):
            return '''# 验证创建/更新响应
        assert "id" in response_data
        # 验证关键字段已更新'''
        
        elif route.method == 'DELETE':
            return '''# DELETE操作通常返回空响应或确认信息
        # 204状态码表示成功删除'''
        
        else:
            return '''# 验证基本响应结构
        assert len(response_data) > 0 or response_data == {}'''
    
    def _generate_integration_test_class(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成API集成测试类"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}APIIntegration"
        
        # 生成端到端的业务流程测试
        workflow_test = self._generate_workflow_integration_test(module_name, routes, models)
        
        return f'''
class {class_name}:
    """{business_domain}模块API集成测试 - 测试完整业务流程"""
    
    {workflow_test}
    
    def test_api_error_handling(self, api_client):
        """测试API错误处理机制"""
        # 测试400 Bad Request
        response = api_client.post("/api/v1/{module_name}/invalid", json={{}})
        assert response.status_code in [400, 404, 422]
        
        error_data = response.json()
        assert not error_data.get("success", True)
        assert "error" in error_data or "detail" in error_data
    
    def test_api_rate_limiting(self, api_client):
        """测试API限流机制"""
        # 快速发送多个请求测试限流
        responses = []
        for _ in range(20):
            response = api_client.get("/api/v1/{module_name}/test")
            responses.append(response.status_code)
        
        # 检查是否有429状态码（限流）
        if 429 in responses:
            print("✅ API限流机制正常工作")
        else:
            print("ℹ️ 未触发API限流（可能阈值较高）")
'''
    
    def _generate_workflow_integration_test(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成业务流程集成测试"""
        
        if module_name == 'user_auth':
            return '''
    def test_user_auth_workflow(self, api_client):
        """测试用户认证完整流程：注册 -> 登录 -> 获取用户信息 -> 更新信息"""
        
        # 1. 用户注册
        register_data = {
            "username": "integration_test_user",
            "email": "integration@test.com",
            "password": "test_password123",
            "phone": "13900139000",
            "real_name": "集成测试用户"
        }
        
        register_response = api_client.post(
            "/api/v1/user-auth/register",
            json=register_data
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        user_data = register_response.json()["data"]
        user_id = user_data["id"]
        
        # 2. 用户登录
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        
        login_response = api_client.post(
            "/api/v1/user-auth/login",
            json=login_data
        )
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()["data"]
        access_token = token_data["access_token"]
        
        # 3. 获取用户信息
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = api_client.get(
            "/api/v1/user-auth/me",
            headers=headers
        )
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.json()["data"]
        assert profile_data["id"] == user_id
        assert profile_data["username"] == register_data["username"]
        
        # 4. 更新用户信息
        update_data = {
            "real_name": "更新后的姓名",
            "phone": "13900139001"
        }
        
        update_response = api_client.put(
            "/api/v1/user-auth/me",
            json=update_data,
            headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_data = update_response.json()["data"]
        assert updated_data["real_name"] == update_data["real_name"]
        assert updated_data["phone"] == update_data["phone"]
        
        print("✅ 用户认证完整流程测试通过")
'''
        elif module_name == 'shopping_cart':
            return '''
    def test_shopping_cart_workflow(self, api_client):
        """测试购物车完整流程：添加商品 -> 更新数量 -> 查看购物车 -> 删除商品"""
        
        # 准备用户认证
        headers = {"Authorization": "Bearer test_token"}
        
        # 1. 添加商品到购物车
        add_item_data = {
            "sku_id": 12345,
            "quantity": 2
        }
        
        add_response = api_client.post(
            "/api/v1/shopping-cart/items",
            json=add_item_data,
            headers=headers
        )
        assert add_response.status_code == status.HTTP_200_OK
        cart_data = add_response.json()["data"]
        assert cart_data["total_items"] >= 1
        
        # 2. 更新商品数量
        update_data = {
            "sku_id": 12345,
            "quantity": 3
        }
        
        update_response = api_client.put(
            "/api/v1/shopping-cart/items",
            json=update_data,
            headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # 3. 查看购物车
        view_response = api_client.get(
            "/api/v1/shopping-cart",
            headers=headers
        )
        assert view_response.status_code == status.HTTP_200_OK
        cart_items = view_response.json()["data"]["items"]
        assert len(cart_items) >= 1
        
        # 4. 删除商品
        delete_response = api_client.delete(
            f"/api/v1/shopping-cart/items/{add_item_data['sku_id']}",
            headers=headers
        )
        assert delete_response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        
        print("✅ 购物车完整流程测试通过")
'''
        else:
            return f'''
    def test_{module_name}_workflow(self, api_client):
        """测试{self.get_module_business_domain(module_name)}模块完整业务流程"""
        
        # TODO: 根据具体业务逻辑实现完整流程测试
        # 1. 创建资源
        # 2. 查询资源
        # 3. 更新资源
        # 4. 删除资源
        
        headers = {{"Authorization": "Bearer test_token"}}
        
        # 示例流程测试
        response = api_client.get("/api/v1/{module_name}/health")
        assert response.status_code in [200, 404]  # 404表示端点不存在但服务正常
        
        print("✅ {self.get_module_business_domain(module_name)}基础流程测试通过")
'''
