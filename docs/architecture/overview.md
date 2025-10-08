<!--
文档说明：
- 内容：系统技术架构总览，包括技术选型、架构决策、系统设计原则
- 使用方法：架构设计和技术选型的指导文档，开发前必读
- 更新方法：重大技术架构变更时更新，需要技术负责人确认
- 引用关系：被其他架构文档和模块设计文档引用
- 更新频率：重大架构变更时
-->

# 技术架构总览

## 架构设计原则

### 核心原则
1. **契约优先 (Contract-First)** - 接口、数据模型、状态机在开发前冻结
2. **适配器抽象 (Adapter Pattern)** - 第三方集成通过适配器接口实现
3. **功能开关 (Feature Flag)** - 每个功能支持独立启用/禁用
4. **配置驱动 (Configuration-Driven)** - 业务规则通过配置文件管理
5. **事件驱动 (Event-Driven)** - 重要操作发布事件，支持异步处理
6. **移动优先 (Mobile-First)** - 优先优化移动端性能和用户体验
7. **社交驱动 (Social-Driven)** - 支持社交分享、拼团等社交电商功能
8. **数据驱动 (Data-Driven)** - 基于用户行为和业务数据优化决策
9. **事务在Service (Transaction in Service)** - Service层负责事务边界管理，Repository层不控制事务

### 架构演进原则
- **前瞻性设计** - 从 Mini-MVP 开始考虑最终产品需求
- **可扩展架构** - 所有模块支持功能扩展，避免大量重构
- **接口稳定性** - API 设计支持向后兼容和版本演进
- **数据模型前瞻** - 数据库设计预留扩展字段

## 技术选型架构原则

### 技术选型决策框架
**决策优先级**: 业务需求适配度 > 团队技术栈熟悉度 > 技术先进性 > 社区活跃度

#### 核心技术选型原则

1. **Python生态优先原则**
   - **理由**: 农产品电商需要复杂的算法支持(推荐算法、供应链优化、质量检测)
   - **决策**: Python在数据科学和AI领域优势明显，FastAPI提供高性能Web框架
   - **边界**: 避免多语言混合架构，降低团队学习成本

2. **异步优先原则** 
   - **理由**: 电商平台高并发场景(秒杀、库存同步、支付回调)
   - **决策**: FastAPI + SQLAlchemy 2.0 异步栈，Redis异步客户端
   - **边界**: 所有I/O密集操作必须使用async/await模式

3. **云原生兼容原则**
   - **理由**: 农产品季节性流量波动大，需要弹性伸缩能力
   - **决策**: 容器化部署，无状态服务设计，外部存储依赖
   - **边界**: 避免本地文件系统依赖，所有状态外部化

4. **数据一致性优先原则**
   - **理由**: 农产品溯源、库存管理、财务结算要求强一致性
   - **决策**: MySQL ACID事务，关键业务操作事务包装
   - **边界**: 宁可牺牲部分性能，保证数据准确性

#### 技术选型决策记录

| 技术领域 | 选型决策 | 核心原因 | 替代方案分析 |
|---------|---------|---------|-------------|
| **Web框架** | FastAPI | 高性能+类型提示+自动文档 | Django过重，Flask功能不足 |
| **数据库** | MySQL 8.0 | ACID事务+农产品行业广泛使用 | PostgreSQL功能过剩，MongoDB一致性弱 |
| **ORM框架** | SQLAlchemy 2.0 | 异步支持+成熟生态 | Django ORM绑定框架，Peewee功能有限 |
| **缓存引擎** | Redis 7.0 | 高性能+数据结构丰富 | Memcached功能单一，本地缓存无法共享 |
| **消息队列** | Redis Pub/Sub | 轻量级+与缓存复用基础设施 | RabbitMQ/Kafka过重，部署复杂 |

## 系统架构

