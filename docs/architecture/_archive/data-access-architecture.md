# SQLAlchemy数据访问架构设计

## 核心设计原则

### 1. 统一Base类管理
- **单一数据源**: 所有模型必须从 `app.core.database.Base` 继承
- **禁止重复定义**: 任何模块都不得重新定义 declarative_base()
- **导入规范**: 统一的导入路径 `from app.core.database import Base`

### 2. Session管理策略
- **依赖注入**: 通过FastAPI的依赖注入系统管理Session
- **事务控制**: Repository层负责事务边界管理
- **会话作用域**: 请求级Session，自动回收

### 3. 模块化数据访问
- **Repository模式**: 每个业务模块提供Repository封装数据访问
- **接口统一**: 标准的CRUD操作接口
- **关系管理**: 跨模块外键关系通过导入实现

## 具体实现设计

### app/core/database.py (已存在，需微调)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 统一的Base类 - 全局唯一
Base = declarative_base()

# 数据库引擎和会话配置
engine = create_engine(DATABASE_URL, ...)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### app/shared/mixins.py (新增)
```python
from sqlalchemy import Column, Integer, DateTime, func
from app.core.database import Base

class TimestampMixin:
    """通用时间戳混入"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class BaseModel(Base):
    """通用基础模型"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
```

### app/modules/user_auth/models.py (修改)
```python
from sqlalchemy import Column, String, Boolean
from app.shared.mixins import BaseModel  # 从共享基础导入

class User(BaseModel):
    __tablename__ = 'users'
    
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
```

### app/modules/user_auth/repositories.py (新增)
```python
from sqlalchemy.orm import Session
from .models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_active_users(self):
        return self.db.query(User).filter(User.is_active == True).all()
```

### 业务逻辑层使用 (示例)
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.user_auth.repositories import UserRepository

def register_user(email: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    
    # 检查用户是否存在
    if user_repo.find_by_email(email):
        raise ValueError("用户已存在")
    
    # 创建新用户
    return user_repo.create_user({"email": email})
```

## 跨模块关系管理

### 外键关系设计
```python
# app/modules/order_management/models.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.shared.mixins import BaseModel
# 导入其他模块的模型用于关系定义
from app.modules.user_auth.models import User

class Order(BaseModel):
    __tablename__ = 'orders'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 关系定义
    user = relationship("User", back_populates="orders")

# app/modules/user_auth/models.py 中添加反向关系
class User(BaseModel):
    # ... 其他字段
    orders = relationship("Order", back_populates="user")
```
