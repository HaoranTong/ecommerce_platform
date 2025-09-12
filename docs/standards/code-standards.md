# 代码组织规范

此文档定义代码文件组织、模块划分、导入管理的标准。

## 目录结构标准

### FastAPI项目结构
```
app/
├── main.py              # 应用入口
├── database.py          # 数据库连接
├── db.py               # 数据库会话管理
├── auth.py             # 认证相关
├── models.py           # SQLAlchemy数据模型 (单文件)
├── redis_client.py     # Redis连接
├── payment_auth.py     # 支付认证服务
├── payment_service.py  # 支付业务逻辑
├── api/                # API路由
│   ├── __init__.py
│   ├── routes.py       # 主路由
│   └── {module}_routes.py
├── schemas/            # Pydantic模式
│   ├── __init__.py
│   └── {schema}.py
├── services/           # 业务逻辑
│   ├── __init__.py
│   └── {service}.py
└── utils/              # 工具函数 (如需要)
    ├── __init__.py
    └── {util}.py
```

## 文件命名规范

### 基础规则
- 使用小写字母+下划线：`user_routes.py`
- 避免缩写，使用完整单词
- 文件名要清晰表达功能

### 模块文件命名
- 路由文件：`{module}_routes.py`
- 数据模型：在 `models.py` 中定义类 (单数形式)
- Pydantic模式：`{schema}.py`
- 服务类：`{service}.py`

## 🚨 强制注释规范

### 文件头部注释 (必须包含)
```python
"""
文件名：user_routes.py
文件路径：app/api/user_routes.py
功能描述：用户管理相关的API路由定义
主要功能：
- 用户注册、登录、信息更新
- 用户权限验证和管理
- 用户数据的CRUD操作
使用说明：
- 导入：from app.api import user_routes
- 路由前缀：/api/v1/users
- 认证要求：部分接口需要JWT认证
依赖模块：
- app.models.User: 用户数据模型
- app.auth: 用户认证相关功能
创建时间：2025-09-12
最后修改：2025-09-12
"""
```

### 函数文档字符串 (必须包含)
```python
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    创建新用户
    
    Args:
        user_data (UserCreate): 用户创建数据，包含用户名、邮箱、密码等信息
        db (Session): 数据库会话依赖注入
        
    Returns:
        UserRead: 创建成功的用户信息（不包含密码）
        
    Raises:
        HTTPException: 
            - 400: 用户名或邮箱已存在
            - 422: 输入数据验证失败
            
    Example:
        ```python
        user_data = UserCreate(username="test", email="test@example.com", password="123456")
        new_user = create_user(user_data, db)
        ```
        
    Note:
        - 密码会自动加密存储
        - 创建时会自动设置created_at时间戳
        - 默认角色为'user'
    """
```

### 类文档字符串 (必须包含)
```python
class UserService:
    """
    用户业务逻辑服务类
    
    功能描述：
        处理用户相关的业务逻辑，包括用户创建、验证、权限管理等操作
        
    主要方法：
        - create_user(): 创建新用户
        - authenticate_user(): 用户认证
        - update_user_profile(): 更新用户资料
        
    使用方式：
        ```python
        user_service = UserService(db_session)
        user = user_service.create_user(user_data)
        ```
        
    Dependencies:
        - SQLAlchemy Session: 数据库操作
        - bcrypt: 密码加密
        - JWT: Token生成
    """
```

### 重要代码块注释 (必须包含)
```python
# ================== 用户认证验证 ==================
# 检查用户名和邮箱的唯一性，防止重复注册
existing_user = db.query(User).filter(
    or_(User.username == user_data.username, User.email == user_data.email)
).first()

if existing_user:
    # 返回具体的错误信息，帮助前端处理
    if existing_user.username == user_data.username:
        raise HTTPException(status_code=400, detail="用户名已存在")
    else:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

# ================== 密码加密处理 ==================
# 使用bcrypt进行密码加密，确保安全性
password_hash = bcrypt.hashpw(
    user_data.password.encode('utf-8'), 
    bcrypt.gensalt()
)
```

### 强制执行规则
1. **所有新建Python文件必须包含完整的文件头部注释**
2. **所有函数（包括路由处理函数）必须包含文档字符串**
3. **所有类必须包含类文档字符串**
4. **复杂逻辑代码块必须有解释性注释**
5. **代码审查时，缺少注释的代码不允许合并**

## 类和函数命名

### 类命名
- 使用帕斯卡命名法：`UserService`, `ProductModel`
- 模型类：`User`, `Product`, `Order`
- 服务类：`UserService`, `ProductService`
- 模式类：`UserCreate`, `UserRead`, `UserUpdate`

### 函数命名
- 使用小写字母+下划线：`get_user_by_id`
- API端点函数：动词+名词形式
- 服务函数：明确的业务含义

### 变量命名
- 使用小写字母+下划线：`user_id`, `product_list`
- 布尔值：`is_active`, `has_permission`
- 常量：`MAX_PAGE_SIZE`, `DEFAULT_TIMEOUT`

## 导入管理

### 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地应用导入

### 导入格式
```python
# 标准库
from typing import List, Optional
import os

# 第三方库
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# 本地导入
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead
```

## API路由组织

### 路由注册
- 所有路由在 `app/main.py` 中注册
- 使用统一的前缀：`/api`
- 按功能模块组织路由

### 路由文件结构
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="获取列表")
async def get_items():
    pass

@router.get("/{item_id}", summary="获取详情") 
async def get_item(item_id: int):
    pass

@router.post("/", summary="创建项目")
async def create_item():
    pass
```

## 依赖注入

### 数据库依赖
```python
db: Session = Depends(get_db)
```

### 认证依赖
```python
current_user: User = Depends(get_current_active_user)
current_admin: User = Depends(get_current_admin_user)
```

## 错误处理

### 异常命名
- 使用描述性名称：`UserNotFoundError`
- 继承适当的基类：`HTTPException`

### 错误响应
- 使用标准HTTP状态码
- 提供清晰的错误信息
- 包含错误代码便于调试

## 配置管理

### 环境变量
- 使用大写字母+下划线：`DATABASE_URL`
- 按功能分组：`DB_`, `REDIS_`, `AUTH_`

### 配置文件
- 集中在 `app/config.py`
- 使用Pydantic Settings
- 提供默认值和验证

## 测试文件组织

### 目录结构
```
tests/
├── __init__.py
├── conftest.py         # pytest配置
├── test_api/           # API测试
├── test_services/      # 服务测试
└── test_models/        # 模型测试
```

### 测试文件命名
- 格式：`test_{模块名}.py`
- 测试函数：`test_{功能描述}`

## 禁止行为

- 使用中文变量名或注释
- 超长的函数或类 (函数>50行, 类>200行)
- 循环导入
- 硬编码配置值
- 不一致的命名风格