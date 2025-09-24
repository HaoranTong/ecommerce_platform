<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,project-structure-standards.md-->

# 技术栈标准规范

## 概述

本文档基于 [技术架构总览](../architecture/overview.md) 的选型原则，规范电商平台项目的具体技术栈版本要求和配置标准。确保技术选择的一致性和兼容性。

## 依赖标准

本标准依赖以下L1核心标准：

- **[项目结构标准](./project-structure-standards.md)** - 定义技术组件的目录结构规范
- **[命名规范](./naming-conventions-standards.md)** - 技术组件和配置文件的命名规则

## 具体标准

### 强制技术栈要求

### Python环境标准
- **Python版本**: 3.11+ (强制，禁止使用3.10以下版本)
- **虚拟环境**: 必须使用独立虚拟环境，禁止全局安装
- **依赖管理**: requirements.txt + pip，版本锁定

### Web框架标准
- **FastAPI**: 0.100+ (强制，禁止使用其他框架)
- **异步支持**: 必须使用async/await模式
- **自动文档**: 强制启用OpenAPI文档生成

### 数据层技术标准
- **ORM框架**: SQLAlchemy 2.0+ (强制，禁止使用1.x版本)
- **数据库**: MySQL 8.0+ (生产环境强制)
- **测试数据库**: SQLite 3.35+ (测试环境强制)
- **数据验证**: Pydantic V2 (2.0+) (强制，禁止使用V1)

### 缓存技术标准
- **Redis**: 7.0+ (强制)
- **连接库**: redis-py 4.0+ (async支持)

### 安全技术标准
- **认证**: JWT (PyJWT 2.0+)
- **密码哈希**: bcrypt (强制)
- **HTTPS**: TLS 1.3+ (生产环境强制)

### 测试技术标准
- **测试框架**: pytest 7.0+ (强制)
- **Mock库**: pytest-mock (强制，禁止unittest.mock)
- **HTTP测试**: httpx + TestClient (FastAPI测试专用)
- **数据库测试**: pytest-asyncio (异步测试支持)

### 开发工具标准
- **代码格式**: black (强制)
- **类型检查**: mypy (推荐)
- **导入排序**: isort (推荐)

## 版本兼容性矩阵

| 技术组件 | 最低版本 | 推荐版本 | 禁止版本 | 升级策略 |
|---------|---------|---------|---------|---------|
| **Python** | 3.11.0 | 3.11.x | < 3.11 | 跟随稳定版 |
| **FastAPI** | 0.100.0 | 最新稳定版 | < 0.100 | 定期升级 |
| **SQLAlchemy** | 2.0.0 | 2.0.x | 1.x 全系列 | 禁止降级 |
| **Pydantic** | 2.0.0 | 2.x.x | 1.x 全系列 | 禁止降级 |
| **Redis** | 7.0.0 | 7.0.x | < 7.0 | 跟随稳定版 |
| **MySQL** | 8.0.0 | 8.0.x | < 8.0 | 谨慎升级 |

## 环境配置标准

### 开发环境配置
```bash
# 1. Python环境检查
python --version  # 必须 >= 3.11

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate.ps1  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 环境变量配置
cp .env.example .env  # 复制环境变量模板
```

### 依赖版本锁定
```txt
# requirements.txt 必须包含版本锁定
fastapi>=0.100.0,<1.0.0
sqlalchemy>=2.0.0,<3.0.0
pydantic>=2.0.0,<3.0.0
redis>=4.0.0,<5.0.0
pytest>=7.0.0,<8.0.0
pytest-mock>=3.10.0
```

## 标准配置方案

### FastAPI应用配置（强制）
```python
# app/main.py - 统一FastAPI应用配置
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="农产品电商平台API",
    description="高品质农产品电商平台API服务",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置（强制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SQLAlchemy数据库配置（强制）
```python
# app/core/database.py - 统一数据库配置
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+aiomysql://user:password@localhost/ecommerce"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # 连接池大小（强制）
    max_overflow=30,        # 最大溢出连接（强制）
    pool_pre_ping=True,     # 连接验证（强制）
    pool_recycle=3600,      # 连接回收时间（强制）
    echo=False              # 生产环境禁止SQL日志
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)
```

### Redis缓存配置（强制）
```python
# app/core/redis_client.py - 统一Redis配置
import redis.asyncio as redis

redis_client = redis.from_url(
    "redis://localhost:6379/0",
    encoding="utf-8",
    decode_responses=True,
    max_connections=100,        # 最大连接数（强制）
    retry_on_timeout=True,      # 超时重试（强制）
    socket_timeout=5.0,         # 套接字超时（强制）
    socket_connect_timeout=5.0   # 连接超时（强制）
)
```

## Pydantic V2强制标准

### 配置语法（强制）
```python
# ✅ 正确：Pydantic V2语法
from pydantic import BaseModel, ConfigDict

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
# ❌ 禁止：Pydantic V1语法
class UserModel(BaseModel):
    class Config:  # 禁止使用
        from_attributes = True
```

### 验证器语法（强制）
```python
# ✅ 正确：Pydantic V2语法
from pydantic import field_validator, model_validator

@field_validator('field_name')
@classmethod
def validate_field(cls, v: str) -> str:
    return v

@model_validator(mode='before')
@classmethod
def validate_model(cls, data: Any) -> Any:
    return data

# ❌ 禁止：Pydantic V1语法
@validator('field_name')  # 禁止使用
def validate_field(cls, v):
    return v
```

### 类型注解（强制）
```python
# ✅ 正确：明确类型注解
from typing import Optional, List
from pydantic import BaseModel

class ProductSchema(BaseModel):
    id: int
    name: str
    price: float
    tags: List[str]
    description: Optional[str] = None

# ❌ 禁止：缺少类型注解
class ProductSchema(BaseModel):
    id = None  # 禁止
    name = ""  # 禁止
```

## 违规检测机制

### 自动化检查
- **CI/CD检查**: 部署时自动验证技术栈版本
- **依赖扫描**: 定期扫描项目依赖版本合规性
- **代码检查**: 通过pre-commit hook检查代码规范

### 违规处理
- **P0级违规**: 使用禁止版本 → 立即停止部署，强制升级
- **P1级违规**: 版本过低 → 计划升级，设定截止时间
- **P2级违规**: 版本偏新 → 评估风险，谨慎升级

## 迁移指导

### 从旧版本迁移
1. **Pydantic V1 → V2**: 
   - 替换Config类为model_config
   - 更新validator为field_validator
   - 测试所有数据模型

2. **SQLAlchemy 1.x → 2.0**:
   - 更新查询语法为2.0风格
   - 替换session用法
   - 更新异步支持

### 迁移验证
- **单元测试**: 确保所有测试通过
- **集成测试**: 验证系统集成功能
- **性能测试**: 确认性能无回归

---

**相关文档**:
- [技术架构总览](../architecture/overview.md) - 技术选型原则和决策依据
- [开发环境配置](../operations/development-setup.md) - 环境搭建指南
- [项目结构标准](project-structure-standards.md) - 代码组织规范
