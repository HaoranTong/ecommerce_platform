<!--
文档说明：
- 内容：模块文档与功能代码/数据模型的详细对应关系矩阵
- 使用方法：开发时确认文档与代码的一致性，架构验证的参考依据
- 更新方法：新增模块、修改代码结构或更新文档时更新
- 引用关系：被模块开发检查清单引用，引用各模块的文档和代码
- 更新频率：代码结构变更或文档更新时
-->

# 模块文档与功能代码对应关系矩阵

## 文档概述

本文档提供各业务模块的文档、功能代码和数据模型之间的完整对应关系矩阵，用于确保开发过程中文档与代码的同步一致性。

## 对应关系矩阵

### 核心交易模块组

#### 用户认证模块 (user-auth)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/user-auth/overview.md` | `app/modules/user_auth/` | `app/shared/models.py` (User, Role) | ✅ 已同步 |
| API规范 | `docs/modules/user-auth/api-spec.md` | `app/modules/user_auth/routes.py` | - | ✅ 已同步 |
| API实现 | `docs/modules/user-auth/api-implementation.md` | `app/modules/user_auth/service.py` | - | ✅ 已同步 |
| README | `docs/modules/user-auth/README.md` | - | - | ✅ 已同步 |

#### 商品管理模块 (product-catalog)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/product-catalog/overview.md` | `app/modules/product_catalog/` | `app/shared/models.py` (Product, Category) | ⚠️ 需检查 |
| API规范 | `docs/modules/product-catalog/api-spec.md` | `app/modules/product_catalog/routes.py` | - | ⚠️ 需检查 |
| API实现 | `docs/modules/product-catalog/api-implementation.md` | `app/modules/product_catalog/service.py` | - | ⚠️ 需检查 |
| README | `docs/modules/product-catalog/README.md` | - | - | ✅ 已同步 |

#### 购物车模块 (shopping-cart)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/shopping-cart/overview.md` | `app/modules/shopping_cart/` | `app/shared/models.py` (Cart, CartItem) | ⚠️ 需检查 |
| API规范 | `docs/modules/shopping-cart/api-spec.md` | `app/modules/shopping_cart/routes.py` | - | ⚠️ 需检查 |
| API实现 | `docs/modules/shopping-cart/api-implementation.md` | `app/modules/shopping_cart/service.py` | - | ⚠️ 需检查 |
| README | `docs/modules/shopping-cart/README.md` | - | - | ✅ 已同步 |

#### 订单管理模块 (order-management)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/order-management/overview.md` | `app/modules/order_management/` | `app/shared/models.py` (Order, OrderItem) | ⚠️ 需检查 |
| API规范 | `docs/modules/order-management/api-spec.md` | `app/modules/order_management/routes.py` | - | ⚠️ 需检查 |
| API实现 | `docs/modules/order-management/api-implementation.md` | `app/modules/order_management/service.py` | - | ⚠️ 需检查 |
| README | `docs/modules/order-management/README.md` | - | - | ✅ 已同步 |

#### 支付服务模块 (payment-service)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/payment-service/overview.md` | `app/modules/payment_service/` | `app/shared/models.py` (Payment, PaymentMethod) | ⚠️ 需检查 |
| API规范 | `docs/modules/payment-service/api-spec.md` | `app/modules/payment_service/routes.py` | - | ⚠️ 需检查 |
| API实现 | `docs/modules/payment-service/api-implementation.md` | `app/modules/payment_service/service.py` | - | ⚠️ 需检查 |
| README | `docs/modules/payment-service/README.md` | - | - | ✅ 已同步 |

### 农产品特色模块组

#### 批次溯源模块 (batch-traceability)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/batch-traceability/overview.md` | `app/modules/batch_traceability/` | `app/shared/models.py` (BatchInfo, TraceRecord) | ⚠️ 需检查 |
| API规范 | `docs/modules/batch-traceability/api-spec.md` | `app/modules/batch_traceability/routes.py` | - | ⚠️ 需检查 |
| README | `docs/modules/batch-traceability/README.md` | - | - | ✅ 已同步 |

