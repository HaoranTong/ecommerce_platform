# 电商平台后端服务

> 基于FastAPI构建的模块化农产品电商平台，采用文档驱动开发和标准化架构

## 🚀 快速开始

**新手开发者**: [📖 开发环境配置指南](docs/operations/development-setup.md) - 快速搭建开发环境

**核心命令**:
```powershell
# 1. 克隆并设置环境
git clone https://github.com/HaoranTong/ecommerce_platform.git
cd ecommerce_platform && python -m venv .venv && .venv\Scripts\Activate.ps1

# 2. 安装依赖并检查环境
pip install -r requirements.txt
.\tools\check_test_env.ps1 -TestMode lite

# 3. 运行测试验证
pytest tests/unit/ -v
```

**进阶开发**: [📖 AI开发控制文档](MASTER.md) - 深度掌握项目架构和开发流程

## 🎯 核心特性
- 🏗️ **模块化单体架构** - 垂直切片模块化设计，清晰边界
- 🌾 **农产品电商** - 专注农产品溯源、质量认证、冷链物流
- ### 📋 开发标准文档体系 (三层架构)
🎯 **入口**: [📖 标准文档导航](docs/standards/README.md) - 统一标准体系入口

| 层级 | 文档名称 | 职责范围 | 使用场景 |
|------|----------|----------|----------|
| **FOUNDATION** | [项目基础设定](PROJECT-FOUNDATION.md) | 项目架构权威定义 | 🏗️ 架构决策/项目设置 |
| **L1核心** | [命名规范总纲](docs/standards/naming-conventions-standards.md) | 全局命名规则权威定义 | 🔤 命名决策 |
| **L2领域** | [数据库设计标准](docs/standards/database-standards.md) | 数据库设计和ORM规范 | 🗄️ 数据建模 |
| **L2领域** | [API设计标准](docs/standards/api-standards.md) | RESTful API设计规范 | 🌐 接口设计 |
| **L2领域** | [代码标准规范](docs/standards/code-standards.md) | 代码质量和开发实践 | 💻 编码规范 |
| **L2领域** | [脚本管理标准](docs/standards/scripts-standards.md) | DevOps脚本管理规范 | 🛠️ 自动化脚本 |
| **L2领域** | [部署标准规范](docs/standards/deployment-standards.md) | 容器化和运维标准 | 🚀 部署运维 |- 按业务领域组织代码，模块边界清晰
- � **JWT认证体系** - 完整的用户认证与权限管理
- �🛒 **高性能购物车** - 基于Redis的分布式购物车系统
- 📦 **商品管理系统** - 商品信息、分类管理、库存控制
- � **多渠道支付** - 支持多种支付方式和退款处理
- 🔄 **标准化工具链** - 自动化开发、测试、部署流程

## 📁 项目结构

