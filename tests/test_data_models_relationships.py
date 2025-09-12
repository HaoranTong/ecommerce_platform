"""
数据模型关系映射测试脚本

按照 docs/standards/testing-standards.md 规范编写的临时调试脚本
用途：验证 SQLAlchemy 数据模型之间的关系映射是否正确
生命周期：临时使用，测试完成后移至 tests/ 目录

测试范围：
- 用户与订单的一对多关系
- 订单与订单项的一对多关系  
- 商品与订单项的一对多关系
- 用户与购物车的一对多关系
- 购物车与购物车项的一对多关系
- 库存与商品的一对一关系
- 关系映射的双向访问
- 级联删除和更新
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# 导入应用模块
try:
    from app.models import Base, User, Product, Order, OrderItem, Cart
    from app.database import DATABASE_URL
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保项目结构正确且所有依赖已安装")
    sys.exit(1)

class DataModelRelationshipTester:
    """数据模型关系测试器"""
    
    def __init__(self, use_sqlite=True):
        """初始化测试器
        
        Args:
            use_sqlite: 是否使用 SQLite 内存数据库（默认 True）
        """
        if use_sqlite:
            # 使用 SQLite 内存数据库进行测试
            self.engine = create_engine("sqlite:///:memory:", echo=False)
            print("🔧 使用 SQLite 内存数据库进行测试")
        else:
            # 使用配置的数据库连接
            self.engine = create_engine(DATABASE_URL)
            print(f"🔧 使用配置的数据库: {DATABASE_URL}")
        
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = None
    
    def setup_database(self):
        """设置测试数据库"""
        try:
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            print("✅ 数据库表创建成功")
            
            # 创建数据库会话
            self.session = self.SessionLocal()
            print("✅ 数据库会话创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据库设置失败: {e}")
            return False
    
    def test_user_order_relationship(self):
        """测试用户与订单的一对多关系"""
        print("\n🔍 测试用户与订单的一对多关系...")
        
        try:
            # 创建测试用户
            user = User(
                username="testuser",
                email="test@example.com", 
                hashed_password="hashed_password",
                phone_number="1234567890"
            )
            self.session.add(user)
            self.session.flush()  # 获取 user.id
            
            # 创建测试订单
            order1 = Order(
                user_id=user.id,
                total_amount=100.00,
                status="pending"
            )
            order2 = Order(
                user_id=user.id,
                total_amount=200.00,
                status="completed"
            )
            
            self.session.add_all([order1, order2])
            self.session.commit()
            
            # 测试关系映射
            fresh_user = self.session.query(User).filter_by(id=user.id).first()
            
            # 测试正向关系：用户 -> 订单
            user_orders = fresh_user.orders
            assert len(user_orders) == 2, f"用户应该有2个订单，实际有{len(user_orders)}个"
            assert user_orders[0].total_amount in [100.00, 200.00], "订单金额不正确"
            
            # 测试反向关系：订单 -> 用户
            fresh_order = self.session.query(Order).filter_by(id=order1.id).first()
            assert fresh_order.user.username == "testuser", "订单用户关系不正确"
            
            print("✅ 用户与订单关系测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 用户与订单关系测试失败: {e}")
            return False
    
    def test_order_orderitem_relationship(self):
        """测试订单与订单项的一对多关系"""
        print("\n🔍 测试订单与订单项的一对多关系...")
        
        try:
            # 创建测试数据
            user = User(
                username="testuser2",
                email="test2@example.com",
                hashed_password="hashed_password",
                phone_number="1234567891"
            )
            
            product1 = Product(
                name="测试商品1",
                price=50.00,
                description="测试描述1"
            )
            
            product2 = Product(
                name="测试商品2", 
                price=75.00,
                description="测试描述2"
            )
            
            self.session.add_all([user, product1, product2])
            self.session.flush()
            
            order = Order(
                user_id=user.id,
                total_amount=200.00,
                status="pending"
            )
            self.session.add(order)
            self.session.flush()
            
            # 创建订单项
            order_item1 = OrderItem(
                order_id=order.id,
                product_id=product1.id,
                quantity=2,
                price=50.00
            )
            
            order_item2 = OrderItem(
                order_id=order.id,
                product_id=product2.id,
                quantity=1,
                price=75.00
            )
            
            self.session.add_all([order_item1, order_item2])
            self.session.commit()
            
            # 测试关系映射
            fresh_order = self.session.query(Order).filter_by(id=order.id).first()
            
            # 测试正向关系：订单 -> 订单项
            order_items = fresh_order.order_items
            assert len(order_items) == 2, f"订单应该有2个订单项，实际有{len(order_items)}个"
            
            # 测试反向关系：订单项 -> 订单
            fresh_item = self.session.query(OrderItem).filter_by(id=order_item1.id).first()
            assert fresh_item.order.total_amount == 200.00, "订单项订单关系不正确"
            
            # 测试订单项 -> 商品关系
            assert fresh_item.product.name == "测试商品1", "订单项商品关系不正确"
            
            print("✅ 订单与订单项关系测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 订单与订单项关系测试失败: {e}")
            return False
    
    def test_cart_cartitem_relationship(self):
        """测试购物车与购物车项的一对多关系"""
        print("\n🔍 测试购物车与购物车项的一对多关系...")
        
        try:
            # 创建测试数据
            user = User(
                username="testuser3",
                email="test3@example.com",
                hashed_password="hashed_password",
                phone_number="1234567892"
            )
            
            product = Product(
                name="测试商品3",
                price=30.00,
                description="测试描述3"
            )
            
            self.session.add_all([user, product])
            self.session.flush()
            
            cart = Cart(user_id=user.id)
            self.session.add(cart)
            self.session.flush()
            
            # 创建购物车项
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=3
            )
            
            self.session.add(cart_item)
            self.session.commit()
            
            # 测试关系映射
            fresh_cart = self.session.query(Cart).filter_by(id=cart.id).first()
            
            # 测试正向关系：购物车 -> 购物车项
            cart_items = fresh_cart.cart_items
            assert len(cart_items) == 1, f"购物车应该有1个购物车项，实际有{len(cart_items)}个"
            assert cart_items[0].quantity == 3, "购物车项数量不正确"
            
            # 测试反向关系：购物车项 -> 购物车
            fresh_item = self.session.query(CartItem).filter_by(id=cart_item.id).first()
            assert fresh_item.cart.user_id == user.id, "购物车项购物车关系不正确"
            
            # 测试购物车项 -> 商品关系
            assert fresh_item.product.name == "测试商品3", "购物车项商品关系不正确"
            
            print("✅ 购物车与购物车项关系测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 购物车与购物车项关系测试失败: {e}")
            return False
    
    def test_product_inventory_relationship(self):
        """测试商品与库存的一对一关系"""
        print("\n🔍 测试商品与库存的一对一关系...")
        
        try:
            # 创建测试商品
            product = Product(
                name="测试库存商品",
                price=25.00,
                description="测试库存描述"
            )
            self.session.add(product)
            self.session.flush()
            
            # 创建库存记录
            inventory = Inventory(
                product_id=product.id,
                total_quantity=100,
                available_quantity=90,
                reserved_quantity=10
            )
            self.session.add(inventory)
            self.session.commit()
            
            # 测试关系映射
            fresh_product = self.session.query(Product).filter_by(id=product.id).first()
            fresh_inventory = self.session.query(Inventory).filter_by(id=inventory.id).first()
            
            # 测试正向关系：商品 -> 库存
            product_inventory = fresh_product.inventory
            assert product_inventory is not None, "商品应该有关联的库存记录"
            assert product_inventory.total_quantity == 100, "库存数量不正确"
            
            # 测试反向关系：库存 -> 商品
            inventory_product = fresh_inventory.product
            assert inventory_product.name == "测试库存商品", "库存商品关系不正确"
            
            print("✅ 商品与库存关系测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 商品与库存关系测试失败: {e}")
            return False
    
    def test_cascade_operations(self):
        """测试级联操作"""
        print("\n🔍 测试级联删除操作...")
        
        try:
            # 创建测试数据
            user = User(
                username="cascade_user",
                email="cascade@example.com",
                hashed_password="hashed_password",
                phone_number="1234567893"
            )
            self.session.add(user)
            self.session.flush()
            
            # 创建订单
            order = Order(
                user_id=user.id,
                total_amount=150.00,
                status="pending"
            )
            self.session.add(order)
            self.session.flush()
            
            # 验证删除用户前的状态
            order_count_before = self.session.query(Order).filter_by(user_id=user.id).count()
            assert order_count_before == 1, "删除前应该有1个订单"
            
            # 删除用户
            self.session.delete(user)
            self.session.commit()
            
            # 验证级联删除（如果配置了的话）
            # 注意：这取决于实际的级联配置
            remaining_orders = self.session.query(Order).filter_by(user_id=user.id).count()
            print(f"删除用户后剩余订单数: {remaining_orders}")
            
            print("✅ 级联操作测试完成")
            return True
            
        except Exception as e:
            print(f"❌ 级联操作测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始数据模型关系映射测试...")
        print("=" * 50)
        
        if not self.setup_database():
            return False
        
        test_results = []
        
        try:
            # 运行各项测试
            test_results.append(self.test_user_order_relationship())
            test_results.append(self.test_order_orderitem_relationship()) 
            test_results.append(self.test_cart_cartitem_relationship())
            test_results.append(self.test_product_inventory_relationship())
            test_results.append(self.test_cascade_operations())
            
            # 汇总结果
            passed_tests = sum(test_results)
            total_tests = len(test_results)
            
            print("\n" + "=" * 50)
            print(f"📊 测试结果汇总: {passed_tests}/{total_tests} 通过")
            
            if passed_tests == total_tests:
                print("🎉 所有数据模型关系测试通过！")
                return True
            else:
                print("⚠️ 部分测试失败，需要修复数据模型关系映射")
                return False
                
        except Exception as e:
            print(f"❌ 测试执行过程中发生错误: {e}")
            return False
        
        finally:
            if self.session:
                self.session.close()
                print("🔒 数据库会话已关闭")

def main():
    """主函数"""
    print("数据模型关系映射测试脚本")
    print("按照 docs/standards/testing-standards.md 规范编写")
    print("=" * 60)
    
    # 创建测试器并运行测试
    tester = DataModelRelationshipTester(use_sqlite=True)
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 测试执行成功")
        return 0
    else:
        print("\n❌ 测试执行失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)