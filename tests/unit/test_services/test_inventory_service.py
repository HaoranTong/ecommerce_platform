"""
库存管理模块 - 服务层单元测试

测试库存管理服务的业务逻辑，使用Mock对象隔离数据库依赖。
遵循系统测试标准：
- AAA模式 (Arrange-Act-Assert)
- Mock外部依赖
- 完整的边界条件测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from app.modules.inventory_management.service import InventoryService
from app.modules.inventory_management.models import (
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType, AdjustmentType
)


class TestInventoryServiceGetOperations:
    """测试库存服务的查询操作"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock数据库会话"""
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        """库存服务实例"""
        return InventoryService(db=mock_db)
    
    @pytest.mark.asyncio
    async def test_get_sku_inventory_success(self, inventory_service, mock_db):
        """测试获取SKU库存信息 - 成功场景"""
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
        assert result["is_low_stock"] is False
        mock_db.query.assert_called_once_with(InventoryStock)
    
    @pytest.mark.asyncio
    async def test_get_sku_inventory_not_found(self, inventory_service, mock_db):
        """测试获取SKU库存信息 - 未找到记录"""
        # Arrange
        sku_id = "NONEXISTENT-SKU"
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = await inventory_service.get_sku_inventory(sku_id)
        
        # Assert
        assert result is None
        mock_db.query.assert_called_once_with(InventoryStock)
    
    @pytest.mark.asyncio
    async def test_get_batch_inventory_success(self, inventory_service, mock_db):
        """测试批量获取SKU库存信息 - 成功场景"""
        # Arrange
        sku_ids = ["SKU-001", "SKU-002", "SKU-003"]
        mock_inventories = []
        
        for i, sku_id in enumerate(sku_ids):
            mock_inv = Mock()
            mock_inv.sku_id = sku_id
            mock_inv.available_quantity = 50 + i * 10
            mock_inv.reserved_quantity = 5 + i
            mock_inv.total_quantity = 60 + i * 10
            mock_inv.is_low_stock = False
            mock_inventories.append(mock_inv)
        
        mock_db.query.return_value.filter.return_value.all.return_value = mock_inventories
        
        # Act
        result = await inventory_service.get_batch_inventory(sku_ids)
        
        # Assert
        assert len(result) == 3
        for i, item in enumerate(result):
            assert item["sku_id"] == sku_ids[i]
            assert item["available_quantity"] == 50 + i * 10
            assert item["reserved_quantity"] == 5 + i
        mock_db.query.assert_called_once_with(InventoryStock)


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

        # Mock: 不存在重复记录，创建成功
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, Mock(
            id=1, 
            sku_id="NEW-SKU-001",
            total_quantity=100,
            available_quantity=100,
            reserved_quantity=0,
            warning_threshold=15,
            critical_threshold=8,
            is_low_stock=False,
            is_critical_stock=False,
            is_out_of_stock=False,
            is_active=True,
            updated_at=datetime.now(timezone.utc)
        )]
        
        # Act
        result = await inventory_service.create_sku_inventory(inventory_data)
        
        # Assert
        assert result is not None
        assert result["sku_id"] == inventory_data["sku_id"]
        assert result["total_quantity"] == inventory_data["initial_quantity"]
        assert result["available_quantity"] == inventory_data["initial_quantity"]
        assert result["reserved_quantity"] == 0
        
        # 验证数据库操作
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_sku_inventory_duplicate_should_fail(self, inventory_service, mock_db):
        """测试创建重复SKU库存记录 - 应该失败"""
        # Arrange
        inventory_data = {
            "sku_id": "EXISTING-SKU",
            "initial_quantity": 50
        }
        
        # Mock: 存在重复记录
        mock_existing = Mock()
        mock_existing.sku_id = "EXISTING-SKU"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await inventory_service.create_sku_inventory(inventory_data)
        
        assert "已存在" in str(exc_info.value)
        mock_db.add.assert_not_called()


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
        )        # Assert
        assert result["success"] is True
        assert "reservation_id" in result
        assert len(result["reserved_items"]) == 2
        
        # 验证数据库操作
        assert mock_db.add.call_count >= len(reservation_data["items"])
        mock_db.commit.assert_called()
    
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
        
        # Assert
        assert "库存不足" in str(exc_info.value) or "insufficient" in str(exc_info.value).lower()


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
        )        # Assert
        assert result["success"] is True
        assert len(result["deducted_items"]) == 2
        
        # 验证每个库存都进行了扣减
        for mock_stock in mock_stocks:
            mock_stock.deduct_inventory.assert_called_once()
        
        mock_db.commit.assert_called()
    
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
            )        # Assert
        assert result["success"] is False
        assert "failed_items" in result
        assert "SKU-004" in result["failed_items"]
        
        # 应该回滚事务
        mock_db.rollback.assert_called()