### 整体架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户层 (UI)    │    │   管理层 (Admin) │    │   第三方集成     │
│ 微信小程序/H5/PC │    │   后台管理系统   │    │ 支付/物流/AI/IoT │
│ 分销商小程序    │    │   供应商后台     │    │ 区块链/短信/OSS  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └─────────┐       ┌─────┴─────┐         ┌───────┘
                   │       │           │         │
         ┌─────────▼───────▼───────────▼─────────▼─────────┐
         │                API 网关层                       │
         │    (路由/认证/限流/监控/日志/社交分享)            │
         └─────────────────┬───────────────────────────────┘
                           │
         ┌─────────────────▼───────────────────────────────┐
         │                核心业务服务层                   │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │用户认证 │ │商品管理 │ │订单管理 │ │支付结算 │ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │购物车   │ │库存管理 │ │批次溯源 │ │会员系统 │ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         └─────────────────┬───────────────────────────────┘
                           │
         ┌─────────────────▼───────────────────────────────┐
         │              支撑业务服务层                     │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │分销商   │ │营销活动 │ │通知服务 │ │客服系统 │ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │社交功能 │ │供应商   │ │风控系统 │ │数据分析 │ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         └─────────────────┬───────────────────────────────┘
                           │
         ┌─────────────────▼───────────────────────────────┐
         │             基础设施服务层                      │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │物流管理 │ │AI推荐   │ │区块链   │ │IoT集成  │ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         └─────────────────┬───────────────────────────────┘
                           │
         ┌─────────────────▼───────────────────────────────┐
         │                数据存储层                       │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │ MySQL   │ │ Redis   │ │文件存储 │ │消息队列 │ │
         │ │(主数据) │ │(缓存)   │ │(OSS)   │ │(RabbitMQ)│ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
         │ │区块链DB │ │向量DB   │ │时序DB   │ │搜索引擎 │ │
         │ │(溯源)   │ │(AI推荐) │ │(IoT)    │ │(ES)     │ │
         │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
         └─────────────────────────────────────────────────┘
