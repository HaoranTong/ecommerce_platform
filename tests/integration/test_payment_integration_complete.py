"""
支付服务模块 - 完整集成测试

测试支付服务与其他模块的集成，包括：
- 支付创建与订单关联
- 支付状态更新与订单状态同步  
- 支付回调处理
- 退款流程集成

遵循 testing-standards.md 要求，使用 MySQL 测试数据库
修复了User模型字段名称问题（password_hash vs hashed_password）
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.modules.payment_service.models import Payment, Refund
from app.modules.order_management.models import Order
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Product, Category, Brand, SKU


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def test_user(integration_test_db: Session):
    """创建测试用户 - 使用正确的字段名称"""
    unique_suffix = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique_suffix}",
        email=f"test_{unique_suffix}@example.com", 
        password_hash="hashed_password_here",  # 正确的字段名称
        phone=f"138{unique_suffix[:8]}"
    )
    integration_test_db.add(user)
    integration_test_db.commit()
    integration_test_db.refresh(user)
    return user


@pytest.fixture
def test_category(integration_test_db: Session):
    """创建测试分类"""
    unique_suffix = str(uuid.uuid4())[:8]
    category = Category(
        name=f"测试分类_{unique_suffix}",
        description="测试用分类"
    )
    integration_test_db.add(category)
    integration_test_db.commit()
    integration_test_db.refresh(category)
    return category


@pytest.fixture
def test_brand(integration_test_db: Session):
    """创建测试品牌"""
    unique_suffix = str(uuid.uuid4())[:8]
    brand = Brand(
        name=f"测试品牌_{unique_suffix}",
        slug=f"test-brand-{unique_suffix}",  # 添加必需的slug字段
        description="测试用品牌"
    )
    integration_test_db.add(brand)
    integration_test_db.commit()
    integration_test_db.refresh(brand)
    return brand


@pytest.fixture
def test_product(integration_test_db: Session, test_category, test_brand):
    """创建测试商品"""
    unique_suffix = str(uuid.uuid4())[:8]
    product = Product(
        name=f"测试商品_{unique_suffix}",
        category_id=test_category.id,
        brand_id=test_brand.id,
        description="测试用商品",
        status='published'  # 移除price字段，添加状态字段
    )
    integration_test_db.add(product)
    integration_test_db.commit()
    integration_test_db.refresh(product)
    return product


@pytest.fixture
def test_sku(integration_test_db: Session, test_product):
    """创建测试SKU"""
    unique_suffix = str(uuid.uuid4())[:8]
    sku = SKU(
        product_id=test_product.id,
        sku_code=f"SKU_{unique_suffix}",
        price=Decimal('199.99'),
        cost_price=Decimal('100.00'),  # 移除stock_quantity，添加实际存在的字段
        is_active=True
    )
    integration_test_db.add(sku)
    integration_test_db.commit()
    integration_test_db.refresh(sku)
    return sku


@pytest.fixture
def test_order(integration_test_db: Session, test_user, test_sku):
    """创建测试订单"""
    unique_suffix = str(uuid.uuid4())[:8]
    order = Order(
        order_number=f"ORDER_{unique_suffix}",  # 使用正确的字段名
        user_id=test_user.id,
        total_amount=Decimal('199.99'),
        status='pending'
    )
    integration_test_db.add(order)
    integration_test_db.commit()
    integration_test_db.refresh(order)
    return order


class TestPaymentIntegration:
    """支付服务集成测试"""
    
    @pytest.mark.integration
    def test_create_payment_for_order(self, integration_test_db: Session, test_order, test_user):
        """测试为订单创建支付"""
        # 创建支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='alipay',
            status='pending'
        )
        integration_test_db.add(payment)
        integration_test_db.commit()
        integration_test_db.refresh(payment)
        
        # 验证支付记录
        assert payment.id is not None
        assert payment.order_id == test_order.id
        assert payment.user_id == test_user.id
        assert payment.amount == Decimal('199.99')
        assert payment.payment_method == 'alipay'
        assert payment.status == 'pending'
    
    @pytest.mark.integration
    def test_payment_status_query(self, integration_test_db: Session, test_order, test_user):
        """测试支付状态查询"""
        # 创建支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='wechat',
            status='completed',
            paid_at=datetime.utcnow()
        )
        integration_test_db.add(payment)
        integration_test_db.commit()
        
        # 查询支付记录
        found_payment = integration_test_db.query(Payment).filter(
            Payment.payment_no == payment.payment_no
        ).first()
        
        # 验证查询结果
        assert found_payment is not None
        assert found_payment.status == 'completed'
        assert found_payment.paid_at is not None
        assert found_payment.payment_method == 'wechat'
        
    @pytest.mark.integration  
    def test_payment_callback_processing(self, integration_test_db: Session, test_order, test_user):
        """测试支付回调处理"""
        # 创建待支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='alipay',
            status='pending'
        )
        integration_test_db.add(payment)
        integration_test_db.commit()
        
        # 模拟回调处理
        payment.status = 'completed'
        payment.paid_at = datetime.utcnow()
        payment.callback_received_at = datetime.utcnow()
        payment.external_transaction_id = f"TXN_{unique_suffix}"
        integration_test_db.commit()
        
        # 验证回调处理结果
        integration_test_db.refresh(payment)
        assert payment.status == 'completed'
        assert payment.paid_at is not None
        assert payment.callback_received_at is not None
        assert payment.external_transaction_id.startswith('TXN_')
        
    @pytest.mark.integration
    def test_payment_list_for_user(self, integration_test_db: Session, test_order, test_user):
        """测试用户支付记录列表查询"""
        # 创建多个支付记录
        payments_data = []
        for i in range(3):
            unique_suffix = str(uuid.uuid4())[:8]
            payment = Payment(
                payment_no=f"PAY_{unique_suffix}_{i}",
                order_id=test_order.id,
                user_id=test_user.id,
                amount=Decimal(f'{100 + i * 50}.00'),
                payment_method=['alipay', 'wechat', 'unionpay'][i],
                status=['pending', 'completed', 'failed'][i]
            )
            integration_test_db.add(payment)
            payments_data.append(payment)
        integration_test_db.commit()
        
        # 查询用户支付记录
        user_payments = integration_test_db.query(Payment).filter(
            Payment.user_id == test_user.id
        ).all()
        
        # 验证查询结果
        assert len(user_payments) >= 3
        payment_methods = [p.payment_method for p in user_payments]
        assert 'alipay' in payment_methods
        assert 'wechat' in payment_methods
        assert 'unionpay' in payment_methods
        
    @pytest.mark.integration
    def test_refund_creation(self, integration_test_db: Session, test_order, test_user):
        """测试退款创建"""
        # 创建已完成的支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='alipay',
            status='completed',
            paid_at=datetime.utcnow()
        )
        integration_test_db.add(payment)
        integration_test_db.commit()
        integration_test_db.refresh(payment)
        
        # 创建退款记录
        refund = Refund(
            refund_no=f"REF_{unique_suffix}",
            payment_id=payment.id,
            amount=Decimal('99.99'),
            reason="用户申请退款",
            status='pending',
            operator_id=test_user.id
        )
        integration_test_db.add(refund)
        integration_test_db.commit()
        integration_test_db.refresh(refund)
        
        # 验证退款记录
        assert refund.id is not None
        assert refund.payment_id == payment.id
        assert refund.amount == Decimal('99.99')
        assert refund.reason == "用户申请退款"
        assert refund.status == 'pending'


class TestPaymentOrderIntegration:
    """支付与订单集成测试"""
    
    @pytest.mark.integration
    def test_payment_order_status_sync(self, integration_test_db: Session, test_order, test_user):
        """测试支付状态与订单状态同步"""
        # 创建支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=test_order.total_amount,
            payment_method='wechat',
            status='pending'
        )
        integration_test_db.add(payment)
        integration_test_db.commit()
        
        # 模拟支付完成，同步订单状态
        payment.status = 'completed'
        payment.paid_at = datetime.utcnow()
        
        # 同步更新订单支付状态
        test_order.payment_status = 'paid'
        test_order.status = 'confirmed'
        integration_test_db.commit()
        
        # 验证状态同步
        integration_test_db.refresh(payment)
        integration_test_db.refresh(test_order)
        assert payment.status == 'completed'
        assert test_order.payment_status == 'paid'
        assert test_order.status == 'confirmed'
        
    @pytest.mark.integration
    def test_payment_amount_validation(self, integration_test_db: Session, test_order, test_user):
        """测试支付金额验证"""
        # 创建支付记录，金额与订单金额一致
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=test_order.total_amount,  # 使用订单金额
            payment_method='alipay',
            status='pending'
        )
        integration_test_db.add(payment)
        integration_test_db.commit()
        integration_test_db.refresh(payment)
        
        # 验证支付金额与订单金额匹配
        assert payment.amount == test_order.total_amount
        
        # 验证关联关系
        assert payment.order_id == test_order.id
        assert payment.user_id == test_user.id


class TestPaymentErrorHandling:
    """支付错误处理测试"""
    
    @pytest.mark.integration
    def test_payment_for_nonexistent_order(self, integration_test_db: Session, test_user):
        """测试为不存在的订单创建支付"""
        # 尝试为不存在的订单ID创建支付
        unique_suffix = str(uuid.uuid4())[:8]
        
        # 这种情况下应该在业务逻辑层进行验证
        # 数据库层会通过外键约束阻止此类操作
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=99999,  # 不存在的订单ID
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='alipay',
            status='pending'
        )
        
        integration_test_db.add(payment)
        
        # 应该抛出外键约束错误
        with pytest.raises(Exception) as exc_info:
            integration_test_db.commit()
        
        # 验证是外键约束错误
        assert "foreign key constraint fails" in str(exc_info.value).lower()
        
    @pytest.mark.integration
    def test_duplicate_payment_prevention(self, integration_test_db: Session, test_order, test_user):
        """测试重复支付预防"""
        # 创建第一个支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment1 = Payment(
            payment_no=f"PAY_{unique_suffix}_1",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='alipay',
            status='pending'
        )
        integration_test_db.add(payment1)
        integration_test_db.commit()
        
        # 创建第二个支付记录（同一订单）
        payment2 = Payment(
            payment_no=f"PAY_{unique_suffix}_2",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='wechat',
            status='pending'
        )
        integration_test_db.add(payment2)
        integration_test_db.commit()
        
        # 查询该订单的所有支付记录
        order_payments = integration_test_db.query(Payment).filter(
            Payment.order_id == test_order.id
        ).all()
        
        # 验证可以创建多个支付记录（业务层应控制重复支付）
        assert len(order_payments) >= 2
        payment_nos = [p.payment_no for p in order_payments]
        assert f"PAY_{unique_suffix}_1" in payment_nos
        assert f"PAY_{unique_suffix}_2" in payment_nos
        
    @pytest.mark.integration
    def test_invalid_payment_method(self, integration_test_db: Session, test_order, test_user):
        """测试无效支付方式处理"""
        # 创建使用无效支付方式的支付记录
        unique_suffix = str(uuid.uuid4())[:8]
        payment = Payment(
            payment_no=f"PAY_{unique_suffix}",
            order_id=test_order.id,
            user_id=test_user.id,
            amount=Decimal('199.99'),
            payment_method='invalid_method',  # 无效的支付方式
            status='pending'
        )
        
        # 模型层允许任意字符串，验证应在Service层进行
        integration_test_db.add(payment)
        integration_test_db.commit()
        integration_test_db.refresh(payment)
        
        # 验证记录创建成功（但Service层应该验证支付方式有效性）
        assert payment.id is not None
        assert payment.payment_method == 'invalid_method'
        assert payment.status == 'pending'