"""
库存管理模块测试配置和工具

提供库存管理测试所需的fixtures、工具函数和测试数据工厂。
遵循系统测试标准的配置要求。
"""

import pytest
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from decimal import Decimal
import uuid

from app.modules.inventory_management.models import (
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType, AdjustmentType
)


class InventoryTestDataFactory:
    """库存测试数据工厂"""
    
    @staticmethod
    def create_stock_data(
        sku_id: str = None,
        total_quantity: int = 100,
        available_quantity: int = None,
        reserved_quantity: int = 0,
        warning_threshold: int = 10,
        critical_threshold: int = 5,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """创建库存测试数据"""
        if sku_id is None:
            sku_id = f"TEST-SKU-{uuid.uuid4().hex[:8].upper()}"
        
        if available_quantity is None:
            available_quantity = total_quantity - reserved_quantity
        
        return {
            "sku_id": sku_id,
            "total_quantity": total_quantity,
            "available_quantity": available_quantity,
            "reserved_quantity": reserved_quantity,
            "warning_threshold": warning_threshold,
            "critical_threshold": critical_threshold,
            "is_active": is_active
        }
    
    @staticmethod
    def create_reservation_data(
        sku_id: str,
        reserved_quantity: int = 10,
        reservation_type: ReservationType = ReservationType.CART,
        reference_id: str = None,
        expires_in_hours: int = 2,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """创建预占测试数据"""
        if reference_id is None:
            reference_id = f"TEST-REF-{uuid.uuid4().hex[:8]}"
        
        return {
            "sku_id": sku_id,
            "reserved_quantity": reserved_quantity,
            "reservation_type": reservation_type,
            "reference_id": reference_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
            "is_active": is_active
        }
    
    @staticmethod
    def create_transaction_data(
        sku_id: str,
        transaction_type: TransactionType = TransactionType.DEDUCT,
        quantity: int = 10,
        reference_type: str = "order",
        reference_id: str = None,
        reason: str = "测试事务",
        operator_id: str = "test_admin"
    ) -> Dict[str, Any]:
        """创建事务测试数据"""
        if reference_id is None:
            reference_id = f"TEST-TX-{uuid.uuid4().hex[:8]}"
        
        return {
            "sku_id": sku_id,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "reference_type": reference_type,
            "reference_id": reference_id,
            "reason": reason,
            "operator_id": operator_id
        }


@pytest.fixture
def inventory_factory():
    """库存数据工厂fixture"""
    return InventoryTestDataFactory()


@pytest.fixture
def sample_stock_data():
    """示例库存数据"""
    return {
        "sku_id": "SAMPLE-SKU-001",
        "total_quantity": 100,
        "available_quantity": 80,
        "reserved_quantity": 20,
        "warning_threshold": 15,
        "critical_threshold": 8
    }


@pytest.fixture
def low_stock_data():
    """低库存测试数据"""
    return {
        "sku_id": "LOW-STOCK-SKU",
        "total_quantity": 12,
        "available_quantity": 8,
        "reserved_quantity": 4,
        "warning_threshold": 15,
        "critical_threshold": 8
    }


@pytest.fixture
def critical_stock_data():
    """紧急库存测试数据"""
    return {
        "sku_id": "CRITICAL-SKU",
        "total_quantity": 6,
        "available_quantity": 3,
        "reserved_quantity": 3,
        "warning_threshold": 15,
        "critical_threshold": 8
    }


@pytest.fixture
def out_of_stock_data():
    """缺货测试数据"""
    return {
        "sku_id": "OUT-OF-STOCK-SKU",
        "total_quantity": 0,
        "available_quantity": 0,
        "reserved_quantity": 0,
        "warning_threshold": 10,
        "critical_threshold": 5
    }


class InventoryTestHelper:
    """库存测试辅助工具"""
    
    @staticmethod
    def create_stock_in_db(db, stock_data: Dict[str, Any]) -> InventoryStock:
        """在数据库中创建库存记录"""
        stock = InventoryStock(**stock_data)
        db.add(stock)
        db.commit()
        db.refresh(stock)
        return stock
    
    @staticmethod
    def verify_stock_quantities(stock: InventoryStock, 
                              expected_total: int, 
                              expected_available: int, 
                              expected_reserved: int):
        """验证库存数量"""
        assert stock.total_quantity == expected_total, \
            f"总库存不匹配: 期望 {expected_total}, 实际 {stock.total_quantity}"
        assert stock.available_quantity == expected_available, \
            f"可用库存不匹配: 期望 {expected_available}, 实际 {stock.available_quantity}"
        assert stock.reserved_quantity == expected_reserved, \
            f"预占库存不匹配: 期望 {expected_reserved}, 实际 {stock.reserved_quantity}"


@pytest.fixture
def inventory_helper():
    """库存测试辅助工具fixture"""
    return InventoryTestHelper()


# 数据验证工具
class InventoryDataValidator:
    """库存数据验证工具"""
    
    @staticmethod
    def validate_inventory_response(data: Dict, expected_fields: List[str] = None):
        """验证库存响应数据格式"""
        if expected_fields is None:
            expected_fields = [
                "sku_id", "total_quantity", "available_quantity", 
                "reserved_quantity", "is_low_stock", "is_active"
            ]
        
        for field in expected_fields:
            assert field in data, f"响应数据缺少字段: {field}"
        
        assert isinstance(data["total_quantity"], int), "total_quantity 应该是整数"
        assert isinstance(data["available_quantity"], int), "available_quantity 应该是整数"
        assert isinstance(data["reserved_quantity"], int), "reserved_quantity 应该是整数"
        assert isinstance(data["is_low_stock"], bool), "is_low_stock 应该是布尔值"
        assert isinstance(data["is_active"], bool), "is_active 应该是布尔值"


@pytest.fixture
def data_validator():
    """数据验证器fixture"""
    return InventoryDataValidator()