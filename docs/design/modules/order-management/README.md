<!--
文档说明：
- 内容：订单管理模块README导航文档
- 作用：提供快速导航和基本信息
- 使用方法：模块文档的入口，简洁明了
- 符合标准：A3标准（模块导航文档）
-->

# 订单管理模块 (Order Management)

📋 **状态**: ✅ 已完成  
📅 **创建日期**: 2025-09-16  
👤 **负责人**: 架构团队  
🔄 **最后更新**: 2025-10-14  
📦 **业务域**: 交易域 (Transaction Domain)  

## 快速导航

| 文档类型 | 文档名称 | 描述 |
|---------|----------|------|
| **概述** | [overview.md](./overview.md) | 模块详细概述和技术架构 |
| **需求** | [requirements.md](./requirements.md) | 业务需求和功能规格 |
| **设计** | [design.md](./design.md) | 技术设计和架构决策 |
| **API规范** | [api-spec.md](./api-spec.md) | API接口规范定义 |
| **API实施** | [api-implementation.md](./api-implementation.md) | API开发实施记录 |
| **实现** | [implementation.md](./implementation.md) | 开发实现详细记录 |

## 模块简介

订单管理模块负责电商平台的订单全生命周期管理，从订单创建、状态流转到订单查询和修改，提供完整的订单业务能力。采用状态机模式管理订单状态，通过商品快照机制实现与商品模块的解耦。

### 核心功能
- **订单创建**: 从购物车生成订单，保存商品价格快照
- **状态管理**: 订单状态机管理（待支付→已支付→已发货→已送达）
- **订单查询**: 订单列表、详情查询，支持分页和搜索
- **订单修改**: 地址修改（限定状态）、订单取消
- **商品快照**: 保存订单商品信息，历史不可变
- **状态审计**: 订单状态变更历史记录

### 技术栈
- **后端框架**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **数据验证**: Pydantic 2.5.0
- **数据库**: MySQL 8.0
- **缓存**: Redis 7.0（订单缓存）
- **认证**: JWT Token + RBAC权限控制

## 快速开始

### API端点
- **基础路径**: `/api/v1/order-management/`
- **认证方式**: JWT Bearer Token
- **主要接口**: 
  - POST `/orders` - 创建订单
  - GET `/orders` - 订单列表
  - GET `/orders/{order_id}` - 订单详情
  - PUT `/orders/{order_id}` - 更新订单
  - DELETE `/orders/{order_id}` - 取消订单
- **完整规范**: 详见 [api-spec.md](./api-spec.md)

### 数据模型
- **核心表**: 
  - `orders` - 订单主表
  - `order_items` - 订单商品明细表
  - `order_status_history` - 订单状态历史表
- **数据关系**: 详见 [overview.md](./overview.md#数据模型)

### 模块结构
```
app/modules/order_management/
├── __init__.py          # 模块初始化
├── models.py            # 数据模型（Order, OrderItem, OrderStatusHistory）
├── schemas.py           # Pydantic DTO（请求/响应模型）
├── service.py           # 业务逻辑（状态机、快照管理）
├── router.py            # API路由定义
└── dependencies.py      # 依赖注入和权限控制
```

## 模块边界

### 包含功能
- ✅ 订单创建和商品快照
- ✅ 订单状态机管理
- ✅ 订单查询和搜索
- ✅ 订单修改（限定条件）
- ✅ 订单状态历史记录

### 排除功能
- ❌ 支付处理 → 由 `payment-service` 模块负责
- ❌ 库存扣减 → 由 `inventory-management` 模块负责
- ❌ 物流配送 → 由 `logistics-management` 模块负责
- ❌ 订单评价 → 由独立评价模块负责
- ❌ 优惠券使用 → 由 `marketing-campaigns` 模块负责

### 依赖关系
- **依赖模块**: user_auth, product_catalog, shopping_cart, inventory_management, payment_service
- **被依赖**: payment_service, logistics_management, member_system, data_analytics_platform
- **详细说明**: 详见 [overview.md](./overview.md#模块边界)

## 相关链接

### 架构文档
- [系统架构概览](../../architecture/overview.md)
- [业务架构设计](../../architecture/business-architecture.md)
- [应用架构设计](../../architecture/application-architecture.md)

### 标准规范
- [API设计标准](../../standards/api-standards.md)
- [数据库设计标准](../../standards/database-standards.md)
- [命名规范标准](../../standards/naming-conventions-standards.md)
- [代码开发规范](../../standards/code-standards.md)

### 相关模块
- [用户认证模块](../user-auth/README.md)
- [商品目录模块](../product-catalog/README.md)
- [购物车模块](../shopping-cart/README.md)
- [支付服务模块](../payment-service/README.md)
