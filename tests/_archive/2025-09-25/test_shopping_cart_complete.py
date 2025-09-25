"""
增强的shopping_cart集成测试 - 修复外键依赖
应用inventory_management成功模式创建完整的数据依赖链
"""

import pytest
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

# 导入被测试的模块
from app.modules.shopping_cart.models import Cart, CartItem
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
from app.modules.shopping_cart.schemas import AddItemRequest, UpdateQuantityRequest, CartResponse
from app.modules.shopping_cart.service import CartService
from app.shared.base_models import Base

# 导入依赖的模型 - 创建完整数据链
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Category, Brand, Product

# 集成测试数据库配置
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"


@pytest.fixture(scope="function")
def integration_test_engine():
    """集成测试数据库引擎，应用inventory_management成功模式"""
    engine = create_engine(INTEGRATION_TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function") 
def integration_test_db(integration_test_engine):
    """集成测试数据库会话，包含数据清理和外键处理"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=integration_test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # 清理数据并重置auto_increment
        try:
            session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            # 按依赖顺序清理表
            cleanup_tables = [
                'cart_items', 'carts', 'products', 'brands', 'categories', 'users'
            ]
            for table in cleanup_tables:
                session.execute(text(f"DELETE FROM {table};"))
                session.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1;"))
            
            session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()


@pytest.fixture
def test_data_factory(integration_test_db):
    """数据工厂 - 创建完整数据依赖链"""
    def create_complete_test_data():
        """创建完整的测试数据链：User -> Category -> Brand -> Product"""
        # 生成唯一标识符
        unique_suffix = str(uuid.uuid4())[:8]
        random_id = random.randint(10000, 99999)
        
        # 1. 创建用户
        user = User(
            username=f"testuser_{unique_suffix}",
            email=f"test_{unique_suffix}@example.com",
            password_hash="hashed_password",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        integration_test_db.add(user)
        integration_test_db.flush()
        
        # 2. 创建品类
        category = Category(
            name=f"测试品类_{unique_suffix}",
            description=f"测试品类描述_{unique_suffix}",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        integration_test_db.add(category)
        integration_test_db.flush()
        
        # 3. 创建品牌
        brand = Brand(
            name=f"测试品牌_{unique_suffix}",
            slug=f"test-brand-{unique_suffix}",  # 添加必需的slug字段
            description=f"测试品牌描述_{unique_suffix}",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        integration_test_db.add(brand)
        integration_test_db.flush()
        
        # 4. 创建商品
        product = Product(
            name=f"测试商品_{unique_suffix}",
            description=f"测试商品描述_{unique_suffix}",
            category_id=category.id,
            brand_id=brand.id,
            status="published",  # 发布状态
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        integration_test_db.add(product)
        integration_test_db.flush()
        
        integration_test_db.commit()
        
        return {
            'user': user,
            'category': category,
            'brand': brand,
            'product': product
        }
    
    return create_complete_test_data


@pytest.fixture
def cart_service(integration_test_db):
    """购物车服务实例"""
    return CartService(db=integration_test_db, redis_client=None)


@pytest.fixture
def sample_cart_with_data(integration_test_db, test_data_factory):
    """创建包含完整数据链的购物车"""
    data = test_data_factory()
    
    cart = Cart(
        user_id=data['user'].id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    integration_test_db.add(cart)
    integration_test_db.commit()
    integration_test_db.refresh(cart)
    
    return {
        'cart': cart,
        'user': data['user'],
        'product': data['product'],
        'category': data['category'],
        'brand': data['brand']
    }


@pytest.fixture
def sample_cart_item_with_data(integration_test_db, sample_cart_with_data):
    """创建包含完整数据链的购物车商品项"""
    cart_data = sample_cart_with_data
    
    cart_item = CartItem(
        cart_id=cart_data['cart'].id,
        sku_id=cart_data['product'].id,
        quantity=2,
        unit_price=Decimal("99.99"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    integration_test_db.add(cart_item)
    integration_test_db.commit()
    integration_test_db.refresh(cart_item)
    
    cart_data['cart_item'] = cart_item
    return cart_data


# ==================== 数据模型测试 ====================

class TestCartModel:
    """Cart模型测试类 - 修复外键依赖"""
    
    def test_cart_creation(self, integration_test_db, test_data_factory):
        """测试购物车创建 - 使用真实用户数据"""
        data = test_data_factory()
        
        cart = Cart(user_id=data['user'].id)
        integration_test_db.add(cart)
        integration_test_db.commit()
        integration_test_db.refresh(cart)
        
        assert cart.id is not None
        assert cart.user_id == data['user'].id
        assert cart.created_at is not None
        assert cart.updated_at is not None
        assert isinstance(cart.created_at, datetime)
        assert isinstance(cart.updated_at, datetime)
    
    def test_cart_user_id_unique_constraint(self, integration_test_db, test_data_factory):
        """测试用户ID唯一约束 - 使用真实用户数据"""
        data = test_data_factory()
        
        # 创建第一个购物车
        cart1 = Cart(user_id=data['user'].id)
        integration_test_db.add(cart1)
        integration_test_db.commit()
        
        # 尝试创建重复购物车
        cart2 = Cart(user_id=data['user'].id)
        integration_test_db.add(cart2)
        
        with pytest.raises(Exception):
            integration_test_db.commit()
    
    def test_cart_items_relationship(self, integration_test_db, sample_cart_with_data):
        """测试购物车商品项关联关系 - 使用真实数据链"""
        cart_data = sample_cart_with_data
        
        # 添加商品项到购物车
        item1 = CartItem(
            cart_id=cart_data['cart'].id,
            sku_id=cart_data['product'].id,
            quantity=2,
            unit_price=Decimal("99.99")
        )
        
        # 创建第二个商品用于测试
        unique_suffix = str(uuid.uuid4())[:8]
        product2 = Product(
            name=f"测试商品2_{unique_suffix}",
            description=f"测试商品2描述_{unique_suffix}",
            category_id=cart_data['category'].id,
            brand_id=cart_data['brand'].id,
            status="published",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        integration_test_db.add(product2)
        integration_test_db.flush()
        
        item2 = CartItem(
            cart_id=cart_data['cart'].id,
            sku_id=product2.id,
            quantity=1,
            unit_price=Decimal("199.99")
        )
        
        integration_test_db.add_all([item1, item2])
        integration_test_db.commit()
        
        # 验证关联关系
        integration_test_db.refresh(cart_data['cart'])
        assert len(cart_data['cart'].items) == 2
        assert cart_data['cart'].total_items == 2
        assert cart_data['cart'].total_quantity == 3  # 2 + 1
        expected_total = Decimal("99.99") * 2 + Decimal("199.99") * 1
        assert cart_data['cart'].total_amount == expected_total


class TestCartItemModel:
    """CartItem模型测试类 - 修复外键依赖"""
    
    def test_cart_item_creation(self, integration_test_db, sample_cart_with_data):
        """测试购物车商品项创建 - 使用真实数据链"""
        cart_data = sample_cart_with_data
        
        cart_item = CartItem(
            cart_id=cart_data['cart'].id,
            sku_id=cart_data['product'].id,
            quantity=3,
            unit_price=Decimal("150.50")
        )
        integration_test_db.add(cart_item)
        integration_test_db.commit()
        integration_test_db.refresh(cart_item)
        
        assert cart_item.id is not None
        assert cart_item.cart_id == cart_data['cart'].id
        assert cart_item.sku_id == cart_data['product'].id
        assert cart_item.quantity == 3
        assert cart_item.unit_price == Decimal("150.50")
        assert cart_item.subtotal == Decimal("451.50")
        assert cart_item.created_at is not None
        assert cart_item.updated_at is not None
    
    def test_cart_item_quantity_constraint(self, integration_test_db, sample_cart_with_data):
        """测试购物车商品项数量约束 - 使用真实数据链"""
        cart_data = sample_cart_with_data
        
        # 测试有效数量范围
        valid_cart_item = CartItem(
            cart_id=cart_data['cart'].id,
            sku_id=cart_data['product'].id,
            quantity=5,
            unit_price=Decimal("99.99")
        )
        integration_test_db.add(valid_cart_item)
        integration_test_db.commit()
        
        # 测试update_quantity方法
        valid_cart_item.update_quantity(10)
        assert valid_cart_item.quantity == 10
        
        # 测试无效数量
        with pytest.raises(ValueError):
            valid_cart_item.update_quantity(0)  # 小于最小值
            
        with pytest.raises(ValueError):
            valid_cart_item.update_quantity(1000)  # 大于最大值


class TestCartService:
    """CartService测试类 - 修复外键依赖"""
    
    @pytest.mark.asyncio
    async def test_add_item_new_cart(self, cart_service, test_data_factory):
        """测试添加商品到新购物车 - 使用真实数据链"""
        data = test_data_factory()
        
        request = AddItemRequest(
            sku_id=data['product'].id,
            quantity=2
        )
        
        result = await cart_service.add_item(user_id=data['user'].id, request=request)
        
        assert isinstance(result, CartResponse)
        assert result.user_id == data['user'].id
        assert result.total_items == 1  # 一种商品
        assert result.total_quantity == 2  # 总数量为2
        assert len(result.items) == 1
        assert result.items[0].sku_id == data['product'].id
        assert result.items[0].quantity == 2
    
    @pytest.mark.asyncio
    async def test_add_item_existing_product(self, cart_service, sample_cart_item_with_data):
        """测试添加已存在的商品 - 使用真实数据链"""
        cart_data = sample_cart_item_with_data
        
        request = AddItemRequest(
            sku_id=cart_data['product'].id,
            quantity=3
        )
        
        result = await cart_service.add_item(user_id=cart_data['user'].id, request=request)
        
        assert isinstance(result, CartResponse)
        assert result.user_id == cart_data['user'].id
        # 原来2个 + 新加3个 = 5个
        assert result.total_quantity == 5
        assert len(result.items) == 1  # 同一商品，应该合并
        assert result.items[0].quantity == 5


print("✅ 购物车集成测试文件已创建 - 应用inventory_management成功模式")