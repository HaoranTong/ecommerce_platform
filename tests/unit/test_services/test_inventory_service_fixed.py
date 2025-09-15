"""
库存管理服务层单元测试

测试库存管理服务类的所有业务逻辑，使用Mock对象隔离数据库依赖
遵循AAA测试模式（Arrange-Act-Assert）
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta, timezone

from app.modules.inventory_management.service import InventoryService
from app.modules.inventory_management.models import (
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType
)


class TestInventoryServiceGetOperations:
    """测试库存服务的查询操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_get_sku_inventory_success(self, inventory_service, mock_db):
        """测试获取SKU库存 - 成功场景"""
        # Arrange
        sku_id = "TEST-SKU-001"
        mock_inventory = Mock()
        mock_inventory.id = 1
        mock_inventory.sku_id = sku_id
        mock_inventory.total_quantity = 100
        mock_inventory.available_quantity = 80
        mock_inventory.reserved_quantity = 20
        mock_inventory.warning_threshold = 10
        mock_inventory.critical_threshold = 5
        mock_inventory.is_low_stock = False
        mock_inventory.is_critical_stock = False
        mock_inventory.is_out_of_stock = False
        mock_inventory.is_active = True
        mock_inventory.updated_at = datetime.now(timezone.utc)

        mock_db.query.return_value.filter.return_value.first.return_value = mock_inventory

        # Act
        result = await inventory_service.get_sku_inventory(sku_id)

        # Assert
        assert result is not None
        assert result["sku_id"] == sku_id
        assert result["total_quantity"] == 100
        assert result["available_quantity"] == 80
        assert result["reserved_quantity"] == 20

    @pytest.mark.asyncio
    async def test_get_sku_inventory_not_found(self, inventory_service, mock_db):
        """测试获取SKU库存 - SKU不存在"""
        # Arrange
        sku_id = "NONEXISTENT-SKU"
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = await inventory_service.get_sku_inventory(sku_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_batch_inventory_success(self, inventory_service, mock_db):
        """测试批量获取库存 - 成功场景"""
        # Arrange
        sku_ids = ["SKU-001", "SKU-002"]
        mock_inventories = []
        for i, sku_id in enumerate(sku_ids):
            mock_inv = Mock()
            mock_inv.sku_id = sku_id
            mock_inv.available_quantity = 50 + i * 10
            mock_inv.reserved_quantity = 10 + i * 5
            mock_inv.total_quantity = 60 + i * 15
            mock_inv.is_low_stock = False
            mock_inventories.append(mock_inv)

        mock_db.query.return_value.filter.return_value.all.return_value = mock_inventories

        # Act
        result = await inventory_service.get_batch_inventory(sku_ids)

        # Assert
        assert len(result) == 2
        assert result[0]["sku_id"] == "SKU-001"
        assert result[1]["sku_id"] == "SKU-002"


class TestInventoryServiceCreateOperations:
    """测试库存服务的创建操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_create_sku_inventory_success(self, inventory_service, mock_db):
        """测试创建SKU库存记录 - 成功场景"""
        # Arrange
        inventory_data = {
            "sku_id": "NEW-SKU-001",
            "initial_quantity": 100,
            "warning_threshold": 15,
            "critical_threshold": 8
        }

        # Mock: 不存在重复记录，创建成功后的查询结果
        mock_created_inventory = Mock()
        mock_created_inventory.id = 1
        mock_created_inventory.sku_id = "NEW-SKU-001"
        mock_created_inventory.total_quantity = 100
        mock_created_inventory.available_quantity = 100
        mock_created_inventory.reserved_quantity = 0
        mock_created_inventory.warning_threshold = 15
        mock_created_inventory.critical_threshold = 8
        mock_created_inventory.is_low_stock = False
        mock_created_inventory.is_critical_stock = False
        mock_created_inventory.is_out_of_stock = False
        mock_created_inventory.is_active = True
        mock_created_inventory.updated_at = datetime.now(timezone.utc)

        # 第一次查询返回None（不存在），第二次返回创建的记录
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_created_inventory]
        
        # Act
        result = await inventory_service.create_sku_inventory(inventory_data)
        
        # Assert
        assert result is not None
        assert result["sku_id"] == "NEW-SKU-001"
        assert result["total_quantity"] == 100
        assert mock_db.add.call_count == 2  # 库存记录 + 事务记录
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_sku_inventory_duplicate_should_fail(self, inventory_service, mock_db):
        """测试创建SKU库存记录 - 重复SKU应该失败"""
        # Arrange
        inventory_data = {
            "sku_id": "EXISTING-SKU",
            "initial_quantity": 100
        }
        
        # Mock: 已存在记录
        existing_inventory = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_inventory

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await inventory_service.create_sku_inventory(inventory_data)
        
        assert "已存在" in str(exc_info.value)


class TestInventoryServiceReservationOperations:
    """测试库存服务的预占操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_reserve_inventory_success(self, inventory_service, mock_db):
        """测试库存预占 - 成功场景"""
        # Arrange
        items = [
            {"sku_id": "SKU-001", "quantity": 10},
            {"sku_id": "SKU-002", "quantity": 5}
        ]

        # Mock: 库存充足
        mock_stocks = []
        for item in items:
            mock_stock = Mock()
            mock_stock.sku_id = item["sku_id"]
            mock_stock.available_quantity = 100
            mock_stock.can_reserve.return_value = True
            mock_stock.reserve_quantity.return_value = True
            mock_stocks.append(mock_stock)

        # Mock with_for_update chain
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.side_effect = mock_stocks

        # Act
        result = await inventory_service.reserve_inventory(
            reservation_type=ReservationType.CART,
            reference_id="cart_123",
            items=items,
            expires_minutes=120,
            user_id=1
        )

        # Assert
        assert result is not None
        assert "reservation_id" in result
        assert "expires_at" in result
        assert "reserved_items" in result
        assert len(result["reserved_items"]) == 2
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_reserve_inventory_insufficient_stock(self, inventory_service, mock_db):
        """测试库存预占 - 库存不足"""
        # Arrange
        items = [{"sku_id": "SKU-003", "quantity": 100}]  # 数量过大

        # Mock: 库存不足
        mock_stock = Mock()
        mock_stock.sku_id = "SKU-003"
        mock_stock.available_quantity = 10
        mock_stock.can_reserve.return_value = False

        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_stock
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await inventory_service.reserve_inventory(
                reservation_type=ReservationType.CART,
                reference_id="cart_456",
                items=items,
                expires_minutes=120,
                user_id=1
            )
        
        assert "库存不足" in str(exc_info.value)


class TestInventoryServiceDeductOperations:
    """测试库存服务的扣减操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_deduct_inventory_success(self, inventory_service, mock_db):
        """测试库存扣减 - 成功场景"""
        # Arrange
        items = [
            {"sku_id": "SKU-001", "quantity": 5},
            {"sku_id": "SKU-002", "quantity": 3}
        ]

        # Mock: 库存充足
        mock_stocks = []
        for item in items:
            mock_stock = Mock()
            mock_stock.sku_id = item["sku_id"]
            mock_stock.total_quantity = 100
            mock_stock.reserved_quantity = 20
            mock_stock.deduct_quantity.return_value = True
            mock_stocks.append(mock_stock)

        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.side_effect = mock_stocks
        
        # Act
        result = await inventory_service.deduct_inventory(
            order_id="order_123",
            items=items,
            operator_id=1
        )

        # Assert
        assert result is not None
        assert result["order_id"] == "order_123"
        assert "deducted_items" in result
        assert len(result["deducted_items"]) == 2
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_deduct_inventory_insufficient_reserved(self, inventory_service, mock_db):
        """测试库存扣减 - 预占量不足"""
        # Arrange
        items = [{"sku_id": "SKU-004", "quantity": 50}]  # 超出预占量

        # Mock: 预占量不足
        mock_stock = Mock()
        mock_stock.sku_id = "SKU-004"
        mock_stock.reserved_quantity = 10
        mock_stock.deduct_quantity.return_value = False

        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_stock
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await inventory_service.deduct_inventory(
                order_id="order_456", 
                items=items,
                operator_id=1
            )
        
        assert "库存不足" in str(exc_info.value) or "预占" in str(exc_info.value)


class TestInventoryServiceThresholdOperations:
    """测试库存服务的阈值更新操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_update_thresholds_success(self, inventory_service, mock_db):
        """测试更新库存阈值 - 成功场景"""
        # Arrange
        sku_id = "SKU-005"
        warning_threshold = 15
        critical_threshold = 8

        # Mock: 存在库存记录
        mock_stock = Mock()
        mock_stock.sku_id = sku_id
        mock_stock.warning_threshold = 10
        mock_stock.critical_threshold = 5

        mock_db.query.return_value.filter.return_value.first.return_value = mock_stock
        
        # Act
        result = await inventory_service.update_thresholds(sku_id, warning_threshold, critical_threshold)
        
        # Assert
        assert result is True
        assert mock_stock.warning_threshold == warning_threshold
        assert mock_stock.critical_threshold == critical_threshold
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_thresholds_sku_not_found(self, inventory_service, mock_db):
        """测试更新库存阈值 - SKU不存在"""
        # Arrange
        sku_id = "NONEXISTENT-SKU"
        warning_threshold = 15
        critical_threshold = 8

        # Mock: SKU不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = await inventory_service.update_thresholds(sku_id, warning_threshold, critical_threshold)
        
        # Assert
        assert result is False
        mock_db.commit.assert_not_called()


class TestInventoryServiceReleaseOperations:
    """测试库存服务的预占释放操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_release_reservation_success(self, inventory_service, mock_db):
        """测试释放预占 - 成功场景"""
        # Arrange
        reservation_id = "reservation_123"

        # Mock: 存在有效的预占记录
        mock_reservation = Mock()
        mock_reservation.sku_id = "SKU-008"
        mock_reservation.quantity = 15
        mock_reservation.is_active = True

        mock_stock = Mock()
        mock_stock.sku_id = "SKU-008"
        mock_stock.release_quantity.return_value = True

        # Mock设置要按照实际调用链
        def mock_query_side_effect(model_class):
            query_mock = Mock()
            if model_class == InventoryReservation:
                # InventoryReservation查询链: query().filter().all()
                query_mock.filter.return_value.all.return_value = [mock_reservation]
            elif model_class == InventoryStock:
                # InventoryStock查询链: query().filter().with_for_update().first()
                query_mock.filter.return_value.with_for_update.return_value.first.return_value = mock_stock
            return query_mock

        mock_db.query.side_effect = mock_query_side_effect

        # Act
        result = await inventory_service.release_reservation(reservation_id, user_id=1)
        
        # Assert
        assert result is True
        assert mock_reservation.is_active is False
        mock_stock.release_quantity.assert_called_once_with(15)
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_release_reservation_not_found(self, inventory_service, mock_db):
        """测试释放预占 - 预占记录不存在"""
        # Arrange
        reservation_id = "nonexistent_reservation"

        # Mock: 预占记录不存在
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Act
        result = await inventory_service.release_reservation(reservation_id, user_id=1)
        
        # Assert
        assert result is False
        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_release_reservation_already_inactive(self, inventory_service, mock_db):
        """测试释放预占 - 预占已失效"""
        # Arrange
        reservation_id = "inactive_reservation"

        # Mock: 预占记录已失效(空结果模拟已失效)
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Act
        result = await inventory_service.release_reservation(reservation_id, user_id=1)
        
        # Assert  
        assert result is False
        mock_db.commit.assert_not_called()