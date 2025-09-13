# 功能模块导航

📝 **文档类型**: 模块导航  
📍 **作用**: 提供电商平台各功能模块的概括描述、结构导航和清晰索引  
🔗 **使用方法**: 快速找到目标模块，查看模块概览和文档入口

## 📂 模块目录结构

### 核心交易模块 (5个)

| 模块 | 状态 | 文档链接 | 核心功能 |
|------|------|----------|----------|
| **用户认证** | ✅ 完成 | [user-auth/](./user-auth/) | 登录注册、权限管理、JWT认证 |
| **商品管理** | ✅ 完成 | [product-catalog/](./product-catalog/) | 商品信息、分类管理、规格管理 |
| **购物车** | ✅ 完成 | [shopping-cart/](./shopping-cart/) | 购物车管理、价格计算、实时同步 |
| **订单管理** | ✅ 完成 | [order-management/](./order-management/) | 订单处理、状态流转、履约管理 |
| **支付服务** | ✅ 完成 | [payment-service/](./payment-service/) | 支付渠道、风控安全、退款处理 |

### 农产品特色模块 (2个)

| 模块 | 状态 | 文档链接 | 核心功能 |
|------|------|----------|----------|
| **批次溯源** | 🔄 开发中 | [batch-traceability/](./batch-traceability/) | 农产品溯源、批次管理、质量认证 |
| **物流管理** | 🔄 开发中 | [logistics-management/](./logistics-management/) | 冷链配送、物流跟踪、配送优化 |

### 营销会员模块 (4个)

| 模块 | 状态 | 文档链接 | 核心功能 |
|------|------|----------|----------|
| **会员系统** | 🔄 开发中 | [member-system/](./member-system/) | 会员等级、积分体系、权益管理 |
| **分销商管理** | 🔄 开发中 | [distributor-management/](./distributor-management/) | 多级分销、佣金管理、团队管理 |
| **营销活动** | 🔄 开发中 | [marketing-campaigns/](./marketing-campaigns/) | 优惠券、促销活动、营销工具 |
| **社交功能** | 🔄 开发中 | [social-features/](./social-features/) | 社交分享、拼团功能、社群营销 |

### 基础服务模块 (7个)

| 模块 | 状态 | 文档链接 | 核心功能 |
|------|------|----------|----------|
| **库存管理** | 📋 规划中 | [inventory-management/](./inventory-management/) | 库存跟踪、预占机制、补货管理 |
| **通知服务** | 📋 规划中 | [notification-service/](./notification-service/) | 多渠道通知、模板管理、智能发送 |
| **供应商管理** | 📋 规划中 | [supplier-management/](./supplier-management/) | 供应商入驻、协作管理、绩效评估 |
| **推荐系统** | 📋 规划中 | [recommendation-system/](./recommendation-system/) | 个性化推荐、智能算法、用户画像 |
| **客服系统** | 📋 规划中 | [customer-service-system/](./customer-service-system/) | 在线客服、工单管理、知识库 |
| **风控系统** | 📋 规划中 | [risk-control-system/](./risk-control-system/) | 反欺诈、风险评估、安全防护 |
| **数据分析** | 📋 规划中 | [data-analytics-platform/](./data-analytics-platform/) | 数据报表、业务分析、决策支持 |

### 技术基础设施模块 (5个)

| 模块 | 状态 | 文档链接 | 核心功能 |
|------|------|----------|----------|
| **应用核心** | ✅ 完成 | [application-core/](./application-core/) | 应用框架、配置管理、启动逻辑 |
| **数据库核心** | ✅ 完成 | [database-core/](./database-core/) | 数据库连接、事务管理、连接池 |
| **数据模型** | ✅ 完成 | [data-models/](./data-models/) | ORM基础类、模型混入、数据类型 |
| **Redis缓存** | ✅ 完成 | [redis-cache/](./redis-cache/) | 缓存策略、会话存储、分布式锁 |
| **数据库工具** | ✅ 完成 | [database-utils/](./database-utils/) | 数据库工具、迁移脚本、维护命令 |

## 📋 文档导航

### 架构文档
- [模块架构设计](../architecture/modules/) - 详细的模块分类矩阵和依赖关系
- [技术架构规范](../architecture/technical/) - 技术栈选择和架构决策
- [数据架构设计](../architecture/data/) - 数据模型设计和存储架构

### 开发文档
- [模块开发指南](../development/modules/) - 模块开发规范和最佳实践
- [API文档规范](../api/README.md) - 接口设计和文档标准
- [测试文档标准](../development/testing/) - 测试策略和用例设计

### 运维文档
- [部署配置指南](../operations/deployment/) - 环境配置和部署流程
- [监控运维手册](../operations/monitoring/) - 系统监控和故障处理