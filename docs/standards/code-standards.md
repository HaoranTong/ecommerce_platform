# 代码组织规范

此文档定义代码文件组织、模块划分、导入管理的标准。

## 目录结构标准

### FastAPI项目结构
```
app/
├── main.py              # 应用入口
├── database.py          # 数据库连接
├── auth.py             # 认证相关
├── redis_client.py     # Redis连接
├── api/                # API路由
│   ├── __init__.py
│   ├── routes.py       # 主路由
│   └── {module}_routes.py
├── models/             # 数据模型
│   ├── __init__.py
│   └── {model}.py
├── schemas/            # Pydantic模式
│   ├── __init__.py
│   └── {schema}.py
├── services/           # 业务逻辑
│   ├── __init__.py
│   └── {service}.py
└── utils/              # 工具函数
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
- 数据模型：`{model}.py` (单数形式)
- Pydantic模式：`{schema}.py`
- 服务类：`{service}.py`

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