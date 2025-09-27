<!--version info: v1.0.0### 强制目录结构 (不可变更)
```tree```tree
ecommerce_platform/
├── 📂 app/                    # 应用程序源码
├── 📚 docs/                   # 技术文档体系  
├── 🧪 tests/                  # 测试代码体系
├── 📂 tools/                  # DevOps自动化工具
├── 📂 logs/                   # 运行时日志文件
├── 📂 alembic/                # 数据库版本迁移
├── 📂 reports/                # 测试和分析报告输出
├── 📂 .github/                # GitHub工作流和配置
├── 📂 .venv/                  # Python虚拟环境 (开发时)
├── 📂 .pytest_cache/         # pytest缓存目录 (开发时)
├── 📋 PROJECT-FOUNDATION.md   # 本文档 (项目基础设定)
├── 📄 MASTER.md              # AI开发控制文档
├── 📄 README.md              # 项目入口和概览文档
├── 📄 requirements.txt        # Python生产环境依赖
├── 📄 requirements_dev.txt    # Python开发环境依赖
├── 📄 pyproject.toml         # 项目配置和构建设置  
├── 📄 docker-compose.yml     # 容器编排配置
├── 📄 alembic.ini            # 数据库迁移工具配置
├── 🚀 start.ps1              # 项目启动脚本
├── 🔧 .env                   # 环境变量配置 (本地)
├── 📝 .env.example           # 环境变量配置模板
├── 📝 .envrc                 # direnv自动环境加载
└── 📄 .gitignore             # Git版本控制忽略规则
```m/
├── 📂 app/                    # 应用程序源码
├── 📚 docs/                   # 技术文档体系  
├── 🧪 tests/                  # 测试代码体系
├── 📂 tools/                  # DevOps自动化工具
├── 📂 logs/                   # 运行时日志文件
├── 📂 alembic/                # 数据库版本迁移
├── 📂 reports/                # 测试和分析报告输出
├── 📂 .github/                # GitHub工作流和配置
├── 📂 .venv/                  # Python虚拟环境 (开发时)
├── 📂 .pytest_cache/         # pytest缓存目录 (开发时)
├── 📋 PROJECT-FOUNDATION.md   # 本文档 (项目基础设定)
├── 📄 MASTER.md              # AI开发控制文档
├── 📄 README.md              # 项目入口和概览文档
├── 📄 requirements.txt        # Python生产环境依赖
├── 📄 requirements_dev.txt    # Python开发环境依赖
├── 📄 pyproject.toml         # 项目配置和构建设置  
├── 📄 docker-compose.yml     # 容器编排配置
├── 📄 alembic.ini            # 数据库迁移工具配置
├── 🚀 start.ps1              # 项目启动脚本
├── 🔧 .env                   # 环境变量配置 (本地)
├── 📝 .env.example           # 环境变量配置模板
├── 📝 .envrc                 # direnv自动环境加载
└── 📄 .gitignore             # Git版本控制忽略规则
```24, level: FOUNDATION, dependencies: ADR-003-->

# 项目基础设定 (PROJECT FOUNDATION)

> **文档性质**: 项目宪法级基础设定  
> **权威级别**: 最高权威 (FOUNDATION级)  
> **变更控制**: 仅经ADR决策流程  
> **关联决策**: [ADR-003 文档架构重构决策](docs/adr/ADR-003-document-architecture-restructure.md)  
> **维护责任**: 系统架构师  
> **更新频率**: 仅在重大架构调整时变更  

## 🎯 项目基本信息

### 文档定位
本文档定义项目的基础架构设定，包括根目录结构、权威关系、核心约束等不可轻易调整的核心要素。所有其他文档和标准都必须遵循本文档的定义。

### 权威性声明
- **最高优先级**: 本文档具有项目最高权威性，覆盖其他所有标准文档
- **基础宪法**: 定义项目的基本架构和不可变规则
- **变更控制**: 任何修改必须通过ADR决策记录流程
- **全局影响**: 本文档的变更将影响整个项目的架构和开发流程

## 🏗️ 根目录结构定义

### 强制目录结构 (不可变更)
```tree
ecommerce_platform/
├── 📂 app/                    # 应用程序源码
├── � docs/                   # 技术文档体系  
├── � tests/                  # 测试代码体系
├── 📂 tools/                  # DevOps自动化工具
├── 📂 logs/                   # 运行时日志文件
├── 📂 alembic/                # 数据库版本迁移
├── � PROJECT-FOUNDATION.md   # 本文档 (项目基础设定)
├── 📄 MASTER.md              # AI开发控制文档
├── 📄 README.md              # 项目入口和概览文档
├── 📄 requirements.txt        # Python生产环境依赖
├── 📄 requirements_dev.txt    # Python开发环境依赖
├── 📄 pyproject.toml         # 项目配置和构建设置  
├── 📄 docker-compose.yml     # 容器编排配置
├── 📄 alembic.ini            # 数据库迁移工具配置
└── � start.ps1              # 项目启动脚本
```

