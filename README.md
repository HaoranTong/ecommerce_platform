# 电商平台后端服务

> 基于FastAPI构建的模块化农产品电商平台，采用文档驱动开发和标准化架构

## 🏗️ 技术架构核心 (新手必读)

### **技术栈组合**
- **Web框架**: FastAPI (异步高性能，自动API文档)
- **数据库**: MySQL 8.0 (ACID事务，数据一致性优先)
- **ORM**: SQLAlchemy 2.0 (异步支持，类型提示)
- **缓存**: Redis 7.0 (高性能缓存，消息队列)
- **认证**: JWT + OAuth 2.0 (无状态认证)

### **架构设计原则**
- **模块化单体架构**: 垂直切片业务模块，清晰边界分离
- **异步优先**: 所有I/O密集操作使用async/await模式
- **数据一致性优先**: 关键业务操作事务包装，宁可牺牲性能
- **契约优先**: 接口、数据模型、状态机开发前冻结
- **适配器抽象**: 第三方集成通过适配器接口实现

### **测试架构 (五层架构)**
- **单元测试 (70%)**: Mock测试 + SQLite内存数据库
- **集成测试 (20%)**: MySQL Docker + 真实数据库  
- **E2E测试 (6%)**: 端到端业务流程验证
- **烟雾测试 (2%)**: 基础健康检查
- **专项测试 (2%)**: 性能测试 + 安全测试

### **开发约束 (严格遵守)**
- ❌ **禁止**: 根目录创建未定义文件/目录
- ❌ **禁止**: 跨目录污染 (app/中放测试，tests/中放业务代码)
- ❌ **禁止**: 使用unittest.mock (必须用pytest-mock)
- ❌ **禁止**: 自定义数据库连接 (必须用conftest.py)
- ❌ **禁止**: 绕过ADR流程修改基础架构

### **目录架构说明**
```
app/modules/{模块名}/     # 业务模块 (垂直切片)
├── router.py           # API路由定义
├── service.py          # 业务逻辑层
├── models.py           # 数据模型 (SQLAlchemy)
├── schemas.py          # API模型 (Pydantic)
└── dependencies.py     # 依赖注入
```

## 🎯 项目简介

**核心价值**: 模块化单体架构的农产品电商平台，专注溯源、质量认证和供应链管理，提供完整的JWT认证体系和高性能购物体验。

## 🚀 快速开始

### 环境准备
```powershell
# 1. 克隆并设置环境
git clone https://github.com/HaoranTong/ecommerce_platform.git
cd ecommerce_platform && python -m venv .venv && .venv\Scripts\Activate.ps1

# 2. 安装依赖并验证环境
pip install -r requirements.txt
pytest tests/unit/ -v
```

### 启动步骤
```powershell
# 启动开发服务器
.\start.ps1
```

## 📁 项目结构概览

```
ecommerce_platform/
├── 📂 app/                     # 应用程序源码
├── 📚 docs/                    # 技术文档体系
├── 🧪 tests/                   # 测试代码体系
├── 🛠️ tools/                   # 自动化工具脚本
├── 📝 alembic/                 # 数据库迁移
├── 📊 logs/                    # 运行日志
├── 📊 reports/                 # 分析报告
├── 📂 .github/                 # GitHub工作流配置
├── 📋 PROJECT-FOUNDATION.md    # 项目基础设定 (最高权威)
├── 📄 MASTER.md               # AI开发控制文档
├── 📄 README.md               # 项目入口 (本文档)
├── 📄 requirements.txt         # 生产环境依赖
├── 📄 pyproject.toml          # 项目配置
├── 📄 docker-compose.yml      # 容器编排配置
└── 🚀 start.ps1               # 项目启动脚本
```

## 🧭 快速导航

### 核心入口
- **[📖 项目基础设定](PROJECT-FOUNDATION.md)** - 项目架构权威定义
- **[📖 技术文档中心](docs/README.md)** - 完整技术文档导航
- **[📖 开发工具集](tools/README.md)** - 自动化脚本和工具

### 开发资源
- **[📖 应用代码](app/README.md)** - 源码结构说明
- **[📖 测试体系](tests/README.md)** - 测试代码组织

## 📊 执行状态与健康检查

- **[📖 项目状态](docs/status/README.md)** - 当前开发进度和模块状态

## 📞 联系方式与支撑资源

- **项目负责人**: 产品经理 + AI程序员协作模式
- **技术支撑**: 基于文档驱动开发，所有技术决策记录在[技术文档中心](docs/README.md)
- **问题反馈**: 通过项目状态文档跟踪和管理

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。