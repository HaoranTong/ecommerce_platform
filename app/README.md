# 应用程序核心代码

电商平台后端核心代码，采用模块化单体架构，包含核心基础设施、共享组件、第三方适配器和业务模块。

## 📁 目录结构

```
app/
├── � core/                        # 核心基础设施
│   ├── database.py                 # 数据库连接管理
│   ├── redis_client.py             # Redis缓存客户端
│   ├── auth.py                     # 认证中间件
│   └── __init__.py                 # 核心组件导出
├── 🔄 shared/                      # 共享组件
│   ├── models.py                   # 共享数据模型
│   └── __init__.py                 # 共享组件导出
├── 🔌 adapters/                    # 第三方适配器
│   ├── payment/                    # 支付适配器（待开发）
│   ├── blockchain/                 # 区块链适配器（待开发）
│   └── ai/                         # AI服务适配器（待开发）
├── 🏢 modules/                     # 业务模块
│   ├── ✅ user_auth/               # 用户认证模块
│   ├── ✅ product_catalog/         # 商品管理模块
│   ├── ✅ shopping_cart/           # 购物车模块
│   ├── ✅ order_management/        # 订单管理模块
│   ├── ✅ payment_service/         # 支付服务模块
│   ├── � batch_traceability/      # 批次溯源模块（待开发）
│   ├── 📋 logistics_management/    # 物流管理模块（待开发）
│   ├── � member_system/           # 会员系统模块（待开发）
│   ├── � distributor_management/  # 分销商管理模块（待开发）
│   ├── 📋 marketing_campaigns/     # 营销活动模块（待开发）
│   ├── � social_features/         # 社交功能模块（待开发）
│   ├── 📋 inventory_management/    # 库存管理模块（待开发）
│   ├── � notification_service/    # 通知服务模块（待开发）
│   ├── 📋 supplier_management/     # 供应商管理模块（待开发）
│   ├── � recommendation_system/   # 推荐系统模块（待开发）
│   ├── � customer_service_system/ # 客服系统模块（待开发）
│   ├── � risk_control_system/     # 风控系统模块（待开发）
│   └── 📋 data_analytics_platform/ # 数据分析模块（待开发）
├── 🚀 main.py                      # FastAPI应用入口点
└── __init__.py                     # 包初始化文件
```

## 🔑 架构层次说明

### 🔧 核心基础设施层 (core/)
| 组件 | 作用 | 依赖 |
|-----|------|------|
| **database.py** | 数据库连接和会话管理 | SQLAlchemy |
| **redis_client.py** | Redis缓存连接管理 | Redis |
| **auth.py** | JWT认证和权限中间件 | FastAPI Security |

### 🔄 共享组件层 (shared/)
| 组件 | 作用 | 依赖 |
|-----|------|------|
| **models.py** | 跨模块共享的数据模型 | SQLAlchemy |

### 🏢 业务模块层 (modules/)
每个业务模块包含完整的垂直切片：
- **router.py** - API路由定义
- **service.py** - 业务逻辑处理
- **models.py** - 数据模型定义
- **schemas.py** - 请求/响应模型
- **dependencies.py** - 模块依赖注入

### 🔌 适配器层 (adapters/)
第三方服务集成适配器，支持可替换策略。

## 🔗 相关文档

- [API接口文档](api/README.md) - API路由详细说明
- [基础模型文档](../docs/design/modules/base-models/) - 数据库设计
- [业务服务文档](services/README.md) - 服务层架构