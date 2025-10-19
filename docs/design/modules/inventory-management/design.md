---
title: "库存管理模块设计文档"
version: "v1.1.0"
status: "active"
created: "2025-09-15"
updated: "2025-10-18"
owner: "系统架构师"
dependencies:
  - "docs/standards/api-standards.md"
  - "docs/standards/database-standards.md"
  - "docs/standards/architecture-standards.md"
  - "docs/architecture/application-architecture.md"
labels:
  - "inventory-management"
  - "system-design"
  - "repository-pattern"
---

# 库存管理模块设计文档

<!--
文件名：design.md
文件路径：docs/design/modules/inventory-management/design.md
文档类型：系统设计文档 (L2)
模块名称：库存管理模块 (Inventory Management Module)
文档版本：v1.1.0
创建时间：2025-09-15
最后修改：2025-10-18
维护人员：系统架构师
文档状态：正式版本

文档用途：
- 定义库存管理模块的系统架构设计
- 描述数据模型和业务流程设计
- 提供技术选型和性能优化方案

相关文档：
- 需求规格说明书：requirements.md
- 实现指南：implementation.md
- API规范：api-spec.md
-->

## 依赖标准

本文档遵循以下标准规范：

| 标准文档 | 版本 | 应用范围 |
|---------|------|---------|
| [API设计标准](../../standards/api-standards.md) | v1.0 | RESTful API设计、路由命名 |
| [数据库设计标准](../../standards/database-standards.md) | v1.0 | 表结构设计、字段命名、索引设计 |
| [架构设计标准](../../standards/architecture-standards.md) | v1.0 | 四层架构、Repository模式、依赖注入 |
| [应用架构](../../architecture/application-architecture.md) | v1.0 | 模块化单体、模块边界、依赖管理 |
| [数据架构](../../architecture/data-architecture.md) | v1.0 | 数据模型设计、实体关系 |

**架构版本**: V2.0 - 四层架构 (Router → Service → Repository → Model)

## 概述

### 模块定位

库存管理模块是电商平台的核心基础模块，位于**商品域 (Product Domain)**，负责商品库存的实时跟踪、预占管理、补货预警和库存同步。本模块确保库存数据的准确性和一致性，防止超卖现象，支持高并发场景下的库存操作。

### 核心职责

1. **库存数据管理**: 维护SKU级别的库存主数据，包括总库存、可用库存、预占库存和冻结库存
2. **库存预占机制**: 为购物车和订单提供库存预占/释放服务，支持超时自动释放
3. **库存变更追踪**: 记录所有库存变更操作的详细日志，提供完整的审计追踪
4. **库存预警服务**: 监控库存水平，提供低库存预警和缺货通知
5. **高并发支持**: 通过乐观锁和缓存策略，支持高并发库存操作

### 架构特点

- **四层架构**: 采用Router → Service → Repository → Model分层设计，关注点清晰分离
- **Repository模式**: 数据访问层完全封装，提升可测试性和可维护性
- **事务安全**: 关键操作使用数据库事务保证ACID特性
- **缓存优化**: Repository层支持Redis缓存，减少数据库压力
- **权限控制**: 基于RBAC的细粒度权限管理

### 设计原则

1. **单一职责**: 每层只负责特定的关注点
2. **开闭原则**: 对扩展开放，对修改封闭
3. **依赖倒置**: 高层模块不依赖低层模块，都依赖抽象
4. **接口隔离**: Repository提供明确的接口，Service不直接操作数据库
5. **领域驱动**: 业务逻辑集中在Service层，Repository只负责数据访问

## 1. 架构设计

### 1.1 整体架构（四层架构）

```text
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (表现层)                         │
├─────────────────────────────────────────────────────────────────┤
│  • FastAPI Router: 路由定义和请求处理                              │
│  • Pydantic Schemas: 请求/响应数据验证                            │
│  • Dependencies: 依赖注入和权限控制                                │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Business Layer (业务逻辑层)                     │
├─────────────────────────────────────────────────────────────────┤
│  • Service Classes: 业务流程编排                                  │
│  • Business Rules: 库存业务规则验证                                │
│  • Transaction Management: 事务边界管理                           │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Repository Layer (数据操作层) ⭐NEW               │
├─────────────────────────────────────────────────────────────────┤
│  • Data Access Methods: CRUD操作封装                              │
│  • Query Builders: 复杂查询构建                                   │
│  • Cache Strategy: 缓存策略实现                                   │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Model Layer (数据模型层)                      │
├─────────────────────────────────────────────────────────────────┤
│  • SQLAlchemy Models: ORM模型定义                                │
│  • Database Constraints: 数据库约束                               │
│  • Relationships: 实体关系映射                                    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer (基础设施层)                │
├─────────────────────────────────────────────────────────────────┤
│  • MySQL Database: 持久化存储                                    │
│  • Redis Cache: 分布式缓存                                       │
│  • Logging: 日志记录                                            │
│  • Monitoring: 性能监控                                         │
└─────────────────────────────────────────────────────────────────┘
```text

