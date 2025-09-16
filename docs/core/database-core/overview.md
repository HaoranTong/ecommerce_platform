# 数据库连接模块 (Database Connection Module)

## 模块概述

数据库连接模块 (`app/database.py`) 是电商平台的数据持久化核心组件，负责SQLAlchemy数据库引擎配置、连接池管理、会话生命周期控制和数据库表操作。

### 主要功能

1. **数据库连接管理**
   - SQLAlchemy引擎配置
   - 连接池参数优化
   - 连接健康检查
   - 自动连接回收

2. **会话管理**
   - 数据库会话工厂
   - 依赖注入支持
   - 自动事务管理
   - 资源自动释放

3. **表结构管理**
   - 数据库表创建
   - 表结构同步
   - 开发环境表重建
   - 模型元数据管理

4. **配置管理**
   - 环境变量驱动配置
   - 多环境支持
   - 默认配置提供
   - 安全配置实践

## 技术架构

### 核心组件

```mermaid
graph TB
    A[Database Module] --> B[SQLAlchemy Engine]
    A --> C[Session Factory]
    A --> D[Base Model Class]
    A --> E[Connection Pool]
    
    B --> F[MySQL Connection]
    C --> G[Database Sessions]
    D --> H[Model Metadata]
    E --> I[Connection Management]
    
    F --> J[(MySQL Database)]
    G --> K[FastAPI Dependencies]
    H --> L[Table Creation]
    I --> M[Resource Optimization]
```

### 连接池架构

```mermaid
graph LR
    A[Application] --> B[Session Factory]
    B --> C[Connection Pool]
    C --> D[Connection 1]
    C --> E[Connection 2]
    C --> F[Connection N]
    
    D --> G[(Database)]
    E --> G
    F --> G
    
    H[Health Check] --> C
    I[Auto Recycle] --> C
```

## 代码结构

### 文件组织

```
app/database.py
├── 环境配置
├── 引擎创建
├── 会话工厂
├── 基类定义
├── 依赖函数
└── 表管理函数
```

### 关键组件说明

#### 1. 数据库引擎配置

```python
engine = create_engine(
    DATABASE_URL,
    echo=False,              # SQL日志控制
    pool_size=10,            # 连接池大小
    max_overflow=20,         # 最大溢出连接
    pool_recycle=3600,       # 连接回收时间(秒)
    pool_pre_ping=True       # 连接健康检查
)
```

**配置参数说明:**
- `pool_size=10`: 常驻连接池大小，适合中等负载
- `max_overflow=20`: 临时连接数，处理流量峰值
- `pool_recycle=3600`: 1小时回收，避免连接超时
- `pool_pre_ping=True`: 使用前检查，确保连接有效

#### 2. 会话工厂

```python
SessionLocal = sessionmaker(
    autocommit=False,    # 禁用自动提交，手动控制事务
    autoflush=False,     # 禁用自动刷新，优化性能
    bind=engine          # 绑定数据库引擎
)
```

**配置特性:**
- 手动事务控制，确保数据一致性
- 性能优化配置，减少不必要的数据库操作
- 引擎绑定，统一连接管理

#### 3. 依赖注入函数

```python
def get_db():
    """获取数据库会话依赖
    
    用于FastAPI的依赖注入系统
    自动管理会话生命周期
    """
    db = SessionLocal()
    try:
        yield db    # 生成器模式，支持依赖注入
    finally:
        db.close()  # 确保资源释放
```

**功能特性:**
- FastAPI依赖注入兼容
- 自动资源管理
- 异常安全的会话关闭

## 配置说明

### 环境变量

| 变量名 | 默认值 | 描述 | 示例 |
|--------|--------|------|------|
| `DATABASE_URL` | `mysql+pymysql://root:123456@localhost:3307/ecommerce_platform` | 数据库连接字符串 | `mysql+pymysql://user:pass@host:port/db` |

### 连接字符串格式

```
mysql+pymysql://[username]:[password]@[host]:[port]/[database]
```

**组成部分:**
- `mysql+pymysql`: 数据库驱动 (MySQL + PyMySQL)
- `username`: 数据库用户名
- `password`: 数据库密码  
- `host`: 数据库主机地址
- `port`: 数据库端口号
- `database`: 数据库名称

### 环境配置示例

#### 开发环境
```bash
export DATABASE_URL="mysql+pymysql://dev_user:dev_pass@localhost:3306/ecommerce_dev"
```

#### 测试环境
```bash
export DATABASE_URL="mysql+pymysql://test_user:test_pass@test-db:3306/ecommerce_test"
```

#### 生产环境
```bash
export DATABASE_URL="mysql+pymysql://prod_user:${DB_PASSWORD}@prod-db:3306/ecommerce_prod"
```

## API接口

### 核心函数

#### get_db()
**功能**: 获取数据库会话依赖  
**用途**: FastAPI路由中的依赖注入  
**返回**: SQLAlchemy Session对象  

