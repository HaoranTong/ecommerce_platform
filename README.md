# 电商平台后端服务

> 基于FastAPI构建的模块化农产品电商平台，采用文档驱动开发和标准化架构

## 🎯 核心特性
- 🏗️ **模块化单体架构** - 垂直切片模块化设计，清晰边界
- 🌾 **农产品电商** - 专注农产品溯源、质量认证、冷链物流
- 🔗 **业务领域驱动** - 按业务领域组织代码，模块边界清晰
- � **JWT认证体系** - 完整的用户认证与权限管理
- �🛒 **高性能购物车** - 基于Redis的分布式购物车系统
- 📦 **商品管理系统** - 商品信息、分类管理、库存控制
- � **多渠道支付** - 支持多种支付方式和退款处理
- 🔄 **标准化工具链** - 自动化开发、测试、部署流程

## 📁 项目结构

```
ecommerce_platform/
├── 📂 app/                     # 应用程序源码
│   ├── main.py                 # FastAPI应用入口
│   ├── core/                   # 核心基础设施
│   │   ├── auth.py            # 认证管理
│   │   ├── database.py        # 数据库连接
│   │   ├── redis_client.py    # Redis客户端
│   │   └── security_logger.py # 安全日志
│   ├── shared/                 # 共享组件
│   │   ├── base_models.py     # 基础数据模型
│   │   ├── base_schemas.py    # 基础验证模式
│   │   └── api_schemas.py     # API通用模式
│   └── modules/                # 业务功能模块 (19个)
│       ├── user_auth/         # 用户认证模块
│       ├── product_catalog/   # 商品管理模块  
│       ├── shopping_cart/     # 购物车模块
│       ├── order_management/  # 订单管理模块
│       ├── payment_service/   # 支付服务模块
│       ├── batch_traceability/ # 批次溯源模块
│       └── ... (13个其他模块) # 其他业务模块
├── 📚 docs/                    # 项目技术文档
│   ├── README.md              # 文档导航中心
│   ├── core/                  # 核心组件文档
│   ├── shared/                # 共享组件文档
│   ├── modules/               # 业务模块文档 (19个)
│   ├── architecture/          # 系统架构设计
│   ├── adr/                   # 架构决策记录 (ADR)
│   ├── standards/             # 开发规范标准
│   ├── development/           # 开发环境指南
│   ├── operations/            # 运维部署文档
│   ├── requirements/          # 需求分析文档
│   └── templates/             # 文档标准模板
├── 🧪 tests/                   # 测试代码
├── 🛠️ scripts/                 # 自动化脚本
├── 📝 alembic/                 # 数据库迁移
├── 📊 logs/                    # 日志文件
├── 📋 根目录配置文件/           # 项目配置与工具
│   ├── requirements.txt       # 生产环境依赖包
│   ├── requirements_dev.txt   # 开发环境依赖包
│   ├── pyproject.toml         # Python项目配置
│   ├── alembic.ini            # 数据库迁移配置
│   ├── docker-compose.yml     # 容器编排配置
│   ├── start.ps1              # 项目启动脚本
│   ├── dev_env.ps1           # 开发环境配置脚本
│   ├── dev_tools.ps1         # 开发工具启动脚本
│   ├── .env.example          # 环境变量配置模板
│   ├── .gitignore            # Git忽略文件配置
│   ├── .envrc                # 环境自动加载配置
│   ├── .coverage             # 测试覆盖率配置
│   └── MASTER.md             # AI开发规范控制文档
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- MySQL 8.0+ 或 PostgreSQL 13+
- Redis 7.0+

### 安装启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd ecommerce_platform

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等信息

# 4. 数据库迁移
alembic upgrade head

# 5. 启动服务
python -m app.main
# 或使用脚本: .\start.ps1
```

### 开发工具
```bash
# 运行测试
pytest

# 代码规范检查
.\scripts\check_naming_compliance.ps1

# 冒烟测试
.\scripts\smoke_test.ps1
```
- `POST /` - 创建订单
- `GET /{id}` - 获取订单详情
- `PUT /{id}/cancel` - 取消订单

### 支付管理 `/api/v1/payment-service`
- `POST /payments` - 创建支付
- `GET /payments/{id}` - 获取支付状态
- `POST /payments/{id}/confirm` - 确认支付
- `POST /payments/refunds` - 申请退款

## 🚀 部署

### 开发环境
```powershell
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload
```

### 生产环境
```bash
# 使用Docker部署
docker-compose up -d

# 或使用Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📝 更新日志

### v1.0.0-phase1 (当前版本) - 2025-09-16
- ✅ **Phase 1 Mini-MVP 实施完成**
- ✅ 支付服务模块：完整的支付、退款业务逻辑及API实现
- ✅ 库存管理模块：高性能库存管理系统及优化
- ✅ 用户认证模块：JWT认证体系和权限管理基础
- ✅ 测试框架建设：22个单元测试用例，SQLite内存数据库
- ✅ 性能优化：async/await优化，模块导入架构规范化
- ✅ 架构验证：核心模块成功导入，MASTER规范符合性验证

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
## � 文档导航

### 🎯 核心开发文档 (优先查阅)
- [🗓️ **开发计划速览**](DEVELOPMENT_PLAN.md) - **6期迭代计划快速导航** ⭐
- [📋 **完整开发计划**](docs/requirements/functional.md#迭代计划) - 详细迭代规划和功能优先级
- [📋 功能需求规范](docs/requirements/functional.md) - 详细功能需求与业务规则
- [🏗️ 系统架构设计](docs/architecture/overview.md) - 技术架构与设计原则
- [📦 业务模块文档](docs/modules/) - 19个完整模块设计文档

### 📚 完整文档导航
- [📋 项目文档](docs/) - 完整技术文档中心
- [🏗️ 系统架构](docs/architecture/) - 架构设计与技术选型  
- [📦 功能模块](docs/modules/) - 业务模块设计文档 (19个完整模块)
- [🔧 核心组件](docs/core/) - 应用核心基础设施文档
- [🔗 共享组件](docs/shared/) - 通用数据模型和工具  
- [📡 API规范](docs/standards/api-standards.md) - 接口设计标准
- [💻 开发指南](docs/development/) - 开发环境配置
- [🚀 部署运维](docs/operations/) - 生产环境部署
- [🛠️ 开发规范](docs/standards/) - 代码标准与流程

## 🎯 项目状态

当前版本：**Phase 1 Mini-MVP 完成**  
主要分支：`dev` → `main`

### Phase 1 实施完成情况 (100%)
- ✅ **支付服务模块** - 完整技术实现 (文档、模型、服务、API、测试)
- ✅ **库存管理模块** - 完整技术实现 + 性能优化
- ✅ **用户认证模块** - 基础架构实现
- ✅ **核心基础设施** - 数据库、Redis、认证、安全日志
- ✅ **测试框架** - 单元测试、集成测试环境搭建
- ✅ **模块化架构** - 严格边界、清晰依赖、标准化导入

### 技术实现亮点
- 🏗️ **模块化单体架构** - 基于业务领域的垂直切分
- 💳 **支付服务** - 完整支付流程、退款管理、多渠道支持  
- 📦 **库存管理** - 预占机制、批量操作、阈值预警
- ⚡ **性能优化** - 同步/异步方法分离、导入优化
- 🧪 **测试覆盖** - 22个单元测试用例、完整验证流程

---

**💡 提示：** 详细的开发文档和API规范请查看 [`docs/`](docs/) 目录