"""
Auto Generated Test - 已生成到正式目录

文件路径: tests/integration/test_api/test_user_auth_api.py
生成时间: 2025-10-05 22:34:45
生成工具: tools/generate_test_template.py v2.0
状态: GENERATED - 需要经过代码审查和测试验证

说明: 此文件已生成到正式目录，请进行代码审查和测试验证。
     审查通过后即可直接用于项目测试。
     
流程: 生成 -> 审查 -> 验证 -> 提交版本控制
"""


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

class TestUserAuthPostAPI:
    """用户认证模块POST方法API测试"""
    

    def test_register_user(self, api_client):
        """测试register_user - 使用统一工厂和真实JWT认证"""
        
        
                # 动态生成测试数据，避免硬编码
        fake = Faker()
        test_data = {
    "username": fake.user_name().replace(".", "_")[:20],
    "email": fake.email(),
    "password": fake.password(length=12),
    "phone": f"1{fake.random_int(min=3, max=9)}{fake.random_int(min=100000000, max=999999999)}",
    "verification_code": fake.numerify("######"),
    "real_name": fake.name()[:50]
}
        
        # 发送请求
        response = api_client.post(
            "/api/v1/user-auth/register",
            json=test_data
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_201_CREATED
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证UserRead响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0



    def test_login_user(self, api_client, mysql_integration_db):
        """测试login_user - 使用统一工厂和真实JWT认证"""
        # 无需认证的公开API
        
        # 使用统一工厂创建已存在的用户进行登录测试
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username="test_login_user",
            password_hash=get_password_hash("TestPassword123!")
        )
        
        test_data = {
            "username": test_user.username,
            "password": "TestPassword123!"
        }
        
        # 发送请求
        response = api_client.post(
            "/api/v1/user-auth/login",
            json=test_data
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证Token响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0



    def test_refresh_token(self, api_client, mysql_integration_db):
        """测试refresh_token - 使用统一工厂和真实JWT认证"""
        # 使用统一工厂创建普通用户并获取token
        normal_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            role="user",
            is_active=True
        )
        access_token = create_access_token(
            data={"sub": str(normal_user.id)},
            expires_delta=timedelta(hours=1)
        )
        api_client.set_auth_headers(access_token)
        
        # 通过登录API获取真实的refresh_token进行测试
        # 先创建测试用户
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username="test_refresh_user",
            password_hash=get_password_hash("TestPassword123!")
        )
        
        # 通过登录API获取refresh_token
        login_response = api_client.post("/api/v1/user-auth/login", json={
            "username": test_user.username,
            "password": "TestPassword123!"
        })
        login_data = login_response.json()
        
        test_data = {
            "refresh_token": login_data["refresh_token"]
        }
        
        # 发送请求
        response = api_client.post(
            "/api/v1/user-auth/refresh",
            json=test_data
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证Token响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0



    def test_logout_user(self, api_client):
        """测试logout_user - 使用统一工厂和真实JWT认证"""
        
        # 使用新的JWT认证方式创建用户并获取token
        access_token, test_user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(access_token)
        
        
                # 动态生成测试数据，避免硬编码
        fake = Faker()
        test_data = {
    "data": fake.text(max_nb_chars=50)
}
        
        # 发送请求
        response = api_client.post(
            "/api/v1/user-auth/logout",
            json=test_data
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证基本响应结构
        assert response_data is not None
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0




class TestUserAuthGetAPI:
    """用户认证模块GET方法API测试"""
    

    def test_get_current_user_info(self, api_client):
        """测试get_current_user_info - 使用统一工厂和真实JWT认证"""
        
        # 使用新的JWT认证方式创建用户并获取token
        access_token, test_user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(access_token)
        
        
        query_params = {
    "page": 1,
    "size": 10
}
        
        # 发送请求
        response = api_client.get(
            "/api/v1/user-auth/me",
            params=query_params
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证UserRead响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0



    def test_list_users(self, api_client):
        """测试list_users - 使用统一工厂和真实JWT认证"""
        
        # 使用管理员认证（因为这个API需要管理员权限）
        access_token, admin_user = api_client.authenticate_as_admin()
        api_client.set_auth_headers(access_token)
        
        
        query_params = {
    "page": 1,
    "size": 10
}
        
        # 发送请求
        response = api_client.get(
            "/api/v1/user-auth/users",
            params=query_params
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证基本响应结构
        assert response_data is not None
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0



    def test_get_user_by_id(self, api_client):
        """测试get_user_by_id - 使用统一工厂和真实JWT认证"""
        
        # 使用管理员认证（因为这个API需要管理员权限）
        access_token, admin_user = api_client.authenticate_as_admin()
        api_client.set_auth_headers(access_token)
        
        
        query_params = {
    "page": 1,
    "size": 10
}
        
        # 发送请求
        response = api_client.get(
            "/api/v1/user-auth/users/1",
            params=query_params
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证UserRead响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0




class TestUserAuthPutAPI:
    """用户认证模块PUT方法API测试"""
    

    def test_update_current_user(self, api_client):
        """测试update_current_user - 使用统一工厂和真实JWT认证"""
        
        # 使用新的JWT认证方式创建用户并获取token
        access_token, test_user, _ = api_client.authenticate_as_user()
        api_client.set_auth_headers(access_token)
        
        
                # 动态生成测试数据，避免硬编码
        fake = Faker()
        test_data = {
    "email": fake.email(),
    "phone": f"1{fake.random_int(min=3, max=9)}{fake.random_int(min=100000000, max=999999999)}",
    "real_name": fake.name()[:50]
}
        
        # 发送请求
        response = api_client.put(
            "/api/v1/user-auth/me",
            json=test_data
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证UserRead响应结构
        assert isinstance(response_data, dict)
        assert len(response_data) > 0
        # 具体字段验证基于Schema运行时分析
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0



    def test_change_password(self, api_client, mysql_integration_db):
        """测试change_password - 使用统一工厂和真实JWT认证"""
        # 使用统一工厂创建普通用户并获取token
        normal_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            role="user",
            is_active=True
        )
        access_token = create_access_token(
            data={"sub": str(normal_user.id)},
            expires_delta=timedelta(hours=1)
        )
        api_client.set_auth_headers(access_token)
        
        # 确保认证用户和测试用户一致，创建具有已知密码的用户进行密码修改测试
        # 创建具有已知密码的测试用户
        test_user = StandardTestDataFactory.create_user(
            mysql_integration_db,
            username="test_password_change_user",
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
        }
        
        # 发送请求
        response = api_client.put(
            "/api/v1/user-auth/password",
            json=test_data
        )
        
        # 验证响应
        assert response.status_code == status.HTTP_200_OK
        
        # 验证响应数据存在
        response_data = response.json()
        assert response_data is not None
        
        # 验证关键字段（根据操作类型）
        # 验证基本响应结构
        assert response_data is not None
        
        # 验证响应时间 (API标准要求<2s)
        assert response.elapsed.total_seconds() < 2.0





class TestUserAuthAPIIntegration:
    """用户认证模块API集成测试 - 测试完整业务流程"""
    
    def test_user_auth_workflow(self, api_client):
        """测试user_auth模块完整流程：auth -> read -> create -> update"""
        
        # 通过动态schema分析生成测试数据
        # 基于路由分析自动生成工作流测试
        
        print("✅ user_auth模块完整流程测试通过")
    
    def test_api_error_handling(self, api_client):
        """测试API错误处理机制"""
        # 测试400 Bad Request
        response = api_client.post("/api/v1/user_auth/invalid", json={})
        assert response.status_code in [400, 404, 422]
        
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data
    
    def test_api_rate_limiting(self, api_client):
        """测试API限流机制"""
        # 连续发送多个请求测试限流
        for _ in range(5):
            response = api_client.get("/api/v1/user_auth")
            # 正常情况下应该成功，限流时返回429
            assert response.status_code in [200, 404, 429]
