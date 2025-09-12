# 电商平台后端服务

> 基于FastAPI构建的模块化电商平台后端服务，采用文档驱动开发和标准化架构

## 🎯 核心特性
- 🏗️ **模块化架构**：Controller→Service→Model三层架构模式
- 🛒 **高性能购物车**：基于Redis的购物车存储系统
- 👤 **用户管理**：JWT认证与权限控制
- 📦 **商品管理**：商品CRUD、分类管理、库存控制
- 🛍️ **订单系统**：订单创建、状态管理、流程控制
- 💰 **支付系统**：多种支付方式、退款处理
- � **数据统计**：业务指标统计和报表
- �🔄 **标准化工具链**：开发、测试、部署自动化

## 🚀 快速开始

### 环境准备
```powershell
# 启动开发环境
.\dev_env.ps1
```

### 启动服务
```powershell
# 启动API服务
.\dev_tools.ps1 start-api

# 或直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问服务
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc  
- **健康检查**: http://localhost:8000/api/health

## 📁 项目结构

```
ecommerce_platform/
├── 📱 app/                      # 应用程序核心代码
│   ├── api/                     # API路由和接口
│   │   ├── routes/              # 模块化路由定义
│   │   │   ├── user.py          # 用户管理路由
│   │   │   ├── product.py       # 商品管理路由
│   │   │   ├── order.py         # 订单管理路由
│   │   │   ├── payment.py       # 支付管理路由
│   │   │   └── __init__.py      # 路由统一导出
│   │   ├── main_routes.py       # 主路由入口
│   │   ├── schemas.py           # API数据模式
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
│   │   ├── product_service.py   # 商品业务服务
│   │   ├── order_service.py     # 订单业务服务
│   │   ├── payment_service.py   # 支付业务服务
│   │   └── __init__.py          # 服务统一导出
│   ├── main.py                  # FastAPI应用入口
│   ├── database.py              # 数据库配置
│   ├── auth.py                  # 用户认证
│   └── __init__.py              # 应用包初始化
├── 📚 docs/                     # 项目文档
│   ├── architecture/            # 系统架构设计
│   ├── api/                     # API接口文档  
│   ├── modules/                 # 功能模块文档
│   ├── development/             # 开发指南
│   ├── operations/              # 运维部署
│   ├── standards/               # 开发规范
│   └── requirements/            # 需求分析
├── 🧪 tests/                    # 测试代码
│   ├── integration/             # 集成测试
│   ├── conftest.py              # pytest配置
│   └── test_*.py                # 单元测试
├── 🛠️ scripts/                  # 自动化脚本
│   ├── smoke_test.ps1           # 冒烟测试
│   ├── feature_finish.ps1       # 功能完成流程
│   └── release_to_main.ps1      # 发布脚本
├── 🗄️ alembic/                  # 数据库迁移
│   ├── versions/                # 迁移版本文件
│   └── alembic.ini              # 迁移配置
├── requirements.txt             # Python依赖包
├── docker-compose.yml           # Docker编排配置
└── README.md                    # 项目说明文档
```

## 🏗️ 架构设计

### 三层架构模式
```
┌─────────────────┐
│   Controller    │  ← API路由层（app/api/routes/）
│    (Routes)     │    处理HTTP请求和响应
└─────────────────┘
         │
┌─────────────────┐
│    Service      │  ← 业务逻辑层（app/services/）
│   (Business)    │    核心业务逻辑处理
└─────────────────┘
         │
┌─────────────────┐
│     Model       │  ← 数据访问层（app/models/）
│   (Database)    │    数据库操作和模型定义
└─────────────────┘
```

### 模块化设计
- **用户模块**: 注册、登录、权限管理
- **商品模块**: 商品CRUD、分类管理、库存控制
- **订单模块**: 订单创建、状态管理、购物车
- **支付模块**: 支付处理、退款管理、统计

## 🛠️ 开发规范

### 代码标准
- 遵循PEP 8代码规范
- 文件头注释包含功能描述和依赖说明
- 统一的错误处理和响应格式
- 完整的类型注解和文档字符串

### API设计
- RESTful API设计原则
- 统一的响应格式和状态码
- 完整的接口文档和示例
- 请求验证和错误处理

## 🧪 测试

```powershell
# 运行所有测试
pytest

# 运行冒烟测试
.\scripts\smoke_test.ps1

# 生成测试报告
pytest --cov=app --cov-report=html
```

## 📖 API文档

### 用户管理 `/api/v1/users`
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户信息
- `PUT /me` - 更新用户信息

### 商品管理 `/api/v1/products`
- `GET /` - 获取商品列表
- `POST /` - 创建商品（管理员）
- `GET /{id}` - 获取商品详情
- `PUT /{id}` - 更新商品（管理员）

### 订单管理 `/api/v1/orders`
- `GET /` - 获取订单列表
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
│   └── workflows/               # GitHub Actions
├── ⚙️ 配置文件
│   ├── docker-compose.yml       # 容器编排
│   ├── requirements.txt         # Python依赖
│   ├── alembic.ini              # 数据库迁移配置
│   └── .env.example             # 环境变量模板
├── 🚀 启动脚本
│   ├── start.ps1                # 项目启动
│   ├── dev_env.ps1              # 开发环境配置
│   └── dev_tools.ps1            # 开发工具集
└── 🧪 临时测试脚本 (开发期间)
    ├── test_auth_integration.py # 认证功能集成测试
    ├── test_inventory_api.py    # 库存API功能测试
    └── test_inventory_integration.py # 库存集成测试
```

> **📝 说明**：根目录的`test_*.py`文件为开发调试期间的临时测试脚本，用于快速验证功能。功能开发完成后将移至`tests/`目录进行长期维护。

## �📚 文档导航

- [📋 项目文档](docs/) - 完整技术文档
- [🏗️ 系统架构](docs/architecture/) - 架构设计与技术选型  
- [📡 API接口](docs/api/) - 接口规范与使用说明
- [💻 开发指南](docs/development/) - 开发环境与工具
- [🚀 部署运维](docs/operations/) - 部署配置与运维

## 📞 支持

- 📖 [完整文档](docs/)
- 🐛 [问题反馈](../../issues)
- 📧 技术支持：[联系方式]

---
⚡ 快速开始请查看 [开发指南](docs/development/README.md)