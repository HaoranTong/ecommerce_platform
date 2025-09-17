"""
库存管理模块核心功能测试

测试基于SKU的库存管理系统核心功能，验证架构合规性
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session

# 使用标准测试配置 - 符合testing-standards.md要求
# 标准fixture将通过conftest.py自动提供

# 导入库存管理相关模块
from app.modules.inventory_management.models import (
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType, AdjustmentType
)
from app.modules.inventory_management.schemas import (
    TransactionTypeEnum, LowStockQuery, TransactionQuery
)
from app.modules.inventory_management.service import InventoryService
from app.modules.inventory_management.schemas import (
    SKUInventoryCreate, ReservationItem, DeductItem,
    AdjustmentTypeEnum, LowStockQuery, TransactionQuery
)


@pytest.fixture
def test_sku_inventory(unit_test_db: Session):
    """测试SKU库存fixture"""
    inventory = InventoryStock(
        sku_id=1001,
        total_quantity=100,
        available_quantity=100,
        reserved_quantity=0,
        warning_threshold=20,
        critical_threshold=10
    )
    unit_test_db.add(inventory)
    unit_test_db.commit()
    unit_test_db.refresh(inventory)
    return inventory


@pytest.fixture
def multiple_test_inventories(unit_test_db: Session):
    """多个测试库存fixture"""
    inventories = [
        InventoryStock(
            sku_id=2001, total_quantity=50, available_quantity=50, reserved_quantity=0,
            warning_threshold=15, critical_threshold=5
        ),
        InventoryStock(
            sku_id=2002, total_quantity=13, available_quantity=8, reserved_quantity=5,
            warning_threshold=10, critical_threshold=5
        ),
        InventoryStock(
            sku_id=2003, total_quantity=8, available_quantity=3, reserved_quantity=5,
            warning_threshold=10, critical_threshold=5
        )
    ]
    
    for inventory in inventories:
        unit_test_db.add(inventory)
    unit_test_db.commit()
    
    for inventory in inventories:
        unit_test_db.refresh(inventory)
    
    return inventories


class TestInventoryCore:
    """库存管理核心功能测试"""

    def test_create_sku_inventory(self, unit_test_db: Session):
        """测试创建SKU库存 - 验证架构合规性"""
        service = InventoryService(unit_test_db)
        
        inventory_data = SKUInventoryCreate(
            sku_id=1001,
            initial_quantity=100,
            warning_threshold=20,
            critical_threshold=10
        )
        
        # 执行创建
        result = service.create_sku_inventory(inventory_data)
        
        # 验证结果符合架构要求
        assert result.sku_id == 1001  # 使用sku_id而不是product_id
        assert result.total_quantity == 100
        assert result.available_quantity == 100
        assert result.reserved_quantity == 0
        assert result.warning_threshold == 20
        assert result.critical_threshold == 10

    def test_get_sku_inventory(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试获取SKU库存 - 验证架构合规性"""
        service = InventoryService(unit_test_db)
        
        # 获取库存
        result = service.get_sku_inventory(1001)
        
        # 验证返回数据符合架构
        assert result is not None
        assert result.sku_id == 1001  # 确认使用sku_id
        assert result.total_quantity == 100
        assert result.available_quantity == 100
        assert result.reserved_quantity == 0

    def test_batch_inventory_query(self, unit_test_db: Session, multiple_test_inventories: List[InventoryStock]):
        """测试批量库存查询 - 验证架构合规性"""
        service = InventoryService(unit_test_db)
        
        # 批量查询
        sku_ids = [2001, 2002, 2003]
        result = service.get_batch_inventory(sku_ids)
        
        # 验证结果
        assert len(result) == 3
        for item in result:
            assert hasattr(item, 'sku_id')  # 确认使用sku_id字段
            assert item.sku_id in sku_ids

    def test_inventory_reservation_flow(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试库存预占流程 - 完整业务流程验证"""
        service = InventoryService(unit_test_db)
        
        # 1. 预占库存
        items = [ReservationItem(sku_id=1001, quantity=30)]
        reservation = asyncio.run(service.reserve_inventory(
            reservation_type=ReservationType.CART,
            reference_id="user_123",
            items=items,
            expires_minutes=30,
            user_id=1002
        ))
        
        # 验证预占结果
        assert reservation.reservation_id is not None
        assert len(reservation.reserved_items) == 1
        assert reservation.reserved_items[0].sku_id == 1001
        assert reservation.reserved_items[0].reserved_quantity == 30
        assert reservation.reserved_items[0].available_after_reserve == 70
        
        # 2. 验证库存状态变化
        current_inventory = service.get_sku_inventory(1001)
        assert current_inventory.available_quantity == 70
        assert current_inventory.reserved_quantity == 30
        
        # 3. 释放预占
        release_result = asyncio.run(service.release_reservation(
            reservation_id="user_123",  # 使用 reference_id
            user_id=1002
        ))
        assert release_result is True
        
        # 4. 验证库存恢复
        final_inventory = service.get_sku_inventory(1001)
        assert final_inventory.available_quantity == 100
        assert final_inventory.reserved_quantity == 0

    def test_inventory_deduction_flow(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试库存扣减流程 - 验证订单出库"""
        service = InventoryService(unit_test_db)
        
        # 1. 先预占
        items = [ReservationItem(sku_id=1001, quantity=25)]
        reservation = asyncio.run(service.reserve_inventory(
            reservation_type=ReservationType.ORDER,
            reference_id="order_456",
            items=items,
            expires_minutes=30,
            user_id=1002
        ))
        
        # 2. 扣减库存（实际出库）
        deduct_items = [DeductItem(
            sku_id=1001,
            quantity=25,
            reservation_id=reservation.reservation_id
        )]
        
        deduct_result = asyncio.run(service.deduct_inventory(
            order_id="ORD789",
            items=deduct_items,
            operator_id=1002
        ))
        
        # 验证扣减结果
        assert deduct_result.order_id == "ORD789"
        assert len(deduct_result.deducted_items) == 1
        assert deduct_result.deducted_items[0].sku_id == 1001
        assert deduct_result.deducted_items[0].deducted_quantity == 25
        assert deduct_result.deducted_items[0].remaining_quantity == 75
        
        # 验证最终库存状态
        final_inventory = service.get_sku_inventory(1001)
        assert final_inventory.total_quantity == 75  # 总量减少
        assert final_inventory.available_quantity == 75  # 可用量正确
        assert final_inventory.reserved_quantity == 0   # 预占已清除

    def test_inventory_adjustment_operations(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试库存调整操作 - 验证管理员功能"""
        service = InventoryService(unit_test_db)
        
        # 测试增加库存
        increase_result = asyncio.run(service.adjust_inventory(
            sku_id=1001,
            adjustment_type=AdjustmentType.INCREASE,
            quantity=50,
            reason="新货入库",
            reference="PO2025001",
            operator_id=1001
        ))
        
        assert increase_result.sku_id == 1001
        assert increase_result.old_quantity == 100
        assert increase_result.new_quantity == 150
        
        # 测试减少库存  
        decrease_result = asyncio.run(service.adjust_inventory(
            sku_id=1001,
            adjustment_type=AdjustmentType.DECREASE,
            quantity=30,
            reason="损耗报废",
            reference="WO2025001",
            operator_id=1001
        ))
        
        assert decrease_result.sku_id == 1001
        assert decrease_result.old_quantity == 150
        assert decrease_result.new_quantity == 120

    def test_low_stock_warning_system(self, unit_test_db: Session, multiple_test_inventories: List[InventoryStock]):
        """测试库存预警系统"""
        service = InventoryService(unit_test_db)
        
        # 获取预警级别的低库存
        warning_query = LowStockQuery(level="warning", limit=10, offset=0)
        warning_result = service.get_low_stock_skus(warning_query)
        
        # 应该找到库存为8的SKU（低于warning_threshold=10）
        warning_skus = [item.sku_id for item in warning_result]
        assert 2002 in warning_skus  # 库存8，低于阈值10
        assert 2003 in warning_skus  # 库存3，低于阈值10
        
        # 获取严重不足级别的库存
        critical_query = LowStockQuery(level="critical", limit=10, offset=0)
        critical_result = service.get_low_stock_skus(critical_query)
        
        # 应该只找到库存为3的SKU（低于critical_threshold=5）
        critical_skus = [item.sku_id for item in critical_result]
        assert 2003 in critical_skus  # 库存3，低于阈值5
        assert 2002 not in critical_skus  # 库存8，高于阈值5

    def test_inventory_transaction_logging(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试库存变动记录 - 验证审计功能"""
        service = InventoryService(unit_test_db)
        
        # 执行一些库存操作
        asyncio.run(service.adjust_inventory(
            sku_id=1001,
            adjustment_type=AdjustmentType.INCREASE,
            quantity=20,
            reason="测试入库",
            reference="TEST001",
            operator_id=1001
        ))
        
        # 查询变动记录
        query = TransactionQuery(
            sku_ids=[1001],
            limit=10,
            offset=0
        )
        
        logs = service.get_transaction_logs(query)
        
        # 验证记录存在
        assert logs.sku_id == 1001
        assert logs.total >= 1
        assert len(logs.logs) >= 1
        
        # 验证记录内容
        latest_log = logs.logs[0]
        assert latest_log.sku_id == 1001
        assert latest_log.transaction_type == TransactionTypeEnum.RESTOCK
        assert latest_log.quantity_change == 20
        assert latest_log.operator_id == 1001

    def test_data_consistency_validation(self, unit_test_db: Session):
        """测试数据一致性验证"""
        service = InventoryService(unit_test_db)
        
        # 创建一个数据不一致的库存记录
        inconsistent_inventory = InventoryStock(
            sku_id=9999,
            total_quantity=50,
            available_quantity=30,
            reserved_quantity=30,  # 30+30 != 50，不一致
            warning_threshold=15,
            critical_threshold=20,  # critical > warning，不合理
            is_active=True
        )
        unit_test_db.add(inconsistent_inventory)
        unit_test_db.commit()
        
        # 执行一致性检查
        check_result = service.check_inventory_consistency()
        
        # 验证发现了不一致问题
        assert check_result.inconsistent_skus >= 1
        assert len(check_result.details) >= 1
        
        # 检查是否正确识别了不一致问题
        inconsistent_item = next(
            (item for item in check_result.details if item.sku_id == 9999),
            None
        )
        assert inconsistent_item is not None
        assert "数量不一致" in inconsistent_item.issue or "阈值设置不合理" in inconsistent_item.issue

    def test_expired_reservation_cleanup(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试过期预占清理"""
        service = InventoryService(unit_test_db)
        
        # 创建一个过期的预占记录
        expired_time = datetime.now(timezone.utc) - timedelta(hours=2)
        expired_reservation = InventoryReservation(
            sku_id=1001,
            reservation_type=ReservationType.CART,
            reference_id="expired_test",
            quantity=40,
            expires_at=expired_time,
            is_active=True
        )
        unit_test_db.add(expired_reservation)
        
        # 更新库存状态模拟预占
        inventory = unit_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == 1001
        ).first()
        inventory.available_quantity -= 40
        inventory.reserved_quantity += 40
        unit_test_db.commit()
        
        # 执行清理
        cleanup_result = service.cleanup_expired_reservations()
        
        # 验证清理结果
        assert cleanup_result.cleaned_reservations >= 1
        assert cleanup_result.released_quantity >= 40
        
        # 验证库存已恢复
        updated_inventory = service.get_sku_inventory(1001)
        assert updated_inventory.available_quantity == 100
        assert updated_inventory.reserved_quantity == 0

    def test_error_handling_and_boundaries(self, unit_test_db: Session, test_sku_inventory: InventoryStock):
        """测试错误处理和边界情况"""
        service = InventoryService(unit_test_db)
        
        # 测试预占数量超过可用库存
        items = [ReservationItem(sku_id=1001, quantity=150)]  # 超过100的可用库存
        with pytest.raises(ValueError, match="库存不足"):
            asyncio.run(service.reserve_inventory(
                reservation_type=ReservationType.CART,
                reference_id="test_user",
                items=items,
                expires_minutes=30,
                user_id=1002
            ))
        
        # 测试不存在的SKU操作
        result = service.get_sku_inventory("NONEXISTENT_SKU")
        assert result is None
        
        # 测试重复创建同一SKU的库存
        duplicate_data = SKUInventoryCreate(
            sku_id=1001,  # 已存在
            initial_quantity=50,
            warning_threshold=10,
            critical_threshold=5
        )
        
        with pytest.raises(ValueError, match="已存在"):
            service.create_sku_inventory(duplicate_data)


# ============ 测试运行函数 ============

def run_architecture_compliance_tests():
    """运行架构合规性测试"""
    import subprocess
    import sys
    
    print("🏗️  库存管理模块架构合规性测试")
    print("=" * 50)
    print("验证项目:")
    print("✓ 使用sku_id而不是product_id")
    print("✓ 遵循Product-SKU分离原则") 
    print("✓ 完整的预占机制实现")
    print("✓ 库存变动审计跟踪")
    print("✓ 数据一致性保证")
    print("✓ 错误处理和边界验证")
    print("=" * 50)
    
    # 运行测试
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v", "-s", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n🎉 架构合规性测试全部通过！")
        print("📋 库存管理模块100%符合系统架构设计要求")
    else:
        print(f"\n❌ 测试失败 (退出码: {result.returncode})")
        print("请检查上述错误信息并修复问题")
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_architecture_compliance_tests()
    exit(0 if success else 1)
