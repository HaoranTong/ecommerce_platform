"""
数据模型关系测试 - SQLite版本
用于在不启动Docker的情况下测试SQLAlchemy关系映射
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# 将app目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.data_models import Base, User, Product, Category, Order, CartItem, OrderItem

def test_models_with_sqlite():
    """使用SQLite测试数据模型关系"""
    print("🧪 开始使用SQLite测试数据模型关系...")
    
    # 创建SQLite内存数据库
    engine = create_engine('sqlite:///:memory:', echo=True)
    
    try:
        # 创建所有表
        print("\n📋 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 测试基本模型创建
        print("\n👤 测试用户模型...")
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            full_name="Test User"
        )
        session.add(user)
        session.commit()
        print("✅ 用户创建成功")
        
        # 测试分类模型
        print("\n📂 测试分类模型...")
        category = Category(
            name="水果",
            description="新鲜水果类",
            slug="fruits"
        )
        session.add(category)
        session.commit()
        print("✅ 分类创建成功")
        
        # 测试商品模型
        print("\n🛍️ 测试商品模型...")
        product = Product(
            name="苹果",
            description="新鲜红苹果",
            price=5.99,
            sku="APPLE001"
        )
        session.add(product)
        session.commit()
        print("✅ 商品创建成功")
        
        # 测试商品-分类关联
        print("\n🔗 测试商品-分类关联...")
        # 直接关联分类（一对多关系）
        product.category_id = category.id
        session.commit()
        print("✅ 商品-分类关联成功")
        
        # 测试关系查询
        print("\n🔍 测试关系查询...")
        
        # 查询商品的分类
        product_with_categories = session.query(Product).filter_by(id=product.id).first()
        print(f"商品: {product_with_categories.name}")
        print(f"商品分类: {product_with_categories.category.name if product_with_categories.category else 'None'}")
        
        # 查询分类的商品
        category_with_products = session.query(Category).filter_by(id=category.id).first()
        print(f"分类: {category_with_products.name}")
        print(f"关联商品数量: {len(category_with_products.products)}")
        
        # 测试订单模型
        print("\n📝 测试订单模型...")
        order = Order(
            user_id=user.id,
            total_amount=5.99,
            status='pending'
        )
        session.add(order)
        session.commit()
        print("✅ 订单创建成功")
        
        # 测试订单项
        print("\n📦 测试订单项...")
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            unit_price=5.99,
            total_price=11.98
        )
        session.add(order_item)
        session.commit()
        print("✅ 订单项创建成功")
        
        # 测试购物车
        print("\n🛒 测试购物车...")
        cart_item = CartItem(
            user_id=user.id,
            product_id=product.id,
            quantity=1
        )
        session.add(cart_item)
        session.commit()
        print("✅ 购物车项创建成功")
        
        # 验证所有关系
        print("\n✅ 验证所有关系...")
        user_with_relations = session.query(User).filter_by(id=user.id).first()
        print(f"用户订单数量: {len(user_with_relations.orders)}")
        print(f"用户购物车项数量: {len(user_with_relations.cart_items)}")
        
        order_with_items = session.query(Order).filter_by(id=order.id).first()
        print(f"订单项数量: {len(order_with_items.items)}")
        print(f"订单用户: {order_with_items.user.username}")
        
        session.close()
        print("\n🎉 所有数据模型关系测试通过！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_models_with_sqlite()
    if success:
        print("\n✅ 数据模型关系测试完成 - 无问题发现")
    else:
        print("\n❌ 数据模型关系测试失败 - 需要修复")
        sys.exit(1)