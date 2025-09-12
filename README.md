# 定制化电商平台

> 专为农产品销售设计的现代化电商平台，基于FastAPI构建

## 🎯 核心特性
- 🛒 高性能购物车系统（Redis存储）
- 👤 JWT用户认证与权限管理  
- 📦 商品管理与订单处理
- 🔄 标准化开发工具链

## 🚀 快速开始

```powershell
# 启动开发环境
.\dev_env.ps1
.\dev_tools.ps1 start-api
```

访问：http://localhost:8000

## � 项目结构

```
ecommerce_platform/
├── 📱 app/                      # 应用程序核心代码
│   ├── api/                     # API路由和接口
│   ├── schemas/                 # 数据验证模型
│   ├── services/                # 业务逻辑服务
│   ├── main.py                  # FastAPI应用入口
│   ├── models.py                # 数据库模型
│   ├── database.py              # 数据库配置
│   └── auth.py                  # 用户认证
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