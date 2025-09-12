# 应用程序核心代码

电商平台后端核心代码，包含API接口、数据模型、业务服务等核心功能。

## 📁 目录结构

```
app/
├── 🛣️ api/                     # API路由和接口层
│   ├── api_routes.py          # 主路由配置和汇总
│   ├── cart_routes.py         # 购物车相关API
│   ├── category_routes.py     # 商品分类API
│   ├── certificate_routes.py  # 证书管理API
│   ├── inventory_routes.py    # 库存管理API
│   ├── order_routes.py        # 订单管理API
│   ├── payment_routes.py      # 支付相关API
│   ├── product_routes.py      # 商品管理API
│   ├── user_routes.py         # 用户管理API
│   ├── test_routes.py         # 测试和调试API
│   ├── schemas.py             # API数据验证模型
│   └── __init__.py            # 模块初始化
├── 📋 schemas/                # Pydantic数据模型
│   ├── inventory.py           # 库存相关数据模型
│   └── __init__.py            # 模块初始化
├── ⚙️ services/               # 业务逻辑服务层
│   ├── inventory.py           # 库存管理业务逻辑
│   └── __init__.py            # 模块初始化
├── 🚀 main.py                 # FastAPI应用入口点
├── 🗄️ data_models.py          # SQLAlchemy数据库模型
├── 🔗 database.py             # 数据库连接和配置
├── 📊 db.py                   # 数据库会话管理
├── 🔐 auth.py                 # 用户认证和JWT处理
├── 💳 payment_auth.py         # 支付认证服务
├── 💰 payment_service.py      # 支付业务逻辑
├── 🔴 redis_client.py         # Redis客户端配置
├── __init__.py                # 包初始化文件
└── __pycache__/               # Python缓存目录
```

## 🔑 核心文件说明

| 文件 | 作用 | 依赖 |
|-----|------|------|
| **main.py** | FastAPI应用启动入口 | 所有模块 |
| **data_models.py** | 数据库表模型定义 | database.py |
| **database.py** | 数据库连接配置 | SQLAlchemy |
| **auth.py** | JWT认证和用户鉴权 | data_models.py |
| **redis_client.py** | Redis缓存客户端 | Redis |

## 🔗 相关文档

- [API接口文档](api/README.md) - API路由详细说明
- [数据模型文档](../docs/modules/data-models/) - 数据库设计
- [业务服务文档](services/README.md) - 服务层架构