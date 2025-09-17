# 项目文档中心

电商平台技术文档导航，包含系统架构设计、API规范、开发指南等核心文档。

## 📁 目录结构

```
docs/
├── 📐 architecture/         # 系统架构设计
│   ├── overview.md          # 架构总览和设计原则
│   ├── data-models.md       # 数据库设计规范
│   ├── security.md          # 安全架构设计
│   ├── event-driven.md      # 事件驱动架构
│   └── integration.md       # 第三方集成方案

├── 🏗️ core/                 # 核心基础设施文档
│   ├── README.md            # 核心组件导航
│   ├── application-core/    # 应用核心框架
│   ├── database-core/       # 数据库连接管理
│   ├── database-utils/      # 数据库工具脚本
│   └── redis-cache/         # Redis缓存管理
├── � shared/               # 共享组件文档
│   ├── README.md            # 共享组件导航
│   └── base-models/         # 基础数据模型
├── �📦 modules/              # 业务功能模块文档
│   ├── README.md            # 模块总览索引
│   ├── user-auth/           # 用户认证模块
│   ├── product-catalog/     # 商品管理模块
│   ├── shopping-cart/       # 购物车模块
│   ├── order-management/    # 订单管理模块
│   ├── payment-service/     # 支付服务模块
│   ├── quality-control/     # 质量控制模块
│   ├── batch-traceability/  # 批次溯源模块
│   ├── logistics-management/ # 物流管理模块
│   ├── member-system/       # 会员系统模块
│   ├── distributor-management/ # 分销商管理模块
│   ├── marketing-campaigns/ # 营销活动模块
│   ├── social-features/     # 社交功能模块
│   ├── inventory-management/ # 库存管理模块
│   ├── notification-service/ # 通知服务模块
│   ├── supplier-management/ # 供应商管理模块
│   ├── recommendation-system/ # 推荐系统模块
│   ├── customer-service-system/ # 客服系统模块
│   ├── risk-control-system/ # 风控系统模块
│   └── data-analytics-platform/ # 数据分析模块
├── 💻 development/          # 开发环境指南
│   ├── README.md            # 开发指南导航
│   ├── testing-setup.md     # 测试环境配置指南
│   └── tools.md             # 开发工具配置
├── 🚀 operations/           # 运维部署文档
│   ├── README.md            # 运维指南
│   ├── deployment.md        # 部署指南
│   └── environment.md       # 环境配置
├── 📋 requirements/         # 需求分析文档
│   ├── README.md            # 需求概览
│   ├── business.md          # 业务需求规格
│   ├── functional.md        # 功能需求说明
│   └── non-functional.md    # 非功能需求
├── 📏 standards/            # 开发规范标准
│   ├── README.md            # 规范标准导航
│   ├── api-standards.md     # API设计规范
│   ├── openapi.yaml         # API契约定义
│   ├── code-standards.md    # 代码组织规范
│   ├── database-standards.md # 数据库设计规范
│   ├── document-standards.md # 文档管理规范
│   ├── naming-conventions.md # 命名规范
│   ├── testing-standards.md # 测试规范
│   └── workflow-standards.md # 工作流程规范
├── 📊 status/               # 项目状态报告
│   ├── README.md            # 状态概览
│   ├── status.md            # 项目状态总览
│   ├── current-sprint.md    # 当前冲刺状态
│   ├── daily-log.md         # 每日工作日志
│   ├── issues-tracking.md   # 问题跟踪记录
│   └── milestones.md        # 里程碑进展
├── 📝 templates/            # 文档模板
│   ├── README.md            # 模板列表
│   └── module-template.md   # 模块文档标准模板
├── 📊 analysis/             # 分析报告文档
│   └── README.md            # 分析报告导航
└── 🗂️ _archive/             # 已归档文档
    ├── README.md            # 归档文档说明
    └── README_root_old.md   # 原根目录README备份
```

## 🔗 快速链接

### 核心文档
- [系统架构图](architecture/overview.md) - 了解整体架构
- [核心组件文档](core/README.md) - 应用核心基础设施
- [共享组件文档](shared/README.md) - 通用数据模型和工具
- [业务模块总览](modules/README.md) - 所有功能模块导航

### 开发指南  
- [开发环境配置](development/README.md) - 搭建开发环境
- [测试环境配置](development/testing-setup.md) - 测试环境详细配置指南
- [API设计规范](standards/api-standards.md) - API接口标准
- [代码规范标准](standards/code-standards.md) - 代码组织规范
- [文档管理规范](standards/document-standards.md) - 文档编写标准

### 运维部署
- [部署运维指南](operations/README.md) - 生产环境部署
- [环境配置说明](operations/environment.md) - 环境变量设置

### 项目管理
- [需求分析文档](requirements/README.md) - 业务和功能需求
- [项目状态总览](status/README.md) - 当前项目进展
- [里程碑追踪](status/milestones.md) - 重要节点记录

### 归档备份
- [文档归档](_archive/README.md) - 已清理的废弃文档和事件Schema