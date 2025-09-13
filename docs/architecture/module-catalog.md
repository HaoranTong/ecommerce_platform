<!--
文档说明：
- 内容：模块详细目录清单，每个模块的功能说明和当前状态
- 使用方法：模块查找和状态跟踪的参考手册，开发规划依据
- 更新方法：模块新增或状态变更时更新
- 引用关系：被README.md引用，引用各模块的overview.md
- 更新频率：每个开发周期或里程碑完成时
-->

# 模块详细目录

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-13  
👤 **负责人**: 系统架构师  
🔄 **最后更新**: 2025-09-13  
📋 **版本**: v1.0.0  

## 快速导航

- [核心交易模块](#核心交易模块-5个) - 电商平台基础功能
- [农产品特色模块](#农产品特色模块-2个) - 行业差异化功能  
- [营销会员模块](#营销会员模块-4个) - 用户运营功能
- [基础服务模块](#基础服务模块-7个) - 平台支撑功能
- [技术基础设施模块](#技术基础设施模块-5个) - 技术基础能力

## 核心交易模块 (5个)

> 电商平台的核心交易流程模块，提供用户、商品、订单、支付等基础功能

### [用户认证模块](../modules/user-auth/)
- **功能**: 用户注册、登录、权限管理、会话控制
- **技术**: JWT认证、RBAC权限、密码安全策略
- **状态**: ✅ 已完成
- **API文档**: [用户认证API](../modules/user-auth/api-spec.md)

### [商品管理模块](../modules/product-catalog/)
- **功能**: 商品信息管理、分类体系、库存同步、价格策略
- **技术**: 商品数据模型、分类树结构、价格计算引擎
- **状态**: ✅ 已完成  
- **API文档**: [商品管理API](../modules/product-catalog/api-spec.md)

### [购物车模块](../modules/shopping-cart/)
- **功能**: 购物车操作、价格计算、优惠券应用、库存校验
- **技术**: Redis会话存储、价格计算算法、优惠券引擎
- **状态**: ✅ 已完成
- **API文档**: [购物车API](../modules/shopping-cart/api-spec.md)

### [订单管理模块](../modules/order-management/)
- **功能**: 订单创建、状态流转、订单查询、退款处理
- **技术**: 订单状态机、工作流引擎、事务处理
- **状态**: ✅ 已完成
- **API文档**: [订单管理API](../modules/order-management/api-spec.md)

### [支付服务模块](../modules/payment-service/)
- **功能**: 支付渠道集成、支付流程控制、对账管理、风控检测
- **技术**: 第三方支付SDK、支付状态机、对账算法
- **状态**: ✅ 已完成
- **API文档**: [支付服务API](../modules/payment-service/api-spec.md)

## 农产品特色模块 (2个)

> 农产品电商的行业特色功能，提供溯源和冷链配送能力

### [批次溯源模块](../modules/batch-traceability/)
- **功能**: 农产品溯源信息管理、批次跟踪、质量检测记录、溯源码生成
- **技术**: 区块链溯源、二维码生成、质量数据采集
- **状态**: 🔄 开发中
- **文档**: [溯源模块概览](../modules/batch-traceability/overview.md)

### [物流管理模块](../modules/logistics-management/)
- **功能**: 冷链配送管理、物流跟踪、配送路径优化、温度监控
- **技术**: GPS定位、温控传感器、路径算法、物流API集成
- **状态**: 🔄 开发中  
- **文档**: [物流模块概览](../modules/logistics-management/overview.md)

## 营销会员模块 (4个)

> 用户运营和营销推广功能，提升用户粘性和平台GMV

### [会员系统模块](../modules/member-system/)
- **功能**: 会员等级管理、积分体系、会员权益、成长体系
- **技术**: 积分算法、等级计算、权益配置、成长任务
- **状态**: 🔄 开发中
- **文档**: [会员系统概览](../modules/member-system/overview.md)

### [分销商管理模块](../modules/distributor-management/)
- **功能**: 多级分销体系、佣金计算、分销商管理、分销数据统计
- **技术**: 分销关系树、佣金算法、业绩统计、结算系统
- **状态**: 🔄 开发中
- **文档**: [分销管理概览](../modules/distributor-management/overview.md)

### [营销活动模块](../modules/marketing-campaigns/)
- **功能**: 优惠券管理、促销活动、限时抢购、满减策略
- **技术**: 优惠券引擎、活动配置、库存限制、并发控制
- **状态**: 🔄 开发中
- **文档**: [营销活动概览](../modules/marketing-campaigns/overview.md)

### [社交功能模块](../modules/social-features/)
- **功能**: 社交分享、拼团购买、用户评价、内容推荐
- **技术**: 社交API、拼团算法、评价系统、内容算法
- **状态**: 🔄 开发中
- **文档**: [社交功能概览](../modules/social-features/overview.md)

## 基础服务模块 (7个)

> 为业务模块提供支撑服务，包括运营、风控、数据等能力

### [库存管理模块](../modules/inventory-management/)
- **功能**: 库存监控、自动补货、库存预警、多仓管理
- **技术**: 库存算法、预警机制、补货策略、仓储集成
- **状态**: 📝 规划中
- **文档**: [库存管理概览](../modules/inventory-management/overview.md)

### [通知服务模块](../modules/notification-service/)
- **功能**: 短信通知、邮件推送、站内消息、推送服务
- **技术**: 消息队列、多渠道API、模板引擎、推送优化
- **状态**: 📝 规划中
- **文档**: [通知服务概览](../modules/notification-service/overview.md)

### [客服系统模块](../modules/customer-service-system/)
- **功能**: 在线客服、工单系统、知识库、智能机器人
- **技术**: WebSocket、工单流程、搜索引擎、AI对话
- **状态**: 📝 规划中
- **文档**: [客服系统概览](../modules/customer-service-system/overview.md)

### [供应商管理模块](../modules/supplier-management/)
- **功能**: 供应商入驻、资质管理、采购协作、结算管理
- **技术**: 供应商门户、资质验证、采购流程、财务集成
- **状态**: 📝 规划中
- **文档**: [供应商管理概览](../modules/supplier-management/overview.md)

### [风控系统模块](../modules/risk-control-system/)
- **功能**: 交易风控、反欺诈检测、风险评估、黑名单管理
- **技术**: 风控规则引擎、机器学习、实时决策、风险评分
- **状态**: 📝 规划中
- **文档**: [风控系统概览](../modules/risk-control-system/overview.md)

### [数据分析平台模块](../modules/data-analytics-platform/)
- **功能**: 业务数据分析、用户行为分析、经营报表、数据大屏
- **技术**: 数据仓库、OLAP分析、可视化图表、实时计算
- **状态**: 📝 规划中
- **文档**: [数据分析概览](../modules/data-analytics-platform/overview.md)

### [推荐系统模块](../modules/recommendation-system/)
- **功能**: 个性化推荐、商品推荐、内容推荐、推荐效果分析
- **技术**: 协同过滤、深度学习、特征工程、A/B测试
- **状态**: 📝 规划中
- **文档**: [推荐系统概览](../modules/recommendation-system/overview.md)

## 技术基础设施模块 (5个)

> 为所有业务模块提供技术支撑和基础能力

### [应用核心模块](../modules/application-core/)
- **功能**: API路由、中间件、异常处理、配置管理
- **技术**: FastAPI框架、中间件链、全局异常、配置中心
- **状态**: ✅ 已完成
- **API文档**: [应用核心API](../modules/application-core/api-spec.md)

### [数据库核心模块](../modules/database-core/)
- **功能**: 数据库连接、会话管理、连接池、事务控制
- **技术**: SQLAlchemy、连接池、事务管理、数据库配置
- **状态**: ✅ 已完成
- **API文档**: [数据库核心API](../modules/database-core/api-spec.md)

### [数据模型模块](../modules/data-models/)
- **功能**: ORM模型定义、数据验证、模型关系、数据迁移
- **技术**: Pydantic模型、SQLAlchemy ORM、Alembic迁移
- **状态**: ✅ 已完成
- **API文档**: [数据模型API](../modules/data-models/api-spec.md)

### [Redis缓存模块](../modules/redis-cache/)
- **功能**: 缓存服务、会话存储、分布式锁、消息队列
- **技术**: Redis客户端、缓存策略、序列化、分布式锁
- **状态**: ✅ 已完成
- **API文档**: [Redis缓存API](../modules/redis-cache/api-spec.md)

### [数据库工具模块](../modules/database-utils/)
- **功能**: 数据库工具函数、查询构建、批量操作、性能优化
- **技术**: 查询构建器、批量处理、索引优化、慢查询分析
- **状态**: ✅ 已完成
- **API文档**: [数据库工具API](../modules/database-utils/api-spec.md)

## 模块状态统计

### 按开发状态分类
- ✅ **已完成**: 10个模块 (5个核心交易 + 5个技术基础设施)
- 🔄 **开发中**: 6个模块 (2个农产品特色 + 4个营销会员)  
- 📝 **规划中**: 7个模块 (7个基础服务)

### 按优先级分类
- **P0 核心**: 5个 (全部已完成)
- **P1 重要**: 6个 (全部开发中)
- **P2 支撑**: 7个 (全部规划中)
- **P3 基础**: 5个 (全部已完成)

### 按业务域分类
- **用户管理域**: 2个模块
- **商品管理域**: 3个模块  
- **交易流程域**: 7个模块
- **营销推广域**: 5个模块
- **运营支撑域**: 6个模块
- **技术基础域**: 5个模块

## 相关文档

- [模块架构设计](./module-architecture.md) - 模块分类和依赖关系
- [依赖关系图](./dependency-architecture.md) - 模块间依赖分析  
- [性能要求标准](../standards/performance-standards.md) - 模块性能指标
- [API设计规范](../standards/openapi.yaml) - 统一API标准
- [开发指南](../guides/development-guide.md) - 模块开发规范

## 更新日志

### v1.0.0 (2025-09-13)
- ✅ 初始版本，包含23个模块的完整目录
- ✅ 按业务域和优先级分类整理
- ✅ 添加模块状态和技术栈说明
- ✅ 建立文档交叉引用关系