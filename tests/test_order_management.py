"""
文件名：test_order_management.py
文件路径：tests/test_order_management.py
功能描述：订单管理模块单元测试

测试覆盖：
- 订单模型测试 (Order, OrderItem, OrderStatusHistory)
- 订单服务层测试 (OrderService)
- 订单API接口测试 (Router endpoints)

测试策略：
- 使用SQLite内存数据库 (符合testing-standards.md)
- 单元测试独立性原则
- 全面的边界条件测试

依赖模块：
- app.modules.order_management.models
- app.modules.order_management.service
- app.modules.order_management.schemas

创建时间：2025-09-15
最后修改：2025-09-15
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import HTTPException

# 导入被测试的模型和服务
from app.modules.order_management.models import Order, OrderItem, OrderStatusHistory, OrderStatus
from app.modules.order_management.service import OrderService
from app.modules.order_management.schemas import OrderCreateRequest, OrderStatusUpdateRequest

# 导入依赖模型
from app.modules.user_auth.models import User, Role
from app.modules.product_catalog.models import Product, Category, Brand, SKU
from app.modules.inventory_management.models import InventoryStock

# 导入测试工具
from app.main import app


class TestOrderModels:
    """订单模型测试类"""
    
    def test_order_creation(self, unit_test_db):
        """测试订单创建"""
        db = unit_test_db
        
        # 创建测试用户
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # 创建订单
        order = Order(
            order_number="ORD-2025-0001",
            user_id=user.id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            discount_amount=Decimal("5.00"),
            total_amount=Decimal("105.00"),
            shipping_address="Test Address"
        )
        db.add(order)
        db.commit()
        
        # 验证订单属性
        assert order.id is not None
        assert order.order_number == "ORD-2025-0001"
        assert order.user_id == user.id
        assert order.status == 'pending'
        assert order.subtotal == Decimal("100.00")
        assert order.total_amount == Decimal("105.00")
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_order_item_creation(self, unit_test_db):
        """测试订单商品项创建"""
        db = unit_test_db
        
        # 创建测试数据
        user = User(username="test_user", email="test@example.com",
                   password_hash="hashed", is_active=True)
        db.add(user)
        
        category = Category(name="Test Category", is_active=True, sort_order=1)
        db.add(category)
        
        brand = Brand(name="Test Brand", slug="test-brand", is_active=True)
        db.add(brand)
        db.commit()
        
        product = Product(
            name="Test Product",
            category_id=category.id,
            brand_id=brand.id,
            description="Test Description",
            status="active"
        )
        db.add(product)
        db.commit()
        
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-SKU-001",
            name="Test SKU",
            price=Decimal("50.00"),
            is_active=True
        )
        db.add(sku)
        db.commit()
        
        order = Order(
            order_number="ORD-2025-0001",
            user_id=user.id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("110.00")
        )
        db.add(order)
        db.commit()
        
        # 创建订单商品项
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            sku_id=sku.id,
            sku_code=sku.sku_code,
            product_name=product.name,
            sku_name=sku.name,
            quantity=2,
            unit_price=Decimal("50.00"),
            total_price=Decimal("100.00")
        )
        db.add(order_item)
        db.commit()
        
        # 验证订单商品项属性
        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.product_id == product.id
        assert order_item.sku_id == sku.id
        assert order_item.sku_code == "TEST-SKU-001"
        assert order_item.quantity == 2
        assert order_item.unit_price == Decimal("50.00")
        assert order_item.total_price == Decimal("100.00")

    def test_order_status_history_creation(self, unit_test_db):
        """测试订单状态历史记录创建"""
        db = unit_test_db
        
        # 创建测试数据
        user = User(username="test_user", email="test@example.com",
                   password_hash="hashed", is_active=True)
        db.add(user)
        db.commit()
        
        order = Order(
            order_number="ORD-2025-0001",
            user_id=user.id,
            status='pending',
            subtotal=Decimal("100.00"),
            shipping_fee=Decimal("10.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("110.00")
        )
        db.add(order)
        db.commit()
        
        # 创建状态历史记录
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=None,
            new_status='pending',
            remark="订单创建",
            operator_id=user.id
        )
        db.add(status_history)
        db.commit()
        
        # 验证状态历史记录
        assert status_history.id is not None
        assert status_history.order_id == order.id
        assert status_history.old_status is None
        assert status_history.new_status == 'pending'
        assert status_history.remark == "订单创建"
        assert status_history.operator_id == user.id
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


class TestOrderService:
    """订单服务层测试类"""
    
    @pytest.fixture
    def order_service(self, unit_test_db):
        """订单服务实例"""
        return OrderService(db=unit_test_db)
    
    @pytest.fixture
    def test_user(self, unit_test_db):
        """测试用户"""
        db = unit_test_db
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashed_password",
            is_active=True
        )
        db.add(user)
        db.commit()
        return user
    
    @pytest.fixture
    def test_product_data(self, unit_test_db):
        """测试商品数据"""
        db = unit_test_db
        
        category = Category(name="Test Category", is_active=True, sort_order=1)
        db.add(category)
        
        brand = Brand(name="Test Brand", slug="test-brand", is_active=True)
        db.add(brand)
        db.commit()
        
        product = Product(
            name="Test Product",
            category_id=category.id,
            brand_id=brand.id,
            description="Test Description",
            status="active"
        )
        db.add(product)
        db.commit()
        
        sku = SKU(
            product_id=product.id,
            sku_code="TEST-SKU-001",
            name="Test SKU",
            price=Decimal("50.00"),
            is_active=True
        )
        db.add(sku)
        db.commit()
        
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
        db.commit()
        
        return {
            "category": category,
            "brand": brand,
            "product": product,
            "sku": sku,
            "inventory": inventory
        }

    @pytest.mark.asyncio
    async def test_create_order_success(self, order_service, test_user, test_product_data):
        """测试成功创建订单"""
        sku = test_product_data["sku"]
        
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 2,
                "unit_price": sku.price
            }],
            shipping_address={
                "recipient": "Test User",
                "phone": "13800138000",
                "address": "Test Shipping Address"
            },
            notes="Test order notes"
        )
        
        result = await order_service.create_order(
            order_data=order_request,
            user_id=test_user.id
        )
        
        assert result is not None
        assert result.user_id == test_user.id
        assert result.status == 'pending'
        assert result.subtotal == Decimal("100.00")  # 2 * 50.00
        assert result.total_amount > result.subtotal  # 包含运费

    @pytest.mark.asyncio
    async def test_create_order_insufficient_inventory(self, order_service, test_user, test_product_data):
        """测试库存不足时创建订单失败"""
        sku = test_product_data["sku"]
        
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 200,  # 超过库存数量
                "unit_price": sku.price
            }],
            shipping_address={
                "recipient": "Test User",
                "phone": "13800138000",
                "address": "Test Address"
            }
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await order_service.create_order(
                order_data=order_request,
                user_id=test_user.id
            )
        
        assert exc_info.value.status_code == 400
        assert "库存不足" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_order_status_success(self, order_service, test_user, test_product_data):
        """测试成功更新订单状态"""
        # 先创建订单
        sku = test_product_data["sku"]
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 1,
                "unit_price": sku.price
            }],
            shipping_address={
                "recipient": "Test User",
                "phone": "13800138000",
                "address": "Test Address"
            }
        )
        
        order = await order_service.create_order(
            order_data=order_request,
            user_id=test_user.id
        )
        
        # 更新订单状态
        update_request = OrderStatusUpdateRequest(
            status='paid',
            remark="Payment confirmed"
        )
        
        updated_order = await order_service.update_order_status(
            order_id=order.id,
            new_status=update_request.status,
            operator_id=test_user.id,
            remark=update_request.remark
        )
        
        assert updated_order.status == 'paid'
        
        # 验证状态历史记录
        history = await order_service.get_order_status_history(order.id)
        assert len(history) >= 2  # 创建时一条，更新时一条
        assert history[-1].new_status == 'paid'
        assert history[-1].remark == "Payment confirmed"

    @pytest.mark.asyncio
    async def test_cancel_order_success(self, order_service, test_user, test_product_data):
        """测试成功取消订单"""
        # 先创建订单
        sku = test_product_data["sku"]
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 2,
                "unit_price": sku.price
            }],
            shipping_address={
                "recipient": "Test User",
                "phone": "13800138000", 
                "address": "Test Address"
            }
        )
        
        order = await order_service.create_order(
            order_data=order_request,
            user_id=test_user.id
        )
        
        # 取消订单
        result = await order_service.cancel_order(
            order_id=order.id,
            operator_id=test_user.id,
            reason="User requested cancellation"
        )
        
        assert result is True
        
        # 验证订单状态
        cancelled_order = await order_service.get_order_by_id(order.id)
        assert cancelled_order.status == 'cancelled'
        
        # 验证库存已释放
        inventory = order_service.db.query(InventoryStock).filter(
            InventoryStock.sku_id == sku.id
        ).first()
        assert inventory.available_quantity == 100  # 库存已恢复

    @pytest.mark.asyncio
    async def test_get_order_by_id_success(self, order_service, test_user, test_product_data):
        """测试根据ID获取订单"""
        # 先创建订单
        sku = test_product_data["sku"]
        order_request = OrderCreateRequest(
            items=[{
                "product_id": sku.product_id,
                "sku_id": sku.id,
                "quantity": 1,
                "unit_price": sku.price
            }],
            shipping_address={
                "recipient": "Test User",
                "phone": "13800138000",
                "address": "Test Address"
            }
        )
        
        created_order = await order_service.create_order(
            order_data=order_request,
            user_id=test_user.id
        )
        
        # 获取订单
        retrieved_order = await order_service.get_order_by_id(created_order.id)
        
        assert retrieved_order is not None
        assert retrieved_order.id == created_order.id
        assert retrieved_order.user_id == test_user.id
        assert retrieved_order.order_number == created_order.order_number

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self, order_service):
        """测试获取不存在的订单"""
        result = await order_service.get_order_by_id(99999)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_orders_success(self, order_service, test_user, test_product_data):
        """测试获取用户订单列表"""
        # 创建多个订单
        sku = test_product_data["sku"]
        
        for i in range(3):
            order_request = OrderCreateRequest(
                items=[{
                    "product_id": sku.product_id,
                    "sku_id": sku.id,
                    "quantity": i + 1,
                    "unit_price": sku.price
                }],
                shipping_address={
                    "recipient": f"Test User {i+1}",
                    "phone": "13800138000",
                    "address": f"Test Address {i+1}"
                }
            )
            
            await order_service.create_order(
                order_data=order_request,
                user_id=test_user.id
            )
        
        # 获取用户订单
        orders = await order_service.get_orders_list(
            user_id=test_user.id,
            skip=0,
            limit=10
        )
        
        assert len(orders) == 3
        for order in orders:
            assert order.user_id == test_user.id


class TestOrderAPI:
    """订单API接口测试类"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)
    
    def test_api_create_order_unauthorized(self, client):
        """测试未授权创建订单"""
        order_data = {
            "items": [{
                "product_id": 1,
                "sku_id": 1,
                "quantity": 1,
                "unit_price": 50.00
            }],
            "shipping_address": "Test Address"
        }
        
        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code == 403  # 禁止访问（未授权）

    # 注意：完整的API测试需要认证Mock，这里只测试基础结构
    # 更完整的API测试将在集成测试中进行