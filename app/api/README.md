# API路由模块

FastAPI路由定义，包含所有API端点的路由配置和处理逻辑。

## 📁 目录结构

```
api/
├── api_routes.py          # 主路由配置和汇总
├── cart_routes.py         # 购物车相关API
├── category_routes.py     # 商品分类API
├── certificate_routes.py  # 证书管理API
├── inventory_routes.py    # 库存管理API
├── order_routes.py        # 订单管理API
├── payment_routes.py      # 支付相关API
├── product_routes.py      # 商品管理API
├── user_routes.py         # 用户管理API
├── test_routes.py         # 测试和调试API
├── schemas.py             # API数据验证模型
└── __init__.py            # 模块初始化
```

## 🛣️ 路由说明

| 路由文件 | 路径前缀 | 主要功能 |
|---------|---------|---------|
| **cart_routes.py** | `/cart` | 购物车增删改查、价格计算 |
| **product_routes.py** | `/products` | 商品信息管理、搜索、分页 |
| **order_routes.py** | `/orders` | 订单创建、状态更新、查询 |
| **user_routes.py** | `/users` | 用户注册、登录、信息管理 |
| **payment_routes.py** | `/payment` | 支付处理、回调、查询 |
| **inventory_routes.py** | `/inventory` | 库存查询、更新、预占 |
| **category_routes.py** | `/categories` | 商品分类管理 |
| **certificate_routes.py** | `/certificates` | 证书和溯源管理 |

## 🔗 相关文档

- [API规范文档](../../docs/api/) - 完整API文档
- [数据模型](../schemas/README.md) - 请求响应模型