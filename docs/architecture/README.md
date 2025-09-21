# 架构设计文档

本目录包含电商平台的系统架构设计文档，遵循IEEE 830标准的六层架构体系。

## 目录结构

```
docs/architecture/
├── README.md                          # 本文件：目录导航和结构说明
├── overview.md                        # 架构总览：整体架构设计和技术选型
├── business-architecture.md           # 业务架构：30个业务模块的领域设计
├── application-architecture.md        # 应用架构：模块化单体技术架构
├── data-architecture.md              # 数据架构：数据模型和存储设计
├── infrastructure-architecture.md     # 基础设施架构：基础设施和运维架构
├── migration-roadmap.md              # 架构演进路线：从单体到微服务演进策略
├── security.md                       # 安全架构：电商平台安全体系设计
├── integration.md                    # 集成架构：外部系统集成方案
└── _archive/                         # 归档目录：已废弃的历史架构文档
    ├── table-module-mapping.md       # 已归档：表-模块分配设计
    ├── module-architecture.md        # 已归档：模块架构设计
    ├── data-models.md               # 已归档：数据模型设计
    ├── event-driven.md              # 已归档：事件驱动架构设计
    ├── deployment-architecture.md    # 已归档：部署架构设计
    ├── module-catalog.md            # 已归档：模块目录
    ├── dependency-architecture.md    # 已归档：依赖架构设计
    └── data-access-architecture.md   # 已归档：数据访问架构设计
```

## 文档功能说明

### 📋 核心架构文档（必读）
| 文档名称 | 功能定位 | 适用人员 |
|---------|---------|---------|
| [overview.md](overview.md) | 系统整体架构设计和技术选型决策 | 全体技术人员 |
| [business-architecture.md](business-architecture.md) | 30个业务模块的领域建模和业务流程设计 | 业务分析师、产品经理 |
| [application-architecture.md](application-architecture.md) | 模块化单体应用的技术架构实现 | 应用开发者、后端工程师 |
| [data-architecture.md](data-architecture.md) | 数据模型设计和存储架构方案 | 数据工程师、DBA |
| [infrastructure-architecture.md](infrastructure-architecture.md) | 基础设施和运维架构设计 | 运维工程师、DevOps |
| [migration-roadmap.md](migration-roadmap.md) | 架构演进策略和实施计划 | 架构师、技术负责人 |

### 🔧 专项架构文档（深入阅读）
| 文档名称 | 功能定位 | 适用人员 |
|---------|---------|---------|
| [security.md](security.md) | 电商平台安全体系和防护方案 | 安全工程师、后端开发 |
| [integration.md](integration.md) | 外部系统集成架构和接口设计 | 集成开发、API开发 |

## 快速导航

### 👥 按角色查阅
- **架构师** → [overview.md](overview.md) → [migration-roadmap.md](migration-roadmap.md)
- **业务分析师** → [business-architecture.md](business-architecture.md)
- **应用开发者** → [application-architecture.md](application-architecture.md)
- **数据工程师** → [data-architecture.md](data-architecture.md)
- **运维工程师** → [infrastructure-architecture.md](infrastructure-architecture.md)
- **安全工程师** → [security.md](security.md)

### 🎯 按场景查阅
- **项目启动** → overview.md → business-architecture.md → application-architecture.md
- **系统集成** → integration.md → data-architecture.md
- **性能优化** → infrastructure-architecture.md → migration-roadmap.md
- **安全加固** → security.md → infrastructure-architecture.md
- **架构演进** → migration-roadmap.md → application-architecture.md

## 相关文档

- [需求文档](../requirements/) - 架构设计的输入依据
- [开发文档](../development/) - 基于架构的开发指南
- [运维文档](../operations/) - 基于架构的部署运维方案