### 1.2 四层架构说明

#### 1.2.1 API层（Presentation Layer）
- **职责**: 处理HTTP请求响应、数据验证、错误处理
- **文件**: `router.py`, `schemas.py`, `dependencies.py`
- **关键特性**:
  - 统一的API路径规范: `/api/v1/inventory-management/*`
  - Pydantic V2数据验证
  - OpenAPI文档自动生成
  - JWT认证和权限控制

#### 1.2.2 业务逻辑层（Business Layer）
- **职责**: 实现核心业务逻辑、事务管理、业务规则验证
- **文件**: `service.py`
- **关键特性**:
  - 库存预留和释放逻辑
  - 库存扣减和回滚逻辑
  - 低库存预警判断
  - 库存一致性检查
  - 业务异常处理

#### 1.2.3 数据操作层（Repository Layer）⭐ 新增
- **职责**: 封装数据访问逻辑、提供统一的数据操作接口
- **文件**: `repository.py`
- **关键特性**:
  - 数据库CRUD操作封装
  - 复杂查询构建（分页、过滤、排序）
  - 缓存读写策略
  - 数据库事务管理
  - SQL查询优化
- **设计优势**:
  - ✅ **分离关注点**: Service层专注业务逻辑，Repository层专注数据访问
  - ✅ **可测试性**: Repository层可以轻松Mock，便于单元测试
  - ✅ **可维护性**: 数据访问逻辑集中管理，易于优化和重构
  - ✅ **可扩展性**: 支持切换不同数据源（MySQL → PostgreSQL）

#### 1.2.4 数据模型层（Model Layer）
- **职责**: 定义数据结构、实体关系、数据库约束
- **文件**: `models.py`
- **关键特性**:
  - SQLAlchemy ORM模型定义
  - 表结构和索引设计
  - 外键关系和级联操作
  - 数据完整性约束

### 1.3 模块交互设计

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Order Module │────▶│ Inventory    │────▶│ Product      │
│              │     │ Management   │     │ Catalog      │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
       │                       │                   │
       ▼                       ▼                   ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Shopping     │     │ Notification │     │ User Auth    │
│ Cart         │     │ Service      │     │ Module       │
└──────────────┘     └──────────────┘     └──────────────┘
```text

## 2. 数据模型设计

### 2.1 核心实体关系图

```text
┌─────────────────────┐       ┌─────────────────────┐
│   InventoryStock    │       │ InventoryReservation│
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │   ┌───│ id (PK)             │
│ sku_id (UK)         │◄──┤   │ sku_id (FK)         │
│ total_quantity      │   │   │ reservation_type    │
│ available_quantity  │   │   │ reference_id        │
│ reserved_quantity   │   │   │ quantity            │
│ warning_threshold   │   │   │ expires_at          │
│ critical_threshold  │   │   │ is_active           │
│ is_active          │   │   │ created_at          │
│ created_at         │   │   │ updated_at          │
│ updated_at         │   │   └─────────────────────┘
└─────────────────────┘   │   
           │               │   ┌─────────────────────┐
           └───────────────┴───│InventoryTransaction │
                               ├─────────────────────┤
                               │ id (PK)             │
                               │ sku_id (FK)         │
                               │ transaction_type    │
                               │ quantity_change     │
                               │ quantity_before     │
                               │ quantity_after      │
                               │ reference_type      │
                               │ reference_id        │
                               │ reason              │
                               │ operator_id         │
                               │ created_at          │
                               └─────────────────────┘
