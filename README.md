# 电商平台后端服务

> 基于FastAPI构建的模块化农产品电商平台，采用文档驱├── 📝 alembic├── 📊 reports/                 # 测试和分析报告输出
├── 📂 .github/                 # GitHub工作流和CI/CD配置
├── 📋 PROJECT-FOUNDATION.md    # 项目基础架构设定 (最高权威文档)
├── 📄 MASTER.md               # AI开发控制文档
├── 📄 README.md               # 项目入口导航文档 (本文档)
├── 📄 requirements.txt         # 生产环境Python依赖
├── 📄 requirements_dev.txt     # 开发环境Python依赖
├── 📄 pyproject.toml          # 项目配置和构建设置
├── 📄 docker-compose.yml      # 容器编排配置
├── 📄 alembic.ini             # 数据库迁移工具配置
├── 🚀 start.ps1               # 项目启动脚本
├── 🔧 .env                    # 环境变量配置 (本地开发)
├── 📝 .env.example            # 环境变量配置模板
├── 📝 .envrc                  # direnv自动环境加载配置
└── 📄 .gitignore              # Git版本控制忽略规则      # 数据库版本迁移
├── 📊 reports/                 # 测试和分析报告输出
├── 📂 .github/                 # GitHub工作流和CI/CD配置
├── 📋 PROJECT-FOUNDATION.md    # 项目基础架构设定 (最高权威文档)
├── 📄 MASTER.md               # AI开发控制文档
├── 📄 README.md               # 项目入口导航文档 (本文档)
├── 📄 requirements.txt         # 生产环境Python依赖
├── 📄 requirements_dev.txt     # 开发环境Python依赖
├── 📄 pyproject.toml          # 项目配置和构建设置
├── 📄 docker-compose.yml      # 容器编排配置
├── 📄 alembic.ini             # 数据库迁移工具配置
├── 🚀 start.ps1               # 项目启动脚本
├── 🔧 .env                    # 环境变量配置 (本地开发)
├── 📝 .env.example            # 环境变量配置模板
├── 📝 .envrc                  # direnv自动环境加载配置
└── 📄 .gitignore              # Git版本控制忽略规则## 🎯 核心特性
- 🏗️ **模块化单体架构** - 垂直切片模块化设计，清晰边界
- 🌾 **农产品电商** - 专注农产品溯源、质量认证、冷链物流  
- 🔐 **JWT认证体系** - 完整的用户认证与权限管理
- 🛒 **高性能购物车** - 基于Redis的分布式购物车系统
- � **商品管理系统** - 商品信息、分类管理、库存控制
- 💳 **多渠道支付** - 支持多种支付方式和退款处理
- 🔄 **标准化工具链** - 自动化开发、测试、部署流程

## �🚀 快速开始

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

## 📁 项目结构

根目录结构（详细结构请参考 [📖 项目基础设定](PROJECT-FOUNDATION.md)）：

```
ecommerce_platform/
├── 📂 app/                     # 应用程序源码 (19个业务模块)
├── 📚 docs/                    # 技术文档体系 (详见 docs/README.md)
├── 🧪 tests/                   # 测试代码体系 (6种测试类型)
├── 🛠️ tools/                   # 自动化工具和脚本 (13个工具脚本)
├── � logs/                    # 运行时日志文件
├── 📝 alembic/                 # 数据库版本迁移
├── � PROJECT-FOUNDATION.md    # 项目基础架构设定 (最高权威文档)
├── � MASTER.md               # AI开发控制文档
├── � README.md               # 项目入口导航文档 (本文档)
├── 📄 requirements.txt         # 生产环境Python依赖
├── 📄 requirements_dev.txt     # 开发环境Python依赖
├── 📄 pyproject.toml          # 项目配置和构建设置
├── 📄 docker-compose.yml      # 容器编排配置
├── 📄 alembic.ini             # 数据库迁移工具配置
├── 🚀 start.ps1               # 项目启动脚本
├── 🔧 dev_env.ps1             # 开发环境配置脚本
├── 🛠️ dev_tools.ps1           # 开发工具启动脚本
└── 📄 .gitignore              # Git版本控制忽略配置
```

> **📖 详细信息**: 
> - 完整目录结构和权威定义：[PROJECT-FOUNDATION.md](PROJECT-FOUNDATION.md)
> - 应用模块详细说明：[app/README.md](app/README.md)  
> - 技术文档导航中心：[docs/README.md](docs/README.md)
> - 测试代码结构说明：[tests/README.md](tests/README.md)
> - 自动化脚本使用指南：[tools/README.md](tools/README.md)

## 🧭 快速导航

### 📋 开发标准文档体系 
🎯 **统一入口**: [📖 技术文档导航中心](docs/README.md) - AI友好检索和完整文档索引

| 层级 | 文档名称 | 职责范围 | 使用场景 |
|------|----------|----------|----------|
| **FOUNDATION** | [项目基础设定](PROJECT-FOUNDATION.md) | 项目目录结构权威定义 | 🏗️ 新建目录/文件 |
| **L1核心** | [命名规范总纲](docs/standards/naming-conventions-standards.md) | 全局命名规则权威定义 | 🔤 命名决策 |
| **L2领域** | [数据库设计标准](docs/standards/database-standards.md) | 数据库设计和ORM规范 | 🗄️ 数据建模 |
| **L2领域** | [API设计标准](docs/standards/api-standards.md) | RESTful API设计规范 | 🌐 接口设计 |
| **L2领域** | [代码标准规范](docs/standards/code-standards.md) | 代码质量和开发实践 | 💻 编码规范 |
| **L2领域** | [脚本管理标准](docs/standards/scripts-standards.md) | DevOps脚本管理规范 | 🛠️ 自动化脚本 |

### 🔧 开发工具快速通道
- **[自动化脚本总览](tools/README.md)** - 13个开发和运维自动化工具
- **[工具使用指南](docs/operations/README.md)** - 详细的工具文档和操作手册

### 📚 核心技术文档
- **[需求分析](docs/requirements/)** - 业务需求和系统需求分析
- **[系统架构](docs/architecture/)** - 架构设计和技术选型决策  
- **[模块设计](docs/design/modules/)** - 19个业务模块详细设计文档
- **[运维指南](docs/operations/)** - 部署、监控、故障处理指南

### 📊 项目状态与进展
- **[项目状态概览](docs/status/README.md)** - 当前版本和开发进度跟踪
- **[更新日志](docs/status/changelog.md)** - 版本更新和变更记录
- **[开发贡献指南](docs/development/contributing.md)** - 参与开发的规范和流程

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**💡 提示**: 详细的开发文档和API规范请查看 [📖 技术文档导航中心](docs/README.md)
