<!--
文档说明：
- 内容：模块README导航模板，模块入口文档
- 作用：提供快速导航和基本信息，不包含详细内容
- 使用方法：复制此模板，替换模板变量，保持简洁
-->

# 购物车模块 (Shopping Cart)

📋 **状态**: 设计完成，待开发  
👤 **负责人**: 后端开发团队  
🔄 **最后更新**: 2025-09-16  

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

购物车模块是电商平台的核心交易准备模块，提供完整的购物车CRUD操作、实时库存验证和价格计算功能。

### 核心功能
- **购物车管理**: 添加、查看、修改、删除购物车商品
- **库存验证**: 实时验证商品库存，防止超卖问题
- **价格计算**: 动态计算商品小计和购物车总价
- **高性能缓存**: 基于Redis的高性能数据存储
- **数据一致性**: Redis+MySQL双写保证数据可靠性

### 技术栈
- **后端**: FastAPI + SQLAlchemy 2.0 (异步支持)
- **数据库**: MySQL 8.0 (主存储)
- **缓存**: Redis 7.0 (分布式缓存)
- **认证**: JWT Token + FastAPI Security
- **测试**: pytest + pytest-asyncio

## 快速开始

### API端点
- **基础路径**: `/api/v1/cart/`
- **认证方式**: JWT Bearer Token
- **主要接口**: 
  - `POST /items` - 添加商品到购物车
  - `GET /` - 获取购物车内容  
  - `PUT /items/{item_id}` - 更新商品数量
  - `DELETE /items/{item_id}` - 删除商品
  - 详见 [api-spec.md](./api-spec.md)

### 数据模型
- **核心表**: `carts` (购物车主表)、`cart_items` (购物车商品项)
- **关联关系**: 用户1:1购物车、购物车1:N商品项
- **详细结构**: 详见 [overview.md](./overview.md#数据模型)

### 性能指标
- **响应时间**: < 100ms (P95)
- **并发用户**: > 1000 
- **缓存命中率**: > 85%
- **系统可用性**: 99.9%

## 相关链接
- [系统架构](../../architecture/overview.md)
- [API设计规范](../../standards/api-standards.md)
- [开发规范](../../standards/code-standards.md)