```

### 技术选型原则

#### 后端技术栈原则
- **高性能框架**: 选择支持异步处理的现代Web框架
- **关系型数据库**: 选择成熟稳定的关系型数据库确保ACID特性
- **缓存系统**: 选择高性能内存数据库支持多种使用模式
- **ORM框架**: 选择支持异步和类型提示的现代ORM
- **认证机制**: 基于标准JWT和OAuth 2.0协议
- **异步处理**: 支持消息队列的异步任务处理

#### 前端技术栈原则  
- **移动优先**: 优先支持移动端原生开发
- **管理后台**: 选择现代前端框架支持组件化开发
- **API文档**: 基于OpenAPI标准自动生成API文档

> **具体技术选型和版本配置**: 详见 [系统技术栈设计](../design/system/technology-stack.md)

#### 基础设施
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx (反向代理 + 静态文件)
- **应用服务器**: Uvicorn + Gunicorn
- **监控**: Prometheus + Grafana (后期)
- **日志**: 结构化日志 + ELK Stack (后期)

#### 第三方集成
- **支付**: 微信支付 + 支付宝 + 银行卡 + 数字人民币
- **短信**: 腾讯云短信服务
- **对象存储**: 腾讯云 COS / 阿里云 OSS
- **CDN**: 腾讯云 CDN / 阿里云 CDN
- **区块链**: 腾讯云TBaaS / 蚂蚁链 (溯源存证)
- **AI服务**: 腾讯云AI / 百度AI (推荐算法)
- **IoT平台**: 腾讯云IoT / 阿里云IoT (设备数据采集)
- **地图服务**: 腾讯地图 / 高德地图 (物流配送)
- **实名认证**: 腾讯云身份验证 (供应商认证)

## 模块架构

### 服务拆分原则
1. **业务边界清晰** - 按照业务领域进行服务拆分
2. **数据独立** - 每个服务拥有独立的数据存储
3. **接口标准** - 统一的 API 设计和通信规范
4. **故障隔离** - 服务间故障不相互影响

### 核心服务模块（模块化单体架构）
```
app/
├── core/                       # 核心基础设施
│   ├── database.py             # 数据库连接管理
│   ├── redis_client.py         # Redis缓存客户端
│   ├── auth.py                 # 认证中间件
│   └── __init__.py             # 核心组件导出
├── shared/                     # 共享组件
│   ├── models.py               # 共享数据模型
│   └── __init__.py             # 共享组件导出
├── adapters/                   # 第三方适配器
│   ├── payment/                # 支付适配器
│   │   ├── wechat_adapter.py   # 微信支付适配器
│   │   ├── alipay_adapter.py   # 支付宝适配器
│   │   └── config.py           # 支付配置
│   ├── blockchain/             # 区块链适配器（待开发）
│   └── ai/                     # AI服务适配器（待开发）
├── modules/                    # 业务模块（垂直切片）
│   ├── user_auth/              # 用户认证模块
│   │   ├── router.py           # API路由
│   │   ├── service.py          # 业务逻辑
│   │   ├── models.py           # 数据模型
│   │   ├── schemas.py          # 请求/响应模型
│   │   └── dependencies.py     # 模块依赖
│   ├── product_catalog/        # 商品管理模块
│   ├── shopping_cart/          # 购物车模块
│   ├── order_management/       # 订单管理模块
│   ├── payment_service/        # 支付服务模块
│   ├── quality_control/        # 质量控制模块（证书管理）
│   ├── batch_traceability/     # 批次溯源模块（待开发）
│   ├── logistics_management/   # 物流管理模块（待开发）
│   ├── member_system/          # 会员系统模块（待开发）
│   ├── distributor_management/ # 分销商管理模块（待开发）
│   ├── marketing_campaigns/    # 营销活动模块（待开发）
│   ├── social_features/        # 社交功能模块（待开发）
│   ├── inventory_management/   # 库存管理模块（待开发）
│   ├── notification_service/   # 通知服务模块（待开发）
│   ├── supplier_management/    # 供应商管理模块（待开发）
│   ├── recommendation_system/  # 推荐系统模块（待开发）
│   ├── customer_service_system/ # 客服系统模块（待开发）
│   ├── risk_control_system/    # 风控系统模块（待开发）
│   └── data_analytics_platform/ # 数据分析模块（待开发）
└── main.py                     # FastAPI应用入口点
```

### 架构层次说明

#### 🏛️ 模块化单体架构总体说明

项目采用**模块化单体架构**（Modular Monolith），结合**四层分层架构**：

```
┌─────────────────────────────────────────────┐
│   第1层: Router (路由层/表现层)            │  ← API接口定义、请求响应处理
├─────────────────────────────────────────────┤
│   第2层: Service (业务逻辑层)                │  ← 业务规则、流程控制、事务管理
├─────────────────────────────────────────────┤
│   第3层: Repository (数据访问层)            │  ← 数据库操作封装、查询构建
├─────────────────────────────────────────────┤
│   第4层: Model (数据模型层)                  │  ← ORM模型定义、实体关系
└─────────────────────────────────────────────┘
```

**层次详细说明**：

| 层次 | 文件 | 职责 | 依赖方向 |
|------|------|------|----------|
| **Router层** | `router.py` | • API路由定义<br>• 请求验证<br>• 响应格式化<br>• 异常处理 | → Service层 |
| **Service层** | `service.py`<br>`{domain}_service.py` | • 业务逻辑实现<br>• 事务管理<br>• 业务规则验证<br>• 流程编排 | → Repository层 |
| **Repository层** | `repository.py` | • 数据库操作封装<br>• 复杂查询构建<br>• 数据访问抽象<br>• ORM操作 | → Model层 |
| **Model层** | `models.py` | • ORM模型定义<br>• 实体关系映射<br>• 数据库表结构 | 无依赖 |

**分层原则**：
1. ✅ **单向依赖**：上层可以依赖下层，禁止反向依赖
2. ✅ **职责分离**：Router处理HTTP，Service处理业务，Repository处理数据
3. ✅ **易于测试**：每层可独立测试，上层可Mock下层
4. ✅ **便于维护**：修改数据访问不影响业务逻辑

**事务管理原则** ⚠️ 重要：

| 层次 | 事务职责 | 操作 | 原因 |
|------|---------|------|------|
| **Service层** | ✅ 负责事务管理 | `db.commit()`<br>`db.rollback()` | • 业务逻辑决定原子性边界<br>• 编排多个Repository调用<br>• 控制跨表事务一致性 |
| **Repository层** | ❌ 不负责事务 | `db.add()`<br>`db.flush()`<br>`db.refresh()` | • 保持方法无状态可复用<br>• 避免过早提交<br>• 便于Service编排 |

**为什么Service管理事务？**
- 业务原子性由业务层决定（如：创建订单+扣库存必须在同一事务）
- Repository方法需要在不同事务上下文中复用
- 测试隔离性要求Service可控制事务提交时机

#### 🔧 核心基础设施层 (core/)
负责应用程序的基础服务：数据库连接、缓存管理、认证中间件等跨模块的核心功能。

#### 🔄 共享组件层 (shared/)
提供跨模块共享的数据模型和工具函数，避免模块间的重复代码。

#### 🔌 适配器层 (adapters/)
封装第三方服务集成，提供统一的接口，支持可替换的实现策略。

#### 🏢 业务模块层 (modules/) - 四层分层架构

采用**垂直切片架构**，每个模块内部实现**四层分层架构**：

```
app/modules/{module_name}/
├── router.py           # 第1层: API路由定义
├── service.py          # 第2层: 业务逻辑处理
├── repository.py       # 第3层: 数据访问层 (推荐)
├── models.py           # 第4层: 数据模型定义
├── schemas.py          # Pydantic请求/响应模型
├── dependencies.py     # 模块依赖注入
└── __init__.py         # 模块初始化
```

**文件职责详细说明**：

1. **router.py** (第1层 - 表现层)
   - 定义FastAPI路由和端点
   - 处理HTTP请求和响应
   - 调用Service层处理业务
   - 处理异常和错误响应

2. **service.py** (第2层 - 业务逻辑层)
   - 实现核心业务逻辑
   - 管理事务边界
   - 执行业务规则验证
   - 编排多个Repository调用

3. **repository.py** (第3层 - 数据访问层) ⭐ **新增推荐**
   - 封装所有数据库操作
   - 提供标准CRUD接口
   - 实现复杂查询逻辑
   - 隔离ORM具体实现

4. **models.py** (第4层 - 数据模型层)
   - 定义SQLAlchemy ORM模型
   - 映射数据库表结构
   - 定义实体关系

5. **schemas.py** (数据传输对象)
   - 定义API请求/响应模型
   - Pydantic数据验证
   - 文档自动生成

6. **dependencies.py** (依赖注入)
   - 定义权限检查
   - 公共依赖抽取
   - 数据库会话管理

### Repository模式推广计划 🎯

#### 为什么引入Repository模式？

**当前问题**：
- ❌ Service层直接操作ORM，职责混乱
- ❌ 数据访问逻辑分散在多个Service中
- ❌ 难以Mock数据层进行单元测试
- ❌ 更换ORM或数据源成本高

**Repository模式优势**：
- ✅ **职责清晰**：Service专注业务，Repository专注数据
- ✅ **可测试性**：Repository可轻松Mock
- ✅ **可维护性**：数据访问逻辑集中管理
- ✅ **可扩展性**：便于切换数据源或ORM
- ✅ **代码复用**：通用查询方法集中定义

#### Repository模式实施标准

**标准Repository接口**：

```python
class BaseRepository:
    """Repository基类，定义标准CRUD接口
    
    ⚠️ 重要原则：Repository层不负责事务管理
    - Repository只负责数据访问操作（add/flush/refresh）
    - 事务的提交/回滚由Service层控制
    - Repository方法保持无状态，可在不同事务上下文中复用
    """
    
    @staticmethod
    def create(db: Session, entity: Model) -> Model:
        """创建实体（不提交事务）"""
        db.add(entity)
        db.flush()  # 刷新以获取自动生成的ID
        db.refresh(entity)
        return entity
    
    @staticmethod
    def get_by_id(db: Session, entity_id: int) -> Optional[Model]:
        """根据ID查询"""
        return db.query(Model).filter(Model.id == entity_id).first()
    
    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Model]:
        """列表查询（带过滤）"""
        query = db.query(Model)
        # 应用过滤条件
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, entity: Model, data: Dict[str, Any]) -> Model:
        """更新实体（不提交事务）"""
        for key, value in data.items():
            setattr(entity, key, value)
        db.flush()
        db.refresh(entity)
        return entity
    
    @staticmethod
    def soft_delete(db: Session, entity: Model) -> None:
        """软删除（不提交事务）"""
        entity.is_deleted = True
        db.flush()