```text

### 2.2 数据模型详细设计

#### 2.2.1 库存主表 (InventoryStock)

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | PK, AUTO_INCREMENT | 主键ID |
| sku_id | Integer | FK, NOT NULL, UK | 关联的SKU ID (引用 skus.id) |
| total_quantity | Integer | NOT NULL, ≥0 | 总库存数量 |
| available_quantity | Integer | Computed | 可用库存 = 总库存 - 预占库存 |
| reserved_quantity | Integer | NOT NULL, ≥0 | 预占库存数量 |
| warning_threshold | Integer | NOT NULL, ≥0 | 低库存预警阈值 |
| critical_threshold | Integer | NOT NULL, ≥0 | 紧急库存阈值 |
| is_active | Boolean | NOT NULL, DEFAULT TRUE | 是否启用库存管理 |
| created_at | DateTime | NOT NULL | 创建时间 |
| updated_at | DateTime | NOT NULL | 更新时间 |

**约束条件**:
- `available_quantity = total_quantity - reserved_quantity`
- `critical_threshold <= warning_threshold`
- `reserved_quantity <= total_quantity`

#### 2.2.2 库存预占表 (InventoryReservation)

**设计说明**:
- `sku_id`外键指向`inventory_stocks.sku_id`而非主键`id`，原因：
  1. 业务语义明确：直接关联到SKU维度，而非库存记录维度
  2. `inventory_stocks.sku_id`有UNIQUE约束，确保1:1关系
  3. 与业务查询逻辑对齐，避免额外JOIN操作

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | PK, AUTO_INCREMENT | 主键ID |
| sku_id | Integer | FK, NOT NULL | 关联的SKU ID (引用 inventory_stocks.sku_id) |
| reservation_type | Enum | NOT NULL | 预占类型 (cart/order) |
| reference_id | String(100) | NOT NULL | 关联业务ID |
| quantity | Integer | NOT NULL, >0 | 预占数量 |
| expires_at | DateTime | NOT NULL | 过期时间 |
| is_active | Boolean | NOT NULL, DEFAULT TRUE | 是否有效 |
| created_at | DateTime | NOT NULL | 创建时间 |
| updated_at | DateTime | NOT NULL | 更新时间 |

**索引设计**:
- `idx_reservation_sku_id`: (sku_id)
- `idx_reservation_reference`: (reference_id)
- `idx_reservation_expires`: (expires_at)
- `idx_reservation_active`: (is_active)

#### 2.2.3 库存事务表 (InventoryTransaction)

**设计说明**:
- `sku_id`外键设计同`InventoryReservation`，指向`inventory_stocks.sku_id`
- 目的：建立清晰的业务语义关系和优化查询性能

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | PK, AUTO_INCREMENT | 主键ID |
| sku_id | Integer | FK, NOT NULL | 关联的SKU ID (引用 inventory_stocks.sku_id) |
| transaction_type | Enum | NOT NULL | 事务类型 |
| quantity_change | Integer | NOT NULL | 数量变化 |
| quantity_before | Integer | NOT NULL | 变更前数量 |
| quantity_after | Integer | NOT NULL | 变更后数量 |
| reference_type | String(50) | | 关联业务类型 |
| reference_id | String(100) | | 关联业务ID |
| reason | String(500) | | 变更原因 |
| operator_id | Integer | | 操作人ID |
| created_at | DateTime | NOT NULL | 创建时间 |

**索引设计**:
- `idx_transaction_sku_id`: (sku_id)
- `idx_transaction_type`: (transaction_type)
- `idx_transaction_created`: (created_at)
- `idx_transaction_reference`: (reference_type, reference_id)

### 2.3 枚举类型定义

#### 2.3.1 事务类型 (TransactionType)
```python
class TransactionType(enum.Enum):
    RESERVE = "reserve"      # 预占
    RELEASE = "release"      # 释放预占
    DEDUCT = "deduct"        # 扣减（实际出库）  
    ADJUST = "adjust"        # 手动调整
    RESTOCK = "restock"      # 入库
```text

#### 2.3.2 预占类型 (ReservationType)
```python
class ReservationType(enum.Enum):
    CART = "cart"            # 购物车预占
    ORDER = "order"          # 订单预占
```python

## 3. 业务流程设计

### 3.1 库存预占流程（四层架构）

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant Router as Router层
    participant Service as Service层
    participant Repo as Repository层
    participant DB as 数据库
    participant Cache as Redis缓存

    Client->>Router: POST /inventory-management/reserve
    Router->>Router: 数据验证(Pydantic)
    Router->>Service: reserve_inventory(items)
    
    Service->>Service: 业务规则验证
    Service->>Repo: get_inventory_by_sku(sku_id)
    Repo->>Cache: 查询缓存
    alt 缓存命中
        Cache-->>Repo: 返回缓存数据
    else 缓存未命中
        Repo->>DB: SELECT * FROM inventory_stock
        DB-->>Repo: 返回库存数据
        Repo->>Cache: 写入缓存
    end
    Repo-->>Service: 返回库存对象
    
    Service->>Service: 检查库存充足性
    
    alt 库存充足
        Service->>Repo: begin_transaction()
        Service->>Repo: update_inventory(sku_id, quantity)
        Repo->>DB: UPDATE inventory_stock
        Service->>Repo: create_reservation(data)
        Repo->>DB: INSERT INTO inventory_reservation
        Service->>Repo: create_transaction_log(data)
        Repo->>DB: INSERT INTO inventory_transaction
        Service->>Repo: commit_transaction()
        Service->>Repo: invalidate_cache(sku_id)
        Repo->>Cache: DELETE cache_key
        Service-->>Router: 返回预占结果
        Router-->>Client: 200 OK + ReservationResponse
    else 库存不足
        Service-->>Router: 抛出InsufficientInventoryError
        Router-->>Client: 400 Bad Request + 错误详情
    end
```text

### 3.2 库存扣减流程（四层架构）