class TestInventoryServiceAdjustmentOperations:
    """测试库存服务的阈值更新操作（作为调整操作的代理测试）"""
    
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

        # 验证数据库操作
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

        # 不应该有数据库提交操作
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

        def mock_query_side_effect(model_class):
            query_mock = Mock()
            if model_class == InventoryReservation:
                query_mock.filter.return_value.all.return_value = [mock_reservation]
            elif model_class == InventoryStock:
                query_mock.filter.return_value.first.return_value = mock_stock
            return query_mock

        mock_db.query.side_effect = mock_query_side_effect

        # Act
        result = await inventory_service.release_reservation(reservation_id, user_id=1)        # Assert
        assert result["success"] is True
        assert result["reservation_id"] == reservation_id
        assert result["sku_id"] == "SKU-008"
        assert result["released_quantity"] == 15
        
        # 验证操作
        mock_stock.release_reservation.assert_called_once_with(15)
        assert mock_reservation.is_active is False
        mock_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_release_reservation_not_found(self, inventory_service, mock_db):
        """测试释放预占 - 预占记录不存在"""
        # Arrange
        reservation_id = "nonexistent_reservation"

        # Mock: 预占记录不存在
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await inventory_service.release_reservation(reservation_id, user_id=1)
        assert "不存在" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_release_reservation_already_inactive(self, inventory_service, mock_db):
        """测试释放预占 - 预占已失效"""
        # Arrange
        reservation_id = "inactive_reservation"

        # Mock: 预占记录已失效(空结果模拟已失效)
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await inventory_service.release_reservation(reservation_id, user_id=1)
        assert "已失效" in str(exc_info.value)


class TestInventoryServiceQueryOperations:
    """测试库存服务的查询操作"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def inventory_service(self, mock_db):
        return InventoryService(db=mock_db)
    
    @pytest.mark.asyncio
    async def test_get_low_stock_items_success(self, inventory_service, mock_db):
        """测试获取低库存商品列表 - 成功场景"""
        # Arrange
        query_params = {
            "warning_only": False,
            "critical_only": False,
            "page": 1,
            "page_size": 10
        }
        
        # Mock: 低库存商品
        mock_stocks = []
        for i in range(3):
            mock_stock = Mock()
            mock_stock.sku_id = f"LOW-STOCK-{i:03d}"
            mock_stock.available_quantity = 5 + i
            mock_stock.warning_threshold = 10
            mock_stock.critical_threshold = 5
            mock_stock.is_low_stock = True
            mock_stock.is_critical_stock = (i == 0)  # 第一个是紧急库存
            mock_stocks.append(mock_stock)
        
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_stocks
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        
        # Act
        result = await inventory_service.get_low_stock_items(query_params)
        
        # Assert
        assert result["total"] == 3
        assert len(result["items"]) == 3
        assert result["page"] == 1
        assert result["page_size"] == 10
        
        # 验证第一个是紧急库存
        assert result["items"][0]["is_critical_stock"] is True
        assert result["items"][1]["is_critical_stock"] is False
    
    @pytest.mark.asyncio
    async def test_get_inventory_transactions_success(self, inventory_service, mock_db):
        """测试获取库存事务历史 - 成功场景"""
        # Arrange
        sku_id = "SKU-009"
        query_params = {
            "start_date": datetime.now(timezone.utc) - timedelta(days=7),
            "end_date": datetime.now(timezone.utc),
            "transaction_type": None,
            "page": 1,
            "page_size": 20
        }
        
        # Mock: 事务记录
        mock_transactions = []
        for i in range(5):
            mock_tx = Mock()
            mock_tx.id = f"tx_{i:03d}"
            mock_tx.sku_id = sku_id
            mock_tx.transaction_type = TransactionType.DEDUCT if i % 2 == 0 else TransactionType.IN_STOCK
            mock_tx.quantity = 10 + i
            mock_tx.reference_type = "order" if i % 2 == 0 else "purchase"
            mock_tx.reference_id = f"ref_{i:03d}"
            mock_tx.created_at = datetime.now(timezone.utc) - timedelta(hours=i)
            mock_transactions.append(mock_tx)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_transactions
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        # Act
        result = await inventory_service.get_inventory_transactions(sku_id, query_params)
        
        # Assert
        assert result["total"] == 5
        assert len(result["transactions"]) == 5
        assert result["sku_id"] == sku_id
        
        # 验证事务类型
        for i, tx in enumerate(result["transactions"]):
            expected_type = TransactionType.DEDUCT if i % 2 == 0 else TransactionType.IN_STOCK
            assert tx["transaction_type"] == expected_type