```python
from fastapi import Depends
from app.database import get_db

@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

#### create_tables()
**功能**: 创建所有数据库表  
**用途**: 应用初始化、数据库迁移  
**注意**: 生产环境建议使用Alembic迁移  

```python
from app.database import create_tables
create_tables()  # 创建所有表
```

#### drop_tables()
**功能**: 删除所有数据库表  
**用途**: 开发测试环境重置  
**警告**: 仅用于开发，会丢失所有数据  

```python
from app.database import drop_tables
drop_tables()  # 删除所有表 (谨慎使用)
```

## 使用示例

### 1. FastAPI路由中使用

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    db_user = User(**user_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

### 2. 手动会话管理

```python
from app.database import SessionLocal
from app.models import Product

# 手动会话管理 (不推荐在FastAPI中使用)
def update_product_stock():
    session = SessionLocal()
    try:
        product = session.query(Product).filter(Product.id == 1).first()
        product.stock_quantity -= 1
        session.commit()
    finally:
        session.close()
```

### 3. 数据库初始化

```python
from app.database import create_tables, engine
from app.models import Base

# 应用启动时创建表
def initialize_database():
    """初始化数据库表结构"""
    # 方式1: 使用内置函数
    create_tables()
    
    # 方式2: 直接使用SQLAlchemy
    Base.metadata.create_all(bind=engine)
```

## 性能优化

### 连接池优化

1. **合理设置池大小**
   ```python
   # 根据并发需求调整
   pool_size=20,        # 高并发场景
   max_overflow=30,     # 流量峰值处理
   ```

2. **连接回收策略**
   ```python
   pool_recycle=1800,   # 30分钟回收 (MySQL默认超时8小时)
   pool_pre_ping=True,  # 连接健康检查
   ```

### 会话优化

1. **批量操作**
   ```python
   # 批量插入优化
   db.bulk_insert_mappings(User, user_data_list)
   db.commit()
   ```

2. **查询优化**
   ```python
   # 使用索引和合适的查询
   users = db.query(User).filter(User.email.in_(email_list)).all()
   ```

## 监控和调试

### 启用SQL日志

```python
# 开发环境启用SQL日志
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 输出所有SQL语句
    # echo="debug"  # 更详细的调试信息
)
```

### 连接池监控

```python
# 检查连接池状态
pool = engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked in: {pool.checkedin()}")
print(f"Checked out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

### 性能监控指标

推荐监控指标：
- 连接池使用率
- 平均查询时间
- 连接建立失败率
- 事务回滚率

## 安全考虑

### 1. 连接字符串安全

```python
# 推荐: 使用环境变量
DATABASE_URL = os.getenv("DATABASE_URL")

# 避免: 硬编码密码
# DATABASE_URL = "mysql://user:password@host/db"  # 不安全
```

### 2. 权限最小化

```sql
-- 应用用户权限 (最小权限原则)
GRANT SELECT, INSERT, UPDATE, DELETE ON ecommerce_platform.* TO 'app_user'@'%';

-- 避免使用root用户连接
```

### 3. 连接加密

```python
# 生产环境使用SSL连接
DATABASE_URL = "mysql+pymysql://user:pass@host/db?ssl_disabled=false"
```

## 故障排除

### 常见问题

1. **连接超时**
   ```
   sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 20 reached
   ```
   **解决**: 增加连接池大小或检查连接泄漏

2. **连接被拒绝**
   ```
   pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
   ```
   **解决**: 检查数据库服务状态和网络连通性

3. **权限错误**
   ```
   pymysql.err.OperationalError: (1045, "Access denied for user")
   ```
   **解决**: 验证用户名密码和数据库权限

### 调试方法

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig()
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

2. **测试连接**
   ```python
   from app.database import engine
   try:
       conn = engine.connect()
       result = conn.execute("SELECT 1")
       print("数据库连接正常")
       conn.close()
   except Exception as e:
       print(f"连接失败: {e}")
   ```

3. **检查配置**
   ```python
   from app.database import DATABASE_URL
   print(f"当前数据库URL: {DATABASE_URL}")
   ```

## 部署考虑

### 开发环境

```bash
# 使用本地MySQL
export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/ecommerce_dev"
```

### 容器环境

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - DATABASE_URL=mysql+pymysql://app_user:app_pass@db:3306/ecommerce
  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=ecommerce
      - MYSQL_USER=app_user
      - MYSQL_PASSWORD=app_pass
      - MYSQL_ROOT_PASSWORD=root_pass
```

### 生产环境

```bash
# 使用外部数据库服务
export DATABASE_URL="mysql+pymysql://user:${DB_PASSWORD}@rds-endpoint:3306/ecommerce"
```

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 0.1.0 | 2025-09-11 | 初始版本，基础数据库连接实现 |

## 相关文档

- [数据模型定义](../models/overview.md)
- [数据库迁移指南](../../operations/deployment.md#数据库迁移)
- [Alembic使用文档](../../development/tools.md#alembic)
- [SQLAlchemy官方文档](https://docs.sqlalchemy.org/)
