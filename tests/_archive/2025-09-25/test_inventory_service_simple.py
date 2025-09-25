"""
库存管理服务层单元测试 - 简化版本
测试所有核心方法以确保0错误
"""

import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from app.modules.inventory_management.service import InventoryService
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
from app.modules.inventory_management.models import ReservationType


class TestInventoryServiceCore:
    """核心服务测试"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db):
        return InventoryService(db=mock_db)

    def test_get_sku_inventory_found(self, service, mock_db):
        """测试获取SKU库存 - 找到"""
        mock_inv = Mock()
        mock_inv.id = 1
        mock_inv.sku_id = 1001  # ✅ 修复：使用int类型符合Schema定义
        mock_inv.total_quantity = 100
        mock_inv.available_quantity = 80
        mock_inv.reserved_quantity = 20
        mock_inv.warning_threshold = 10
        mock_inv.critical_threshold = 5
        mock_inv.is_low_stock = False
        mock_inv.is_critical_stock = False
        mock_inv.is_out_of_stock = False
        mock_inv.is_active = True
        mock_inv.updated_at = datetime.now(timezone.utc)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_inv
        
        result = service.get_sku_inventory(1001)  # ✅ 修复：使用int类型
        
        assert result is not None
        assert result.sku_id == 1001  # ✅ 修复：result是Pydantic对象，不是dict
        assert result.total_quantity == 100

    def test_get_sku_inventory_not_found(self, service, mock_db):
        """测试获取SKU库存 - 未找到"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = service.get_sku_inventory("NONE")
        
        assert result is None

    def test_get_batch_inventory(self, service, mock_db):
        """测试批量获取库存"""
        mock_inv1 = Mock()
        mock_inv1.id = 1
        mock_inv1.sku_id = 1001  # ✅ 修复：使用int类型
        mock_inv1.available_quantity = 50
        mock_inv1.reserved_quantity = 5
        mock_inv1.total_quantity = 55
        mock_inv1.warning_threshold = 10
        mock_inv1.critical_threshold = 5
        mock_inv1.is_low_stock = False
        mock_inv1.is_critical_stock = False
        mock_inv1.is_out_of_stock = False
        mock_inv1.is_active = True
        mock_inv1.updated_at = datetime.now(timezone.utc)
        
        mock_inv2 = Mock()
        mock_inv2.id = 2
        mock_inv2.sku_id = 1002  # ✅ 修复：使用int类型
        mock_inv2.available_quantity = 30
        mock_inv2.reserved_quantity = 10
        mock_inv2.total_quantity = 40
        mock_inv2.warning_threshold = 10
        mock_inv2.critical_threshold = 5
        mock_inv2.is_low_stock = True
        mock_inv2.is_critical_stock = False
        mock_inv2.is_out_of_stock = False
        mock_inv2.is_active = True
        mock_inv2.updated_at = datetime.now(timezone.utc)
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_inv1, mock_inv2]
        
        result = service.get_batch_inventory([1001, 1002])  # ✅ 修复：使用int类型
        
        assert len(result) == 2
        assert result[0].sku_id == 1001  # ✅ 修复：Pydantic对象访问
        assert result[1].sku_id == 1002

    def test_create_sku_inventory_success(self, service, mock_db):
        """测试创建库存 - 成功"""
        # Mock查询重复返回None，创建后返回新记录
        mock_new = Mock()
        mock_new.id = 1
        mock_new.sku_id = 1001
        mock_new.total_quantity = 100
        mock_new.available_quantity = 100
        mock_new.reserved_quantity = 0
        mock_new.warning_threshold = 15
        mock_new.critical_threshold = 8
        mock_new.is_low_stock = False
        mock_new.is_critical_stock = False
        mock_new.is_out_of_stock = False
        mock_new.is_active = True
        mock_new.updated_at = datetime.now(timezone.utc)
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_new]
        
        # 使用Mock对象模拟Pydantic模型
        data = Mock()
        data.sku_id = 1001
        data.initial_quantity = 100
        data.warning_threshold = 15
        data.critical_threshold = 8
        
        result = service.create_sku_inventory(data)
        
        assert result is not None
        assert result.sku_id == 1001  # ✅ 修复：Pydantic对象访问
        assert result.total_quantity == 100
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

    def test_create_sku_inventory_duplicate(self, service, mock_db):
        """测试创建库存 - 重复SKU"""
        mock_existing = Mock()
        mock_existing.sku_id = 2001
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        
        # 使用Mock对象模拟Pydantic模型
        data = Mock()
        data.sku_id = 2001
        data.initial_quantity = 50
        
        with pytest.raises(ValueError) as exc:
            service.create_sku_inventory(data)
        assert "已存在" in str(exc.value)

    @pytest.mark.asyncio
    async def test_reserve_inventory_success(self, service, mock_db):
        """测试预占库存 - 成功"""
        mock_inv = Mock()
        mock_inv.can_reserve.return_value = True
        mock_inv.reserve_quantity.return_value = True
        mock_inv.available_quantity = 90
        
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_inv
        
        # ✅ 修复：使用Mock对象模拟item结构
        item = Mock()
        item.sku_id = 1001  # ✅ 使用int类型
        item.quantity = 10
        items = [item]
        
        result = await service.reserve_inventory(
            reservation_type=ReservationType.CART,
            reference_id="cart_1",
            items=items,
            expires_minutes=120,
            user_id=1
        )
        
        # ✅ 修复：result是Pydantic对象，不是字典
        assert hasattr(result, 'reservation_id')
        assert hasattr(result, 'expires_at')
        assert hasattr(result, 'reserved_items')
        assert result.reservation_id is not None
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_reserve_inventory_insufficient(self, service, mock_db):
        """测试预占库存 - 库存不足"""
        mock_inv = Mock()
        mock_inv.can_reserve.return_value = False
        mock_inv.available_quantity = 5
        
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_inv
        
        # ✅ 修复：使用Mock对象模拟item结构
        item = Mock()
        item.sku_id = 1002  # ✅ 使用int类型
        item.quantity = 100
        items = [item]
        
        with pytest.raises(ValueError) as exc:
            await service.reserve_inventory(
                reservation_type=ReservationType.CART,
                reference_id="cart_2",
                items=items,
                expires_minutes=120,
                user_id=1
            )
        assert "库存不足" in str(exc.value)
        mock_db.rollback.assert_called()

    @pytest.mark.asyncio 
    async def test_deduct_inventory_success(self, service, mock_db):
        """测试扣减库存 - 成功"""
        mock_inv = Mock()
        mock_inv.deduct_quantity.return_value = True
        mock_inv.total_quantity = 95
        
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_inv
        
        # ✅ 修复：使用Mock对象模拟item结构
        item = Mock()
        item.sku_id = 1003  # ✅ 使用int类型
        item.quantity = 5
        item.reservation_id = None  # ✅ 添加reservation_id属性
        items = [item]
        
        result = await service.deduct_inventory(
            order_id="order_1",
            items=items,
            operator_id=1
        )
        
        # ✅ 修复：result是Pydantic对象，不是字典
        assert hasattr(result, 'order_id')
        assert result.order_id == "order_1"
        assert hasattr(result, 'deducted_items')
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_deduct_inventory_insufficient(self, service, mock_db):
        """测试扣减库存 - 库存不足"""
        mock_inv = Mock()
        mock_inv.deduct_quantity.return_value = False
        
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_inv
        
        # ✅ 修复：使用Mock对象模拟item结构
        item = Mock()
        item.sku_id = 1004  # ✅ 使用int类型
        item.quantity = 50
        item.reservation_id = None  # ✅ 添加reservation_id属性
        items = [item]
        
        with pytest.raises(ValueError):
            await service.deduct_inventory(
                order_id="order_2",
                items=items,
                operator_id=1
            )
        mock_db.rollback.assert_called()

    @pytest.mark.asyncio
    async def test_release_reservation_success(self, service, mock_db):
        """测试释放预占 - 成功"""
        mock_res = Mock()
        mock_res.sku_id = 1005  # ✅ 修复：使用int类型
        mock_res.quantity = 15
        mock_res.is_active = True
        
        mock_inv = Mock()
        
        def mock_query(model):
            query_mock = Mock()
            if "Reservation" in str(model):
                query_mock.filter.return_value.all.return_value = [mock_res]
            else:
                query_mock.filter.return_value.with_for_update.return_value.first.return_value = mock_inv
            return query_mock
        
        mock_db.query.side_effect = mock_query
        
        result = await service.release_reservation("res_1", user_id=1)
        
        assert result is True
        assert mock_res.is_active is False
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_release_reservation_not_found(self, service, mock_db):
        """测试释放预占 - 未找到"""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = await service.release_reservation("none", user_id=1)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_update_thresholds_success(self, service, mock_db):
        """测试更新阈值 - 成功"""
        mock_inv = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_inv
        
        result = await service.update_thresholds("SKU-6", 20, 10)
        
        assert result is True
        assert mock_inv.warning_threshold == 20
        assert mock_inv.critical_threshold == 10
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_update_thresholds_not_found(self, service, mock_db):
        """测试更新阈值 - SKU不存在"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = await service.update_thresholds("NONE", 20, 10)
        
        assert result is False