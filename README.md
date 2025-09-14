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
├── app/                    # 应用程序源码
├── docs/                   # 项目技术文档
├── tests/                  # 测试代码
├── scripts/                # 自动化脚本
├── alembic/               # 数据库迁移
└── requirements.txt       # 项目依赖
│   │   │   └── dependencies.py       # 模块依赖
│   │   ├── product_catalog/          # 商品管理模块
│   │   ├── shopping_cart/            # 购物车模块
│   │   ├── order_management/         # 订单管理模块
│   │   ├── payment_service/          # 支付服务模块
│   │   ├── batch_traceability/       # 批次溯源模块
│   │   └── ... (18个其他模块)        # 其他业务模块
│   └── main.py                       # FastAPI应用入口
│   │   └── __init__.py          # API包初始化
│   ├── models/                  # 数据模型（SQLAlchemy）
│   │   ├── base.py              # 基础模型类
│   │   ├── user.py              # 用户模型
│   │   ├── product.py           # 商品模型
│   │   ├── order.py             # 订单模型
│   │   ├── payment.py           # 支付模型
│   │   └── __init__.py          # 模型统一导出
│   ├── schemas/                 # 数据验证模式（Pydantic）
│   │   ├── base.py              # 基础模式类
│   │   ├── user.py              # 用户相关模式
│   │   ├── product.py           # 商品相关模式
│   │   ├── order.py             # 订单相关模式
│   │   ├── payment.py           # 支付相关模式
│   │   └── __init__.py          # 模式统一导出
│   ├── services/                # 业务逻辑服务
│   │   ├── user_service.py      # 用户业务服务
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

### 支付管理 `/api/v1/payments`
- `POST /` - 创建支付
- `GET /{id}` - 获取支付状态
- `POST /{id}/confirm` - 确认支付
- `POST /refunds` - 申请退款

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
│   └── test_*.py                # 单元测试
├── 🛠️ scripts/                  # 自动化脚本
│   ├── smoke_test.ps1           # 冒烟测试
│   ├── feature_finish.ps1       # 功能完成流程
│   └── release_to_main.ps1      # 发布脚本
├── 🗄️ alembic/                  # 数据库迁移
│   ├── versions/                # 迁移版本文件
│   └── env.py                   # 迁移环境配置
├── 🔧 .github/                  # CI/CD工作流
##  文档导航

- [📋 项目文档](docs/) - 完整技术文档中心
- [🏗️ 系统架构](docs/architecture/) - 架构设计与技术选型
- [📦 功能模块](docs/modules/) - 业务模块设计文档
- [📡 API规范](docs/standards/api-standards.md) - 接口设计标准
- [💻 开发指南](docs/development/) - 开发环境配置
- [🚀 部署运维](docs/operations/) - 生产环境部署
- [🛠️ 开发规范](docs/standards/) - 代码标准与流程

## 🎯 项目状态

当前版本：**开发阶段**  
主要分支：`feature/add-user-auth`

### 核心模块完成情况
- ✅ 用户认证模块 - JWT认证、权限管理
- ✅ 商品管理模块 - 商品CRUD、分类体系  
- ✅ 购物车模块 - Redis存储、实时计算
- ✅ 订单管理模块 - 订单流程、状态管理
- ✅ 支付服务模块 - 多渠道支付集成
- � 农产品溯源模块 - 开发中
- � 物流管理模块 - 开发中

---

**💡 提示：** 详细的开发文档和API规范请查看 [`docs/`](docs/) 目录