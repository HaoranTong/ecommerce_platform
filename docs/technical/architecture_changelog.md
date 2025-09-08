# 架构变更日志

## 概述

本文档记录电商平台架构的重要变更，遵循文档驱动开发原则，确保所有架构决策可追溯。

## v1.1.0 - 电商核心架构稳定化 (2025-09-08)

### 🎯 目标
完成电商平台核心架构的稳定化，建立可扩展的技术基础。

### 📋 变更摘要

#### 数据模型扩展
- **新增模型**: Category, Order, OrderItem 
- **扩展模型**: User (新增 wx_openid 支持微信登录), Product (完善电商字段)
- **保留模型**: Certificate (向后兼容)
- **关系建立**: 完整的电商业务关系链 User ←→ Order ←→ OrderItem ←→ Product ←→ Category

#### 技术框架升级
- **Pydantic v2 兼容**: 
  - `regex` → `pattern` (Field 验证参数)
  - `orm_mode` → `from_attributes` (Model 配置)
  - 移除 `decimal_places` 约束参数
- **SQLAlchemy 2.x**: 使用现代 SQLAlchemy 语法和最佳实践
- **Alembic 迁移**: 建立干净的迁移链，移除历史垃圾文件

#### API 合约标准化
- **OpenAPI 3.0**: 完整的电商 API 规范定义
- **版本升级**: v1.0.0 → v1.1.0
- **端点覆盖**: 用户管理、商品目录、分类管理、订单处理、支付集成

#### 事件驱动架构
- **事件 Schema**: JSON Schema 定义 User.Created.v1, Product.Created.v1
- **扩展准备**: 为订单状态变更、库存变更等事件预留架构

### 🔧 技术细节

#### 数据库结构变更
```sql
-- 新增表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INT REFERENCES categories(id),
    -- ...其他字段
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INT REFERENCES users(id),
    -- ...其他字段
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    -- ...其他字段
);

-- 扩展现有表
ALTER TABLE users ADD COLUMN wx_openid VARCHAR(50) UNIQUE;
ALTER TABLE products ADD COLUMN category_id INT REFERENCES categories(id);
-- ...其他字段扩展
```

#### 迁移文件管理
- **清理**: 删除所有历史迁移和垃圾文件
- **重建**: 创建 `0001_initial.py` 作为唯一迁移入口
- **验证**: 确保迁移链完整且可重复执行

#### 应用启动验证
- **虚拟环境**: 确保在正确的 Python 虚拟环境中运行
- **依赖检查**: 验证所有 Python 包正确安装
- **服务连接**: 验证 MySQL 和 Redis 容器连接正常
- **API 响应**: 确认 FastAPI 应用正常启动和响应

### 📚 文档更新

#### 新增文档
- `docs/technical/data_models.md`: 完整的数据模型架构文档
- `docs/technical/architecture_changelog.md`: 本变更日志文档

#### 更新文档
- `docs/status/status.md`: 更新项目状态和完成进度
- `docs/technical/index.md`: 更新技术文档索引和版本信息
- `docs/openapi.yaml`: 升级到 v1.1.0，完善 API 规范描述

#### 事件 Schema 更新
- `docs/event-schemas/User.Created.v1.json`: 用户创建事件定义
- `docs/event-schemas/Product.Created.v1.json`: 商品创建事件定义

### ✅ 验证结果

#### 功能验证
- ✅ FastAPI 应用成功启动在 http://127.0.0.1:8000
- ✅ 数据库连接正常，所有表创建成功
- ✅ Alembic 迁移状态正确 (0001_initial)
- ✅ API 端点响应正常
- ✅ 烟雾测试通过

#### 性能验证
- ✅ 应用启动时间 < 5 秒
- ✅ 数据库查询响应正常
- ✅ 无内存泄漏或异常

#### 兼容性验证
- ✅ Python 3.11 兼容
- ✅ Pydantic v2 完全兼容
- ✅ SQLAlchemy 2.x 语法正确
- ✅ Docker 容器环境稳定

### 🚀 后续规划

#### 短期目标 (1-2 周)
- 实现具体业务 API 端点逻辑
- 集成微信支付和支付宝支付
- 添加基础的权限和认证系统
- 实现商品图片上传和管理

#### 中期目标 (1 个月)
- 前端框架集成 (Vue.js/React)
- 完善订单流程和库存管理
- 实现优惠券和促销系统
- 添加数据分析和报表功能

#### 长期目标 (3 个月)
- 多租户架构支持
- 高并发性能优化
- 微服务架构迁移准备
- 生产环境部署和监控

### 🔄 回滚计划

如需回滚到 v1.0.0:
1. 恢复数据库到基础的 3 表结构 (users, products, certificates)
2. 回滚 Pydantic v1 兼容性代码
3. 使用历史备份的迁移文件
4. 更新 OpenAPI 规范到 v1.0.0

### 📊 影响评估

#### 正面影响
- 🎯 建立了完整的电商业务模型基础
- 🛡️ 消除了技术债务和兼容性问题  
- 📈 为快速业务开发奠定了稳固基础
- 📚 建立了完善的文档体系

#### 风险控制
- 🔍 完整的迁移测试确保数据安全
- 🏗️ 渐进式架构变更减少风险
- 📋 详细的文档确保团队协作顺畅
- 🧪 烟雾测试保证基础功能正常

---

## 版本历史

- **v1.1.0** (2025-09-08): 电商核心架构稳定化
- **v1.0.0** (2025-09-07): 基础项目脚手架建立
