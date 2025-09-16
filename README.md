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
│   ├── standards/             # 开发规范标准
│   ├── development/           # 开发环境指南
│   ├── operations/            # 运维部署文档
│   ├── requirements/          # 需求分析文档
│   └── templates/             # 文档标准模板
├── 🧪 tests/                   # 测试代码
├── 🛠️ scripts/                 # 自动化脚本
├── 📝 alembic/                 # 数据库迁移
├── 📊 logs/                    # 日志文件
├── requirements.txt           # 项目依赖
└── docker-compose.yml         # 容器配置
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

### v1.0.0 (当前版本)
- ✅ 完成模块化架构重构
- ✅ 实现三层架构模式
- ✅ 完成用户、商品、订单、支付模块
- ✅ 统一代码规范和文档标准
- ✅ 优化项目结构和依赖管理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
## � 文档导航

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

当前版本：**文档标准化完成**  
主要分支：`main`

### 模块文档完成情况 (100%)
- ✅ **19个业务模块** - 完整7文档结构 (README + 需求 + 设计 + API规范 + API实现 + 实现记录 + 概览)
- ✅ **5个核心组件** - 应用框架、数据库、缓存、工具组件完整文档
- ✅ **1个共享组件** - 基础数据模型标准化文档
- ✅ **自动化工具** - 文档生成、完整性检查、标准验证工具
- ✅ **文档架构** - 分离式结构、依赖管理、模板标准化

---

**💡 提示：** 详细的开发文档和API规范请查看 [`docs/`](docs/) 目录