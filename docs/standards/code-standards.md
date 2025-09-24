<!--version info: v1.0.0, created: 2025-09-23, level: L1, dependencies: naming-conventions-standards.md,PROJECT-FOUNDATION.md-->

# 代码标准规范 (Code Standards)

## 概述

本文档定义代码质量、文档规范和开发实践的具体标准，属于L2领域标准。

## 依赖标准

本标准依赖以下L1核心标准：
- `naming-conventions-standards.md` - 代码命名规范（类、函数、变量、常量命名标准）
- `PROJECT-FOUNDATION.md` - 项目结构和模块组织标准

## 具体标准
⬆️ **文件命名规范**: 参见 [naming-conventions-standards.md](naming-conventions-standards.md#文件命名规范) - Python文件、模块文件命名

## 📋 文档说明

本文档定义代码质量标准、注释规范、导入管理、错误处理等编码实施规范，基于L1核心标准制定具体的代码开发标准。

### 🎯 文档职责
- **代码质量标准**: 注释规范、文档字符串、代码风格一致性
- **开发实践规范**: 错误处理、导入管理、配置管理标准
- **代码组织规范**: 函数设计、类设计、模块化开发最佳实践
- **动态管理职责**: app/目录下新增业务模块的结构标准和代码规范

## L2标准动态管理义务

### 静态内容确认 (基于L1权威定义)
✅ **app/目录结构已完整定义**: 参考 [PROJECT-FOUNDATION.md - app/目录结构](../../PROJECT-FOUNDATION.md#app目录一级结构-应用程序组织)
- core/, modules/, shared/, adapters/ 等核心子目录已权威定义
- 业务模块标准结构已完整规范 (垂直切片架构)
- 19个业务模块命名映射表已建立

### 动态内容管理规范
**新增业务模块管理** (随业务发展动态增加):
1. **新模块创建标准**
   - 模块命名: 必须遵循 [业务模块命名映射表](../../PROJECT-FOUNDATION.md#业务模块标准结构-垂直切片)
   - 目录结构: 严格按照垂直切片标准结构创建 (router.py, service.py, models.py, schemas.py, dependencies.py, README.md)
   - 代码规范: 按照本标准的代码质量要求实施

2. **模块文档规范**
   - 每个新模块必须包含 README.md，说明模块功能、API接口、数据模型
   - 所有Python文件必须包含标准文档字符串
   - 复杂业务逻辑必须有详细注释和设计说明

3. **模块集成标准**  
   - 新模块不得直接导入其他业务模块 (通过shared层集成)
   - API schemas必须在模块内独立定义，不得跨模块共享
   - 数据库表前缀必须遵循命名映射表定义

### 动态管理边界
**本标准负责**:
- ✅ app/目录内所有代码的质量标准和文档规范
- ✅ 新增业务模块的结构标准和命名规范
- ✅ 代码注释、文档字符串、错误处理等编码标准

**本标准不负责**:
- ❌ 项目整体目录结构定义 (由PROJECT-FOUNDATION.md权威定义)
- ❌ 测试代码的组织和规范 (由testing-standards.md管理)
- ❌ 数据库设计和迁移脚本 (由database-standards.md管理)


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
- Pydantic: 数据验证和序列化
- 其他框架: 参见对应领域标准文档

依赖关系:
- app.core: 核心基础设施
- app.modules.{module}.models: 数据模型定义
- app.modules.{module}.schemas: 请求响应模型

使用示例:
from app.modules.user_auth.router import router
app.include_router(router, prefix="/api/v1")
"""
```

```markdown
**注意事项**:
- 重要的业务规则或限制
- 性能考虑或优化建议
- 安全相关的注意点

**文档头部信息模板**:
```

```text
Author: {开发者}
Created: {创建日期}  
Modified: {最后修改日期}
Version: {版本号}
```

```yaml
Version: 1.0.0
```

### 函数和方法文档字符串 (强制要求)
```python
def create_entity(entity_data: EntityCreate, service: EntityService = Depends(get_entity_service)) -> EntityRead:
    """创建新实体记录
    
    执行实体创建流程，包括数据验证、唯一性检查、数据处理和实体创建。
    该函数实现了完整的实体创建业务逻辑，确保数据安全和业务规则。
    
    Args:
        user_data (UserCreate): 用户创建数据模型
            - username: 用户名 (3-50字符，字母数字下划线)
            - email: 邮箱地址 (必须符合邮箱格式)
            - password: 密码 (最少8位，包含字母数字)
            - full_name: 用户全名 (可选)
        service (UserService): 用户业务服务，通过依赖注入获取
        
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
            - 400 Bad Request: 业务规则冲突（如重复标识符）
            - 422 Unprocessable Entity: 输入数据验证失败
            - 500 Internal Server Error: 服务内部错误
            
    Example:
        # 创建用户请求
        user_data = UserCreate(
            username="john_doe", 
            email="john@example.com", 
            password="securePass123"
        )
        
        # 调用创建实体函数
        new_entity = await create_entity(entity_data, db)
        
        # 返回的实体信息
        print(f"Created entity: {new_entity.name} ({new_entity.id})")

    **Business Rules**:
        - 具体业务规则应在需求文档或模块文档中定义
        - 代码文档字符串应引用而非重复定义业务规则
        - 保持代码规范与业务需求的清晰分离
        - 数据验证和唯一性检查应遵循项目结构标准中的模块边界
        
    Performance:
        - 单次操作，平均响应时间 < 200ms
        - 涉及业务逻辑验证和数据持久化操作
        - 建议在高并发场景下使用适当的并发控制机制
        
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
        - Service Layer: 业务逻辑封装和组织
        - Dependency Injection: 依赖注入支持测试和模块解耦
        - Strategy Pattern: 算法策略分离
        
    主要方法:
        - create_entity(entity_data): 创建新实体，包含验证和处理
        - authenticate_entity(credentials): 实体认证
        - get_entity_by_id(entity_id): 根据ID获取实体信息
        - update_entity_profile(entity_id, update_data): 更新实体资料
        - deactivate_entity(entity_id): 停用实体
        - check_entity_permissions(entity_id, resource): 权限验证
        
    Usage:
        # 初始化服务（通过依赖注入）
        entity_service = Depends(get_entity_service)
        
        # 创建实体
        entity_data = EntityCreate(name="john", email="john@example.com")
        new_entity = await entity_service.create_entity(entity_data)
        
        # 实体认证
        credentials = AuthCredentials(identifier="john", token="auth_token")
        auth_result = await entity_service.authenticate_entity(credentials)

    **Dependencies**:
        - service (UserService): 用户业务服务实例
        - password_service (PasswordService): 密码加密服务
        - jwt_service (JWTService): Token生成和验证服务
        - cache_service (CacheService): 缓存服务，可选
        
    Thread Safety:
        该类不是线程安全的，每个请求应使用独立的实例。
        在FastAPI中通过依赖注入确保每个请求的隔离性。
        
    Performance Notes:
        - 业务操作已优化，平均响应时间 < 50ms
        - 密码验证使用异步操作，避免阻塞主线程
        - 支持缓存机制，减少重复计算和外部调用
        
    Security Considerations:
        - 所有密码操作使用bcrypt加密
        - 敏感操作需要额外权限验证
        - 用户输入经过严格的数据验证和清理
    """
```

### 复杂逻辑代码注释 (强制要求)
```python
# =================================================================
# 业务数据验证 - 确保数据完整性和业务规则
# =================================================================
# 业务规则: 关键业务字段必须满足唯一性和完整性约束
# 性能考虑: 使用服务层封装验证逻辑，减少重复代码
# 错误处理: 提供明确的验证错误信息，便于用户理解和修正
try:
    # 调用业务验证服务
    validation_result = service.validate_business_rules(input_data)
    
    if not validation_result.is_valid:
        # 返回具体的验证错误信息
        error_details = validation_result.get_error_details()
        raise HTTPException(
            status_code=400,
            detail=error_details.message,
            headers={"X-Error-Field": error_details.field}
        )
        
except ValidationError as e:
    # 处理业务验证异常
    raise HTTPException(
        status_code=400,
        detail=f"数据验证失败: {e.message}"
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
# 业务逻辑组织 - 确保操作原子性
# =================================================================
# 操作范围: 相关业务对象的创建和初始化应该在同一操作中完成
# 错误处理: 任何步骤失败都应该回滚整个业务操作
# 并发控制: 使用适当的机制处理并发操作的竞态条件
try:
    # 第一步：创建主要业务对象
    result = service.create_main_object(
        data=validated_data,
        context=operation_context
    )
    
    # 第二步：设置关联对象
    service.initialize_related_objects(result.id)
    
    # 第三步：完成操作并确认结果
    service.finalize_operation(result.id)
    
except BusinessError as e:
    # 处理业务规则冲突
    if e.error_code == "DUPLICATE_IDENTIFIER":
        raise HTTPException(status_code=400, detail="标识符已存在")
    elif e.error_code == "DUPLICATE_EMAIL":
        raise HTTPException(status_code=400, detail="邮箱已被使用")
    else:
        raise HTTPException(status_code=400, detail=f"业务规则冲突: {e.message}")
        
except Exception as e:
    # 处理其他未预期错误
    service.rollback_operation()
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail="操作失败，请稍后重试")
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

# 数据验证和序列化  
from pydantic import BaseModel, Field, validator
import bcrypt
import jwt

# =================================================================
# 本地应用导入 - 项目内模块 (按依赖层级排序)
# =================================================================
# 核心基础设施层
from app.core.auth import get_current_user, verify_token
from app.core.config import settings
from app.core.logger import get_logger

# 共享组件层 (仅技术必需的共享)
from app.shared.exceptions import BusinessError, ValidationError
from app.shared.utils import format_datetime, validate_input

# 业务模块层 (当前模块的依赖)
from app.modules.{module}.models import {ModelName}
from app.modules.{module}.schemas import {CreateSchema}, {ReadSchema}, {UpdateSchema}

# =================================================================
# 相对导入 - 同模块内文件 (最小化使用)
# =================================================================
from .service import UserService
from .dependencies import get_user_service
```

### 导入最佳实践和禁止行为
```python
# ✅ 推荐的导入方式 - 明确指定导入项
from typing import List, Optional                    # 具体类型导入
from datetime import datetime, timedelta           # 明确导入函数
from app.modules.user_auth.models import User       # 完整模块路径
from app.services import UserService               # 业务服务类导入

# ❌ 禁止的导入方式 - 避免命名空间污染
from typing import *                                # 禁止星号导入
from datetime import *                              # 污染命名空间
from sqlalchemy import *                           # 第三方库星号导入
import app.modules.user_auth.models as models      # 避免模糊别名
from .. import some_module                          # 避免复杂相对导入

# ✅ 处理导入冲突的正确方式  
from datetime import datetime
from external_lib import DateTime as ExternalDateTime    # 使用明确别名

# ✅ 模块级别的导入组织
from app.modules.user_auth import (               # 多行导入格式
    models,
    schemas, 
    services,
    exceptions
)
```

### 基础设施统一导入原则
```python
# ✅ 正确的基础设施导入方式 - 统一来源
from app.core.config import Settings              # 统一配置管理
from app.core.logging import get_logger           # 统一日志服务

# ❌ 禁止的基础设施导入方式
from multiple_config_sources import *             # 禁止配置来源混乱
```

**数据库相关导入**: 参见项目结构标准中的数据库模块组织规范

### 跨模块引用最佳实践
```python
# ✅ 跨模块导入：直接导入需要的类
from app.modules.user_auth.models import User
from app.modules.product_catalog.models import Product
from app.modules.order_management.services import OrderService

# ✅ 避免循环导入：优先使用字符串引用
class Order(Base):
    user = relationship("User", foreign_keys=[user_id])  # 字符串引用
    
# ❌ 禁止的跨模块导入
from app.modules import *                          # 禁止模块级星号导入
import app.modules.user_auth as user_stuff        # 避免模糊命名
```

### 循环导入预防策略
```python
# 问题场景：模块A和模块B相互依赖

# ❌ 错误：直接相互导入造成循环依赖
# file: app/modules/user_auth/service.py
from app.modules.order_management.models import Order  # 错误

# ✅ 解决方案1：使用接口或协议 (推荐)
# file: app/modules/user_auth/interfaces.py
from typing import Protocol

class OrderServiceProtocol(Protocol):
    def get_orders_by_user(self, user_id: int): ...  # 协议定义

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
from app.core.auth import get_current_user
from app.core.config import get_settings
from .service import UserService

def get_user_service(settings = Depends(get_settings)) -> UserService:
    """获取用户服务实例
    
    使用依赖注入模式创建用户服务，确保每个请求使用独立的服务实例，
    支持单元测试时的依赖替换。
    
    Args:
        settings: 应用配置，通过依赖链自动注入
        
    Returns:
        UserService: 用户服务实例
    """
    return UserService(settings)

def get_validated_entity(
    entity: BaseEntity = Depends(get_current_entity)
) -> BaseEntity:
    """获取经过验证的业务实体
    
    验证当前实体是否满足业务规则要求，不满足条件的实体将被拒绝。
    这是通用的实体验证模式，可用于用户、权限、资源等各种验证场景。
    
    Args:
        entity: 当前业务实体
        
    Returns:
        BaseEntity: 经过验证的业务实体
        
    Raises:
        HTTPException: 实体验证失败时抛出相应错误
    """
    if not entity.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="实体状态无效，访问被拒绝"
        )
    return entity

def get_privileged_entity(
    entity: BaseEntity = Depends(get_validated_entity)
) -> BaseEntity:
    """获取具有特权的业务实体
    
    验证当前实体是否具有执行特殊操作的权限。
    这是通用的权限验证模式，适用于各种权限检查场景。
    
    Args:
        entity: 当前经过验证的实体
        
    Returns:
        BaseEntity: 具有特权的业务实体
        
    Raises:
        HTTPException: 权限不足时抛出403错误
    """
    if not entity.has_privilege:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法执行此操作"
        )
    return entity
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
            
        except DatabaseError as e:
            # 数据库异常处理
            logger.error(f"Database error in create_entity: {e}")
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

class ApplicationSettings(BaseSettings):
    """应用程序配置设置"""
    
    # 应用基本配置
    APP_NAME: str = Field("ECommerce Platform", description="应用名称")
    APP_VERSION: str = Field("1.0.0", description="应用版本")
    DEBUG: bool = Field(False, description="调试模式")
    
    # 安全配置
    SECRET_KEY: str = Field("", description="应用密钥")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="访问令牌过期时间")
    
    # 外部服务配置（具体配置参见各领域标准文档）
    # 数据库配置：遵循项目结构标准中的配置管理规范
    # 缓存配置：遵循项目结构标准中的基础设施组织  
    # API配置：遵循项目结构标准中的接口层组织
    
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

测试代码应遵循与生产代码相同的质量标准，具体的测试组织、结构和质量标准请参见项目结构标准中的测试目录规范。

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

