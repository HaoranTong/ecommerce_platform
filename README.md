# 定制化电商平台

> 专为五常大米等农产品销售设计的定制化电商平台  
> 基于 FastAPI + SQLAlchemy + MySQL + Redis 构建

## 📖 项目概述

本项目是一个完整的电商平台解决方案，专注于农产品销售，具备现代化的技术架构和完善的开发工具链。

**核心特性:**
- 🛒 完整的购物车系统（基于Redis高性能存储）
- 👤 用户认证与权限管理（JWT Token）
- 📦 商品管理与分类系统
- 📊 订单管理与处理流程
- 🔄 标准化开发工具和自动化脚本

**技术栈:**
- **后端**: FastAPI + ### 📦 功能模块
- **[用户认证模块](docs/modules/user-auth/)** - 用户注册、登录、权限管理
- **[商品目录模块](docs/modules/product-catalog/)** - 商品CRUD、分类、库存
- **[购物车模块](docs/modules/shopping-cart/)** - 购物车功能和Redis存储
- **[订单管理模块](docs/modules/order-management/)** - 订单处理流程
- **[支付系统模块](docs/modules/payment-service/)** - 支付集成和回调hemy + Alembic
- **数### 📝 文档模板和规范
- **[模块文档模板](docs/templates/module-template.md)** - 标准化模块文档模板
- **[文档命名规范](MASTER.md#文档命名规范)** - 统一的文档命名标准（在MASTER.md中定义）

## ⚙️ 开发工具 + Redis
- **容器化**: Docker + Docker Compose
- **测试**: pytest + API测试套件
- **文档**: OpenAPI + Markdown

## 🚀 快速开始

### 开发环境启动（推荐）

```powershell
# 1. 配置开发环境
. .\dev_env.ps1

# 2. 检查数据库状态
.\dev_tools.ps1 check-db

# 3. 启动API服务
.\dev_tools.ps1 start-api

# 4. 运行系统测试
.\dev_tools.ps1 test-cart
```

### 传统启动方式

```powershell
# 后台启动（推荐）
.\start.ps1

# 前台启动（开发调试）
.\start.ps1 -Foreground
```

## 📁 项目结构

### 根目录文件说明

| 文件 | 作用 | 描述 |
|------|------|------|
| `MASTER.md` | 📋 文档驱动开发总纲 | **开发者必读！** 项目的核心指导文档，包含强制检查点和工作流程 |
| `requirements.txt` | Python依赖管理 | 生产环境所需的Python包列表，使用`pip install -r requirements.txt`安装 |
| `docker-compose.yml` | 容器编排配置 | 定义MySQL、Redis等服务的Docker容器配置，一键启动开发环境 |
| `alembic.ini` | 数据库迁移配置 | Alembic数据库版本管理工具的配置文件，管理数据库结构变更 |
| `.env.example` | 环境变量模板 | 配置文件模板，复制为`.env`并填入实际配置值（数据库连接、API密钥等） |
| `.envrc` | direnv配置文件 | 自动加载项目环境变量，需要安装direnv工具（可选，用于自动化开发环境） |
| `start.ps1` | 项目启动脚本 | PowerShell启动脚本，一键启动整个项目（数据库+API服务） |
| `dev_env.ps1` | 开发环境配置 | 开发环境初始化脚本，配置Python虚拟环境和依赖 |
| `dev_tools.ps1` | 开发工具集 | 集成开发工具脚本，包含数据库管理、测试执行等功能 |

### 完整目录结构

```
ecommerce_platform/
├── 📁 app/                          # 🚀 应用核心代码
│   ├── main.py                     # FastAPI应用入口点
│   ├── db.py                       # 数据库连接和会话管理
│   ├── database.py                 # 数据库连接配置
│   ├── redis_client.py             # Redis连接配置
│   ├── auth.py                     # 认证相关功能
│   ├── models.py                   # 数据模型定义
│   └── 📁 api/                     # API路由层
│       ├── routes.py               # 主路由入口
│       ├── schemas.py              # 数据验证模式
│       ├── user_routes.py          # 用户相关API
│       ├── product_routes.py       # 商品相关API
│       ├── category_routes.py      # 分类相关API
│       ├── cart_routes.py          # 购物车相关API
│       ├── order_routes.py         # 订单相关API
│       ├── certificate_routes.py   # 证书相关API
│       └── test_routes.py          # 测试接口
├── 📁 alembic/                      # 🗄️ 数据库迁移管理
│   ├── versions/                   # 数据库版本历史
│   ├── env.py                      # Alembic环境配置
│   └── script.py.mako              # 迁移脚本模板
├── 📁 docs/                         # 📚 项目文档 (详见docs/README.md)
│   ├── README.md                   # 📖 文档中心导航和使用指南
│   ├── 📁 requirements/            # 📋 需求文档
│   │   ├── business.md             # 业务需求规格
│   │   ├── functional.md           # 功能需求说明
│   │   └── non-functional.md       # 非功能需求
│   ├── 📁 architecture/            # 🏗️ 架构设计文档
│   │   ├── overview.md             # 系统架构总览
│   │   ├── data-models.md          # 数据模型设计
│   │   ├── security.md             # 安全架构设计
│   │   ├── integration.md          # 第三方集成方案
│   │   └── event-driven.md         # 事件驱动架构
│   ├── 📁 api/                     # 📡 API文档中心
│   │   ├── README.md               # API文档导航
│   │   ├── standards.md            # API设计标准规范
│   │   ├── openapi.yaml            # OpenAPI 3.0规范文档
│   │   └── 📁 modules/             # 各模块API文档
│   │       └── 📁 cart/            # 购物车API
│   │           └── api-spec.md     # 购物车API规范
│   ├── 📁 modules/                 # 📦 模块设计文档
│   │   ├── README.md               # 模块总览索引
│   │   ├── 📁 user-auth/           # 用户认证模块
│   │   ├── 📁 shopping-cart/       # 购物车模块
│   │   ├── 📁 order-management/    # 订单管理模块
│   │   ├── 📁 product-catalog/     # 商品管理模块
│   │   ├── 📁 inventory/           # 库存管理模块
│   │   ├── 📁 payment/             # 支付服务模块
│   │   ├── 📁 notification/        # 通知服务模块
│   │   ├── 📁 batch-traceability/  # 批次溯源模块
│   │   ├── 📁 distributor/         # 分销商管理模块
│   │   └── 📁 recommendation/      # 推荐系统模块
│   ├── 📁 operations/              # 🔧 运维部署文档
│   │   ├── README.md               # 运维指南
│   │   ├── deployment.md           # 部署指南
│   │   └── environment.md          # 环境配置
│   ├── 📁 development/             # 💻 开发相关文档
│   │   ├── README.md               # 开发指南导航
│   │   ├── standards.md            # 开发标准规范
│   │   ├── testing.md              # 测试指南
│   │   ├── tools.md                # 开发工具说明
│   │   └── workflow.md             # 开发工作流程
│   ├── 📁 status/                  # 📊 项目状态文档
│   │   ├── status.md               # 项目状态总览
│   │   ├── current-sprint.md       # 当前冲刺状态
│   │   ├── daily-log.md            # 每日工作日志
│   │   ├── issues-tracking.md      # 问题跟踪记录
│   │   └── milestones.md           # 里程碑进展
│   ├── 📁 templates/               # 📝 文档模板
│   │   └── module-template.md      # 模块文档标准模板
│   └── 📁 _archive/                # 🗂️ 已归档文档
│       ├── event-schemas/          # 事件架构历史版本
│       ├── technical_old/          # 整合的旧技术文档
│       └── technical_legacy/       # 历史技术文档备份
├── 📁 tests/                        # 🧪 测试用例
│   ├── conftest.py                 # pytest配置文件
│   ├── test_users.py               # 用户功能测试
│   ├── test_products.py            # 商品功能测试
│   ├── test_categories.py          # 分类功能测试
│   └── 📁 integration/             # 集成测试
│       └── test_cart_system.ps1    # 购物车系统集成测试脚本
├── 📁 scripts/                      # 🤖 自动化脚本 (详见scripts/README.md)
│   ├── README.md                   # 📖 脚本使用指南和说明
│   ├── feature_finish.ps1          # 功能完成自动化流程
│   ├── release_to_main.ps1         # 发布到主分支脚本
│   ├── smoke_test.ps1              # 冒烟测试脚本
│   ├── log_status.ps1              # 状态记录脚本
│   ├── sync_env.ps1                # 环境同步脚本
│   └── _smoke_cert.py              # SSL证书验证工具
├── 📁 .venv/                        # 🐍 Python虚拟环境
├── 📁 .git/                         # 📝 Git版本控制
├── 📁 .github/                      # 🔄 GitHub Actions配置
├── alembic.ini                     # 数据库迁移配置文件
├── docker-compose.yml              # Docker容器编排配置
├── requirements.txt                # Python依赖包列表
├── .env.example                    # 环境变量配置模板
├── .envrc                          # direnv自动环境配置
├── .gitignore                      # Git忽略文件配置
├── start.ps1                       # 🚀 项目启动脚本
├── dev_env.ps1                     # 开发环境配置脚本
└── dev_tools.ps1                   # 开发工具集脚本
```

### 📁 关键目录说明

| 目录 | 功能说明 | 重要文件 |
|------|----------|----------|
| **app/** | 应用核心代码，包含所有业务逻辑 | `main.py`, `database.py`, `api/routes.py` |
| **docs/** | 完整项目文档，包含架构设计和模块文档 | `README.md`, `requirements/`, `modules/` |
| **tests/** | 测试代码，包含单元测试和集成测试 | `conftest.py`, `integration/` |
| **scripts/** | 自动化开发脚本 | `smoke_test.ps1`, `feature_finish.ps1` |
| **alembic/** | 数据库版本管理和迁移 | `versions/`, `env.py` |

### 🔧 开发脚本说明

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `start.ps1` | 一键启动整个项目 | 日常开发启动 |
| `dev_env.ps1` | 配置开发环境 | 首次环境搭建 |
| `dev_tools.ps1` | 开发工具集 | 数据库管理、测试执行 |
| `scripts/smoke_test.ps1` | 烟雾测试 | 快速验证系统健康 |
| `scripts/feature_finish.ps1` | 功能完成检查 | 功能开发完成验证 |
| `tests/integration/test_cart_system.ps1` | 购物车集成测试 | 购物车功能完整性测试 |

### 服务访问

- **应用首页**: http://127.0.0.1:8000/
- **API 文档**: http://127.0.0.1:8000/docs  
- **ReDoc 文档**: http://127.0.0.1:8000/redoc
- **健康检查**: http://127.0.0.1:8000/api/health

### 停止服务

```powershell
# 停止所有服务
docker-compose down

# 停止FastAPI应用（如果独立运行）
Get-Process python | Where-Object {$_.ProcessName -eq "python"} | Stop-Process
```

## 📁 项目结构

```
ecommerce_platform/
├── app/                        # 🚀 应用核心代码
│   ├── main.py                 # FastAPI应用入口
│   ├── models.py               # SQLAlchemy数据模型
│   ├── database.py             # 数据库配置和连接
│   ├── auth.py                 # 认证和授权
│   ├── redis_client.py         # Redis客户端配置
│   └── api/                    # API路由模块
│       ├── routes.py           # 主路由注册
│       ├── schemas.py          # Pydantic数据模式
│       ├── user_routes.py      # 用户管理API
│       ├── product_routes.py   # 商品管理API
│       ├── category_routes.py  # 分类管理API
│       ├── cart_routes.py      # 购物车API
│       ├── order_routes.py     # 订单管理API
│       └── certificate_routes.py # 证书管理API
│
├── alembic/                    # 🗃️ 数据库迁移
│   ├── versions/               # 迁移脚本版本
│   ├── env.py                  # Alembic环境配置
│   └── script.py.mako          # 迁移脚本模板
│
├── tests/                      # 🧪 测试代码
│   ├── conftest.py             # pytest配置
│   ├── test_users.py           # 用户功能测试
│   ├── test_products.py        # 商品功能测试
│   └── test_categories.py      # 分类功能测试
│
├── scripts/                    # 🔧 自动化脚本
│   ├── smoke_test.ps1          # 烟雾测试脚本
│   ├── feature_finish.ps1      # 功能完成自动化
│   ├── release_to_main.ps1     # 发布到主分支
│   ├── log_status.ps1          # 状态日志记录
│   └── sync_env.ps1            # 环境同步脚本
│
├── docs/                       # 📚 技术文档（详见下方文档导航）
├── .github/                    # ⚙️ GitHub工作流配置
├── .venv/                      # 🐍 Python虚拟环境
├── .env                        # 🔐 环境变量配置
├── requirements.txt            # 📦 Python依赖
├── alembic.ini                 # ⚙️ Alembic配置
├── docker-compose.yml          # 🐳 Docker服务配置
├── start.ps1                   # 🚀 应用启动脚本
├── dev_env.ps1                 # 🛠️ 开发环境配置
├── dev_tools.ps1               # 🔨 开发工具集
└── test_cart_system.ps1        # 🧪 购物车系统测试
```
├── .github/                    # ⚙️ GitHub工作流配置
├── .venv/                      # 🐍 Python虚拟环境
├── .env                        # 🔐 环境变量配置
├── requirements.txt            # 📦 Python依赖
├── alembic.ini                 # ⚙️ Alembic配置
├── docker-compose.yml          # 🐳 Docker服务配置
├── start.ps1                   # 🚀 应用启动脚本
├── dev_env.ps1                 # 🛠️ 开发环境配置
└── dev_tools.ps1               # 🔨 开发工具集
```

## 📚 技术文档导航

### 🎯 开发入口
- **[总纲文档](MASTER.md)** - **必读！** 开发工作流程和强制检查点
- **[命名规范](docs/standards/naming-conventions.md)** - **强制执行！** 项目统一命名标准
- **[脚本使用指南](scripts/README.md)** - **命名检查必备！** 自动化工具使用说明

### 📋 需求与规范
- **[业务需求](docs/requirements/business.md)** - 项目业务需求和目标
- **[功能需求](docs/requirements/functional.md)** - 详细功能规范
- **[非功能需求](docs/requirements/non-functional.md)** - 性能、安全、合规要求

### 🏗️ 技术架构
- **[架构总览](docs/architecture/overview.md)** - 技术选型和架构决策
- **[API设计标准](docs/architecture/api-standards.md)** - API设计规范和约定
- **[数据模型标准](docs/architecture/data-standards.md)** - 数据库设计规范
- **[安全架构](docs/architecture/security.md)** - 安全策略和实施方案
- **[第三方集成](docs/architecture/integration.md)** - 外部服务集成规范

### � 功能模块
- **[用户认证模块](docs/modules/user-auth/)** - 用户注册、登录、权限管理
- **[商品管理模块](docs/modules/product-management/)** - 商品CRUD、分类、库存
- **[购物车模块](docs/modules/shopping-cart/)** - 购物车功能和Redis存储
- **[订单管理模块](docs/modules/order-management/)** - 订单处理流程
- **[支付系统模块](docs/modules/payment-system/)** - 支付集成和回调

### 🔧 运维指南
- **[部署指南](docs/operations/deployment.md)** - 生产环境部署
- **[环境配置](docs/operations/environment.md)** - 环境变量管理
- **[监控配置](docs/operations/monitoring.md)** - 系统监控和告警
- **[故障排除](docs/operations/troubleshooting.md)** - 常见问题解决
- **[运维手册](docs/operations/runbook.md)** - 日常运维操作

### 🛠️ 开发指南
- **[开发工作流程](docs/development/workflow.md)** - 标准开发流程
- **[编码规范](docs/development/standards.md)** - 代码质量标准
- **[测试策略](docs/development/testing.md)** - 测试方法和工具
- **[开发工具](docs/development/tools.md)** - 开发环境配置

### 📊 项目状态
- **[项目状态总览](docs/status/status.md)** - 整体进度和模块完成情况 **（每周更新）**
- **[当前冲刺](docs/status/current-sprint.md)** - 当前Sprint的任务和进展 **（每日更新）**  
- **[工作日志](docs/status/daily-log.md)** - 每日开发工作记录 **（每日更新）**
- **[问题跟踪](docs/status/issues-tracking.md)** - Bug、任务和解决方案跟踪 **（实时更新）**
- **[里程碑](docs/status/milestones.md)** - 版本发布和重要节点记录 **（里程碑达成时更新）**

> **📋 Status目录使用说明**  
> - **目的**: 提供项目实时状态跟踪，便于团队协作和进度管理
> - **更新责任**: 开发团队成员每日更新工作日志，项目经理每周汇总状态
> - **自动化集成**: 结合Git提交记录和CI/CD流程自动更新部分状态信息
> - **查看方式**: 团队会议时查看整体状态，个人开发时查看当前冲刺和问题跟踪

### 📝 文档模板和规范
- **[模块文档模板](docs/templates/module-template.md)** - 标准化模块文档模板
- **[文档命名规范说明](docs/README.md#文档命名规范)** - 为什么有些是README.md，有些是overview.md

> **📋 文档命名规范说明**  
> - **README.md**: 用于目录级别的导航和说明文档（如 `docs/development/README.md`）
> - **overview.md**: 用于具体功能模块的概览文档（如 `docs/modules/user-auth/overview.md`）
> - **standards.md**: 用于规范和标准类文档（如 `docs/api/standards.md`）
> - 这种命名规范确保了文档层次清晰，便于开发者快速定位所需信息

## 🛠️ 开发工具

### 命名规范检查工具

```powershell
# 📋 命名规范检查（强制每日执行）
.\scripts\check_naming_compliance.ps1           # 标准检查
.\scripts\check_naming_compliance.ps1 -Verbose  # 详细报告

# 🔧 配置管理
.\scripts\check_naming_compliance.ps1 -ConfigPath .\scripts\naming_config.json
```

**重要**: 所有开发者每日必须执行命名检查，确保代码符合项目规范。详见 **[脚本使用指南](scripts/README.md)**

### 标准化开发工具集

```powershell
# 环境配置
. .\dev_env.ps1              # 配置开发环境

# 开发工具
.\dev_tools.ps1 check-db     # 检查数据库连接
.\dev_tools.ps1 migrate      # 执行数据库迁移
.\dev_tools.ps1 test-cart    # 运行购物车测试
.\dev_tools.ps1 start-api    # 启动API服务
.\dev_tools.ps1 stop-api     # 停止API服务
.\dev_tools.ps1 reset-env    # 重置开发环境
```

### 自动化脚本

```powershell
# 功能开发完成后的自动化流程
.\scripts\feature_finish.ps1

# 发布到主分支（先预览再执行）
.\scripts\release_to_main.ps1 -DryRun
.\scripts\release_to_main.ps1 -RunNow

# 烟雾测试
.\scripts\smoke_test.ps1

# 状态日志
.\scripts\log_status.ps1
```

## 🐛 故障排除

### 常见问题

**Docker启动失败:**
```powershell
docker info                          # 检查Docker状态
start "Docker Desktop.exe"           # 启动Docker Desktop
```

**端口占用:**
```powershell
netstat -ano | findstr :8000        # 检查端口占用
taskkill /PID <PID> /F               # 强制停止进程
```

**数据库连接失败:**
```powershell
docker-compose exec mysql mysqladmin ping -u root -p
docker-compose down -v && docker-compose up -d    # 重置数据库
```

**迁移失败:**
```powershell
alembic current                      # 检查当前迁移状态
alembic stamp head                   # 强制设置迁移版本
```

### 环境要求

- **操作系统**: Windows 10/11
- **Python**: 3.11+
- **Docker**: Docker Desktop with WSL2
- **PowerShell**: 5.1+ 或 PowerShell Core 7+

## 🌟 开发工作流

### 命名规范强制执行
所有开发活动必须严格遵循项目命名规范，确保跨层一致性：

```powershell
# 📋 强制命名检查（每日必做）
.\scripts\check_naming_compliance.ps1

# 🔍 查看详细报告
.\scripts\check_naming_compliance.ps1 -Verbose

# ⚠️  修复不符合规范的命名
# 根据检查报告修复后重新验证
.\scripts\check_naming_compliance.ps1 -ConfigPath .\scripts\naming_config.json
```

**命名规范优先级**: 文档 → 数据库 → API → 代码
- **模块命名**: 统一使用 `user-auth`, `shopping-cart`, `product-catalog`, `order-management`
- **API端点**: RESTful规范，如 `/api/users`, `/api/products`, `/api/carts`
- **数据库表**: snake_case，如 `users`, `products`, `cart_items`
- **代码文件**: snake_case，如 `user_routes.py`, `cart_routes.py`

详细说明参见：**[命名规范文档](docs/standards/naming-conventions.md)**

### 分支策略
- `main` - 生产就绪代码
- `dev` - 开发集成分支
- `feature/*` - 功能开发分支

### 开发流程
1. **命名检查** - 执行 `.\scripts\check_naming_compliance.ps1` 确保符合规范
2. 从 `dev` 创建 `feature/` 分支
3. 在功能分支进行开发和测试
4. **再次命名检查** - 开发完成后验证命名一致性
5. 使用 `.\scripts\feature_finish.ps1` 自动合并到 `dev`
6. 使用 `.\scripts\release_to_main.ps1` 发布到 `main`

> **⚠️ 重要提醒**: 所有文档、API、数据库、代码的命名必须严格遵循命名规范。不符合规范的代码将无法通过CI/CD检查。

## 📞 支持与贡献

### 技术支持
- 查看 **[故障排除文档](docs/operations/troubleshooting.md)**
- 查看 **[工作日志](docs/status/daily-log.md)** 了解最新状态
- 参考 **[开发工作流程](docs/development/workflow.md)**

### 贡献指南
- **强制执行命名规范** - 提交前必须通过 `.\scripts\check_naming_compliance.ps1` 检查
- 遵循 **[编码规范](docs/development/standards.md)**
- 确保所有测试通过
- 更新相关文档
- 使用标准化脚本进行提交

**命名规范检查清单**：
```powershell
# 提交前必须执行的检查
.\scripts\check_naming_compliance.ps1 -Verbose
# 返回码必须为 0（无违规）才能提交
```

---

**开始开发前，请务必阅读 [总纲文档](MASTER.md)！**
