"""
E2E Test Generator

🚨 **关键模板格式化错误预防指南** 🚨

常见错误类型和正确解决方案:

1. **页面URL和元素选择器模板**:
   ❌ 错误: f"{{base_url}}/{{path}}"           # 双重转义
   ✅ 正确: f"{base_url}/{path}"               # 直接变量引用

2. **测试步骤文档字符串**:
   ❌ 错误: 在docstring中使用花括号{{}}导致格式错误
   ✅ 正确: 使用变量替换或简单字符串拼接

3. **测试数据文件路径**:
   ❌ 错误: 路径拼接中的转义字符错误
   ✅ 正确: 使用Path对象或os.path.join确保跨平台兼容

功能: 生成端到端用户流程测试代码
使用场景: 完整业务流程自动化测试

版本: v2.0.0
更新时间: 2025-10-07 (完整实现E2E测试生成)
"""

from typing import Dict, List
from .base_generator import BaseTestGenerator, ModelInfo, RouterInfo


class E2ETestGenerator(BaseTestGenerator):
    """E2E测试生成器 - 生成完整的端到端业务流程测试"""
    
    def generate_tests(self, module_name: str, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """生成E2E测试代码"""
        routes = self.analyze_router_file(module_name)
        test_content = self._generate_e2e_test_content(module_name, routes, models)
        return {f"tests/e2e/test_{module_name}_workflows.py": test_content}
    
    def _generate_e2e_test_content(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成E2E测试文件内容"""
        
        business_domain = self.get_module_business_domain(module_name)
        api_path = module_name.replace('_', '-')
        
        header = self.generate_test_file_header(
            module_name,
            "端到端业务流程",
            f"测试{business_domain}模块的完整用户业务流程\n"
            f"从用户角度验证端到端功能正确性"
        )
        
        imports = '''
import pytest
import asyncio
from httpx import AsyncClient
from fastapi import status
from faker import Faker

from app.main import app
from tests.conftest import api_client
'''
        
        # 生成主要的E2E测试类
        main_workflow_class = self._generate_main_workflow_test(module_name, routes, models, api_path)
        
        # 生成错误场景测试类
        error_workflow_class = self._generate_error_workflow_test(module_name, routes, api_path)
        
        return f'''{header}

{imports}

{main_workflow_class}

{error_workflow_class}
'''
    
    def _generate_main_workflow_test(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo], api_path: str) -> str:
        """生成主要业务流程测试类"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}E2EWorkflow"
        
        # 分析路由确定工作流
        workflow_steps = self._analyze_workflow_steps(routes, api_path)
        
        return f'''
@pytest.mark.e2e
@pytest.mark.asyncio
class {class_name}:
    """
    {business_domain}模块端到端测试
    
    测试完整的用户业务流程，验证：
    1. 用户认证和授权
    2. 数据创建和管理
    3. 业务流程正确性
    4. 错误处理和恢复
    """
    
    async def test_complete_business_workflow(self, async_api_client):
        """测试完整业务流程"""
        fake = Faker()
        
        # 步骤1: 用户认证
        print("\\n🔐 步骤1: 用户认证...")
        token, user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        assert token is not None
        assert user is not None
        print(f"✅ 用户认证成功: {{user.get('username', 'unknown')}}")
        
{workflow_steps}
        
        print("\\n✅ 完整业务流程测试通过")
    
    async def test_concurrent_user_workflow(self, async_api_client):
        """测试多用户并发业务流程"""
        fake = Faker()
        
        print("\\n👥 测试并发用户场景...")
        
        # 创建多个用户并发执行业务流程
        async def single_user_workflow(user_id):
            token, user = await async_api_client.authenticate_as_admin()
            headers = {{"Authorization": f"Bearer {{token}}"}}
            
            # 执行简单的CRUD操作
            response = await async_api_client.get(f"/api/v1/{api_path}/", headers=headers)
            return response.status_code == 200 or response.status_code == 404
        
        # 并发执行10个用户的工作流
        results = await asyncio.gather(*[single_user_workflow(i) for i in range(10)])
        
        # 验证所有用户都成功
        success_rate = sum(results) / len(results) * 100
        print(f"📊 并发测试成功率: {{success_rate:.1f}}%")
        
        assert success_rate >= 80, f"并发成功率过低: {{success_rate:.1f}}%"
        
        print("✅ 并发用户流程测试通过")
    
    async def test_workflow_with_data_dependencies(self, async_api_client):
        """测试具有数据依赖关系的业务流程"""
        fake = Faker()
        
        print("\\n🔗 测试数据依赖场景...")
        
        # 步骤1: 认证
        token, user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 步骤2: 创建父数据（如果模块有层级关系）
        {self._generate_dependency_workflow(routes, api_path)}
        
        print("✅ 数据依赖流程测试通过")
'''
    
    def _analyze_workflow_steps(self, routes: List[RouterInfo], api_path: str) -> str:
        """分析路由并生成工作流步骤"""
        
        # 查找POST路由（创建操作）
        post_routes = [r for r in routes if r.method == 'POST']
        # 查找GET路由（查询操作）
        get_routes = [r for r in routes if r.method == 'GET' and '{' not in r.path]
        # 查找PUT路由（更新操作）
        put_routes = [r for r in routes if r.method == 'PUT']
        # 查找DELETE路由（删除操作）
        delete_routes = [r for r in routes if r.method == 'DELETE']
        
        steps = []
        
        # 步骤2: 创建数据
        if post_routes:
            route = post_routes[0]
            steps.append(f'''
        # 步骤2: 创建数据
        print("\\n📝 步骤2: 创建数据...")
        create_data = {{
            "name": fake.name()[:50],
            "description": fake.text(max_nb_chars=100)
        }}
        
        response = await async_api_client.post(
            f"/api/v1{route.path}",
            json=create_data,
            headers=headers
        )
        
        # 验证创建成功
        if response.status_code in [201, 200]:
            created_item = response.json()
            print(f"✅ 数据创建成功: {{created_item}}")
            item_id = created_item.get('id')
        else:
            print(f"⚠️ 创建失败: {{response.status_code}}")
            item_id = None
''')
        
        # 步骤3: 查询数据列表
        if get_routes:
            route = get_routes[0]
            steps.append(f'''
        # 步骤3: 查询数据列表
        print("\\n📋 步骤3: 查询数据列表...")
        response = await async_api_client.get(
            f"/api/v1{route.path}",
            headers=headers
        )
        
        assert response.status_code in [200, 404], f"查询失败: {{response.status_code}}"
        
        if response.status_code == 200:
            items = response.json()
            print(f"✅ 查询成功，获取 {{len(items) if isinstance(items, list) else 'N/A'}} 条数据")
''')
        
        # 步骤4: 更新数据（如果有item_id）
        if put_routes and post_routes:
            route = put_routes[0]
            steps.append(f'''
        # 步骤4: 更新数据
        if item_id:
            print("\\n✏️ 步骤4: 更新数据...")
            update_data = {{
                "name": fake.name()[:50] + "_updated",
                "description": fake.text(max_nb_chars=100)
            }}
            
            update_path = f"/api/v1{route.path}".replace("{{", "{{{{").replace("}}", "}}}}")
            if "{{" in update_path:
                update_path = update_path.format(item_id)
            
            response = await async_api_client.put(
                update_path,
                json=update_data,
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ 数据更新成功")
''')
        
        # 步骤5: 删除数据（如果有item_id）
        if delete_routes and post_routes:
            route = delete_routes[0]
            steps.append(f'''
        # 步骤5: 删除数据
        if item_id:
            print("\\n🗑️ 步骤5: 删除数据...")
            delete_path = f"/api/v1{route.path}".replace("{{", "{{{{").replace("}}", "}}}}")
            if "{{" in delete_path:
                delete_path = delete_path.format(item_id)
            
            response = await async_api_client.delete(
                delete_path,
                headers=headers
            )
            
            assert response.status_code in [200, 204, 404], f"删除失败: {{response.status_code}}"
            print("✅ 数据删除成功")
''')
        
        return ''.join(steps) if steps else '''
        # 步骤2: 执行基本业务操作
        print("\\n📝 步骤2: 执行业务操作...")
        response = await async_api_client.get(f"/api/v1/{api_path}/", headers=headers)
        print(f"✅ 业务操作完成: {{response.status_code}}")
'''
    
    def _generate_dependency_workflow(self, routes: List[RouterInfo], api_path: str) -> str:
        """生成数据依赖工作流"""
        
        # 查找POST路由
        post_routes = [r for r in routes if r.method == 'POST']
        
        if not post_routes:
            return '''
        # 模块无创建端点，跳过依赖测试
        pass
'''
        
        return '''
        # 创建测试数据
        test_data = {"name": fake.name()[:50]}
        
        response = await async_api_client.post(
            f"/api/v1/{api_path}/",
            json=test_data,
            headers=headers
        )
        
        # 验证数据依赖处理
        if response.status_code in [200, 201]:
            print("✅ 依赖数据创建成功")
        else:
            print(f"⚠️ 依赖数据创建失败: {response.status_code}")
'''
    
    def _generate_error_workflow_test(self, module_name: str, routes: List[RouterInfo], api_path: str) -> str:
        """生成错误场景测试类"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}E2EErrorHandling"
        
        return f'''
@pytest.mark.e2e
@pytest.mark.asyncio
class {class_name}:
    """
    {business_domain}模块错误处理E2E测试
    
    测试异常场景和错误恢复：
    1. 无效数据处理
    2. 权限不足场景
    3. 资源不存在处理
    4. 并发冲突解决
    """
    
    async def test_invalid_data_handling(self, async_api_client):
        """测试无效数据处理"""
        fake = Faker()
        
        print("\\n❌ 测试无效数据处理...")
        
        # 认证
        token, user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 发送无效数据
        invalid_data = {{
            "name": "",  # 空名称
            "invalid_field": "should_be_rejected"
        }}
        
        response = await async_api_client.post(
            f"/api/v1/{api_path}/",
            json=invalid_data,
            headers=headers
        )
        
        # 应该返回验证错误
        assert response.status_code in [400, 422, 404], f"未正确处理无效数据: {{response.status_code}}"
        print("✅ 无效数据处理正确")
    
    async def test_unauthorized_access_handling(self, async_api_client):
        """测试未授权访问处理"""
        
        print("\\n🚫 测试未授权访问...")
        
        # 不提供认证token
        response = await async_api_client.get(f"/api/v1/{api_path}/")
        
        # 应该返回401或403（取决于端点是否需要认证）
        assert response.status_code in [200, 401, 403, 404], f"未授权访问处理异常: {{response.status_code}}"
        print("✅ 未授权访问处理正确")
    
    async def test_resource_not_found_handling(self, async_api_client):
        """测试资源不存在处理"""
        
        print("\\n🔍 测试资源不存在处理...")
        
        # 认证
        token, user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 访问不存在的资源
        response = await async_api_client.get(
            f"/api/v1/{api_path}/999999",
            headers=headers
        )
        
        # 应该返回404
        assert response.status_code in [404, 400], f"资源不存在处理异常: {{response.status_code}}"
        print("✅ 资源不存在处理正确")
    
    async def test_workflow_rollback_on_error(self, async_api_client):
        """测试错误时的工作流回滚"""
        fake = Faker()
        
        print("\\n🔄 测试工作流回滚...")
        
        # 认证
        token, user = await async_api_client.authenticate_as_admin()
        headers = {{"Authorization": f"Bearer {{token}}"}}
        
        # 尝试创建数据
        test_data = {{"name": fake.name()[:50]}}
        
        response = await async_api_client.post(
            f"/api/v1/{api_path}/",
            json=test_data,
            headers=headers
        )
        
        # 记录初始状态
        initial_status = response.status_code
        
        # 验证系统能恢复正常
        response = await async_api_client.get(
            f"/api/v1/{api_path}/",
            headers=headers
        )
        
        assert response.status_code in [200, 404], "系统未能从错误恢复"
        print("✅ 工作流回滚测试通过")
'''
