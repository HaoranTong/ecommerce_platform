<!--version info: v1.0.0, created: 2025-09-23, level: L1, dependencies: none-->

# 项目结构组织标准  
维护人：系统架构师
权威级别：L1核心标准
依赖关系：无上级依赖 (最高权威)
被依赖：所有L2领域标准
关联决策：ADR-002 标准文档架构重构
变更说明：建立项目结构最高权威标准，定义完整目录组织规范
-->

## 🎯 根目录结构标准 (最高权威)

### 强制目录结构 (不可变更)
```tree
ecommerce_platform/
├── 📂 app/                    # 应用程序源码 → 详见 L2: code-standards.md
├── 📂 docs/                   # 技术文档体系 → 详见 L2: document-standards.md  
├── 📂 tests/                  # 测试代码体系 → 详见 L2: testing-standards.md
├── 📂 scripts/                # DevOps自动化脚本 → 详见 L2: scripts-standards.md
├── 📂 logs/                   # 运行时日志文件 → 详见 L2: logging-standards.md
├── 📂 alembic/                # 数据库版本迁移 → 详见 L2: database-standards.md
├── 📄 requirements.txt        # Python生产环境依赖
├── 📄 requirements_dev.txt    # Python开发环境依赖
├── 📄 pyproject.toml         # 项目配置和构建设置  
├── 📄 docker-compose.yml     # 容器编排配置
├── 📄 alembic.ini            # 数据库迁移工具配置
├── 📄 MASTER.md              # AI开发控制文档 (最高优先级)
└── 📄 README.md              # 项目入口和概览文档
```

### 🏗️ 目录职责权威定义

| 目录路径 | 核心职责 | 允许内容 | 🚫 禁止内容 | 详细标准引用 |
|---------|---------|---------|-------------|-------------|
| `app/` | 应用程序源代码 | Python模块、配置、业务逻辑 | 测试代码、文档、日志、临时文件 | [code-standards.md](code-standards.md) |
| `docs/` | 技术文档和规范 | Markdown文档、架构图、设计文档 | 源代码、可执行文件、日志、临时文件 | [document-standards.md](document-standards.md) |
| `tests/` | 测试代码和测试数据 | 测试脚本、Mock数据、测试配置 | 生产代码、业务逻辑、用户文档 | [testing-standards.md](testing-standards.md) |
| `scripts/` | 自动化脚本和工具 | 部署脚本、构建工具、检查脚本 | 业务逻辑、测试代码、用户文档 | [scripts-standards.md](scripts-standards.md) |
| `logs/` | 应用运行时日志 | 日志文件、错误报告、监控数据 | 源代码、配置文件、用户数据 | [logging-standards.md](logging-standards.md) |
| `alembic/` | 数据库迁移脚本 | 迁移脚本、版本文件、环境配置 | 业务逻辑、测试数据、用户文档 | [database-standards.md](database-standards.md) |

### 🔒 根目录文件权威定义

| 文件名 | 用途说明 | 内容要求 | 🚫 禁止操作 |
|--------|---------|---------|------------|
| `MASTER.md` | AI开发控制和流程管理 | 开发规范、检查点、强制规则 | 删除、重命名、未授权修改 |
| `README.md` | 项目入口和概览介绍 | 项目介绍、快速开始、架构概述 | 包含详细技术实施细节 |
| `requirements.txt` | 生产环境Python依赖 | 固定版本依赖列表 | 包含开发工具依赖 |
| `requirements_dev.txt` | 开发环境额外依赖 | 测试、构建、调试工具依赖 | 包含生产环境依赖 |
| `pyproject.toml` | 项目配置和元数据 | 构建配置、工具配置、项目元信息 | 包含敏感信息 |
| `docker-compose.yml` | 容器化部署配置 | 服务定义、网络配置、卷挂载 | 包含生产环境密钥 |
| `alembic.ini` | 数据库迁移配置 | 迁移路径、日志配置、连接模板 | 包含真实数据库连接信息 |

## 🏗️ 关键子目录组织标准