```mermaid
sequenceDiagram
    participant Order as 订单服务
    participant Router as Router层
    participant Service as Service层
    participant Repo as Repository层
    participant DB as 数据库

    Order->>Router: POST /inventory-management/deduct
    Router->>Service: deduct_inventory(items)
    
    Service->>Repo: get_reservations_by_ids(reservation_ids)
    Repo->>DB: SELECT * FROM inventory_reservation
    DB-->>Repo: 返回预占记录
    Repo-->>Service: 返回预占对象列表
    
    Service->>Repo: get_inventories_for_update(sku_ids)
    Repo->>DB: SELECT FOR UPDATE FROM inventory_stock
    DB-->>Repo: 加锁的库存记录
    Repo-->>Service: 返回库存对象列表
    
    Service->>Service: 验证预占有效性
    
    Service->>Repo: begin_transaction()
    
    loop 每个SKU
        Service->>Repo: deduct_inventory_quantity(sku_id, qty)
        Repo->>DB: UPDATE inventory_stock SET total_quantity=...
        Service->>Repo: invalidate_reservation(reservation_id)
        Repo->>DB: UPDATE inventory_reservation SET is_active=false
        Service->>Repo: create_transaction_log(type='deduct', ...)
        Repo->>DB: INSERT INTO inventory_transaction
    end
    
    Service->>Repo: commit_transaction()
    Service->>Repo: invalidate_cache(sku_ids)
    
    Service-->>Router: 返回扣减结果
    Router-->>Order: 200 OK + DeductResponse
```text

### 3.3 预占自动释放流程

```mermaid
sequenceDiagram
    participant Scheduler as 定时任务
    participant Service as 库存服务
    participant DB as 数据库
    participant Cache as 缓存

    Scheduler->>Service: 扫描过期预占
    Service->>DB: 查询过期预占记录
    
    loop 每个过期预占
        Service->>DB: 开始事务
        Service->>DB: 释放预占库存
        Service->>DB: 标记预占无效
        Service->>DB: 记录释放事务
        Service->>DB: 提交事务
        Service->>Cache: 更新缓存
    end
    
    Service-->>Scheduler: 完成清理任务
```text

## 4. 核心算法设计

### 4.1 库存并发控制算法

```python
# 悲观锁实现
async def reserve_inventory_with_lock(sku_id: str, quantity: int):
    async with database.transaction():
        # 使用 SELECT FOR UPDATE 加行锁
        inventory = await db.query(InventoryStock).filter(
            InventoryStock.sku_id == sku_id
        ).with_for_update().first()
        
        if inventory.available_quantity >= quantity:
            inventory.reserved_quantity += quantity
            # 创建预占记录
            reservation = InventoryReservation(...)
            db.add(reservation)
            return True
        else:
            raise InsufficientInventoryError()
```text

### 4.2 批量操作优化算法

```python
async def batch_reserve_inventory(items: List[Dict]):
    # 按 SKU 分组，避免重复查询
    sku_quantities = defaultdict(int)
    for item in items:
        sku_quantities[item['sku_id']] += item['quantity']
    
    # 批量查询库存
    inventories = await db.query(InventoryStock).filter(
        InventoryStock.sku_id.in_(sku_quantities.keys())
    ).with_for_update().all()
    
    # 验证库存充足性
    inventory_map = {inv.sku_id: inv for inv in inventories}
    for sku_id, total_quantity in sku_quantities.items():
        if inventory_map[sku_id].available_quantity < total_quantity:
            raise InsufficientInventoryError(sku_id)
    
    # 批量更新库存
    for sku_id, quantity in sku_quantities.items():
        inventory_map[sku_id].reserved_quantity += quantity
```text

### 4.3 缓存一致性算法

```python
class InventoryCacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 300  # 5分钟
    
    async def get_inventory(self, sku_id: str):
        # 尝试从缓存获取
        cache_key = f"inventory:{sku_id}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # 缓存未命中，查询数据库
        inventory = await self._query_from_db(sku_id)
        if inventory:
            await self.redis.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(inventory)
            )
        return inventory
    
    async def invalidate_cache(self, sku_id: str):
        """库存更新后清除缓存"""
        cache_key = f"inventory:{sku_id}"
        await self.redis.delete(cache_key)
```python

## 5. Repository层详细设计 ⭐

### 5.1 Repository层职责

Repository层作为数据访问抽象层，负责：
- **数据访问封装**: 封装所有数据库操作，提供统一的数据访问接口
- **查询构建**: 构建复杂的数据库查询，支持分页、过滤、排序
- **缓存管理**: 实现缓存读写策略，提高查询性能
- **事务管理**: 管理数据库事务边界，确保数据一致性
- **SQL优化**: 优化SQL语句，使用适当的索引和查询策略

### 5.2 Repository接口设计

