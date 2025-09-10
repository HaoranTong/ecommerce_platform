# 开发工作总纲

> **🎯 这是你每次开发前必须阅读的总纲文档**  
> **所有技术文档的导航和工作流程的唯一入口**

## 🚨 强制检查点

你必须在以下时刻阅读本文档：

1. **开始新功能开发前** - 确认技术架构和需求理解
2. **提交代码前** - 检查是否遵循所有规范
3. **更新技术文档前** - 确认文档边界和更新规则  
4. **测试遇到问题时** - 寻找解决方案和调试指南
5. **每日工作开始时** - 回顾当前状态和优先级

## 📋 开发工作流程

### Phase 1: 开发准备 (必须完成)

1. **阅读需求规范**
   - [ ] [业务需求](requirements/business.md) - 理解项目目标
   - [ ] [功能需求](requirements/functional.md) - 明确具体功能要求
   - [ ] [非功能需求](requirements/non-functional.md) - 了解性能和安全要求

2. **检查技术架构**
   - [ ] [架构总览](architecture/overview.md) - 确认技术选型
   - [ ] [API设计标准](architecture/api-standards.md) - 遵循API规范
   - [ ] [数据模型标准](architecture/data-standards.md) - 遵循数据库规范

3. **查看模块设计**
   - [ ] 检查 `docs/modules/` 下相关模块文档
   - [ ] 理解模块间依赖关系
   - [ ] 确认API契约和数据结构

### Phase 2: 开发实施 (严格执行)

1. **代码开发**
   - [ ] 遵循 [编码规范](development/standards.md)
   - [ ] 使用 [开发工具](development/tools.md) 配置环境
   - [ ] 实时更新 [工作日志](status/daily-log.md)

2. **测试验证**
   - [ ] 执行 [测试策略](development/testing.md)
   - [ ] 运行烟雾测试: `.\scripts\smoke_test.ps1`
   - [ ] 更新测试用例和文档

3. **文档更新**
   - [ ] 更新模块实现文档 `docs/modules/[module]/implementation.md`
   - [ ] 记录问题和解决方案到 [问题跟踪](status/issues-tracking.md)
   - [ ] 更新API文档（如有接口变更）

### Phase 3: 完成和集成 (质量保证)

1. **代码提交**
   - [ ] 运行完整测试套件
   - [ ] 使用自动化脚本: `.\scripts\feature_finish.ps1`
   - [ ] 创建模块总结: `docs/modules/[module]/summary.md`

2. **文档同步**
   - [ ] 确保所有变更都有文档记录
   - [ ] 更新 [当前阶段状态](status/current-sprint.md)
   - [ ] 更新 [里程碑记录](status/milestones.md)

## 📁 文档体系导航

### 🎯 核心文档 (开发必读)
- **本文档** - 总纲和工作流程
- **[功能需求](requirements/functional.md)** - 具体功能规范
- **[API设计标准](architecture/api-standards.md)** - API开发规范
- **[数据模型标准](architecture/data-standards.md)** - 数据库设计规范

### 📦 模块文档 (按需查阅)
```
docs/modules/
├── user-auth/           # 用户认证模块
├── product-management/  # 商品管理模块  
├── shopping-cart/       # 购物车模块
├── order-management/    # 订单管理模块
└── payment-system/      # 支付系统模块
```

每个模块包含：
- `README.md` - 模块概述
- `requirements.md` - 详细需求
- `design.md` - 技术设计
- `api-spec.md` - API规范
- `implementation.md` - 开发记录
- `summary.md` - 完成总结

### 📊 状态文档 (实时更新)
- **[工作日志](status/daily-log.md)** - 每日进展记录
- **[当前阶段](status/current-sprint.md)** - 开发状态
- **[问题跟踪](status/issues-tracking.md)** - Bug和任务
- **[里程碑](status/milestones.md)** - 版本发布

## ⚡ 快速命令参考

### 开发环境
```powershell
. .\dev_env.ps1              # 配置环境
.\dev_tools.ps1 check-db     # 检查数据库
.\dev_tools.ps1 start-api    # 启动服务
.\dev_tools.ps1 test-cart    # 运行测试
```

### 自动化脚本
```powershell
.\scripts\smoke_test.ps1         # 烟雾测试
.\scripts\feature_finish.ps1     # 功能完成
.\scripts\release_to_main.ps1    # 发布主分支
.\scripts\log_status.ps1         # 记录状态
```

## 🚨 重要规则和约束

### 文档更新规则
1. **单一事实源** - 每个技术决策只在一个文档中详细定义
2. **及时同步** - 代码变更必须同步更新文档
3. **避免重复** - 不同文档间通过引用而非复制共享信息

### 开发规范
1. **架构优先** - 所有开发必须遵循已定义的架构标准
2. **测试驱动** - 功能完成必须有对应测试
3. **文档驱动** - 重要变更必须先更新文档

### 质量标准
1. **完整性** - 功能实现必须完整，不允许临时方案
2. **一致性** - API设计和数据模型必须保持一致
3. **可维护性** - 代码和文档必须清晰易懂

## 🆘 遇到问题时

1. **首先查看** [故障排除](operations/troubleshooting.md)
2. **检查日志** [问题跟踪](status/issues-tracking.md)
3. **参考规范** [开发工作流程](development/workflow.md)
4. **更新状态** [工作日志](status/daily-log.md)

---

**⚠️ 重要提醒: 任何偏离本文档流程的开发行为都可能导致架构不一致和技术债务！**
