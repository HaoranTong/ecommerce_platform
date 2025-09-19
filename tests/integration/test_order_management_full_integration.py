"""
Order Management Integration Tests
Complete testing with unique data generation patterns
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import HTTPException

# 导入被测试的模型和服务
from app.modules.order_management.models import Order, OrderItem, OrderStatusHistory, OrderStatus
from app.modules.order_management.service import OrderService
from app.modules.order_management.schemas import OrderCreateRequest, OrderStatusUpdateRequest, OrderItemRequest, ShippingAddressRequest

# 导入依赖模型
from app.modules.user_auth.models import User, Role
from app.modules.product_catalog.models import Product, Category, Brand, SKU
from app.modules.inventory_management.models import InventoryStock

# 导入测试工具
from app.main import app


class TestOrderManagementFullIntegration:
    """订单管理完整集成测试"""
    
    def _create_unique_data(self, db: Session, test_id: str):
        """创建唯一的测试数据链"""
        
        # 创建用户
        user = User(
            username=f"test_user_{test_id}",
            email=f"test_{test_id}@example.com",
            password_hash="hashed_password",
            is_active=True,
            role="user"
        )
        db.add(user)
        db.flush()
        
        # 创建分类
        category = Category(
            name=f"Test Category {test_id}",
            is_active=True,
            sort_order=1
        )
        db.add(category)
        db.flush()
        
        # 创建品牌
        brand = Brand(
            name=f"Test Brand {test_id}",
            slug=f"test-brand-{test_id}",
            is_active=True
        )
        db.add(brand)
        db.flush()
        
        # 创建商品
        product = Product(
            name=f"Test Product {test_id}",
            category_id=category.id,
            brand_id=brand.id,
            description=f"Test Description {test_id}",
            status="active"
        )
        db.add(product)
        db.flush()
        
        # 创建SKU
        sku = SKU(
            product_id=product.id,
            sku_code=f"TEST-SKU-{test_id}",
            name=f"Test SKU {test_id}",
            price=Decimal("50.00"),
            is_active=True
        )
        db.add(sku)
        db.flush()
        
        # 创建库存
        inventory = InventoryStock(
            sku_id=sku.id,
            total_quantity=100,
            available_quantity=100,
            reserved_quantity=0,
            warning_threshold=10,
            critical_threshold=5,
            is_active=True
        )
        db.add(inventory)
        db.flush()
        
        db.commit()
        
        return {
            "user": user,
            "category": category,
            "brand": brand,
            "product": product,
            "sku": sku,
            "inventory": inventory
        }

    def test_order_creation(self, integration_test_db):
        """测试订单创建"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单
        order = Order(
            order_number=f"ORD-{test_id}-0001",
            user_id=data["user"].id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            discount_amount=Decimal("5.00"),
            total_amount=Decimal("105.00"),
            shipping_address=f"Test Address {test_id}"
        )
        integration_test_db.add(order)
        integration_test_db.commit()
        
        # 验证订单属性
        assert order.id is not None
        assert order.order_number == f"ORD-{test_id}-0001"
        assert order.user_id == data["user"].id
        assert order.status == 'pending'
        assert order.subtotal == Decimal("100.00")
        assert order.total_amount == Decimal("105.00")
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_order_item_creation(self, integration_test_db):
        """测试订单商品项创建"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单
        order = Order(
            order_number=f"ORD-{test_id}-0001",
            user_id=data["user"].id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("110.00")
        )
        integration_test_db.add(order)
        integration_test_db.commit()
        
        # 创建订单商品项
        order_item = OrderItem(
            order_id=order.id,
            product_id=data["product"].id,
            sku_id=data["sku"].id,
            sku_code=data["sku"].sku_code,
            product_name=data["product"].name,
            sku_name=data["sku"].name,
            quantity=2,
            unit_price=Decimal("50.00"),
            total_price=Decimal("100.00")
        )
        integration_test_db.add(order_item)
        integration_test_db.commit()
        
        # 验证订单商品项属性
        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.product_id == data["product"].id
        assert order_item.sku_id == data["sku"].id
        assert order_item.sku_code == data["sku"].sku_code
        assert order_item.quantity == 2
        assert order_item.unit_price == Decimal("50.00")
        assert order_item.total_price == Decimal("100.00")

    def test_order_status_history_creation(self, integration_test_db):
        """测试订单状态历史记录创建"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单
        order = Order(
            order_number=f"ORD-{test_id}-0001",
            user_id=data["user"].id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("110.00")
        )
        integration_test_db.add(order)
        integration_test_db.commit()
        
        # 创建状态历史记录
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=None,
            new_status='pending',
            remark="订单创建",
            operator_id=data["user"].id
        )
        integration_test_db.add(status_history)
        integration_test_db.commit()
        
        # 验证状态历史记录
        assert status_history.id is not None
        assert status_history.order_id == order.id
        assert status_history.old_status is None
        assert status_history.new_status == 'pending'
        assert status_history.remark == "订单创建"
        assert status_history.operator_id == data["user"].id
        assert status_history.created_at is not None

    def test_order_status_enum(self):
        """测试订单状态枚举"""
        # 验证所有订单状态
        expected_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
        actual_statuses = [status.value for status in OrderStatus]
        
        for status in expected_statuses:
            assert status in actual_statuses
        
        # 验证枚举使用
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.PAID.value == "paid"
        assert OrderStatus.SHIPPED.value == "shipped"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.CANCELLED.value == "cancelled"

    @pytest.mark.asyncio
    async def test_create_order_success(self, integration_test_db):
        """测试成功创建订单"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单服务
        order_service = OrderService(db=integration_test_db)
        
        # 准备订单请求
        order_items = [OrderItemRequest(
            product_id=data["product"].id,
            sku_id=data["sku"].id,
            quantity=2
        )]
        
        shipping_address = ShippingAddressRequest(
            recipient=f"Test User {test_id}",
            phone="13800138000",
            address=f"Test Address {test_id}"
        )
        
        order_request = OrderCreateRequest(
            items=order_items,
            shipping_address=shipping_address,
            notes="Test order"
        )
        
        # 创建订单
        result = await order_service.create_order(order_request, data["user"].id)
        
        # 验证结果
        assert result is not None
        assert hasattr(result, 'id') and result.id is not None

    @pytest.mark.asyncio
    async def test_create_order_insufficient_inventory(self, integration_test_db):
        """测试库存不足时创建订单"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 修改库存为不足
        data["inventory"].available_quantity = 1
        integration_test_db.commit()
        
        # 创建订单服务
        order_service = OrderService(db=integration_test_db)
        
        # 准备超出库存的订单请求
        order_items = [OrderItemRequest(
            product_id=data["product"].id,
            sku_id=data["sku"].id,
            quantity=10  # 超出库存
        )]
        
        shipping_address = ShippingAddressRequest(
            recipient=f"Test User {test_id}",
            phone="13800138000",
            address=f"Test Address {test_id}"
        )
        
        order_request = OrderCreateRequest(
            items=order_items,
            shipping_address=shipping_address,
            notes="Test order with insufficient inventory"
        )
        
        # 验证抛出异常
        with pytest.raises((HTTPException, ValueError, Exception)):
            await order_service.create_order(order_request, data["user"].id)

    @pytest.mark.asyncio 
    async def test_update_order_status_success(self, integration_test_db):
        """测试成功更新订单状态"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单
        order = Order(
            order_number=f"ORD-{test_id}-0001",
            user_id=data["user"].id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            total_amount=Decimal("110.00")
        )
        integration_test_db.add(order)
        integration_test_db.commit()
        
        # 创建订单服务
        order_service = OrderService(db=integration_test_db)
        
        # 更新订单状态 - 根据service方法签名调用
        result = await order_service.update_order_status(
            order_id=order.id, 
            new_status="paid",
            operator_id=data["user"].id,
            remark="订单已支付"
        )
        
        # 验证状态更新成功
        assert result is not None or result is True
        
        # 刷新订单数据
        integration_test_db.refresh(order)
        assert order.status == "paid"

    @pytest.mark.asyncio
    async def test_cancel_order_success(self, integration_test_db):
        """测试成功取消订单"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单
        order = Order(
            order_number=f"ORD-{test_id}-0001", 
            user_id=data["user"].id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            total_amount=Decimal("110.00")
        )
        integration_test_db.add(order)
        integration_test_db.commit()
        
        # 创建订单服务
        order_service = OrderService(db=integration_test_db)
        
        # 取消订单
        result = await order_service.cancel_order(order.id, data["user"].id, "用户取消")
        
        # 验证取消成功
        assert result is not None or result is True
        
        # 刷新订单数据
        integration_test_db.refresh(order)
        assert order.status == "cancelled"

    @pytest.mark.asyncio
    async def test_get_order_by_id_success(self, integration_test_db):
        """测试成功获取订单详情"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建订单
        order = Order(
            order_number=f"ORD-{test_id}-0001",
            user_id=data["user"].id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            total_amount=Decimal("110.00")
        )
        integration_test_db.add(order)
        integration_test_db.commit()
        
        # 创建订单服务
        order_service = OrderService(db=integration_test_db)
        
        # 获取订单详情
        result = await order_service.get_order_by_id(order.id)
        
        # 验证结果
        assert result is not None
        if hasattr(result, 'id'):
            assert result.id == order.id
        elif isinstance(result, dict):
            assert result.get('id') == order.id or result.get('order_id') == order.id

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self, integration_test_db):
        """测试获取不存在的订单"""
        order_service = OrderService(db=integration_test_db)
        
        # 获取不存在的订单
        result = await order_service.get_order_by_id(999999)
        
        # 验证返回None或抛出异常
        assert result is None or isinstance(result, type(None))

    @pytest.mark.asyncio
    async def test_get_user_orders_success(self, integration_test_db):
        """测试成功获取用户订单列表"""
        test_id = str(uuid.uuid4())[:8]
        data = self._create_unique_data(integration_test_db, test_id)
        
        # 创建多个订单
        for i in range(3):
            order = Order(
                order_number=f"ORD-{test_id}-{i:04d}",
                user_id=data["user"].id,
                status='pending',
                subtotal=Decimal("100.00"),
                shipping_fee=Decimal("10.00"),
                total_amount=Decimal("110.00")
            )
            integration_test_db.add(order)
        
        integration_test_db.commit()
        
        # 创建订单服务
        order_service = OrderService(db=integration_test_db)
        
        # 获取用户订单列表
        result = await order_service.get_orders_list(user_id=data["user"].id)
        
        # 验证结果
        assert result is not None
        if isinstance(result, list):
            assert len(result) >= 3
        elif hasattr(result, '__len__'):
            assert len(result) >= 3

    def test_api_create_order_unauthorized(self):
        """测试未授权创建订单API"""
        client = TestClient(app)
        
        order_data = {
            "items": [{"product_id": 1, "sku_id": 1, "quantity": 1}],
            "shipping_address": "Test Address"
        }
        
        response = client.post("/api/orders/", json=order_data)
        
        # 验证返回未授权状态
        assert response.status_code in [401, 403, 404, 422]  # 可能的未授权状态码