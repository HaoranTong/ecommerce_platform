<!--
文档说明：
- 内容：数据库工具模块API接口实现细节，记录数据库脚本和工具的具体实现
- 使用方法：开发人员维护数据库工具时的参考，实现代码的详细记录
- 更新方法：实现代码变更时同步更新，记录实际的工具实现
- 引用关系：基于api-spec.md规范，记录实际脚本实现
- 更新频率：工具代码变更时
-->

# 数据库工具模块API实现

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 实现架构

### 文件结构
```
app/utils/
├── __init__.py
├── db_init.py           # 数据库初始化
├── db_utils.py          # 数据库工具函数
├── test_data.py         # 测试数据管理
├── performance.py       # 性能分析工具
└── validation.py        # 数据验证工具
```

## 数据库初始化实现

### 数据库创建
```python
# app/utils/db_init.py
import mysql.connector
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.base import Base

def create_database():
    """创建数据库"""
    connection = mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    cursor = connection.cursor()
    
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
        print(f"数据库 {settings.DB_NAME} 创建成功")
    except Exception as e:
        print(f"数据库创建失败: {e}")
    finally:
        cursor.close()
        connection.close()

def create_tables():
    """创建所有表"""
    engine = create_engine(settings.DATABASE_URL)
    try:
        Base.metadata.create_all(bind=engine)
        print("所有表创建成功")
    except Exception as e:
        print(f"表创建失败: {e}")
```

### 基础数据初始化
```python
def seed_data():
    """初始化基础数据"""
    from app.database import get_db
    from app.models.user import User
    from app.models.category import Category
    
    db = next(get_db())
    
    # 创建默认分类
    categories = [
        Category(name="五常大米", description="优质五常大米"),
        Category(name="有机蔬菜", description="有机认证蔬菜"),
        Category(name="时令水果", description="新鲜时令水果")
    ]
    
    for category in categories:
        existing = db.query(Category).filter(Category.name == category.name).first()
        if not existing:
            db.add(category)
    
    # 创建管理员用户
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_admin=True
    )
    
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if not existing_admin:
        db.add(admin_user)
    
    db.commit()
    print("基础数据初始化完成")
```

## 测试数据管理实现

### 测试用户创建
```python
# app/utils/test_data.py
from faker import Faker
from app.models.user import User
from app.utils.security import get_password_hash

fake = Faker('zh_CN')

def create_test_users(count: int = 100):
    """创建测试用户"""
    from app.database import get_db
    
    db = next(get_db())
    
    users = []
    for i in range(count):
        user = User(
            username=f"testuser_{i}_{fake.user_name()}",
            email=fake.email(),
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        users.append(user)
    
    db.bulk_save_objects(users)
    db.commit()
    print(f"创建了 {count} 个测试用户")

def create_test_products(count: int = 500):
    """创建测试商品"""
    from app.models.product import Product
    from app.database import get_db
    
    db = next(get_db())
    
    products = []
    for i in range(count):
        product = Product(
            name=f"{fake.word()}大米",
            description=fake.text(max_nb_chars=200),
            price=fake.pydecimal(left_digits=3, right_digits=2, positive=True),
            stock_quantity=fake.random_int(min=0, max=1000),
            category_id=fake.random_int(min=1, max=3)
        )
        products.append(product)
    
    db.bulk_save_objects(products)
    db.commit()
    print(f"创建了 {count} 个测试商品")

def cleanup_test_data():
    """清理测试数据"""
    from app.database import get_db
    
    db = next(get_db())
    
    # 删除测试用户
    db.query(User).filter(User.username.like("testuser_%")).delete()
    
    # 删除测试商品
    db.query(Product).filter(Product.name.like("%测试%")).delete()
    
    db.commit()
    print("测试数据清理完成")
```

## 性能分析工具实现

### 查询性能分析
```python
# app/utils/performance.py
import time
import psutil
from sqlalchemy import text
from app.database import get_db

def analyze_query_performance(query: str):
    """分析查询性能"""
    db = next(get_db())
    
    # 记录开始时间和内存
    start_time = time.time()
    start_memory = psutil.virtual_memory().used
    
    try:
        # 执行查询
        result = db.execute(text(query))
        rows = result.fetchall()
        
        # 记录结束时间和内存
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        return {
            "execution_time": end_time - start_time,
            "memory_used": end_memory - start_memory,
            "rows_returned": len(rows),
            "query": query
        }
    except Exception as e:
        return {
            "error": str(e),
            "query": query
        }

def get_slow_queries():
    """获取慢查询列表"""
    db = next(get_db())
    
    slow_queries = db.execute(text("""
        SELECT query_time, sql_text, rows_examined
        FROM mysql.slow_log
        WHERE query_time > 1
        ORDER BY query_time DESC
        LIMIT 10
    """)).fetchall()
    
    return [
        {
            "query_time": row[0],
            "sql_text": row[1],
            "rows_examined": row[2]
        }
        for row in slow_queries
    ]
```

## 数据验证工具实现

### 数据完整性验证
```python
# app/utils/validation.py
from app.database import get_db
from app.models import User, Product, Order

def validate_data_integrity():
    """验证数据完整性"""
    db = next(get_db())
    issues = []
    
    # 检查孤儿记录
    orphan_orders = db.query(Order).filter(
        ~Order.user_id.in_(db.query(User.id))
    ).count()
    
    if orphan_orders > 0:
        issues.append(f"发现 {orphan_orders} 个孤儿订单记录")
    
    # 检查重复数据
    duplicate_emails = db.query(User.email).group_by(User.email).having(
        func.count(User.email) > 1
    ).count()
    
    if duplicate_emails > 0:
        issues.append(f"发现 {duplicate_emails} 个重复邮箱")
    
    # 检查数据约束
    invalid_prices = db.query(Product).filter(Product.price <= 0).count()
    
    if invalid_prices > 0:
        issues.append(f"发现 {invalid_prices} 个无效价格商品")
    
    return {
        "total_issues": len(issues),
        "issues": issues,
        "validation_time": datetime.utcnow()
    }

def fix_data_issues():
    """修复数据问题"""
    db = next(get_db())
    
    # 删除孤儿订单
    orphan_orders = db.query(Order).filter(
        ~Order.user_id.in_(db.query(User.id))
    )
    orphan_count = orphan_orders.count()
    orphan_orders.delete()
    
    # 修复无效价格
    invalid_products = db.query(Product).filter(Product.price <= 0)
    invalid_count = invalid_products.count()
    invalid_products.update({"price": 1.00})
    
    db.commit()
    
    return f"修复了 {orphan_count} 个孤儿订单和 {invalid_count} 个无效价格"
```

## 命令行接口实现

### CLI命令注册
```python
# app/utils/cli.py
import click
from app.utils.db_init import create_database, create_tables, seed_data
from app.utils.test_data import create_test_users, create_test_products, cleanup_test_data

@click.group()
def cli():
    """数据库工具命令行界面"""
    pass

@cli.command()
def init_db():
    """初始化数据库"""
    create_database()
    create_tables()
    seed_data()

@cli.command()
@click.option('--count', default=100, help='创建用户数量')
def create_users(count):
    """创建测试用户"""
    create_test_users(count)

@cli.command()
@click.option('--count', default=500, help='创建商品数量')
def create_products(count):
    """创建测试商品"""
    create_test_products(count)

@cli.command()
def cleanup():
    """清理测试数据"""
    cleanup_test_data()

if __name__ == '__main__':
    cli()
```