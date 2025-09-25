<!--version info: v1.0.0, created: 2025-09-25, level: L2, dependencies: naming-conventions-standards.md,database-standards.md-->

# 数据访问层设计标准 (Data Access Layer Standards)

## 概述

本文档定义数据访问层（Repository Pattern）的设计规范和实现标准，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- **[命名规范标准](naming-conventions-standards.md)** - Repository类命名、方法命名标准
- **[数据库设计标准](database-standards.md)** - 数据模型、查询优化规范

## 具体标准

## 📋 文档说明

本文档定义数据访问层的架构模式、接口设计、实现规范，确保数据访问的一致性和可维护性。

### 🎯 文档职责
- **Repository模式**: 数据访问层抽象接口设计
- **实现规范**: 具体数据访问类实现标准
- **查询优化**: 数据库查询性能优化指导
- **事务管理**: 数据库事务控制规范
- **错误处理**: 数据访问异常处理标准

---

## 🎯 数据访问层核心原则

### Repository模式原则
1. **抽象数据访问** - 将数据访问逻辑与业务逻辑分离
2. **统一接口规范** - 提供标准化的数据操作接口
3. **可测试性** - 支持单元测试的Mock和Stub
4. **查询优化** - 集中管理数据库查询优化
5. **事务一致性** - 确保数据操作的ACID特性

### 模块化设计原则
- **模块独立性** - 每个业务模块独立管理自己的数据访问层
- **公共组件复用** - 共享基础查询工具和数据库连接
- **接口统一性** - 遵循统一的Repository接口设计模式
- **性能优化** - 集中管理查询缓存和连接池
- **监控追踪** - 支持SQL执行监控和性能分析

## 🏗️ Repository架构设计

### 1. 简化Repository模式（推荐）

对于大多数CRUD操作，建议直接在Service层使用SQLAlchemy ORM：

```python
# app/modules/user_auth/service.py
class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建用户 - 直接使用ORM"""
        db_user = User(**user_data.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        return db.query(User).offset(skip).limit(limit).all()
```

### 2. 复杂Repository模式（特殊场景）

对于复杂查询或需要特殊优化的场景，可创建独立Repository：

```python
# app/modules/user_auth/repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.user_auth.models import User

class UserRepositoryInterface(ABC):
    """用户数据访问接口"""
    
    @abstractmethod
    def create(self, db: Session, user: User) -> User:
        pass
    
    @abstractmethod
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def update(self, db: Session, user_id: int, **kwargs) -> Optional[User]:
        pass
    
    @abstractmethod
    def delete(self, db: Session, user_id: int) -> bool:
        pass

class UserRepository(UserRepositoryInterface):
    """用户数据访问实现"""
    
    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    def get_active_users_with_roles(self, db: Session) -> List[User]:
        """复杂查询：获取有角色的活跃用户"""
        return db.query(User)\
                 .join(UserRole)\
                 .filter(User.is_active == True)\
                 .filter(User.is_deleted == False)\
                 .all()
```

## 📊 使用场景判断

### 何时使用简化模式（Service直接ORM）

✅ **推荐场景**：
- 基础CRUD操作
- 单表查询
- 简单条件过滤
- 快速原型开发
- 团队ORM熟练度高

```python
# 适合简化模式的场景
def get_user_profile(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: UserCreate):
    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    return user
```

### 何时使用Repository模式

✅ **推荐场景**：
- 复杂多表联查
- 原生SQL优化需求
- 多种数据源切换
- 高度可测试性要求
- 数据访问逻辑复杂

```python
# 适合Repository模式的场景
def get_user_permissions_report(db: Session, user_id: int):
    # 复杂的权限分析查询，涉及多表联结和聚合
    return db.execute(text("""
        SELECT u.username, r.name as role_name, 
               COUNT(p.id) as permission_count
        FROM users u
        JOIN user_roles ur ON u.id = ur.user_id
        JOIN roles r ON ur.role_id = r.id
        JOIN role_permissions rp ON r.id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE u.id = :user_id AND u.is_active = 1
        GROUP BY u.id, r.id
    """), {"user_id": user_id}).fetchall()
```

## ⚖️ 架构决策指南

### 项目当前状态评估

根据当前user_auth模块实现分析：

| 评估维度 | 当前状态 | 建议方案 |
|---------|----------|---------|
| 查询复杂度 | 简单到中等 | ✅ 保持Service直接ORM |
| 团队熟练度 | 高（FastAPI + SQLAlchemy） | ✅ 继续使用ORM |
| 性能要求 | 标准电商应用 | ✅ ORM性能足够 |
| 测试需求 | 单元测试 + 集成测试 | ✅ ORM支持良好 |
| 维护成本 | 追求简洁 | ✅ 减少抽象层次 |

### 推荐策略

1. **现阶段（MVP和快速迭代）**：
   - 使用Service直接ORM模式
   - 专注业务逻辑实现
   - 保持代码简洁性

2. **演进阶段（性能优化需求）**：
   - 识别性能瓶颈查询
   - 选择性引入Repository
   - 渐进式架构升级

3. **成熟阶段（企业级需求）**：
   - 完整Repository抽象
   - 多数据源支持
   - 高级缓存策略

## 🔧 实现规范

### Service层数据访问规范

```python
class UserService:
    """用户业务服务 - 推荐的简化数据访问模式"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """用户认证 - 包含业务逻辑的数据访问"""
        # 查询用户
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        # 业务验证
        if not user or not verify_password(password, user.password_hash):
            return None
        
        # 更新登录信息
        user.last_login_at = datetime.utcnow()
        user.failed_login_attempts = 0
        db.commit()
        
        return user
    
    @staticmethod
    def create_user_with_validation(db: Session, user_data: UserCreate) -> User:
        """创建用户 - 包含业务验证"""
        # 检查唯一性
        existing = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
```

### 查询优化规范

```python
# 1. 使用索引优化查询
def get_active_users_by_role(db: Session, role: str):
    """利用复合索引 idx_role_active"""
    return db.query(User).filter(
        User.role == role,
        User.is_active == True
    ).all()

# 2. 预加载关联数据
from sqlalchemy.orm import joinedload

def get_user_with_roles(db: Session, user_id: int):
    """使用joinedload预加载角色数据"""
    return db.query(User)\
             .options(joinedload(User.roles))\
             .filter(User.id == user_id)\
             .first()

# 3. 分页查询优化
def get_users_paginated(db: Session, page: int, size: int):
    """分页查询优化"""
    offset = (page - 1) * size
    return db.query(User)\
             .filter(User.is_deleted == False)\
             .order_by(User.created_at.desc())\
             .offset(offset)\
             .limit(size)\
             .all()
```

## 📝 总结建议

### 当前项目建议
1. **保持现有架构**：user_auth模块当前的Service直接ORM模式符合项目需求
2. **关注性能监控**：监控SQL查询性能，识别优化需求
3. **渐进式演进**：根据业务复杂度增长，选择性引入Repository模式
4. **统一规范**：确保所有模块遵循相同的数据访问模式

### 未来演进路径
1. **短期**：完善现有Service层数据访问规范
2. **中期**：为复杂查询场景引入Repository抽象
3. **长期**：建立完整的数据访问层架构体系

---

## 🔗 相关文档
- [数据库设计标准](database-standards.md) - 数据模型和查询优化
- [代码规范标准](code-standards.md) - Service层实现规范
- [性能优化标准](performance-standards.md) - 查询性能优化指导