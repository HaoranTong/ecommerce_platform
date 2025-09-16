# 数据库工具模块 (Database Utils Module)

## 模块概述

数据库工具模块 (`app/db.py`) 是电商平台的数据库操作辅助组件，提供简化的数据库连接管理、会话工具函数和模型基类导出，主要用于测试环境、脚本工具和Alembic迁移。

### 主要功能

1. **简化连接管理**
   - 环境变量优先级配置
   - 多环境数据库URL支持
   - SQLAlchemy引擎创建
   - 会话工厂配置

2. **工具函数**
   - 上下文管理器式会话
   - 资源自动清理
   - 异常安全处理
   - 测试友好接口

3. **模型导出**
   - Base类重新导出
   - Alembic迁移支持
   - 测试模块便利导入
   - 模型元数据访问

4. **配置管理**
   - 多层级环境变量
   - 开发环境默认配置
   - 生产环境兼容性
   - 灵活的连接字符串

## 技术架构

### 模块关系图

```mermaid
graph TB
    A[app.db] --> B[database.py]
    A --> C[models.py]
    A --> D[Environment Variables]
    
    B --> E[SQLAlchemy Engine]
    B --> F[Session Factory]
    C --> G[Base Model Class]
    D --> H[DATABASE_URL]
    D --> I[ALEMBIC_DSN]
    
    J[Tests] --> A
    K[Alembic] --> A
    L[Scripts] --> A
    M[CLI Tools] --> A
```

### 配置优先级

```mermaid
graph LR
    A[DATABASE_URL] --> B{存在?}
    B -->|是| C[使用DATABASE_URL]
    B -->|否| D[ALEMBIC_DSN]
    D --> E{存在?}
    E -->|是| F[使用ALEMBIC_DSN]
    E -->|否| G[使用默认配置]
    
    C --> H[连接数据库]
    F --> H
    G --> H
```

## 代码结构

### 文件组织

```
app/db.py
├── 导入依赖
├── 环境变量配置
├── 引擎和会话创建
├── 工具函数定义
└── 模型基类导出
```

### 关键组件说明

#### 1. 环境变量配置

```python
DATABASE_URL = (
    os.environ.get('DATABASE_URL') or          # 优先级1: 标准环境变量
    os.environ.get('ALEMBIC_DSN') or           # 优先级2: Alembic专用
    'mysql+pymysql://root:rootpass@localhost:3307/dev_vision'  # 优先级3: 默认配置
)
```

**优先级说明:**
1. `DATABASE_URL`: 标准数据库连接环境变量
2. `ALEMBIC_DSN`: Alembic迁移工具专用变量
3. 默认配置: 开发环境fallback配置

#### 2. 引擎配置

```python
engine = create_engine(
    DATABASE_URL,
    echo=False,      # 禁用SQL日志 (性能考虑)
    future=True      # 启用SQLAlchemy 2.0特性
)
```

**配置特点:**
- `future=True`: 使用SQLAlchemy 2.0 API
- `echo=False`: 生产环境友好的日志设置
- 简化配置，专注工具用途

#### 3. 会话工厂

```python
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,  # 手动控制刷新
    autocommit=False, # 手动控制提交
    future=True       # 2.0 API兼容
)
```

**会话特性:**
- 手动事务控制
- 2.0 API兼容性
- 工具友好配置

#### 4. 工具函数

```python
def get_session():
    """Yield a SQLAlchemy session (context manager style)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**设计模式:**
- 生成器模式
- 上下文管理器兼容
- 资源自动清理
- 异常安全

## API接口

### 核心函数

| 函数名 | 参数 | 返回值 | 用途 |
|--------|------|--------|------|
| `get_session` | 无 | `Generator[Session]` | 获取数据库会话 (生成器) |

### 全局对象

| 对象名 | 类型 | 描述 |
|--------|------|------|
| `engine` | `Engine` | SQLAlchemy数据库引擎 |
| `SessionLocal` | `sessionmaker` | 会话工厂类 |
| `Base` | `DeclarativeMeta` | 模型基类 (重新导出) |

## 使用示例

### 1. 脚本中使用

```python
from app.db import get_session
from app.models import User, Product

