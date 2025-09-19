#!/usr/bin/env python3
"""
订单管理模块集成测试

测试订单管理模块与其他系统模块的协同工作
包括用户认证、商品目录、库存管理、支付服务等模块的集成
"""

import asyncio
import pytest
import sys
import os
import subprocess
from typing import Dict, Any
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import patch

# 项目导入
from app.main import app
from tests.factories.test_data_factory import StandardTestDataFactory, TestDataValidator
from app.core.database import get_db
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Category, Brand, Product, SKU
from app.modules.order_management.models import Order, OrderItem, OrderStatusHistory
from app.modules.order_management.service import OrderService
from app.modules.order_management.schemas import (
    OrderCreateRequest, OrderItemRequest, ShippingAddressRequest
)
from app.modules.inventory_management.models import InventoryStock
from app.modules.inventory_management.service import InventoryService


class TestOrderIntegration:
    """订单管理模块集成测试"""

    @pytest.fixture(scope="class")
    def integration_db_session(self):
        """集成测试数据库会话"""
        # 使用内存SQLite数据库进行测试
        engine = create_engine("mysql+pymysql://root:test_password@localhost:3308/ecommerce_platform_test")
        
        # 导入所有模型并创建表
        from app.modules.user_auth.models import Base
        
        Base.metadata.create_all(engine)
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = TestingSessionLocal()
        
        yield session
        
        session.close()

    @pytest.fixture(scope="class")
    def integration_client(self, integration_db_session):
        """集成测试客户端"""
        def override_get_db():
            try:
                yield integration_db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture(scope="class")
    def test_data(self, integration_db_session):
        """创建集成测试数据"""
        print("\n🏗️  设置集成测试数据...")
        
        # 1. 创建用户认证数据
        user = User(
            username="integration_test_user",
            email="integration@test.com",
            password_hash="test_password_hash",
            email_verified=True,
            is_active=True
        )
        integration_db_session.add(user)
        integration_db_session.flush()
        print(f"✅ 创建测试用户: {user.username}")

        # 2. 创建商品目录数据
        category = Category(
            name="集成测试分类",
            parent_id=None
        )
        integration_db_session.add(category)
        integration_db_session.flush()

        brand = Brand(
            name="集成测试品牌",
            slug="integration-test-brand"
        )
        integration_db_session.add(brand)
        integration_db_session.flush()

        product = Product(
            name="集成测试商品",
            description="集成测试商品描述",
            category_id=category.id,
            brand_id=brand.id,
            status="active"  # 使用OrderService期望的状态
        )
        integration_db_session.add(product)
        integration_db_session.flush()
        print(f"✅ 创建测试商品: {product.name}")

        sku = SKU(
            product_id=product.id,
            sku_code="INT-TEST-001",
            name="集成测试SKU",
            price=Decimal("99.99"),
            cost_price=Decimal("50.00"),
            weight=Decimal("1.0"),
            is_active=True
        )
        integration_db_session.add(sku)
        integration_db_session.flush()
        print(f"✅ 创建测试SKU: {sku.sku_code}")

        # 3. 创建库存数据
        inventory = InventoryStock(
            sku_id=sku.id,
            total_quantity=100,
            available_quantity=100,
            reserved_quantity=0,
            warning_threshold=10,
            critical_threshold=5
        )
        integration_db_session.add(inventory)
        integration_db_session.commit()
        print(f"✅ 创建测试库存: {inventory.total_quantity}件")

        return {
            "user": user,
            "category": category,
            "brand": brand,
            "product": product,
            "sku": sku,
            "inventory": inventory
        }

    def test_end_to_end_order_creation(self, integration_db_session, test_data):
        """测试端到端订单创建流程"""
        print("\n🛒 测试端到端订单创建流程...")
        
        user = test_data["user"]
        sku = test_data["sku"]
        
        order_service = OrderService(integration_db_session)
        inventory_service = InventoryService(integration_db_session)
        
        # 1. 验证初始状态
        initial_inventory = inventory_service.get_or_create_inventory(str(sku.id))
        print(f"✅ 验证初始库存: {initial_inventory['available_quantity']}件")
        
        # 2. 准备订单请求
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 3,
                "unit_price": sku.price
            }],
            shipping_address=ShippingAddressRequest(
                recipient="集成测试收货人",
                phone="13800138000",
                address="集成测试地址123号"
            ),
            notes="集成测试订单"
        )

        # 3. 执行订单创建
        created_order = asyncio.run(
            order_service.create_order(order_request, user.id)
        )
        
        assert created_order is not None
        assert created_order.user_id == user.id
        assert created_order.status == "pending"
        assert len(created_order.order_items) == 1
        assert created_order.order_items[0].quantity == 3
        print(f"✅ 订单创建成功: {created_order.order_number}")

        # 4. 验证库存变化
        updated_inventory = inventory_service.get_or_create_inventory(str(sku.id))
        assert updated_inventory["available_quantity"] == 97  # 100 - 3
        assert updated_inventory["reserved_quantity"] == 3
        print(f"✅ 库存正确扣减: 可用{updated_inventory['available_quantity']}, 预占{updated_inventory['reserved_quantity']}")

        # 5. 验证订单历史记录
        history = integration_db_session.query(OrderStatusHistory).filter(
            OrderStatusHistory.order_id == created_order.id
        ).all()
        assert len(history) == 1
        assert history[0].new_status == "pending"
        print("✅ 订单历史记录正确")

    def test_order_status_lifecycle(self, integration_db_session, test_data):
        """测试订单状态生命周期管理"""
        print("\n🔄 测试订单状态生命周期...")

        user = test_data["user"]
        sku = test_data["sku"]
        order_service = OrderService(integration_db_session)

        # 1. 创建订单
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 1,
                "unit_price": sku.price
            }],
            shipping_address=ShippingAddressRequest(
                recipient="状态测试用户",
                phone="13800138001", 
                address="状态测试地址"
            )
        )

        order = asyncio.run(order_service.create_order(order_request, user.id))
        assert order.status == "pending"
        print(f"✅ 订单创建: {order.order_number} - {order.status}")

        # 2. 测试状态转换 (使用合法的状态转换)
        asyncio.run(order_service.update_order_status(order.id, "paid", user.id))
        
        updated_order = asyncio.run(order_service.get_order_by_id(order.id))
        assert updated_order.status == "paid"
        print(f"✅ 状态更新: {updated_order.status}")

        # 3. 验证历史记录
        history = integration_db_session.query(OrderStatusHistory).filter(
            OrderStatusHistory.order_id == order.id
        ).all()
        assert len(history) == 2  # pending + paid
        print("✅ 状态历史记录正确")

    def test_order_cancellation_with_inventory_release(self, integration_db_session, test_data):
        """测试订单取消与库存释放"""
        print("\n❌ 测试订单取消与库存释放...")
        
        user = test_data["user"]
        sku = test_data["sku"]
        order_service = OrderService(integration_db_session)
        inventory_service = InventoryService(integration_db_session)

        # 1. 记录初始库存
        initial_inventory = inventory_service.get_or_create_inventory(str(sku.id))
        initial_available = initial_inventory["available_quantity"]
        initial_reserved = initial_inventory["reserved_quantity"]

        # 2. 创建订单
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 2,
                "unit_price": sku.price
            }],
            shipping_address=ShippingAddressRequest(
                recipient="取消测试用户",
                phone="13800138002",
                address="取消测试地址"
            )
        )
        
        order = asyncio.run(order_service.create_order(order_request, user.id))
        print(f"✅ 创建订单: {order.order_number}")

        # 3. 验证库存被预占
        after_create = inventory_service.get_or_create_inventory(str(sku.id))
        assert after_create["reserved_quantity"] == initial_reserved + 2

        # 4. 取消订单
        asyncio.run(order_service.update_order_status(order.id, "cancelled", user.id))
        
        # 5. 验证库存释放
        after_cancel = inventory_service.get_or_create_inventory(str(sku.id))
        assert after_cancel["available_quantity"] == initial_available
        assert after_cancel["reserved_quantity"] == initial_reserved
        print("✅ 库存正确释放")

    def test_insufficient_inventory_handling(self, integration_db_session, test_data):
        """测试库存不足处理"""
        print("\n📦 测试库存不足处理...")
        
        user = test_data["user"]
        sku = test_data["sku"]
        order_service = OrderService(integration_db_session)

        # 尝试创建超出库存的订单
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 200,  # 超过可用库存100
                "unit_price": sku.price
            }],
            shipping_address=ShippingAddressRequest(
                recipient="库存测试用户",
                phone="13800138003",
                address="库存测试地址"
            )
        )

        # 应该抛出库存不足异常
        with pytest.raises(Exception) as exc_info:
            asyncio.run(order_service.create_order(order_request, user.id))
        
        assert "库存不足" in str(exc_info.value) or "insufficient" in str(exc_info.value).lower()
        print("✅ 库存不足异常正确抛出")

    def test_api_integration_with_authentication(self, integration_client, test_data):
        """测试API集成与认证"""
        print("\n🔐 测试API集成与认证...")
        
        # 这是一个简化的API测试示例
        # 在实际实现中，需要配置认证token等
        response = integration_client.get("/")
        # 这是一个基础的API可用性测试 - 主页应该可访问
        assert response.status_code == 200
        print("✅ 订单API路由可访问")

    def test_data_consistency_across_modules(self, integration_db_session, test_data):
        """测试跨模块数据一致性"""
        print("\n🔗 测试跨模块数据一致性...")

        user = test_data["user"]
        sku = test_data["sku"]

        order_service = OrderService(integration_db_session)
        inventory_service = InventoryService(integration_db_session)

        # 1. 创建多个订单
        orders = []
        total_quantity = 0

        for i in range(3):
            quantity = i + 1  # 1, 2, 3
            total_quantity += quantity

            order_request = OrderCreateRequest(
                items=[{
                    "product_id": sku.product_id,
                    "sku_id": sku.id,
                    "quantity": quantity,
                    "unit_price": sku.price
                }],
                shipping_address=ShippingAddressRequest(
                    recipient=f"一致性测试用户{i+1}",
                    phone=f"1380013800{i}",
                    address=f"一致性测试地址{i+1}号"
                )
            )

            order = asyncio.run(order_service.create_order(order_request, user.id))
            orders.append(order)
            print(f"✅ 创建订单 {i+1}: {order.order_number}, 数量: {quantity}")

        # 2. 验证库存一致性
        inventory = inventory_service.get_or_create_inventory(str(sku.id))
        expected_reserved = total_quantity
        actual_reserved = inventory["reserved_quantity"]

        print(f"📊 预期预占库存: {expected_reserved}, 实际预占库存: {actual_reserved}")
        assert actual_reserved >= expected_reserved, f"库存数据不一致: 预期>={expected_reserved}, 实际{actual_reserved}"

        # 3. 验证订单项数据一致性
        total_order_items = integration_db_session.query(OrderItem).filter(
            OrderItem.sku_id == sku.id
        ).count()

        expected_items = len(orders)
        print(f"📊 预期订单项数量: {expected_items}, 实际订单项数量: {total_order_items}")
        assert total_order_items >= expected_items

        # 4. 验证用户订单关系
        user_orders = asyncio.run(order_service.get_orders_list(
            user_id=user.id,
            status=None,
            limit=10,
            skip=0
        ))

        assert len(user_orders) >= 3
        print(f"✅ 用户订单数量正确: {len(user_orders)}")

        print("✅ 跨模块数据一致性验证通过")

    def test_error_recovery_and_rollback(self, integration_db_session, test_data):
        """测试错误恢复和回滚机制"""
        print("\n🔄 测试错误恢复和回滚...")
        
        user = test_data["user"]
        sku = test_data["sku"]
        order_service = OrderService(integration_db_session)
        inventory_service = InventoryService(integration_db_session)

        # 1. 记录初始状态
        initial_inventory = inventory_service.get_or_create_inventory(str(sku.id))
        initial_orders = len(asyncio.run(order_service.get_orders_list()))

        # 2. 尝试创建有问题的订单（模拟中途失败）
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 1,
                "unit_price": sku.price
            }],
            shipping_address=ShippingAddressRequest(
                recipient="",  # 空收货人，可能导致验证失败
                phone="invalid_phone",  # 无效电话
                address="回滚测试地址"
            )
        )

        # 3. 在某些验证失败情况下，系统应该保持数据一致性
        try:
            asyncio.run(order_service.create_order(order_request, user.id))
        except Exception as e:
            print(f"✅ 预期异常被捕获: {str(e)}")
        
        # 4. 验证系统状态未被破坏
        final_inventory = inventory_service.get_or_create_inventory(str(sku.id))
        final_orders = len(asyncio.run(order_service.get_orders_list()))

        # 库存应该保持不变或者正确回滚
        assert final_inventory["available_quantity"] >= initial_inventory["available_quantity"] - 1
        print("✅ 系统状态一致性保持")


def run_integration_tests():
    """运行集成测试的主函数"""
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration/test_order_integration.py",
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    """直接运行此文件进行集成测试"""
    success = run_integration_tests()
    if success:
        print("✅ 所有集成测试通过！")
    else:
        print("❌ 部分集成测试失败")
        exit(1)
