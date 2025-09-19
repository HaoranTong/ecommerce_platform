"""
Shopping Cart Module Standalone Unit Tests

符合统一测试策略的业务逻辑测试：*_standalone.py → 100% 真实数据库 + pytest-mock
测试完整的购物车业务流程，确保数据一致性和业务逻辑正确性。
"""
import sys
import os
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入模型和服务
from app.modules.shopping_cart.models import CartItem
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import SKU, Product, Category, Brand
from app.modules.shopping_cart.service import CartService


class TestDataFactory:
    """统一测试数据工厂 - 消除硬编码ID，建立数据依赖关系"""
    
    @staticmethod
    def create_test_user(db, email_suffix="test"):
        """创建测试用户 - 使用动态数据避免ID冲突"""
        user = User(
            email=f"user_{email_suffix}@example.com",
            username=f"testuser_{email_suffix}",
            password_hash="hashed_password_123",
            is_active=True,
            email_verified=True  # 修正字段名：is_verified -> email_verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_test_category(db, name="Test Category"):
        """创建测试分类"""
        category = Category(
            name=name,
            description=f"Description for {name}",
            is_active=True
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def create_test_brand(db, name="Test Brand"):
        """创建测试品牌"""
        # 生成唯一的slug，避免重复
        import uuid
        slug = f"{name.lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"
        brand = Brand(
            name=name,
            slug=slug,  # 添加必需的slug字段
            description=f"Description for {name}",
            is_active=True
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand
    
    @staticmethod
    def create_test_product(db, category, brand, name="Test Product"):
        """创建测试产品"""
        product = Product(
            name=name,
            description=f"Description for {name}",
            category_id=category.id,
            brand_id=brand.id,
            status="published"  # 使用status字段而不是is_active
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def create_test_sku(db, product, sku_code="TEST_SKU", price=Decimal("99.99"), stock=100):
        """创建测试SKU"""
        sku = SKU(
            sku_code=sku_code,
            product_id=product.id,
            price=price,
            cost_price=price * Decimal("0.6"),
            # 移除stock_quantity和reserved_quantity字段，这些属于inventory_management模块
            is_active=True
        )
        db.add(sku)
        db.commit()
        db.refresh(sku)
        return sku
    
    @staticmethod
    def create_complete_test_data(db):
        """创建完整的测试数据链 - 用户、商品、SKU"""
        category = TestDataFactory.create_test_category(db, "Electronics")
        brand = TestDataFactory.create_test_brand(db, "TestBrand")
        product = TestDataFactory.create_test_product(db, category, brand, "Test Product")
        sku = TestDataFactory.create_test_sku(db, product, "TEST_SKU_001", Decimal("99.99"))
        user = TestDataFactory.create_test_user(db, "cart")
        return user, sku


class TestShoppingCartBusinessLogic:
    """购物车业务逻辑测试 - 使用真实数据库验证完整业务流程"""
    
    @pytest.mark.asyncio
    async def test_add_item_to_cart_success(self, unit_test_db):
        """测试成功添加商品到购物车"""
        # Arrange - 创建完整测试数据
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # Act - 添加商品到购物车
        from app.modules.shopping_cart.schemas import AddItemRequest
        request = AddItemRequest(sku_id=sku.id, quantity=2)  # 使用整数ID
        
        cart_response = await service.add_item(user_id=user.id, request=request)
        
        # Assert - 验证CartResponse结果
        assert cart_response is not None
        assert cart_response.user_id == user.id
        assert cart_response.total_quantity == 2
        assert len(cart_response.items) == 1
        assert cart_response.items[0].sku_id == sku.id
        assert cart_response.items[0].quantity == 2
        
        # 验证数据库中确实创建了记录
        from app.modules.shopping_cart.models import CartItem
        db_cart_item = unit_test_db.query(CartItem).filter_by(
            sku_id=sku.id
        ).first()
        assert db_cart_item is not None
        assert db_cart_item.quantity == 2
    
    @pytest.mark.asyncio
    async def test_add_item_quantity_update(self, unit_test_db):
        """测试向现有购物车项添加数量"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # 先添加一个商品
        from app.modules.shopping_cart.schemas import AddItemRequest
        request1 = AddItemRequest(sku_id=sku.id, quantity=2)
        await service.add_item(user.id, request1)
        
        # Act - 再次添加相同商品
        request2 = AddItemRequest(sku_id=sku.id, quantity=3)
        cart_response = await service.add_item(user.id, request2)
        
        # Assert - 验证数量已累加
        assert cart_response.items[0].quantity == 5  # 2 + 3
        
        # 验证数据库中只有一条记录
        from app.modules.shopping_cart.models import CartItem
        cart_items = unit_test_db.query(CartItem).filter_by(
            sku_id=sku.id
        ).all()
        assert len(cart_items) == 1
        assert cart_items[0].quantity == 5
    
    @pytest.mark.asyncio
    async def test_get_cart_items_success(self, unit_test_db):
        """测试获取购物车商品列表"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # 添加商品到购物车
        from app.modules.shopping_cart.schemas import AddItemRequest
        request = AddItemRequest(sku_id=sku.id, quantity=2)
        await service.add_item(user.id, request)
        
        # Act - 获取购物车
        cart_response = await service.get_cart(user.id)
        
        # Assert
        assert len(cart_response.items) == 1
        assert cart_response.user_id == user.id
        assert cart_response.items[0].sku_id == sku.id
        assert cart_response.items[0].quantity == 2
    
    def test_update_cart_item_quantity(self, unit_test_db):
        """测试更新购物车商品数量"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # 先添加商品
        cart_item = service.add_item_to_cart(user.id, sku.sku_code, 2)
        
        # Act - 更新数量
        updated_item = service.update_cart_item_quantity(
            cart_item.id, 
            new_quantity=5,
            user_id=user.id
        )
        
        # Assert
        assert updated_item.quantity == 5
        
        # 验证数据库更新
        db_item = unit_test_db.query(CartItem).get(cart_item.id)
        assert db_item.quantity == 5
    
    def test_remove_cart_item_success(self, unit_test_db):
        """测试删除购物车商品"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        cart_item = service.add_item_to_cart(user.id, sku.sku_code, 2)
        cart_item_id = cart_item.id
        
        # Act - 删除商品
        result = service.remove_cart_item(cart_item_id, user.id)
        
        # Assert
        assert result is True
        
        # 验证数据库中已删除
        db_item = unit_test_db.query(CartItem).get(cart_item_id)
        assert db_item is None
    
    def test_clear_cart_success(self, unit_test_db):
        """测试清空购物车"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # 添加多个商品
        service.add_item_to_cart(user.id, sku.sku_code, 2)
        
        # 创建第二个SKU并添加
        sku2 = TestDataFactory.create_test_sku(
            unit_test_db, sku.product, "TEST_SKU_002", Decimal("49.99")
        )
        service.add_item_to_cart(user.id, sku2.sku_code, 1)
        
        # Act - 清空购物车
        result = service.clear_cart(user.id)
        
        # Assert
        assert result is True
        
        # 验证购物车已清空
        cart_items = unit_test_db.query(CartItem).filter_by(user_id=user.id).all()
        assert len(cart_items) == 0
    
    def test_calculate_cart_total(self, unit_test_db):
        """测试购物车总价计算"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # 添加商品
        service.add_item_to_cart(user.id, sku.sku_code, 2)  # 2 * 99.99 = 199.98
        
        # 添加第二个商品
        sku2 = TestDataFactory.create_test_sku(
            unit_test_db, sku.product, "TEST_SKU_002", Decimal("49.99")
        )
        service.add_item_to_cart(user.id, sku2.sku_code, 3)  # 3 * 49.99 = 149.97
        
        # Act - 计算总价
        total = service.calculate_cart_total(user.id)
        
        # Assert
        expected_total = Decimal("199.98") + Decimal("149.97")  # 349.95
        assert total == expected_total
    
    def test_get_cart_summary(self, unit_test_db):
        """测试购物车摘要信息"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        service.add_item_to_cart(user.id, sku.sku_code, 2)
        
        # Act
        summary = service.get_cart_summary(user.id)
        
        # Assert
        assert summary["total_items"] == 1
        assert summary["total_quantity"] == 2
        assert summary["total_amount"] == Decimal("199.98")
        assert len(summary["items"]) == 1


class TestShoppingCartEdgeCases:
    """购物车边界情况测试"""
    
    def test_add_item_invalid_user(self, unit_test_db):
        """测试无效用户ID"""
        # Arrange
        _, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # Act & Assert
        with pytest.raises(ValueError, match="用户不存在"):
            service.add_item_to_cart(user_id=99999, sku_id=sku.sku_code, quantity=1)
    
    def test_add_item_invalid_sku(self, unit_test_db):
        """测试无效SKU"""
        # Arrange
        user, _ = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # Act & Assert
        with pytest.raises(ValueError, match="SKU不存在"):
            service.add_item_to_cart(user.id, "INVALID_SKU", 1)
    
    def test_add_item_insufficient_stock(self, unit_test_db):
        """测试库存不足"""
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # 设置库存为5
        sku.stock_quantity = 5
        unit_test_db.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="库存不足"):
            service.add_item_to_cart(user.id, sku.sku_code, 10)  # 尝试添加10个
    
    def test_empty_cart_operations(self, unit_test_db):
        """测试空购物车操作"""
        # Arrange
        user = TestDataFactory.create_test_user(unit_test_db, "empty_cart")
        service = CartService(unit_test_db)
        
        # Act & Assert
        cart_items = service.get_cart_items(user.id)
        assert len(cart_items) == 0
        
        total = service.calculate_cart_total(user.id)
        assert total == Decimal("0.00")
        
        summary = service.get_cart_summary(user.id)
        assert summary["total_items"] == 0
        assert summary["total_quantity"] == 0
        assert summary["total_amount"] == Decimal("0.00")


class TestShoppingCartConcurrency:
    """购物车并发操作测试"""
    
    def test_concurrent_add_same_item(self, unit_test_db):
        """测试并发添加相同商品的处理"""
        # 这个测试模拟了两个请求同时添加相同商品的情况
        # 在真实场景中需要使用数据库锁或乐观锁来处理
        
        # Arrange
        user, sku = TestDataFactory.create_complete_test_data(unit_test_db)
        service = CartService(unit_test_db)
        
        # Act - 连续两次添加（模拟并发）
        service.add_item_to_cart(user.id, sku.sku_code, 2)
        service.add_item_to_cart(user.id, sku.sku_code, 3)
        
        # Assert - 验证数量正确累加
        cart_items = unit_test_db.query(CartItem).filter_by(
            user_id=user.id,
            sku_id=sku.sku_code
        ).all()
        
        assert len(cart_items) == 1  # 只有一条记录
        assert cart_items[0].quantity == 5  # 数量正确累加
