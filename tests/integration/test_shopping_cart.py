"""
文件名：test_shopping_cart.py
文件路径：tests/test_shopping_cart.py
功能描述：购物车模块完整单元测试套件
主要功能：
- CartService业务逻辑测试：添加商品、获取购物车、更新数量、删除操作
- 数据模型测试：Cart和CartItem模型的创建、关联关系、约束验证
- 业务规则测试：数量限制、商品种类限制、权限验证
- 异常处理测试：错误场景的异常抛出和数据回滚
- 边界条件测试：空购物车、最大数量、批量操作等边界情况
使用说明：
- 运行测试：pytest tests/test_shopping_cart.py -v
- 覆盖率：pytest tests/test_shopping_cart.py --cov=app.modules.shopping_cart
- 调试模式：pytest tests/test_shopping_cart.py -s --tb=short
依赖模块：
- pytest: 测试框架
- app.modules.shopping_cart: 被测试模块
- sqlalchemy: 数据库ORM测试
创建时间：2025-09-16
最后修改：2025-09-16
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

# 导入被测试的模块 - 按照强制检查清单验证字段存在性
from app.modules.shopping_cart.models import Cart, CartItem
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
from app.modules.shopping_cart.schemas import AddItemRequest, UpdateQuantityRequest, CartResponse
from app.modules.shopping_cart.service import CartService
from app.shared.base_models import Base

# 导入所有相关模型确保表结构创建和外键关系正确 - [CHECK:TEST-001]
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Product, Category, SKU  
from app.modules.inventory_management.models import InventoryStock

# 集成测试数据库配置（MySQL Docker容器）
INTEGRATION_TEST_DATABASE_URL = "mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test"


@pytest.fixture(scope="function")  
def test_engine():
    """
    集成测试数据库引擎
    
    使用MySQL Docker容器，用于集成测试的真实环境模拟。
    每个测试函数使用独立的事务，确保测试间无干扰。
    """
    engine = create_engine(
        INTEGRATION_TEST_DATABASE_URL
    )
    # 创建所有表结构
    Base.metadata.create_all(bind=engine)
    yield engine
    # 测试结束后清理资源
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    测试数据库会话
    
    提供独立的数据库会话，支持事务回滚和数据隔离。
    确保每个测试用例从干净的数据库状态开始。
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def cart_service(test_db):
    """
    购物车服务实例
    
    创建CartService实例，注入测试数据库会话。
    用于测试购物车的所有业务逻辑操作。
    """
    return CartService(db=test_db, redis_client=None)


@pytest.fixture(autouse=True, scope="function")
def setup_test_data(test_db):
    """
    自动创建完整测试数据链 - [CHECK:TEST-001]
    
    修复原始测试的设计缺陷：购物车测试需要完整的数据依赖支持。
    按照外键依赖顺序创建：User → Category → Product → SKU → InventoryStock
    """
    from sqlalchemy import text
    
    # 按反向依赖关系清理数据（避免外键约束冲突）
    test_db.query(InventoryStock).delete()
    test_db.query(SKU).delete() 
    test_db.query(Product).delete()
    test_db.query(Category).delete()
    test_db.query(User).delete()
    test_db.commit()
    
    # 重置AUTO_INCREMENT确保ID的一致性
    test_db.execute(text("ALTER TABLE users AUTO_INCREMENT = 1"))
    test_db.execute(text("ALTER TABLE categories AUTO_INCREMENT = 1"))  
    test_db.execute(text("ALTER TABLE products AUTO_INCREMENT = 1"))
    test_db.commit()
    
    # 1. 创建测试用户 (确保user_id=1存在)
    user = User(
        username="test_user_1",
        email="test1@example.com", 
        password_hash="hashed_password",
        phone="13900139000",
        is_active=True
    )
    test_db.add(user)
    test_db.flush()
    assert user.id == 1, f"Expected user.id=1, got {user.id}"
    
    # 2. 创建测试分类
    category = Category(
        name="测试分类",
        description="购物车集成测试分类",
        is_active=True
    )
    test_db.add(category)
    test_db.flush()
    
    # 3. 创建测试商品
    product = Product(
        name="测试商品",
        description="购物车集成测试商品",
        category_id=category.id,
        status="published"
    )
    test_db.add(product)
    test_db.flush()
    
    # 4. 创建测试SKU (使用固定ID 12345用于测试兼容性)
    test_db.execute(text("""
        INSERT INTO skus (id, product_id, sku_code, price, cost_price, is_active, created_at, updated_at) 
        VALUES (12345, :product_id, 'TEST_SKU_12345', 99.99, 59.99, true, NOW(), NOW())
    """), {"product_id": product.id})
    
    # 5. 创建库存记录（包含所有必需字段）
    test_db.execute(text("""
        INSERT INTO inventory_stocks (sku_id, total_quantity, available_quantity, reserved_quantity, warning_threshold, critical_threshold, is_active, created_at, updated_at)
        VALUES (12345, 1000, 1000, 0, 10, 5, true, NOW(), NOW())
    """))
    
    test_db.commit()
    
    return {"user_id": user.id, "sku_id": 12345, "product_id": product.id}


@pytest.fixture
def sample_cart(test_db):
    """
    示例购物车数据
    
    创建测试用的购物车记录，包含预设的用户ID和时间戳。
    为购物车商品项测试提供基础数据。
    """
    cart = Cart(
        user_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(cart)
    test_db.commit()
    test_db.refresh(cart)
    return cart


@pytest.fixture
def sample_cart_item(test_db, sample_cart):
    """
    示例购物车商品项
    
    创建测试用的购物车商品项，关联到sample_cart。
    包含真实的字段数据，用于测试商品项相关功能。
    """
    cart_item = CartItem(
        cart_id=sample_cart.id,
        sku_id=12345,
        quantity=2,
        unit_price=Decimal("99.99"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(cart_item)
    test_db.commit()
    test_db.refresh(cart_item)
    return cart_item


# ==================== 数据模型测试 ====================

class TestCartModel:
    """
    Cart模型测试类
    
    测试购物车主表模型的创建、字段验证、关联关系等功能。
    验证模型定义与数据库表结构的一致性。
    """
    
    def test_cart_creation(self, test_db):
        """
        测试购物车创建
        
        验证Cart模型的基本创建功能，包括：
        - 所有必需字段的正确设置
        - 自动生成的时间戳字段
        - 数据库主键自增功能
        """
        # ================== 创建购物车记录 ==================
        cart = Cart(user_id=1)
        test_db.add(cart)
        test_db.commit()
        test_db.refresh(cart)
        
        # ================== 验证字段值 ==================
        assert cart.id is not None  # 主键自动生成
        assert cart.user_id == 1     # 用户ID正确设置
        assert cart.created_at is not None  # 创建时间自动设置
        assert cart.updated_at is not None  # 更新时间自动设置
        assert isinstance(cart.created_at, datetime)  # 时间类型正确
        assert isinstance(cart.updated_at, datetime)
    
    def test_cart_user_id_unique_constraint(self, test_db):
        """
        测试用户ID唯一约束
        
        验证每个用户只能有一个购物车的业务规则。
        确保数据库层面的唯一性约束正确工作。
        """
        # ================== 创建第一个购物车 ==================
        cart1 = Cart(user_id=1)
        test_db.add(cart1)
        test_db.commit()
        
        # ================== 尝试创建重复购物车 ==================
        cart2 = Cart(user_id=1)  # 相同的user_id
        test_db.add(cart2)
        
        # ================== 验证唯一约束异常 ==================
        with pytest.raises(Exception):  # 应该抛出数据库完整性异常
            test_db.commit()
    
    def test_cart_items_relationship(self, test_db, sample_cart):
        """
        测试购物车商品项关联关系
        
        验证Cart与CartItem之间的一对多关联关系。
        测试级联删除和关联查询功能。
        """
        # ================== 添加商品项到购物车 ==================
        item1 = CartItem(
            cart_id=sample_cart.id,
            sku_id=12345,
            quantity=2,
            unit_price=Decimal("99.99")
        )
        item2 = CartItem(
            cart_id=sample_cart.id,
            sku_id=67890,
            quantity=1,
            unit_price=Decimal("149.99")
        )
        test_db.add_all([item1, item2])
        test_db.commit()
        
        # ================== 验证关联关系 ==================
        test_db.refresh(sample_cart)
        assert len(sample_cart.items) == 2  # 购物车包含2个商品项
        assert sample_cart.items[0].cart_id == sample_cart.id  # 正确关联
        assert sample_cart.items[1].cart_id == sample_cart.id


class TestCartItemModel:
    """
    CartItem模型测试类
    
    测试购物车商品项模型的创建、约束验证、业务逻辑等功能。
    验证商品项的数据完整性和业务规则。
    """
    
    def test_cart_item_creation(self, test_db, sample_cart):
        """
        测试购物车商品项创建
        
        验证CartItem模型的基本创建功能，包括所有字段的正确设置。
        """
        # ================== 创建购物车商品项 ==================
        cart_item = CartItem(
            cart_id=sample_cart.id,
            sku_id=12345,
            quantity=3,
            unit_price=Decimal("79.99")
        )
        test_db.add(cart_item)
        test_db.commit()
        test_db.refresh(cart_item)
        
        # ================== 验证字段值 ==================
        assert cart_item.id is not None
        assert cart_item.cart_id == sample_cart.id
        assert cart_item.sku_id == 12345
        assert cart_item.quantity == 3
        assert cart_item.unit_price == Decimal("79.99")
        assert cart_item.created_at is not None
        assert cart_item.updated_at is not None
    
    def test_cart_item_quantity_constraint(self, test_db, sample_cart):
        """
        测试商品数量约束
        
        验证数量字段的有效性检查，确保不能设置无效的数量值。
        """
        # ================== 测试有效数量 ==================
        valid_item = CartItem(
            cart_id=sample_cart.id,
            sku_id=12345,
            quantity=1,  # 最小有效值
            unit_price=Decimal("99.99")
        )
        test_db.add(valid_item)
        test_db.commit()  # 应该成功
        
        # ================== 测试无效数量 ==================
        # 数据库层约束检查：数量必须大于0（CHECK约束）
        invalid_item = CartItem(
            cart_id=sample_cart.id,
            sku_id=67890,
            quantity=0,  # 无效数量，违反CHECK约束
            unit_price=Decimal("99.99")
        )
        test_db.add(invalid_item)
        
        # 应该抛出完整性错误
        with pytest.raises(Exception) as exc_info:
            test_db.commit()
        
        # 验证错误包含约束信息
        assert "constraint" in str(exc_info.value).lower() or "check" in str(exc_info.value).lower()


# ==================== 业务逻辑测试 ====================

class TestCartService:
    """
    CartService业务逻辑测试类
    
    测试购物车服务的所有业务方法，包括正常流程和异常处理。
    验证业务规则、数据一致性、事务管理等核心功能。
    """
    
    @pytest.mark.asyncio
    async def test_add_item_new_cart(self, cart_service):
        """
        测试添加商品到新购物车
        
        验证当用户没有购物车时，自动创建购物车并添加商品的功能。
        """
        # ================== 准备测试数据 ==================
        request = AddItemRequest(sku_id=12345, quantity=2)
        
        # ================== 执行添加操作 ==================
        result = await cart_service.add_item(user_id=1, request=request)
        
        # ================== 验证结果 ==================
        assert isinstance(result, CartResponse)
        assert result.user_id == 1
        assert result.total_items == 1  # 一种商品
        assert result.total_quantity == 2  # 总数量为2
        assert len(result.items) == 1
        assert result.items[0].sku_id == 12345
        assert result.items[0].quantity == 2
    
    @pytest.mark.asyncio
    async def test_add_item_existing_product(self, cart_service):
        """
        测试添加已存在商品（数量合并）
        
        验证当购物车中已有相同商品时，数量合并的功能。
        """
        # ================== 第一次添加商品 ==================
        request1 = AddItemRequest(sku_id=12345, quantity=2)
        await cart_service.add_item(user_id=1, request=request1)
        
        # ================== 第二次添加相同商品 ==================
        request2 = AddItemRequest(sku_id=12345, quantity=3)
        result = await cart_service.add_item(user_id=1, request=request2)
        
        # ================== 验证数量合并 ==================
        assert result.total_items == 1  # 仍然是一种商品
        assert result.total_quantity == 5  # 数量合并：2+3=5
        assert result.items[0].quantity == 5
    
    @pytest.mark.asyncio
    async def test_add_item_quantity_limit(self, cart_service):
        """
        测试商品数量限制
        
        验证单个商品数量不能超过999的业务规则。
        """
        # ================== 添加接近限制的数量 ==================
        request1 = AddItemRequest(sku_id=12345, quantity=990)
        await cart_service.add_item(user_id=1, request=request1)
        
        # ================== 尝试超过限制 ==================
        request2 = AddItemRequest(sku_id=12345, quantity=20)  # 990+20=1010 > 999
        
        with pytest.raises(HTTPException) as exc_info:
            await cart_service.add_item(user_id=1, request=request2)
        
        # ================== 验证异常信息 ==================
        assert exc_info.value.status_code == 400
        assert "999" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_add_item_max_items_limit(self, cart_service):
        """
        测试购物车商品种类限制
        
        验证购物车商品种类不能超过50种的业务规则。
        """
        # ================== 添加49种不同商品 ==================
        for i in range(49):
            request = AddItemRequest(sku_id=10000 + i, quantity=1)
            await cart_service.add_item(user_id=1, request=request)
        
        # ================== 添加第50种商品（应该成功） ==================
        request_50 = AddItemRequest(sku_id=10050, quantity=1)
        result = await cart_service.add_item(user_id=1, request=request_50)
        assert result.total_items == 50
        
        # ================== 尝试添加第51种商品（应该失败） ==================
        request_51 = AddItemRequest(sku_id=10051, quantity=1)
        with pytest.raises(HTTPException) as exc_info:
            await cart_service.add_item(user_id=1, request=request_51)
        
        assert exc_info.value.status_code == 400
        assert "50" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_cart_empty(self, cart_service):
        """
        测试获取空购物车
        
        验证用户没有购物车时返回空购物车结构的功能。
        """
        # ================== 获取不存在的购物车 ==================
        result = await cart_service.get_cart(user_id=999)
        
        # ================== 验证空购物车结构 ==================
        assert isinstance(result, CartResponse)
        assert result.cart_id == 0
        assert result.user_id == 999
        assert result.total_items == 0
        assert result.total_quantity == 0
        assert result.total_amount == Decimal("0.00")
        assert len(result.items) == 0
    
    @pytest.mark.asyncio
    async def test_get_cart_with_items(self, cart_service):
        """
        测试获取有商品的购物车
        
        验证购物车包含商品时的完整信息返回。
        """
        # ================== 添加多个商品 ==================
        request1 = AddItemRequest(sku_id=12345, quantity=2)
        request2 = AddItemRequest(sku_id=67890, quantity=1)
        await cart_service.add_item(user_id=1, request=request1)
        await cart_service.add_item(user_id=1, request=request2)
        
        # ================== 获取购物车 ==================
        result = await cart_service.get_cart(user_id=1)
        
        # ================== 验证购物车内容 ==================
        assert result.total_items == 2  # 两种商品
        assert result.total_quantity == 3  # 总数量：2+1=3
        assert len(result.items) == 2
        
        # 验证商品项信息
        sku_ids = [item.sku_id for item in result.items]
        assert 12345 in sku_ids
        assert 67890 in sku_ids
    
    @pytest.mark.asyncio
    async def test_update_quantity_success(self, cart_service):
        """
        测试更新商品数量成功
        
        验证正常的商品数量更新功能。
        """
        # ================== 添加商品 ==================
        request = AddItemRequest(sku_id=12345, quantity=2)
        result = await cart_service.add_item(user_id=1, request=request)
        item_id = result.items[0].item_id
        
        # ================== 更新数量 ==================
        updated_cart = await cart_service.update_quantity(
            user_id=1, 
            item_id=item_id, 
            quantity=5
        )
        
        # ================== 验证更新结果 ==================
        assert updated_cart.total_quantity == 5
        assert updated_cart.items[0].quantity == 5
    
    @pytest.mark.asyncio
    async def test_update_quantity_invalid_item(self, cart_service):
        """
        测试更新不存在的商品项
        
        验证更新不存在或不属于当前用户的商品项时的异常处理。
        """
        # ================== 尝试更新不存在的商品项 ==================
        with pytest.raises(HTTPException) as exc_info:
            await cart_service.update_quantity(
                user_id=1, 
                item_id=99999,  # 不存在的商品项ID
                quantity=5
            )
        
        # ================== 验证异常信息 ==================
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_quantity_invalid_range(self, cart_service):
        """
        测试更新无效数量范围
        
        验证数量超出有效范围时的异常处理。
        """
        # ================== 添加商品 ==================
        request = AddItemRequest(sku_id=12345, quantity=2)
        result = await cart_service.add_item(user_id=1, request=request)
        item_id = result.items[0].item_id
        
        # ================== 测试数量过小 ==================
        with pytest.raises(HTTPException) as exc_info:
            await cart_service.update_quantity(user_id=1, item_id=item_id, quantity=0)
        assert exc_info.value.status_code == 400
        
        # ================== 测试数量过大 ==================
        with pytest.raises(HTTPException) as exc_info:
            await cart_service.update_quantity(user_id=1, item_id=item_id, quantity=1000)
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_delete_item_success(self, cart_service):
        """
        测试删除商品项成功
        
        验证正常的商品项删除功能。
        """
        # ================== 添加两个商品 ==================
        request1 = AddItemRequest(sku_id=12345, quantity=2)
        request2 = AddItemRequest(sku_id=67890, quantity=1)
        await cart_service.add_item(user_id=1, request=request1)
        result = await cart_service.add_item(user_id=1, request=request2)
        
        # 获取第一个商品的item_id
        item_to_delete = next(item for item in result.items if item.sku_id == 12345)
        
        # ================== 删除商品项 ==================
        success = await cart_service.delete_item(user_id=1, item_id=item_to_delete.item_id)
        
        # ================== 验证删除结果 ==================
        assert success is True
        
        # 验证购物车状态
        updated_cart = await cart_service.get_cart(user_id=1)
        assert updated_cart.total_items == 1  # 剩余一种商品
        assert updated_cart.items[0].sku_id == 67890  # 剩余的商品
    
    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, cart_service):
        """
        测试删除不存在的商品项
        
        验证删除不存在商品项时的处理逻辑。
        """
        # ================== 尝试删除不存在的商品项 ==================
        success = await cart_service.delete_item(user_id=1, item_id=99999)
        
        # ================== 验证返回结果 ==================
        assert success is False
    
    @pytest.mark.asyncio
    async def test_batch_delete_items(self, cart_service):
        """
        测试批量删除商品项
        
        验证一次性删除多个商品项的功能。
        """
        # ================== 添加多个商品 ==================
        requests = [
            AddItemRequest(sku_id=12345, quantity=1),
            AddItemRequest(sku_id=67890, quantity=2),
            AddItemRequest(sku_id=11111, quantity=3)
        ]
        
        for req in requests:
            await cart_service.add_item(user_id=1, request=req)
        
        # 获取购物车状态
        cart = await cart_service.get_cart(user_id=1)
        item_ids_to_delete = [item.item_id for item in cart.items[:2]]  # 删除前两个
        
        # ================== 批量删除 ==================
        success = await cart_service.batch_delete_items(user_id=1, item_ids=item_ids_to_delete)
        
        # ================== 验证删除结果 ==================
        assert success is True
        
        updated_cart = await cart_service.get_cart(user_id=1)
        assert updated_cart.total_items == 1  # 剩余一种商品
    
    @pytest.mark.asyncio
    async def test_clear_cart(self, cart_service):
        """
        测试清空购物车
        
        验证清空整个购物车的功能。
        """
        # ================== 添加多个商品 ==================
        requests = [
            AddItemRequest(sku_id=12345, quantity=2),
            AddItemRequest(sku_id=67890, quantity=1),
            AddItemRequest(sku_id=11111, quantity=3)
        ]
        
        for req in requests:
            await cart_service.add_item(user_id=1, request=req)
        
        # ================== 清空购物车 ==================
        success = await cart_service.clear_cart(user_id=1)
        
        # ================== 验证清空结果 ==================
        assert success is True
        
        empty_cart = await cart_service.get_cart(user_id=1)
        assert empty_cart.total_items == 0
        assert empty_cart.total_quantity == 0
        assert len(empty_cart.items) == 0
    
    @pytest.mark.asyncio
    async def test_clear_empty_cart(self, cart_service):
        """
        测试清空空购物车
        
        验证对不存在的购物车执行清空操作的处理逻辑。
        """
        # ================== 清空不存在的购物车 ==================
        success = await cart_service.clear_cart(user_id=999)
        
        # ================== 验证结果 ==================
        assert success is False


# ==================== 边界条件测试 ====================

class TestCartServiceEdgeCases:
    """
    购物车服务边界条件测试
    
    测试各种边界情况和异常场景，确保系统的稳定性和可靠性。
    """
    
    @pytest.mark.asyncio
    async def test_concurrent_add_same_item(self, cart_service):
        """
        测试并发添加相同商品
        
        模拟并发场景，验证数据一致性和事务隔离。
        """
        # ================== 模拟并发添加 ==================
        request = AddItemRequest(sku_id=12345, quantity=1)
        
        # 连续快速添加相同商品
        results = []
        for _ in range(5):
            result = await cart_service.add_item(user_id=1, request=request)
            results.append(result)
        
        # ================== 验证最终状态 ==================
        final_cart = await cart_service.get_cart(user_id=1)
        assert final_cart.total_quantity == 5  # 所有数量都被正确累加
        assert final_cart.total_items == 1     # 仍然只有一种商品
    
    @pytest.mark.asyncio
    async def test_price_calculation_precision(self, cart_service):
        """
        测试价格计算精度
        
        验证使用Decimal进行精确价格计算，避免浮点数精度问题。
        """
        # ================== 添加商品（价格为99.99） ==================
        request = AddItemRequest(sku_id=12345, quantity=3)
        result = await cart_service.add_item(user_id=1, request=request)
        
        # ================== 验证价格计算精度 ==================
        expected_total = Decimal("99.99") * 3  # 299.97
        assert result.total_amount == expected_total
        assert result.items[0].subtotal == expected_total
    
    @pytest.mark.asyncio 
    async def test_user_isolation(self, cart_service):
        """
        测试用户数据隔离
        
        验证不同用户的购物车数据完全隔离，不会相互影响。
        """
        # ================== 用户1添加商品 ==================
        request1 = AddItemRequest(sku_id=12345, quantity=2)
        await cart_service.add_item(user_id=1, request=request1)
        
        # ================== 用户2添加不同商品 ==================
        request2 = AddItemRequest(sku_id=67890, quantity=3)
        await cart_service.add_item(user_id=2, request=request2)
        
        # ================== 验证数据隔离 ==================
        cart1 = await cart_service.get_cart(user_id=1)
        cart2 = await cart_service.get_cart(user_id=2)
        
        assert cart1.user_id == 1
        assert cart2.user_id == 2
        assert cart1.items[0].sku_id == 12345
        assert cart2.items[0].sku_id == 67890
        assert cart1.total_items == 1
        assert cart2.total_items == 1


# ==================== 性能测试 ====================

class TestCartServicePerformance:
    """
    购物车服务性能测试
    
    测试大数据量和高并发场景下的性能表现。
    """
    
    @pytest.mark.asyncio
    async def test_large_cart_performance(self, cart_service):
        """
        测试大购物车性能
        
        验证购物车包含大量商品时的查询和操作性能。
        """
        import time
        
        # ================== 添加大量商品 ==================
        start_time = time.time()
        
        # 添加30种商品（接近限制但不超过）
        for i in range(30):
            request = AddItemRequest(sku_id=10000 + i, quantity=1)
            await cart_service.add_item(user_id=1, request=request)
        
        add_time = time.time() - start_time
        
        # ================== 测试查询性能 ==================
        query_start = time.time()
        result = await cart_service.get_cart(user_id=1)
        query_time = time.time() - query_start
        
        # ================== 性能断言 ==================
        assert result.total_items == 30
        assert add_time < 5.0    # 添加30个商品应在5秒内完成
        assert query_time < 1.0  # 查询应在1秒内完成
        
        print(f"添加30个商品耗时: {add_time:.2f}秒")
        print(f"查询购物车耗时: {query_time:.3f}秒")


if __name__ == "__main__":
    # 运行测试的示例命令
    print("购物车模块单元测试")
    print("运行命令：pytest tests/test_shopping_cart.py -v")
    print("覆盖率测试：pytest tests/test_shopping_cart.py --cov=app.modules.shopping_cart")
