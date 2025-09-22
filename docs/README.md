# 项目文档中心

> **版本**: v2.0 - 基于四层文档体系  
> **更新**: 2025-09-22  
> **架构**: 模块化单体→微服务演进架构  

电商平台技术文档导航，采用四层文档体系：需求→架构→设计→标准，支持微服务演进。

## 📁 四层文档体系

```
docs/
├── � requirements/         # 需求层：纯业务需求
│   ├── README.md            # 需求层导航
│   ├── functional.md        # 功能需求规范
│   ├── business.md          # 业务需求规范
│   └── non-functional.md    # 非功能需求规范
├── 🏗️ architecture/         # 架构层：系统整体设计原则
│   ├── README.md            # 架构层导航
│   ├── overview.md          # 架构总览和设计原则
│   ├── application-architecture.md  # 应用架构设计
│   ├── business-architecture.md     # 业务架构设计
│   ├── data-architecture.md         # 数据架构设计
│   ├── infrastructure-architecture.md # 基础设施架构
│   ├── migration-roadmap.md         # 微服务演进路线图
│   ├── integration.md       # 第三方集成方案
│   └── security.md          # 安全架构设计
├── 🎨 design/               # 设计层：具体详细设计
│   ├── README.md            # 设计层导航
│   ├── modules/             # 业务模块详细设计（保持边界独立）
│   │   ├── README.md        # 业务模块索引
│   │   ├── user-auth/       # 用户认证模块
│   │   ├── product-catalog/ # 商品目录模块
│   │   ├── shopping-cart/   # 购物车模块
│   │   ├── order-management/ # 订单管理模块
│   │   ├── payment-service/ # 支付服务模块
│   │   ├── inventory-management/ # 库存管理模块
│   │   ├── member-system/   # 会员系统模块
│   │   ├── quality-control/ # 质量控制模块
│   │   ├── batch-traceability/ # 批次溯源模块
│   │   ├── customer-service-system/ # 客服系统模块
│   │   ├── data-analytics-platform/ # 数据分析平台模块
│   │   ├── distributor-management/ # 经销商管理模块
│   │   ├── logistics-management/ # 物流管理模块
│   │   ├── marketing-campaigns/ # 营销活动模块
│   │   ├── notification-service/ # 通知服务模块
│   │   ├── recommendation-system/ # 推荐系统模块
│   │   ├── risk-control-system/ # 风控系统模块
│   │   ├── social-features/ # 社交功能模块
│   │   └── supplier-management/ # 供应商管理模块
│   └── components/          # 技术组件详细设计（保持边界清晰）
│       ├── README.md        # 技术组件索引
│       ├── application-core/ # 应用核心组件
│       ├── database-core/   # 数据库核心组件
│       ├── database-utils/  # 数据库工具组件
│       ├── redis-cache/     # Redis缓存组件
│       └── base-models/     # 基础模型组件
├── 📊 planning/             # 项目管理层
│   ├── README.md            # 项目管理导航
│   └── DEVELOPMENT_PLAN.md  # 开发计划文档
├── 📏 standards/            # 标准层：开发规范和执行标准
│   ├── README.md            # 标准层导航
│   ├── document-standards.md # 文档结构规范（权威标准）
│   ├── api-standards.md     # API设计规范
│   ├── database-standards.md # 数据库设计规范
│   ├── code-standards.md    # 代码组织规范
│   ├── testing-standards.md # 测试规范（五层架构）
│   ├── naming-conventions.md # 命名规范
│   ├── workflow-standards.md # 工作流程规范
│   ├── checkpoint-cards.md  # 检查点卡片系统
│   └── openapi.yaml         # API契约定义
├── � tools/               # 开发工具指南
│   ├── README.md            # 工具使用导航
│   ├── scripts-usage-manual.md # 开发脚本使用手册
│   ├── testing-tools.md     # 测试工具配置指南
│   ├── test-management.md   # 测试文件管理策略
│   └── troubleshooting.md   # 工具故障排除手册
├── 🚀 operations/           # 运维部署层
│   ├── README.md            # 运维指南导航
│   ├── deployment.md        # 部署指南
│   ├── development-setup.md # 开发环境配置
│   ├── testing-environment.md # 测试环境配置
│   ├── production-config.md # 生产环境配置
│   ├── environment-variables.md # 环境变量管理
│   ├── monitoring.md        # 监控告警配置
│   ├── troubleshooting.md   # 故障排除指南
│   └── runbook.md           # 运维操作手册
├── �️ adr/                  # 架构决策记录
│   ├── README.md            # ADR索引
│   └── ADR-0001-调整功能需求和架构设计.md # 文档架构调整决策
├── 📊 status/               # 状态管理层
│   ├── README.md            # 状态管理导航
│   ├── current-work-status.md # 当前工作状态
│   ├── issues-tracking.md   # 问题跟踪记录
│   ├── work-history-archive.md # 工作历史档案
│   └── module-status.md     # 模块状态管理
├── 📝 templates/            # 文档模板库
│   ├── README.md            # 模板导航
│   └── module-template.md   # 模块文档标准模板
├── 📊 analysis/             # 分析报告归档
│   ├── README.md            # 分析报告导航
│   └── [各类分析报告]        # 历史分析文档
└── 🗂️ _archive/             # 废弃文档备份
    ├── README.md            # 归档文档说明
    └── [已废弃文档]          # 废弃文档备份
```