```
ecommerce_platform/
├── 📂 app/                     # 应用程序源码
│   ├── __init__.py            # 应用包初始化
│   ├── main.py                # FastAPI应用入口
│   ├── README.md              # 应用架构说明
│   ├── adapters/              # 外部适配器层
│   ├── core/                  # 核心业务层
│   ├── modules/               # 业务功能模块 (19个)
│   │   ├── user_auth/         # 用户认证模块
│   │   ├── product_catalog/   # 商品管理模块  
│   │   ├── shopping_cart/     # 购物车模块
│   │   ├── order_management/  # 订单管理模块
│   │   ├── payment_service/   # 支付服务模块
│   │   ├── inventory_management/ # 库存管理模块
│   │   ├── member_system/     # 会员系统模块
│   │   ├── logistics_management/ # 物流管理模块
│   │   ├── notification_service/ # 通知服务模块
│   │   ├── quality_control/   # 质量控制模块
│   │   ├── recommendation_system/ # 推荐系统模块
│   │   ├── risk_control_system/ # 风控系统模块
│   │   ├── social_features/   # 社交功能模块
│   │   ├── supplier_management/ # 供应商管理模块
│   │   ├── marketing_campaigns/ # 营销活动模块
│   │   ├── customer_service_system/ # 客服系统模块
│   │   ├── data_analytics_platform/ # 数据分析平台模块
│   │   ├── distributor_management/ # 经销商管理模块
│   │   └── batch_traceability/ # 批次溯源模块
│   └── shared/                # 共享组件
│       ├── __init__.py        # 共享包初始化
│       ├── api_schemas.py     # API通用模式
│       └── base_models.py     # 基础数据模型
├── 📚 docs/                    # 项目技术文档
│   ├── README.md              # 文档导航中心
│   ├── requirements/          # 需求分析文档
│   ├── architecture/          # 系统架构设计
│   ├── design/                # 详细设计文档
│   │   ├── system/            # 系统级设计
│   │   ├── modules/           # 业务模块设计
│   │   └── components/        # 技术组件设计
│   ├── standards/             # 🆕 开发标准文档体系 [📖 导航入口](docs/standards/README.md)
│   ├── operations/            # 运维部署文档
│   ├── planning/              # 项目计划文档
│   ├── status/                # 项目状态管理
│   ├── tools/                 # 工具使用文档
│   ├── templates/             # 文档标准模板
│   ├── analysis/              # 分析报告文档
│   ├── adr/                   # 架构决策记录
│   └── _archive/              # 文档存档
├── 🧪 tests/                   # 测试代码
│   ├── conftest.py            # 测试全局配置
│   ├── conftest_e2e.py        # E2E测试配置
│   ├── README.md              # 测试说明文档
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   ├── e2e/                   # 端到端测试
│   ├── performance/           # 性能测试
│   ├── security/              # 安全测试
│   ├── smoke/                 # 冒烟测试
│   ├── factories/             # 测试数据工厂
│   └── generated/             # 自动生成测试
├── 🛠️ tools/                   # 自动化工具
│   └── README.md              # 脚本使用说明
├── 📝 alembic/                 # 数据库迁移
├── 📊 logs/                    # 日志文件
├── 🔧 开发环境配置/             # 开发工具和配置
│   ├── .github/               # GitHub工作流配置
│   ├── .pytest_cache/         # pytest缓存目录
│   ├── .venv/                 # Python虚拟环境
│   └── __pycache__/           # Python字节码缓存
└── 📋 项目配置文件/            # 根目录配置
    ├── README.md              # 项目说明文档
    ├── MASTER.md              # AI开发规范控制文档
    ├── requirements.txt       # 生产环境依赖包
    ├── requirements_dev.txt   # 开发环境依赖包
    ├── pyproject.toml         # Python项目配置
    ├── alembic.ini            # 数据库迁移配置
    ├── docker-compose.yml     # 容器编排配置
    ├── start.ps1              # 项目启动脚本
    ├── dev_env.ps1            # 开发环境配置脚本
    ├── dev_tools.ps1          # 开发工具启动脚本
    ├── .env.example           # 环境变量配置模板
    ├── .envrc                 # 环境自动加载配置
    └── .gitignore             # Git忽略文件配置
```

## 🧭 快速导航

### 📋 开发标准文档体系 (三层架构)
🎯 **入口**: [📖 标准文档导航](docs/standards/README.md) - 统一标准体系入口

| 层级 | 文档名称 | 职责范围 | 使用场景 |
|------|----------|----------|----------|
| **FOUNDATION** | [项目基础设定](PROJECT-FOUNDATION.md) | 项目架构权威定义 | 🏗️ 架构决策/项目设置 |
| **L1核心** | [命名规范总纲](docs/standards/naming-conventions-standards.md) | 全局命名规则权威定义 | 🔤 命名决策 |
| **L2领域** | [数据库设计标准](docs/standards/database-standards.md) | 数据库设计和ORM规范 | 🗄️ 数据建模 |
| **L2领域** | [API设计标准](docs/standards/api-standards.md) | RESTful API设计规范 | 🌐 接口设计 |
| **L2领域** | [代码标准规范](docs/standards/code-standards.md) | 代码质量和开发实践 | 💻 编码规范 |
| **L2领域** | [脚本管理标准](docs/standards/scripts-standards.md) | DevOps脚本管理规范 | 🛠️ 自动化脚本 |
| **L2领域** | [部署标准规范](docs/standards/deployment-standards.md) | 容器化和运维标准 | 🚀 部署运维 |

