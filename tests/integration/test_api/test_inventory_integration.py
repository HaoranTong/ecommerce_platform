"""
库存管理模块 - API集成测试

测试完整的API端点功能，包括数据库交互和业务流程。
遵循系统测试标准：
- 使用真实数据库连接
- 测试完整业务流程
- 验证端到端功能
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
import json

from app.modules.inventory_management.models import (
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType
)


class TestInventoryStockAPI:
    """测试库存查询API"""
    
    def test_get_sku_inventory_success(self, integration_test_client, integration_test_db):
        """测试获取SKU库存信息 - 成功场景"""
        # Arrange - 创建测试数据
        test_stock = InventoryStock(
            sku_id="INT-TEST-SKU-001",
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20,
            warning_threshold=15,
            critical_threshold=8
        )
        integration_test_db.add(test_stock)
        integration_test_db.commit()
        integration_test_db.refresh(test_stock)
        
        # Act - 调用API
        response = integration_test_client.get(f"/api/inventory/stock/{test_stock.sku_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["sku_id"] == test_stock.sku_id
        assert data["total_quantity"] == 100
        assert data["available_quantity"] == 80
        assert data["reserved_quantity"] == 20
        assert data["warning_threshold"] == 15
        assert data["critical_threshold"] == 8
        assert data["is_low_stock"] is True  # 80 < 15 (warning_threshold)
        assert data["is_active"] is True
    
    def test_get_sku_inventory_not_found(self, integration_test_client):
        """测试获取不存在的SKU库存信息"""
        # Act
        response = integration_test_client.get("/api/inventory/stock/NONEXISTENT-SKU")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "不存在" in data["detail"]
    
    def test_get_batch_inventory_success(self, integration_test_client, integration_test_db):
        """测试批量获取SKU库存信息"""
        # Arrange - 创建多个测试数据
        test_skus = ["BATCH-SKU-001", "BATCH-SKU-002", "BATCH-SKU-003"]
        for i, sku_id in enumerate(test_skus):
            stock = InventoryStock(
                sku_id=sku_id,
                total_quantity=50 + i * 25,
                available_quantity=40 + i * 20,
                reserved_quantity=10 + i * 5
            )
            integration_test_db.add(stock)
        integration_test_db.commit()
        
        # Act
        request_data = {"sku_ids": test_skus}
        response = integration_test_client.post("/api/inventory/stock/batch", json=request_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        for i, item in enumerate(data):
            assert item["sku_id"] == test_skus[i]
            assert item["total_quantity"] == 50 + i * 25
            assert item["available_quantity"] == 40 + i * 20


class TestInventoryCreateAPI:
    """测试库存创建API"""
    
    def test_create_sku_inventory_success(self, integration_test_client, integration_test_db):
        """测试创建SKU库存记录 - 成功场景"""
        # Arrange
        inventory_data = {
            "sku_id": "CREATE-TEST-SKU-001",
            "initial_quantity": 150,
            "warning_threshold": 20,
            "critical_threshold": 10
        }
        
        # Act
        response = integration_test_client.post("/api/inventory/stock", json=inventory_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["sku_id"] == inventory_data["sku_id"]
        assert data["total_quantity"] == 150
        assert data["available_quantity"] == 150
        assert data["reserved_quantity"] == 0
        
        # 验证数据库中的记录
        db_stock = integration_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == inventory_data["sku_id"]
        ).first()
        assert db_stock is not None
        assert db_stock.total_quantity == 150
    
    def test_create_sku_inventory_duplicate_should_fail(self, integration_test_client, integration_test_db):
        """测试创建重复SKU库存记录 - 应该失败"""
        # Arrange - 先创建一个库存记录
        existing_sku = "DUPLICATE-TEST-SKU"
        existing_stock = InventoryStock(
            sku_id=existing_sku,
            total_quantity=100,
            available_quantity=100
        )
        integration_test_db.add(existing_stock)
        integration_test_db.commit()
        
        # Act - 尝试创建重复记录
        inventory_data = {
            "sku_id": existing_sku,
            "initial_quantity": 50
        }
        response = integration_test_client.post("/api/inventory/stock", json=inventory_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "已存在" in data["detail"]


class TestInventoryReservationAPI:
    """测试库存预占API"""
    
    def test_reserve_inventory_success(self, integration_test_client, integration_test_db):
        """测试库存预占 - 成功场景"""
        # Arrange - 创建库存数据
        test_stocks = []
        for i in range(2):
            stock = InventoryStock(
                sku_id=f"RESERVE-SKU-{i:03d}",
                total_quantity=100,
                available_quantity=100,
                reserved_quantity=0
            )
            integration_test_db.add(stock)
            test_stocks.append(stock)
        integration_test_db.commit()
        
        # Act - 预占库存
        reserve_data = {
            "items": [
                {"sku_id": "RESERVE-SKU-000", "quantity": 20},
                {"sku_id": "RESERVE-SKU-001", "quantity": 15}
            ],
            "reservation_type": "cart",
            "reference_id": "cart_integration_test_001",
            "expires_in_hours": 2
        }
        response = integration_test_client.post("/api/inventory/reserve", json=reserve_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reservation_id" in data
        assert len(data["reserved_items"]) == 2
        
        # 验证数据库中的库存变化
        updated_stock_1 = integration_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == "RESERVE-SKU-000"
        ).first()
        assert updated_stock_1.available_quantity == 80  # 100 - 20
        assert updated_stock_1.reserved_quantity == 20
        
        # 验证预占记录
        reservations = integration_test_db.query(InventoryReservation).filter(
            InventoryReservation.reference_id == "cart_integration_test_001"
        ).all()
        assert len(reservations) == 2
    
    def test_reserve_inventory_insufficient_stock(self, integration_test_client, integration_test_db):
        """测试库存预占 - 库存不足"""
        # Arrange
        stock = InventoryStock(
            sku_id="LOW-STOCK-SKU",
            total_quantity=10,
            available_quantity=5,  # 可用库存很少
            reserved_quantity=5
        )
        integration_test_db.add(stock)
        integration_test_db.commit()
        
        # Act - 尝试预占过多库存
        reserve_data = {
            "items": [
                {"sku_id": "LOW-STOCK-SKU", "quantity": 10}  # 超出可用量
            ],
            "reservation_type": "cart",
            "reference_id": "cart_insufficient_test"
        }
        response = integration_test_client.post("/api/inventory/reserve", json=reserve_data)
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "insufficient_stock" in data
        assert "LOW-STOCK-SKU" in data["insufficient_stock"]
    
    def test_release_reservation_success(self, integration_test_client, integration_test_db):
        """测试释放库存预占 - 成功场景"""
        # Arrange - 创建库存和预占记录
        stock = InventoryStock(
            sku_id="RELEASE-TEST-SKU",
            total_quantity=100,
            available_quantity=70,
            reserved_quantity=30
        )
        integration_test_db.add(stock)
        integration_test_db.commit()
        
        reservation = InventoryReservation(
            sku_id="RELEASE-TEST-SKU",
            reserved_quantity=15,
            reservation_type=ReservationType.CART,
            reference_id="cart_to_release",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            is_active=True
        )
        integration_test_db.add(reservation)
        integration_test_db.commit()
        integration_test_db.refresh(reservation)
        
        # Act - 释放预占
        release_data = {
            "reservation_ids": [reservation.id]
        }
        response = integration_test_client.delete("/api/inventory/reserve", json=release_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["released_reservations"]) == 1
        
        # 验证库存恢复
        updated_stock = integration_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == "RELEASE-TEST-SKU"
        ).first()
        assert updated_stock.available_quantity == 85  # 70 + 15
        assert updated_stock.reserved_quantity == 15   # 30 - 15
        
        # 验证预占记录状态
        updated_reservation = integration_test_db.query(InventoryReservation).filter(
            InventoryReservation.id == reservation.id
        ).first()
        assert updated_reservation.is_active is False


class TestInventoryDeductAPI:
    """测试库存扣减API"""
    
    def test_deduct_inventory_success(self, integration_test_client, integration_test_db):
        """测试库存扣减 - 成功场景"""
        # Arrange - 创建有预占的库存
        stock = InventoryStock(
            sku_id="DEDUCT-TEST-SKU",
            total_quantity=100,
            available_quantity=50,
            reserved_quantity=50
        )
        integration_test_db.add(stock)
        integration_test_db.commit()
        
        # Act - 扣减库存
        deduct_data = {
            "items": [
                {"sku_id": "DEDUCT-TEST-SKU", "quantity": 25}
            ],
            "reference_type": "order",
            "reference_id": "order_deduct_test_001",
            "operator_id": "admin_001"
        }
        response = integration_test_client.post("/api/inventory/deduct", json=deduct_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["deducted_items"]) == 1
        
        # 验证库存变化
        updated_stock = integration_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == "DEDUCT-TEST-SKU"
        ).first()
        assert updated_stock.total_quantity == 75     # 100 - 25
        assert updated_stock.available_quantity == 50  # 保持不变
        assert updated_stock.reserved_quantity == 25   # 50 - 25
        
        # 验证事务记录
        transaction = integration_test_db.query(InventoryTransaction).filter(
            InventoryTransaction.sku_id == "DEDUCT-TEST-SKU",
            InventoryTransaction.reference_id == "order_deduct_test_001"
        ).first()
        assert transaction is not None
        assert transaction.transaction_type == TransactionType.DEDUCT
        assert transaction.quantity == 25


class TestInventoryAdjustmentAPI:
    """测试库存调整API"""
    
    def test_adjust_inventory_increase_success(self, integration_test_client, integration_test_db):
        """测试库存调整 - 增加库存"""
        # Arrange
        stock = InventoryStock(
            sku_id="ADJUST-INCREASE-SKU",
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20
        )
        integration_test_db.add(stock)
        integration_test_db.commit()
        
        # Act - 增加库存
        adjust_data = {
            "adjustment_type": "increase",
            "quantity": 50,
            "reason": "采购入库",
            "operator_id": "admin_002"
        }
        response = integration_test_client.post(f"/api/inventory/adjust/{stock.sku_id}", json=adjust_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["adjustment_type"] == "increase"
        assert data["quantity"] == 50
        
        # 验证库存增加
        updated_stock = integration_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == stock.sku_id
        ).first()
        assert updated_stock.total_quantity == 150    # 100 + 50
        assert updated_stock.available_quantity == 130 # 80 + 50
        assert updated_stock.reserved_quantity == 20   # 保持不变
    
    def test_adjust_inventory_decrease_success(self, integration_test_client, integration_test_db):
        """测试库存调整 - 减少库存"""
        # Arrange
        stock = InventoryStock(
            sku_id="ADJUST-DECREASE-SKU",
            total_quantity=100,
            available_quantity=80,
            reserved_quantity=20
        )
        integration_test_db.add(stock)
        integration_test_db.commit()
        
        # Act - 减少库存
        adjust_data = {
            "adjustment_type": "decrease",
            "quantity": 30,
            "reason": "盘点损耗",
            "operator_id": "admin_003"
        }
        response = integration_test_client.post(f"/api/inventory/adjust/{stock.sku_id}", json=adjust_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["adjustment_type"] == "decrease"
        
        # 验证库存减少
        updated_stock = integration_test_db.query(InventoryStock).filter(
            InventoryStock.sku_id == stock.sku_id
        ).first()
        assert updated_stock.total_quantity == 70     # 100 - 30
        assert updated_stock.available_quantity == 50  # 80 - 30
        assert updated_stock.reserved_quantity == 20   # 保持不变


class TestInventoryQueryAPI:
    """测试库存查询API"""
    
    def test_get_low_stock_items_success(self, integration_test_client, integration_test_db):
        """测试获取低库存商品列表"""
        # Arrange - 创建不同库存水平的商品
        stocks_data = [
            ("NORMAL-STOCK", 100, 50, 15, 8),     # 正常库存
            ("LOW-STOCK", 12, 8, 15, 8),          # 低库存（预警）
            ("CRITICAL-STOCK", 6, 3, 15, 8),      # 紧急库存
            ("OUT-OF-STOCK", 0, 0, 15, 8)         # 缺货
        ]
        
        for sku_id, total, available, warning, critical in stocks_data:
            stock = InventoryStock(
                sku_id=sku_id,
                total_quantity=total,
                available_quantity=available,
                reserved_quantity=total - available,
                warning_threshold=warning,
                critical_threshold=critical
            )
            integration_test_db.add(stock)
        integration_test_db.commit()
        
        # Act - 查询低库存商品
        response = integration_test_client.get("/api/inventory/low-stock?page=1&page_size=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3  # 至少有3个低库存商品
        
        # 验证返回的都是低库存商品
        for item in data["items"]:
            assert item["is_low_stock"] is True
    
    def test_get_inventory_transactions_success(self, integration_test_client, integration_test_db):
        """测试获取库存事务历史"""
        # Arrange - 创建库存和事务记录
        stock = InventoryStock(
            sku_id="TRANSACTION-TEST-SKU",
            total_quantity=100,
            available_quantity=100
        )
        integration_test_db.add(stock)
        integration_test_db.commit()
        
        # 创建多个事务记录
        transactions_data = [
            (TransactionType.IN_STOCK, 50, "purchase", "PO_001"),
            (TransactionType.DEDUCT, 20, "order", "ORDER_001"),
            (TransactionType.ADJUST, 10, "adjustment", "ADJ_001")
        ]
        
        for tx_type, quantity, ref_type, ref_id in transactions_data:
            transaction = InventoryTransaction(
                sku_id="TRANSACTION-TEST-SKU",
                transaction_type=tx_type,
                quantity=quantity,
                reference_type=ref_type,
                reference_id=ref_id,
                operator_id="admin_001"
            )
            integration_test_db.add(transaction)
        integration_test_db.commit()
        
        # Act - 查询事务历史
        response = integration_test_client.get(
            "/api/inventory/transactions/TRANSACTION-TEST-SKU?page=1&page_size=10"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert data["sku_id"] == "TRANSACTION-TEST-SKU"
        assert len(data["transactions"]) >= 3
        
        # 验证事务类型
        tx_types = [tx["transaction_type"] for tx in data["transactions"]]
        assert TransactionType.IN_STOCK in tx_types
        assert TransactionType.DEDUCT in tx_types
        assert TransactionType.ADJUST in tx_types


class TestInventoryBusinessFlowIntegration:
    """测试库存管理业务流程集成"""
    
    def test_complete_inventory_lifecycle(self, integration_test_client, integration_test_db):
        """测试完整的库存生命周期"""
        # Step 1: 创建库存
        inventory_data = {
            "sku_id": "LIFECYCLE-TEST-SKU",
            "initial_quantity": 100,
            "warning_threshold": 20,
            "critical_threshold": 10
        }
        create_response = integration_test_client.post("/api/inventory/stock", json=inventory_data)
        assert create_response.status_code == 201
        
        # Step 2: 预占库存（购物车）
        reserve_data = {
            "items": [{"sku_id": "LIFECYCLE-TEST-SKU", "quantity": 30}],
            "reservation_type": "cart",
            "reference_id": "lifecycle_cart_001",
            "expires_in_hours": 2
        }
        reserve_response = integration_test_client.post("/api/inventory/reserve", json=reserve_data)
        assert reserve_response.status_code == 200
        reservation_id = reserve_response.json()["reservation_id"]
        
        # Step 3: 验证预占后的库存状态
        stock_response = integration_test_client.get("/api/inventory/stock/LIFECYCLE-TEST-SKU")
        assert stock_response.status_code == 200
        stock_data = stock_response.json()
        assert stock_data["available_quantity"] == 70  # 100 - 30
        assert stock_data["reserved_quantity"] == 30
        
        # Step 4: 扣减库存（订单确认）
        deduct_data = {
            "items": [{"sku_id": "LIFECYCLE-TEST-SKU", "quantity": 25}],
            "reference_type": "order",
            "reference_id": "lifecycle_order_001",
            "operator_id": "customer_001"
        }
        deduct_response = integration_test_client.post("/api/inventory/deduct", json=deduct_data)
        assert deduct_response.status_code == 200
        
        # Step 5: 释放剩余预占
        release_data = {"reservation_ids": [reservation_id]}
        release_response = integration_test_client.delete("/api/inventory/reserve", json=release_data)
        assert release_response.status_code == 200
        
        # Step 6: 验证最终库存状态
        final_stock_response = integration_test_client.get("/api/inventory/stock/LIFECYCLE-TEST-SKU")
        assert final_stock_response.status_code == 200
        final_data = final_stock_response.json()
        assert final_data["total_quantity"] == 75      # 100 - 25 (扣减)
        assert final_data["available_quantity"] == 70   # 70 + 5 (释放剩余预占)
        assert final_data["reserved_quantity"] == 5     # 30 - 25 (扣减)
        
        # Step 7: 验证事务历史记录
        transactions_response = integration_test_client.get(
            "/api/inventory/transactions/LIFECYCLE-TEST-SKU"
        )
        assert transactions_response.status_code == 200
        tx_data = transactions_response.json()
        assert tx_data["total"] >= 2  # 至少有初始入库和扣减记录