```python
# repository.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from datetime import datetime

class InventoryRepository:
    """库存管理数据访问层"""
    
    def __init__(self, db: Session):
        """
        初始化Repository
        
        Args:
            db: SQLAlchemy数据库会话
        """
        self.db = db
    
    # ============ 库存主表操作 ============
    
    def get_inventory_by_sku(self, sku_id: int) -> Optional[InventoryStock]:
        """根据SKU ID获取库存记录"""
        
    def get_inventories_by_sku_ids(self, sku_ids: List[int]) -> List[InventoryStock]:
        """批量获取库存记录"""
        
    def get_inventory_for_update(self, sku_id: int) -> Optional[InventoryStock]:
        """获取库存记录并加悲观锁（SELECT FOR UPDATE）"""
        
    def create_inventory(self, inventory_data: Dict[str, Any]) -> InventoryStock:
        """创建新的库存记录"""
        
    def update_inventory_quantity(
        self, 
        sku_id: int, 
        total_change: int = 0,
        reserved_change: int = 0
    ) -> bool:
        """更新库存数量"""
        
    def deactivate_inventory(self, sku_id: int) -> bool:
        """停用库存管理"""
    
    # ============ 库存预占操作 ============
    
    def create_reservation(self, reservation_data: Dict[str, Any]) -> InventoryReservation:
        """创建库存预占记录"""
        
    def get_reservation_by_id(self, reservation_id: int) -> Optional[InventoryReservation]:
        """根据ID获取预占记录"""
        
    def get_active_reservations_by_sku(self, sku_id: int) -> List[InventoryReservation]:
        """获取SKU的所有有效预占"""
        
    def get_expired_reservations(self, before: datetime) -> List[InventoryReservation]:
        """获取过期的预占记录"""
        
    def invalidate_reservation(self, reservation_id: int) -> bool:
        """标记预占失效"""
        
    def invalidate_reservations_batch(self, reservation_ids: List[int]) -> int:
        """批量标记预占失效"""
    
    # ============ 库存事务日志操作 ============
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> InventoryTransaction:
        """创建库存变动日志"""
        
    def get_transactions_by_sku(
        self, 
        sku_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryTransaction]:
        """获取SKU的变动历史"""
        
    def get_transactions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        transaction_type: Optional[str] = None
    ) -> List[InventoryTransaction]:
        """按日期范围查询事务记录"""
    
    # ============ 统计查询操作 ============
    
    def get_low_stock_items(self, threshold: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取低库存商品列表"""
        
    def get_inventory_statistics(self, sku_ids: List[int]) -> Dict[str, Any]:
        """获取库存统计信息"""
    
    # ============ 事务管理 ============
    
    def begin_transaction(self):
        """开始数据库事务"""
        
    def commit_transaction(self):
        """提交事务"""
        
    def rollback_transaction(self):
        """回滚事务"""
        
    def flush(self):
        """刷新会话（不提交）"""
```python

### 5.3 Service与Repository交互

```python
# service.py

class InventoryService:
    """库存管理业务逻辑层"""
    
    def __init__(self, db: Session):
        self.repository = InventoryRepository(db)
    
    async def reserve_inventory(self, items: List[ReservationItem]) -> ReservationResponse:
        """
        库存预占业务逻辑
        
        Service层职责：
        - 业务规则验证
        - 流程编排
        - 异常处理
        
        Repository层职责：
        - 数据查询
        - 数据更新
        - 事务管理
        """
        try:
            # 1. 查询库存（通过Repository）
            sku_ids = [item.sku_id for item in items]
            inventories = self.repository.get_inventories_by_sku_ids(sku_ids)
            
            # 2. 业务规则验证（Service层职责）
            self._validate_inventory_availability(items, inventories)
            
            # 3. 开始事务（通过Repository）
            self.repository.begin_transaction()
            
            # 4. 更新库存（通过Repository）
            for item in items:
                self.repository.update_inventory_quantity(
                    sku_id=item.sku_id,
                    reserved_change=item.quantity
                )
                
                # 5. 创建预占记录（通过Repository）
                self.repository.create_reservation({
                    'sku_id': item.sku_id,
                    'quantity': item.quantity,
                    'reservation_type': 'cart',
                    'reference_id': item.cart_id,
                    'expires_at': datetime.now() + timedelta(minutes=30)
                })
                
                # 6. 记录事务日志（通过Repository）
                self.repository.create_transaction({
                    'sku_id': item.sku_id,
                    'transaction_type': 'reserve',
                    'quantity_change': item.quantity,
                    ...
                })
            
            # 7. 提交事务（通过Repository）
            self.repository.commit_transaction()
            
            return ReservationResponse(success=True)
            
        except Exception as e:
            # 8. 异常回滚（通过Repository）
            self.repository.rollback_transaction()
            raise
```text

### 5.4 Repository层优势

| 优势 | 说明 | 示例 |
|------|------|------|
| **关注点分离** | Service专注业务逻辑，Repository专注数据访问 | Service不包含SQL语句 |
| **可测试性** | Repository可以Mock，便于单元测试 | 测试Service时Mock Repository |
| **可维护性** | 数据访问逻辑集中，易于优化 | 统一修改查询策略 |
| **可扩展性** | 支持切换数据源 | MySQL → PostgreSQL |
| **性能优化** | 统一的缓存和查询优化策略 | Repository层统一缓存 |

## 6. 性能优化设计

### 6.1 数据库优化

#### 5.1.1 索引策略
```sql
-- 库存主表核心索引
CREATE INDEX idx_inventory_sku_id ON inventory_stock(sku_id);
CREATE INDEX idx_inventory_active ON inventory_stock(is_active);
CREATE INDEX idx_inventory_low_stock ON inventory_stock(available_quantity) 
  WHERE available_quantity <= warning_threshold;

-- 预占表查询优化索引  
CREATE INDEX idx_reservation_sku_active ON inventory_reservation(sku_id, is_active);
CREATE INDEX idx_reservation_expires ON inventory_reservation(expires_at) 
  WHERE is_active = true;

-- 事务表历史查询索引
CREATE INDEX idx_transaction_sku_created ON inventory_transaction(sku_id, created_at);
CREATE INDEX idx_transaction_type_created ON inventory_transaction(transaction_type, created_at);
```text