def create_test_data():
    """创建测试数据脚本"""
    with get_session() as session:
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        session.add(test_user)
        
        # 创建测试商品
        test_product = Product(
            name="测试商品",
            sku="TEST001",
            price=99.99,
            stock_quantity=100
        )
        session.add(test_product)
        
        # 提交事务
        session.commit()
        
        print(f"创建用户: {test_user.id}")
        print(f"创建商品: {test_product.id}")

if __name__ == "__main__":
    create_test_data()
```

### 2. 数据迁移脚本

```python
from app.db import get_session
from app.models import Product

def migrate_product_data():
    """数据迁移示例"""
    with get_session() as session:
        # 批量更新商品状态
        updated = session.query(Product)\
            .filter(Product.stock_quantity == 0)\
            .update({"status": "out_of_stock"})
        
        session.commit()
        print(f"更新了 {updated} 个商品的状态")

def cleanup_inactive_products():
    """清理非活跃商品"""
    with get_session() as session:
        # 删除非活跃商品
        deleted = session.query(Product)\
            .filter(Product.status == "inactive")\
            .delete()
        
        session.commit()
        print(f"删除了 {deleted} 个非活跃商品")
```

### 3. 测试辅助函数

```python
from app.db import get_session, Base, engine
from app.models import User

def setup_test_database():
    """设置测试数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def teardown_test_database():
    """清理测试数据库"""
    # 删除所有表
    Base.metadata.drop_all(bind=engine)

def create_test_user() -> User:
    """创建测试用户"""
    with get_session() as session:
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="test_hash"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# pytest示例
def test_user_creation():
    """测试用户创建"""
    user = create_test_user()
    assert user.id is not None
    assert user.username == "testuser"
```

### 4. 批量操作工具

```python
from app.db import get_session
from app.models import Product

def bulk_update_prices(price_adjustments: dict):
    """批量更新商品价格"""
    with get_session() as session:
        for product_id, new_price in price_adjustments.items():
            session.query(Product)\
                .filter(Product.id == product_id)\
                .update({"price": new_price})
        
        session.commit()
        print(f"更新了 {len(price_adjustments)} 个商品的价格")

def export_products_to_csv(filename: str):
    """导出商品数据到CSV"""
    import csv
    
    with get_session() as session:
        products = session.query(Product).all()
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', '名称', 'SKU', '价格', '库存'])
            
            for product in products:
                writer.writerow([
                    product.id,
                    product.name,
                    product.sku,
                    product.price,
                    product.stock_quantity
                ])
        
        print(f"导出 {len(products)} 个商品到 {filename}")
```

## 配置说明

### 环境变量

| 变量名 | 优先级 | 描述 | 示例 |
|--------|--------|------|------|
| `DATABASE_URL` | 1 | 标准数据库连接字符串 | `mysql+pymysql://user:pass@host:port/db` |
| `ALEMBIC_DSN` | 2 | Alembic专用连接字符串 | `mysql+pymysql://user:pass@host:port/db` |
| 默认配置 | 3 | Fallback开发配置 | `mysql+pymysql://root:rootpass@localhost:3307/dev_vision` |

### 使用场景

| 环境变量 | 使用场景 | 设置方式 |
|----------|----------|----------|
| `DATABASE_URL` | 生产环境、标准部署 | `export DATABASE_URL="..."` |
| `ALEMBIC_DSN` | 数据库迁移、CI/CD | `export ALEMBIC_DSN="..."` |
| 默认配置 | 本地开发、快速测试 | 无需设置 |

### 环境配置示例

#### 开发环境
```bash
# 使用默认配置 (无需设置)
python script.py
```

#### 测试环境
```bash
export DATABASE_URL="mysql+pymysql://test_user:test_pass@localhost:3306/test_db"
python -m pytest
```

#### 生产环境
```bash
export DATABASE_URL="mysql+pymysql://prod_user:${DB_PASSWORD}@db-server:3306/prod_db"
python migration_script.py
```

#### Alembic迁移
```bash
export ALEMBIC_DSN="mysql+pymysql://migration_user:migration_pass@db:3306/app_db"
alembic upgrade head
```

## 与其他模块的区别

### vs database.py

| 特性 | db.py | database.py |
|------|-------|-------------|
| **用途** | 工具脚本、测试 | FastAPI应用 |
| **会话管理** | 生成器模式 | 依赖注入 |
| **配置** | 多环境变量 | 单一环境变量 |
| **连接池** | 简化配置 | 优化配置 |
| **API集成** | 不适用 | FastAPI兼容 |

### 选择指南

```python
# 使用 db.py 的场景
from app.db import get_session

# 1. 脚本工具
def data_migration_script():
    with get_session() as session:
        # 数据迁移逻辑
        pass

# 2. 测试代码
def test_function():
    with get_session() as session:
        # 测试逻辑
        pass

# 使用 database.py 的场景
from app.database import get_db

# FastAPI路由
@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    # API逻辑
    pass
```

## 性能考虑

### 1. 连接复用

```python
# 长时间运行的脚本应该复用连接
from app.db import SessionLocal

def long_running_task():
    """长时间运行任务的连接管理"""
    session = SessionLocal()
    try:
        for i in range(1000):
            # 处理逻辑
            if i % 100 == 0:
                session.commit()  # 定期提交
        
        session.commit()  # 最终提交
    finally:
        session.close()
```

### 2. 批量操作优化

```python
def batch_insert_products(products_data: list):
    """批量插入商品优化"""
    with get_session() as session:
        # 使用bulk_insert_mappings优化
        session.bulk_insert_mappings(Product, products_data)
        session.commit()

def batch_update_with_case(updates: dict):
    """使用CASE语句批量更新"""
    from sqlalchemy import case
    
    with get_session() as session:
        # 构建CASE更新语句
        when_clauses = [
            (Product.id == product_id, new_price)
            for product_id, new_price in updates.items()
        ]
        
        session.query(Product)\
            .filter(Product.id.in_(updates.keys()))\
            .update({
                Product.price: case(when_clauses, else_=Product.price)
            })
        
        session.commit()
```

## 调试和监控

### 1. 启用SQL日志

```python
# 临时启用SQL日志 (调试用)
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 或者修改引擎配置
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, echo=True)
```

### 2. 连接状态检查

```python
def check_database_connection():
    """检查数据库连接状态"""
    try:
        with get_session() as session:
            result = session.execute("SELECT 1").scalar()
            print(f"数据库连接正常: {result}")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

def get_database_info():
    """获取数据库信息"""
    with get_session() as session:
        result = session.execute("""
            SELECT 
                DATABASE() as current_db,
                USER() as current_user,
                VERSION() as version
        """).fetchone()
        
        return {
            "database": result.current_db,
            "user": result.current_user,
            "version": result.version
        }
```

### 3. 性能监控

```python
import time
from contextlib import contextmanager

@contextmanager
def timed_session():
    """带性能监控的会话"""
    start_time = time.time()
    with get_session() as session:
        try:
            yield session
        finally:
            duration = time.time() - start_time
            if duration > 1.0:  # 慢操作警告
                print(f"数据库操作耗时: {duration:.2f}s")
```

## 故障排除

### 常见问题

1. **导入错误**
   ```python
   ImportError: cannot import name 'Base' from 'app.db'
   ```
   **解决方案:** 确保`app.models`正确定义了`Base`

2. **连接字符串错误**
   ```
   sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL
   ```
   **解决方案:** 检查数据库URL格式和特殊字符转义

3. **会话未关闭警告**
   ```
   SAWarning: Session was never rollback/commit
   ```
   **解决方案:** 确保使用`with get_session()`上下文管理器

### 调试技巧

```python
def debug_environment():
    """调试环境配置"""
    import os
    
    print("数据库配置检查:")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    print(f"ALEMBIC_DSN: {os.environ.get('ALEMBIC_DSN', 'Not set')}")
    
    from app.db import engine
    print(f"实际使用URL: {engine.url}")

def test_basic_operations():
    """测试基础数据库操作"""
    try:
        with get_session() as session:
            # 测试查询
            result = session.execute("SELECT 1").scalar()
            print(f"基础查询测试: {result}")
            
            # 测试事务
            session.begin()
            session.rollback()
            print("事务测试: 通过")
            
    except Exception as e:
        print(f"数据库操作测试失败: {e}")
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1.0 | 2025-09-11 | 初始版本，提供基础数据库工具函数 |

## 相关文档

- [数据库连接模块](../database/overview.md)
- [数据模型定义](../models/overview.md)
- [Alembic迁移指南](../../operations/deployment.md#数据库迁移)
- [测试指南](../../development/testing.md#数据库测试)