### app/ 目录一级结构 (强制标准)
```tree
app/
├── main.py                    # FastAPI应用入口点 (唯一入口)
├── 📂 core/                   # 核心基础设施组件
│   ├── database.py            # 数据库连接和会话管理
│   ├── redis_client.py        # Redis缓存客户端
│   ├── auth.py               # 认证中间件和JWT处理
│   ├── security.py           # 安全相关工具和验证
│   └── __init__.py           # 核心组件导出
├── 📂 modules/               # 业务功能模块 (垂直切片架构)
│   ├── user_auth/            # 用户认证模块
│   ├── product_catalog/      # 商品管理模块
│   ├── shopping_cart/        # 购物车模块
│   ├── order_management/     # 订单管理模块
│   ├── payment_service/      # 支付服务模块
│   ├── inventory_management/ # 库存管理模块
│   ├── member_system/        # 会员系统模块
│   ├── logistics_management/ # 物流管理模块
│   ├── notification_service/ # 通知服务模块
│   ├── quality_control/      # 质量控制模块
│   ├── recommendation_system/ # 推荐系统模块
│   ├── risk_control_system/  # 风控系统模块
│   ├── social_features/      # 社交功能模块
│   ├── supplier_management/  # 供应商管理模块
│   ├── marketing_campaigns/  # 营销活动模块
│   ├── customer_service_system/ # 客服系统模块
│   ├── data_analytics_platform/ # 数据分析平台模块
│   ├── distributor_management/  # 经销商管理模块
│   └── batch_traceability/   # 批次溯源模块
├── 📂 shared/                # 跨模块共享组件 (最小化原则)
│   ├── base_models.py        # ORM基础类和通用字段
│   ├── api_schemas.py        # 通用API响应模式
│   ├── exceptions.py         # 全局异常类定义
│   ├── constants.py          # 全局常量定义
│   └── __init__.py          # 共享组件导出
└── 📂 adapters/              # 外部系统适配器
    ├── payment/              # 支付服务适配器
    │   ├── wechat_adapter.py # 微信支付适配器
    │   ├── alipay_adapter.py # 支付宝适配器
    │   └── __init__.py       # 支付适配器导出
    ├── blockchain/           # 区块链服务适配器 (待开发)
    ├── ai/                   # AI服务适配器 (待开发)  
    └── __init__.py          # 适配器包导出
```

### docs/ 目录一级结构 (四层文档体系)
```tree
docs/
├── 📂 requirements/          # L1: 业务需求层 (纯需求，不涉及实现)
├── 📂 architecture/          # L2: 系统架构层 (整体设计原则和策略)
├── 📂 design/               # L3: 详细设计层 (具体实现方案)
│   ├── system/              # 系统级设计 (技术选型、算法、集成)
│   ├── modules/             # 业务模块设计 (保持模块边界独立)
│   └── components/          # 技术组件设计 (保持组件边界独立)
├── 📂 standards/            # L4: 开发标准层 (规范和执行标准)
├── 📂 operations/           # 运维部署层 (部署、监控、维护)
├── 📂 planning/             # 项目管理层 (计划、进度、资源)
├── 📂 adr/                  # 架构决策记录 (重要决策追踪)
├── 📂 tools/                # 工具使用指南 (开发工具文档)
├── 📂 status/               # 项目状态管理 (当前状态、问题追踪)
├── 📂 templates/            # 文档标准模板 (标准化模板)
├── 📂 analysis/             # 分析报告归档 (分析结果存储)
├── 📂 _archive/             # 废弃文档备份 (历史文档保存)
└── 📄 README.md             # 文档导航中心
```

### tests/ 目录一级结构 (五层测试架构)
```tree
tests/
├── 📂 unit/                 # 单元测试 (70% 覆盖率目标)
│   ├── test_models/         # 数据模型测试 (Mock测试)
│   ├── test_services/       # 业务逻辑测试 (SQLite内存数据库)
│   └── *_standalone.py     # 业务流程测试 (SQLite内存数据库)
├── 📂 integration/          # 集成测试 (20% 覆盖率目标)
│   └── test_*.py           # 模块间集成测试 (MySQL Docker)
├── 📂 e2e/                  # 端到端测试 (6% 覆盖率目标)
│   └── test_*.py           # 完整业务流程测试 (MySQL Docker)
├── 📂 smoke/                # 烟雾测试 (2% 覆盖率目标)
│   └── test_*.py           # 基础功能验证 (SQLite文件数据库)
├── 📂 performance/          # 性能测试 (2% 覆盖率目标)
│   └── test_*.py           # 性能和压力测试
├── 📂 security/             # 安全测试 (专项测试)
│   └── test_*.py           # 安全漏洞和权限测试
├── 📂 factories/            # 测试数据工厂 (数据生成)
│   └── *.py                # 测试数据构建器
├── 📂 generated/            # 自动生成测试 (工具生成)
│   └── test_*.py           # 自动化生成的测试用例
├── 📄 conftest.py          # pytest主配置文件
├── 📄 conftest_e2e.py      # E2E测试专用配置
└── 📄 README.md            # 测试体系说明文档
```

