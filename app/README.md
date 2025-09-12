# 应用程序核心代码

电商平台后端核心代码，包含API接口、数据模型、业务服务等核心功能。

## 📁 目录结构

```
app/
├── api/                    # API路由和接口
│   ├── __init__.py
│   └── routes.py          # 主要API路由定义
├── schemas/               # Pydantic数据模型
│   └── __init__.py
├── services/              # 业务逻辑服务
│   └── __init__.py
├── auth.py               # 用户认证和JWT处理
├── database.py           # 数据库连接和配置
├── db.py                 # 数据库会话管理
├── main.py               # FastAPI应用入口
├── models.py             # SQLAlchemy数据模型
├── payment_auth.py       # 支付认证服务
├── payment_service.py    # 支付业务逻辑
├── redis_client.py       # Redis客户端配置
└── __init__.py           # 包初始化文件
```

## 🔑 核心文件说明

| 文件 | 作用 | 依赖 |
|-----|------|------|
| **main.py** | FastAPI应用启动入口 | 所有模块 |
| **models.py** | 数据库表模型定义 | database.py |
| **database.py** | 数据库连接配置 | SQLAlchemy |
| **auth.py** | JWT认证和用户鉴权 | models.py |
| **redis_client.py** | Redis缓存客户端 | Redis |

## 🔗 相关文档

- [API接口文档](api/README.md) - API路由详细说明
- [数据模型文档](../docs/modules/data-models/) - 数据库设计
- [业务服务文档](services/README.md) - 服务层架构