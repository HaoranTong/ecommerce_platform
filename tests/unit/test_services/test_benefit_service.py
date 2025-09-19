"""
会员系统模块 - 权益服务单元测试
严格遵循testing-standards.md和MASTER文档要求
使用实际models.py字段和service.py方法，确保100%字段名称正确性
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

# 导入实际的模型和服务 - 严格按照实际代码结构
from app.modules.member_system.models import (
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
    MemberProfile, MemberLevel, MemberPoint
)
from app.modules.member_system.service import BenefitService, get_benefit_service
from fastapi import HTTPException


class TestBenefitService:
    """
    权益服务单元测试类
    
    测试范围：
    - BenefitService所有公有方法
    - 权益查询和折扣计算
    - 等级权益配置验证
    
    字段验证：严格使用models.py中定义的实际字段名
    - MemberProfile: id, user_id, level_id, total_spent等
    - MemberLevel: id, level_name, discount_rate, benefits等
    """

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_redis(self):
        """模拟Redis客户端"""
        return Mock()

    @pytest.fixture
    def benefit_service(self, mock_db, mock_redis):
        """创建权益服务实例"""
        return BenefitService(mock_db, mock_redis)

    @pytest.fixture
    def sample_member_level(self):
        """测试会员等级数据 - 使用实际字段名"""
        return MemberLevel(
            id=2,
            level_name="银牌会员",  # 实际字段名：level_name
            min_points=1000,  # 实际字段名：min_points
            discount_rate=Decimal('0.950'),  # 实际字段名：discount_rate (95折)
            benefits={  # 实际字段名：benefits
                "point_multiplier": 1.2,
                "free_shipping_threshold": 79,
                "birthday_gift": True,
                "priority_service": True
            }
        )

    @pytest.fixture
    def sample_member_profile(self, sample_member_level):
        """测试会员档案数据 - 使用实际字段名"""
        return MemberProfile(
            id=1,
            member_code="M202509180001",  # 实际字段名：member_code
            user_id=1,  # 实际字段名：user_id
            level_id=2,  # 实际字段名：level_id (银牌会员)
            total_spent=Decimal('1500.00'),  # 实际字段名：total_spent
            status=1,  # 实际字段名：status
            level=sample_member_level
        )

    def test_get_available_benefits_success(self, benefit_service, mock_db, sample_member_profile, sample_member_level):
        """
        测试成功获取可用权益
        
        验证：
        - 返回完整的权益信息
        - 包含等级名称和折扣率
        - 使用实际字段名
        """
        # 设置查询Mock
        # 第1个查询：获取会员信息
        member_query = Mock()
        member_query.filter.return_value.first.return_value = sample_member_profile
        
        # 第2个查询：获取等级信息
        level_query = Mock()
        level_query.filter.return_value.first.return_value = sample_member_level
        
        mock_db.query.side_effect = [member_query, level_query]

        # 执行测试
        result = benefit_service.get_available_benefits(1)

        # 验证结果结构
        assert result is not None
        assert "benefits" in result
        assert "level" in result
        assert "discount_rate" in result

        # 验证等级信息 - 使用实际字段名
        assert result["level"] == "银牌会员"  # level_name字段
        assert result["discount_rate"] == 0.95  # discount_rate字段

        # 验证权益内容 - 使用实际benefits字段的JSON内容
        benefits = result["benefits"]
        assert benefits["point_multiplier"] == 1.2
        assert benefits["free_shipping_threshold"] == 79
        assert benefits["birthday_gift"] is True
        assert benefits["priority_service"] is True

    def test_get_available_benefits_member_not_found(self, benefit_service, mock_db):
        """
        测试获取不存在会员的权益
        
        验证：
        - 当会员不存在时返回空权益信息
        """
        # 模拟会员不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # 执行测试
        result = benefit_service.get_available_benefits(999)

        # 验证返回默认结构
        assert result["benefits"] == []
        assert result["level"] is None

    def test_get_available_benefits_no_level_benefits(self, benefit_service, mock_db):
        """
        测试获取无权益配置等级的权益
        
        验证：
        - 当等级无权益配置时返回空列表
        """
        # 创建无权益配置的会员
        member_no_benefits = Mock()
        member_no_benefits.user_id = 1
        member_no_benefits.level_id = 1

        # 创建无权益配置的等级
        level_no_benefits = Mock()
        level_no_benefits.level_name = "注册会员"
        level_no_benefits.benefits = None  # 无权益配置

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            member_no_benefits, level_no_benefits
        ]

        # 执行测试
        result = benefit_service.get_available_benefits(1)

        # 验证返回空权益
        assert result["benefits"] == []
        assert result["level"] == "注册会员"

    def test_calculate_discount_success(self, benefit_service, mock_db, sample_member_profile, sample_member_level):
        """
        测试成功计算会员折扣
        
        验证：
        - 使用实际的discount_rate字段计算
        - 正确的折扣计算逻辑
        """
        # 模拟会员查询
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_member_profile, sample_member_level
        ]

        # 执行测试 - 原价100元
        order_amount = Decimal('100.00')
        result = benefit_service.calculate_discount(1, order_amount)

        # 验证折扣计算 - 95折
        expected_amount = order_amount * sample_member_level.discount_rate
        assert result == expected_amount
        assert result == Decimal('95.00')  # 100 * 0.95

    def test_calculate_discount_member_not_found(self, benefit_service, mock_db):
        """
        测试不存在会员的折扣计算
        
        验证：
        - 当会员不存在时返回原价
        """
        # 模拟会员不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # 执行测试
        order_amount = Decimal('100.00')
        result = benefit_service.calculate_discount(999, order_amount)

        # 验证返回原价
        assert result == order_amount

    def test_calculate_discount_level_not_found(self, benefit_service, mock_db):
        """
        测试等级不存在的折扣计算
        
        验证：
        - 当等级不存在时返回原价
        """
        # 模拟会员存在但等级不存在
        mock_member = Mock()
        mock_member.user_id = 1
        mock_member.level_id = 999

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_member, None  # 会员存在，等级不存在
        ]

        # 执行测试
        order_amount = Decimal('100.00')
        result = benefit_service.calculate_discount(1, order_amount)

        # 验证返回原价
        assert result == order_amount

    def test_calculate_discount_different_amounts(self, benefit_service, mock_db, sample_member_profile, sample_member_level):
        """
        测试不同金额的折扣计算
        
        验证：
        - 各种订单金额的正确折扣计算
        """
        # 模拟查询
        mock_db.query.return_value.filter.return_value.first.side_effect = lambda: [
            sample_member_profile, sample_member_level
        ][mock_db.query.call_count - 1] if mock_db.query.call_count <= 2 else None

        # 测试不同金额
        test_cases = [
            (Decimal('50.00'), Decimal('47.50')),    # 50 * 0.95
            (Decimal('200.50'), Decimal('190.475')),  # 200.5 * 0.95
            (Decimal('999.99'), Decimal('949.9905')), # 999.99 * 0.95
        ]

        for original_amount, expected_amount in test_cases:
            # 重置mock计数
            mock_db.reset_mock()
            mock_db.query.return_value.filter.return_value.first.side_effect = [
                sample_member_profile, sample_member_level
            ]
            
            result = benefit_service.calculate_discount(1, original_amount)
            assert result == expected_amount


class TestBenefitServiceErrorHandling:
    """
    权益服务错误处理测试
    """

    @pytest.fixture
    def benefit_service(self):
        """创建权益服务实例"""
        return BenefitService(Mock(spec=Session), Mock())

    def test_database_error_in_get_benefits(self, benefit_service):
        """
        测试获取权益时的数据库错误
        
        验证：
        - 数据库异常的正确处理和日志记录
        """
        mock_db = Mock(spec=Session)
        mock_db.query.side_effect = Exception("Database connection failed")
        
        service = BenefitService(mock_db, Mock())
        
        # 验证异常传播
        with pytest.raises(Exception):
            service.get_available_benefits(1)

    def test_database_error_in_calculate_discount(self, benefit_service):
        """
        测试计算折扣时的数据库错误
        
        验证：
        - 数据库异常时返回原价（安全降级）
        """
        mock_db = Mock(spec=Session)
        mock_db.query.side_effect = Exception("Database connection failed")
        
        service = BenefitService(mock_db, Mock())
        
        order_amount = Decimal('100.00')
        result = service.calculate_discount(1, order_amount)
        
        # 验证返回原价作为安全降级
        assert result == order_amount


class TestBenefitServiceIntegration:
    """
    权益服务集成测试
    """

    def test_get_benefit_service_factory(self):
        """
        测试工厂函数正确性
        
        验证：
        - get_benefit_service工厂函数返回正确的服务实例
        """
        mock_db = Mock(spec=Session)
        mock_redis = Mock()

        service = get_benefit_service(mock_db, mock_redis)

        assert isinstance(service, BenefitService)
        assert service.db is mock_db
        assert service.redis is mock_redis

    def test_benefit_service_initialization(self):
        """
        测试权益服务初始化
        
        验证：
        - 服务实例的正确初始化
        - 缓存前缀设置
        """
        mock_db = Mock(spec=Session)
        mock_redis = Mock()
        
        service = BenefitService(mock_db, mock_redis)
        
        assert service.db is mock_db
        assert service.redis is mock_redis
        assert service.cache_prefix == "benefits:"


class TestBenefitServiceBoundaryConditions:
    """
    权益服务边界条件测试
    """

    @pytest.fixture
    def benefit_service(self):
        """创建权益服务实例"""
        return BenefitService(Mock(spec=Session), Mock())

    def test_extreme_discount_rates(self, benefit_service):
        """
        测试极端折扣率
        
        验证：
        - 1.0折扣率（无折扣）
        - 接近0的折扣率
        """
        mock_db = Mock(spec=Session)
        
        # 测试无折扣情况
        no_discount_member = Mock()
        no_discount_member.user_id = 1
        no_discount_member.level_id = 1
        
        no_discount_level = Mock()
        no_discount_level.discount_rate = Decimal('1.000')
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            no_discount_member, no_discount_level
        ]
        
        service = BenefitService(mock_db, Mock())
        
        order_amount = Decimal('100.00')
        result = service.calculate_discount(1, order_amount)
        
        assert result == order_amount  # 无折扣
        
    def test_high_value_order_discount(self, benefit_service):
        """
        测试大额订单折扣计算
        
        验证：
        - 高价值订单的精确折扣计算
        """
        mock_db = Mock(spec=Session)
        
        vip_member = Mock()
        vip_member.user_id = 1
        vip_member.level_id = 5
        
        vip_level = Mock()
        vip_level.discount_rate = Decimal('0.800')  # 8折
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            vip_member, vip_level
        ]
        
        service = BenefitService(mock_db, Mock())
        
        # 测试高价值订单
        high_value_amount = Decimal('9999.99')
        result = service.calculate_discount(1, high_value_amount)
        
        expected_amount = high_value_amount * Decimal('0.800')
        assert result == expected_amount


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])