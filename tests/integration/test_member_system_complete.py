"""
会员系统模块 - 完整集成测试

测试会员系统与其他模块的集成，包括：
- 会员档案创建与用户关联
- 积分系统的完整流程测试
- 会员等级管理和升级机制
- 优惠券和折扣计算

遵循 testing-standards.md 要求，使用 MySQL 测试数据库
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.modules.member_system.models import MemberLevel, MemberProfile, PointTransaction, MemberPoint
from app.modules.user_auth.models import User


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_user(integration_test_db: Session):
    """创建测试用户"""
    unique_suffix = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique_suffix}",
        email=f"test_{unique_suffix}@example.com", 
        password_hash="hashed_password_here",
        phone=f"138{unique_suffix[:8]}"
    )
    integration_test_db.add(user)
    integration_test_db.commit()
    integration_test_db.refresh(user)
    return user


@pytest.fixture
def test_member_level(integration_test_db: Session):
    """创建测试会员等级"""
    unique_suffix = str(uuid.uuid4())[:8]
    member_level = MemberLevel(
        level_name=f"VIP等级_{unique_suffix}",
        min_points=1000,
        discount_rate=Decimal('0.9'),
        benefits={'free_shipping': True, 'birthday_discount': 0.1}
    )
    integration_test_db.add(member_level)
    integration_test_db.commit()
    integration_test_db.refresh(member_level)
    return member_level


class TestMemberSystemIntegration:
    """会员系统集成测试"""
    
    @pytest.mark.integration
    def test_create_member_profile(self, integration_test_db: Session, test_user, test_member_level):
        """测试创建会员档案"""
        # 创建会员档案
        from datetime import datetime
        today = datetime.now()
        member_code = f"M{today.strftime('%Y%m%d')}0001"
        
        member_profile = MemberProfile(
            member_code=member_code,
            user_id=test_user.id,
            level_id=test_member_level.id,
            total_spent=Decimal('0.00'),
            status=1,  # ACTIVE
            join_date=date.today()
        )
        integration_test_db.add(member_profile)
        integration_test_db.commit()
        integration_test_db.refresh(member_profile)
        
        # 验证会员档案
        assert member_profile.id is not None
        assert member_profile.user_id == test_user.id
        assert member_profile.level_id == test_member_level.id
        assert member_profile.total_spent == Decimal('0.00')
        assert member_profile.status == 1
        assert member_profile.member_code.startswith('M')
        assert len(member_profile.member_code) == 13
        
    @pytest.mark.integration
    def test_member_points_system(self, integration_test_db: Session, test_member_level):
        """测试会员积分系统"""
        # 创建专用测试用户
        unique_suffix = str(uuid.uuid4())[:8]
        test_user2 = User(
            username=f"member_test_user_{unique_suffix}",
            email=f"member_{unique_suffix}@test.com",
            password_hash="hashed_test_password",
            real_name=f"会员测试用户_{unique_suffix}",
            phone=f"139{unique_suffix[:8]}"
        )
        integration_test_db.add(test_user2)
        integration_test_db.commit()
        integration_test_db.refresh(test_user2)
        
        # 删除可能存在的会员档案（数据清理）
        integration_test_db.query(MemberProfile).filter(
            MemberProfile.user_id == test_user2.id
        ).delete()
        integration_test_db.commit()
        
        # 创建会员档案
        from datetime import datetime
        today = datetime.now()
        member_code = f"M{today.strftime('%Y%m%d')}{unique_suffix[:4]}"
        
        member_profile = MemberProfile(
            member_code=member_code,
            user_id=test_user2.id,
            level_id=test_member_level.id,
            total_spent=Decimal('0.00'),
            status=1,
            join_date=date.today()
        )
        integration_test_db.add(member_profile)
        integration_test_db.commit()
        
        # 创建积分记录
        member_point = MemberPoint(
            user_id=test_user2.id,
            level_id=test_member_level.id,
            current_points=100,
            total_earned=100,
            total_used=0
        )
        integration_test_db.add(member_point)
        integration_test_db.commit()
        integration_test_db.refresh(member_point)
        
        # 验证积分记录
        assert member_point.user_id == test_user2.id
        assert member_point.current_points == 100
        assert member_point.total_earned == 100
        assert member_point.total_used == 0
        
    @pytest.mark.integration
    def test_point_transactions(self, integration_test_db: Session):
        """测试积分交易记录"""
        # 创建专用测试用户
        unique_suffix = str(uuid.uuid4())[:8]
        test_user_tx = User(
            username=f"tx_test_user_{unique_suffix}",
            email=f"tx_{unique_suffix}@test.com",
            password_hash="hashed_test_password",
            real_name=f"交易测试用户_{unique_suffix}",
            phone=f"135{unique_suffix[:8]}"
        )
        integration_test_db.add(test_user_tx)
        integration_test_db.commit()
        integration_test_db.refresh(test_user_tx)
        
        # 创建积分交易记录 - 赚取积分
        earn_transaction = PointTransaction(
            user_id=test_user_tx.id,
            transaction_type='earn',
            points_change=100,
            reference_id=f'ORDER_{unique_suffix}',
            reference_type='order',
            description='购物获得积分',
            status='completed'
        )
        integration_test_db.add(earn_transaction)
        integration_test_db.commit()
        integration_test_db.refresh(earn_transaction)
        
        # 验证赚取积分交易
        assert earn_transaction.id is not None
        assert earn_transaction.user_id == test_user_tx.id
        assert earn_transaction.transaction_type == 'earn'
        assert earn_transaction.points_change == 100
        assert earn_transaction.status == 'completed'
        
        # 创建积分交易记录 - 使用积分
        use_transaction = PointTransaction(
            user_id=test_user_tx.id,
            transaction_type='use',
            points_change=-50,
            reference_id=f'COUPON_{unique_suffix}',
            reference_type='coupon',
            description='优惠券消费积分',
            status='completed'
        )
        integration_test_db.add(use_transaction)
        integration_test_db.commit()
        integration_test_db.refresh(use_transaction)
        
        # 验证使用积分交易
        assert use_transaction.user_id == test_user_tx.id
        assert use_transaction.transaction_type == 'use'
        assert use_transaction.points_change == -50
        assert use_transaction.status == 'completed'
        
    @pytest.mark.integration
    def test_member_level_management(self, integration_test_db: Session):
        """测试会员等级管理"""
        # 创建多个会员等级
        levels_data = [
            {'name': '普通会员', 'min_points': 0, 'discount': Decimal('1.0')},
            {'name': 'VIP会员', 'min_points': 1000, 'discount': Decimal('0.9')},
            {'name': '钻石会员', 'min_points': 5000, 'discount': Decimal('0.8')}
        ]
        
        created_levels = []
        for level_data in levels_data:
            unique_suffix = str(uuid.uuid4())[:8]
            level = MemberLevel(
                level_name=f"{level_data['name']}_{unique_suffix}",
                min_points=level_data['min_points'],
                discount_rate=level_data['discount'],
                benefits={'free_shipping': level_data['min_points'] >= 1000}
            )
            integration_test_db.add(level)
            created_levels.append(level)
            
        integration_test_db.commit()
        
        # 验证等级创建
        for i, level in enumerate(created_levels):
            integration_test_db.refresh(level)
            assert level.id is not None
            assert level.min_points == levels_data[i]['min_points']
            assert level.discount_rate == levels_data[i]['discount']
            
        # 查询所有等级
        all_levels = integration_test_db.query(MemberLevel).filter(
            MemberLevel.level_name.contains('会员_')
        ).order_by(MemberLevel.min_points).all()
        
        assert len(all_levels) >= 3
        # 验证按积分要求排序
        prev_points = -1
        for level in all_levels[:3]:  # 只检查我们创建的3个
            assert level.min_points >= prev_points
            prev_points = level.min_points


class TestMemberLevelUpgrade:
    """会员等级升级测试"""
    
    @pytest.mark.integration
    def test_member_level_upgrade_process(self, integration_test_db: Session):
        """测试会员等级升级流程"""
        # 创建专用测试用户
        unique_suffix = str(uuid.uuid4())[:8]
        test_user3 = User(
            username=f"upgrade_test_user_{unique_suffix}",
            email=f"upgrade_{unique_suffix}@test.com",
            password_hash="hashed_test_password",
            real_name=f"升级测试用户_{unique_suffix}",
            phone=f"137{unique_suffix[:8]}"
        )
        integration_test_db.add(test_user3)
        integration_test_db.commit()
        integration_test_db.refresh(test_user3)
        
        # 删除可能存在的会员档案（数据清理）
        integration_test_db.query(MemberProfile).filter(
            MemberProfile.user_id == test_user3.id
        ).delete()
        integration_test_db.commit()
        
        # 创建等级体系
        
        # 普通会员等级
        normal_level = MemberLevel(
            level_name=f"普通会员_{unique_suffix}",
            min_points=0,
            discount_rate=Decimal('1.0'),
            benefits={'free_shipping': False}
        )
        integration_test_db.add(normal_level)
        
        # VIP会员等级
        vip_level = MemberLevel(
            level_name=f"VIP会员_{unique_suffix}",
            min_points=1000,
            discount_rate=Decimal('0.9'),
            benefits={'free_shipping': True, 'birthday_discount': 0.1}
        )
        integration_test_db.add(vip_level)
        integration_test_db.commit()
        integration_test_db.refresh(normal_level)
        integration_test_db.refresh(vip_level)
        
        # 创建初始会员档案（普通会员）
        from datetime import datetime
        today = datetime.now()
        member_code = f"M{today.strftime('%Y%m%d')}{unique_suffix[:4]}"
        
        member_profile = MemberProfile(
            member_code=member_code,
            user_id=test_user3.id,
            level_id=normal_level.id,
            total_spent=Decimal('500.00'),  # 消费金额
            status=1,
            join_date=date.today()
        )
        integration_test_db.add(member_profile)
        integration_test_db.commit()
        integration_test_db.refresh(member_profile)
        
        # 删除可能存在的积分记录（数据清理）
        integration_test_db.query(MemberPoint).filter(
            MemberPoint.user_id == test_user3.id
        ).delete()
        integration_test_db.commit()
        
        # 创建对应的积分记录
        member_point = MemberPoint(
            user_id=test_user3.id,
            level_id=normal_level.id,
            current_points=500,
            total_earned=500,
            total_used=0
        )
        integration_test_db.add(member_point)
        integration_test_db.commit()
        integration_test_db.refresh(member_point)
        
        # 验证初始等级
        assert member_profile.level_id == normal_level.id
        assert member_point.current_points == 500
        
        # 模拟积分增加，达到升级条件
        member_point.current_points = 1200
        member_point.total_earned = 1200
        member_profile.level_id = vip_level.id  # 升级到VIP
        member_point.level_id = vip_level.id
        integration_test_db.commit()
        integration_test_db.refresh(member_profile)
        integration_test_db.refresh(member_point)
        
        # 验证升级后状态
        assert member_profile.level_id == vip_level.id
        assert member_point.current_points == 1200
        
        # 验证升级后的会员等级信息
        upgraded_level = integration_test_db.query(MemberLevel).filter(
            MemberLevel.id == member_profile.level_id
        ).first()
        assert upgraded_level.level_name.startswith('VIP会员_')
        assert upgraded_level.discount_rate == Decimal('0.9')
        assert upgraded_level.benefits['free_shipping'] is True


class TestMemberPointsIntegration:
    """会员积分集成测试"""
    
    @pytest.mark.integration
    def test_points_earn_and_use_cycle(self, integration_test_db: Session):
        """测试积分获得和使用的完整周期"""
        # 创建专用测试用户
        unique_suffix = str(uuid.uuid4())[:8]
        test_user_cycle = User(
            username=f"cycle_test_user_{unique_suffix}",
            email=f"cycle_{unique_suffix}@test.com",
            password_hash="hashed_test_password",
            real_name=f"周期测试用户_{unique_suffix}",
            phone=f"134{unique_suffix[:8]}"
        )
        integration_test_db.add(test_user_cycle)
        integration_test_db.commit()
        integration_test_db.refresh(test_user_cycle)
        
        # 删除可能存在的积分记录（数据清理）
        integration_test_db.query(MemberPoint).filter(
            MemberPoint.user_id == test_user_cycle.id
        ).delete()
        integration_test_db.commit()
        
        # 创建会员等级（积分需要关联等级）
        test_level = MemberLevel(
            level_name=f"测试等级_{unique_suffix}",
            min_points=0,
            discount_rate=Decimal('1.0'),
            benefits={}
        )
        integration_test_db.add(test_level)
        integration_test_db.commit()
        integration_test_db.refresh(test_level)
        
        # 创建积分账户
        member_points = MemberPoint(
            user_id=test_user_cycle.id,
            level_id=test_level.id,
            current_points=0,
            total_earned=0,
            total_used=0
        )
        integration_test_db.add(member_points)
        integration_test_db.commit()
        integration_test_db.refresh(member_points)
        
        # 第一次获得积分
        earn_tx1 = PointTransaction(
            user_id=test_user_cycle.id,
            transaction_type='earn',
            points_change=200,
            reference_id=f'ORDER_{unique_suffix}_1',
            reference_type='order',
            description='首次购物获得积分',
            status='completed'
        )
        integration_test_db.add(earn_tx1)
        
        # 更新积分账户
        member_points.current_points += 200
        member_points.total_earned += 200
        integration_test_db.commit()
        
        # 第二次获得积分
        earn_tx2 = PointTransaction(
            user_id=test_user_cycle.id,
            transaction_type='earn',
            points_change=150,
            reference_id=f'ORDER_{unique_suffix}_2',
            reference_type='order',
            description='第二次购物获得积分',
            status='completed'
        )
        integration_test_db.add(earn_tx2)
        
        # 更新积分账户
        member_points.current_points += 150
        member_points.total_earned += 150
        integration_test_db.commit()
        
        # 验证积分累计
        integration_test_db.refresh(member_points)
        assert member_points.total_earned == 350
        assert member_points.current_points == 350
        assert member_points.total_used == 0
        
        # 使用积分
        use_tx = PointTransaction(
            user_id=test_user_cycle.id,
            transaction_type='use',
            points_change=-100,
            reference_id=f'DISCOUNT_{unique_suffix}',
            reference_type='discount',
            description='购物抵扣使用积分',
            status='completed'
        )
        integration_test_db.add(use_tx)
        
        # 更新积分账户
        member_points.current_points -= 100
        member_points.total_used += 100
        integration_test_db.commit()
        
        # 验证积分使用后状态
        integration_test_db.refresh(member_points)
        assert member_points.total_earned == 350  # 总获得积分不变
        assert member_points.current_points == 250  # 当前积分减少
        assert member_points.total_used == 100  # 已用积分增加
        
        # 查询该用户的所有积分交易记录
        all_transactions = integration_test_db.query(PointTransaction).filter(
            PointTransaction.user_id == member_points.user_id
        ).order_by(PointTransaction.created_at).all()
        
        assert len(all_transactions) >= 3
        # 验证交易记录
        earn_transactions = [tx for tx in all_transactions if tx.transaction_type == 'earn']
        use_transactions = [tx for tx in all_transactions if tx.transaction_type == 'use']
        
        assert len(earn_transactions) >= 2
        assert len(use_transactions) >= 1
        
        # 验证积分变化总和
        total_earned = sum(tx.points_change for tx in earn_transactions)
        total_used = sum(abs(tx.points_change) for tx in use_transactions)
        
        assert total_earned >= 350
        assert total_used >= 100
        
    @pytest.mark.integration
    def test_member_benefits_calculation(self, integration_test_db: Session):
        """测试会员权益计算"""
        # 创建专用测试用户
        unique_suffix = str(uuid.uuid4())[:8]
        test_user4 = User(
            username=f"benefits_test_user_{unique_suffix}",
            email=f"benefits_{unique_suffix}@test.com",
            password_hash="hashed_test_password",
            real_name=f"权益测试用户_{unique_suffix}",
            phone=f"136{unique_suffix[:8]}"
        )
        integration_test_db.add(test_user4)
        integration_test_db.commit()
        integration_test_db.refresh(test_user4)
        
        # 删除可能存在的会员档案（数据清理）
        integration_test_db.query(MemberProfile).filter(
            MemberProfile.user_id == test_user4.id
        ).delete()
        integration_test_db.commit()
        
        # 创建VIP等级
        vip_level = MemberLevel(
            level_name=f"VIP会员_{unique_suffix}",
            min_points=1000,
            discount_rate=Decimal('0.85'),  # 8.5折
            benefits={
                'free_shipping': True,
                'birthday_discount': 0.2,
                'exclusive_products': True
            }
        )
        integration_test_db.add(vip_level)
        integration_test_db.commit()
        integration_test_db.refresh(vip_level)
        
        # 创建VIP会员档案
        from datetime import datetime
        today = datetime.now()
        member_code = f"M{today.strftime('%Y%m%d')}{unique_suffix[:4]}"
        
        member_profile = MemberProfile(
            member_code=member_code,
            user_id=test_user4.id,
            level_id=vip_level.id,
            total_spent=Decimal('1500.00'),
            status=1,
            join_date=date.today()
        )
        integration_test_db.add(member_profile)
        integration_test_db.commit()
        integration_test_db.refresh(member_profile)
        
        # 验证会员权益
        assert member_profile.level_id == vip_level.id
        
        # 获取等级信息并验证权益
        level_info = integration_test_db.query(MemberLevel).filter(
            MemberLevel.id == member_profile.level_id
        ).first()
        
        assert level_info.discount_rate == Decimal('0.85')
        assert level_info.benefits['free_shipping'] is True
        assert level_info.benefits['birthday_discount'] == 0.2
        assert level_info.benefits['exclusive_products'] is True
        
        # 模拟价格计算
        original_price = Decimal('100.00')
        member_price = original_price * level_info.discount_rate
        expected_price = Decimal('85.00')
        
        assert member_price == expected_price, "Member discount calculation should be correct"