```

#### 推广实施计划

**已完成模块** (✅ 2个)：
- ✅ `product_catalog` - 已实现完整Repository模式（CategoryRepository, ProductRepository, BrandRepository, SKURepository）
- ✅ `user_auth` - 简单模块，暂不需要Repository层

**计划推广模块** (🎯 17个)：

| 优先级 | 模块名 | 复杂度 | 预计工作量 | 推荐引入Repository | 实施状态 |
|--------|--------|--------|-----------|-------------------|----------|
| **P0** | `order_management` | 高 | 2天 | ✅ 强烈推荐 | 🔜 待实施 |
| **P0** | `inventory_management` | 高 | 2天 | ✅ 强烈推荐 | 🔜 待实施 |
| **P0** | `payment_service` | 高 | 2天 | ✅ 强烈推荐 | 🔜 待实施 |
| **P1** | `member_system` | 中 | 1.5天 | ✅ 推荐 | 📋 计划中 |
| **P1** | `batch_traceability` | 中 | 1.5天 | ✅ 推荐 | 📋 计划中 |
| **P1** | `distributor_management` | 中 | 1.5天 | ✅ 推荐 | 📋 计划中 |
| **P1** | `marketing_campaigns` | 中 | 1.5天 | ✅ 推荐 | 📋 计划中 |
| **P2** | `shopping_cart` | 低 | 0.5天 | 🤔 可选 | ⏸️ 暂缓 |
| **P2** | `quality_control` | 低 | 1天 | 🤔 可选 | ⏸️ 暂缓 |
| **P2** | `logistics_management` | 中 | 1天 | ✅ 推荐 | 📋 计划中 |
| **P2** | `notification_service` | 低 | 0.5天 | ❌ 不必要 | ⏸️ 暂缓 |
| **P2** | `social_features` | 中 | 1天 | 🤔 可选 | 📋 计划中 |
| **P2** | `supplier_management` | 中 | 1天 | ✅ 推荐 | 📋 计划中 |
| **P2** | `recommendation_system` | 中 | 1天 | 🤔 可选 | 📋 计划中 |
| **P2** | `customer_service_system` | 中 | 1天 | 🤔 可选 | 📋 计划中 |
| **P2** | `risk_control_system` | 中 | 1天 | ✅ 推荐 | 📋 计划中 |
| **P2** | `data_analytics_platform` | 高 | 2天 | ✅ 推荐 | 📋 计划中 |

**复杂度评估标准**：
- **高复杂度**：4+个实体，复杂关联关系，多表联合查询 → **强烈推荐Repository**
- **中复杂度**：2-3个实体，中等查询复杂度 → **推荐Repository**
- **低复杂度**：1-2个实体，简单CRUD → **可选Repository**

#### 实施步骤（以order_management为例）

**第1步：创建repository.py文件（数据访问层）**
```python
# app/modules/order_management/repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Order, OrderItem