## 🎯 四层文档体系核心特征

### � 需求层 (requirements/)
- **职责**: 纯业务需求定义，不涉及技术实现
- **特征**: 做什么（What），用户故事，业务规则  
- **约束**: 技术无关，面向业务价值

### 🏗️ 架构层 (architecture/)  
- **职责**: 系统整体架构思路和设计原则
- **特征**: 为什么这样做（Why），架构思维，演进策略
- **约束**: 指导性原则，不涉及具体实现细节

### 🎨 设计层 (design/)
- **职责**: 具体的详细设计文档
- **特征**: 怎么做（How），技术实现，详细方案
- **边界管理**: 严格保持模块/组件边界独立，支持微服务演进

### 📏 标准层 (standards/)
- **职责**: 开发规范和执行标准  
- **特征**: 按什么标准做（Standard），约束性规范
- **约束**: 具有强制约束力，跨服务统一标准

## �🔗 快速导航

### 🎯 核心入口
- [🏗️ 系统架构总览](architecture/README.md) - 了解整体架构设计原则
- [🎨 设计层导航](design/README.md) - 业务模块和技术组件设计
- [📏 文档标准规范](standards/document-standards.md) - **权威标准文档**
- [📊 当前工作状态](status/current-work-status.md) - 实时工作进展

### 🚀 开发必备  
- [� 开发工具指南](tools/README.md) - 工具使用和脚本操作
- [🚀 环境配置指南](operations/development-setup.md) - 开发环境搭建
- [🧪 测试工具配置](tools/testing-tools.md) - 测试环境详细配置
- [📋 需求规格总览](requirements/README.md) - 业务和功能需求
- [🔧 API设计规范](standards/api-standards.md) - API接口标准

### 📦 业务模块 
- [👥 用户认证模块](design/modules/user-auth/README.md) - 用户认证和授权
- [🛒 商品目录模块](design/modules/product-catalog/README.md) - 商品管理
- [🛍️ 购物车模块](design/modules/shopping-cart/README.md) - 购物车功能
- [📋 订单管理模块](design/modules/order-management/README.md) - 订单处理
- [💳 支付服务模块](design/modules/payment-service/README.md) - 支付处理

### 🔧 技术组件
- [🏗️ 应用核心组件](design/components/application-core/README.md) - 应用基础框架
- [🗄️ 数据库核心组件](design/components/database-core/README.md) - 数据库连接管理
- [⚡ Redis缓存组件](design/components/redis-cache/README.md) - 缓存管理
- [📊 基础模型组件](design/components/base-models/README.md) - 通用数据模型

### 📚 项目管理
- [📊 项目计划管理](planning/README.md) - 开发计划和进度管理
- [🗂️ 架构决策记录](adr/README.md) - ADR决策历史
- [📊 问题追踪管理](status/issues-tracking.md) - 问题跟踪记录
- [🗂️ 文档归档](/_archive/README.md) - 已清理的废弃文档