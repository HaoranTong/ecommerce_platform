# 文档索引

## 项目概述
本项目是一个基于FastAPI的定制化电商平台，主要用于五常大米等农产品的在线销售。

## 文档分类

### 📚 用户文档
- [README.md](../README.md) - 项目概述和快速启动指南
- [开发工具使用指南](development_tools_guide.md) - 标准化开发工具说明

### 🏗️ 技术文档
- [购物车系统技术文档](technical/shopping_cart_system.md) - 购物车模块完整技术文档
- [订单管理系统技术文档](technical/order_management_system.md) - 订单管理技术规范
- [定制化电商平台功能需求方案](technical/定制化电商平台功能需求方案-1.0.md) - 业务需求文档

### 📡 API文档
- [购物车API文档](api/cart_api.md) - 购物车相关API接口文档
- [OpenAPI规范](openapi.yaml) - 完整的API规范文件

### 🔧 开发文档
- [开发工作流程规范](development_workflow.md) - 标准化开发流程
- [代码审查报告](cart_code_review_report.md) - 购物车功能代码审查
- [代码清理进度](code_cleanup_progress.md) - 技术债务清理记录

### 📊 状态文档
- [项目总体状态](status/项目总体状态-20250909.md) - 项目整体进展
- [系统监控看板](status/系统监控看板-20250909.md) - 系统运行状态监控

## 文档更新记录

### 2025-09-09
- ✅ 完成购物车系统技术文档
- ✅ 创建购物车API文档  
- ✅ 更新开发工具使用指南
- ✅ 规范化文档结构
- ✅ 更新README.md主文档

### 历史记录
- 2025-09-08: 创建项目基础文档
- 2025-09-07: 初始化项目文档结构

## 文档贡献指南

### 文档规范
1. **技术文档**: 使用Markdown格式，包含完整的技术细节
2. **API文档**: 遵循OpenAPI规范，包含请求/响应示例
3. **用户文档**: 简洁明了，包含实际使用示例
4. **更新记录**: 每次更新都要记录变更内容和日期

### 文档结构
```
docs/
├── README.md                   # 文档索引（本文件）
├── development_tools_guide.md  # 开发工具指南
├── development_workflow.md     # 开发流程规范
├── cart_code_review_report.md  # 代码审查报告
├── code_cleanup_progress.md    # 清理进度记录
├── technical/                  # 技术文档目录
│   ├── shopping_cart_system.md
│   ├── order_management_system.md
│   └── ...
├── api/                        # API文档目录
│   ├── cart_api.md
│   └── ...
└── status/                     # 状态文档目录
    ├── 项目总体状态-20250909.md
    └── ...
```

### 维护责任
- **技术文档**: 开发团队维护
- **API文档**: 与代码同步更新
- **用户文档**: 产品团队维护
- **状态文档**: 项目经理维护

## 相关资源

### 外部链接
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Redis文档](https://redis.io/documentation)

### 项目链接
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/health
