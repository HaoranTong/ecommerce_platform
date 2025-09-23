<!--version info: v2.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions.md,project-structure-standards.md-->

# 代码标准规范 (Code Standards)

## 概述

本文档定义代码质量、文档规范和开发实践的具体标准，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- `naming-conventions.md` - 代码命名规范（类、函数、变量、常量命名标准）
- `project-structure-standards.md` - 项目结构和模块组织标准

## 具体标准
⬆️ **文件命名规范**: 参见 [naming-conventions.md](naming-conventions.md#文件命名规范) - Python文件、模块文件命名

## 📋 文档说明

本文档定义代码质量标准、注释规范、导入管理、错误处理等编码实施规范，基于L1核心标准制定具体的代码开发标准。

### 🎯 文档职责
- **代码质量标准**: 注释规范、文档字符串、代码风格
- **模块化开发规范**: 依赖注入、导入管理、模块独立性
- **错误处理标准**: 异常处理、错误响应、调试支持
- **配置管理规范**: 环境变量、配置文件、依赖管理
- **测试代码规范**: 测试组织、命名约定、覆盖率要求

---

## � 代码注释和文档规范

### Python文件头部文档字符串 (强制要求)
```python
"""
{模块名称} - {功能简述}

该模块实现{业务领域}的{核心功能}，提供{主要服务或API}。

主要功能:
- 功能点1: 具体描述
- 功能点2: 具体描述
- 功能点3: 具体描述

技术栈:
- FastAPI: API路由和依赖注入
- SQLAlchemy: 数据库ORM操作
- Pydantic: 数据验证和序列化

依赖关系:
- app.core.database: 数据库连接管理
- app.modules.{module}.models: 数据模型定义
- app.modules.{module}.schemas: 请求响应模型

使用示例:
    ```python
    from app.modules.user_auth.router import router
    app.include_router(router, prefix="/api/v1")
    ```

```markdown
注意事项:
- 重要的业务规则或限制
- 性能考虑或优化建议
- 安全相关的注意点

Author: {开发者}
Created: {创建日期}
Modified: {最后修改日期}
```
Version: 1.0.0
"""
```

### 函数和方法文档字符串 (强制要求)
```python
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """创建新用户账户
    
    执行用户注册流程，包括数据验证、唯一性检查、密码加密和用户创建。
    该函数实现了完整的用户注册业务逻辑，确保数据安全和业务规则。
    
    Args:
        user_data (UserCreate): 用户创建数据模型
            - username: 用户名 (3-50字符，字母数字下划线)
            - email: 邮箱地址 (必须符合邮箱格式)
            - password: 密码 (最少8位，包含字母数字)
            - full_name: 用户全名 (可选)
        db (Session): SQLAlchemy数据库会话，通过依赖注入获取
        
    Returns:
        UserRead: 新创建的用户信息响应模型
            - id: 用户唯一标识符
            - username: 用户名
            - email: 邮箱地址
            - full_name: 用户全名
            - is_active: 激活状态 (默认True)
            - created_at: 创建时间戳
            
    Raises:
        HTTPException: HTTP异常，包含具体错误信息
            - 400 Bad Request: 用户名或邮箱已存在
            - 422 Unprocessable Entity: 输入数据验证失败
            - 500 Internal Server Error: 数据库操作失败
            
    Example:
        ```python
        # 创建用户请求
        user_data = UserCreate(
            username="john_doe", 
            email="john@example.com", 
            password="securePass123"
        )
        
        # 调用创建用户函数
        new_user = await create_user(user_data, db)
        
        # 返回的用户信息
        print(f"Created user: {new_user.username} ({new_user.id})")
        ```
            
```markdown
    Business Rules:
        - 用户名在系统中必须唯一
        - 邮箱地址在系统中必须唯一  
        - 密码使用bcrypt进行加密存储
        - 新用户默认角色为'user'
        - 创建后用户状态为已激活
        
    Performance:
        - 单次操作，平均响应时间 < 200ms
```
        - 涉及2次数据库查询：唯一性检查 + 插入操作
        - 建议在高并发场景下使用数据库唯一约束
        
    Security:
        - 密码不会在响应中返回
        - 使用bcrypt进行密码哈希，成本因子为12
        - 输入数据通过Pydantic进行严格验证
    """
```

### 类文档字符串 (强制要求)
```python
class UserService:
    """用户业务逻辑服务类
    
    该类封装用户相关的所有业务逻辑操作，包括用户生命周期管理、
    认证验证、权限控制等核心功能。采用依赖注入模式，支持单元测试。
    
    职责范围:
        - 用户账户管理: 创建、更新、删除、查询用户
        - 身份认证: 登录验证、密码验证、Token管理  
        - 权限控制: 角色验证、权限检查、访问控制
        - 数据验证: 业务规则验证、数据完整性检查
        
    设计模式:
        - Repository Pattern: 数据访问抽象
        - Service Layer: 业务逻辑封装
        - Dependency Injection: 依赖注入支持测试
        
    主要方法:
        - create_user(user_data): 创建新用户，包含验证和加密
        - authenticate_user(credentials): 用户登录认证
        - get_user_by_id(user_id): 根据ID获取用户信息
        - update_user_profile(user_id, update_data): 更新用户资料
        - deactivate_user(user_id): 停用用户账户
        - check_user_permissions(user_id, resource): 权限验证
        
    Usage:
        ```python
        # 初始化服务
        user_service = UserService(db_session=db)
        
        # 创建用户
        user_data = UserCreate(username="john", email="john@example.com")
        new_user = await user_service.create_user(user_data)
        
        # 用户认证
        credentials = LoginCredentials(username="john", password="pass")
        auth_result = await user_service.authenticate_user(credentials)
        ```
        
```markdown
    Dependencies:
        - db_session (Session): SQLAlchemy数据库会话
        - password_service (PasswordService): 密码加密服务
        - jwt_service (JWTService): Token生成和验证服务
        - cache_service (CacheService): 缓存服务，可选
        
    Thread Safety:
        该类不是线程安全的，每个请求应使用独立的实例。
        在FastAPI中通过依赖注入确保每个请求的隔离性。
        
    Performance Notes:
```
        - 用户查询操作已优化，平均响应时间 < 50ms
        - 密码验证使用异步操作，避免阻塞主线程
        - 支持Redis缓存，减少重复数据库查询
        
    Security Considerations:
        - 所有密码操作使用bcrypt加密
        - 敏感操作需要额外权限验证
        - 用户输入经过严格的数据验证和清理
    """
```

### 复杂逻辑代码注释 (强制要求)
```python
# =================================================================
# 用户唯一性验证 - 防止用户名和邮箱重复注册
# =================================================================
# 业务规则: 用户名和邮箱在整个系统中必须保持全局唯一性
# 性能考虑: 使用单次查询检查两个字段，避免多次数据库往返
# 错误处理: 提供具体的重复字段信息，便于前端用户体验优化
existing_user = db.query(User).filter(
    or_(
        User.username == user_data.username,
        User.email == user_data.email
    )
).first()

if existing_user:
    # 区分具体的重复字段，返回精确的错误信息
    # 这样前端可以高亮显示具体的错误字段
    if existing_user.username == user_data.username:
        raise HTTPException(
            status_code=400, 
            detail="用户名已存在，请选择其他用户名",
            headers={"X-Error-Field": "username"}
        )
    else:
        raise HTTPException(
            status_code=400, 
            detail="邮箱已被注册，请使用其他邮箱或尝试登录",
            headers={"X-Error-Field": "email"}
        )

# =================================================================
# 密码安全处理 - bcrypt加密存储
# =================================================================  
# 安全标准: 使用bcrypt算法，成本因子为12（2^12次迭代）
# 性能平衡: 成本因子12在安全性和性能间取得平衡，加密时间约100ms
# 盐值管理: bcrypt自动生成随机盐值，每次加密结果不同
try:
    password_hash = bcrypt.hashpw(
        user_data.password.encode('utf-8'),  # 确保字符串编码一致性
        bcrypt.gensalt(rounds=12)            # 使用标准安全级别
    )
except Exception as e:
    # 密码加密失败应该记录错误但不暴露给客户端
    logger.error(f"Password hashing failed: {e}")
    raise HTTPException(
        status_code=500,
        detail="账户创建失败，请稍后重试"
    )

# =================================================================
# 数据库事务管理 - 确保数据一致性
# =================================================================
# 事务范围: 用户创建和初始权限设置必须在同一事务中完成
# 回滚策略: 任何步骤失败都应回滚整个用户创建过程
# 并发控制: 使用数据库约束处理并发创建的竞态条件
try:
    # 开始事务：创建用户记录
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.flush()  # 获取用户ID但不提交事务
    
    # 事务内操作：设置默认用户权限
    default_role = db.query(Role).filter(Role.name == "user").first()
    if default_role:
        user_role = UserRole(user_id=new_user.id, role_id=default_role.id)
        db.add(user_role)
    
    # 提交整个事务
    db.commit()
    
except IntegrityError as e:
    # 处理数据库约束冲突（如唯一性约束）
    db.rollback()
    if "username" in str(e.orig):
        raise HTTPException(status_code=400, detail="用户名已存在")
    elif "email" in str(e.orig):
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    else:
        raise HTTPException(status_code=400, detail="数据冲突，请检查输入")
        
except Exception as e:
    # 处理其他数据库错误
    db.rollback()
    logger.error(f"User creation failed: {e}")
    raise HTTPException(status_code=500, detail="用户创建失败")
```

### 📋 注释规范执行标准

**强制要求清单**:
✅ **必须包含的注释**:
1. 所有Python文件的模块级文档字符串
2. 所有公共类的类文档字符串  
3. 所有公共方法和函数的文档字符串
4. 复杂业务逻辑的块级注释
5. 重要算法和数据处理的行内注释

❌ **质量标准**:
- 注释必须与代码同步更新
- 避免显而易见的注释 (如 `i += 1  # 增加i的值`)
- 使用中文注释，提高团队理解效率
- 注释应解释"为什么"而不仅仅是"做什么"

🔍 **代码审查检查点**:
- 新增函数是否有完整的文档字符串
- 复杂逻辑是否有足够的解释性注释
- 业务规则是否在注释中清晰说明
- 安全相关代码是否有风险提示
- 性能考虑是否在注释中体现

## 📦 导入管理和依赖组织

### 导入顺序和格式标准 (PEP 8 + 项目扩展)
```python
"""
导入顺序标准 - 各组之间用空行分隔
1. 标准库导入 (Python内置模块)
2. 第三方库导入 (pip安装的包)  
3. 本地应用导入 (项目内模块)
4. 相对导入 (同级或下级模块)
"""

# =================================================================
# 标准库导入 - Python内置模块
# =================================================================
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

# =================================================================
# 第三方库导入 - 外部依赖包
# =================================================================
# FastAPI框架相关
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

# 数据库和ORM
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

# 数据验证和序列化
from pydantic import BaseModel, Field, validator
import bcrypt
import jwt

# =================================================================
# 本地应用导入 - 项目内模块 (按依赖层级排序)
# =================================================================
# 核心基础设施层
from app.core.database import get_db, Base
from app.core.auth import get_current_user, verify_token
from app.core.config import settings

# 共享组件层 (仅技术必需的共享)
from app.shared.exceptions import BusinessError, ValidationError

# 业务模块层 (当前模块的依赖)
from app.modules.user_auth.models import User, UserRole
from app.modules.user_auth.schemas import UserCreate, UserRead, UserUpdate

# =================================================================
# 相对导入 - 同模块内文件 (最小化使用)
# =================================================================
from .service import UserService
from .dependencies import get_user_service
```

### 导入最佳实践和禁止行为
```python
# ✅ 推荐的导入方式
from typing import List, Optional                    # 明确指定导入项
from app.modules.user_auth.models import User       # 完整模块路径
from sqlalchemy.orm import Session                  # 具体导入所需类

# ❌ 禁止的导入方式
from typing import *                                # 禁止星号导入
import app.modules.user_auth.models as models      # 避免模糊别名
from .. import some_module                          # 避免复杂相对导入

# ✅ 处理导入冲突的正确方式
from datetime import datetime
from sqlalchemy import DateTime as SQLDateTime      # 使用明确别名

# ✅ 模块级别的导入组织
from app.modules.user_auth import (               # 多行导入格式
    models,
    schemas, 
    services,
    exceptions
)
```

### 循环导入预防策略
```python
# 问题场景：模块A和模块B相互依赖

# ❌ 错误：直接相互导入造成循环依赖
# file: app/modules/user_auth/service.py
from app.modules.order_management.models import Order  # 错误

# ✅ 解决方案1：使用字符串引用 (推荐)
# file: app/modules/user_auth/models.py
from sqlalchemy.orm import relationship

class User(Base):
    orders = relationship("Order", back_populates="user")  # 字符串引用

# ✅ 解决方案2：在函数内导入 (谨慎使用)
def get_user_orders(user_id: int):
    from app.modules.order_management.service import OrderService  # 函数内导入
    order_service = OrderService()
    return order_service.get_orders_by_user(user_id)

# ✅ 解决方案3：使用事件或消息机制 (最佳实践)
from app.core.events import EventBus

def create_user(user_data):
    # ... 创建用户逻辑
    EventBus.publish("user_created", {"user_id": user.id})  # 事件通知
```

## 🔗 依赖注入和模块化设计

### FastAPI依赖注入模式
```python
# =================================================================
# 依赖函数定义 - 模块内dependencies.py
# =================================================================
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from .service import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """获取用户服务实例
    
    使用依赖注入模式创建用户服务，确保每个请求使用独立的服务实例，
    支持单元测试时的依赖替换。
    
    Args:
        db: 数据库会话，通过依赖链自动注入
        
    Returns:
        UserService: 用户服务实例
    """
    return UserService(db)

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户
    
    验证当前用户是否为活跃状态，非活跃用户将被拒绝访问。
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        User: 活跃的用户对象
        
    Raises:
        HTTPException: 用户未激活时抛出403错误
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被停用"
        )
    return current_user

def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取管理员用户
    
    验证当前用户是否具有管理员权限。
    
    Args:
        current_user: 当前活跃用户
        
    Returns:
        User: 具有管理员权限的用户
        
    Raises:
        HTTPException: 非管理员用户访问时抛出403错误
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user
```

### 路由处理函数依赖注入
```python
# =================================================================
# API路由函数 - 使用依赖注入
# =================================================================
from fastapi import APIRouter, Depends, status
from .dependencies import get_user_service, get_current_active_user
from .schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.post("/users/", 
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED,
             summary="创建新用户",
             description="注册新用户账户，执行数据验证和安全检查")
async def create_user(
    user_data: UserCreate,                                # 请求体数据
    user_service: UserService = Depends(get_user_service) # 业务服务注入
) -> UserRead:
    """创建用户API端点"""
    return await user_service.create_user(user_data)

@router.get("/users/me", 
            response_model=UserRead,
            summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)  # 认证用户注入
) -> UserRead:
    """获取当前登录用户的详细信息"""
    return UserRead.from_orm(current_user)

@router.put("/users/me",
            response_model=UserRead, 
            summary="更新当前用户信息")
async def update_current_user(
    user_update: UserUpdate,                               # 更新数据
    current_user: User = Depends(get_current_active_user), # 当前用户
    user_service: UserService = Depends(get_user_service)  # 业务服务
) -> UserRead:
    """更新当前用户的个人信息"""
    return await user_service.update_user(current_user.id, user_update)
```

## 🚨 错误处理和异常管理

### 自定义异常层级结构
```python
# =================================================================
# 异常定义 - 模块内exceptions.py
# =================================================================
from fastapi import HTTPException, status

class BaseBusinessException(Exception):
    """业务异常基类
    
    所有业务相关异常的基类，提供统一的异常处理接口。
    """
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)

class UserBusinessError(BaseBusinessException):
    """用户业务异常"""
    pass

class UserNotFoundError(UserBusinessError):
    """用户不存在异常"""
    def __init__(self, user_id: int = None, username: str = None):
        if user_id:
            message = f"用户ID {user_id} 不存在"
        elif username:
            message = f"用户名 '{username}' 不存在" 
        else:
            message = "用户不存在"
        super().__init__(message, "USER_NOT_FOUND")

class UserAlreadyExistsError(UserBusinessError):
    """用户已存在异常"""
    def __init__(self, field: str, value: str):
        message = f"{field} '{value}' 已被使用"
        super().__init__(message, "USER_ALREADY_EXISTS")

class InsufficientPermissionError(UserBusinessError):
    """权限不足异常"""
    def __init__(self, required_permission: str):
        message = f"操作需要 '{required_permission}' 权限"
        super().__init__(message, "INSUFFICIENT_PERMISSION")
```

### HTTP异常处理和响应
```python
# =================================================================
# 异常处理器 - 统一错误响应格式
# =================================================================
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
import logging

logger = logging.getLogger(__name__)

async def business_exception_handler(request: Request, exc: BaseBusinessException):
    """业务异常处理器
    
    统一处理业务逻辑异常，转换为标准的HTTP响应格式。
    
    Args:
        request: FastAPI请求对象
        exc: 业务异常实例
        
    Returns:
        JSONResponse: 标准错误响应
    """
    # 记录业务异常日志
    logger.warning(f"Business exception: {exc.error_code} - {exc.message}")
    
    # 根据异常类型确定HTTP状态码
    status_code_mapping = {
        "USER_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "USER_ALREADY_EXISTS": status.HTTP_400_BAD_REQUEST,
        "INSUFFICIENT_PERMISSION": status.HTTP_403_FORBIDDEN,
    }
    
    status_code = status_code_mapping.get(
        exc.error_code, 
        status.HTTP_400_BAD_REQUEST
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "code": status_code,
            "message": exc.message,
            "error": {
                "type": "BUSINESS_ERROR",
                "code": exc.error_code,
                "details": []
            },
            "metadata": {
                "request_id": getattr(request.state, 'request_id', None),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """数据验证异常处理器"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # 转换Pydantic验证错误为用户友好格式
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "value": error.get("input")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "code": 422,
            "message": "请求数据验证失败",
            "error": {
                "type": "VALIDATION_ERROR",
                "code": "VALIDATION_FAILED",
                "details": error_details
            },
            "metadata": {
                "request_id": getattr(request.state, 'request_id', None),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

### 错误处理最佳实践
```python
# =================================================================
# 服务层错误处理示例
# =================================================================
class UserService:
    async def create_user(self, user_data: UserCreate) -> User:
        """创建用户 - 展示完整的错误处理模式"""
        try:
            # 1. 业务规则验证
            await self._validate_user_uniqueness(user_data)
            
            # 2. 数据处理
            hashed_password = self._hash_password(user_data.password)
            
            # 3. 数据库操作
            user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=hashed_password
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            return user
            
        except UserAlreadyExistsError:
            # 业务异常直接向上传播
            raise
            
        except SQLAlchemyError as e:
            # 数据库异常处理
            logger.error(f"Database error in create_user: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库操作失败，请稍后重试"
            )
            
        except Exception as e:
            # 未预期异常处理
            logger.error(f"Unexpected error in create_user: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="服务器内部错误"
            )
    
    async def _validate_user_uniqueness(self, user_data: UserCreate):
        """验证用户唯一性 - 私有方法展示具体验证逻辑"""
        existing_user = await self.db.query(User).filter(
            or_(
                User.username == user_data.username,
                User.email == user_data.email
            )
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise UserAlreadyExistsError("用户名", user_data.username)
            else:
                raise UserAlreadyExistsError("邮箱", user_data.email)
```

## ⚙️ 配置管理和环境设置

### 配置文件组织结构
```python
# =================================================================
# 配置定义 - app/core/config.py
# =================================================================
from pydantic import BaseSettings, Field, validator
from typing import Optional, List
import os

class DatabaseSettings(BaseSettings):
    """数据库配置设置"""
    
    # 数据库连接配置
    DB_HOST: str = Field("localhost", description="数据库主机地址")
    DB_PORT: int = Field(5432, description="数据库端口")
    DB_USER: str = Field("postgres", description="数据库用户名")
    DB_PASSWORD: str = Field("", description="数据库密码")
    DB_NAME: str = Field("ecommerce", description="数据库名称")
    
    # 连接池配置
    DB_POOL_SIZE: int = Field(10, description="连接池大小")
    DB_MAX_OVERFLOW: int = Field(20, description="最大溢出连接数")
    DB_POOL_TIMEOUT: int = Field(30, description="连接超时时间(秒)")
    
    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_prefix = "DB_"  # 环境变量前缀

class RedisSettings(BaseSettings):
    """Redis缓存配置"""
    
    REDIS_HOST: str = Field("localhost", description="Redis主机地址")
    REDIS_PORT: int = Field(6379, description="Redis端口")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis密码")
    REDIS_DB: int = Field(0, description="Redis数据库编号")
    REDIS_TTL: int = Field(3600, description="默认缓存时间(秒)")
    
    @property
    def redis_url(self) -> str:
        """构建Redis连接URL"""
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_prefix = "REDIS_"

class AuthSettings(BaseSettings):
    """认证授权配置"""
    
    # JWT配置
    JWT_SECRET_KEY: str = Field(..., description="JWT密钥")
    JWT_ALGORITHM: str = Field("HS256", description="JWT算法")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="访问令牌过期时间(分钟)")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, description="刷新令牌过期时间(天)")
    
    # 密码安全配置
    PASSWORD_MIN_LENGTH: int = Field(8, description="密码最小长度")
    PASSWORD_BCRYPT_ROUNDS: int = Field(12, description="bcrypt加密轮次")
    
    @validator("JWT_SECRET_KEY")
    def validate_secret_key(cls, v):
        """验证JWT密钥强度"""
        if len(v) < 32:
            raise ValueError("JWT密钥长度至少32位")
        return v
    
    class Config:
        env_prefix = "AUTH_"

