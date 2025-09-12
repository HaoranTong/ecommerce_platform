"""
库存管理模块集成测试

测试库存管理模块的完整功能，包括：
- 库存查询和创建
- 库存预占和释放  
- 库存扣减和调整
- 库存变动记录
"""

import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Product, Category, Inventory, InventoryTransaction, CartReservation
from app.services.inventory import InventoryService
from app.schemas.inventory import ReservationItem, DeductItem, InventoryAdjustment, AdjustmentType


# 测试数据库配置
TEST_DATABASE_URL = "mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform"

def get_test_db():
    """获取测试数据库会话"""
    engine = create_engine(TEST_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db


def setup_test_data(db: Session):
    """设置测试数据"""
    print("📝 设置测试数据...")
    
    # 先清理可能存在的测试数据
    try:
        db.query(CartReservation).filter(CartReservation.user_id.in_([999, 998])).delete(synchronize_session=False)
        db.query(InventoryTransaction).filter(InventoryTransaction.product_id.in_([9999, 9998])).delete(synchronize_session=False)
        db.query(Inventory).filter(Inventory.product_id.in_([9999, 9998])).delete(synchronize_session=False)
        db.query(Product).filter(Product.id.in_([9999, 9998])).delete(synchronize_session=False)
        db.query(Category).filter(Category.id == 9999).delete(synchronize_session=False)
        db.query(User).filter(User.email.in_(["test_inventory@example.com", "admin_inventory@example.com"])).delete(synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
    
    # 创建测试分类
    category = Category(id=9999, name="农产品测试", sort_order=1, is_active=True)
    db.add(category)
    db.commit()
    db.refresh(category)
    
    # 创建测试商品
    products = [
        Product(
            id=9999,
            name="有机苹果",
            sku="APPLE_TEST_001", 
            description="新鲜有机苹果",
            category_id=category.id,
            price=28.80,
            stock_quantity=100,
            status="active"
        ),
        Product(
            id=9998,
            name="有机橙子",
            sku="ORANGE_TEST_001",
            description="新鲜有机橙子", 
            category_id=category.id,
            price=32.50,
            stock_quantity=50,
            status="active"
        )
    ]
    
    for product in products:
        db.add(product)
    db.commit()
    
    # 创建测试用户
    user = User(
        id=999,
        username="test_inventory_user",
        email="test_inventory@example.com",
        password_hash="hashed_password",
        phone="13800138000",
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 创建管理员用户
    admin = User(
        id=998,
        username="admin_inventory_user",
        email="admin_inventory@example.com", 
        password_hash="hashed_password",
        phone="13800138001",
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✅ 测试数据创建完成: {len(products)}个商品, 2个用户")
    return {
        "category": category,
        "products": products,
        "user": user,
        "admin": admin
    }


def test_inventory_creation_and_query(db: Session, test_data: dict):
    """测试库存创建和查询"""
    print("\n🔍 测试库存创建和查询...")
    
    service = InventoryService(db)
    products = test_data["products"]
    
    for product in products:
        # 获取或创建库存记录
        inventory = service.get_or_create_inventory(product.id)
        assert inventory is not None
        assert inventory.product_id == product.id
        assert inventory.available_quantity == product.stock_quantity
        assert inventory.reserved_quantity == 0
        assert inventory.total_quantity == product.stock_quantity
        print(f"  ✅ 商品 {product.name} 库存记录创建成功: 可用{inventory.available_quantity}")
    
    # 测试批量查询
    product_ids = [p.id for p in products]
    inventories = service.get_inventories_batch(product_ids)
    assert len(inventories) == len(products)
    print(f"  ✅ 批量查询成功: 获取{len(inventories)}个库存记录")


def test_cart_reservation(db: Session, test_data: dict):
    """测试购物车库存预占"""
    print("\n🛒 测试购物车库存预占...")
    
    service = InventoryService(db)
    user = test_data["user"]
    products = test_data["products"]
    
    # 预占商品
    items = [
        ReservationItem(product_id=products[0].id, quantity=5),
        ReservationItem(product_id=products[1].id, quantity=3)
    ]
    
    result = service.reserve_for_cart(user.id, items, 30)
    assert "reservation_id" in result
    assert "expires_at" in result
    assert len(result["reserved_items"]) == 2
    
    print(f"  ✅ 购物车预占成功: {result['reservation_id']}")
    
    # 验证库存扣减
    for i, item in enumerate(items):
        inventory = service.get_inventory(item.product_id)
        expected_available = products[i].stock_quantity - item.quantity
        assert inventory.available_quantity == expected_available
        assert inventory.reserved_quantity == item.quantity
        print(f"    商品 {products[i].name}: 可用{inventory.available_quantity}, 预占{inventory.reserved_quantity}")
    
    # 测试释放预占
    success = service.release_cart_reservation(user.id)
    assert success
    print("  ✅ 购物车预占释放成功")
    
    # 验证库存恢复
    for i, item in enumerate(items):
        inventory = service.get_inventory(item.product_id)
        assert inventory.available_quantity == products[i].stock_quantity
        assert inventory.reserved_quantity == 0
        print(f"    商品 {products[i].name}: 库存已恢复到{inventory.available_quantity}")


def test_order_reservation(db: Session, test_data: dict):
    """测试订单库存预占"""
    print("\n📦 测试订单库存预占...")
    
    service = InventoryService(db)
    products = test_data["products"]
    
    order_id = 12345
    items = [
        ReservationItem(product_id=products[0].id, quantity=8),
        ReservationItem(product_id=products[1].id, quantity=5)
    ]
    
    result = service.reserve_for_order(order_id, items)
    assert "reservation_id" in result
    print(f"  ✅ 订单预占成功: {result['reservation_id']}")
    
    # 验证库存变化
    for i, item in enumerate(items):
        inventory = service.get_inventory(item.product_id)
        expected_available = products[i].stock_quantity - item.quantity
        assert inventory.available_quantity == expected_available
        assert inventory.reserved_quantity == item.quantity
        print(f"    商品 {products[i].name}: 可用{inventory.available_quantity}, 预占{inventory.reserved_quantity}")
    
    return order_id, items


def test_inventory_deduction(db: Session, test_data: dict, order_id: int, reserved_items: list):
    """测试库存扣减"""
    print("\n💳 测试库存扣减...")
    
    service = InventoryService(db)
    products = test_data["products"]
    
    # 扣减库存
    deduct_items = [
        DeductItem(product_id=item.product_id, quantity=item.quantity)
        for item in reserved_items
    ]
    
    success = service.deduct_inventory(order_id, deduct_items)
    assert success
    print("  ✅ 库存扣减成功")
    
    # 验证库存变化
    for i, item in enumerate(deduct_items):
        inventory = service.get_inventory(item.product_id)
        expected_available = products[i].stock_quantity - item.quantity
        assert inventory.available_quantity == expected_available
        assert inventory.reserved_quantity == 0  # 预占应该被清零
        print(f"    商品 {products[i].name}: 最终可用库存{inventory.available_quantity}")


def test_inventory_adjustment(db: Session, test_data: dict):
    """测试库存调整"""
    print("\n⚙️ 测试库存调整...")
    
    service = InventoryService(db)
    admin = test_data["admin"]
    products = test_data["products"]
    
    product = products[0]
    original_inventory = service.get_inventory(product.id)
    original_quantity = original_inventory.available_quantity
    
    # 增加库存
    adjustment = InventoryAdjustment(
        adjustment_type=AdjustmentType.ADD,
        quantity=20,
        reason="补货入库"
    )
    
    success = service.adjust_inventory(product.id, adjustment, admin.id)
    assert success
    print("  ✅ 库存增加调整成功")
    
    # 验证调整结果
    updated_inventory = service.get_inventory(product.id)
    expected_quantity = original_quantity + 20
    assert updated_inventory.available_quantity == expected_quantity
    print(f"    商品 {product.name}: {original_quantity} → {updated_inventory.available_quantity}")
    
    # 减少库存
    adjustment = InventoryAdjustment(
        adjustment_type=AdjustmentType.SUBTRACT,
        quantity=10,
        reason="损耗扣减"
    )
    
    success = service.adjust_inventory(product.id, adjustment, admin.id)
    assert success
    print("  ✅ 库存减少调整成功")
    
    # 验证调整结果
    final_inventory = service.get_inventory(product.id)
    expected_final = expected_quantity - 10
    assert final_inventory.available_quantity == expected_final
    print(f"    商品 {product.name}: {expected_quantity} → {final_inventory.available_quantity}")


def test_warning_threshold(db: Session, test_data: dict):
    """测试预警阈值"""
    print("\n⚠️ 测试预警阈值...")
    
    service = InventoryService(db)
    products = test_data["products"]
    
    product = products[0]
    
    # 设置预警阈值
    success = service.update_warning_threshold(product.id, 50)
    assert success
    print("  ✅ 预警阈值设置成功")
    
    # 验证预警状态
    inventory = service.get_inventory(product.id)
    assert inventory.warning_threshold == 50
    print(f"    商品 {product.name}: 预警阈值{inventory.warning_threshold}, 当前库存{inventory.available_quantity}")
    print(f"    低库存状态: {inventory.is_low_stock}")


def test_low_stock_query(db: Session, test_data: dict):
    """测试低库存查询"""
    print("\n📊 测试低库存查询...")
    
    service = InventoryService(db)
    
    # 获取低库存商品列表
    items, total = service.get_low_stock_products(page=1, page_size=10)
    
    print(f"  ✅ 低库存查询成功: 找到{total}个低库存商品")
    for item in items:
        print(f"    {item['product_name']}: 库存{item['available_quantity']}, 阈值{item['warning_threshold']}")


def test_transaction_history(db: Session, test_data: dict):
    """测试库存变动历史"""
    print("\n📝 测试库存变动历史...")
    
    service = InventoryService(db)
    products = test_data["products"]
    
    from app.schemas.inventory import TransactionQuery
    
    # 查询第一个商品的变动历史
    product = products[0]
    query = TransactionQuery(page=1, page_size=10)
    
    transactions, total = service.get_inventory_transactions(product.id, query)
    
    print(f"  ✅ 变动历史查询成功: 商品 {product.name} 有{total}条变动记录")
    for tx in transactions[:3]:  # 显示前3条记录
        print(f"    {tx.created_at.strftime('%H:%M:%S')} {tx.transaction_type.value} {tx.quantity} - {tx.reason}")


def cleanup_test_data(db: Session):
    """清理测试数据"""
    print("\n🧹 清理测试数据...")
    
    try:
        # 删除库存相关数据
        db.query(CartReservation).filter(CartReservation.user_id.in_([999, 998])).delete(synchronize_session=False)
        db.query(InventoryTransaction).filter(InventoryTransaction.product_id.in_([9999, 9998])).delete(synchronize_session=False)
        db.query(Inventory).filter(Inventory.product_id.in_([9999, 9998])).delete(synchronize_session=False)
        
        # 删除基础数据
        db.query(Product).filter(Product.id.in_([9999, 9998])).delete(synchronize_session=False)
        db.query(Category).filter(Category.id == 9999).delete(synchronize_session=False)
        db.query(User).filter(User.id.in_([999, 998])).delete(synchronize_session=False)
        
        db.commit()
        print("  ✅ 测试数据清理完成")
    except Exception as e:
        print(f"  ⚠️ 清理测试数据时出错: {e}")
        db.rollback()


def main():
    """主测试函数"""
    print("🚀 开始库存管理模块集成测试")
    print("=" * 50)
    
    db = get_test_db()
    
    try:
        # 设置测试数据
        test_data = setup_test_data(db)
        
        # 执行各项测试
        test_inventory_creation_and_query(db, test_data)
        test_cart_reservation(db, test_data)
        order_id, reserved_items = test_order_reservation(db, test_data)
        test_inventory_deduction(db, test_data, order_id, reserved_items)
        test_inventory_adjustment(db, test_data)
        test_warning_threshold(db, test_data)
        test_low_stock_query(db, test_data)
        test_transaction_history(db, test_data)
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！库存管理模块功能正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理测试数据
        cleanup_test_data(db)
        db.close()


if __name__ == "__main__":
    main()