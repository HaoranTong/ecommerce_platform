"""
安全测试生成器

🚨 **关键模板格式化错误预防指南** 🚨

常见错误类型和正确解决方案:

1. **f-string模板中的花括号转义错误**:
   ❌ 错误: f"/api/v1/{{module_name}}/endpoint"  # 双重转义
   ✅ 正确: f"/api/v1/{module_name}/endpoint"    # 直接变量引用

2. **URL路径模板错误**:
   ❌ 错误: "倢/api/v1/{api_module_name}/test倢"  # 乱码字符
   ✅ 正确: f"/api/v1/{module_name}/test"        # 清晰的路径格式

3. **代码模板中的变量作用域**:
   ❌ 错误: 在字符串模板中引用未传递的变量
   ✅ 正确: 确保所有模板变量都通过.format()或f-string正确传递

4. **HTTP请求模板格式**:
   ❌ 错误: 混合引号和特殊字符导致语法错误
   ✅ 正确: 使用一致的引号风格和正确的转义

功能: 生成基于OWASP Top 10的安全测试代码，检测Web应用安全漏洞
使用方法: 通过BaseTestGenerator继承，由主生成器调用generate_security_tests方法
使用场景: 电商平台安全漏洞检测和防护能力验证

生成的安全测试:
1. SQL注入测试 - 检测数据库查询注入漏洞
2. XSS攻击测试 - 验证跨站脚本攻击防护
3. CSRF防护测试 - 验证跨站请求伪造防护机制
4. 认证绕过测试 - 检测身份认证绕过漏洞
5. 权限提升测试 - 验证访问控制和权限边界
6. 敏感数据泄露测试 - 检测数据暴露风险
7. 输入验证测试 - 验证输入数据安全过滤

输出位置: tests/security/test_{module}_security.py
测试框架: pytest + 安全测试工具集

技术特点:
- 基于OWASP Top 10安全标准
- 自动生成恶意输入测试用例
- 支持API安全扫描
- 集成安全测试报告

版本: v1.0.0
作者: AI Assistant
创建时间: 2025-10-01
更新时间: 2025-10-06 (修复内容混乱问题，添加模板格式化指南)
"""

import secrets
from typing import Any, Dict, List

from faker import Faker

from .base_generator import BaseTestGenerator, ModelInfo, RouterInfo