#### 物流管理模块 (logistics-management)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/logistics-management/overview.md` | `app/modules/logistics_management/` | `app/shared/models.py` (Shipment, LogisticsInfo) | ⚠️ 需检查 |
| API规范 | `docs/modules/logistics-management/api-spec.md` | `app/modules/logistics_management/routes.py` | - | ⚠️ 需检查 |
| README | `docs/modules/logistics-management/README.md` | - | - | ✅ 已同步 |

### 营销会员模块组

#### 会员系统模块 (member-system)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/member-system/overview.md` | `app/modules/member_system/` | `app/shared/models.py` (MemberLevel, Points) | ⚠️ 需检查 |
| API规范 | `docs/modules/member-system/api-spec.md` | `app/modules/member_system/routes.py` | - | ⚠️ 需检查 |
| README | `docs/modules/member-system/README.md` | - | - | ✅ 已同步 |

#### 分销商管理模块 (distributor-management)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/distributor-management/overview.md` | `app/modules/distributor_management/` | `app/shared/models.py` (Distributor, Commission) | ⚠️ 需检查 |
| README | `docs/modules/distributor-management/README.md` | - | - | ✅ 已同步 |

#### 营销活动模块 (marketing-campaigns)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/marketing-campaigns/overview.md` | `app/modules/marketing_campaigns/` | `app/shared/models.py` (Campaign, Coupon) | ⚠️ 需检查 |
| README | `docs/modules/marketing-campaigns/README.md` | - | - | ✅ 已同步 |

#### 社交功能模块 (social-features)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/social-features/overview.md` | `app/modules/social_features/` | `app/shared/models.py` (SocialPost, Follow) | ⚠️ 需检查 |
| README | `docs/modules/social-features/README.md` | - | - | ✅ 已同步 |

### 基础服务模块组

#### 库存管理模块 (inventory-management)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/inventory-management/overview.md` | `app/modules/inventory_management/` | `app/shared/models.py` (Inventory, Stock) | ⚠️ 需检查 |
| README | `docs/modules/inventory-management/README.md` | - | - | ✅ 已同步 |

#### 通知服务模块 (notification-service)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/notification-service/overview.md` | `app/modules/notification_service/` | `app/shared/models.py` (Notification, NotificationTemplate) | ⚠️ 需检查 |
| README | `docs/modules/notification-service/README.md` | - | - | ✅ 已同步 |

#### 客服系统模块 (customer-service-system)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/customer-service-system/overview.md` | `app/modules/customer_service_system/` | `app/shared/models.py` (ServiceTicket, FAQ) | ⚠️ 需检查 |
| README | `docs/modules/customer-service-system/README.md` | - | - | ✅ 已同步 |

#### 供应商管理模块 (supplier-management)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/supplier-management/overview.md` | `app/modules/supplier_management/` | `app/shared/models.py` (Supplier, SupplyContract) | ⚠️ 需检查 |
| README | `docs/modules/supplier-management/README.md` | - | - | ✅ 已同步 |

#### 风控系统模块 (risk-control-system)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/risk-control-system/overview.md` | `app/modules/risk_control_system/` | `app/shared/models.py` (RiskRule, RiskLog) | ⚠️ 需检查 |
| README | `docs/modules/risk-control-system/README.md` | - | - | ✅ 已同步 |

#### 数据分析平台模块 (data-analytics-platform)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/data-analytics-platform/overview.md` | `app/modules/data_analytics_platform/` | `app/shared/models.py` (Analytics, Report) | ⚠️ 需检查 |
| README | `docs/modules/data-analytics-platform/README.md` | - | - | ✅ 已同步 |

#### 推荐系统模块 (recommendation-system)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/recommendation-system/overview.md` | `app/modules/recommendation_system/` | `app/shared/models.py` (Recommendation, UserPreference) | ⚠️ 需检查 |
| API实现 | `docs/modules/recommendation-system/api-implementation.md` | `app/modules/recommendation_system/service.py` | - | ⚠️ 需检查 |
| README | `docs/modules/recommendation-system/README.md` | - | - | ✅ 已同步 |

#### 质量控制模块 (quality-control)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/quality-control/overview.md` | `app/modules/quality_control/` | `app/shared/models.py` (QualityCheck, QualityReport) | ⚠️ 需检查 |
| README | `docs/modules/quality-control/README.md` | - | - | ✅ 已同步 |