### 🔧 开发工具快速通道
- **[脚本工具总览](tools/README.md)** - 13个自动化开发脚本
- **[工具使用指南](docs/tools/README.md)** - 详细的工具文档
- **[标准文档验证](docs/tools/scripts-usage-manual.md#validate_standards.ps1---标准文档验证-)** - 🆕 Phase 3.1质量验证工具

### 📚 技术文档体系
- **[需求分析](docs/requirements/)** - 业务需求和系统需求
- **[系统架构](docs/architecture/)** - 架构设计和ADR决策记录
- **[模块设计](docs/design/modules/)** - 19个业务模块详细设计
- **[运维指南](docs/operations/)** - 部署、监控、故障处理

## 🚀 快速开始

### 开发环境配置
- **[环境搭建指南](docs/development/environment-setup.md)** - 详细的开发环境配置
- **[快速启动脚本](tools/README.md)** - 13个自动化开发脚本

### 部署运维
- **[部署指南](docs/operations/deployment.md)** - 生产环境部署文档
- **[运维手册](docs/operations/README.md)** - 运维监控和故障处理

### API接口规范
- **[API设计标准](docs/standards/api-standards.md)** - RESTful API设计规范
- **[模块API文档](docs/design/modules/)** - 各业务模块接口说明

## 🧭 快速导航

### 📋 开发标准文档体系 (L0-L1-L2架构)
🎯 **入口**: [📖 技术文档导航中心](docs/README.md)

| 层级 | 文档名称 | 职责范围 | 使用场景 |
|------|----------|----------|----------|
| **L0导航** | [docs/README.md](docs/README.md) | 统一入口和AI友好检索 | 📍 **首选入口** |
| **FOUNDATION权威** | [PROJECT-FOUNDATION.md](PROJECT-FOUNDATION.md) | 项目目录结构权威定义 | 🏗️ 新建目录/文件 |
| **L1核心** | [命名规范总纲](docs/standards/naming-conventions-standards.md) | 全局命名规则权威定义 | 🔤 命名决策 |
| **L2领域** | [数据库设计标准](docs/standards/database-standards.md) | 数据库设计和ORM规范 | �️ 数据建模 |
| **L2领域** | [API设计标准](docs/standards/api-standards.md) | RESTful API设计规范 | � 接口设计 |
| **L2领域** | [代码标准规范](docs/standards/code-standards.md) | 代码质量和开发实践 | � 编码规范 |
| **L2领域** | [脚本管理标准](docs/standards/scripts-standards.md) | DevOps脚本管理规范 | 🛠️ 自动化脚本 |
| **L2领域** | [部署标准规范](docs/standards/deployment-standards.md) | 容器化和运维标准 | 🚀 部署运维 |

### 🔧 开发工具快速通道
- **[脚本工具总览](tools/README.md)** - 13个自动化开发脚本
- **[工具使用指南](docs/tools/README.md)** - 详细的工具文档
- **[标准文档验证](docs/tools/scripts-usage-manual.md#validate_standards.ps1---标准文档验证-)** - 🆕 Phase 3.1质量验证工具

### 📚 技术文档体系
- **[需求分析](docs/requirements/)** - 业务需求和系统需求
- **[系统架构](docs/architecture/)** - 架构设计和ADR决策记录
- **[模块设计](docs/design/modules/)** - 19个业务模块详细设计
- **[运维指南](docs/operations/)** - 部署、监控、故障处理

### 📊 项目状态
- **[项目状态](docs/status/)** - 当前版本和开发进度
- **[更新日志](docs/status/changelog.md)** - 版本更新记录
- **[贡献指南](docs/development/contributing.md)** - 开发参与指南

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**💡 提示：** 详细的开发文档和API规范请查看 [`docs/`](docs/) 目录
