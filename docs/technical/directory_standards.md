# 目录架构标准

## 当前目录结构（保持不变）

```
e:\ecommerce_platform\
├── app/                    # FastAPI 应用代码
│   ├── __init__.py
│   ├── main.py            # 应用入口
│   ├── db.py              # 数据库连接
│   ├── models.py          # SQLAlchemy 模型
│   └── api/               # API 路由
│       ├── __init__.py
│       ├── routes.py      # 基础路由（用户管理）
│       ├── schemas.py     # Pydantic 模型
│       ├── product_routes.py    # 商品路由
│       └── certificate_routes.py # 证书路由（考虑重构）
├── alembic/               # 数据库迁移
│   ├── env.py
│   └── versions/
├── docs/                  # 文档
│   ├── openapi.yaml       # API 契约（新增）
│   ├── event-schemas/     # 事件 Schema（新增）
│   ├── technical/         # 技术文档
│   ├── status/           # 状态日志
│   └── usage/            # 使用文档
├── scripts/              # 自动化脚本
│   ├── smoke_test.ps1    # 烟雾测试
│   ├── feature_finish.ps1 # 功能完成
│   ├── release_to_main.ps1 # 发布到主干
│   └── log_status.ps1    # 状态日志
├── tests/                # 测试代码
├── requirements.txt      # Python 依赖
├── alembic.ini          # Alembic 配置
├── docker-compose.yml   # 开发环境
└── README.md            # 项目说明
```

## 规划的扩展结构（渐进式扩展）

**阶段 1：Mini-MVP（当前）**
- 保持现有结构不变
- 补全缺失的契约文件

**阶段 2：添加前端支持**
```
├── frontend/             # 前端代码（新增）
│   ├── miniprogram/     # 微信小程序
│   │   ├── pages/
│   │   ├── components/
│   │   ├── utils/
│   │   └── app.js
│   └── admin/           # 后台管理（预留）
```

**阶段 3：基础设施完善**
```
├── infra/               # 基础设施（新增）
│   ├── docker/          # Docker 相关
│   ├── k8s/            # Kubernetes 配置
│   └── scripts/        # 部署脚本
```

## 文件命名规范

### Python 模块
- 使用小写+下划线：`user_service.py`
- 路由文件：`{resource}_routes.py`
- 模型文件：按业务领域分组

### 文档文件
- OpenAPI：`openapi.yaml`
- 事件 Schema：`{EventType}.v{Version}.json`
- 技术文档：中文文件名 + 版本号

### 数据库迁移
- 使用描述性名称：`add_user_table`
- 版本号格式：`YYYY_MM_DD_sequential`

## 模块组织原则

1. **按功能域分组**：每个业务领域独立模块
2. **契约优先**：所有接口变更先更新 OpenAPI
3. **事件驱动**：重要操作发布事件
4. **测试并行**：每个模块对应测试文件

## 依赖管理

- 生产依赖：`requirements.txt`
- 开发依赖：`requirements-dev.txt`（将创建）
- 测试依赖：包含在开发依赖中

## 配置管理

- 环境变量：使用 `.env` 文件（本地）
- 配置类：`app/config.py`（将创建）
- 敏感信息：使用环境变量，不入库