#### 5.1.2 分区策略
```sql
-- 事务表按月分区
CREATE TABLE inventory_transaction (
    ...
) PARTITION BY RANGE (created_at);

-- 创建月度分区
CREATE TABLE inventory_transaction_2025_09 PARTITION OF inventory_transaction
  FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
```sql

### 5.2 缓存策略

#### 5.2.1 多层缓存架构
```text
┌─────────────────┐
│ Application     │ ← 应用层缓存 (内存)
│ Level Cache     │
├─────────────────┤
│ Redis Cache     │ ← 分布式缓存 (Redis)
│ Distributed     │
├─────────────────┤
│ Database        │ ← 数据持久层 (PostgreSQL)
│ Persistent      │
└─────────────────┘
```sql

#### 5.2.2 缓存更新策略
- **Write-Through**: 写入时同时更新缓存和数据库
- **Cache-Aside**: 读取时检查缓存，未命中时查询数据库
- **TTL策略**: 设置合理的过期时间，避免数据过期
- **主动失效**: 数据变更时主动清除相关缓存

### 5.3 并发控制优化

#### 5.3.1 锁粒度优化
```python
# 行级锁：只锁定相关SKU记录
SELECT * FROM inventory_stock 
WHERE sku_id = ? FOR UPDATE;

# 避免表级锁：使用批量操作时按SKU排序，避免死锁
ORDER BY sku_id ASC FOR UPDATE;
```text

#### 5.3.2 事务隔离级别
- **读已提交**: 普通查询操作使用READ COMMITTED
- **可重复读**: 涉及库存变更的事务使用REPEATABLE READ
- **串行化**: 关键业务场景使用SERIALIZABLE

## 6. 错误处理设计

### 6.1 异常类型定义

```python
class InventoryException(BaseException):
    """库存管理基础异常"""
    pass

class InsufficientInventoryError(InventoryException):
    """库存不足异常"""
    def __init__(self, sku_id: str, requested: int, available: int):
        self.sku_id = sku_id
        self.requested = requested
        self.available = available
        super().__init__(f"SKU {sku_id} 库存不足，需要: {requested}, 可用: {available}")

class InventoryNotFoundError(InventoryException):
    """库存记录不存在异常"""
    pass

class ReservationExpiredError(InventoryException):
    """预占已过期异常"""
    pass

class InvalidOperationError(InventoryException):
    """无效操作异常"""
    pass
```python

### 6.2 错误码规范

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|--------|------------|------|----------|
| INV_001 | 404 | SKU库存记录不存在 | 检查SKU ID有效性 |
| INV_002 | 400 | 库存数量不足 | 减少请求数量或等待补货 |
| INV_003 | 400 | 预占已过期 | 重新发起预占请求 |
| INV_004 | 409 | 并发冲突 | 重试操作 |
| INV_005 | 422 | 参数验证失败 | 检查请求参数格式 |
| INV_006 | 500 | 数据库操作失败 | 联系系统管理员 |

### 6.3 重试机制设计

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
async def reserve_inventory_with_retry(sku_id: str, quantity: int):
    """带重试的库存预占"""
    try:
        return await reserve_inventory(sku_id, quantity)
    except ConcurrencyError:
        # 并发冲突时等待随机时间后重试
        await asyncio.sleep(random.uniform(0.1, 0.5))
        raise
```text

## 7. 监控和观测设计

### 7.1 关键指标监控

#### 7.1.1 业务指标
- **库存准确率**: 库存记录与实际库存的一致性
- **预占成功率**: 预占请求的成功率
- **库存周转率**: 库存变化频率
- **缺货率**: 缺货SKU占比

#### 7.1.2 技术指标  
- **API响应时间**: 各接口的平均响应时间和P99
- **数据库性能**: 查询耗时、连接池使用率
- **缓存命中率**: Redis缓存的命中率
- **事务成功率**: 数据库事务的成功率

### 7.2 告警规则

```yaml
# Prometheus告警规则示例
groups:
  - name: inventory.rules
    rules:
      - alert: HighInventoryAPILatency
        expr: histogram_quantile(0.99, inventory_api_duration_seconds) > 0.5
        for: 5m
        annotations:
          summary: "库存API延迟过高"
          
      - alert: LowInventoryLevels
        expr: inventory_low_stock_count > 100
        for: 10m
        annotations:
          summary: "低库存商品数量过多"
          
      - alert: InventoryDatabaseErrors
        expr: rate(inventory_db_errors_total[5m]) > 0.1
        for: 2m
        annotations:
          summary: "库存数据库错误率过高"
