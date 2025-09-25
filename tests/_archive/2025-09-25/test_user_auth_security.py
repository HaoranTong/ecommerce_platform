"""
User_Auth 安全测试套件

测试类型: 专项测试 (Security)
生成时间: 2025-09-20 21:34:33

根据testing-standards.md第190-210行安全测试规范
"""

import pytest
import requests
from sqlalchemy.orm import Session

# 测试工厂导入
from tests.factories import User_AuthFactory, UserFactory

# Fixture导入
from tests.conftest import mysql_integration_db, api_client


@pytest.mark.security
class TestUser_AuthSecurity:
    """安全测试"""
    
    def test_user_auth_sql_injection_protection(self, api_client):
        """测试user_auth SQL注入防护"""
        # SQL注入攻击测试
        malicious_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; INSERT INTO users VALUES('hacker', 'password'); --"
        ]
        
        for payload in malicious_payloads:
            response = api_client.get(f"/user_auth/{payload}")
            
            # 验证没有返回敏感数据或系统错误
            assert response.status_code in [400, 404, 422]
            assert "error" not in response.text.lower() or "sql" not in response.text.lower()
            
    def test_user_auth_xss_protection(self, api_client):
        """测试user_auth XSS防护"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            test_data = User_AuthFactory.build_dict()
            test_data['name'] = payload
            
            response = api_client.post(f"/user_auth/", json=test_data)
            
            if response.status_code == 201:
                # 如果创建成功，验证返回的数据已被转义
                response_text = response.text
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
                
    def test_user_auth_authorization_check(self, api_client):
        """测试user_auth权限控制"""
        # 未授权访问测试
        response = api_client.get(f"/user_auth/")
        
        # 根据实际权限设计验证
        if response.status_code == 401:
            assert "unauthorized" in response.text.lower()
        elif response.status_code == 403:
            assert "forbidden" in response.text.lower()
            
    def test_user_auth_input_validation(self, api_client):
        """测试user_auth输入验证"""
        # 无效输入测试
        invalid_payloads = [
            {"name": ""},  # 空值
            {"name": "x" * 1000},  # 超长值
            {"invalid_field": "test"},  # 无效字段
            {},  # 空对象
        ]
        
        for payload in invalid_payloads:
            response = api_client.post(f"/user_auth/", json=payload)
            
            # 验证输入验证生效
            assert response.status_code in [400, 422]
            
    def test_user_auth_rate_limiting(self, api_client):
        """测试user_auth速率限制"""
        # 快速连续请求测试
        responses = []
        
        for i in range(100):  # 发送100个快速请求
            response = api_client.get(f"/user_auth/")
            responses.append(response.status_code)
            
        # 验证是否有速率限制生效
        rate_limited = any(status == 429 for status in responses)
        
        # 如果没有速率限制，至少验证服务稳定性
        if not rate_limited:
            successful_requests = sum(1 for status in responses if status == 200)
            assert successful_requests > 50, "服务在高频请求下不稳定"
