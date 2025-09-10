# 电商平台文档中心

项目的技术文档和开发指南。

## � 文档结构

### 📋 需求文档
- [业务需求](requirements/business.md) - 项目目标和业务逻辑
- [功能需求](requirements/functional.md) - 具体功能说明
- [非功能需求](requirements/non-functional.md) - 性能、安全要求

### 🏗️ 系统架构
- [架构概览](architecture/overview.md) - 技术架构设计
- [数据模型](architecture/data-models.md) - 数据库设计
- [API标准](architecture/api-standards.md) - 接口规范
- [安全架构](architecture/security.md) - 安全设计

### 🔧 功能模块
- [用户认证](modules/user-auth/overview.md) - 登录注册功能
- [购物车](modules/shopping-cart/overview.md) - 购物车功能
- [商品管理](modules/product-catalog/overview.md) - 商品管理
- [订单管理](modules/order-management/overview.md) - 订单处理
- [支付系统](modules/payment/overview.md) - 支付集成

### 🛠️ 开发指南
- [编码标准](development/standards.md) - 代码规范
- [测试指南](development/testing.md) - 测试方法
- [开发工具](development/tools.md) - 工具配置

### 🚀 运维部署
- [部署指南](operations/deployment.md) - 部署流程
- [环境配置](operations/environment.md) - 环境变量

### 📊 项目状态
- [里程碑](status/milestones.md) - 项目进度
- [当前Sprint](status/current-sprint.md) - 当前工作
- [问题跟踪](status/issues-tracking.md) - 问题管理

## � 快速开始

**开发人员**:
1. 阅读 [架构概览](architecture/overview.md)
2. 查看 [编码标准](development/standards.md)
3. 了解相关的[功能模块](modules/)

**运维人员**:
1. 查看 [部署指南](operations/deployment.md)
2. 配置 [环境变量](operations/environment.md)

## 📈 项目状态

- **进度**: 40% (核心功能开发中)
- **当前工作**: 购物车和订单管理
- **文档数量**: 60+ 个

## 🔧 脚本工具

```powershell
# 检查文档状态
.\scripts\check_docs.ps1

# 设置环境
.\scripts\sync_env.ps1 -Action create
```

更多脚本使用说明: [scripts/USAGE.md](../scripts/USAGE.md)