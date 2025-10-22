# 会员系统模块

� **状态**: ✅ 已发布  
 **负责人**: 开发团队  
🔄 **最后更新**: 2025-10-22  

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

会员系统模块是电商平台的核心商业化模块，负责会员生命周期管理、积分经济体系和等级权益体系的全面运营。

### 核心功能
- **会员等级管理** - 基于消费金额的自动等级晋升体系
- **积分系统** - 积分获得、使用、过期和冻结的完整管理
- **会员档案** - 个人信息管理和偏好设置
- **权益体系** - 等级权益和个性化服务体系

### 技术栈
- **后端**: FastAPI + SQLAlchemy
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **其他**: JWT认证、Pydantic数据验证

## 快速开始

### API端点
- **基础路径**: `/api/v1/member-system/`
- **主要接口**: 详见 [api-spec.md](./api-spec.md)

### 数据模型
- **核心表**: `members`, `member_levels`, `member_points`
- **关联表**: 详见 [overview.md](./overview.md#数据模型)

## 相关链接
- **项目文档**: [MASTER.md](../../../../MASTER.md)
- **架构标准**: [document-management-standards.md](../../../standards/document-management-standards.md)
- **API标准**: [api-standards.md](../../../standards/api-standards.md)