### 核心目录职责
| 目录 | 核心职责 | 管理标准 |
|------|---------|---------|
| `app/` | 应用程序源代码 | code-standards.md |
| `docs/` | 技术文档和规范 | document-management-standards.md |
| `tests/` | 测试代码和测试数据 | testing-standards.md |
| `tools/` | 自动化工具和脚本 | scripts-standards.md |
| `logs/` | 运行时日志记录 | logging-standards.md |
| `alembic/` | 数据库迁移管理 | database-standards.md |

## ⚖️ 文档权威体系

### 权威等级金字塔
```
                    PROJECT-FOUNDATION.md
                    (项目宪法级最高权威)
                           ▲
                  ┌────────┼────────┐
                  │        │        │
            需求分析层   架构设计层   标准层
            (业务权威)   (技术权威)   (质量权威)
                  │        │        │
                  └────────┼────────┘
                           ▼
                     详细设计层
                    (实现规范权威)
```

### 依赖关系约束矩阵
| 文档层级 | 可引用层级 | 禁止引用层级 | 权威关系 |
|---------|-----------|------------|----------|
| **需求分析层** | PROJECT-FOUNDATION.md | 架构、设计、标准层 | 业务需求最高权威 |
| **架构设计层** | 需求层、PROJECT-FOUNDATION.md | 详细设计层 | 技术架构最高权威 |
| **详细设计层** | 需求层、架构层、标准层 | 无 | 受架构约束的实现权威 |
| **标准层** | PROJECT-FOUNDATION.md | 需求、架构、设计层 | 质量标准横向约束权威 |

### 权威冲突解决机制
1. **PROJECT-FOUNDATION.md** > 所有其他文档 (宪法级绝对权威)
2. **需求分析** vs **架构设计**: 需求定义WHAT，架构定义HOW，职责互补无冲突
3. **架构设计** > **详细设计**: 架构约束实现，实现不得违反架构边界
4. **标准层** ⊥ **所有层**: 横向质量约束，与其他层级形成交叉制约关系
5. **冲突解决流程**: 通过ADR决策记录机制解决重大权威冲突

## 🏷️ 业务模块核心映射

### 核心模块名称映射
| 业务概念名 | 技术实现名 | API路径前缀 |
|------------|------------|-------------|
| user-auth | user_auth | /auth/* |
| shopping-cart | shopping_cart | /cart/* |
| product-catalog | product_catalog | /products/* |
| order-management | order_management | /orders/* |
| payment-service | payment_service | /payments/* |
| inventory-management | inventory_management | /inventory/* |

> **完整映射表**: 详见 [naming-conventions-standards.md](docs/standards/naming-conventions-standards.md)

## 🚫 核心约束原则

### 根目录层面禁止
- ❌ 创建未在本文档定义的目录或文件
- ❌ 修改根目录强制文件的文件名或位置
- ❌ 在根目录放置临时文件、日志文件、缓存文件

### 跨目录污染禁止
- ❌ 在 `app/` 目录中放置测试相关文件  
- ❌ 在 `tests/` 目录中放置生产业务代码
- ❌ 在 `docs/` 目录中放置可执行文件或源码

### 权威违反禁止
- ❌ 绕过本文档定义直接修改基础架构
- ❌ 不经ADR流程修改本基础设定文档
- ❌ 违反依赖关系约束矩阵的引用规则

## 🔒 变更控制机制

### 变更控制级别
- **CRITICAL**: 目录结构、权威关系、基本规则 - 需经ADR流程
- **MAJOR**: 模块映射、依赖关系规则 - 需架构评审  
- **MINOR**: 说明文档、补充内容 - 可直接修改

### 维护责任
- **主要维护者**: 系统架构师
- **变更审批者**: 技术负责人 + 产品负责人
- **同步执行者**: 全体开发人员

---

**📋 检查点标记**: [CHECK:ARCH-001] [CHECK:DOC-006]  
**🔗 关联决策**: [ADR-003](docs/adr/ADR-003-document-architecture-restructure.md)  
**📅 创建时间**: 2025-09-24  
**� 维护责任**: 系统架构师  
**🔄 下次审查**: 2025-12-24