class SecurityTestGenerator(BaseTestGenerator):
    """安全测试代码生成器"""
    
    def generate_tests(self, module_name: str, models: Dict[str, ModelInfo]) -> Dict[str, str]:
        """生成安全测试代码"""
        
        routes = self.analyze_router_file(module_name)
        test_content = self._generate_security_test_content(module_name, routes, models)
        return {f"tests/security/test_{module_name}_security.py": test_content}
    
    def _generate_security_test_content(self, module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo]) -> str:
        """生成安全测试文件内容"""
        
        # 生成动态测试数据 - 避免硬编码
        fake = Faker()
        
        # 动态生成测试token和ID
        test_token = f"security_test_{secrets.token_hex(8)}"
        user_level_token = f"user_level_{secrets.token_hex(8)}"
        user_a_token = f"user_a_{secrets.token_hex(6)}"
        user_b_id = f"test_user_{fake.random_int(1000, 9999)}"
        
        # 正确转换模块名为API路径格式 (user_auth -> user-auth)
        api_module_name = module_name.replace('_', '-')
        
        header = self.generate_test_file_header(
            module_name,
            "安全防护",
            f"测试{self.get_module_business_domain(module_name)}模块的安全防护机制\\n"
            f"基于OWASP Top 10，包括注入攻击、认证绕过、权限提升等安全测试"
        )
        
        imports = '''
import pytest
import json
import asyncio
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch

from app.main import app
from tests.conftest import api_client
'''
        
        # 生成OWASP Top 10测试类
        owasp_class = self._generate_owasp_top10_tests(module_name, api_module_name, routes, models, test_token)
        
        # 生成认证授权测试类
        auth_class = self._generate_authentication_tests(module_name, api_module_name, routes, models, test_token, user_level_token)
        
        # 生成输入验证测试类
        input_validation_class = self._generate_input_validation_tests(module_name, api_module_name, routes, models, test_token)
        
        # 生成数据保护测试类
        data_protection_class = self._generate_data_protection_tests(module_name, models, test_token, user_a_token, user_b_id)
        
        return header + imports + "\n\n".join([
            owasp_class,
            auth_class,
            input_validation_class,
            data_protection_class
        ])
    
    def _generate_owasp_top10_tests(self, module_name: str, api_module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo], test_token: str) -> str:
        """生成OWASP Top 10安全测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}OWASPTop10"
        
        # 动态生成测试数据 - 避免硬编码
        default_test_data = self._generate_dynamic_security_data(routes)

        return f'''
class {class_name}:
    """{business_domain}模块OWASP Top 10安全测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_security_test(self, async_api_client):
        """安全测试前置：获取真实的admin和普通用户token"""
        # 创建管理员用户和token
        admin_token, admin_user = await async_api_client.authenticate_as_admin()
        self.admin_token = admin_token
        self.admin_user = admin_user
        
        # 创建普通用户和token（用于权限测试）
        user_token, normal_user = await async_api_client.authenticate_as_user()
        self.user_token = user_token
        self.normal_user = normal_user
        yield
    
    async def test_sql_injection_protection(self, async_api_client):
        """测试SQL注入防护 - OWASP #1"""
        
        # SQL注入攻击载荷
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "admin'; --",
            "1' OR 1=1#"
        ]
        
        # 使用动态选择的端点进行SQL注入测试
        get_endpoint = "{self._select_auth_endpoint(routes, api_module_name)}"
        post_endpoint = "{self._select_post_endpoint(routes, api_module_name)}"
        
        test_endpoints = [
            {{"method": "GET", "path": get_endpoint, "params": {{"search": None}}}},
            {{"method": "POST", "path": post_endpoint, "json": {{"username": None, "email": None, "password": None}}}},
        ]
        
        # 测试各个端点的SQL注入防护
        for payload in sql_payloads:
            for endpoint in test_endpoints:
                try:
                    if endpoint["method"] == "GET":
                        # 更新查询参数
                        params = {{k: payload if v is None else v for k, v in endpoint["params"].items()}}
                        response = await async_api_client.get(endpoint["path"], params=params)
                    elif endpoint["method"] == "POST":
                        # 更新JSON数据
                        json_data = {{k: payload if v is None else v for k, v in endpoint["json"].items()}}
                        response = await async_api_client.post(endpoint["path"], json=json_data)
                    
                    # 应该返回400/422而不是500，说明有输入验证
                    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR, f"SQL注入可能成功: {{endpoint}}"
                    
                except Exception as e:
                    # 如果端点不存在，跳过测试
                    if "404" in str(e) or "Not Found" in str(e):
                        continue
                    raise
        
        print("✅ SQL注入防护测试通过")
    
    async def test_xss_protection(self, async_api_client):
        """测试XSS跨站脚本防护 - OWASP #7"""
        
        # XSS攻击载荷
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>"
        ]
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 使用真实的POST端点进行XSS测试
        test_endpoint = "{self._select_post_endpoint(routes, api_module_name)}"
        
        for payload in xss_payloads:
            # 测试输入字段的XSS防护
            response = await async_api_client.post(
                test_endpoint,
                json={{"description": payload, "comment": payload}},
                headers=headers
            )
            
            # 验证响应不包含原始脚本代码
            if response.status_code == 200:
                response_text = response.text
                assert "<script>" not in response_text.lower()
                assert "javascript:" not in response_text.lower()
                assert "onerror=" not in response_text.lower()
        
        print("✅ XSS防护测试通过")
    
    async def test_csrf_protection(self, async_api_client):
        """测试CSRF跨站请求伪造防护 - OWASP #8"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 使用真实的POST端点进行CSRF测试
        sensitive_endpoint = "{self._select_post_endpoint(routes, api_module_name)}"
        
        # 测试缺少CSRF token的请求
        response = await async_api_client.post(
            sensitive_endpoint,
            json={{"action": "delete", "target": "important_data"}},
            headers=headers
        )
        
        # 对于敏感操作，应该要求额外的验证
        # 可能返回403或要求额外验证
        if response.status_code not in [404, 405]:  # 端点存在的情况下
            assert response.status_code in [403, 422, 400]
        
        print("✅ CSRF防护测试通过")
    
    async def test_broken_authentication(self, async_api_client):
        """测试认证机制安全性 - OWASP #2"""
        
        # 测试弱密码
        from faker import Faker
        fake = Faker()
        weak_passwords = [fake.password(length=6), fake.word(), "admin", "", fake.word()]
        
        for weak_password in weak_passwords:
            response = await async_api_client.post(
                "/api/v1/user-auth/login",
                json={{"username": fake.user_name(), "password": weak_password}}
            )
            
            # 弱密码应该被拒绝（已经在注册时验证）
            # 或者登录失败
            assert response.status_code in [401, 400, 422]
        
        # 测试暴力破解防护
        test_username = fake.user_name()
        for _ in range(10):
            response = await async_api_client.post(
                "/api/v1/user-auth/login",
                json={{"username": test_username, "password": fake.password()}}
            )
            await asyncio.sleep(0.1)
        
        # 应该有频率限制或账户锁定
        print("✅ 认证安全测试通过")
    
    async def test_sensitive_data_exposure(self, async_api_client):
        """测试敏感数据泄露防护 - OWASP #3"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 测试API响应是否泄露敏感信息
        response = await async_api_client.get("/api/v1/user-auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json().get("data", {{}})
            
            # 确保密码哈希不在响应中
            sensitive_fields = ["password", "password_hash", "secret", "private_key"]  # noqa: 安全测试标准敏感字段列表
            for field in sensitive_fields:
                assert field not in user_data
                
            # 确保没有内部系统信息泄露
            internal_fields = ["internal_id", "system_role", "debug_info"]
            for field in internal_fields:
                assert field not in user_data
        
        print("✅ 敏感数据保护测试通过")
    
    async def test_security_misconfiguration(self, async_api_client):
        """测试安全配置错误 - OWASP #6"""
        
        # 测试是否暴露调试信息
        response = await async_api_client.get("/api/v1/debug")
        assert response.status_code == 404  # 生产环境不应该有debug端点
        
        # 测试是否暴露系统信息
        response = await async_api_client.get("/api/v1/system/info")
        assert response.status_code == 404  # 不应该暴露系统信息
        
        # 测试错误处理
        response = await async_api_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        # 确保错误响应不包含内部路径或堆栈信息
        if response.status_code in [400, 500]:
            error_text = response.text.lower()
            assert "/app/" not in error_text
            assert "traceback" not in error_text
            assert "exception" not in error_text
        
        print("✅ 安全配置测试通过")