```text

### 7.3 链路追踪

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def reserve_inventory(sku_id: str, quantity: int):
    with tracer.start_as_current_span("reserve_inventory") as span:
        span.set_attribute("sku_id", sku_id)
        span.set_attribute("quantity", quantity)
        
        try:
            # 库存预占逻辑
            result = await _do_reserve(sku_id, quantity)
            span.set_attribute("success", True)
            return result
        except Exception as e:
            span.set_attribute("error", str(e))
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise
```text

## 8. 安全设计

### 8.1 权限控制

#### 8.1.1 RBAC权限模型
```python
class Permission(enum.Enum):
    INVENTORY_READ = "inventory:read"
    INVENTORY_CREATE = "inventory:create"  
    INVENTORY_UPDATE = "inventory:update"
    INVENTORY_DELETE = "inventory:delete"
    INVENTORY_ADMIN = "inventory:admin"

class Role(enum.Enum):
    GUEST = "guest"           # 游客
    USER = "user"            # 普通用户  
    BUSINESS = "business"     # 业务系统
    ADMIN = "admin"          # 管理员

# 角色权限映射
ROLE_PERMISSIONS = {
    Role.GUEST: [Permission.INVENTORY_READ],
    Role.USER: [Permission.INVENTORY_READ],
    Role.BUSINESS: [Permission.INVENTORY_READ, Permission.INVENTORY_UPDATE],
    Role.ADMIN: list(Permission)
}
```text

#### 8.1.2 API权限验证
```python
from functools import wraps
from fastapi import Depends, HTTPException, status

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@router.post("/inventory/adjust")
@require_permission(Permission.INVENTORY_ADMIN)
async def adjust_inventory(...):
    """只有管理员可以手动调整库存"""
    pass
```python

### 8.2 数据保护

#### 8.2.1 敏感数据加密
```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key.encode())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```python

#### 8.2.2 审计日志
```python
class AuditLogger:
    async def log_inventory_operation(
        self,
        operation: str,
        sku_id: str,
        user_id: int,
        old_value: dict,
        new_value: dict,
        ip_address: str
    ):
        audit_log = {
            "timestamp": datetime.now(timezone.utc),
            "operation": operation,
            "sku_id": sku_id,
            "user_id": user_id,
            "changes": {
                "old": old_value,
                "new": new_value
            },
            "ip_address": ip_address,
            "user_agent": request.headers.get("User-Agent")
        }
        
        await self.security_logger.log(audit_log)
```python

---

## 具体标准

### 数据模型标准

1. **表命名规范**
   - 所有表名使用小写蛇形命名: `inventory_stocks`, `inventory_reservations`
   - 表名必须使用复数形式表示集合
   - 中间表使用两个实体名称组合: `table1_table2_relation`

2. **字段命名规范**
   - 主键统一使用 `id` (BIGINT AUTO_INCREMENT)
   - 外键使用 `{entity}_id` 格式: `sku_id`, `warehouse_id`
   - 布尔字段使用 `is_` 前缀: `is_active`, `is_deleted`
   - 时间字段使用 `_at` 后缀: `created_at`, `updated_at`, `expires_at`
   - 数量字段使用 `_quantity` 后缀: `total_quantity`, `available_quantity`

3. **必需字段**
   - 所有表必须包含: `id`, `created_at`, `updated_at`
   - 逻辑删除表必须包含: `is_deleted`, `deleted_at`
   - 有状态实体必须包含: `status`

4. **索引设计**
   - 主键自动索引
   - 外键必须创建索引: `idx_{table}_{field}`
   - 唯一约束必须命名: `uk_{table}_{fields}`
   - 复合索引命名: `idx_{table}_{field1}_{field2}`
   - 查询频繁的字段必须创建索引

5. **数据类型标准**
   - 主键: `BIGINT AUTO_INCREMENT`
   - 外键: `BIGINT`
   - 数量: `INT` (非负使用UNSIGNED)
   - 金额: `DECIMAL(10,2)`
   - 状态: `VARCHAR(20)` (使用枚举值)
   - 短文本: `VARCHAR(N)` (N≤255)
   - 长文本: `TEXT`
   - 时间: `DATETIME` (使用UTC时区)

### API设计标准

1. **路由命名规范**
   - 使用复数名词: `/stocks`, `/reservations`
   - 使用中划线分隔: `/inventory-management`
   - RESTful资源路径: `/stocks/{stock_id}`
   - 动作使用POST + 路径: `/stocks/{stock_id}/adjust`

2. **HTTP方法规范**
   - GET: 查询操作(列表、详情)
   - POST: 创建操作和特殊动作
   - PUT: 全量更新操作
   - PATCH: 部分更新操作
   - DELETE: 删除操作

3. **响应格式标准**
   ```json
   {
     "code": 200,
     "message": "操作成功",
     "data": {...},
     "timestamp": "2025-10-18T12:00:00Z"
   }
   ```

4. **错误响应标准**
   ```json
   {
     "code": 400,
     "message": "库存不足",
     "error_code": "INSUFFICIENT_STOCK",
     "details": {
       "sku_id": 1001,
       "required": 10,
       "available": 5
     }
   }
   ```

