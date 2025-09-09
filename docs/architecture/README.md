# 项目架构文档索引

## 📚 文档组织结构

### 🏗️ 核心架构文档 (`docs/architecture/`)
- **[数据模型规范](./data_models.md)** ✅ - 统一的数据模型定义和配置管理
- **[API契约规范](./api_contracts.md)** ✅ - RESTful API设计和版本管理  
- **[测试策略规范](./testing_strategy.md)** ✅ - 全面的测试体系和自动化策略
- **[部署运维规范](./deployment_operations.md)** ✅ - 容器化部署和运维最佳实践
- [技术架构总览](tech_architecture.md) - 核心技术选型和架构决策
- [配置管理规范](configuration.md) - 统一配置驱动架构
- [开发工作流程](development_workflow.md) - 标准化开发流程

### 📦 功能模块文档 (`docs/modules/`)
- [用户认证模块](../modules/user_auth/README.md) - 用户认证、权限管理
- [商品管理模块](../modules/product_management/README.md) - 商品、分类、库存管理
- [购物车模块](../modules/shopping_cart/README.md) - 购物车、临时存储
- [订单管理模块](../modules/order_management/README.md) - 订单生命周期管理
- [支付系统模块](../modules/payment_system/README.md) - 支付集成、回调处理
- [后台管理模块](../modules/admin_system/README.md) - PC端管理界面
- [移动端模块](../modules/mobile_app/README.md) - 小程序/H5界面

### 🔧 运维文档 (`docs/operations/`)
- [部署指南](../operations/deployment.md)
- [监控告警](../operations/monitoring.md)
- [故障排除](../operations/troubleshooting.md)

## 📝 文档维护规范

### 更新频率
- **架构文档**: 重大架构变更时更新
- **模块文档**: 每个功能迭代完成时更新
- **API文档**: 接口变更时立即更新

### 审查机制
- 所有文档变更需要代码审查
- 架构文档变更需要技术负责人确认
- API变更需要接口契约测试通过

## 🔗 快速导航

### 按开发阶段
1. **当前阶段**: [支付系统模块](../modules/payment_system/README.md)
2. **下一阶段**: [后台管理模块](../modules/admin_system/README.md)
3. **计划阶段**: [移动端模块](../modules/mobile_app/README.md)

### 按技术领域
- **数据层**: [数据模型规范](data_models.md)
- **服务层**: [API契约规范](api_contracts.md)
- **界面层**: [前端开发规范](frontend_standards.md)
- **集成层**: [第三方集成规范](integration_standards.md)