### scripts/ 目录一级结构 (功能分组管理)
```tree
scripts/
├── 📂 dev/                  # 开发环境脚本
│   ├── dev_env.ps1          # 开发环境配置脚本
│   ├── dev_checkpoint.ps1   # 开发阶段检查点验证
│   └── dev_tools.ps1        # 开发辅助工具脚本
├── 📂 test/                 # 测试相关脚本  
│   ├── run_module_tests.ps1     # 模块测试执行脚本
│   ├── setup_test_env.ps1       # 测试环境配置脚本
│   ├── integration_test.ps1     # 集成测试执行脚本
│   ├── smoke_test.ps1          # 烟雾测试执行脚本
│   └── e2e_test_verification.py # E2E测试验证脚本
├── 📂 deploy/               # 部署发布脚本
│   ├── release_to_main.ps1  # 发布到主分支脚本
│   ├── sync_env.ps1         # 环境同步脚本
│   └── feature_finish.ps1   # 特性完成流程脚本
├── 📂 check/                # 质量检查脚本
│   ├── check_code_standards.ps1    # 代码规范检查
│   ├── check_database_schema.ps1   # 数据库模式检查  
│   ├── check_docs.ps1              # 文档完整性检查
│   ├── check_naming_compliance.ps1 # 命名规范检查
│   └── check_test_env.ps1          # 测试环境检查
├── 📂 utils/                # 通用工具脚本
│   ├── model_analyzer.py           # 模型分析工具
│   ├── api_service_mapping_analyzer.py # API服务映射分析
│   ├── generate_test_template.py   # 测试模板生成工具
│   ├── validate_pydantic_v2.py    # Pydantic V2验证工具
│   ├── validate_test_config.py    # 测试配置验证工具
│   ├── validate_test_structure.py # 测试结构验证工具
│   └── verify_inventory_module.py # 库存模块验证工具
└── 📄 README.md             # 脚本使用指南文档
```

## 🚫 严格禁止行为清单

### 根目录层面禁止事项
- ❌ 在根目录创建未定义的目录或文件
- ❌ 修改根目录强制文件的文件名
- ❌ 在根目录放置临时文件、日志文件、缓存文件
- ❌ 创建语言特定的配置目录 (如: .vscode/, .idea/, 使用 .gitignore 忽略)
- ❌ 放置个人配置文件或开发环境特定文件

### 跨目录污染禁止事项
- ❌ 在 `app/` 目录中放置测试相关文件  
- ❌ 在 `tests/` 目录中放置生产业务代码
- ❌ 在 `docs/` 目录中放置可执行文件或源码
- ❌ 在 `scripts/` 目录中放置业务逻辑代码
- ❌ 在 `logs/` 目录中放置配置文件或源码
- ❌ 在 `alembic/` 目录中放置非迁移相关文件

### 模块边界污染禁止事项  
- ❌ 业务模块间直接相互导入 (必须通过共享层)
- ❌ 跨模块共享API schemas (每个模块独立定义)
- ❌ 在 `shared/` 中放置业务逻辑代码
- ❌ 适配器直接访问业务模块内部实现

## 🎯 业务模块标准结构 (垂直切片)

### 模块内部标准结构 (强制要求)
```tree
modules/{module_name}/
├── __init__.py              # 模块导出接口
├── router.py               # API路由定义 (FastAPI路由)
├── service.py              # 业务逻辑层 (核心业务实现)
├── models.py               # 数据模型层 (SQLAlchemy模型)
├── schemas.py              # API模式层 (Pydantic模型)
├── dependencies.py         # 依赖注入 (模块特定依赖)
├── exceptions.py           # 模块异常 (可选，复杂模块使用)
└── README.md              # 模块说明文档
```

### 模块命名映射标准 (权威定义)

