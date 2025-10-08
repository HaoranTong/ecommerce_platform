<!--version info: v2.0.0, updated: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,../../PROJECT-FOUNDATION.md-->

# 数据库设计规范 (Database Standards)

## 概述

本文档定义数据库设计、ORM使用和数据迁移的具体标准，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- **[命名规范标准](naming-conventions-standards.md)** - 数据库表名命名（模块+复数形式）、字段名命名（主键外键时间戳规则）、索引命名标准（idx_前缀规则）
- **[项目基础定义](../../PROJECT-FOUNDATION.md)** - 数据库配置位置（alembic/目录管理）、模块数据边界（业务模块数据独立性）、迁移文件组织标准

## 具体标准
⬆️ **模块命名映射**: 参见 [PROJECT-FOUNDATION.md](../../PROJECT-FOUNDATION.md#业务模块标准结构-垂直切片)

## 📋 文档说明

本文档定义数据库设计、ORM规范、迁移管理等技术实施标准，基于L1核心标准制定具体的数据库开发规范。

### 🎯 文档职责
- **数据建模标准**: 表设计、字段类型、约束定义、关系映射规范
- **ORM实践规范**: SQLAlchemy模型定义、Session管理、查询优化
- **数据库运维标准**: 迁移管理、索引策略、性能优化方案


## 🎯 数据库设计原则

### 主键设计标准

#### 业务实体表主键设计
- **统一标准**：所有业务实体表主键使用 `id` (INTEGER AUTO_INCREMENT)
- **兼容性原则**：确保SQLite、PostgreSQL、MySQL等数据库的一致性行为
- **扩展策略**：超大规模数据采用分库分表，而非单表大主键策略
- **⚠️ 重要限制**：禁止使用 BIGINT 作为主键，维护统一性和兼容性

#### 关联表（多对多中间表）主键设计

**适用场景**：多对多关系的中间表（如user_roles, role_permissions, product_tags等）

**推荐方式：联合主键**（✅ 优先采用）
```python
class UserRole(Base):
    """用户角色关联表 - 使用联合主键"""
    __tablename__ = "user_roles"
    
    # 联合主键：两个外键字段共同组成主键
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    
    # 其他关联信息字段
    assigned_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime, server_default=func.now())
```

**优势**：
- ✅ **天然唯一性**：联合主键自动保证(user_id, role_id)组合唯一
- ✅ **节省空间**：无需额外的自增id字段
- ✅ **语义清晰**：主键即业务关系，自然主键
- ✅ **符合规范**：SQLAlchemy和数据库设计最佳实践
- ✅ **查询高效**：主键索引直接支持关联查询

**可选方式：独立id主键** (⚠️ 特殊场景使用)
```python
class UserRole(Base):
    """用户角色关联表 - 使用独立id（不推荐）"""
    __tablename__ = "user_roles"
    
    # 独立自增主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    
    # 必须添加唯一约束保证业务逻辑
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
    )
```

**使用场景**：
- ⚠️ 需要在关联表上建立进一步的关联关系（极少见）
- ⚠️ ORM框架对联合主键支持不佳（SQLAlchemy支持良好，无此问题）

**劣势**：
- ❌ 额外存储开销（多一个id字段）
- ❌ 需要额外唯一约束保证业务唯一性
- ❌ 人工主键，语义不如自然主键清晰

**设计原则**：
1. ✅ **关联表优先使用联合主键**（默认选择）
2. ⚠️ **仅在特殊业务需求时使用独立id**（需要文档说明理由）
3. ✅ **两个外键字段必须建立索引**（联合主键自动建立）

### 外键约束设计
- **引用完整性**：必须定义外键约束确保数据一致性
- **级联操作**：合理设置 ON DELETE 和 ON UPDATE 行为
- **索引要求**：所有外键字段必须创建索引提升查询性能

### 软删除设计规范
- **统一字段**：使用 `deleted_at` (TIMESTAMP NULL)
- **删除标记**：NULL 表示未删除，时间戳表示删除时间
- **查询过滤**：应用层查询需要主动过滤已删除记录

## 数据类型标准

### 字符串类型
- 短文本：`VARCHAR(255)`
- 长文本：`TEXT`
- 固定长度：`CHAR(n)`

### 数值类型  
- **整数**：`INT`, `INTEGER` (主键使用INTEGER确保跨数据库兼容性)
- **大整数**：`BIGINT` (仅在确需超过21亿记录的特殊场景使用)
- **金额**：`DECIMAL(10,2)`
- **百分比**：`DECIMAL(5,2)`

### 时间类型
- 时间戳：`TIMESTAMP` (默认值 CURRENT_TIMESTAMP)
- 日期：`DATE`
- 时间：`TIME`

## 🔍 索引设计规范

### 索引创建原则
- **外键强制**：所有外键字段必须创建索引
- **查询优化**：经常用于WHERE、ORDER BY、JOIN的字段需要索引
- **复合索引设计**：按字段选择性从高到低排序
- **覆盖索引应用**：对于频繁查询可考虑覆盖索引减少回表操作

### 性能优化指导
```sql
-- 复合索引字段顺序设计原则
-- 1. 等值查询字段在前
-- 2. 范围查询字段在后
-- 3. 选择性高的字段在前

-- 示例：订单查询索引设计
CREATE INDEX idx_orders_user_status_created ON orders (user_id, status, created_at);
-- 支持查询：WHERE user_id = ? AND status = ? ORDER BY created_at
```

### 索引维护策略
- **监控索引使用率**：定期检查未使用的索引并清理
- **重复索引检测**：避免功能重复的索引浪费存储空间
- **大表索引重建**：定期重建大表索引保持性能

## 🏗️ SQLAlchemy ORM 规范

### Base类统一管理
```python
# 所有模型必须继承统一的Base类
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'
    # 模型定义...
```

**导入规范**: 遵循命名规范标准中的导入命名约定和项目结构标准中的模块组织

### 模型定义标准模板
```python
from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from app.core.database import Base

class User(Base):
    """用户模型
    
    业务说明：用户认证和基本信息管理
    表设计：users表，主键id，包含标准时间戳字段
    """
    __tablename__ = 'users'
    
    # 主键设计 (统一使用INTEGER)
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    
    # 业务字段设计
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(255), unique=True, nullable=False, index=True, comment="邮箱")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    
    # 标准时间戳字段 (强制要求)
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="软删除时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

### 关系定义和外键约束
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Order(Base):
    """订单模型 - 展示外键关系定义标准"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), 
                     nullable=False, index=True, comment="用户ID外键")
    
    # 关系定义：使用back_populates建立双向关系
    user = relationship("User", back_populates="orders", 
                       doc="关联用户，支持order.user访问")

class User(Base):
    # ... 其他字段定义
    
    # 反向关系定义
    orders = relationship("Order", back_populates="user", 
                         cascade="all, delete-orphan",
                         doc="用户的所有订单，支持user.orders访问")
```

### 模块化数据库架构

**📁 模型文件组织结构**:
```tree
app/
├── core/
│   ├── database.py              # 统一Base类和数据库配置
│   └── __init__.py
├── modules/
│   ├── user_auth/
│   │   ├── models.py            # 用户认证模型（User, UserProfile）
│   │   └── __init__.py
│   ├── product_catalog/
│   │   ├── models.py            # 商品管理模型（Product, Category）
│   │   └── __init__.py
│   ├── order_management/
│   │   ├── models.py            # 订单模型（Order, OrderItem）
│   │   └── __init__.py
│   └── ...                     # 其他19个业务模块
└── shared/
    ├── base_models.py           # 公共基础模型（如果需要）
    └── __init__.py
```

**🔗 SQLAlchemy关系映射**:
```python
# app/modules/order_management/models.py - 订单模型定义
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # 关系定义：使用字符串引用避免循环导入
    user = relationship("User", foreign_keys=[user_id])
    # 如果需要反向关系，在User模型中定义orders关系
```

## 🔄 Session管理和事务控制

### FastAPI依赖注入模式 (标准)
```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db

async def create_user_endpoint(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db)
):
    """标准的API端点数据库操作模式"""
    try:
        # 创建模型实例
        user = User(**user_data.dict())
        
        # 数据库操作
        db.add(user)
        db.commit()
        db.refresh(user)  # 获取数据库生成的字段（如id, created_at）
        
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="数据库操作失败")
```

### 查询优化和唯一性验证
```python
# =================================================================
# 高效的唯一性验证查询 - 单次查询检查多个字段
# =================================================================
from sqlalchemy import or_
from sqlalchemy.orm import Session

def validate_user_uniqueness(db: Session, user_data):
    """验证用户数据的唯一性约束
    
    使用单次查询检查用户名和邮箱的唯一性，
    提高性能并减少数据库往返次数。
    """
    existing_user = db.query(User).filter(
        or_(
            User.username == user_data.username,
            User.email == user_data.email
        )
    ).first()
    
    if existing_user:
        # 精确识别冲突字段，提供具体错误信息
        if existing_user.username == user_data.username:
            raise ValueError("用户名已存在")
        else:
            raise ValueError("邮箱已被注册")
    
    return True  # 验证通过

# 性能优化：使用exists()进行存在性检查
def check_username_exists(db: Session, username: str) -> bool:
    """高性能的用户名存在性检查"""
    return db.query(
        db.query(User).filter(User.username == username).exists()
    ).scalar()
```

### 事务管理最佳实践
```python
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

@contextmanager
def database_transaction(db: Session):
    """数据库事务上下文管理器 - 确保事务安全"""
    try:
        yield db
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

# 使用示例：复杂业务操作
def transfer_inventory(db: Session, from_product: int, to_product: int, quantity: int):
    with database_transaction(db):
        # 减少源商品库存
        source = db.query(Product).filter(Product.id == from_product).first()
        source.stock_quantity -= quantity
        
        # 增加目标商品库存
        target = db.query(Product).filter(Product.id == to_product).first()
        target.stock_quantity += quantity
        
        # 创建库存变动记录
        inventory_log = InventoryLog(...)
        db.add(inventory_log)
```

## 🔄 Alembic数据库迁移规范

### 迁移文件命名和组织
- **文件命名格式**: `{时间戳}_{操作类型}_{简要描述}.py`
- **操作类型标识**: `create`, `alter`, `drop`, `add`, `remove`
- **描述规范**: 使用下划线分隔的英文，简明扼要

```bash
# 迁移文件命名示例
20250923120000_create_users_table.py           # 创建用户表
20250923120100_add_email_index_to_users.py     # 添加邮箱索引
20250923120200_alter_products_add_sku.py       # 产品表添加SKU字段
```

### 迁移内容编写标准
```python
"""create users table

Revision ID: abc123
Revises: def456
Create Date: 2025-09-23 12:00:00

业务说明：创建用户认证模块的基础用户表
影响范围：新增users表，包含基础字段和索引
回滚说明：删除users表及相关索引
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # 如果使用PostgreSQL

def upgrade():
    """执行向上迁移：创建表和索引"""
    # 创建表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        comment='用户基础信息表'
    )
    
    # 创建索引
    op.create_index('uk_users_username', 'users', ['username'], unique=True)
    op.create_index('uk_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_active', 'users', ['is_active'])

def downgrade():
    """执行向下迁移：回滚操作"""
    # 删除索引
    op.drop_index('idx_users_active', 'users')
    op.drop_index('uk_users_email', 'users')
    op.drop_index('uk_users_username', 'users')
    
    # 删除表
    op.drop_table('users')
```

### 迁移管理最佳实践
- **单一职责原则**: 每个迁移文件只处理一种类型的变更
- **可回滚设计**: 每个upgrade操作必须有对应的downgrade实现
- **生产环境验证**: 迁移脚本必须在测试环境验证后才能应用到生产

## 📝 完整示例：商品模型设计

### SQLAlchemy模型定义
```python
# app/modules/product_catalog/models.py
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ProductStatus(enum.Enum):
    """商品状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"

class Product(Base):
    """商品模型 - 完整示例
    
    业务说明：商品目录管理的核心模型
    表设计：products表，关联categories表
    特性：包含价格、库存、状态管理
    """
    __tablename__ = 'products'
    
    # 主键设计
    id = Column(Integer, primary_key=True, autoincrement=True, comment="商品ID")
    
    # 基础信息字段
    name = Column(String(255), nullable=False, comment="商品名称")
    description = Column(Text, nullable=True, comment="商品描述")
    sku = Column(String(50), unique=True, nullable=False, index=True, comment="商品SKU")
    
    # 价格和库存
    price = Column(DECIMAL(10, 2), nullable=False, comment="商品价格")
    stock_quantity = Column(Integer, nullable=False, default=0, comment="库存数量")
    
    # 关联和状态
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), 
                        nullable=True, index=True, comment="分类ID")
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE, 
                   nullable=False, index=True, comment="商品状态")
    
    # 标准时间戳
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), 
                       nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="软删除时间")
    
    # 关系定义
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
```

## ❌ 禁止行为和常见错误

### 🚨 严格禁止
1. **主键类型错误**: 禁止使用BIGINT作为主键，必须使用INTEGER
2. **Base类重复定义**: 禁止在模块中重新定义Base类
3. **缺失时间戳字段**: 所有业务表必须包含created_at, updated_at
4. **外键无索引**: 外键字段必须创建索引
5. **循环导入**: 模型导入时避免循环依赖

### ⚠️ 设计反模式
```python
# ❌ 错误的主键定义
id = Column(BigInteger, primary_key=True)  # 禁止使用BigInteger

# ❌ 错误的Base类导入
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()  # 禁止重复定义

# ❌ 缺失必要字段
class BadModel(Base):
    __tablename__ = 'bad_table'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    # ❌ 缺少created_at, updated_at字段

# ❌ 外键字段未加索引  
user_id = Column(Integer, ForeignKey('users.id'))  # ❌ 缺少index=True
```

### ✅ 正确实践对比
```python
# ✅ 正确的模型设计
class GoodModel(Base):
    __tablename__ = 'good_table'
    
    # ✅ 正确的主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # ✅ 正确的外键设计
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # ✅ 必须的时间戳字段
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
```

## 🔄 SQLAlchemy导入和循环依赖规范

### 标准导入模式
```python
# =================================================================
# SQLAlchemy标准导入 - 数据库操作相关
# =================================================================
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy import and_, or_, func, text, select
from sqlalchemy.orm import Session, relationship, selectinload, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# 数据库连接和会话管理
from app.core.database import Base, get_db

# SQLAlchemy特定导入
from sqlalchemy.orm import Session
from sqlalchemy import func
```

### 关系映射循环依赖解决
```python
# 问题场景：User模型和Order模型相互依赖

# ✅ 解决方案1：使用字符串引用 (推荐)
# file: app/modules/user_auth/models.py
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    
    # 使用字符串引用避免导入Order模型
    orders = relationship("Order", back_populates="user")

# file: app/modules/order_management/models.py  
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # 使用字符串引用避免导入User模型
    user = relationship("User", back_populates="orders")

# ✅ 解决方案2：在服务层处理关联查询
def get_user_with_orders(user_id: int, db: Session):
    from app.modules.user_auth.models import User
    from app.modules.order_management.models import Order
    
    return db.query(User).options(
        selectinload(User.orders)
    ).filter(User.id == user_id).first()
```

