---
title: "Document Management Standards"
version: "v3.0.0"
status: "Active"
created: "2025-09-27"
updated: "2025-09-27"
owner: "Documentation Governance Board"
dependencies:
	- "../../PROJECT-FOUNDATION.md"
	- "./naming-conventions-standards.md"
labels:
	- "standard"
	- "l1"
	- "documentation"
---

# 文档管理标准（Document Management Standards）

> **版本**: v3.0.0  
> **状态**: 执行中（Active）  
> **更新日期**: 2025-09-27  
> **发布单位**: 文档治理委员会（Documentation Governance Board）  
> **适用范围**: ecommerce_platform 项目 docs/ 目录及其文档生命周期全流程  
> **关键依赖**: [PROJECT-FOUNDATION.md](../../PROJECT-FOUNDATION.md)、[naming-conventions-standards.md](./naming-conventions-standards.md)

---

## 导航总览（Navigation Overview）

| 层级 | 内容重点 | 目标输出 | 预计行数占比 |
|------|----------|----------|--------------|
| I. 基础定义层 | 管什么、边界是什么、依赖是谁 | 管理范围矩阵、边界声明、权威依赖 | ~20% |
| II. 标准规范层 | 具体怎么做、每类文档标准细则 | A/B/C 三类 30 个文档标准、检测机制 | ~60% |
| III. 执行指导层 | 如何执行、如何检查 | 决策树、维护触发器、检查清单、工具集成 | ~20% |

