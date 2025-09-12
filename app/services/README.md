# 业务逻辑服务层

本目录包含电商平台的业务逻辑服务模块，负责处理核心业务逻辑，分离控制器和数据访问层。

## 📁 目录结构

```
services/
├── user_service.py        # 用户管理服务
├── product_service.py     # 商品管理服务  
├── order_service.py       # 订单管理服务
├── cart_service.py        # 购物车服务
├── payment_service.py     # 支付服务
├── category_service.py    # 分类管理服务
└── __init__.py            # 模块初始化
```

## 🔧 服务模块列表

| 服务模块 | 文件 | 状态 | 功能描述 |
|---------|------|------|----------|
| **用户服务** | `user_service.py` | ✅ 完成 | 用户注册、认证、权限管理 |
| **商品服务** | `product_service.py` | ✅ 完成 | 商品CRUD、库存管理、搜索 |
| **订单服务** | `order_service.py` | ✅ 完成 | 订单创建、状态管理、金额计算 |
| **购物车服务** | `cart_service.py` | ✅ 完成 | 购物车管理、价格计算、验证 |
| **支付服务** | `payment_service.py` | ✅ 完成 | 支付处理、状态管理、退款 |
| **分类服务** | `category_service.py` | ✅ 完成 | 分类管理、层级结构、商品统计 |

## 🏗️ 架构设计

### 服务层职责
- **业务逻辑处理**：封装复杂的业务规则和流程
- **数据验证**：验证业务数据的合法性和完整性
- **事务管理**：协调多个数据模型的事务操作
- **错误处理**：统一的业务异常处理
- **缓存管理**：业务数据的缓存策略

### 调用关系
```
Controller层 (api_routes.py)
       ↓
Service层 (services/*.py)
       ↓
Model层 (data_models.py)
```

### 使用示例

```python
from app.services import UserService, ProductService

# 用户服务
user = UserService.create_user(db, email="user@example.com", password="password")
authenticated_user = UserService.authenticate_user(db, "user@example.com", "password")

# 商品服务
products = ProductService.get_products(db, category_id=1, skip=0, limit=10)
product = ProductService.create_product(db, product_data)
```

## 📋 开发规范

### 文件命名
- 服务文件：`{模块}_service.py`
- 类命名：`{模块}Service`
- 方法命名：动词+名词，如 `create_user`、`get_products`

### 方法设计
- 静态方法：所有业务方法都是静态方法
- 参数顺序：`db: Session` 总是第一个参数
- 返回类型：明确的类型注解
- 异常处理：使用 `HTTPException` 抛出业务异常

### 错误处理
```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="用户不存在"
    )
```

## 🔄 状态管理

各服务模块都包含完整的状态管理机制：
- **用户状态**：active, inactive, banned
- **商品状态**：active, inactive, out_of_stock
- **订单状态**：pending, paid, shipped, delivered, cancelled
- **支付状态**：pending, processing, completed, failed, refunded

## 🚀 扩展指南

添加新服务模块的步骤：
1. 创建 `{模块}_service.py` 文件
2. 实现 `{模块}Service` 类
3. 在 `__init__.py` 中导出新服务
4. 更新本README文档
5. 编写单元测试

## 🔗 相关文档

- [API路由](../api/README.md) - 调用这些服务的API
- [数据模型](../data_models.py) - 服务操作的数据模型