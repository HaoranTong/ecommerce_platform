# 库存管理模块

## 模块概述

提供库存查询、预占、扣减、调整等功能

## 核心功能

- 库存实时查询
- 库存预占释放
- 库存扣减操作
- 库存调整管理
- 库存预警

## API接口

- **路径前缀**: `/api/inventory-management/`
- **路由文件**: `router.py`
- **认证要求**: 根据具体接口要求
- **权限控制**: 支持用户和管理员不同权限级别

## 模块文件

`
inventory_management/
├── __init__.py          # 模块初始化
├── router.py            # API路由定义
├── service.py           # 业务逻辑服务
├── models.py            # 数据模型定义
├── schemas.py           # 数据验证模式
├── dependencies.py      # 依赖注入配置
└── README.md           # 模块文档(本文件)
`

## 使用入口

### API调用示例

`python
# 导入路由
from app.modules.inventory_management.router import router

# 注册到主应用
app.include_router(router, prefix="/api/inventory-management/")
`

### 服务调用示例

`python
# 导入服务
from app.modules.inventory_management.service import inventory_managementService

# 在其他模块中使用
service = inventory_managementService(db)
`

## 相关文档

- [API设计标准](../../../docs/standards/api-standards.md)
- [数据库设计规范](../../../docs/standards/database-standards.md)
- [模块开发指南](../../../docs/development/module-development-guide.md)

## 开发状态

- ✅ 模块结构创建
- ✅ 核心功能实现完成
- ✅ 性能优化完成 (同步方法优化)
- ✅ 完整文档支持
- ⏳ 单元测试待完善

## 更新日志

### 2025-09-16
- 性能优化：移除不必要的async/await，提升同步操作性能
- 代码质量提升：确保导入架构合规
- 文档状态更新

### 2025-09-13
- 创建模块基础结构
- 初始化模块文件
- 添加模块README文档
