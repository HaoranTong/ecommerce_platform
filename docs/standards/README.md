<!--version info: v1.0.0, created: 2025-09-23, level: L2, dependencies: naming-conventions-standards.md,project-structure-standards.md-->

# 开发规范标准

项目开发过程中的各类规范、标准和约束文档。

## 📁 目录结构

```tree
standards/
├── README.md                          # 本文档
├── standards-master-index.md          # L0导航：AI友好统一检索入口
├── project-structure-standards.md     # L1核心：项目结构权威标准
├── naming-conventions-standards.md    # L1核心：命名规范权威标准
├── naming-conventions-standards.md              # L1核心：命名规范总纲（兼容性保留）
├── api-standards.md                   # L2领域：API设计规范
├── code-standards.md                  # L2领域：代码质量规范
├── database-standards.md              # L2领域：数据库设计规范
├── deployment-standards.md            # L2领域：容器化部署规范
├── document-dependencies-standards.md # L2领域：文档依赖管理规范
├── document-management-standards.md   # L2领域：文档管理规范
├── performance-standards.md           # L2领域：性能标准规范
├── scripts-standards.md               # L2领域：DevOps脚本规范
├── technology-stack-standards.md      # L2领域：技术栈标准规范
├── testing-standards.md               # L2领域：测试规范（五层架构）
├── workflow-standards.md              # L2领域：工作流程规范
└── openapi.yaml                       # API契约定义（全局标准）
```

## 📋 规范说明

| 规范文档 | 适用范围 | 强制程度 | 层级 |
|---------|---------|---------|-------|
| **standards-master-index.md** | AI友好统一检索入口 | 强制 | L0导航 |
| **project-structure-standards.md** | 项目结构权威标准 | 强制 | L1核心 |
| **naming-conventions-standards.md** | 命名规范权威标准 | 强制 | L1核心 |
| **naming-conventions-standards.md** | 命名规范总纲（兼容性） | 强制 | L1核心 |
| **api-standards.md** | API设计和接口规范 | 强制 | L2领域 |
| **code-standards.md** | 代码结构和组织 | 强制 | L2领域 |
| **database-standards.md** | 数据库设计 | 强制 | L2领域 |
| **deployment-standards.md** | 容器化和运维标准 | 强制 | L2领域 |
| **document-dependencies-standards.md** | 文档依赖关系管理 | 强制 | L2领域 |
| **document-management-standards.md** | 文档编写和管理 | 强制 | L2领域 |
| **performance-standards.md** | 性能标准和优化规范 | 强制 | L2领域 |
| **scripts-standards.md** | DevOps脚本管理规范 | 强制 | L2领域 |
| **technology-stack-standards.md** | 技术栈标准和版本规范 | 强制 | L2领域 |
| **testing-standards.md** | 测试编写和执行（五层架构） | 强制 | L2领域 |
| **workflow-standards.md** | 开发流程 | 强制 | L2领域 |
| **openapi.yaml** | 全局API契约定义 | 强制 | 契约 |
| **../tools/checkpoint-cards.md** | AI检查点卡片系统（已移至tools目录） | 强制 | 工具 |

## 🔗 使用指引

### 📚 开发入门路径
1. **新人必读** → [文档管理规范](document-management-standards.md) - 了解文档编写标准
2. **命名规范** → [命名规范总纲](naming-conventions-standards.md) - 掌握统一命名规则
3. **工作流程** → [开发工作流程](workflow-standards.md) - 学习标准开发流程

### 🎯 专项开发指引
- **API开发** → [API设计规范](api-standards.md) - API设计标准和约定
- **数据库设计** → [数据库设计规范](database-standards.md) - 数据表和字段规范
- **代码组织** → [代码组织规范](code-standards.md) - 文件结构和命名
- **测试编写** → [测试规范](testing-standards.md) - 测试策略和实施

### ⚡ 快速检查清单
- **开始编写代码** → 必须执行 [code-development-checklist.md](code-development-checklist.md) ⭐
- **执行检查点验证** → 使用 [checkpoint-cards.md](../tools/checkpoint-cards.md) - 26张精准导航卡片
- **API契约遵循** → 参考 [openapi.yaml](openapi.yaml) - 全局API标准
- **性能要求确认** → 检查 [performance-standards.md](performance-standards.md)
- **技术栈合规检查** → 遵循 [technology-stack-standards.md](technology-stack-standards.md)
- **文档依赖管理** → 参考 [document-dependencies-standards.md](document-dependencies-standards.md)
- **任何命名操作** → 检查 [naming-conventions-standards.md](naming-conventions-standards.md)
- **API设计** → 检查 [api-standards.md](api-standards.md)
- **数据库操作** → 检查 [database-standards.md](database-standards.md)
- **创建文档** → 检查 [document-management-standards.md](document-management-standards.md)
