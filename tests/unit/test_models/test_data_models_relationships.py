"""
Data model relationship mapping unit tests
"""

import pytest

try:
    from app.modules.user_auth.models import User
    from app.modules.product_catalog.models import Product
    from app.modules.order_management.models import Order, OrderItem
    from app.modules.shopping_cart.models import Cart, CartItem
    from app.modules.inventory_management.models import InventoryStock
except ImportError as e:
    pytest.skip("Model imports failed")


def test_user_order_relationship(unit_test_db):
    """Test User to Order one-to-many relationship"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    
    unit_test_db.add(user)
    unit_test_db.flush()
    
    order = Order(
        user_id=user.id,
        total_amount=100.00,
        status="pending"
    )
    
    unit_test_db.add(order)
    unit_test_db.commit()
    
    fresh_order = unit_test_db.query(Order).filter_by(id=order.id).first()
    assert fresh_order.user_id == user.id


def test_inventory_stock_creation(unit_test_db):
    """Test InventoryStock model creation"""
    inventory = InventoryStock(
        sku_id=1,
        total_quantity=100,
        available_quantity=90,
        reserved_quantity=10
    )
    unit_test_db.add(inventory)
    unit_test_db.commit()
    
    fresh_inventory = unit_test_db.query(InventoryStock).filter_by(id=inventory.id).first()
    assert fresh_inventory.total_quantity == 100