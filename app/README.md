# 应用程序核心代码

电商平台后端核心代码，采用模块化单体架构，包含核心基础设施、共享组件、第三方适配器和业务模块。

## 📁 目录结构

```
app/
├── core/                        # 核心基础设施
│   ├── async_utils.py           # 异步工具函数
│   ├── auth.py                  # 认证中间件
│   ├── database.py              # 数据库连接管理
│   ├── exceptions.py            # 自定义异常
│   ├── model_discovery.py       # 模型发现工具
│   ├── redis_client.py          # Redis缓存客户端
│   ├── security_logger.py       # 安全日志
│   ├── verification.py          # 验证工具
│   └── __init__.py              # 核心组件导出
├── shared/                      # 共享组件
│   ├── api_schemas.py           # API公共模型
│   ├── base_models.py           # 基础模型
│   ├── response.py              # 响应处理
│   └── __init__.py              # 共享组件导出
├── adapters/                    # 第三方适配器
│   ├── payment/                 # 支付适配器
│   └── __init__.py              # 适配器导出
├── modules/                     # 业务模块
│   ├── user_auth/               # 用户认证模块
│   ├── product_catalog/         # 商品管理模块
│   ├── shopping_cart/           # 购物车模块
│   ├── order_management/        # 订单管理模块
│   ├── payment_service/         # 支付服务模块
│   ├── batch_traceability/      # 批次溯源模块
│   ├── customer_service_system/ # 客服系统模块
│   ├── data_analytics_platform/ # 数据分析模块
│   ├── distributor_management/  # 分销商管理模块
│   ├── inventory_management/    # 库存管理模块
│   ├── logistics_management/    # 物流管理模块
│   ├── marketing_campaigns/     # 营销活动模块
│   ├── member_system/           # 会员系统模块
│   ├── notification_service/    # 通知服务模块
│   ├── quality_control/         # 质量控制模块
│   ├── recommendation_system/  # 推荐系统模块
│   ├── risk_control_system/     # 风控系统模块
│   ├── social_features/         # 社交功能模块
│   ├── supplier_management/     # 供应商管理模块
│   └── __init__.py              # 模块初始化
├── frontend/                    # 前端代码
├── main.py                      # FastAPI应用入口点
└── __init__.py                  # 包初始化文件
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
| **api_schemas.py** | 跨模块共享的API模型 | Pydantic |
| **base_models.py** | 基础模型定义 | SQLAlchemy |
| **response.py** | 统一响应处理 | FastAPI |

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

- [API接口文档](../docs/api/) - API路由详细说明
- [基础模型文档](../docs/design/base-models/) - 数据库设计
- [业务服务文档](../docs/services/) - 服务层架构