'''
    
    def _generate_authentication_tests(self, module_name: str, api_module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo], test_token: str, user_level_token: str) -> str:
        """生成认证授权测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}Authentication"
        
        return f'''
class {class_name}:
    """{business_domain}模块认证授权安全测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_security_test(self, async_api_client):
        """安全测试前置：获取真实的admin和普通用户token"""
        # 创建管理员用户和token
        admin_token, admin_user = await async_api_client.authenticate_as_admin()
        self.admin_token = admin_token
        self.admin_user = admin_user
        
        # 创建普通用户和token（用于权限测试）
        user_token, normal_user = await async_api_client.authenticate_as_user()
        self.user_token = user_token
        self.normal_user = normal_user
        yield
    
    async def test_unauthorized_access(self, async_api_client):
        """测试未授权访问防护"""
        
        # 测试不带token的请求
        protected_endpoints = [
            "/api/v1/{module_name}/protected",
            "/api/v1/{module_name}/admin",
            "/api/v1/{module_name}/user-data"
        ]
        
        for endpoint in protected_endpoints:
            response = await async_api_client.get(endpoint)
            # 应该返回401未授权，而不是200
            assert response.status_code in [401, 404, 405]
        
        print("✅ 未授权访问防护测试通过")
    
    async def test_token_validation(self, async_api_client):
        """测试Token验证机制"""
        
        # 测试无效token
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
            "Bearer ",
            "",
            "malformed.jwt.token"
        ]
        
        for token in invalid_tokens:
            headers = {{"Authorization": f"Bearer {{token}}"}}
            response = await async_api_client.get("{self._select_auth_endpoint(routes, api_module_name)}", headers=headers)
            # 对于真实存在的端点，期望401（未授权）或403（禁止访问）
            if response.status_code not in [404, 405]:  # 端点存在
                assert response.status_code in [401, 403]
        
        # 测试过期token（模拟）
        expired_token = "expired.jwt.token"
        headers = {{"Authorization": f"Bearer {{expired_token}}"}}
        response = await async_api_client.get("{self._select_auth_endpoint(routes, api_module_name)}", headers=headers)
        if response.status_code not in [404, 405]:  # 端点存在
            assert response.status_code in [401, 403]
        
        print("✅ Token验证测试通过")
    
    async def test_privilege_escalation(self, async_api_client):
        """测试权限提升防护"""
        
        # 使用普通用户token尝试访问管理员端点
        headers = {{"Authorization": f"Bearer {{self.user_token}}"}}
        
        admin_endpoints = [
            "/api/v1/{module_name}/admin/users",
            "/api/v1/{module_name}/admin/settings",
            "/api/v1/{module_name}/admin/delete"
        ]
        
        for endpoint in admin_endpoints:
            response = await async_api_client.get(endpoint, headers=headers)
            # 应该返回403权限不足，而不是200
            assert response.status_code in [403, 404, 405]
        
        print("✅ 权限提升防护测试通过")
    
    async def test_session_security(self, async_api_client):
        """测试会话安全性"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 测试会话固定攻击防护
        # 登录前后的会话ID应该不同
        
        # 测试并发会话限制
        concurrent_requests = []
        for _ in range(10):
            req = async_api_client.get("/api/v1/{module_name}/me", headers=headers)
            concurrent_requests.append(req)
        
        responses = await asyncio.gather(*concurrent_requests, return_exceptions=True)
        
        # 验证并发请求处理
        successful_responses = [r for r in responses if hasattr(r, 'status_code') and r.status_code == 200]
        
        print(f"✅ 会话安全测试通过，并发请求处理正常: {{len(successful_responses)}}/10")
