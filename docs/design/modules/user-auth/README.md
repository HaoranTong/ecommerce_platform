<!--
文档说明：
- 内容：模块README导航模板，模块入口文档
- 作用：提供快速导航和基本信息，不包含详细内容
- 使用方法：复制此模板，替换模板变量，保持简洁
-->

# user-auth用户认证模块

📋 **状态**: 文档驱动开发验证中  
👤 **负责人**: 开发团队  
🔄 **最后更新**: 2025-09-25  

## 快速导航

| 文档类型 | 文档名称 | 描述 |
|---------|----------|------|
| **概述** | [overview.md](./overview.md) | 模块详细概述和技术架构 |
| **需求** | [requirements.md](./requirements.md) | 业务需求和功能规格 |
| **设计** | [design.md](./design.md) | 技术设计和架构决策 |
| **API规范** | [api-spec.md](./api-spec.md) | API接口规范定义 |
| **API实施** | [api-implementation.md](./api-implementation.md) | API开发实施记录 |
| **实现** | [implementation.md](./implementation.md) | 开发实现详细记录 |

## 模块简介

用户认证模块是电商平台的安全核心，基于JWT令牌机制提供完整的用户身份验证、权限控制和会话管理服务。

### 核心功能
- **用户管理**: 注册、登录、密码管理、个人信息维护
- **权限控制**: 角色权限管理、API访问保护、资源授权控制  
- **会话管理**: JWT令牌生成验证、自动登出、并发会话控制
- **安全防护**: 密码加密存储、防暴力破解、异常登录检测

### 技术栈
- **后端**: FastAPI + SQLAlchemy + bcrypt + PyJWT
- **数据库**: MySQL 8.0 (users表 + 角色权限)
- **缓存**: Redis (会话状态 + 令牌黑名单)
- **其他**: HTTPS传输 + 环境变量配置

## 快速开始

### API端点
- **基础路径**: `/api/v1/user-auth/`
- **核心接口**: 注册、登录、密码管理、用户信息、权限验证
- **完整规范**: 详见 [api-spec.md](./api-spec.md)

### 数据模型
- **核心表**: `users` (用户账户信息 + role角色字段)
- **关联模式**: 与所有业务模块的用户关联
- **详细结构**: 详见 [overview.md](./overview.md#数据模型)

## 相关链接

### 🔧 专项技术文档
- **[认证机制详解](authentication-details.md)** - JWT实现和密码管理深度技术方案
- **[集成设计方案](auth-integration-design.md)** - 与其他模块的认证集成策略
- **[数据库迁移](user-role-migration.md)** - 用户角色字段添加的迁移方案
- **[版本实现计划](v1-implementation-plan.md)** - V1.0版本的具体开发计划

### 🔗 关联业务模块  
- **用户管理模块** - 用户档案和信息管理
- **购物车模块** - 需要用户认证的购物功能
- **订单管理模块** - 订单权限控制和用户关联
- **商品管理模块** - 管理员权限的商品操作
- [系统架构](../../architecture/overview.md)
- [API设计规范](../../standards/api-standards.md)
- [开发规范](../../standards/code-standards.md)
