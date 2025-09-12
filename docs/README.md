# 项目文档中心

电商平台技术文档导航，包含架构设计、API规范、开发指南等核心文档。

## 📁 目录结构

```
docs/
├── 📐 architecture/         # 系统架构设计
│   ├── overview.md          # 架构总览和设计原则
│   ├── data-models.md       # 数据库设计规范
│   ├── security.md          # 安全架构设计
│   ├── event-driven.md      # 事件驱动架构
│   └── integration.md       # 第三方集成方案
├── 📡 api/                  # API接口文档
│   ├── README.md            # API文档中心导航
│   ├── api-design-standards.md # API设计标准规范
│   ├── openapi.yaml         # OpenAPI 3.0规范文档
│   └── modules/             # 各模块API文档
├── 📦 modules/              # 功能模块文档
│   ├── README.md            # 模块总览索引
│   ├── user-auth/           # 用户认证模块
│   ├── shopping-cart/       # 购物车模块
│   ├── order-management/    # 订单管理模块
│   ├── product-catalog/     # 商品管理模块
│   ├── inventory-management/ # 库存管理模块
│   ├── payment-service/     # 支付服务模块
│   ├── notification-service/ # 通知服务模块
│   └── recommendation-system/ # 推荐系统模块
├── 💻 development/          # 开发环境指南
│   ├── README.md            # 开发指南导航
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

- [系统架构图](architecture/overview.md) - 了解整体架构
- [API快速开始](api/README.md) - API接口使用
- [开发环境配置](development/README.md) - 搭建开发环境
- [部署运维指南](operations/README.md) - 生产环境部署