class OrderRepository:
    """订单数据访问层
    
    ⚠️ 注意：Repository方法不负责事务提交
    所有方法只执行数据访问操作，由Service层控制事务边界
    """
    
    @staticmethod
    def create(db: Session, order: Order) -> Order:
        """创建订单（不提交事务）"""
        db.add(order)
        db.flush()  # 刷新获取ID，但不提交
        db.refresh(order)
        return order
    
    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        """根据ID查询订单"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    # ... 其他方法

class OrderItemRepository:
    @staticmethod
    def create(db: Session, order_item: OrderItem) -> OrderItem:
        """创建订单项（不提交事务）"""
        db.add(order_item)
        db.flush()
        db.refresh(order_item)
        return order_item
```

**第2步：创建service.py，管理事务边界**
```python
# app/modules/order_management/service.py
from .repository import OrderRepository, OrderItemRepository
from ..inventory_management.repository import InventoryRepository

class OrderService:
    """订单业务逻辑层
    
    ✅ 核心职责：
    1. 业务逻辑处理和验证
    2. 事务边界管理（commit/rollback）
    3. 编排多个Repository调用
    4. 异常处理和业务流程控制
    """
    
    @staticmethod
    def create_order(db: Session, order_data: dict, items: List[dict]) -> Order:
        """创建订单（完整业务流程）
        
        事务范围：
        - 创建订单主表
        - 创建订单明细
        - 扣减库存
        以上操作必须在同一事务中，保证原子性
        """
        try:
            # 1. 业务验证
            validate_order_data(order_data)
            
            # 2. 创建订单（调用Repository，不提交）
            order = Order(**order_data)
            order = OrderRepository.create(db, order)
            
            # 3. 创建订单项（调用Repository，不提交）
            for item_data in items:
                item = OrderItem(order_id=order.id, **item_data)
                OrderItemRepository.create(db, item)
                
                # 4. 扣减库存（调用Repository，不提交）
                InventoryRepository.deduct_stock(
                    db, 
                    product_id=item.product_id,
                    quantity=item.quantity
                )
            
            # 5. Service层统一提交事务
            db.commit()
            db.refresh(order)
            return order
            
        except Exception as e:
            # 6. 发生异常时回滚整个事务
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"订单创建失败: {str(e)}"
            )
    
    @staticmethod
    def get_order(db: Session, order_id: int) -> Optional[Order]:
        """查询订单（只读操作，无需事务控制）"""
        return OrderRepository.get_by_id(db, order_id)
```

**第3步：更新单元测试，Mock Repository**
```python
# tests/unit/test_order_service.py
from unittest.mock import Mock
from app.modules.order_management.service import OrderService

def test_create_order():
    # Mock Repository
    mock_repo = Mock()
    mock_repo.create.return_value = expected_order
    
    # 测试Service逻辑
    result = OrderService.create_order(db, order_data)
    assert result == expected_order
```

#### 推广时间表

| 阶段 | 时间 | 目标 | 成果 |
|------|------|------|------|
| **阶段1** | Week 1-2 | P0模块实施 | 3个核心模块完成Repository重构 |
| **阶段2** | Week 3-4 | P1模块实施 | 5个重要模块完成Repository重构 |
| **阶段3** | Week 5-6 | P2模块评估 | 评估并选择性实施 |
| **阶段4** | Week 7-8 | 验收和文档 | 更新测试、文档、培训 |

### 模块化单体架构优势

1. **开发效率高** - 单一代码库，统一部署
2. **业务内聚强** - 按业务域垂直切分，边界清晰
3. **扩展性好** - 模块可独立开发和测试
4. **维护成本低** - 避免微服务的分布式复杂性
5. **性能优越** - 模块间直接调用，无网络开销
6. **分层清晰** - 四层架构，职责明确，易于维护

### 演进路径

模块化单体架构为后续演进提供清晰路径：
- **阶段1**: 当前模块化单体架构 + 四层分层架构
- **阶段2**: Repository模式全面推广（进行中）
- **阶段3**: 按需提取高频模块为独立服务
- **阶段4**: 完整微服务架构（如需要）
```

### DDD微服务边界映射
**当前模块化实现 → 未来微服务边界**:
- `user_routes.py` → `user-service` (用户管理和认证)
- `product_routes.py + category_routes.py` → `product-service` (商品管理和分类)
- `cart_routes.py` → `cart-service` (购物车，基于Redis)
- `order_routes.py` → `order-service` (订单处理和状态管理)
- `payment_routes.py` → `checkout-service` (结算和支付流程)

**农产品电商特色微服务**:
- `batch_routes.py` → `batch-service` (批次管理和溯源)
- `member_routes.py` → `member-service` (会员体系和积分)
- `distributor_routes.py` → `distributor-service` (分销商管理)
- `marketing_routes.py` → `campaign-service` (营销活动管理)
- `social_routes.py` → `social-service` (社交功能)

**支撑服务模块**:
- `inventory-service` - 库存管理和预警
- `notification-service` - 消息通知和推送
- `customer-service` - 客服系统和工单
- `analytics-service` - 数据分析和报表
- `risk-service` - 风控和反欺诈
- `logistics-service` - 物流和配送
- `supplier-service` - 供应商管理

**基础设施服务**:
- `ai-service` - AI推荐和分析
- `trace-service` - 溯源和区块链
- `iot-service` - IoT设备集成
- `ledger-service` - 财务和对账

**技术基础设施模块**:
- `application-core` - FastAPI应用入口和路由注册
- `database-core` - SQLAlchemy连接池和会话管理
- `data-models` - 所有业务实体的ORM模型定义
- `redis-cache` - Redis连接管理和缓存策略
- `database-utils` - 数据库工具脚本和测试辅助
- `recommendation-system` - 商品推荐算法和实时推荐

### 数据架构
- **主数据库**: MySQL - 事务性数据存储
- **缓存层**: Redis - 会话、购物车、热点数据、分布式锁
- **文件存储**: OSS - 图片、文档等静态文件
- **搜索引擎**: Elasticsearch - 商品搜索、用户行为分析
- **区块链存储**: 区块链节点 - 溯源数据存证
- **向量数据库**: Pinecone/Milvus - AI推荐算法
- **时序数据库**: InfluxDB - IoT设备数据、监控数据
- **消息队列**: RabbitMQ - 异步任务、事件驱动

## 安全架构

### 认证与授权
- **用户认证**: JWT Token + 微信登录
- **API安全**: Token 验证 + Rate Limiting
- **权限控制**: RBAC 基于角色的访问控制
- **数据加密**: HTTPS + 数据库字段加密

### 数据安全
- **传输安全**: TLS 1.3 加密传输
- **存储安全**: 敏感数据加密存储
- **访问控制**: 最小权限原则
- **审计日志**: 完整的操作审计追踪

## 性能架构

### 缓存策略
```
L1: 应用内存缓存 (本地缓存)
L2: Redis 分布式缓存 (热点数据)
L3: CDN 边缘缓存 (静态资源)
```

### 数据库优化
- **读写分离**: 主库写入，从库读取
- **连接池**: 数据库连接池管理
- **索引优化**: 基于查询模式的索引设计
- **分库分表**: 基于业务的水平拆分 (后期)

### 接口优化
- **异步处理**: 耗时操作异步执行
- **批量操作**: 减少网络请求次数
- **数据压缩**: 响应数据压缩传输
- **CDN加速**: 静态资源 CDN 分发

## 部署架构

### 环境划分
- **开发环境**: 本地 Docker Compose
- **测试环境**: 云服务器 + CI/CD
- **生产环境**: 云服务器集群 + 负载均衡

### 容器化部署
```yaml
services:
  - api-server     # FastAPI 应用服务
  - mysql          # MySQL 数据库
  - redis          # Redis 缓存
  - nginx          # 反向代理
  - monitor        # 监控服务
```

### CI/CD 流程
```
代码提交 → 自动测试 → 构建镜像 → 自动部署 → 健康检查
```

## 监控与运维

### 监控体系
- **应用监控**: 性能指标、错误率、响应时间
- **基础设施监控**: CPU、内存、磁盘、网络
- **业务监控**: 关键业务指标实时监控
- **日志监控**: 结构化日志收集和分析

### 告警机制
- **阈值告警**: 基于指标阈值的自动告警
- **异常检测**: 基于机器学习的异常检测
- **通知渠道**: 短信、邮件、企业微信
- **值班机制**: 7x24 小时值班响应

## 扩展规划

### 水平扩展
- **无状态设计**: 应用服务无状态，支持水平扩展
- **负载均衡**: 基于轮询和权重的负载分发
- **自动扩缩容**: 基于负载的自动扩缩容
- **容灾备份**: 多可用区部署和容灾切换

### 功能扩展
- **微服务化**: 逐步拆分为独立的微服务
- **API网关**: 统一的 API 网关和服务治理
- **服务网格**: 服务间通信和治理 (后期)
- **容器编排**: Kubernetes 集群管理 (后期)
