"""
会员系统模块 - API集成测试
严格遵循testing-standards.md和MASTER文档要求
测试实际的API端点，确保100%使用真实路径和参数
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
from decimal import Decimal

# 导入实际的应用和依赖
from app.main import app
from app.core.database import get_db
from app.core.auth import get_current_user
from app.modules.user_auth.models import User
from app.modules.member_system.models import (
    MemberProfile, MemberLevel, MemberPoint, PointTransaction
)


class TestMemberSystemAPIIntegration:
    """
    会员系统API集成测试
    
    测试范围：
    - 真实API端点的完整流程测试
    - 认证和权限验证
    - 请求响应格式验证
    
    API端点验证：严格使用router.py中定义的实际路径
    - /api/v1/member-system/profile (GET/PUT)
    - /api/v1/member-system/register (POST)
    - /api/v1/member-system/points/earn (POST)
    - /api/v1/member-system/points/use (POST)
    - /api/v1/member-system/benefits/available (GET)
    """

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    def mock_db_session(self):
        """模拟数据库会话"""
        return Mock()

    @pytest.fixture
    def mock_current_user(self):
        """模拟当前用户"""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            role="user",
            status="active",
            is_active=True
        )

    @pytest.fixture
    def sample_member_data(self):
        """测试会员数据 - 使用实际字段名"""
        return {
            "member_code": "M202509180001",
            "user_id": 1,
            "level_id": 1,
            "total_spent": "0.00",
            "status": 1
        }

    def test_get_member_profile_success(self, client, mock_db_session, mock_current_user):
        """
        测试GET /api/v1/member-system/profile - 成功获取会员信息
        
        验证：
        - 使用实际的API路径
        - 正确的响应格式
        - 实际字段名的返回
        """
        # 模拟依赖注入
        def override_get_db():
            return mock_db_session

        def override_get_current_user():
            return mock_current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 模拟会员服务返回 - 符合 MemberWithDetails schema
        mock_member_info = {
            "member_id": "1",
            "user_id": 1,
            "level": {
                "level_id": 1,
                "level_name": "注册会员",
                "level_code": "BASIC",
                "discount_rate": 1.0,
                "point_multiplier": 1.0
            },
            "points": {
                "total_points": 200,
                "available_points": 100,
                "frozen_points": 0,
                "expiring_points": 0,
                "expiring_date": None
            },
            "statistics": {
                "total_spent": 150.0,
                "total_orders": 5,
                "join_date": "2025-09-18",
                "last_active": None
            },
            "benefits": {
                "free_shipping": False,
                "birthday_gift": False,
                "priority_service": False,
                "exclusive_events": False,
                "points_multiplier": False,
                "custom_service": False
            }
        }

        with patch('app.modules.member_system.service.MemberService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_member_profile.return_value = mock_member_info

            # 执行API请求 - 使用实际的API路径
            response = client.get("/api/v1/member-system/profile")

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构和字段名 - 符合 MemberWithDetails schema
            assert "data" in data  # APIResponse结构
            member_data = data["data"]
            
            assert "member_id" in member_data
            assert "user_id" in member_data
            assert "level" in member_data
            assert "points" in member_data
            assert "statistics" in member_data
            assert "benefits" in member_data
            
            # 验证具体字段值
            assert member_data["member_id"] == "1"
            assert member_data["user_id"] == 1
            assert member_data["level"]["level_name"] == "注册会员"
            assert member_data["points"]["total_points"] == 200
            assert member_data["points"]["available_points"] == 100

        # 清理依赖覆盖
        app.dependency_overrides.clear()

    def test_post_member_register_success(self, client, mock_db_session, mock_current_user):
        """
        测试POST /api/v1/member-system/register - 成功注册会员
        
        验证：
        - 使用实际的API路径
        - 正确的请求体格式
        - 成功响应处理
        """
        # 模拟依赖注入
        def override_get_db():
            return mock_db_session

        def override_get_current_user():
            return mock_current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 准备请求数据 - 使用实际字段名
        register_data = {
            "birthday": "1990-01-01",
            "preferences": {
                "notification": True,
                "marketing": False
            }
        }

        # 模拟会员服务返回
        mock_member = Mock()
        mock_member.member_code = "M202509180001"
        mock_member.level_id = 1

        with patch('app.modules.member_system.service.MemberService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_member.return_value = mock_member

            # 执行API请求 - 使用实际的API路径
            response = client.post(
                "/api/v1/member-system/register",
                json=register_data
            )

            # 验证响应
            assert response.status_code == 201
            data = response.json()
            
            # 验证调用参数 - 确保字段名正确传递
            mock_service.create_member.assert_called_once_with(1, register_data)

        # 清理依赖覆盖
        app.dependency_overrides.clear()

    def test_post_points_earn_success(self, client, mock_db_session, mock_current_user):
        """
        测试POST /api/v1/member-system/points/earn - 成功获得积分
        
        验证：
        - 使用实际的API路径
        - 正确的请求体格式
        - 积分交易记录返回
        """
        # 模拟依赖注入
        def override_get_db():
            return mock_db_session

        def override_get_current_user():
            return mock_current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 准备请求数据 - 使用实际字段名
        earn_data = {
            "points": 50,
            "reference_type": "order",
            "reference_id": "order_123",
            "description": "购物获得积分"
        }

        # 模拟积分服务返回 - 使用实际字段名
        mock_transaction = Mock()
        mock_transaction.id = 1
        mock_transaction.user_id = 1
        mock_transaction.transaction_type = "earn"
        mock_transaction.points_change = 50
        mock_transaction.reference_id = "order_123"
        mock_transaction.status = "completed"

        with patch('app.modules.member_system.service.PointService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.earn_points.return_value = mock_transaction

            # 执行API请求 - 使用实际的API路径
            response = client.post(
                "/api/v1/member-system/points/earn",
                json=earn_data
            )

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            
            # 验证调用参数 - 使用实际字段名
            mock_service.earn_points.assert_called_once_with(
                user_id=1,
                points=50,
                reference_type="order",
                reference_id="order_123",
                description="购物获得积分"
            )

        # 清理依赖覆盖
        app.dependency_overrides.clear()

    def test_post_points_use_success(self, client, mock_db_session, mock_current_user):
        """
        测试POST /api/v1/member-system/points/use - 成功使用积分
        
        验证：
        - 使用实际的API路径
        - 正确处理积分使用请求
        - 返回交易记录
        """
        # 模拟依赖注入
        def override_get_db():
            return mock_db_session

        def override_get_current_user():
            return mock_current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 准备请求数据 - 使用实际字段名
        use_data = {
            "points": 30,
            "reference_type": "order",
            "reference_id": "order_456",
            "description": "订单抵扣"
        }

        # 模拟积分服务返回
        mock_transaction = Mock()
        mock_transaction.id = 2
        mock_transaction.user_id = 1
        mock_transaction.transaction_type = "use"
        mock_transaction.points_change = -30
        mock_transaction.reference_id = "order_456"
        mock_transaction.status = "completed"

        with patch('app.modules.member_system.service.PointService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.use_points.return_value = mock_transaction

            # 执行API请求 - 使用实际的API路径
            response = client.post(
                "/api/v1/member-system/points/use",
                json=use_data
            )

            # 验证响应
            assert response.status_code == 200
            
            # 验证服务调用 - 使用实际参数名
            mock_service.use_points.assert_called_once_with(
                user_id=1,
                points=30,
                reference_type="order",
                reference_id="order_456",
                description="订单抵扣"
            )

        # 清理依赖覆盖
        app.dependency_overrides.clear()

    def test_get_benefits_available_success(self, client, mock_db_session, mock_current_user):
        """
        测试GET /api/v1/member-system/benefits/available - 成功获取可用权益
        
        验证：
        - 使用实际的API路径
        - 正确的权益信息返回
        """
        # 模拟依赖注入
        def override_get_db():
            return mock_db_session

        def override_get_current_user():
            return mock_current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 模拟权益服务返回
        mock_benefits = {
            "benefits": {
                "point_multiplier": 1.2,
                "free_shipping_threshold": 79,
                "birthday_gift": True
            },
            "level": "银牌会员",
            "discount_rate": 0.95
        }

        with patch('app.modules.member_system.service.BenefitService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_available_benefits.return_value = mock_benefits

            # 执行API请求 - 使用实际的API路径
            response = client.get("/api/v1/member-system/benefits/available")

            # 验证响应
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应结构 - 使用实际字段名
            assert "benefits" in data
            assert "level" in data
            assert "discount_rate" in data
            assert data["level"] == "银牌会员"
            assert data["discount_rate"] == 0.95

        # 清理依赖覆盖
        app.dependency_overrides.clear()

    def test_api_authentication_required(self, client):
        """
        测试API认证要求
        
        验证：
        - 未认证请求被正确拒绝
        - 返回适当的认证错误
        """
        # 测试需要认证的端点 - 使用实际API路径
        protected_endpoints = [
            ("/api/v1/member-system/profile", "GET"),
            ("/api/v1/member-system/register", "POST"),
            ("/api/v1/member-system/points/earn", "POST"),
            ("/api/v1/member-system/points/use", "POST"),
            ("/api/v1/member-system/benefits/available", "GET")
        ]

        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            # 验证返回认证错误
            assert response.status_code in [401, 403], f"端点 {endpoint} 应该需要认证"

    def test_api_error_handling(self, client, mock_db_session, mock_current_user):
        """
        测试API错误处理
        
        验证：
        - 服务层异常的正确处理
        - 适当的HTTP状态码返回
        """
        # 模拟依赖注入
        def override_get_db():
            return mock_db_session

        def override_get_current_user():
            return mock_current_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        # 模拟服务层抛出异常
        with patch('app.modules.member_system.service.MemberService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_member_profile.side_effect = Exception("Database error")

            # 执行API请求
            response = client.get("/api/v1/member-system/profile")

            # 验证错误响应
            assert response.status_code == 500

        # 清理依赖覆盖
        app.dependency_overrides.clear()


class TestMemberSystemAPIValidation:
    """
    会员系统API请求验证测试
    """

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    def test_points_earn_invalid_data(self, client):
        """
        测试积分获得API的数据验证
        
        验证：
        - 无效请求数据的正确处理
        - 参数验证错误的返回
        """
        # 模拟认证通过
        def override_get_current_user():
            return User(id=1, username="test")

        app.dependency_overrides[get_current_user] = override_get_current_user

        # 测试无效数据
        invalid_data_cases = [
            {},  # 空数据
            {"points": -10},  # 负数积分
            {"points": "abc"},  # 非数字积分
            {"points": 50},  # 缺少必需字段
        ]

        for invalid_data in invalid_data_cases:
            response = client.post(
                "/api/v1/member-system/points/earn",
                json=invalid_data
            )
            
            # 验证返回验证错误
            assert response.status_code in [400, 422]

        # 清理依赖覆盖
        app.dependency_overrides.clear()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])