"""
库存管理模块 - 模型单元测试

基于SQLite内存数据库的快速单元测试，测试模型的基本功能和业务逻辑。
遵循系统测试标准：
- AAA模式 (Arrange-Act-Assert)
- 独立性原则
- 清晰的测试命名
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError

from app.modules.inventory_management.models import (
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType, AdjustmentType
)


class TestInventoryStock:
    """测试库存表模型"""
    
    def test_create_inventory_stock_success(self, unit_test_db):
        """测试创建库存记录 - 成功场景"""
        # Arrange
        from app.modules.product_catalog.models import SKU, Product
        
        # 先创建产品
        product = Product(
            name="测试产品001",
            description="测试产品描述",
            status="active",
            category_id=1
        )
        unit_test_db.add(product)
        unit_test_db.flush()
        
        # 创建SKU
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-SKU-001",
            price=100.0,
            cost=60.0,
            weight=1.0
        )
        unit_test_db.add(sku)
        unit_test_db.flush()
        
        initial_quantity = 100
        
        # Act
        stock = InventoryStock(
            sku_id=sku.id,
            total_quantity=initial_quantity,
            available_quantity=initial_quantity,
            reserved_quantity=0,
            warning_threshold=10,
            critical_threshold=5
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        unit_test_db.refresh(stock)
        
        # Assert
        assert stock.id is not None
        assert stock.sku_id == sku.id
        assert stock.total_quantity == initial_quantity
        assert stock.available_quantity == initial_quantity
        assert stock.reserved_quantity == 0
        assert stock.is_active is True
        assert stock.created_at is not None
        assert stock.updated_at is not None
    
    def test_create_inventory_stock_duplicate_sku_should_fail(self, unit_test_db):
        """测试创建重复SKU库存记录 - 应该失败"""
        # Arrange
        from app.modules.product_catalog.models import SKU, Product
        
        # 创建产品和SKU
        product = Product(
            name="测试产品002",
            description="测试产品描述",
            status="active",
            category_id=1
        )
        unit_test_db.add(product)
        unit_test_db.flush()
        
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-SKU-002",
            price=200.0,
            cost=120.0,
            weight=2.0
        )
        unit_test_db.add(sku)
        unit_test_db.flush()
        
        # Act & Assert
        # 创建第一个记录
        stock1 = InventoryStock(sku_id=sku.id, total_quantity=100, available_quantity=100)
        unit_test_db.add(stock1)
        unit_test_db.commit()
        
        # 尝试创建重复SKU记录，应该失败
        stock2 = InventoryStock(sku_id=sku.id, total_quantity=50, available_quantity=50)
        unit_test_db.add(stock2)
        
        with pytest.raises(IntegrityError):
            unit_test_db.commit()
    
    def test_inventory_stock_properties_low_stock_warning(self, unit_test_db):
        """测试库存属性 - 低库存预警"""
        # Arrange
        from app.modules.product_catalog.models import SKU, Product
        
        # 创建产品和SKU
        product = Product(
            name="测试产品003",
            description="测试产品描述",
            status="active",
            category_id=1
        )
        unit_test_db.add(product)
        unit_test_db.flush()
        
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-SKU-003",
            price=300.0,
            cost=180.0,
            weight=3.0
        )
        unit_test_db.add(sku)
        unit_test_db.flush()
        
        stock = InventoryStock(
            sku_id=sku.id,
            total_quantity=8,
            available_quantity=8,
            warning_threshold=10,
            critical_threshold=5
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act & Assert - 检查低库存状态
        assert stock.is_low_stock is True
        assert stock.is_critical_stock is False
        assert stock.is_out_of_stock is False
    
    def test_inventory_stock_properties_critical_stock_warning(self, unit_test_db):
        """测试库存属性 - 紧急库存预警"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=3,
            available_quantity=3,
            warning_threshold=10,
            critical_threshold=5
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act & Assert - 检查紧急库存状态
        assert stock.is_low_stock is True
        assert stock.is_critical_stock is True
        assert stock.is_out_of_stock is False
    
    def test_inventory_stock_properties_out_of_stock(self, unit_test_db):
        """测试库存属性 - 缺货状态"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=0,
            available_quantity=0,
            warning_threshold=10,
            critical_threshold=5
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act & Assert - 检查缺货状态
        assert stock.is_low_stock is True
        assert stock.is_critical_stock is True
        assert stock.is_out_of_stock is True
    
    def test_inventory_stock_can_fulfill_order_sufficient_stock(self, unit_test_db):
        """测试库存检查 - 库存充足"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act & Assert - 测试不同数量的订单
        assert stock.can_reserve(50) is True
        assert stock.can_reserve(80) is True
        assert stock.can_reserve(1) is True
    
    def test_inventory_stock_can_fulfill_order_insufficient_stock(self, unit_test_db):
        """测试库存检查 - 库存不足"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=30,
            reserved_quantity=70
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act & Assert - 测试超出可用库存的订单
        assert stock.can_reserve(40) is False
        assert stock.can_reserve(31) is False
        assert stock.can_reserve(30) is True


class TestInventoryReservation:
    """测试库存预占模型"""
    
    def test_create_inventory_reservation_success(self, unit_test_db):
        """测试创建库存预占记录 - 成功场景"""
        # Arrange
        # 先创建库存记录
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=100
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        unit_test_db.refresh(stock)
        
        # Act - 创建预占记录
        reservation = InventoryReservation(
            sku_id=stock.sku_id,
            quantity=10,
            reservation_type=ReservationType.CART,
            reference_id="cart_123",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2)
        )
        unit_test_db.add(reservation)
        unit_test_db.commit()
        unit_test_db.refresh(reservation)
        
        # Assert
        assert reservation.id is not None
        assert reservation.sku_id == stock.sku_id
        assert reservation.quantity == 10
        assert reservation.reservation_type == ReservationType.CART
        assert reservation.reference_id == "cart_123"
        assert reservation.is_active is True
        assert reservation.expires_at is not None
        assert reservation.created_at is not None
    
    def test_inventory_reservation_is_expired_true(self, unit_test_db):
        """测试预占过期检查 - 已过期"""
        # Arrange
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        reservation = InventoryReservation(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            quantity=5,
            reservation_type=ReservationType.ORDER,
            reference_id="order_456",
            expires_at=expired_time
        )
        unit_test_db.add(reservation)
        unit_test_db.commit()
        
        # Act & Assert
        assert reservation.is_expired is True
    
    def test_inventory_reservation_is_expired_false(self, unit_test_db):
        """测试预占过期检查 - 未过期"""
        # Arrange
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        reservation = InventoryReservation(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            quantity=5,
            reservation_type=ReservationType.ORDER,
            reference_id="order_789",
            expires_at=future_time
        )
        unit_test_db.add(reservation)
        unit_test_db.commit()
        
        # Act & Assert
        assert reservation.is_expired is False


class TestInventoryTransaction:
    """测试库存事务模型"""
    
    def test_create_inventory_transaction_success(self, unit_test_db):
        """测试创建库存事务记录 - 成功场景"""
        # Arrange
        # 先创建库存记录
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=100
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        unit_test_db.refresh(stock)
        
        # Act - 创建事务记录
        transaction = InventoryTransaction(
            sku_id=stock.sku_id,
            transaction_type=TransactionType.DEDUCT,
            quantity_change=-10,
            quantity_before=100,
            quantity_after=90,
            reference_type="order",
            reference_id="order_123",
            reason="订单扣减库存",
            operator_id=1
        )
        unit_test_db.add(transaction)
        unit_test_db.commit()
        unit_test_db.refresh(transaction)
        
        # Assert
        assert transaction.id is not None
        assert transaction.sku_id == stock.sku_id
        assert transaction.transaction_type == TransactionType.DEDUCT
        assert transaction.quantity_change == -10
        assert transaction.quantity_before == 100
        assert transaction.quantity_after == 90
        assert transaction.reference_type == "order"
        assert transaction.reference_id == "order_123"
        assert transaction.reason == "订单扣减库存"
        assert transaction.operator_id == 1
        assert transaction.created_at is not None
    
    def test_inventory_transaction_different_types(self, unit_test_db):
        """测试不同类型的库存事务"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=100
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act - 创建不同类型的事务
        transactions = [
            InventoryTransaction(
                sku_id=stock.sku_id,
                transaction_type=TransactionType.RESTOCK,
                quantity_change=50,
                quantity_before=100,
                quantity_after=150,
                reference_type="purchase",
                reference_id="purchase_001"
            ),
            InventoryTransaction(
                sku_id=stock.sku_id,
                transaction_type=TransactionType.DEDUCT,
                quantity_change=-20,
                quantity_before=150,
                quantity_after=130,
                reference_type="order",
                reference_id="order_001"
            ),
            InventoryTransaction(
                sku_id=stock.sku_id,
                transaction_type=TransactionType.ADJUST,
                quantity_change=5,
                quantity_before=130,
                quantity_after=135,
                reference_type="adjustment",
                reference_id="adj_001"
            )
        ]
        
        for tx in transactions:
            unit_test_db.add(tx)
        unit_test_db.commit()
        
        # Assert - 验证每种类型的事务都被正确创建
        saved_transactions = unit_test_db.query(InventoryTransaction).filter(
            InventoryTransaction.sku_id == stock.sku_id
        ).all()
        
        assert len(saved_transactions) == 3
        
        types = [tx.transaction_type for tx in saved_transactions]
        assert TransactionType.RESTOCK in types
        assert TransactionType.DEDUCT in types
        assert TransactionType.ADJUST in types


