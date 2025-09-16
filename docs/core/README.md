# 核心基础设施文档

📝 **文档类型**: 核心基础设施导航  
📍 **作用**: 提供系统核心基础设施组件的文档导航和技术说明  
🔗 **使用方法**: 查找核心组件的技术文档和API说明

## 📂 目录结构

```
core/
├── application-core/      # 应用程序核心框架
├── database-core/         # 数据库连接和事务管理
├── database-utils/        # 数据库工具和维护脚本
└── redis-cache/          # Redis缓存管理
```

## 🏗️ 核心组件说明

### 应用程序核心 (application-core)
- **功能**: FastAPI应用框架、配置管理、启动逻辑
- **文档**: [application-core/](./application-core/)
- **代码位置**: `app/core/`
- **依赖关系**: 被所有业务模块依赖

### 数据库核心 (database-core)
- **功能**: 数据库连接池、事务管理、SQLAlchemy配置
- **文档**: [database-core/](./database-core/)
- **代码位置**: `app/core/database.py`
- **依赖关系**: 被所有数据访问层依赖

### 数据库工具 (database-utils)
- **功能**: 数据迁移、维护脚本、数据库管理工具
- **文档**: [database-utils/](./database-utils/)
- **代码位置**: `app/core/utils/`
- **依赖关系**: 独立工具，供开发和运维使用

### Redis缓存 (redis-cache)
- **功能**: 缓存策略、会话存储、分布式锁
- **文档**: [redis-cache/](./redis-cache/)
- **代码位置**: `app/core/redis_client.py`
- **依赖关系**: 被需要缓存的业务模块依赖

## 🔗 相关文档
- [系统架构总览](../architecture/overview.md) - 整体架构设计
- [共享组件文档](../shared/) - 共享模块和工具
- [业务模块文档](../modules/) - 业务功能模块
- [开发规范](../standards/) - 开发标准和规范