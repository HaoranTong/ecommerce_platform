# 项目状态跟踪 (简化版)

本目录包含项目核心状态文档，经过简化重构，只保留4个关键文档。

## 📋 核心文档 (仅4个)

### 🤖 自动化文档 (禁止手工编辑)
- **[模块开发状态](module-status.md)** - 自动统计的模块完成情况、API端点、代码行数
  - 📊 **更新方式**: 执行 `scripts/update_module_status.ps1` 
  - ⚠️ **严禁手工编辑**，所有数据通过脚本自动生成

### 📝 人工维护文档
- **[当前工作状态](current-work-status.md)** - 当前开发重点、进行中的任务
- **[问题跟踪](issues-tracking.md)** - 技术问题、解决方案、责任人跟踪
- **[状态目录说明](README.md)** - 本文档，说明文档结构和使用方法

## 🎯 使用说明

### AI开发人员
- **模块完成后** - 立即执行 `scripts/update_module_status.ps1` 更新状态
- **工作开始前** - 查看 module-status.md 了解当前完成情况  
- **遇到问题时** - 在 issues-tracking.md 中记录技术问题
- **工作切换时** - 更新 current-work-status.md 说明当前重点

## 📊 自动化状态更新流程

### 模块开发完成时 (自动化)
```
模块编码完成 
    ↓
执行 scripts/update_module_status.ps1
    ↓
自动更新 module-status.md (API数量、代码行数、完成率)
```

### 日常工作跟踪 (手工维护) 
```
开始新工作 → 更新 current-work-status.md
    ↓
遇到技术问题 → 记录到 issues-tracking.md  
    ↓
问题解决后 → 更新 issues-tracking.md 状态
```

## � 强制规范

### ✅ 允许的操作
- 手工编辑 current-work-status.md 和 issues-tracking.md
- 执行自动化脚本更新 module-status.md  
- 阅读所有状态文档

### ❌ 禁止的操作  
- 手工编辑 module-status.md (只能通过脚本更新)
- 删除或重命名4个核心文档
- 添加新的状态文档 (保持简化结构)
- 跳过脚本直接修改模块统计数据

## 📋 MASTER.md 集成

本状态目录的管理规范已集成到 `MASTER.md` 中：
- 核心文档固定为4个
- 自动化更新点明确定义  
- 手工编辑权限严格控制
- 文档删除保护机制启用

## � 迁移说明

本次重构删除了18个冗余文档，保留核心功能：
- ~~development-standards.md~~ → 已删除，功能迁移到自动化
- ~~各种checkpoint文档~~ → 已删除，内容重复
- ~~phase-two系列文档~~ → 已删除，规划过度细化
- ✅ 保留4个核心文档，功能覆盖完整
