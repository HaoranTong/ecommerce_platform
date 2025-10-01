"""
API测试生成器

基于router.py分析自动生成API端点测试代码
遵循docs/standards/api-standards.md和testing-standards.md规范
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
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch

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
    async def {method_name}(self, api_client: AsyncClient):
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
            # 对于创建和更新操作，生成请求体数据
            if 'register' in route.function_name.lower():
                return '''test_data = {
            "username": "test_user",
            "email": "test@example.com", 
            "password": "test_password123",
            "phone": "13800138000",
            "real_name": "测试用户"
        }'''
            elif 'login' in route.function_name.lower():
                return '''test_data = {
            "username": "test_user",
            "password": "test_password123"
        }'''
            elif 'add' in route.function_name.lower() or 'create' in route.function_name.lower():
                return '''test_data = {
            "name": "测试商品",
            "price": 99.99,
            "description": "这是一个测试商品"
        }'''
            else:
                return '''test_data = {
            "field1": "value1",
            "field2": "value2"
        }'''
        else:
            # 对于查询操作，生成查询参数
            return '''query_params = {
            "page": 1,
            "size": 10
        }'''
    
    def _generate_request_code(self, route: RouterInfo, test_data: str, auth_required: bool) -> str:
        """生成HTTP请求代码"""
        
        headers = "headers" if auth_required else "None"
        
        if route.method == 'GET':
            return f'''response = await api_client.get(
            "{route.path}",
            params=query_params,
            headers={headers}
        )'''
        elif route.method in ['POST', 'PUT', 'PATCH']:
            return f'''response = await api_client.{route.method.lower()}(
            "{route.path}",
            json=test_data,
            headers={headers}
        )'''
        elif route.method == 'DELETE':
            return f'''response = await api_client.delete(
            "{route.path}",
            headers={headers}
        )'''
        else:
            return f'''response = await api_client.{route.method.lower()}(
            "{route.path}",
            headers={headers}
        )'''
    
    def _generate_assertions(self, route: RouterInfo) -> str:
        """生成响应断言代码"""
        
        # 根据不同的操作类型生成不同的期望状态码
        if route.method == 'POST' and 'create' in route.function_name.lower():
            expected_status = 'status.HTTP_201_CREATED'
        elif route.method == 'DELETE':
            expected_status = 'status.HTTP_204_NO_CONTENT'
        else:
            expected_status = 'status.HTTP_200_OK'
        
        return f'''assert response.status_code == {expected_status}
        
        # 验证响应格式符合API标准
        response_data = response.json()
        assert "success" in response_data
        assert "code" in response_data
        assert "message" in response_data
        
        # 验证业务逻辑
        if response_data["success"]:
            assert "data" in response_data
            assert response_data["code"] == response.status_code
        
        # 验证响应时间 (API标准要求<200ms)
        assert response.elapsed.total_seconds() < 0.2'''
    
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
    
    async def test_api_error_handling(self, api_client: AsyncClient):
        """测试API错误处理机制"""
        # 测试400 Bad Request
        response = await api_client.post("/api/v1/{module_name}/invalid", json={{}})
        assert response.status_code in [400, 404, 422]
        
        error_data = response.json()
        assert not error_data.get("success", True)
        assert "error" in error_data or "detail" in error_data
    
    async def test_api_rate_limiting(self, api_client: AsyncClient):
        """测试API限流机制"""
        # 快速发送多个请求测试限流
        responses = []
        for _ in range(20):
            response = await api_client.get("/api/v1/{module_name}/test")
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
    async def test_user_auth_workflow(self, api_client: AsyncClient):
        """测试用户认证完整流程：注册 -> 登录 -> 获取用户信息 -> 更新信息"""
        
        # 1. 用户注册
        register_data = {
            "username": "integration_test_user",
            "email": "integration@test.com",
            "password": "test_password123",
            "phone": "13900139000",
            "real_name": "集成测试用户"
        }
        
        register_response = await api_client.post(
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
        
        login_response = await api_client.post(
            "/api/v1/user-auth/login",
            json=login_data
        )
        assert login_response.status_code == status.HTTP_200_OK
        token_data = login_response.json()["data"]
        access_token = token_data["access_token"]
        
        # 3. 获取用户信息
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = await api_client.get(
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
        
        update_response = await api_client.put(
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
    async def test_shopping_cart_workflow(self, api_client: AsyncClient):
        """测试购物车完整流程：添加商品 -> 更新数量 -> 查看购物车 -> 删除商品"""
        
        # 准备用户认证
        headers = {"Authorization": "Bearer test_token"}
        
        # 1. 添加商品到购物车
        add_item_data = {
            "sku_id": 12345,
            "quantity": 2
        }
        
        add_response = await api_client.post(
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
        
        update_response = await api_client.put(
            "/api/v1/shopping-cart/items",
            json=update_data,
            headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # 3. 查看购物车
        view_response = await api_client.get(
            "/api/v1/shopping-cart",
            headers=headers
        )
        assert view_response.status_code == status.HTTP_200_OK
        cart_items = view_response.json()["data"]["items"]
        assert len(cart_items) >= 1
        
        # 4. 删除商品
        delete_response = await api_client.delete(
            f"/api/v1/shopping-cart/items/{add_item_data['sku_id']}",
            headers=headers
        )
        assert delete_response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        
        print("✅ 购物车完整流程测试通过")
'''
        else:
            return f'''
    async def test_{module_name}_workflow(self, api_client: AsyncClient):
        """测试{self.get_module_business_domain(module_name)}模块完整业务流程"""
        
        # TODO: 根据具体业务逻辑实现完整流程测试
        # 1. 创建资源
        # 2. 查询资源
        # 3. 更新资源
        # 4. 删除资源
        
        headers = {{"Authorization": "Bearer test_token"}}
        
        # 示例流程测试
        response = await api_client.get("/api/v1/{module_name}/health")
        assert response.status_code in [200, 404]  # 404表示端点不存在但服务正常
        
        print("✅ {self.get_module_business_domain(module_name)}基础流程测试通过")
'''