class TestInventoryStockBusinessLogic:
    """测试库存模型的业务逻辑方法"""
    
    def test_adjust_quantity_success(self, unit_test_db):
        """测试调整库存数量 - 成功场景"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act - 增加库存
        result = stock.adjust_quantity(AdjustmentType.INCREASE, 50)
        unit_test_db.commit()
        
        # Assert
        assert result is True
        assert stock.total_quantity == 150
        assert stock.available_quantity == 130
        assert stock.reserved_quantity == 20
        # updated_at 应该被自动更新
        assert stock.updated_at is not None
    
    def test_reserve_quantity_success(self, unit_test_db):
        """测试预占库存 - 成功场景"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=100,
            reserved_quantity=0
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act
        result = stock.reserve_quantity(30)
        unit_test_db.commit()
        
        # Assert
        assert result is True
        assert stock.available_quantity == 70
        assert stock.reserved_quantity == 30
        assert stock.total_quantity == 100  # 总量不变
    
    def test_reserve_quantity_insufficient_stock(self, unit_test_db):
        """测试预占库存 - 库存不足"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=20,
            reserved_quantity=80
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act
        result = stock.reserve_quantity(30)
        
        # Assert
        assert result is False
        # 数量应该保持不变
        assert stock.available_quantity == 20
        assert stock.reserved_quantity == 80
        assert stock.total_quantity == 100
    
    def test_release_quantity_success(self, unit_test_db):
        """测试释放预占库存 - 成功场景"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=70,
            reserved_quantity=30
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act
        result = stock.release_quantity(20)
        unit_test_db.commit()
        
        # Assert
        assert result is True
        assert stock.available_quantity == 90
        assert stock.reserved_quantity == 10
        assert stock.total_quantity == 100  # 总量不变
    
    def test_release_quantity_excessive_amount(self, unit_test_db):
        """测试释放预占库存 - 释放数量超出预占量"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act
        result = stock.release_quantity(30)  # 试图释放30，但只有20预占
        
        # Assert
        assert result is False
        # 数量应该保持不变
        assert stock.available_quantity == 80
        assert stock.reserved_quantity == 20
        assert stock.total_quantity == 100
    
    def test_deduct_quantity_success(self, unit_test_db):
        """测试扣减库存 - 成功场景"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=50,
            reserved_quantity=50
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act
        result = stock.deduct_quantity(30, from_reserved=True)
        unit_test_db.commit()
        
        # Assert
        assert result is True
        assert stock.total_quantity == 70  # 总量减少
        assert stock.reserved_quantity == 20  # 预占量减少
        assert stock.available_quantity == 50  # 可用量不变
    
    def test_deduct_quantity_insufficient_reserved(self, unit_test_db):
        """测试扣减库存 - 预占量不足"""
        # Arrange
        stock = InventoryStock(
            sku_id=test_sku.id  # 🔧 修复：使用SKU对象的ID,
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20
        )
        unit_test_db.add(stock)
        unit_test_db.commit()
        
        # Act
        result = stock.deduct_quantity(30, from_reserved=True)  # 试图扣减30，但只有20预占
        
        # Assert
        assert result is False
        # 数量应该保持不变
        assert stock.total_quantity == 100
        assert stock.available_quantity == 80
        assert stock.reserved_quantity == 20