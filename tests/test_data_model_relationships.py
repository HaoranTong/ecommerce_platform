"""
简单的数据模型关系测试
识别SQLAlchemy关系映射问题
"""
import sys
sys.path.append('.')

try:
    from app.data_models import Base, User, Category, Product, Order, OrderItem, Cart, CartItem, Inventory
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.inspection import inspect
    
    print("✅ 数据模型导入成功")
    
    # 创建内存数据库引擎
    engine = create_engine("sqlite:///:memory:", echo=False)
    SessionLocal = sessionmaker(bind=engine)
    
    # 创建表结构
    print("📊 开始创建表结构...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 表结构创建成功")
    except Exception as e:
        print(f"⚠️ 表结构创建有警告（可能是索引重复）: {e}")
        # 尝试删除后重新创建
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ 表结构重新创建成功")
    
    # 测试模型实例化
    print("\n🔍 测试模型实例化...")
    session = SessionLocal()
    
    # 1. 测试Category模型
    category = Category(name="测试分类", sort_order=1)
    session.add(category)
    session.commit()
    print("✅ Category模型实例化成功")
    
    # 2. 测试Product模型
    product = Product(
        name="测试商品",
        sku="TEST-001", 
        description="测试商品描述",
        category_id=category.id,
        price=99.99,
        stock_quantity=100,
        status="active"
    )
    session.add(product)
    session.commit()
    print("✅ Product模型实例化成功")
    
    # 3. 测试User模型
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    session.add(user)
    session.commit()
    print("✅ User模型实例化成功")
    
    # 4. 测试关系映射
    print("\n🔗 测试关系映射...")
    
    # Category -> Products关系
    try:
        products_in_category = category.products
        print(f"✅ Category.products关系正常: {len(products_in_category)} 个商品")
    except Exception as e:
        print(f"❌ Category.products关系错误: {e}")
    
    # Product -> Category关系
    try:
        product_category = product.category
        print(f"✅ Product.category关系正常: {product_category.name if product_category else 'None'}")
    except Exception as e:
        print(f"❌ Product.category关系错误: {e}")
        
    # Product -> OrderItems关系
    try:
        product_order_items = product.order_items
        print(f"✅ Product.order_items关系正常: {len(product_order_items)} 个订单项")
    except Exception as e:
        print(f"❌ Product.order_items关系错误: {e}")
    
    # User -> Orders关系
    try:
        user_orders = user.orders
        print(f"✅ User.orders关系正常: {len(user_orders)} 个订单")
    except Exception as e:
        print(f"❌ User.orders关系错误: {e}")
        
    # User -> Carts关系
    try:
        user_carts = user.carts
        print(f"✅ User.carts关系正常: {len(user_carts)} 个购物车")
    except Exception as e:
        print(f"❌ User.carts关系错误: {e}")
    
    # 5. 测试创建Order和OrderItem
    print("\n📦 测试Order和OrderItem创建...")
    order = Order(
        order_no="ORDER-001",
        user_id=user.id,
        status="pending",
        subtotal=99.99,
        shipping_fee=0.00,
        discount_amount=0.00,
        total_amount=99.99
    )
    session.add(order)
    session.commit()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_sku=product.sku,
        quantity=1,
        unit_price=product.price,
        total_price=product.price
    )
    session.add(order_item)
    session.commit()
    print("✅ Order和OrderItem创建成功")
    
    # 测试关系
    try:
        order_items = order.order_items
        print(f"✅ Order.order_items关系正常: {len(order_items)} 个订单项")
    except Exception as e:
        print(f"❌ Order.order_items关系错误: {e}")
        
    try:
        item_order = order_item.order
        print(f"✅ OrderItem.order关系正常: {item_order.order_no if item_order else 'None'}")
    except Exception as e:
        print(f"❌ OrderItem.order关系错误: {e}")
        
    try:
        item_product = order_item.product
        print(f"✅ OrderItem.product关系正常: {item_product.name if item_product else 'None'}")
    except Exception as e:
        print(f"❌ OrderItem.product关系错误: {e}")
    
    # 6. 测试购物车
    print("\n🛒 测试Cart和CartItem创建...")
    cart = Cart(
        user_id=user.id,
        status="active",
        total_amount=99.99
    )
    session.add(cart)
    session.commit()
    
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=2,
        unit_price=product.price,
        original_price=product.price,
        total_price=product.price * 2
    )
    session.add(cart_item)
    session.commit()
    print("✅ Cart和CartItem创建成功")
    
    # 测试购物车关系
    try:
        cart_items = cart.items
        print(f"✅ Cart.items关系正常: {len(cart_items)} 个购物车项")
    except Exception as e:
        print(f"❌ Cart.items关系错误: {e}")
        
    try:
        item_cart = cart_item.cart
        print(f"✅ CartItem.cart关系正常: {item_cart.status if item_cart else 'None'}")
    except Exception as e:
        print(f"❌ CartItem.cart关系错误: {e}")
        
    try:
        cart_item_product = cart_item.product
        print(f"✅ CartItem.product关系正常: {cart_item_product.name if cart_item_product else 'None'}")
    except Exception as e:
        print(f"❌ CartItem.product关系错误: {e}")
    
    # 7. 测试Inventory
    print("\n📊 测试Inventory创建...")
    inventory = Inventory(
        product_id=product.id,
        available_quantity=100,
        reserved_quantity=0,
        total_quantity=100,
        warning_threshold=10
    )
    session.add(inventory)
    session.commit()
    print("✅ Inventory创建成功")
    
    # 测试Inventory关系
    try:
        inventory_product = inventory.product
        print(f"✅ Inventory.product关系正常: {inventory_product.name if inventory_product else 'None'}")
    except Exception as e:
        print(f"❌ Inventory.product关系错误: {e}")
        
    try:
        product_inventory = product.inventory
        print(f"✅ Product.inventory关系正常: 总库存{product_inventory.total_quantity if product_inventory else 'None'}")
    except Exception as e:
        print(f"❌ Product.inventory关系错误: {e}")
    
    session.close()
    print("\n🎉 数据模型关系测试完成！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()