- [I. 基础定义层](#i-基础定义层)
- [II. 标准规范层](#ii-标准规范层)
- [III. 执行指导层](#iii-执行指导层)
- [附录](#附录)

---

## I. 基础定义层

> **作用**：明确“管什么”、“管到什么程度”、“与谁配合”，建立文档治理的统筹边界和权威依赖体系。

### 1.1 管理范围与边界矩阵（Scope & Boundary Matrix）

| 文档域 | 管理责任 | 主要输出 | 外部交接标准 | 边界说明 |
|--------|----------|----------|----------------|----------|
| docs/ 根目录 | ✅ 本标准负责 | 目录结构、README、索引类文档 | PROJECT-FOUNDATION.md | 管理结构与内容质量，不约束代码实现 |
| docs/ 子目录 | ✅ 本标准负责 | 模块文档、专题文档、状态文档 | naming-conventions-standards.md | 管理存放位置、模板、元数据、格式 |
| 根目录 README.md | ✅ 本标准负责 | 项目总览、导航、健康状态 | PROJECT-FOUNDATION.md | 内容侧对接项目基础标准 |
| 根目录 MASTER.md | ✅ 本标准负责 | 检查点、执行状态 | dev_checkpoint.ps1 | 负责结构与内容一致性 |
| app/ 内部文档 | ❌ code-standards.md | 内联代码注释、模块说明 | code-standards.md | 本标准不处理代码内文档 |
| tests/ 内部文档 | ❌ testing-standards.md | 测试计划、测试脚本说明 | testing-standards.md | 本标准仅引用测试结果，不定义测试详细流程 |
| scripts/ 文档 | ✅ 本标准协同 | 工具说明、使用指南 | tools/ 文档模板 | 格式由本标准定义，脚本细节由工具维护团队负责 |
| docs/_archive/ | ✅ 本标准负责 | 归档策略、分类索引 | release-to-main.ps1 | 管理归档流程与模板 |
| docs/templates/ | ✅ 本标准负责 | 模板、占位符规范 | create_module_docs.ps1 | 管理模板结构、变量格式 |

### 1.2 职责声明与治理角色（Accountability & Governance Roles）

- **标准所有者（Document Governance Board）**：负责本标准的维护、升级和监督执行。
- **模块负责人（Module Owner）**：落实模块范围内的文档标准，确保 A 类文档实时更新。
- **质量负责人（QA Lead）**：维护自动化检查脚本、监督文档质量检查指标。
- **技术负责人（Tech Lead）**：监督设计与实现类文档的准确性与一致性。
- **运营负责人（Ops Lead）**：确保运维类文档、应急文档的及时更新和操作性。

职责对照表：

| 角色 | 主要职责 | 关键输出 | 协同对象 |
|------|----------|----------|----------|
| 标准所有者 | 标准更新、审计 | 标准版本发布、执行报告 | 所有角色 |
| 模块负责人 | 模块文档维护 | 模块 README、overview、design | Tech Lead、QA Lead |
| QA Lead | 自动化检测、质量审查 | 检测脚本、质量报告 | Ops Lead、标准所有者 |
| Tech Lead | 架构与设计文档监督 | design.md、implementation.md | 模块负责人 |
| Ops Lead | 运维流程与应急文档 | deployment-design、应急文档 | QA Lead、标准所有者 |

### 1.3 权威依赖关系（Authoritative Dependency Chain）

```
PROJECT-FOUNDATION.md
		↓（定义项目全局目录结构与角色）
naming-conventions-standards.md
		↓（定义命名规则、目录命名、文件命名）
document-management-standards.md（本文）
		↓（定义文档类型、模板、质量机制、执行流程）
module-specific-standards.md / scripting-standards.md / testing-standards.md
```

- **继承关系**：本标准继承 PROJECT-FOUNDATION.md 中对 docs/ 的定位，遵守 naming-conventions-standards.md 的命名规则。
- **约束关系**：下游标准（如 testing-standards.md）必须遵从本标准的结构、元数据、归档要求。
- **冲突处理**：若发现冲突，以上游标准为准，并通过 ADR 记录调整。

### 1.4 四层文档体系定义（Four-Layer Documentation Architecture）

| 层级 | 功能定位 | 代表目录 | 典型文档 | 管理重点 |
|------|----------|----------|----------|----------|
| Requirements Layer | 需求与业务场景 | docs/requirements/ | requirements.md、user-stories.md | 明确业务背景、验收标准 |
| Architecture Layer | 全局架构与模块边界 | docs/architecture/ | overview.md、system-architecture.md | 统一架构视图、模块接口 |
| Design Layer | 模块与组件设计实现 | docs/design/modules/<module>/design/ | design.md、implementation.md、api-spec.md | 设计细节、接口与实现一致性 |
| Standards Layer | 标准与流程规范 | docs/standards/ | document-management-standards.md、naming-conventions-standards.md | 权威标准、流程规范 |

### 1.5 与其他标准的边界矩阵（Boundary Matrix）

| 本标准管理 | 其他标准管理 | 交接点 | 交接机制 |
|--------------|----------------|--------|----------|
| 文档格式规范 | code-standards.md | 格式 vs 代码规范 | 通过自动化检查共享规则 |
| 文档创建维护流程 | tooling-standards.md | 流程 vs 工具脚本 | PR 模板、脚本接口文档 |
| 测试文档结构 | testing-standards.md | 文档结构 vs 测试用例细节 | 测试评审会议、标准同步 |
| 运维文档模板 | ops-standards.md | 模板 vs 运维流程 | Ops 例会同步模板变更 |
| ADR 文档标准 | architecture-decision-standards.md | 模板 vs 决策流程 | ADR 看板、每周同步 |

### 1.6 标准适用对象（Stakeholder Coverage）

- **开发团队**：识别并维护模块/组件文档，确保设计与实现同步。
- **测试团队**：依据文档标准维护测试策略、状态报告。
- **运维团队**：使用统一模板维护部署、应急、运维手册。
- **产品团队**：参与业务文档、需求文档规范化。
- **自动化系统**：基于本标准执行文档扫描、格式检测、触发器判断。

### 1.7 版本管理策略（Versioning Strategy）

- **主版本（Major）**：架构性调整（如本次三层架构重构）
- **次版本（Minor）**：新增文档类型、优化模板、调整检测项
- **补丁版本（Patch）**：修复错别字、链接错误、格式瑕疵
- **版本标记**：采用语义化版本（SemVer）并在 Front Matter 中声明
- **变更流程**：
	1. 通过 ADR 提出重大变更（必须记录编号）
	2. 在规划会上审议，标准所有者批准
	3. 更新文档并在 MASTER.md 中登记
	4. 通知所有相关责任人并执行培训

### 1.8 风险与防护策略（Risk & Mitigation）

| 风险 | 可能影响 | 防护措施 |
|------|----------|----------|
| 文档过期 | 决策错误、实现偏差 | 维护触发器、季度审查、自动化提醒 |
| 标准执行不一致 | 文档质量下降 | 决策树流程、自动化检查、人工抽查 |
| 新文档类型缺乏标准 | 文档混乱 | 模板创建流程、ADR 审批 |
| 冗余文档堆积 | 查找困难 | 重复性检测、归档策略、合并流程 |
| 工具脚本失效 | 自动化中断 | QA Lead 定期校验脚本、版本锁定 |

### 1.9 执行里程碑（Execution Milestones）

- **v3.0.0 发布**：三层架构上线、30 个文档标准更新、自动化检查项同步
- **+30 天**：完成所有现有文档向新标准迁移的初步审计
- **+60 天**：执行第一次季度审查，评估执行效果与问题
- **+90 天**：汇总经验，视情况发布 v3.1.0 次版本

---

## II. 标准规范层

> **作用**：提供 A/B/C 三类共 30 个文档的可执行标准，包括模板、内容要求、边界定义、自动化检测点。

### 2.0 分类体系总览（Classification Overview）

| 类别 | 编号范围 | 功能定位 | 详细程度 | 负责人 |
|------|----------|----------|----------|--------|
| A 类（核心） | A1-A19 | 高频、关键、权威文档 | 详细标准（模板+内容+维护+边界） | 模块负责人 + 标准所有者 |
| B 类（辅助） | B1-B8 | 支撑性、流程类文档 | 中等标准（结构+场景+维护） | QA Lead + Ops Lead |
| C 类（特殊） | C1-C3 | 临时、应急、迁移场景 | 简化标准（说明+触发+处理） | Ops Lead + Tech Lead |

### 2.1 A 类核心文档标准（A1-A19）

> **说明**：以下每个文档包括 6 个维度——定位、存放位置、模板结构、内容要求、维护规则、禁止内容及自动化检测点。

#### A1. 根目录 README.md 标准

- **定位**：项目总览、团队协作入口、外部沟通入口。
- **存放路径**：`README.md`
- **模板结构**：
	1. 项目简介（含一句话描述 + 核心价值）
	2. 快速导航（目录索引、模块入口、标准入口）
	3. 快速开始（环境准备、启动步骤）
	4. 项目结构概览（目录树 + 说明）
	5. 执行状态与健康检查入口（链接 MASTER.md）
	6. 联系方式与支撑资源
- **内容要求**：
	- 强制包含项目头像/Logo（如有）或替代描述
	- 提供 docs/ 根目录的聚合链接
	- 引导读者了解 ADR、测试、发布等关键流程
- **维护规则**：
	- 重大发布前后更新运行指引
	- 保持与 docs/README.md 导航一致
	- 采用季度审查机制
- **禁止内容**：实现细节、敏感配置、个人隐私信息
- **自动化检测点**：
	- `pwsh tools/sync_readme.ps1 -Path docs` 确保导航与 docs/README.md 同步
	- `pwsh tools/validate_standards.ps1 -Action format` 验证结构、链接与 Front Matter 元数据

#### A2. 目录 README.md 标准

- **定位**：描述当前目录的职责、子目录结构、维护责任人。
- **存放路径**：`docs/**/README.md`
- **模板结构**：
	1. 目录功能定位
	2. 子目录一览（表格列出名称、描述、责任人、更新时间）
	3. 关键文档列表（链接 + 说明）
	4. 维护职责（责任人、审查频率）
	5. 变更历史摘要（可链接到详细记录）
- **内容要求**：
	- 每个子目录必须至少有一句描述
	- 标注最新更新时间与责任人
	- 说明与其他目录的协作关系
- **维护规则**：新增/删除子目录时必须更新
- **禁止内容**：详细实现步骤、测试结果详情
- **自动化检测点**：
	- `pwsh tools/validate_standards.ps1 -Action format` 检查表格结构与标题层级
	- `pwsh tools/validate_standards.ps1 -Action dependencies` 确保不越界引用

#### A3. 模块 README.md 标准

- **定位**：模块级别（如 `docs/design/modules/payment/README.md`）的概览与维护总览。
- **模板结构**：
	1. 模块简介（业务目标、范围）
	2. 模块结构（包含 design/、implementation/、api/ 等子目录说明）
	3. 模块边界（与其他模块的接口、依赖）
	4. 状态与健康指标（链接 module-status.md）
	5. 责任团队与联系
- **内容要求**：
	- 清晰列出上下游依赖
	- 标注与微服务的映射关系（如适用）
	- 提供快速跳转至关键文档
- **维护规则**：
	- 模块接口变化时立即更新
	- 与 module-status.md 保持一致
- **禁止内容**：实现细节、敏感配置
- **自动化检测点**：
	- `pwsh tools/validate_standards.ps1 -Action dependencies` 检查越界引用
	- `pwsh tools/validate_standards.ps1 -Action full` 验证链接有效性

#### A4. 组件 README.md 标准

- **定位**：组件级（如 `docs/design/modules/payment/components/checkout/README.md`）的内部说明。
- **模板结构**：
	1. 组件职责
	2. 组件接口（公开接口、事件、消息）
	3. 依赖组件/服务
	4. 部署或集成要点（如适用）
	5. 维护人 & 审查节奏
- **内容要求**：
	- 明确组件在模块中的位置（可使用简图）
	- 标注关键接口与依赖
	- 提供指向设计文档、API 文档的链接
- **维护规则**：组件接口变化时必须更新
- **禁止内容**：业务需求描述（应在模块或需求层维护）
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action dependencies`

#### A5. 工具 README.md 标准

- **定位**：描述 `scripts/`、`tools/` 内工具的使用说明。
- **模板结构**：
	1. 工具概要（功能描述、适用场景）
	2. 使用前提（依赖、配置）
	3. 使用步骤（命令示例、参数说明）
	4. 输出结果（日志位置、成功/失败判定）
	5. 故障排查（常见错误、解决方案）
- **内容要求**：提供至少一个示例命令与示例输出
- **维护规则**：工具脚本变更必须同步更新
- **禁止内容**：暴露敏感凭据、内部 IP
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action format` 校验命令格式与代码块

#### A6. overview.md 标准（模块概览）

- **定位**：模块级别概览，描述模块目标、边界、关键组件。
- **存放路径**：`docs/design/modules/<module>/overview.md`
- **模板结构**：
	1. 模块简介（目标、背景）
	2. 模块边界与职责
	3. 模块内部结构图（文字描述 + 图像链接）
	4. 上下游依赖（表格列出来源/去向）
	5. 关键指标（性能、可用性、关键 SLA）
	6. 变更历史摘要
- **内容要求**：必须引用最新的 system-architecture 图或链接
- **维护规则**：架构变更、依赖调整后立即更新
- **禁止内容**：实现细节、代码片段（应放在 design 或 implementation）
- **自动化检测点**：
	- `pwsh tools/validate_standards.ps1 -Action full`
	- `pwsh tools/validate_standards.ps1 -Action format` 验证图像引用格式

#### A7. requirements.md 标准（需求文档）

- **定位**：记录模块/功能的业务需求、场景、验收标准。
- **存放路径**：`docs/requirements/<topic>/requirements.md`
- **模板结构**：
	1. 背景与业务目标
	2. 利益相关者
	3. 功能需求列表（需求编号、描述、优先级、验收标准）
	4. 非功能需求（性能、安全、易用性）
	5. 依赖与约束
	6. 验收标准与测试策略
	7. 变更记录
- **内容要求**：需求编号采用 `REQ-<module>-<id>` 格式
- **维护规则**：需求确认、变更时必须更新，保持历史记录
- **禁止内容**：详细设计或实现步骤（应在 design/implementation）
- **自动化检测点**：
	- `python tools/generate_test_template.py <module>` 用于生成用例模板
	- `pwsh tools/validate_standards.ps1 -Action format` 校验需求编号格式

#### A8. design.md 标准（详细设计）

- **定位**：描述模块内部的详细设计，包括数据结构、流程、接口。
- **存放路径**：`docs/design/modules/<module>/design/design.md`
- **模板结构**：
	1. 引言（设计目标、范围）
	2. 设计概览（架构图、组件分层）
	3. 数据模型（实体、关系、字段说明）
	4. 业务流程（时序图、活动图）
	5. 接口设计（API、事件、消息格式）
	6. 安全考虑与风险控制
	7. 扩展性与性能考量
	8. 变更影响分析
- **内容要求**：
	- 必须引用 requirements.md 中的需求编号
	- 图示应包含描述性文本
	- 所有接口需指向 api-spec.md
- **维护规则**：设计变更前需评审，变更后 24 小时内更新
- **禁止内容**：具体代码实现
- **自动化检测点**：
	- `pwsh tools/maintain_standards.ps1 -Action check -Target docs/design/modules/<module>/design/design.md`
	- `pwsh tools/validate_standards.ps1 -Action full -DocPath docs/design/modules/<module>/design/design.md`

#### A9. implementation.md 标准（实现说明）

- **定位**：描述设计如何落地实施、涉及的关键代码、部署注意事项。
- **存放路径**：`docs/design/modules/<module>/design/implementation.md`
- **模板结构**：
	1. 实现概览（对应的 design.md 章节引用）
	2. 代码结构映射（目录、关键类/函数说明）
	3. 数据库与存储（表结构、索引、迁移）
	4. 异常与错误处理策略
	5. 性能优化手段
	6. 日志与监控埋点
	7. 部署与回滚策略
- **内容要求**：
	- 引用设计中对应章节
	- 提供关键代码片段或伪代码（保持概念层）
	- 标注日志指标、告警阈值
- **维护规则**：上线前必审，发布后若实现调整需同步
- **禁止内容**：冗长的代码块（限制在 30 行以内）
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action format -DocPath docs/design/modules/<module>/design/implementation.md` 验证代码块语言标识

#### A10. api-spec.md 标准（API 规范）

- **定位**：定义 API 接口的规范，包括请求、响应、错误码。
- **存放路径**：`docs/design/modules/<module>/api/api-spec.md`
- **模板结构**：
	1. API 概览（服务描述、版本）
	2. 认证与授权要求
	3. 接口列表（表格：名称、方法、路径、描述、幂等性）
	4. 请求参数（表格，含类型、是否必填、说明）
	5. 响应结构（嵌套 JSON 示例 + 字段说明）
	6. 错误码与处理策略
	7. 变更日志
- **内容要求**：
	- 路径命名遵循 RESTful 原则
	- 必须指定数据类型与取值范围
	- 必须声明幂等性与重试策略
- **维护规则**：任何接口变动需提前更新并通知客户端
- **禁止内容**：未定义的错误码、模糊描述
- **自动化检测点**：
	- `python tools/api_service_mapping_analyzer.py --analyze <module>` 校验接口映射
	- `pwsh tools/validate_standards.ps1 -Action full -DocPath docs/design/modules/<module>/api/api-spec.md`

#### A11. api-implementation.md 标准（API 实现说明）

- **定位**：描述 API 规范如何在代码中实现，包含路由、服务层映射、监控。
- **模板结构**：
	1. 实现概览（对应 api-spec.md 版本）
	2. 路由与控制器映射表
	3. 业务逻辑层实现摘要
	4. 数据访问层说明（ORM、查询、缓存）
	5. 监控与日志（指标、采集方式）
	6. 错误处理与回退机制
	7. 集成测试覆盖范围
- **内容要求**：
	- 每个 API 必须对应代码路径
	- 标注监控指标与告警策略
- **维护规则**：API 规范更新后 24 小时内同步调整
- **禁止内容**：重复 api-spec.md 的完整内容
- **自动化检测点**：`python tools/api_service_mapping_analyzer.py --generate-test <module>`

#### A12. database-design.md 标准

- **定位**：定义模块或系统涉及的数据库结构、索引、约束。
- **模板结构**：
	1. 数据库概览（类型、版本、部署策略）
	2. 模式设计（ER 图、表清单）
	3. 表结构详解（字段、类型、约束、默认值）
	4. 索引策略（索引类型、覆盖字段、维护策略）
	5. 数据迁移策略（版本管理、回滚方案）
	6. 安全与合规（加密、脱敏、权限）
	7. 备份与恢复策略
- **内容要求**：
	- 使用统一表格格式描述字段信息
	- 对应 implementation.md 中的数据操作
- **维护规则**：数据库变更需提前评审，更新后同步 migration 脚本
- **禁止内容**：直贴 SQL 脚本（应存于 migrations）
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action format -DocPath docs/design/modules/<module>/design/database-design.md` 验证表格完整性

#### A13. technology-stack-standards.md 标准

- **定位**：记录项目技术栈、框架、版本、维护策略。
- **模板结构**：
	1. 技术栈概览（前端、后端、数据库、基础设施）
	2. 组件列表（名称、版本、用途、维护人、替代方案）
	3. 版本升级策略（周期、测试要求）
	4. 风险与兼容性说明
	5. 技术债务与淘汰计划
- **内容要求**：
	- 每个组件必须包含当前版本与目标版本
	- 标注升级窗口与回滚策略
- **维护规则**：季度审查；新技术引入需 ADR 批准
- **禁止内容**：未经验证的技术建议
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action format -DocPath docs/standards/technology-stack-standards.md` 验证表格结构

#### A14. testing-standards.md 标准

- **定位**：统一 tests/ 目录的层级结构、命名规范、用例设计与执行流程。
- **模板结构**：
	1. 测试策略概览（范围、目标、覆盖率指标）
	2. 目录结构说明（unit/integration/e2e/performance/security 等）
	3. 用例模板与命名规范
	4. 测试数据与环境要求
	5. 执行流程与报告机制
	6. 质量门禁与准入准出标准
- **内容要求**：
	- 明确各层级测试职责、覆盖率目标
	- 提供示例命名/目录结构，指向模板或案例
	- 说明与 CI/CD、测试工厂脚本的集成方式
- **维护规则**：
	- 新增测试类型或变更目录结构时更新
	- 与 `tools/run_module_tests.ps1`、`tools/integration_test.ps1` 流程保持一致
- **禁止内容**：与代码实现重复的细节、过期的测试指标
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action content -DocPath docs/standards/testing-standards.md`

#### A15. performance-standards.md 标准

- **定位**：性能目标、容量规划、测试策略。
- **模板结构**：
	1. 性能目标（SLA、SLO、SLI）
	2. 关键路径分析
	3. 容量规划（QPS、峰值、冗余策略）
	4. 性能测试计划（工具、场景、基准）
	5. 监控指标与告警阈值
	6. 优化策略与演进计划
- **内容要求**：所有指标需量化；提供历史趋势链接
- **维护规则**：重大版本发布前更新；性能事件后复盘
- **禁止内容**：无验证的性能猜测
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action content -DocPath docs/standards/performance-standards.md`

#### A16. deployment-standards.md 标准

- **定位**：部署架构、环境要求、回滚策略。
- **模板结构**：
	1. 部署拓扑（环境列表、拓扑图）
	2. 部署流程（步骤、执行人、自动化工具）
	3. 环境配置（变量、密钥、依赖服务）
	4. 回滚策略与标准
	5. 监控与验证步骤
	6. 灰度/蓝绿/金丝雀策略（如适用）
- **内容要求**：
	- 明确每个环境的差异
	- 提供回滚时间与责任人
- **维护规则**：部署流程变更需 24 小时内更新
- **禁止内容**：暴露敏感配置值
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action content -DocPath docs/standards/deployment-standards.md`

#### A17. issues-tracking.md 标准

- **定位**：问题管理、缺陷跟踪、响应策略。
- **模板结构**：
	1. 管理范围（缺陷、任务、风险）
	2. 跟踪流程（发现→分析→解决→验证→关闭）
	3. 状态与 SLA（表格：状态、说明、响应时间）
	4. 分级策略（严重级别、升级路径）
	5. 报告与指标（缺陷率、处理周期）
	6. 工具与自动化集成（如 Jira、GitHub Issues）
- **内容要求**：与 QA 流程保持一致
- **维护规则**：流程调整时更新；季度审查指标
- **禁止内容**：具体问题细节（应在 issue 系统中维护）
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action format -DocPath docs/status/issues-tracking.md`

#### A18. module-status.md 标准

- **定位**：模块级状态看板，展示健康度、里程碑、风险。
- **模板结构**：
	1. 模块概览（名称、负责人、当前版本）
	2. 状态指标（表格：指标、当前值、阈值、趋势）
	3. 里程碑与进展（时间线）
	4. 风险与阻塞项（描述、负责人、解决日期）
	5. TODO 与下一步计划
- **内容要求**：
	- 指标需与监控数据保持一致
	- 提供数据来源链接（Grafana、日志等）
- **维护规则**：每周更新；发布前强制更新
- **禁止内容**：无责任人
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action format -DocPath docs/status/module-status.md`

#### A19. work-history-archive.md 标准

- **定位**：归档模块或项目的历史记录、经验总结。
- **模板结构**：
	1. 归档范围概述（时间范围、模块、责任人）
	2. 归档任务列表（表格：任务、描述、完成时间、贡献者）
	3. 关键里程碑与成果
	4. 经验教训与最佳实践
	5. 后续改进建议
- **内容要求**：保留关键信息和成果，不得删除
- **维护规则**：每次归档操作后更新；季度审查一次
- **禁止内容**：敏感数据、个人隐私
- **自动化检测点**：`pwsh tools/validate_standards.ps1 -Action content -DocPath docs/_archive/work-history-archive.md`

### 2.2 B 类辅助文档标准（B1-B8）

> **说明**：提供中等详度的结构要求、使用场景、维护策略。

#### B1. ADR 决策记录标准

- **定位**：架构与战略性技术决策的权威记录，存放于 `docs/adr/`。
- **结构要求**：Status、Date、Context、Decision、Consequences、References、Related、Implementation Plan。
- **使用场景**：任何影响架构边界、技术栈、关键依赖、法规合规的决策。
- **元数据要求**：Front Matter 必须包含 `adr_id`、`status`、`deciders`、`date`、`supersedes`（可选）。
- **维护规则**：
	- 使用 `ADR-<四位编号>-<kebab-case-标题>.md` 命名。
	- `docs/adr/README.md` 维护索引、状态、负责人。
	- 决策状态需及时更新（Proposed → Accepted → Superseded）。
	- 决策被废弃时必须标注 superseded-by 条目并在索引中同步。
- **禁止内容**：模糊的决策描述、缺少后果分析、未经批准的草稿。
- **自动化检测**：
	- `pwsh tools/maintain_standards.ps1 -Action check` 运行标准体系健康检查，将全局告警作为 ADR 审核的参考输入。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/adr/ADR-0001-*.md` 检查代码块标记成对、语言标识是否缺失。
	- `Get-ChildItem docs/adr | Sort-Object Name` 手动核对编号连续性并同步 `docs/adr/README.md` 索引。

#### B2. 分析报告标准（analysis reports）

- **定位**：对系统或业务进行专项分析的正式报告，存放于 `docs/analysis/`。
- **结构要求**：
	1. 背景与目标
	2. 问题定义与范围
	3. 数据来源与假设
	4. 分析方法与步骤（含工具、脚本）
	5. 结果与洞察（可视化说明）
	6. 建议与行动项
	7. 限制与后续工作
	8. 附录与原始数据链接
- **使用场景**：性能压测、容量规划、安全评估、成本分析、实验结果总结等。
- **维护规则**：
	- 完成后在 `docs/analysis/README.md` 登记摘要。
	- 若建议被采纳，应建立 Follow-up Issue 并在文档中引用。
	- 历史报告按年度归档。
- **禁止内容**：未经验证的数据、缺乏来源的结论、敏感原始数据（应单独加密存储）。
- **自动化检测**：
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/analysis/<report>.md` 快速审查 Markdown 代码块、表格语法。
	- `python tools/e2e_test_verification.py --json` 触发端到端验证流程并生成最新的分析报告、JSON 摘要。

#### B3. 模板文档标准

- **定位**：提供各类文档的标准模板，存放于 `docs/templates/`。
- **结构要求**：
	1. 模板用途与适用范围
	2. 模板结构（章节列表）
	3. 变量定义（`{variable_name}` 或 `[[PLACEHOLDER]]`）
	4. 填写说明（示例、注意事项）
	5. 版本信息与维护人
- **维护规则**：
	- 新模板发布前需通过 ADR 审批。
	- 变更后必须更新 `docs/templates/README.md` 索引。
	- 模板废弃需标记并迁移至 `_archive`。
- **禁止内容**：硬编码具体模块信息、敏感配置。
- **自动化检测**：
	- `pwsh tools/create_module_docs.ps1 -ModuleName sample-module -Force` 验证模板变量可渲染并覆盖完整模块文档骨架。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/templates/module-template.md` 校验占位符与代码块标记。

#### B4. 检查点卡片标准

- **定位**：定义AI工作流程检查点的标准格式，存放于 `tools/checkpoint-cards.md`。
- **结构要求**：
	1. 卡片标题（检查点编号 + 功能描述）
	2. 触发条件（明确的触发场景）
	3. 检查重点（核心验证项目）
	4. 精准导航（文档路径 + 行号范围）
	5. 阅读确认（强制文档阅读验证）
	6. 执行脚本（自动化验证工具）
	7. 辅助脚本（可选的补充工具）
- **阅读确认标准**：
	- **描述**：执行脚本前必须打开并阅读指定文档片段
	- **操作要求**：脚本内调用Editor打开文档或提示用户回答验证问题
	- **内容原则**：卡片内不给任何概括信息，只给导航和要求
	- **问题设计**：每个卡片根据需要AI阅读的内容给出具体问题，问题要具体，不阅读无法根据推测回答
- **格式标准**：
	```markdown
	### [编号]: [功能描述]
	**触发条件**: [具体触发场景]
	**检查重点**: [核心验证要求]
	**精准导航**:
	1. **[验证项1]** → `[文档路径]` 第[X-Y]行
	2. **[验证项2]** → `[文档路径]` 第[X-Y]行
	**阅读确认**:
	问题1: [针对文档内容的具体问题，无法推测回答]
	问题2: [针对文档内容的具体问题，无法推测回答]
	**执行脚本**: `[脚本路径]`
	```
- **维护规则**：
	- 所有文档路径必须真实存在且行号准确
	- 检查重点必须与MASTER.md中的检查点列表对应
	- 脚本路径必须经过验证确保可执行
- **禁止内容**：规则描述、标准定义（应引用对应的标准文档）
- **自动化检测**：
	- `tools/validate_checkpoint_cards.ps1` 验证卡片格式和引用准确性
	- `tools/check_docs.ps1` 检查文档路径和脚本存在性

#### B5. 工具文档标准

- **定位**：记录脚本及自动化工具的使用说明，可放置于 `docs/tools/` 或对应 `scripts/` 目录。
- **结构要求**：
	1. 工具概述（功能、适用环境）
	2. 依赖与安装（系统要求、Python 包、权限）
	3. 使用说明（命令、参数、示例）
	4. 输出与结果解读（日志路径、成功标准）
	5. 故障排查（常见错误、恢复步骤）
	6. 维护计划与责任人
- **维护规则**：
	- 工具变更必须同步文档。
	- 重大升级需记录在 work-history-archive.md。
- **禁止内容**：暴露密钥、内部 IP、账号密码。
- **自动化检测**：
	- `pwsh tools/dev_tools.ps1 -Command check-db` 验证文档示例命令真实可执行，及时捕捉接口变化。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/tools/<doc>.md` 检查命令示例的 Markdown 结构。

#### B5. 工具文档标准

- **定位**：记录脚本及自动化工具的使用说明，可放置于 `docs/tools/` 或对应 `scripts/` 目录。
- **结构要求**：
	1. 工具概述（功能、适用环境）
	2. 依赖与安装（系统要求、Python 包、权限）
	3. 使用说明（命令、参数、示例）
	4. 输出与结果解读（日志路径、成功标准）
	5. 故障排查（常见错误、恢复步骤）
	6. 维护计划与责任人
- **维护规则**：
	- 工具变更必须同步文档。
	- 重大升级需记录在 work-history-archive.md。
- **禁止内容**：暴露密钥、内部 IP、账号密码。
- **自动化检测**：
	- `pwsh tools/dev_tools.ps1 -Command check-db` 验证文档示例命令真实可执行，及时捕捉接口变化。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/tools/<doc>.md` 检查命令示例的 Markdown 结构。

#### B6. 检查点日志标准（checkpoint logs）

- **定位**：记录阶段性检查、审核结论，存放于 `docs/status/checkpoints/`。
- **结构要求**：
	1. 检查点名称与编号
	2. 执行时间与参与者
	3. 检查范围与目标
	4. 结果总结（通过/需整改）
	5. 发现的问题（编号、描述、责任人、截止日期）
	6. 后续行动项与跟踪方式
- **维护规则**：
	- 检查完成后 24 小时内更新。
	- 行动项完成后需回填结果并关闭。
	- 重要检查点需在 MASTER.md 中引用。
- **禁止内容**：缺少时间戳、责任人、结论模糊。
- **自动化检测**：
	- `pwsh tools/log_status.ps1 -Message "Checkpoint <name>" -Branch <branch> -Author <owner>` 生成结构化检查点日志样板。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/status/checkpoints/<file>.md` 确认表格与列表语法正确。

#### B6. 规划文档标准

- **定位**：用于阶段规划（季度规划、路线图、项目计划），存放于 `docs/planning/`。
- **结构要求**：
	1. 背景与目标
	2. 范围与边界（包含不包含）
	3. 时间线与里程碑（表格）
	4. 资源计划（人员、预算、工具）
	5. 风险与缓解措施
	6. 跟踪指标与报告机制
	7. 与其他计划的依赖关系
- **维护规则**：
	- 每次评审后更新状态。
	- 延迟或范围变更需有备注与原因。
- **禁止内容**：未确认的承诺、缺乏来源的数字。
- **自动化检测**：
	- `pwsh tools/maintain_standards.ps1 -Action report -Target summary` 获取标准体系现状摘要，为规划评审提供输入依据。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/planning/<plan>.md` 检查表格、任务列表标记。

#### B7. 存档文档标准

- **定位**：存放已完成、历史参考或废弃文档，位于 `docs/_archive/`。
- **结构要求**：
	1. 归档说明（原因、发起人、日期）
	2. 归档内容索引（原路径、文档名称、标签）
	3. 访问方式与权限说明
	4. 恢复流程（条件、步骤、责任人）
	5. 关联 Issue/ADR/PR 链接
- **维护规则**：
	- 归档操作后立即更新索引。
	- 每季度审查是否需要继续保留或清理。
- **禁止内容**：直接删除无备份文档、缺少恢复说明。
- **自动化检测**：
	- `pwsh tools/maintain_standards.ps1 -Action backup` 在归档前为现有标准文档创建快照，确保可追溯。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/_archive/<file>.md` 提醒补全归档说明和链接。

#### B8. 运维文档标准

- **定位**：规范运维相关知识库及操作手册，位于 `docs/operations/`。
- **结构要求**：
	1. 运维范围与职责
	2. 日常操作手册（按任务拆分步骤）
	3. 监控指标与阈值（含 Dashboard 链接）
	4. 告警处理流程（分级响应、联系方式）
	5. 变更管理流程（审批、执行、回顾）
	6. 值班手册与联系方式
- **维护规则**：
	- 运维流程调整后 24 小时内更新。
	- 演练或真实事件后进行复盘并修改文档。
- **禁止内容**：泄露敏感系统信息、未经批准的操作流程。
- **自动化检测**：
	- `pwsh tools/maintain_standards.ps1 -Action report -Target metrics` 生成标准体系质量指标，支持运维文档更新对齐整体规范。
	- `pwsh tools/analyze_simple_markers.ps1 -FilePath docs/operations/<doc>.md` 校验脚本片段和链接语法。

### 2.3 C 类特殊文档标准（C1-C3）

> **说明**：提供简化标准，强调触发条件与处理流程。

#### C1. 迁移文档标准

- **触发条件**：系统迁移、数据迁移、平台切换、云服务变更。
- **结构要求**：
	1. 迁移背景与目标
	2. 影响范围（系统、用户、数据）
	3. 迁移前置条件（检查清单、审批）
	4. 迁移步骤与时间计划（含执行人）
	5. 回滚计划与触发条件
	6. 风险控制与缓解措施
	7. 沟通计划（通知对象、渠道、时间）
	8. 迁移后验证（验证步骤、观察指标）
- **维护规则**：迁移计划确定后创建，执行过程中实时更新；完成后归档至 `_archive` 并记录结果。
- **禁止内容**：缺乏回滚方案、未确认的执行时间。
- **自动化检测**：`tools/check_docs.ps1`；迁移脚本校验工具（如有）。

#### C2. 应急文档标准

- **触发条件**：重大故障、生产事故、合规事件、灾备演练。
- **结构要求**：
	1. 事件分类与严重等级
	2. 触发阈值与判定标准
	3. 响应流程（检测、通知、执行、恢复、复盘）
	4. 分工矩阵（角色、职责、联系方式）
	5. 沟通模板（对内、对外）
	6. 恢复标准与验证步骤
	7. 复盘要求与模板链接
- **维护规则**：演练或真实事件后 48 小时内更新；每半年复核一次。
- **禁止内容**：假设性流程、缺少责任人的操作步骤。
- **自动化检测**：`tools/check_docs.ps1`；`tools/validate_links.ps1` 检查联系方式中的链接。

#### C3. 临时文档标准

- **触发条件**：临时任务、试点项目、快速实验、短期活动。
- **结构要求**：
	1. 背景与目标
	2. 时间范围与里程碑
	3. 任务分解与负责人
	4. 交付物列表（文档、脚本、报告）
	5. 依赖关系与资源需求
	6. 归档策略（完成后去向、保留期限）
- **维护规则**：任务完成后 7 天内归档或删除；若转为长期任务需升级为 A/B 类文档。
- **禁止内容**：长期信息、不受控的敏感数据。
- **自动化检测**：`tools/check_docs.ps1`；临时文档清理脚本（若存在）。

### 2.4 全局质量控制要求（Global Quality Requirements）

- **统一元数据**：所有文档使用 Front Matter 或首段表格声明标题、版本、状态、更新时间。
- **编号规范**：A/B/C 类文档在标题中标注编号（示例：“A7. requirements.md 标准”）。
- **标题层级**：最大到 `###`，避免深层嵌套。
- **图文描述**：任何图像链接必须提供文字描述与来源。
- **链接策略**：内部链接使用相对路径；外部链接注明访问日期。
- **语言要求**：中文为主，可在关键术语后添加英文说明。

### 2.5 自动化检测矩阵（Automation Matrix）

| 检测脚本 | 范围 | 主要检查项 | 触发方式 | 输出 |
|-----------|------|------------|----------|------|
| tools/check_docs.ps1 | 全部文档 | 标题、表格、代码块、front matter | 手动/CI | 控制台 + logs/
| tools/validate_links.ps1 | 核心文档 | 链接有效性 | CI | 控制台 + logs/
| tools/boundary_check.ps1 | A 类文档 | 越界引用、重复内容 | 手动/月度 | 控制台 + 报告
| tools/check_api.ps1 | API 文档 | 接口格式、参数完整性 | 手动/PR | 控制台
| scripts/sync_readme.ps1 | README 系列 | 导航一致性 | PR | 更新文件 + 日志

### 2.6 边界违规规则（Boundary Enforcement Rules）

- **禁止跨层引用**：需求层不得包含设计/实现细节；设计层不得包含实现代码。
- **禁止重复内容**：发现重复超过 30% 的内容必须合并或拆分。
- **禁止未经审批的模板**：新增模板必须经过标准所有者审批并记录。
- **禁止敏感信息**：任何文档不得包含密钥、密码、个人隐私等敏感数据。
- **禁止无责任人文档**：所有文档必须标注责任人，否则视为违规。

### 2.7 质量指标与量化目标（Quality KPIs）

| 指标 | 目标 | 采集方式 | 汇报周期 |
|------|------|----------|----------|
| 文档覆盖率 | ≥ 95% 核心模块具备 A 类文档 | 自动化扫描 + 抽查 | 季度 |
| 文档过期率 | ≤ 5% 超过 90 天未更新的关键文档 | 自动化提醒 + 人工审查 | 月度 |
| 链接失效率 | ≤ 2% | 链接检测脚本 | 月度 |
| 自动化检测通过率 | ≥ 98% | CI/CD 任务 | 持续 |
| 审核完成时效 | ≤ 3 个工作日 | PR 审核记录 | 月度 |

---

## III. 执行指导层

> **作用**：提供可操作的执行流程、决策树、维护触发器、质量检查单以及自动化工具集成方案。

### 3.1 文档创建执行决策树（Pre-Creation Decision Tree）

```
┌─📋 开始创建文档 ────────────────────────────────┐
│                                                  │
│ 1. 定义目标与范围                                │
│    ↓                                              │
│ 2. 重复性检查（搜索 docs/ 与 ISSUE/PR）           │
│    ├── 有现有文档 → ✅ 更新原文档，停止创建        │
│    └── 未发现 → 继续                              │
│             ↓                                      │
│ 3. 分类判定（A/B/C）                              │
│    ├── A 类 → 选择对应详细模板                    │
│    ├── B 类 → 选择辅助模板                        │
│    └── C 类 → 选择特殊模板                        │
│             ↓                                      │
│ 4. 准备元数据（Front Matter、责任人、版本）         │
│             ↓                                      │
│ 5. 填写模板内容（引用标准章节、保持结构）           │
│             ↓                                      │
│ 6. 自动化校验（check_docs、validate_links 等）      │
│             ↓                                      │
│ 7. PR 提交（引用相关 Issue/ADR，指派审核人）        │
│             ↓                                      │
│ 8. 审核通过 → 合并 → 更新触发器                   │
└───────────────────────────────────────────────────┘
```

### 3.2 维护触发器矩阵（Maintenance Triggers Matrix）

| 触发事件 | 影响文档 | 责任人 | 自动化脚本 | 完成时限 |
|----------|----------|--------|------------|----------|
| 新增模块注册 | modules/<module>/README.md、overview.md、design.md | 模块负责人 | scripts/create_module_docs.ps1 | 3 个工作日 |
| API 变更 | api-spec.md、api-implementation.md、implementation.md | 模块负责人 + Tech Lead | tools/check_api.ps1 | 1 个工作日 |
| 需求变更 | requirements.md、design.md、implementation.md | 产品负责人 + 模块负责人 | scripts/generate_test_template.py | 2 个工作日 |
| 部署策略调整 | deployment-design.md、ops 文档 | Ops Lead | scripts/check_docs.ps1 | 1 个工作日 |
| 安全事件 | security-design.md、应急文档 | Ops Lead + Security Team | tools/check_docs.ps1 | 24 小时 |
| 版本发布 | README.md、module-status.md、work-history-archive.md | 标准所有者 + QA Lead | tools/sync_readme.ps1 | 发布当日 |

### 3.3 质量控制检查清单（Quality Control Checklist）

#### 自动化检查项（必选）

- [ ] `tools/check_docs.ps1` 通过
- [ ] `tools/validate_links.ps1` 无失效链接
- [ ] `tools/boundary_check.ps1` 无越界引用
- [ ] `tools/check_api.ps1`（针对 API 相关文档）
- [ ] Front Matter 元数据完整（title/version/status/updated/owner）

#### 人工检查项（必选）

- [ ] 内容是否覆盖所有必要范围，未遗漏
- [ ] 是否严格遵守边界（需求 vs 设计 vs 实现）
- [ ] 是否引用最新的依赖文档与图表
- [ ] 是否标注责任人、审查频率、更新日期
- [ ] 是否附加相关 ADR、Issue、PR 链接
- [ ] 是否遵循命名规范（文件、目录、锚点）

#### 追加检查项（建议）

- [ ] 文档是否包含操作示例或截图（如需要）
- [ ] 是否包含 TODO 或 Follow-up 并指派责任人
- [ ] 是否包含合规性声明（如 GDPR、PCI-DSS）

### 3.4 自动化工具与流程集成（Automation & Workflow Integration）

#### 3.4.1 Git 工作流集成

- **Pre-commit Hook**：执行 `tools/check_docs.ps1`，阻止格式错误提交。
- **CI/CD Pipeline**：在 Pull Request 时运行 `tools/validate_links.ps1`、`tools/check_api.ps1`。
- **Merge Guard**：关键文档（A 类）变更需至少两名审核人批准（模块负责人 + 标准所有者）。
- **Release Checklist**：发布前自动生成受影响文档列表（通过 git diff + 分类规则）。

#### 3.4.2 AI 协作检查点

- **创建前检查**：AI 扫描 docs/ 中现有文档判断是否存在重复。
- **模板推荐**：根据分类（A/B/C）自动推荐对应模板与示例。
- **内容校验**：AI 对照标准核对章节完整性、编号、术语一致性。
- **触发器监控**：AI 根据 git 历史、Issue 标签提醒文档更新。
- **质量评审**：AI 生成审查报告（风险项、缺失章节、失效链接）。

#### 3.4.3 日志与可观测性

- 检查脚本输出保存在 `logs/`，按日期命名。
- 自动化流程失败时触发通知（Slack/Teams/邮件）。
- 定期分析日志统计违规类型分布。

### 3.5 季度审查工作流（Quarterly Review Workflow）

1. **启动**：标准所有者发布季度审查计划，列出重点模块。
2. **自动化扫描**：运行全量检测脚本，收集初步报告。
3. **人工抽查**：每个模块随机抽查至少 2 个 A 类文档。
4. **问题归类**：将问题分为立即处理、计划处理、观察。
5. **行动落实**：责任人提交修复 PR，QA Lead 验证。
6. **总结报告**：在 docs/status/ 目录记录审查结果与改进建议。

### 3.6 归档与废弃流程（Archiving & Decommission Process）

- **触发条件**：模块下线、功能废弃、项目阶段结束。
- **步骤**：
	1. 评估受影响文档（A/B/C 列表）。
	2. 标记文档状态为 Deprecated，并在 Front Matter 更新。
	3. 移动至 `docs/_archive/<year>/`，保留原路径索引。
	4. 在 README、导航文档更新指向。
	5. 更新 work-history-archive.md 记录归档行为与原因。

- **注意事项**：
	- 不得删除具有参考价值的历史文档。
	- 归档后需在 30 天内确认无引用再清理。

### 3.7 违规处理机制（Non-compliance Handling）

- **发现渠道**：自动化脚本、审核、季度审查、团队反馈。
- **处理流程**：
	1. 记录违规（文档名称、问题类型、发现人）。
	2. 指派责任人，设定纠正时限（默认 3 个工作日）。
	3. 纠正完成后由 QA Lead 验证。
	4. 累积违规进入改进计划，必要时召开专项复盘。

### 3.8 培训与推广（Enablement & Adoption）

- 每半年举办一次文档标准培训，涵盖三层架构、工具使用。
- 新成员入职 2 周内完成文档标准学习并签署确认。
- 在团队例会上分享优秀文档案例与经验。

### 3.9 指标监控与报告（Monitoring & Reporting）

- **月度**：输出文档质量报告（覆盖率、过期率、检测通过率）。
- **季度**：审查报告 + 改进计划。
- **年度**：总结执行情况、ROI、下一年度规划。

### 3.10 知识库与搜索集成（Knowledge Base & Search Integration）

- **统一索引**：所有文档通过 `docs/README.md` 与 `docs/search-index.json`（若存在）维护统一索引，AI 检索与人工搜索共用同一数据源。
- **标签体系**：采用标签（如 `module:payment`、`type:design`、`status:deprecated`）增强搜索精度，并在 Front Matter 中声明。
- **全文检索同步**：
	- 每次合并 PR 后触发 `scripts/sync_readme.ps1` 更新索引。
	- 如果启用外部搜索引擎（如 Algolia、ElasticSearch），通过 CI/CD 将增量变更推送。
- **跨团队共享**：对外共享文档需通过脱敏流程，生成只读版本并标记 `visibility:external`。
- **知识反馈闭环**：
	- 支持在文档末尾添加反馈入口（Issue 模板）。
	- 定期统计反馈主题，纳入季度审查。

### 3.11 数据驱动的持续改进（Data-driven Continuous Improvement）

- **指标采集**：
	- 通过自动化脚本收集检测结果、修复时长、违规类型。
	- 统计关键 KPI 的历史趋势（覆盖率、过期率、检测通过率）。
- **数据可视化**：
	- 将统计结果展示在 BI 仪表盘或共享表格中。
	- 对重点模块提供钻取视图（例如：按模块、按责任人、按文档类型）。
- **改进闭环**：
	1. 按月召开质量例会，讨论指标异常。
	2. 制定改进任务（Issue/PR），明确责任人和截止时间。
	3. 回顾改进效果，记录在 work-history-archive.md。
- **激励机制**：
	- 对连续 2 个季度达到目标的团队给予表彰。
	- 对改进显著的文档案例编写“最佳实践”并纳入培训素材。

---

## 附录

### A. 快速索引表（Quick Index）

| 编号 | 文档类型 | 目录位置 | 负责人 | 模板 |
|------|----------|----------|--------|------|
| A1 | 根目录 README | `/README.md` | 标准所有者 | （参考现有 README 结构） |
| A2 | 目录 README | `docs/**/README.md` | 目录所有者 | docs/templates/module-readme-template.md |
| A3 | 模块 README | `docs/design/modules/<module>/README.md` | 模块负责人 | docs/templates/module-readme-template.md |
| A4 | 组件 README | `docs/design/modules/<module>/components/<component>/README.md` | 组件负责人 | docs/templates/module-readme-template.md |
| A5 | 工具 README | `tools/**/README.md` | 工具维护者 | （参考 tools/README.md） |
| A6 | overview | `docs/design/modules/<module>/overview.md` | 模块负责人 | docs/templates/module-template.md |
| A7 | requirements | `docs/design/modules/<module>/requirements.md` | 产品负责人 | docs/templates/module-requirements-template.md |
| A8 | design | `docs/design/modules/<module>/design/design.md` | Tech Lead | docs/templates/module-design-template.md |
| A9 | implementation | `docs/design/modules/<module>/design/implementation.md` | 模块负责人 | docs/templates/module-implementation-template.md |
| A10 | api-spec | `docs/design/modules/<module>/api/api-spec.md` | 模块负责人 | docs/templates/module-design-template.md |
| A11 | api-implementation | `docs/design/modules/<module>/api/api-implementation.md` | 模块负责人 | docs/templates/module-implementation-template.md |
| A12 | database-design | `docs/design/modules/<module>/design/database-design.md` | 数据库管理员 | docs/templates/module-design-template.md |
| A13 | technology-stack | `docs/standards/technology-stack-standards.md` | Tech Lead | docs/templates/README.md |
| A14 | testing-standards | `docs/standards/testing-standards.md` | QA Lead | docs/templates/README.md |
| A15 | performance-standards | `docs/standards/performance-standards.md` | 性能负责人 | docs/templates/README.md |
| A16 | deployment-standards | `docs/standards/deployment-standards.md` | Ops Lead | docs/templates/README.md |
| A17 | issues-tracking | `docs/status/issues-tracking.md` | QA Lead | docs/templates/issues-tracking.md |
| A18 | module-status | `docs/status/module-status.md` | 模块负责人 | docs/templates/module-status.md |
| A19 | work-history-archive | `docs/_archive/work-history-archive.md` | 标准所有者 | docs/templates/work-history-archive.md |
| B1 | ADR | `docs/adr/ADR-xxxx-title.md` | 架构委员会 | docs/templates/adr.md |
| B2 | 分析报告 | `docs/analysis/**` | 分析负责人 | docs/templates/analysis-report.md |
| B3 | 模板文档 | `docs/templates/**` | 标准所有者 | — |
| B4 | 工具文档 | `docs/tools/**` | 工具负责人 | docs/templates/tool-doc.md |
| B5 | 检查点日志 | `docs/status/checkpoints/**` | QA Lead | docs/templates/checkpoint.md |
| B6 | 规划文档 | `docs/planning/**` | 产品负责人 | docs/templates/planning.md |
| B7 | 存档文档 | `docs/_archive/**` | 标准所有者 | docs/templates/archive.md |
| B8 | 运维文档 | `docs/operations/**` | Ops Lead | docs/templates/operations.md |
| C1 | 迁移文档 | `docs/migrations/**` | Ops Lead | docs/templates/migration.md |
| C2 | 应急文档 | `docs/operations/emergency/**` | Ops Lead | docs/templates/emergency.md |
| C3 | 临时文档 | `docs/temp/**` | 任务负责人 | docs/templates/temp.md |

### B. 术语表（Glossary）

- **ADR**：Architecture Decision Record，架构决策记录。
- **Front Matter**：文档头部的元数据块，通常使用 YAML 表示。
- **SLA/SLO/SLI**：服务等级协议/目标/指标。
- **CI/CD**：持续集成/持续交付。
- **STRIDE**：威胁建模方法（Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege）。
- **金丝雀发布**：逐步放量的部署策略，先对小部分用户开放。

### C. 参考文档（References）

- 《项目基础定义》（PROJECT-FOUNDATION.md）
- 《命名规范标准》（naming-conventions-standards.md）
- 《开发命名规范》（code-standards.md）
- 《测试管理标准》（testing-standards.md）
- 《自动化工具使用指南》（tools/README.md）
- 《文档模板目录》（docs/templates/README.md）

---

> **执行宣告**：自 v3.0.0 起，本标准是 docs/ 目录所有文档创建、维护、审核、归档的唯一权威依据。所有团队成员必须在各自职责范围内遵守本标准，任何偏差必须通过 ADR 记录并经标准所有者批准。
