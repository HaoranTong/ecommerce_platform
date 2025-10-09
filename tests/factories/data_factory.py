"""
统一测试数据工厂 - 跨模块集成测试专用

📋 **使用场景**：
- ✅ 集成测试 (tests/integration/) - 真实数据库环境
- ✅ E2E测试 (tests/e2e/) - 完整业务流程测试
- ✅ 烟雾测试 (tests/smoke/) - 基础功能验证
- ✅ 跨模块业务测试 - 完整数据链创建
- ❌ 单元测试 - 推荐使用模块专用Factory Boy工厂

📊 **与专用Factory Boy的分工**：
- **本工厂(统一工厂)**: 真实数据库、集成测试、业务流程测试
- **专用工厂(Factory Boy)**: Mock测试、单元测试、复杂关系测试

🎯 **核心优势**：
- 跨模块数据链创建 (用户→分类→品牌→商品→SKU→库存→订单)
- 数据类型安全保证 (解决sku_id类型问题)
- 真实数据库环境优化
- 支持完整业务流程数据准备

🔧 **使用方法**：
```python
# 集成测试中使用 - 推荐场景
from tests.factories.data_factory import StandardTestDataFactory

def test_complete_order_workflow(integration_test_db):
    # 创建完整业务数据链
    user, category, brand, product, sku = StandardTestDataFactory.create_complete_chain(integration_test_db)

    # 确保数据类型正确
    assert isinstance(sku.id, int)  # ✅ sku_id是整数
    assert isinstance(sku.sku_code, str)  # ✅ sku_code是字符串

    # 进行集成测试
    order_service = OrderService(integration_test_db)
    result = order_service.create_order(user.id, sku.id, quantity=2)
    assert result.success is True

# 单独创建各种数据
user = StandardTestDataFactory.create_user(db, username="testuser")
product = StandardTestDataFactory.create_product(db, name="测试商品")
```

🚨 **重要说明**：
- 确保所有测试都使用正确的数据类型 (sku_id必须是整数)
- 适用于需要真实数据库操作的测试场景
- 自动处理数据关联和完整性约束
- 与SQLite内存数据库、MySQL Docker完美配合

⚠️ **数据类型问题解决方案**：
本工厂专门解决了以下常见问题：
- sku_id类型混乱 (确保使用整数ID而非字符串)
- 外键关系错误
- 数据完整性约束违反
- 跨模块数据创建复杂性

---

创建时间: 2025-09-20
更新时间: 2025-09-25 22:35:00
支持模块: user_auth, product_catalog, shopping_cart, inventory_management, order_management
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.inventory_management.models import (AdjustmentType,
                                                     InventoryReservation,
                                                     InventoryStock,
                                                     InventoryTransaction,
                                                     ReservationType,
                                                     TransactionType)
from app.modules.product_catalog.models import SKU, Brand, Category, Product
from app.modules.shopping_cart.models import CartItem
from app.modules.user_auth.models import Role, User


class StandardTestDataFactory:
    """标准测试数据工厂 - 确保正确的数据类型"""

    def create_sample_data(self) -> dict:
        """创建样本测试数据 - [CHECK:TEST-002] 测试数据一致性验证

        Returns:
            dict: 包含测试场景所需的样本数据
        """
        return {
            "user_data": {
                "username": "test_user",
                "email": "test@example.com",
                "password": "test_password_123",
            },
            "test_scenarios": [
                "user_registration",
                "user_authentication",
                "password_validation",
            ],
        }

    @staticmethod
    def create_user(db: Session, **kwargs) -> User:
        """创建测试用户"""
        import random
        # 生成符合中国手机号格式的测试号码：1[3-9]xxxxxxxxx
        microsecond = datetime.now().microsecond
        second_digit = random.randint(3, 9)  # 第二位必须是3-9
        remaining_digits = f"{random.randint(0, 999999999):09d}"  # 后9位
        
        defaults = {
            "username": f"testuser_{microsecond}",
            "email": f"test_{microsecond}@example.com",
            "password_hash": "hashed_password_123",
            "is_active": True,
            "email_verified": True,
            "status": "active",  # 必需字段
            "phone_verified": False,  # 必需字段
            "two_factor_enabled": False,  # 必需字段
            "failed_login_attempts": 0,
            "phone": f"1{second_digit}{remaining_digits}",  # 符合 ^1[3-9]\d{9}$ 格式
            "real_name": f"测试用户_{microsecond}",
            "role": "user",
            "created_at": datetime.now(),  # 必需字段
            "updated_at": datetime.now(),  # 必需字段
        }
        defaults.update(kwargs)

        user = User(**defaults)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_category(db: Session, **kwargs) -> Category:
        """创建测试分类"""
        defaults = {
            "name": f"测试分类_{datetime.now().microsecond}",
            "description": "测试分类描述",
            "is_active": True,
            "sort_order": 1,
        }
        defaults.update(kwargs)

        category = Category(**defaults)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def create_brand(db: Session, **kwargs) -> Brand:
        """创建测试品牌"""
        import uuid

        unique_id = datetime.now().microsecond
        defaults = {
            "name": f"测试品牌_{unique_id}",
            "slug": f"test-brand-{str(uuid.uuid4())[:8]}",  # 添加必需的slug字段
            "description": "测试品牌描述",
            "is_active": True,
        }
        defaults.update(kwargs)

        brand = Brand(**defaults)
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand

    @staticmethod
    def create_product(
        db: Session, category_id: int, brand_id: int, **kwargs
    ) -> Product:
        """创建测试商品

        Args:
            category_id: 分类ID（整数）
            brand_id: 品牌ID（整数）
        """
        defaults = {
            "name": f"测试商品_{datetime.now().microsecond}",
            "description": "测试商品描述",
            "category_id": category_id,
            "brand_id": brand_id,
            "status": "published",  # 修正status值，移除不存在的is_active字段
        }
        defaults.update(kwargs)

        product = Product(**defaults)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def create_sku(db: Session, product_id: int, **kwargs) -> SKU:
        """创建测试SKU - 关键：返回整数ID

        Args:
            product_id: 商品ID（整数）

        Returns:
            SKU对象，其中sku.id是整数类型（用于外键）
        """
        defaults = {
            "product_id": product_id,
            "sku_code": f"SKU_{datetime.now().microsecond}",
            "name": f"测试SKU_{datetime.now().microsecond}",
            "price": Decimal("99.99"),
            "cost_price": Decimal("50.00"),
            "weight": Decimal("1.0"),
            "is_active": True,
        }
        defaults.update(kwargs)

        sku = SKU(**defaults)
        db.add(sku)
        db.commit()
        db.refresh(sku)

        # 验证返回的ID是数值类型（支持int和long类型）
        assert isinstance(
            sku.id, (int, type(2**63))
        ), f"SKU ID必须是数值类型，当前类型: {type(sku.id)}"
        assert isinstance(
            sku.sku_code, str
        ), f"SKU代码必须是字符串，当前类型: {type(sku.sku_code)}"

        # 确保ID可以用作外键（转换为int如果需要）
        if not isinstance(sku.id, int):
            sku.id = int(sku.id)

        return sku

    @staticmethod
    def create_inventory_stock(db: Session, sku_id: int, **kwargs) -> InventoryStock:
        """创建库存记录

        Args:
            sku_id: SKU的ID（整数，不是sku_code！）
        """
        if not isinstance(sku_id, int):
            raise ValueError(f"sku_id必须是整数类型，当前类型: {type(sku_id)}")

        defaults = {
            "sku_id": sku_id,
            "available_quantity": 100,
            "reserved_quantity": 0,
            "total_quantity": 100,
            "warning_threshold": 10,
            "critical_threshold": 5,
            "is_active": True,
        }
        defaults.update(kwargs)

        inventory = InventoryStock(**defaults)
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
        return inventory

    @staticmethod
    def create_inventory_reservation(
        db: Session, sku_id: int, **kwargs
    ) -> InventoryReservation:
        """创建库存预占记录

        Args:
            sku_id: SKU的ID（整数，不是sku_code！）
        """
        if not isinstance(sku_id, int):
            raise ValueError(f"sku_id必须是整数类型，当前类型: {type(sku_id)}")

        import uuid
        from datetime import datetime, timedelta, timezone

        defaults = {
            "sku_id": sku_id,
            "reserved_quantity": 10,
            "reservation_type": ReservationType.CART,
            "reference_id": f"TEST-REF-{uuid.uuid4().hex[:8]}",
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=2),
            "is_active": True,
        }
        defaults.update(kwargs)

        reservation = InventoryReservation(**defaults)
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    @staticmethod
    def create_inventory_transaction(
        db: Session, sku_id: int, **kwargs
    ) -> InventoryTransaction:
        """创建库存事务记录

        Args:
            sku_id: SKU的ID（整数，不是sku_code！）
        """
        if not isinstance(sku_id, int):
            raise ValueError(f"sku_id必须是整数类型，当前类型: {type(sku_id)}")

        import uuid

        defaults = {
            "sku_id": sku_id,
            "transaction_type": TransactionType.DEDUCT,
            "quantity": 10,
            "reference_type": "order",
            "reference_id": f"TEST-TX-{uuid.uuid4().hex[:8]}",
            "reason": "测试事务",
            "operator_id": "test_admin",
        }
        defaults.update(kwargs)

        transaction = InventoryTransaction(**defaults)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def create_cart_item(db: Session, user_id: int, sku_id: int, **kwargs) -> CartItem:
        """创建购物车项目

        Args:
            user_id: 用户ID（整数）
            sku_id: SKU的ID（整数，不是sku_code！）
        """
        if not isinstance(sku_id, int):
            raise ValueError(f"sku_id必须是整数类型，当前类型: {type(sku_id)}")

        defaults = {
            "user_id": user_id,
            "sku_id": sku_id,
            "quantity": 1,
            "unit_price": Decimal("99.99"),
            "total_price": Decimal("99.99"),
        }
        defaults.update(kwargs)

        cart_item = CartItem(**defaults)
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def create_complete_chain(
        db: Session,
    ) -> tuple[User, Category, Brand, Product, SKU]:
        """创建完整的测试数据链

        Returns:
            (user, category, brand, product, sku) - 所有ID都是正确的整数类型
        """
        user = StandardTestDataFactory.create_user(db)
        category = StandardTestDataFactory.create_category(db)
        brand = StandardTestDataFactory.create_brand(db)
        product = StandardTestDataFactory.create_product(
            db, category_id=category.id, brand_id=brand.id
        )
        sku = StandardTestDataFactory.create_sku(db, product_id=product.id)

        # 验证所有ID都是整数
        assert isinstance(user.id, int)
        assert isinstance(category.id, int)
        assert isinstance(brand.id, int)
        assert isinstance(product.id, int)
        assert isinstance(sku.id, int)

        return user, category, brand, product, sku


class TestDataValidator:
    """测试数据验证器 - 防止sku_id类型错误"""

    @staticmethod
    def validate_sku_id(sku_id) -> None:
        """验证sku_id必须是整数"""
        if not isinstance(sku_id, int):
            raise TypeError(
                f"❌ sku_id必须是整数类型（SKU表的主键id），当前类型: {type(sku_id)}\n"
                f"💡 正确用法: sku_id=sku.id (整数)\n"
                f"❌ 错误用法: sku_id=sku.id  # 🔧 修复：使用整数ID而不是字符串 (字符串)"
            )

    @staticmethod
    def validate_foreign_key_ids(**kwargs) -> None:
        """验证所有外键ID都是整数"""
        for field_name, value in kwargs.items():
            if field_name.endswith("_id") and value is not None:
                if not isinstance(value, int):
                    raise TypeError(
                        f"❌ {field_name}必须是整数类型，当前类型: {type(value)}"
                    )

    @staticmethod
    def validate_inventory_response(data: dict, expected_fields: list = None) -> None:
        """验证库存响应数据格式"""
        if expected_fields is None:
            expected_fields = [
                "sku_id",
                "total_quantity",
                "available_quantity",
                "reserved_quantity",
                "is_low_stock",
                "is_active",
            ]

        for field in expected_fields:
            assert field in data, f"响应数据缺少字段: {field}"

        assert isinstance(data["total_quantity"], int), "total_quantity 应该是整数"
        assert isinstance(
            data["available_quantity"], int
        ), "available_quantity 应该是整数"
        assert isinstance(
            data["reserved_quantity"], int
        ), "reserved_quantity 应该是整数"
        assert isinstance(data["is_low_stock"], bool), "is_low_stock 应该是布尔值"
        assert isinstance(data["is_active"], bool), "is_active 应该是布尔值"

    @staticmethod
    def verify_stock_quantities(
        stock: InventoryStock,
        expected_total: int,
        expected_available: int,
        expected_reserved: int,
    ) -> None:
        """验证库存数量"""
        assert (
            stock.total_quantity == expected_total
        ), f"总库存不匹配: 期望 {expected_total}, 实际 {stock.total_quantity}"
        assert (
            stock.available_quantity == expected_available
        ), f"可用库存不匹配: 期望 {expected_available}, 实际 {stock.available_quantity}"
        assert (
            stock.reserved_quantity == expected_reserved
        ), f"预占库存不匹配: 期望 {expected_reserved}, 实际 {stock.reserved_quantity}"


# 便捷函数
def create_test_sku_with_validation(db: Session, product_id: int) -> SKU:
    """创建测试SKU并验证类型正确性"""
    TestDataValidator.validate_foreign_key_ids(product_id=product_id)
    return StandardTestDataFactory.create_sku(db, product_id)


def get_sku_id_safely(db: Session, sku_code: str = None, product_id: int = None) -> int:
    """安全获取SKU的整数ID

    Args:
        sku_code: SKU代码（可选）
        product_id: 如果没有找到，创建新的SKU

    Returns:
        整数类型的SKU ID
    """
    if sku_code:
        sku = db.query(SKU).filter(SKU.sku_code == sku_code).first()
        if sku:
            return sku.id

    # 如果没有找到，创建新的SKU
    if product_id:
        sku = StandardTestDataFactory.create_sku(db, product_id)
        return sku.id

    raise ValueError("必须提供sku_code或product_id")


# 库存测试便捷函数
def create_low_stock_scenario(db: Session, sku_id: int) -> InventoryStock:
    """创建低库存场景"""
    return StandardTestDataFactory.create_inventory_stock(
        db,
        sku_id,
        total_quantity=12,
        available_quantity=8,
        reserved_quantity=4,
        warning_threshold=15,
        critical_threshold=8,
    )


def create_critical_stock_scenario(db: Session, sku_id: int) -> InventoryStock:
    """创建紧急库存场景"""
    return StandardTestDataFactory.create_inventory_stock(
        db,
        sku_id,
        total_quantity=6,
        available_quantity=3,
        reserved_quantity=3,
        warning_threshold=15,
        critical_threshold=8,
    )


def create_out_of_stock_scenario(db: Session, sku_id: int) -> InventoryStock:
    """创建缺货场景"""
    return StandardTestDataFactory.create_inventory_stock(
        db,
        sku_id,
        total_quantity=0,
        available_quantity=0,
        reserved_quantity=0,
        warning_threshold=10,
        critical_threshold=5,
    )