5. **分页标准**
   - 查询参数: `page`, `page_size`
   - 默认值: `page=1`, `page_size=20`
   - 最大值: `page_size≤100`
   - 响应包含: `total`, `page`, `page_size`, `items`

### 代码实现标准

1. **文件组织**
   ```
   module/
   ├── __init__.py      # 导出router
   ├── models.py        # 数据模型 (ORM)
   ├── schemas.py       # DTO模型 (Pydantic)
   ├── repository.py    # 数据访问层
   ├── service.py       # 业务逻辑层
   ├── dependencies.py  # 依赖注入
   ├── router.py        # HTTP路由层
   └── README.md        # 模块文档
   ```

2. **层次职责**
   - **Router层**: 只负责HTTP请求处理、参数验证、响应序列化
   - **Service层**: 只负责业务逻辑编排、规则验证、事务协调
   - **Repository层**: 只负责数据访问、查询构建、缓存管理
   - **Model层**: 只负责数据结构定义、关系映射、约束声明

3. **命名约定**
   - 类名: PascalCase (`InventoryService`, `InventoryRepository`)
   - 函数名: snake_case (`get_stock_by_id`, `create_reservation`)
   - 常量: UPPER_SNAKE_CASE (`MAX_QUANTITY`, `DEFAULT_THRESHOLD`)
   - 私有方法: `_method_name`

4. **文档注释**
   - 所有公共类必须有docstring
   - 所有公共方法必须有docstring
   - docstring格式:
     ```python
     """
     简要描述
     
     详细描述
     
     Args:
         param1: 参数说明
         param2: 参数说明
     
     Returns:
         返回值说明
     
     Raises:
         ExceptionType: 异常说明
     """
     ```

5. **类型注解**
   - 所有函数参数必须有类型注解
   - 所有函数返回值必须有类型注解
   - 使用typing模块的泛型: `List`, `Dict`, `Optional`

### 事务管理标准

1. **事务边界**
   - Service层方法是事务边界
   - Repository方法不控制事务
   - 使用contextmanager管理事务: `repository.transaction()`

2. **事务隔离级别**
   - 默认: READ_COMMITTED
   - 库存扣减: REPEATABLE_READ
   - 统计查询: READ_UNCOMMITTED (允许脏读)

3. **事务超时**
   - 默认超时: 30秒
   - 长事务超时: 60秒
   - 超时后自动回滚

### 性能优化标准

1. **查询优化**
   - 使用索引覆盖: SELECT只查询索引字段
   - 避免SELECT *: 只查询需要的字段
   - 批量操作: 使用bulk_insert_mappings, bulk_update_mappings
   - 分页查询: 使用limit/offset或游标分页

2. **缓存策略**
   - 库存数据缓存时间: 5分钟
   - 预占数据不缓存 (实时性要求)
   - 缓存键格式: `inventory:stock:{sku_id}:{warehouse_id}`
   - 缓存更新策略: Write-Through (写穿)

3. **并发控制**
   - 乐观锁: 使用version字段
   - 悲观锁: 使用FOR UPDATE (谨慎使用)
   - 分布式锁: 使用Redis实现

### 错误处理标准

1. **异常层次**
   ```python
   BaseException
   ├── InventoryError (基础异常)
   │   ├── InsufficientStockError (库存不足)
   │   ├── ReservationNotFoundError (预占不存在)
   │   ├── ReservationExpiredError (预占已过期)
   │   └── InvalidOperationError (无效操作)
   ```

2. **异常信息**
   - 必须包含: 错误代码、错误消息、错误详情
   - 不暴露敏感信息 (SQL、堆栈)
   - 提供用户友好的错误消息

3. **错误码规范**
   - 格式: `MODULE_ERROR_TYPE`
   - 示例: `INVENTORY_INSUFFICIENT_STOCK`, `INVENTORY_RESERVATION_NOT_FOUND`

### 安全标准

1. **权限控制**
   - 所有API必须有权限检查
   - 使用RBAC模型
   - 权限格式: `resource:action` (`inventory:read`, `inventory:write`)

2. **输入验证**
   - 使用Pydantic进行数据验证
   - 验证数量范围: quantity > 0
   - 验证状态值: 使用枚举类型

3. **SQL注入防护**
   - 使用ORM参数绑定
   - 禁止字符串拼接SQL
   - 使用SQLAlchemy的text()处理原生SQL

### 测试标准

1. **单元测试**
   - Repository层: Mock数据库
   - Service层: Mock Repository
   - 测试覆盖率: ≥80%

2. **集成测试**
   - 使用测试数据库
   - 测试完整业务流程
   - 测试并发场景

3. **性能测试**
   - 库存查询QPS: ≥1000
   - 库存扣减TPS: ≥500
   - 响应时间P99: ≤100ms

---

**文档版本**: v1.1.0  
**创建日期**: 2025-09-15  
**最后更新**: 2025-10-18  
**责任人**: 系统架构师  
**审核人**: 技术总监
