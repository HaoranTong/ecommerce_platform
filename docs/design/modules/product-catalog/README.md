---
title: "product-catalog - 模块总览"
version: "1.0.0"
status: "draft"
created: "2025-10-06"
updated: "2025-10-06"
owner: "待填写"
dependencies:
  - "../../standards/document-management-standards.md"
  - "../../standards/module-implementation-template.md"
labels:
  - module: product-catalog
  - layer: L2
---

<!--
文档说明：
- 内容：模块README导航模板，模块入口文档
- 作用：提供快速导航和基本信息，不包含详细内容
- 使用方法：复制此模板，替换模板变量，保持简洁
-->

# product-catalog模块 模块

📋 **状态**: 草稿  
👤 **负责人**: 待定  
🔄 **最后更新**: 2025-10-06  

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
提供商品信息、分类、品牌和 SKU 的管理功能，包括商品的增删改查、分类树维护、品牌配置和 SKU 属性管理。

### 核心功能
- 商品信息 CRUD  
- 分类树管理  
- 品牌管理  
- SKU 管理  

## 技术栈
- **后端**: FastAPI + SQLAlchemy  
- **数据库**: MySQL 8.0  
- **缓存**: Redis  
- **其他**: Docker Compose

## 快速开始

### API端点
- **基础路径**: `/api/v1/product-catalog/`
- **主要接口**: 详见 [api-spec.md](./api-spec.md)

### 数据模型
- **核心表**: `{table_name}`
- **关联表**: 详见 [overview.md](./overview.md#数据模型)

## 相关链接
- [系统架构](../../architecture/overview.md)
- [API设计规范](../../standards/api-standards.md)
- [开发规范](../../standards/code-standards.md)

## 依赖标准
- [文档管理标准](../../standards/document-management-standards.md)
- [应用架构](../../architecture/application-architecture.md)
- [模块实施模板](../../docs/design/modules/product-catalog/module-implementation-template.md)

## 具体标准

### 模块文档标准
- 每个模块必须包含7个标准文档：README.md、overview.md、requirements.md、design.md、api-spec.md、api-implementation.md、implementation.md
- 文档间通过相对路径引用，保持导航一致性
- 使用标准化的状态标记和负责人信息