| 🏷️ 业务概念名 | 🔧 技术实现名 | 📁 目录路径 | 🌐 API路径前缀 | 🗄️ 数据库表前缀 |
|---------------|---------------|------------|---------------|----------------|
| user-auth | user_auth | app/modules/user_auth/ | /auth/* | user_, auth_ |
| shopping-cart | shopping_cart | app/modules/shopping_cart/ | /cart/* | cart_, shopping_ |  
| product-catalog | product_catalog | app/modules/product_catalog/ | /products/* | product_, catalog_ |
| order-management | order_management | app/modules/order_management/ | /orders/* | order_, payment_ |
| payment-service | payment_service | app/modules/payment_service/ | /payments/* | payment_, transaction_ |
| inventory-management | inventory_management | app/modules/inventory_management/ | /inventory/* | inventory_, stock_ |
| member-system | member_system | app/modules/member_system/ | /members/* | member_, membership_ |
| logistics-management | logistics_management | app/modules/logistics_management/ | /logistics/* | logistics_, shipping_ |
| notification-service | notification_service | app/modules/notification_service/ | /notifications/* | notification_, message_ |
| quality-control | quality_control | app/modules/quality_control/ | /quality/* | quality_, inspection_ |
| recommendation-system | recommendation_system | app/modules/recommendation_system/ | /recommendations/* | recommendation_, suggest_ |
| risk-control-system | risk_control_system | app/modules/risk_control_system/ | /risk/* | risk_, control_ |
| social-features | social_features | app/modules/social_features/ | /social/* | social_, community_ |
| supplier-management | supplier_management | app/modules/supplier_management/ | /suppliers/* | supplier_, vendor_ |
| marketing-campaigns | marketing_campaigns | app/modules/marketing_campaigns/ | /campaigns/* | campaign_, promotion_ |
| customer-service-system | customer_service_system | app/modules/customer_service_system/ | /support/* | support_, ticket_ |
| data-analytics-platform | data_analytics_platform | app/modules/data_analytics_platform/ | /analytics/* | analytics_, metric_ |
| distributor-management | distributor_management | app/modules/distributor_management/ | /distributors/* | distributor_, channel_ |
| batch-traceability | batch_traceability | app/modules/batch_traceability/ | /traceability/* | batch_, trace_ |

## ✅ 结构验证检查清单

### 🔍 根目录结构验证
- [ ] 根目录只包含标准定义的目录和文件
- [ ] 所有强制目录都已创建且包含README.md
- [ ] 没有创建标准外的自定义目录  
- [ ] 配置文件使用标准命名和格式
- [ ] 无临时文件、缓存文件、个人配置文件

### 🔍 目录职责验证  
- [ ] `app/` 只包含应用程序源码，无测试和文档
- [ ] `docs/` 只包含文档，无源码和可执行文件
- [ ] `tests/` 只包含测试代码，无生产业务逻辑
- [ ] `scripts/` 只包含自动化脚本，无业务逻辑
- [ ] `logs/` 只包含日志文件，无源码和配置  
- [ ] `alembic/` 只包含迁移脚本，无业务代码

### 🔍 模块结构验证
- [ ] 所有业务模块遵循垂直切片标准结构
- [ ] 模块命名符合映射表定义
- [ ] 模块间无直接相互导入
- [ ] API schemas 在各模块内独立定义
- [ ] 共享组件最小化，无业务逻辑

### 🔍 文件命名验证  
- [ ] 目录使用小写字母+下划线格式
- [ ] 文件名符合对应标准要求  
- [ ] 模块名称与业务概念保持一致
- [ ] 无中文或特殊字符命名
- [ ] 遵循Python包命名约定

---

## 📋 引用和维护说明

### 📖 本标准的权威性
- **权威级别**: L1核心标准 (最高级别)
- **依赖关系**: 无上级依赖，为其他所有标准提供基础
- **变更控制**: 任何变更必须通过架构评审和影响评估
- **版本管理**: 采用语义版本控制，重大变更需要ADR记录

### 🔄 被依赖标准列表
- [naming-conventions.md](naming-conventions.md) - 依赖本标准的目录结构定义
- [code-standards.md](code-standards.md) - 依赖本标准的app/目录结构  
- [testing-standards.md](testing-standards.md) - 依赖本标准的tests/目录结构
- [scripts-standards.md](scripts-standards.md) - 依赖本标准的scripts/目录结构
- [document-standards.md](document-standards.md) - 依赖本标准的docs/目录结构
- [database-standards.md](database-standards.md) - 依赖本标准的alembic/目录结构

### ⚡ 自动化验证  
- **验证脚本**: `scripts/check/validate_project_structure.ps1`
- **同步工具**: `scripts/sync_readme.ps1` (结构变更时强制执行)
- **质量检查**: `scripts/check_code_standards.ps1` (提交前强制执行)

---

**📋 检查点标记**: [CHECK:ARCH-002] 模块架构设计验证  
**🔗 关联决策**: [ADR-002](../adr/ADR-002-standards-architecture-refactoring.md)  
**📅 最后更新**: 2025-09-23  
**👤 维护责任人**: 系统架构师  
**🔄 下次审查**: 2025-10-23