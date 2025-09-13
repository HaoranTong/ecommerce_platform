<!--
文档说明：
- 内容：数据模型设计的架构原则和业务层面的设计标准
- 使用方法：数据库架构设计时遵循的原则，确保数据模型一致性
- 更新方法：数据设计原则变更时更新，需要架构师确认
- 引用关系：被各模块的design.md文档引用，被standards/database-standards.md引用
- 技术实施：具体的命名规范和编码标准参见 [数据库设计规范](../standards/database-standards.md)
- 更新频率：架构设计原则变化时
-->

# 数据模型架构设计

## 架构引用说明

本文档定义数据模型的**架构原则**和**业务设计标准**。
具体的技术实施规范（命名约定、ORM编写、SQL规范等）请参见：
- [数据库设计规范](../standards/database-standards.md) - 技术实施标准
- [数据模型模块](../modules/data-models/overview.md) - 技术基础设施实现

## ORM基础架构设计

### 统一Base类架构
- **设计原则**: 全系统使用统一的SQLAlchemy Base类
- **实现位置**: `app/core/database.py` 提供唯一的Base类定义
- **使用规范**: 所有业务模块必须从技术基础设施层导入Base类
- **禁止行为**: 任何模块不得重复定义declarative_base()

### 模块化数据模型架构
```
技术基础设施层 (app/core/)
├── database.py              # 统一Base类、Engine、Session配置
└── 为所有业务模块提供ORM基础

业务模块层 (app/modules/)
├── user_auth/models.py      # 用户认证数据模型
├── product_catalog/models.py # 商品管理数据模型
├── order_management/models.py # 订单管理数据模型
└── 各模块独立定义业务数据模型

共享组件层 (app/shared/)
├── mixins.py                # 通用字段混入 (TimestampMixin等)
└── 跨模块共享的数据组件
```

### 数据关系架构原则

#### 外键约束策略
- **级联删除策略**: 根据业务重要性选择 `CASCADE` 或 `SET NULL`
- **核心业务数据**: 使用 `SET NULL` 保护数据完整性
- **从属关系数据**: 使用 `CASCADE` 保持数据一致性
- **日志审计数据**: 禁用级联删除，保证追溯性

#### 跨模块关系设计
- **模块间外键**: 通过明确的业务契约定义跨模块关系
- **循环依赖处理**: 使用字符串引用避免Python导入循环
- **关系维护**: 优先在"多"的一方维护外键关系

## 业务数据模型设计原则

### 核心设计原则
1. **业务导向** - 数据模型设计以业务需求为核心，支持电商平台完整业务流程
2. **模块化** - 每个业务模块独立管理自己的数据模型，减少模块间耦合
3. **可扩展性** - 预留扩展字段和关系，支持业务功能迭代
4. **数据一致性** - 通过外键约束和事务控制保证数据完整性
5. **性能优化** - 基于查询模式合理设计索引和关系

### 业务设计约束
- **审计要求** - 核心业务数据必须包含创建时间、更新时间等审计字段
- **软删除策略** - 重要业务数据采用软删除，保证数据可追溯性
- **状态管理** - 业务实体使用明确的状态字段管理生命周期
- **多租户考虑** - 为未来可能的多租户需求预留租户隔离字段

## 电商业务数据架构

### 核心业务实体关系
```
用户域 (User Domain)
├── 用户认证 (User, Role, Permission)
├── 用户信息 (UserProfile, UserAddress)
└── 会员体系 (MemberLevel, MemberPoints)

商品域 (Product Domain)  
├── 商品管理 (Product, Category, Brand)
├── 库存管理 (Inventory, StockTransaction)
└── 价格管理 (Price, Promotion)

交易域 (Transaction Domain)
├── 购物车 (Cart, CartItem)
├── 订单管理 (Order, OrderItem, OrderStatus)
└── 支付结算 (Payment, PaymentMethod)

农产品特色域 (Agri Domain)
├── 批次溯源 (Batch, TraceRecord)
├── 质量控制 (QualityReport, Certificate)
└── 供应链 (Supplier, LogisticsRecord)
```

### 数据模型分层
- **核心业务层**: 用户、商品、订单等核心业务实体
- **业务规则层**: 会员等级、促销规则、库存策略等业务逻辑数据
- **操作记录层**: 用户行为、操作日志、审计记录等追踪数据
- **配置数据层**: 系统配置、字典数据、参数设置等配置信息

## 技术实施标准引用

具体的数据库实施规范请参见：
- [数据库设计规范](../standards/database-standards.md) - 命名约定、数据类型、SQLAlchemy编写规范
- [数据模型模块文档](../modules/data-models/overview.md) - 技术基础设施实现细节

## 数据迁移和版本管理

### 迁移策略
- **向前兼容** - 新版本数据模型必须兼容旧版本数据
- **分阶段迁移** - 大规模数据变更采用分批迁移策略  
- **回滚机制** - 每个迁移都必须提供可靠的回滚方案
- **测试验证** - 迁移脚本必须在测试环境充分验证

### 版本控制
- **语义化版本** - 数据模型版本遵循语义化版本规范
- **变更日志** - 详细记录每次数据模型变更的原因和影响
- **兼容性矩阵** - 维护数据模型版本与应用版本的兼容性关系

-- 时间字段：_at 后缀
created_at TIMESTAMP    -- 创建时间
updated_at TIMESTAMP    -- 更新时间
deleted_at TIMESTAMP    -- 删除时间（软删除）

-- 金额字段：明确币种
price_cny DECIMAL(10,2) -- 人民币价格
---

**注**: 具体的数据类型标准、字段命名规范、索引设计、SQL编写规范等技术实施细节，请参见 [数据库设计规范](../standards/database-standards.md)。
