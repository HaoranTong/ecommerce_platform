# 数据库设计规范

本文档定义数据库表、字段、关系的命名和设计标准。

## 架构引用说明

本文档基于架构设计原则制定具体的技术实施标准：
- **架构设计原则**: 参见 [数据模型架构设计](../architecture/data-models.md) - 获取ORM架构、业务设计原则
- **技术实施标准**: 本文档定义具体的命名约定、编码规范、SQL标准

## 文档层次关系
```
架构设计层: data-models.md (设计原则)
     ↓ 指导
技术标准层: database-standards.md (本文档 - 实施规范)
     ↓ 指导  
具体实现层: modules/data-models/overview.md (技术实现)
```

---

## 表命名规范

### 基础规则
- 使用复数形式：`users`, `products`, `orders`
- 小写字母+下划线：`order_items`, `user_profiles`
- 避免缩写，使用完整单词

### 关联表命名
- 多对多关系：`user_roles`, `product_categories`
- 中间表：按字母顺序排列实体名

## 字段命名规范

### 主键字段
- **统一标准**：`id` (INTEGER AUTO_INCREMENT)
- **类型说明**：INTEGER，支持21亿记录，满足大多数业务场景需求
- **兼容性考虑**：确保在SQLite、PostgreSQL、MySQL等数据库中的一致性行为
- **扩展策略**：超大规模数据采用分库分表，而非单表大主键策略

### 外键字段  
- 格式：`{表名}_id`
- 示例：`user_id`, `product_id`, `order_id`

### 通用字段
- 创建时间：`created_at` (TIMESTAMP)
- 更新时间：`updated_at` (TIMESTAMP)  
- 软删除：`deleted_at` (TIMESTAMP NULL)
- 状态字段：`status` (VARCHAR 或 ENUM)

### 业务字段
- 数量字段：`quantity`, `amount`
- 金额字段：`price`, `total_amount` (DECIMAL)
- 描述字段：`description`, `note`
- 名称字段：`name`, `title`

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

## 索引规范

### 命名规则
- 主键：`PRIMARY`
- 唯一索引：`uk_{表名}_{字段名}` 
- 普通索引：`idx_{表名}_{字段名}` 或 `idx_{表名}_{字段1}_{字段2}`
- 外键索引：`fk_{表名}_{外键字段名}`
- 复合索引：`idx_{表名}_{字段1}_{字段2}_{字段3}`

### 索引命名示例
```sql
-- 唯一索引
uk_users_email          -- users表的email唯一索引
uk_products_sku         -- products表的sku唯一索引

-- 普通索引  
idx_orders_user_id      -- orders表的user_id索引
idx_orders_status       -- orders表的status索引
idx_orders_user_status  -- orders表的user_id+status复合索引
idx_payments_status_created -- payments表的status+created_at复合索引

-- 外键索引
fk_orders_user_id       -- orders表指向users表的外键索引
fk_order_items_product_id -- order_items表指向products表的外键索引
```

### 创建原则
- 外键字段必须有索引
- 经常查询的字段添加索引
- 联合索引按选择性排序

## SQLAlchemy ORM 编写规范

### Base类导入规范
```python
# ✅ 正确的导入方式 - 统一从技术基础设施层导入
from app.core.database import Base

# ❌ 禁止的导入方式
from app.shared.models import Base  # 禁止
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()  # 禁止重复定义
```

### 模型定义规范
```python
# 标准模型定义模板
from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, func
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'  # 必须定义表名
    
    # 主键字段 (使用BigInteger)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 业务字段
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳字段 (必须包含)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
```

### 关系定义规范
```python
# 外键关系定义
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    
    # 关系定义
    user = relationship("User", back_populates="orders")
```

### 模块化项目数据库组织规范

#### 文件组织结构
```
app/
├── core/
│   └── database.py          # 统一Base类定义和数据库配置
├── modules/
│   ├── user_auth/
│   │   └── models.py        # 用户认证相关模型
│   ├── product_catalog/
│   │   └── models.py        # 商品管理相关模型
│   └── order_management/
│       └── models.py        # 订单管理相关模型
```

#### 跨模块引用规范
```python
# 当需要引用其他模块的模型时
# app/modules/order_management/models.py
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Product

class Order(Base):
    __tablename__ = 'orders'
    user_id = Column(BigInteger, ForeignKey('users.id'))
    # 关系定义中直接使用字符串引用
    user = relationship("User")  # 字符串引用，避免循环导入
```

## Session管理规范

### 依赖注入方式 (推荐)
```python
# 在API端点中使用
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

def create_user(user_data: dict, db: Session = Depends(get_db)):
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### 事务处理规范
```python
# 简单事务
def transfer_operation(db: Session):
    try:
        # 多个数据库操作
        db.add(object1)
        db.add(object2)
        db.commit()
    except Exception:
        db.rollback()
        raise

# 复杂事务使用上下文管理器
from contextlib import contextmanager

@contextmanager
def db_transaction(db: Session):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
```

## 迁移文件规范

### 文件命名
- 格式：`{时间戳}_{操作描述}.py`
- 操作描述使用下划线分隔的英文

### 迁移内容
- 每个迁移文件只做一类操作
- 提供 upgrade 和 downgrade 方法
- 添加详细的注释说明

## 示例

### 标准表结构
```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    category_id BIGINT,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);
```

## 禁止行为

- 使用中文字段名
- 不加索引的外键字段
- 不一致的命名模式
- 缺少时间戳字段