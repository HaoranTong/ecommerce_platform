# 技术组件设计文档

📝 **文档类型**: 技术组件导航  
📍 **作用**: 提供跨模块技术组件的设计文档和使用说明  
🔗 **使用方法**: 查找技术组件的接口定义、实现细节和使用方法

## 📂 目录结构

```
components/
├── application-core/     # 应用核心组件
├── base-models/          # 基础数据模型和ORM混入类
├── database-core/        # 数据库核心组件
├── database-utils/       # 数据库工具组件
├── redis-cache/          # Redis缓存组件
└── README.md            # 技术组件导航（本文档）
```

## 🔧 技术组件说明

### 应用核心组件 (application-core)
- **功能**: FastAPI应用入口、生命周期管理、路由注册
- **文档**: [application-core/](./application-core/)
- **代码位置**: `app/main.py`
- **职责**: 应用初始化、中间件配置、全局错误处理

### 基础数据模型 (base-models)  
- **功能**: ORM基础类、模型混入、通用数据类型定义
- **文档**: [base-models/](./base-models/)
- **代码位置**: `app/shared/base_models.py`, `app/shared/models.py`
- **职责**: SQLAlchemy基础类、时间戳混入、软删除混入、审计混入

### 数据库核心 (database-core)
- **功能**: 数据库连接、会话管理、事务控制
- **文档**: [database-core/](./database-core/)
- **代码位置**: `app/core/database.py`
- **职责**: 数据库引擎配置、会话生命周期、连接池管理

### 数据库工具 (database-utils)
- **功能**: 数据库工具函数、查询优化、批量操作
- **文档**: [database-utils/](./database-utils/)  
- **代码位置**: `app/core/database_utils.py`
- **职责**: 通用查询、分页工具、数据迁移工具

### Redis缓存 (redis-cache)
- **功能**: Redis连接、缓存策略、分布式锁
- **文档**: [redis-cache/](./redis-cache/)
- **代码位置**: `app/core/redis.py`
- **职责**: 缓存管理、会话存储、分布式锁实现

## 💡 使用指南

各技术组件的详细使用说明和API文档请查看对应组件目录中的文档：
- `overview.md` - 组件功能概述和架构说明
- `api-spec.md` - 组件接口规范和使用方法
- `api-implementation.md` - 组件实现细节和配置说明

## 🔗 相关文档
- [系统级设计文档](../system/) - 系统架构和技术选型
- [业务模块文档](../modules/) - 业务功能模块设计
- [开发标准文档](../../standards/) - 开发规范和最佳实践
