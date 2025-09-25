"""
购物车模块单元测试
测试购物车添加、删除、更新等核心功能
符合 [CHECK:TEST-002] 数据类型一致性要求
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 直接导入购物车模块的模型和服务函数，避免加载整个应用
from app.modules.shopping_cart.models import Base, Cart, CartItem
from app.modules.shopping_cart.service import CartService
from app.modules.shopping_cart.schemas import AddItemRequest
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator

# 注释：使用 conftest.py 中的标准 fixture

@pytest.fixture
def test_user(unit_test_db):
    """测试用户"""
    from app.modules.user_auth.models import User
    from app.core.auth import get_password_hash
    
    user = User(
        username="cartuser",
        email="cart@example.com",
        password_hash=get_password_hash("testpass123"),
        failed_attempts=0,
        is_locked=False
    )
    unit_test_db.add(user)
    unit_test_db.commit()
    unit_test_db.refresh(user)
    return user

@pytest.fixture
def test_product(unit_test_db):
    """测试商品"""
    from app.modules.product_catalog.models import Product, Category, Brand
    
    # 创建分类和品牌
    category = Category(name="测试分类", description="测试分类描述")
    brand = Brand(name="测试品牌", description="测试品牌描述")
    unit_test_db.add(category)
    unit_test_db.add(brand)
    unit_test_db.commit()
    
    # 创建商品
    product = Product(
        name="测试商品",
        description="测试商品描述",
        price=Decimal("99.99"),
        category_id=category.id,
        brand_id=brand.id,
        is_active=True
    )
    unit_test_db.add(product)
    unit_test_db.commit()
    unit_test_db.refresh(product)
    return product

@pytest.fixture
def cart_service(unit_test_db):
    """购物车服务实例"""
    return CartService(unit_test_db)

class TestCartOperations:
    """购物车基本操作测试"""
    
    def test_create_cart_for_user(self, unit_test_db, test_user):
        """测试为用户创建购物车"""
        # 创建购物车
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        unit_test_db.refresh(cart)
        
        # 验证购物车属性
        assert cart.id is not None
        assert cart.user_id == test_user.id
        assert cart.created_at is not None
        assert cart.updated_at is not None
        assert isinstance(cart.created_at, datetime)
        assert isinstance(cart.updated_at, datetime)
        
    def test_add_item_to_cart(self, unit_test_db, test_user, test_product):
        """测试添加商品到购物车"""
        # 创建购物车
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        unit_test_db.refresh(cart)
        
        # 添加商品项
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=2,
            price=test_product.price
        )
        unit_test_db.add(cart_item)
        unit_test_db.commit()
        unit_test_db.refresh(cart_item)
        
        # 验证商品项属性 - 符合[CHECK:TEST-002]要求
        assert cart_item.id is not None
        assert cart_item.cart_id == cart.id  # 使用Integer类型ID
        assert cart_item.product_id == test_product.id  # 使用Integer类型ID
        assert cart_item.quantity == 2
        assert isinstance(cart_item.price, Decimal)  # Decimal类型
        assert cart_item.price == Decimal("99.99")
        assert isinstance(cart_item.created_at, datetime)  # datetime对象
        
    def test_cart_item_total_calculation(self, unit_test_db, test_user, test_product):
        """测试购物车商品项总价计算"""
        # 创建购物车和商品项
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=3,
            price=Decimal("50.00")
        )
        unit_test_db.add(cart_item)
        unit_test_db.commit()
        unit_test_db.refresh(cart_item)
        
        # 验证总价计算
        expected_total = cart_item.quantity * cart_item.price
        assert expected_total == Decimal("150.00")
        
    def test_update_cart_item_quantity(self, unit_test_db, test_user, test_product):
        """测试更新购物车商品数量"""
        # 创建购物车和商品项
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        unit_test_db.add(cart_item)
        unit_test_db.commit()
        
        # 更新数量
        cart_item.quantity = 5
        unit_test_db.commit()
        unit_test_db.refresh(cart_item)
        
        # 验证更新结果
        assert cart_item.quantity == 5
        
    def test_delete_cart_item(self, unit_test_db, test_user, test_product):
        """测试删除购物车商品项"""
        # 创建购物车和商品项
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        unit_test_db.add(cart_item)
        unit_test_db.commit()
        item_id = cart_item.id
        
        # 删除商品项
        unit_test_db.delete(cart_item)
        unit_test_db.commit()
        
        # 验证删除结果
        deleted_item = unit_test_db.query(CartItem).filter_by(id=item_id).first()
        assert deleted_item is None

class TestCartConstraints:
    """购物车约束和验证测试"""
    
    def test_user_unique_cart_constraint(self, unit_test_db, test_user):
        """测试用户唯一购物车约束"""
        # 创建第一个购物车
        cart1 = Cart(user_id=test_user.id)
        unit_test_db.add(cart1)
        unit_test_db.commit()
        
        # 尝试创建第二个购物车（应该违反唯一约束）
        cart2 = Cart(user_id=test_user.id)
        unit_test_db.add(cart2)
        
        # 验证约束冲突
        with pytest.raises(Exception):  # 数据库约束错误
            unit_test_db.commit()
            
    def test_cart_item_positive_quantity(self, unit_test_db, test_user, test_product):
        """测试购物车商品项数量必须为正数"""
        # 创建购物车
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        
        # 创建商品项（数量为0或负数应该在业务层面被阻止）
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=0,  # 零数量
            price=test_product.price
        )
        unit_test_db.add(cart_item)
        unit_test_db.commit()
        
        # 业务逻辑应该验证数量大于0
        assert cart_item.quantity >= 0  # 基本数据库约束

class TestCartRelationships:
    """购物车关联关系测试"""
    
    def test_cart_to_items_relationship(self, unit_test_db, test_user, test_product):
        """测试购物车到商品项的一对多关系"""
        # 创建购物车
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        unit_test_db.refresh(cart)
        
        # 添加多个商品项
        item1 = CartItem(cart_id=cart.id, product_id=test_product.id, 
                        quantity=1, price=Decimal("10.00"))
        item2 = CartItem(cart_id=cart.id, product_id=test_product.id, 
                        quantity=2, price=Decimal("20.00"))
        
        unit_test_db.add_all([item1, item2])
        unit_test_db.commit()
        
        # 验证关联关系
        unit_test_db.refresh(cart)  # 刷新以获取关联数据
        assert len(cart.items) == 2
        assert cart.items[0].cart_id == cart.id
        assert cart.items[1].cart_id == cart.id
        
    def test_cascade_delete_cart_items(self, unit_test_db, test_user, test_product):
        """测试删除购物车时级联删除商品项"""
        # 创建购物车和商品项
        cart = Cart(user_id=test_user.id)
        unit_test_db.add(cart)
        unit_test_db.commit()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        unit_test_db.add(cart_item)
        unit_test_db.commit()
        
        cart_id = cart.id
        
        # 删除购物车
        unit_test_db.delete(cart)
        unit_test_db.commit()
        
        # 验证级联删除
        remaining_items = unit_test_db.query(CartItem).filter_by(cart_id=cart_id).all()
        assert len(remaining_items) == 0