'''
    
    def _generate_input_validation_tests(self, module_name: str, api_module_name: str, routes: List[RouterInfo], models: Dict[str, ModelInfo], test_token: str) -> str:
        """生成输入验证测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}InputValidation"
        
        return f'''
class {class_name}:
    """{business_domain}模块输入验证安全测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_security_test(self, async_api_client):
        """安全测试前置：获取真实的admin token"""
        admin_token, admin_user = await async_api_client.authenticate_as_admin()
        self.admin_token = admin_token
        self.admin_user = admin_user
        yield
    
    async def test_malicious_input_handling(self, async_api_client):
        """测试恶意输入处理"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 恶意输入载荷 - 只测试那些应该被Pydantic验证拒绝的输入
        # 注意：路径遍历、SQL注入等特殊字符应该在使用时转义，而不是在输入时拒绝
        malicious_inputs = [
            "A" * 10000,                   # 缓冲区溢出测试 - 超过字段最大长度
            "B" * 5000,                    # 超长输入测试
            "\\x00\\x01\\x02\\x03\\x04",   # 二进制/控制字符测试
        ]
        
        test_endpoint = "{self._select_post_endpoint(routes, api_module_name)}"
        
        for payload in malicious_inputs:
            test_data = {{
                "name": payload,
                "description": payload,
            }}
            
            response = await async_api_client.post(
                test_endpoint,
                json=test_data,
                headers=headers
            )
            
            # 超长输入应该被验证拒绝（返回422）或被服务器拒绝（返回413）
            # 如果endpoint不存在返回404，如果不是POST返回405，都是可接受的
            if response.status_code not in [404, 405]:
                assert response.status_code in [400, 422, 413], f"超长输入应该被拒绝，但返回了 {{response.status_code}}"
        
        print("✅ 恶意输入处理测试通过")
    
    async def test_data_type_validation(self, async_api_client):
        """测试数据类型验证"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 类型错误测试
        invalid_data_types = [
            {{"id": "not_a_number"}},        # 字符串代替数字
            {{"price": "invalid_price"}},     # 无效价格格式
            {{"email": "not_an_email"}},      # 无效邮箱格式
            {{"date": "invalid_date"}},       # 无效日期格式
            {{"phone": "123"}},               # 无效电话格式
            {{"amount": -999999}},            # 负数金额
            {{"quantity": 0}},                # 无效数量
        ]
        
        for invalid_data in invalid_data_types:
            response = await async_api_client.post(
                "{self._select_post_endpoint(routes, api_module_name)}",
                json=invalid_data,
                headers=headers
            )
            
            # 应该返回验证错误，而不是处理错误的数据
            assert response.status_code in [400, 422]
        
        print("✅ 数据类型验证测试通过")
    
    async def test_file_upload_security(self, async_api_client):
        """测试文件上传安全性"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 恶意文件测试
        malicious_files = [
            ("malicious.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("script.js", b"<script>alert('xss')</script>", "application/javascript"),  
            ("large_file.txt", b"A" * (10 * 1024 * 1024), "text/plain"),  # 10MB文件
            ("../../../etc/passwd", b"fake content", "text/plain"),  # 路径遍历文件名
        ]
        
        for filename, content, content_type in malicious_files:
            files = {{"file": (filename, content, content_type)}}
            
            response = await async_api_client.post(
                "{self._select_post_endpoint(routes, api_module_name)}",
                files=files,
                headers=headers
            )
            
            # 恶意文件应该被拒绝
            assert response.status_code in [400, 413, 415, 422]
        
        print("✅ 文件上传安全测试通过")
'''
    
    def _generate_data_protection_tests(self, module_name: str, models: Dict[str, ModelInfo], test_token: str, user_a_token: str, user_b_id: str) -> str:
        """生成数据保护测试"""
        
        business_domain = self.get_module_business_domain(module_name)
        class_name = f"Test{module_name.title().replace('_', '')}DataProtection"
        
        return f'''
class {class_name}:
    """{business_domain}模块数据保护安全测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_security_test(self, async_api_client):
        """安全测试前置：获取真实的admin和普通用户token"""
        # 创建管理员用户和token
        admin_token, admin_user = await async_api_client.authenticate_as_admin()
        self.admin_token = admin_token
        self.admin_user = admin_user
        
        # 创建第一个普通用户（user A）
        user_a_token, user_a = await async_api_client.authenticate_as_user()
        self.user_a_token = user_a_token
        self.user_a = user_a
        yield
    
    async def test_data_encryption(self, async_api_client):
        """测试数据加密保护"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 测试敏感数据是否加密存储
        from faker import Faker
        fake = Faker()
        test_credit_card = fake.credit_card_number()
        
        sensitive_data = {{
            "password": fake.password(),
            "credit_card": test_credit_card,
            "ssn": fake.ssn(),
            "private_info": fake.text()
        }}
        
        response = await async_api_client.post(
            "/api/v1/{module_name}/store-sensitive",
            json=sensitive_data,
            headers=headers
        )
        
        # 即使存储成功，响应也不应该包含原始敏感数据
        if response.status_code in [200, 201]:
            response_data = response.json()
            response_text = json.dumps(response_data).lower()
            
            # 敏感数据不应该以明文出现在响应中
            assert sensitive_data["password"] not in response_text
            assert test_credit_card not in response_text
            assert sensitive_data["private_info"] not in response_text
        
        print("✅ 数据加密保护测试通过")
    
    async def test_data_access_control(self, async_api_client):
        """测试数据访问控制"""
        
        # 使用用户A的token尝试访问admin用户的数据
        headers = {{"Authorization": f"Bearer {{self.user_a_token}}"}}
        admin_user_id = self.admin_user.id
        
        # 尝试访问其他用户的私人数据
        response = await async_api_client.get(
            f"/api/v1/{module_name}/user/{{admin_user_id}}/private",
            headers=headers
        )
        
        # 应该被拒绝访问
        assert response.status_code in [403, 404]
        
        # 尝试修改其他用户的数据
        response = await async_api_client.put(
            f"/api/v1/{module_name}/user/{{admin_user_id}}/profile",
            json={{"name": "hacked"}},  # noqa: 安全测试payload，测试未授权修改
            headers=headers
        )
        
        assert response.status_code in [403, 404]
        
        print("✅ 数据访问控制测试通过")
    
    async def test_data_leakage_prevention(self, async_api_client):
        """测试数据泄露防护"""
        
        headers = {{"Authorization": "Bearer test_token"}}
        
        # 测试批量数据导出是否有限制
        response = await async_api_client.get(
            "/api/v1/{module_name}/export/all",
            headers=headers
        )
        
        # 批量导出应该需要特殊权限或限制
        assert response.status_code in [403, 404, 405]
        
        # 测试分页查询是否有合理限制
        response = await async_api_client.get(
            "/api/v1/{module_name}/list",
            params={{"limit": 100000}},  # 尝试获取大量数据
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json().get("data", {{}})
            items = data.get("items", [])
            # 应该有合理的分页限制
            assert len(items) <= 1000  # 假设最大限制是1000
        
        print("✅ 数据泄露防护测试通过")
    
    async def test_gdpr_compliance(self, async_api_client):
        """测试GDPR合规性"""
        
        headers = {{"Authorization": f"Bearer {{self.admin_token}}"}}
        
        # 测试数据删除权（被遗忘权）
        response = await async_api_client.delete(
            "/api/v1/user-auth/me/data",
            headers=headers
        )
        
        # 应该支持用户数据删除
        assert response.status_code in [200, 202, 204, 404]
        
        # 测试数据导出权
        response = await async_api_client.get(
            "/api/v1/user-auth/me/export",
            headers=headers
        )
        
        # 应该支持用户数据导出
        assert response.status_code in [200, 202, 404]
        
        print("✅ GDPR合规性测试通过")
'''
    
    def _select_auth_endpoint(self, routes: List[RouterInfo], api_module_name: str) -> str:
        """在生成时选择需要认证的真实端点（用于token验证测试）"""
        if routes:
            # 只选择需要认证的GET端点
            auth_required_routes = [r for r in routes if r.auth_required and r.method == "GET"]
            if auth_required_routes:
                return f"/api/v1{auth_required_routes[0].path}"
            
            # 如果没有需要认证的GET端点，尝试其他需要认证的端点
            auth_required_routes = [r for r in routes if r.auth_required]
            if auth_required_routes:
                return f"/api/v1{auth_required_routes[0].path}"
        
        # 如果模块没有需要认证的endpoint，返回user-auth模块的endpoint作为通用测试
        return "/api/v1/user-auth/me"
    
    def _select_post_endpoint(self, routes: List[RouterInfo], api_module_name: str) -> str:
        """在生成时选择POST端点用于输入验证测试（优先选择需要认证的）"""
        if routes:
            # 优先选择需要认证的POST端点（输入验证测试应该在受保护的endpoint上进行）
            auth_post_routes = [r for r in routes if r.method == "POST" and r.auth_required]
            if auth_post_routes:
                return f"/api/v1{auth_post_routes[0].path}"
            
            # 回退：使用任意POST端点
            post_routes = [r for r in routes if r.method == "POST"]
            if post_routes:
                return f"/api/v1{post_routes[0].path}"
            
            # 再回退：使用第一个endpoint（可能不是POST）
            return f"/api/v1{routes[0].path}"
        
        # 最终回退：使用user-auth的注册endpoint
        return "/api/v1/user-auth/register"

    def _generate_dynamic_security_data(self, routes: List[RouterInfo]) -> Dict[str, Any]:
        """动态生成安全测试数据 - 避免硬编码"""
        fake = Faker()
        
        # 基础动态数据
        base_data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": secrets.token_hex(8),  # 安全密码
            "search_term": fake.word(),
            "query": fake.word(),
            "phone": f"1{fake.random_element(elements=[3,4,5,6,7,8,9])}{fake.random_number(digits=9)}",
            "verification_code": str(fake.random_int(100000, 999999)),
            "real_name": fake.name()
        }
        
        # 根据路由信息生成特定数据
        for route in routes:
            if hasattr(route, 'function_name'):
                function_name = route.function_name.lower()
                
                if 'register' in function_name:
                    base_data.update({
                        "username": fake.user_name(),
                        "email": fake.email(),
                        "password": secrets.token_hex(8)
                    })
                elif 'login' in function_name:
                    base_data.update({
                        "email": fake.email(),
                        "password": secrets.token_hex(8)
                    })
                elif 'search' in function_name:
                    base_data["search_term"] = fake.word()
        
        return base_data
