---
title: "tools/task_classification 目录说明"
version: "v1.0.0"
status: "Active"
created: "2025-10-02"
updated: "2025-10-02"
owner: "AI工作流程优化系统"
dependencies:
	- "MASTER.md"
	- "test_ai_workflow.py"
labels:
	- "tool"
	- "configuration"
	- "ai-classification"
document_type: "目录说明文档"
usage_scenario: "理解task_classification目录的结构和配置文件的作用"
usage_method: "开发和维护AI智能分类算法时的配置参考"
cooperation_docs: "与MASTER.md配合，为AI内置算法提供配置参考"
maintenance_note: "配置文件变更时需要同步更新；新增任务类型时需要扩展配置"
---

# tools/task_classification 目录说明

> **功能说明**: 为AI智能任务分类算法提供配置参考和测试验证工具  
> **使用方法**: AI执行时内置算法逻辑，测试时调用Python实现验证  
> **使用场景**: AI算法配置参考、分类效果测试、算法调优、权重配置  
> **配合使用**: 与MASTER.md配合，MASTER.md为执行标准，本目录为配置参考  
> **更新维护**: 算法调整时同步更新配置；新增任务类型时扩展配置文件；定期验证配置与算法的一致性

## 📁 目录结构

```
tools/task_classification/
├── config/                          # 配置文件目录
│   ├── task_types.yaml              # 任务类型定义和权重配置
│   ├── keywords.yaml                # 关键词库配置
│   ├── checkpoint_mapping.yaml      # 检查点映射规则
│   └── weights.yaml                 # 全局权重和阈值参数
├── classifier.py                    # 分类算法的Python参考实现
└── __pycache__/                     # Python运行缓存（可删除）
```

## 📋 子目录和文件说明

| 文件/目录 | 功能描述 | 责任人 | 更新频率 | 最后更新 |
|-----------|----------|--------|----------|----------|
| `config/` | 存放所有配置文件 | AI工作流程优化系统 | 按需更新 | 2025-10-02 |
| `task_types.yaml` | 6大任务类型的权重和关键词定义 | 算法维护团队 | 算法调优时 | 2025-10-02 |
| `keywords.yaml` | 完整的关键词库和正则表达式 | 算法维护团队 | 词库扩展时 | 2025-10-02 |
| `checkpoint_mapping.yaml` | 检查点匹配规则和条件逻辑 | 检查点维护团队 | 检查点变更时 | 2025-10-02 |
| `weights.yaml` | 全局权重、阈值和性能参数 | 算法维护团队 | 参数调优时 | 2025-10-02 |
| `classifier.py` | 算法的完整Python实现 | 开发团队 | 算法逻辑变更时 | 2025-10-02 |

## 🔧 关键文档列表

### 核心配置文件
- [task_types.yaml](config/task_types.yaml) - 定义DESIGN/DEVELOP/TEST/INTEGRATE/MAINTAIN/SECURE六大任务类型
- [keywords.yaml](config/keywords.yaml) - 包含动作动词、技术词汇、技术栈等关键词库
- [checkpoint_mapping.yaml](config/checkpoint_mapping.yaml) - 定义任务类型到检查点的映射规则

### 算法实现
- [classifier.py](classifier.py) - 完整的分类算法实现，包含关键词提取、加权评分、检查点匹配等功能

## 💼 维护职责

- **算法维护团队**: 负责分类算法逻辑、权重配置、关键词库的维护和优化
- **检查点维护团队**: 负责检查点映射规则的维护，确保与MASTER.md保持一致
- **开发团队**: 负责Python实现代码的维护和测试验证
- **质量保证团队**: 负责配置文件的一致性检查和算法效果验证

## 🔄 与其他文档的协作关系

### 与MASTER.md的关系
- **权威关系**: MASTER.md为执行标准，本目录为配置参考
- **同步要求**: MASTER.md的分类要求变更时，需同步更新配置文件
- **一致性**: 任务类型定义、输出格式、置信度阈值必须保持一致

### 与checkpoint-cards.md的关系
- **映射关系**: checkpoint_mapping.yaml中的检查点必须在checkpoint-cards.md中有对应定义
- **同步机制**: 检查点新增或删除时，两边必须同步更新

### 与测试文件的关系
- **验证依赖**: test_ai_workflow.py依赖本目录的配置文件进行算法测试
- **效果评估**: 通过测试脚本验证分类算法的准确性和效果

## 📊 变更历史摘要

| 版本 | 日期 | 变更内容 | 影响范围 |
|------|------|----------|----------|
| v1.0.0 | 2025-10-02 | 初始创建，包含6大任务类型配置 | 全新建立 |

## ⚠️ 重要说明

1. **不是运行时依赖**: AI执行任务时不会调用这些文件，而是内置相同的算法逻辑
2. **配置参考作用**: 为AI内置算法提供标准的配置参考和测试验证
3. **保持同步**: 所有配置变更必须与MASTER.md保持一致，避免冲突
4. **测试验证**: 通过Python实现验证算法效果，指导AI内置算法的优化