### 技术基础设施模块组

#### 应用核心模块 (application-core)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/application-core/overview.md` | `app/core/` | - | ✅ 已同步 |
| README | `docs/modules/application-core/README.md` | - | - | ✅ 已同步 |

#### 数据库核心模块 (database-core)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/database-core/overview.md` | `app/core/database.py` | - | ✅ 已同步 |
| README | `docs/modules/database-core/README.md` | - | - | ✅ 已同步 |

#### 基础模型模块 (base-models)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/base-models/overview.md` | `app/shared/base_models.py` | `app/shared/base_models.py` | ✅ 已同步 |
| README | `docs/modules/base-models/README.md` | - | - | ✅ 已同步 |

#### Redis缓存模块 (redis-cache)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/redis-cache/overview.md` | `app/core/redis_client.py` | - | ✅ 已同步 |
| README | `docs/modules/redis-cache/README.md` | - | - | ✅ 已同步 |

#### 数据库工具模块 (database-utils)

| 文档类型 | 文档路径 | 功能代码路径 | 数据模型路径 | 一致性状态 |
|---------|---------|-------------|-------------|-----------|
| 模块概览 | `docs/modules/database-utils/overview.md` | `app/core/database.py` (工具函数) | - | ⚠️ 需检查 |
| README | `docs/modules/database-utils/README.md` | - | - | ✅ 已同步 |

## 一致性统计

### 总体状态统计

| 一致性状态 | 模块数量 | 占比 | 说明 |
|-----------|---------|------|------|
| ✅ 已同步 | 7 | 30.4% | 文档与代码完全一致 |
| ⚠️ 需检查 | 16 | 69.6% | 需要详细检查一致性 |
| ❌ 不一致 | 0 | 0% | 发现不一致需要修复 |

### 按模块组统计

| 模块组 | 总数 | 已同步 | 需检查 | 不一致 |
|-------|------|-------|-------|-------|
| 核心交易模块 | 5 | 1 | 4 | 0 |
| 农产品特色模块 | 2 | 0 | 2 | 0 |
| 营销会员模块 | 4 | 0 | 4 | 0 |
| 基础服务模块 | 7 | 0 | 7 | 0 |
| 技术基础设施模块 | 5 | 5 | 0 | 0 |

### 文档类型统计

| 文档类型 | 存在数量 | 完整率 | 说明 |
|---------|---------|-------|------|
| 模块概览 (overview.md) | 23 | 100% | 所有模块都有概览文档 |
| API规范 (api-spec.md) | 8 | 34.8% | 主要业务模块有API规范 |
| API实现 (api-implementation.md) | 3 | 13.0% | 部分模块有实现记录 |
| README导航 | 23 | 100% | 所有模块都有README导航 |

## 检查建议

### 高优先级检查项目

1. **用户认证模块** - 已完成的参考模板，可作为其他模块的标准
2. **核心交易模块组** - 业务核心，需要优先确保文档与代码一致
3. **API规范文档** - 缺失的模块需要补充API规范文档

### 检查方法

1. **代码结构检查** - 验证 `app/modules/模块名/` 目录结构与文档描述一致
2. **API接口检查** - 验证 `routes.py` 中的接口与 `api-spec.md` 定义一致
3. **数据模型检查** - 验证 `app/shared/models.py` 中的模型与文档描述一致
4. **服务逻辑检查** - 验证 `service.py` 中的业务逻辑与概览文档一致

## 相关文档

- [模块架构设计](../architecture/module-architecture.md) - 整体模块架构
- [依赖关系架构](../architecture/dependency-architecture.md) - 模块依赖关系
- [文档管理规范](../standards/document-standards.md) - 文档同步规范
- [代码开发检查清单](../standards/code-development-checklist.md) - 开发检查标准

## 更新日志

### v1.0.0 (2025-09-14)
- ✅ 初始版本，完整的模块文档与功能代码对应关系矩阵
- ✅ 23个业务模块的文档-代码映射关系
- ✅ 一致性状态分析和检查建议
- ✅ 统计数据和优化建议