class ApplicationSettings(BaseSettings):
    """应用主配置"""
    
    # 应用基本信息
    APP_NAME: str = Field("E-commerce Platform", description="应用名称")
    APP_VERSION: str = Field("1.0.0", description="应用版本")
    APP_DESCRIPTION: str = Field("农产品电商平台", description="应用描述")
    
    # 运行环境配置
    ENVIRONMENT: str = Field("development", description="运行环境")
    DEBUG: bool = Field(False, description="调试模式")
    LOG_LEVEL: str = Field("INFO", description="日志级别")
    
    # API配置
    API_PREFIX: str = Field("/api/v1", description="API路径前缀")
    CORS_ORIGINS: List[str] = Field(["*"], description="跨域允许的源")
    
    # 实例化子配置
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    auth: AuthSettings = AuthSettings()
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """验证环境配置"""
        allowed_envs = ["development", "testing", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"环境配置必须是: {allowed_envs}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 全局配置实例
settings = ApplicationSettings()
```

### 环境变量管理
```bash
# =================================================================
# 环境变量文件 - .env (开发环境)
# =================================================================

# 应用配置
APP_NAME=E-commerce Platform
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=ecommerce_dev
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_TTL=3600

# 认证配置
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_MIN_LENGTH=8
PASSWORD_BCRYPT_ROUNDS=12

# API配置
API_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## 🧪 测试代码规范

### 测试文件组织结构
```tree
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # pytest全局配置和fixtures
├── test_config.py                 # 测试配置验证
├── unit/                          # 单元测试
│   ├── __init__.py
│   ├── test_models/               # 模型单元测试
│   │   ├── __init__.py
│   │   ├── test_user.py          # 用户模型测试
│   │   └── test_product.py       # 商品模型测试
│   ├── test_services/             # 服务单元测试
│   │   ├── __init__.py
│   │   ├── test_user_service.py  # 用户服务测试
│   │   └── test_auth_service.py  # 认证服务测试
│   └── test_utils/                # 工具函数测试
├── integration/                   # 集成测试
│   ├── __init__.py
│   ├── test_api/                  # API集成测试
│   │   ├── __init__.py
│   │   ├── test_user_api.py      # 用户API测试
│   │   └── test_auth_api.py      # 认证API测试
│   └── test_database/             # 数据库集成测试
└── e2e/                          # 端到端测试
    ├── __init__.py
    └── test_user_workflow.py     # 用户流程测试
```

### 测试代码质量标准
```python
# =================================================================
# 测试配置和Fixtures - tests/conftest.py
# =================================================================
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """数据库引擎fixture - 会话级别"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """数据库会话fixture - 函数级别，每个测试独立事务"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """测试客户端fixture"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user_data():
    """样本用户数据fixture"""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }

# =================================================================
# 单元测试示例 - tests/unit/test_services/test_user_service.py
# =================================================================
import pytest
from unittest.mock import Mock, patch
from app.modules.user_auth.service import UserService
from app.modules.user_auth.schemas import UserCreate
from app.modules.user_auth.exceptions import UserAlreadyExistsError

class TestUserService:
    """用户服务测试类
    
    测试用户服务的所有业务逻辑，确保功能正确性和边界条件处理。
    """
    
    @pytest.fixture
    def user_service(self, db_session):
        """用户服务实例fixture"""
        return UserService(db_session)
    
    @pytest.fixture
    def valid_user_data(self):
        """有效用户数据fixture"""
        return UserCreate(
            username="john_doe",
            email="john@example.com",
            password="securepass123",
            full_name="John Doe"
        )
    
    async def test_create_user_success(self, user_service, valid_user_data):
        """测试成功创建用户
        
        验证正常情况下用户创建流程的正确性。
        """
        # Act - 执行操作
        result = await user_service.create_user(valid_user_data)
        
        # Assert - 验证结果
        assert result.username == valid_user_data.username
        assert result.email == valid_user_data.email
        assert result.full_name == valid_user_data.full_name
        assert result.is_active is True
        assert result.id is not None
        assert hasattr(result, 'created_at')
        
        # 验证密码已加密（不应该是明文）
        assert not hasattr(result, 'password')
    
    async def test_create_user_duplicate_username(self, user_service, valid_user_data):
        """测试创建用户时用户名重复
        
        验证用户名唯一性约束的正确处理。
        """
        # Arrange - 准备数据
        await user_service.create_user(valid_user_data)
        
        # 创建相同用户名但不同邮箱的用户数据
        duplicate_user_data = UserCreate(
            username=valid_user_data.username,  # 相同用户名
            email="different@example.com",       # 不同邮箱
            password="differentpass123"
        )
        
        # Act & Assert - 执行并验证异常
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await user_service.create_user(duplicate_user_data)
        
        assert "用户名" in str(exc_info.value)
        assert valid_user_data.username in str(exc_info.value)
    
    async def test_create_user_duplicate_email(self, user_service, valid_user_data):
        """测试创建用户时邮箱重复"""
        # Arrange
        await user_service.create_user(valid_user_data)
        
        duplicate_email_data = UserCreate(
            username="different_user",
            email=valid_user_data.email,  # 相同邮箱
            password="differentpass123"
        )
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await user_service.create_user(duplicate_email_data)
        
        assert "邮箱" in str(exc_info.value)
    
    @patch('app.modules.user_auth.service.bcrypt.hashpw')
    async def test_create_user_password_hashing(self, mock_hashpw, user_service, valid_user_data):
        """测试密码加密处理
        
        使用Mock验证密码加密函数被正确调用。
        """
        # Arrange
        mock_hashpw.return_value = b'hashed_password'
        
        # Act
        await user_service.create_user(valid_user_data)
        
        # Assert
        mock_hashpw.assert_called_once()
        call_args = mock_hashpw.call_args[0]
        assert call_args[0] == valid_user_data.password.encode('utf-8')

# =================================================================
# API集成测试示例 - tests/integration/test_api/test_user_api.py
# =================================================================
class TestUserAPI:
    """用户API集成测试
    
    测试完整的HTTP请求响应流程，验证API接口的正确性。
    """
    
    def test_create_user_api_success(self, client, sample_user_data):
        """测试创建用户API成功场景"""
        # Act
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == sample_user_data["username"]
        assert data["data"]["email"] == sample_user_data["email"]
        assert "password" not in data["data"]  # 确保密码不被返回
    
    def test_create_user_api_validation_error(self, client):
        """测试创建用户API参数验证错误"""
        # 测试数据缺少必需字段
        invalid_data = {
            "username": "test",
            # 缺少email和password
        }
        
        # Act
        response = client.post("/api/v1/users/", json=invalid_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "VALIDATION_ERROR"
        assert len(data["error"]["details"]) > 0
    
    def test_get_current_user_unauthorized(self, client):
        """测试获取当前用户信息 - 未认证"""
        # Act
        response = client.get("/api/v1/users/me")
        
        # Assert
        assert response.status_code == 401
```

## ❌ 代码质量禁止项和强制要求

### 绝对禁止的行为
```python
# ❌ 禁止行为清单

# 1. 硬编码配置和敏感信息
DATABASE_URL = "postgresql://user:pass@localhost/db"  # 禁止
API_KEY = "sk-1234567890abcdef"                       # 禁止

# 2. 过长的函数和类
def very_long_function():  # 禁止超过50行的函数
    # ... 超过50行代码
    pass

class HugeClass:  # 禁止超过200行的类
    # ... 超过200行代码
    pass

# 3. 不安全的导入和操作
from some_module import *                              # 禁止星号导入
exec("some_dynamic_code")                             # 禁止动态执行
eval("some_expression")                               # 禁止动态求值

# 4. 不规范的异常处理
try:
    risky_operation()
except:  # 禁止捕获所有异常而不指定类型
    pass

# 5. 内存和资源泄漏
file = open("data.txt")  # 禁止不使用with语句
data = file.read()       # 可能造成文件句柄泄漏
```

### ✅ 强制执行的质量标准
```python
# ✅ 必须遵循的标准

# 1. 使用环境变量和配置
from app.core.config import settings
DATABASE_URL = settings.database.database_url        # 正确

# 2. 函数长度控制
def well_structured_function():                       # 函数不超过50行
    """简洁的函数实现"""
    return process_data()

# 3. 安全的导入方式
from typing import List, Optional                     # 明确导入
from app.modules.user_auth.models import User        # 具体路径

# 4. 规范的异常处理
try:
    risky_operation()
except SpecificException as e:                        # 指定异常类型
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail="操作失败")

# 5. 资源管理
with open("data.txt", "r") as file:                   # 使用上下文管理器
    data = file.read()                                # 自动关闭文件

# 6. 完整的类型注解
def process_user(user_id: int, user_data: UserUpdate) -> UserRead:  # 类型注解
    """带有完整类型信息的函数"""
    pass
```

### 🔍 代码质量检查清单

**提交前必检项目**:
- [ ] 所有函数都有类型注解和文档字符串
- [ ] 复杂逻辑都有解释性注释
- [ ] 无硬编码的配置值和敏感信息
- [ ] 异常处理具体且有意义
- [ ] 导入语句规范且无循环依赖
- [ ] 测试覆盖率达到80%以上
- [ ] 代码格式符合Black和isort标准
- [ ] 无pylint和mypy警告错误