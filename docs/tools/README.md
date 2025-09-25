# 开发工具使用指南

## 📋 目录概述

本目录包含项目开发过程中使用的各种工具、脚本和配置的详细使用指南。

**职责定位**: 专注于工具使用指导和脚本操作手册  
**与scripts目录关系**: 本目录提供使用文档，scripts/目录包含实际脚本文件

---

## 📁 目录结构

```
tools/
├── README.md                    # 本文档 - 工具总览导航
├── checkpoint-cards.md          # 🎯 AI检查点卡片系统 (MASTER.md配套)
├── scripts-usage-manual.md     # 开发脚本详细使用手册
├── testing-tools.md            # 测试工具配置和使用指南  
├── test-management.md          # 测试文件生命周期管理
└── troubleshooting.md          # 工具故障排除和诊断手册
```

---

## 🎯 使用导航

### 🎯 AI检查点系统
- **[检查点卡片系统](checkpoint-cards.md)** - MASTER.md配套的AI检查验证程序
  - 完整覆盖文档驱动开发的每个环节
  - REQ/ARCH/DEV/TEST/DOC/STATUS等6大类检查卡片
  - 精准导航到具体文档位置和验证清单

### 🔧 开发脚本工具
- **[脚本使用手册](scripts-usage-manual.md)** - 13个开发脚本的详细使用说明
  - AI检查点验证脚本
  - 代码质量检查脚本
  - 🆕 **标准文档验证脚本** (Phase 3.1新增)  
  - 项目管理脚本
  - 测试执行脚本
  - 📋 **代码块格式分析工具** - 已整合到脚本使用手册中

### 🧪 测试工具套件
- **[测试工具配置](testing-tools.md)** - 测试环境配置和工具使用
- **[测试管理策略](test-management.md)** - Generated目录管理和文件生命周期
- **[故障排除](troubleshooting.md)** - 工具使用过程中的问题解决

---

## 🚀 快速开始

### 新开发人员
1. **环境配置** → 参考 [环境变量管理](../operations/environment-variables.md)
2. **工具了解** → 阅读 [脚本使用手册](scripts-usage-manual.md)
3. **测试配置** → 参考 [测试工具配置](testing-tools.md)

### 日常开发
1. **脚本使用** → 查阅 [脚本使用手册](scripts-usage-manual.md)
2. **问题排查** → 参考 [故障排除](troubleshooting.md)
3. **测试管理** → 使用 [测试管理策略](test-management.md)

---

## 📋 工具分类概览

### AI优化工具
- `ai_checkpoint.ps1` - AI检查点验证
- `scripts-usage-manual.md` - AI优化的结构化信息模板

### 代码质量工具  
- `check_code_standards.ps1` - 代码规范检查
- `check_naming_compliance.ps1` - 命名规范验证
- `validate_pydantic_v2.py` - Pydantic V2语法验证

### 测试工具套件
- `generate_test_template.py` - 智能测试生成器
- `setup_test_env.ps1` - 测试环境配置
- `run_module_tests.ps1` - 模块测试执行

### 项目管理工具
- `feature_finish.ps1` - 功能完成流程
- `sync_readme.ps1` - 文档同步更新
- `update_module_status.ps1` - 模块状态管理

---

## 🔗 关联文档

### 上级文档
- **[MASTER.md](../MASTER.md)** - 项目主控文档和检查点系统
- **[工作流程标准](../standards/workflow-standards.md)** - 开发流程规范

### 同级文档
- **[环境配置](../operations/environment-variables.md)** - 环境变量配置和管理
- **[测试标准](../standards/testing-standards.md)** - 测试规范和标准

### 下级文档
- 本目录内的各个具体工具使用文档

---

## ⚡ 重要提示

- **工具更新**: 工具脚本更新后必须同步更新相关文档
- **使用反馈**: 工具使用问题请记录到 [故障排除](troubleshooting.md)
- **文档维护**: 遵循 [文档标准](../standards/document-management-standards.md) 进行维护

---
*目录重构时间: 2025-09-25 | 更新: 同步删除analyze_simple_markers.md，添加checkpoint-cards.md说明*
