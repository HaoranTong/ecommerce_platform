<!--
文档说明：
- 内容：数据模型模块API接口实现细节，记录ORM模型的具体实现和数据库操作
- 使用方法：开发人员实现数据访问层时的参考，代码实现的详细记录
- 更新方法：实现代码变更时同步更新，记录实际的实现方案
- 引用关系：基于api-spec.md规范，记录实际代码实现
- 更新频率：代码实现变更时
-->

# 数据模型模块API实现

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 实现架构

### 文件结构
```
app/
├── core/
│   ├── database.py      # Base类和数据库配置
│   ├── redis_client.py  # Redis缓存客户端
│   └── auth.py          # 认证中间件
├── shared/
│   ├── models.py        # 通用模型混入
│   ├── api_schemas.py   # API响应模式
│   └── base_schemas.py  # 基础Pydantic模式
├── modules/
│   ├── user_auth/
│   │   ├── models.py    # 用户模型
│   │   └── schemas.py   # 用户Schema
│   ├── product_catalog/
│   │   ├── models.py    # 商品模型
│   │   └── schemas.py   # 商品Schema
│   └── order_management/
│       ├── models.py    # 订单模型
│       └── schemas.py   # 订单Schema
```

## 核心模型实现

### 基础模型类
```python
# app/core/database.py
from sqlalchemy import Column, BigInteger, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

Base = declarative_base()

DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:rootpass@localhost:3307/ecommerce_platform')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/shared/models.py
from app.core.database import Base
from sqlalchemy import Column, BigInteger, DateTime, func

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

### 用户模型实现
```python
# app/modules/user_auth/models.py
from sqlalchemy import Column, String, Boolean, BigInteger
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
```

### 商品模型实现
```python
# app/modules/product_catalog/models.py
from sqlalchemy import Column, String, Text, DECIMAL, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    category_id = Column(BigInteger, ForeignKey("categories.id"))
    
    # 关联关系
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
```

## Schema实现

### 用户Schema
```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 数据库操作实现

### 用户CRUD操作
```python
# app/crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
```

## 性能优化实现

### 索引策略
```python
# 复合索引
Index('idx_user_email_active', User.email, User.is_active)
Index('idx_product_category_price', Product.category_id, Product.price)

# 查询优化
def get_products_with_category(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).options(
        joinedload(Product.category)
    ).offset(skip).limit(limit).all()
```

### 缓存策略
```python
# Redis缓存装饰器
from functools import wraps
import redis

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 迁移脚本

### Alembic配置
```python
# alembic/versions/001_initial_migration.py
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
```

## 测试实现

### 模型测试
```python
# tests/test_models.py
def test_create_user():
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_user_relationships():
    user = User(username="testuser", email="test@example.com")
    order = Order(user_id=user.id, total_amount=100.00)
    assert order.user == user
```