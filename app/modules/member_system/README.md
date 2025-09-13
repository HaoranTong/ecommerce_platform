# 会员系统模块

## 模块概述

提供会员等级、积分、权益管理功能

## 核心功能

- 会员等级管理
- 积分累计使用
- 会员权益配置
- 会员数据分析

## API接口

- **路径前缀**: `/api/member-system/`
- **路由文件**: `router.py`
- **认证要求**: 根据具体接口要求
- **权限控制**: 支持用户和管理员不同权限级别

## 模块文件

`
member_system/
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
from app.modules.member_system.router import router

# 注册到主应用
app.include_router(router, prefix="/api/member-system/")
`

### 服务调用示例

`python
# 导入服务
from app.modules.member_system.service import member_systemService

# 在其他模块中使用
service = member_systemService(db)
`

## 相关文档

- [API设计标准](../../../docs/standards/api-standards.md)
- [数据库设计规范](../../../docs/standards/database-standards.md)
- [模块开发指南](../../../docs/development/module-development-guide.md)

## 开发状态

- ✅ 模块结构创建
- 🔄 功能开发中
- ⏳ 待完善测试
- ⏳ 待完善文档

## 更新日志

### 2025-09-13
- 创建模块基础结构
- 初始化模块文件
- 添加模块README文档
