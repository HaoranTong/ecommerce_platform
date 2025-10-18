# 库存管理模块 (Inventory Management Module)# 库存管理模块 (Inventory Management Module)



> **版本**: v1.1.0  > **版本**: v1.1.0  

> **状态**: 生产就绪  > **状态**: 生产就绪  

> **架构**: 四层架构 (Router → Service → Repository → Model)  > **架构**: 四层架构 (Router → Service → Repository → Model)  

> **最后更新**: 2025-10-18> **最后更新**: 2025-10-18



------



## 📋 模块概述## 📋 模块概述



库存管理模块是电商平台的核心基础模块，负责商品库存的实时跟踪、预占机制、补货预警和库存同步。库存管理模块是电商平台的核心基础模块，负责商品库存的实时跟踪、预占机制、补货预警和库存同步。



### 核心功能### 核心功能



- ✅ **库存跟踪**: 实时库存监控、多维度库存视图 (可用、预占、冻结、总量)- ✅ **库存跟踪**: 实时库存监控、多维度库存视图 (可用、预占、冻结、总量)

- ✅ **预占机制**: 购物车预占、订单库存锁定、预占超时释放、库存回滚- ✅ **预占机制**: 购物车预占、订单库存锁定、预占超时释放、库存回滚

- ✅ **库存管理**: 管理员库存调整、库存预警设置、低库存监控、变动历史追踪- ✅ **库存管理**: 管理员库存调整、库存预警设置、低库存监控、变动历史追踪

- ✅ **系统集成**: 与购物车、订单、商品模块无缝集成，支持Redis缓存- ✅ **系统集成**: 与购物车、订单、商品模块无缝集成，支持Redis缓存



### 技术特性### 技术特性



- 🏗️ **四层架构**: 关注点清晰分离，易于测试和维护- 🏗️ **四层架构**: 关注点清晰分离，易于测试和维护

- 🔒 **事务安全**: Repository层提供完整的事务管理支持- 🔒 **事务安全**: Repository层提供完整的事务管理支持

- 📊 **性能优化**: 复合索引设计，支持高并发库存操作- 📊 **性能优化**: 复合索引设计，支持高并发库存操作

- 🛡️ **权限控制**: 基于RBAC的细粒度权限管理- 🛡️ **权限控制**: 基于RBAC的细粒度权限管理

- 📝 **完整日志**: 所有库存变更操作均有事务日志记录- 📝 **完整日志**: 所有库存变更操作均有事务日志记录



------



## 🏗️ 架构设计## 🏗️ 架构设计



### 四层架构图### 四层架构图



``````

┌─────────────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────┐

│                    HTTP Layer (路由层)                    ││                    HTTP Layer (路由层)                    │

│  router.py - FastAPI路由、请求验证、响应序列化、权限控制   ││  router.py - FastAPI路由、请求验证、响应序列化、权限控制   │

└─────────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────────┘

                            ↓                            ↓

┌─────────────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────┐

│                  Business Layer (业务层)                  ││                  Business Layer (业务层)                  │

│  service.py - 业务逻辑、状态流转、异常处理、事务协调      ││  service.py - 业务逻辑、状态流转、异常处理、事务协调      │

└─────────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────────┘

                            ↓                            ↓

┌─────────────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────┐

│              Data Access Layer (数据访问层)               ││              Data Access Layer (数据访问层)               │

│  repository.py - CRUD封装、查询构建、缓存策略、事务管理   ││  repository.py - CRUD封装、查询构建、缓存策略、事务管理   │

└─────────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────────┘

                            ↓                            ↓

┌─────────────────────────────────────────────────────────┐┌─────────────────────────────────────────────────────────┐

│                  Model Layer (模型层)                     ││                  Model Layer (模型层)                     │

│  models.py - ORM模型、表结构、关系映射、索引定义          ││  models.py - ORM模型、表结构、关系映射、索引定义          │

└─────────────────────────────────────────────────────────┘└─────────────────────────────────────────────────────────┘

``````



### 文件结构### 文件结构



``````

app/modules/inventory_management/app/modules/inventory_management/

├── __init__.py             # 模块初始化，导出router├── __init__.py             # 模块初始化，导出router

├── models.py               # 数据模型层 (351行)├── models.py               # 数据模型层 (351行)

│   ├── InventoryStock           # 库存主表模型│   ├── InventoryStock           # 库存主表模型

│   ├── InventoryReservation     # 库存预占模型│   ├── InventoryReservation     # 库存预占模型

│   └── InventoryTransaction     # 库存交易记录模型│   └── InventoryTransaction     # 库存交易记录模型

├── schemas.py              # DTO层/请求响应模型 (377行)├── schemas.py              # DTO层/请求响应模型 (377行)

│   ├── StockCreate/Update       # 库存CRUD Schema│   ├── StockCreate/Update       # 库存CRUD Schema

│   ├── ReservationCreate        # 预占创建Schema│   ├── ReservationCreate        # 预占创建Schema

│   └── TransactionResponse      # 交易记录Schema│   └── TransactionResponse      # 交易记录Schema

├── repository.py           # 数据访问层 (609行)├── repository.py           # 数据访问层 (609行)

│   └── InventoryRepository      # 数据访问封装类│   └── InventoryRepository      # 数据访问封装类

│       ├── 基础CRUD (10个方法)│       ├── 基础CRUD (10个方法)

│       ├── 预留操作 (10个方法)│       ├── 预留操作 (10个方法)

│       ├── 事务日志 (6个方法)│       ├── 事务日志 (6个方法)

│       ├── 统计查询 (2个方法)│       ├── 统计查询 (2个方法)

│       └── 事务管理 (5个方法)│       └── 事务管理 (5个方法)

├── service.py              # 业务逻辑层 (657行)├── service.py              # 业务逻辑层 (657行)

│   └── InventoryService         # 业务逻辑封装类│   └── InventoryService         # 业务逻辑封装类

│       ├── 库存管理 (8个方法)│       ├── 库存管理 (8个方法)

│       ├── 预占管理 (6个方法)│       ├── 预占管理 (6个方法)

│       └── 业务查询 (5个方法)│       └── 业务查询 (5个方法)

├── dependencies.py         # 依赖注入 (35行)├── dependencies.py         # 依赖注入 (35行)

│   └── get_inventory_service    # Service依赖注入│   └── get_inventory_service    # Service依赖注入

└── router.py               # HTTP路由层 (284行)└── router.py               # HTTP路由层 (284行)

    └── 11个RESTful API端点    └── 11个RESTful API端点

``````



------



## 🚀 快速开始## 🚀 快速开始



### 1. 在main.py中注册模块### 1. 在main.py中注册模块



```python```python

# app/main.py# app/main.py

from app.modules.inventory_management import router as inventory_routerfrom app.modules.inventory_management import router as inventory_router



# 注册路由# 注册路由

app.include_router(app.include_router(

    inventory_router,    inventory_router,

    prefix="/api/v1",    prefix="/api/v1",

    tags=["库存管理"]    tags=["库存管理"]

))

``````



### 2. 执行数据库迁移### 2. 执行数据库迁移



```bash```bash

# 生成迁移脚本# 生成迁移脚本

alembic revision --autogenerate -m "add inventory management tables"alembic revision --autogenerate -m "add inventory management tables"



# 执行迁移# 执行迁移

alembic upgrade headalembic upgrade head

``````



### 3. 启动应用### 3. 启动应用



```bash```bash

# 开发环境# 开发环境

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



# 访问API文档# 访问API文档

# http://localhost:8000/docs# http://localhost:8000/docs

``````



------



## 📡 API端点列表## 📡 API端点列表



### 库存管理 API### 库存管理 API



| 方法 | 端点 | 说明 | 权限 || 方法 | 端点 | 说明 | 权限 |

|------|------|------|------||------|------|------|------|

| GET | `/api/v1/inventory-management/stocks` | 获取库存列表 | `inventory:read` || GET | `/api/v1/inventory-management/stocks` | 获取库存列表 | `inventory:read` |

| GET | `/api/v1/inventory-management/stocks/{stock_id}` | 获取库存详情 | `inventory:read` || GET | `/api/v1/inventory-management/stocks/{stock_id}` | 获取库存详情 | `inventory:read` |

| POST | `/api/v1/inventory-management/stocks` | 创建库存记录 | `inventory:write` || POST | `/api/v1/inventory-management/stocks` | 创建库存记录 | `inventory:write` |

| PUT | `/api/v1/inventory-management/stocks/{stock_id}` | 更新库存信息 | `inventory:write` || PUT | `/api/v1/inventory-management/stocks/{stock_id}` | 更新库存信息 | `inventory:write` |

| POST | `/api/v1/inventory-management/stocks/{stock_id}/adjust` | 调整库存数量 | `inventory:adjust` || POST | `/api/v1/inventory-management/stocks/{stock_id}/adjust` | 调整库存数量 | `inventory:adjust` |

| DELETE | `/api/v1/inventory-management/stocks/{stock_id}` | 删除库存记录 | `inventory:delete` || DELETE | `/api/v1/inventory-management/stocks/{stock_id}` | 删除库存记录 | `inventory:delete` |



### 预占管理 API### 预占管理 API



| 方法 | 端点 | 说明 | 权限 || 方法 | 端点 | 说明 | 权限 |

|------|------|------|------||------|------|------|------|

| POST | `/api/v1/inventory-management/reservations` | 创建库存预占 | `inventory:reserve` || POST | `/api/v1/inventory-management/reservations` | 创建库存预占 | `inventory:reserve` |

| PUT | `/api/v1/inventory-management/reservations/{reservation_id}/confirm` | 确认预占 | `inventory:reserve` || PUT | `/api/v1/inventory-management/reservations/{reservation_id}/confirm` | 确认预占 | `inventory:reserve` |

| PUT | `/api/v1/inventory-management/reservations/{reservation_id}/release` | 释放预占 | `inventory:reserve` || PUT | `/api/v1/inventory-management/reservations/{reservation_id}/release` | 释放预占 | `inventory:reserve` |

| GET | `/api/v1/inventory-management/reservations` | 获取预占列表 | `inventory:read` || GET | `/api/v1/inventory-management/reservations` | 获取预占列表 | `inventory:read` |

| GET | `/api/v1/inventory-management/reservations/{reservation_id}` | 获取预占详情 | `inventory:read` || GET | `/api/v1/inventory-management/reservations/{reservation_id}` | 获取预占详情 | `inventory:read` |



------



## 💻 使用示例## 💻 使用示例



### 示例1: 查询库存### 示例1: 查询库存



```python```python

from app.modules.inventory_management.service import InventoryServicefrom app.modules.inventory_management.service import InventoryService

from app.core.database import get_dbfrom app.core.database import get_db



# 获取数据库会话# 获取数据库会话

db = next(get_db())db = next(get_db())



# 创建服务实例# 创建服务实例

service = InventoryService(db)service = InventoryService(db)



# 查询指定SKU和仓库的库存# 查询指定SKU和仓库的库存

stock = service.get_stock_by_sku_warehouse(stock = service.get_stock_by_sku_warehouse(

    sku_id=1001,    sku_id=1001,

    warehouse_id=1    warehouse_id=1

))



print(f"总库存: {stock.total_quantity}")print(f"总库存: {stock.total_quantity}")

print(f"可用库存: {stock.available_quantity}")print(f"可用库存: {stock.available_quantity}")

print(f"预占库存: {stock.reserved_quantity}")print(f"预占库存: {stock.reserved_quantity}")

```from app.modules.inventory_management.service import inventory_managementService



### 示例2: 创建库存预占# 在其他模块中使用

service = inventory_managementService(db)

```python`

from app.modules.inventory_management.schemas import ReservationCreate

## 相关文档

# 创建预占请求

reservation_data = ReservationCreate(- [API设计标准](../../../docs/standards/api-standards.md)

    sku_id=1001,- [数据库设计规范](../../../docs/standards/database-standards.md)

    warehouse_id=1,- [模块开发指南](../../../docs/development/module-development-guide.md)

    quantity=5,

    reservation_type="cart",  # 购物车预占## 开发状态

    reference_id="cart_12345",

    user_id=1- ✅ 模块结构创建

)- ✅ 核心功能实现完成

- ✅ 性能优化完成 (同步方法优化)

# 执行预占- ✅ 完整文档支持

reservation = service.create_reservation(reservation_data)- ⏳ 单元测试待完善

print(f"预占单号: {reservation.reservation_no}")

```## 更新日志



### 示例3: 调整库存### 2025-09-16

- 性能优化：移除不必要的async/await，提升同步操作性能

```python- 代码质量提升：确保导入架构合规

# 增加库存- 文档状态更新

service.adjust_stock(

    stock_id=1,### 2025-09-13

    quantity=100,- 创建模块基础结构

    adjustment_type="purchase",  # 采购入库- 初始化模块文件

    reason="供应商到货",- 添加模块README文档

    operator_id=1
)

# 减少库存
service.adjust_stock(
    stock_id=1,
    quantity=-50,
    adjustment_type="damage",  # 损耗出库
    reason="商品损坏",
    operator_id=1
)
```

### 示例4: HTTP API调用

```bash
# 获取库存列表
curl -X GET "http://localhost:8000/api/v1/inventory-management/stocks?sku_id=1001" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 创建库存预占
curl -X POST "http://localhost:8000/api/v1/inventory-management/reservations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku_id": 1001,
    "warehouse_id": 1,
    "quantity": 5,
    "reservation_type": "cart",
    "reference_id": "cart_12345"
  }'
```

---

## 🗄️ 数据模型

### 核心表结构

#### 1. inventory_stocks (库存主表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| sku_id | BIGINT | 商品SKU ID |
| warehouse_id | BIGINT | 仓库ID |
| total_quantity | INT | 总库存数量 |
| available_quantity | INT | 可用库存数量 |
| reserved_quantity | INT | 预占库存数量 |
| frozen_quantity | INT | 冻结库存数量 |
| status | VARCHAR(20) | 状态: active/inactive/suspended |
| low_stock_threshold | INT | 低库存预警阈值 |

**索引**:
- `idx_sku_warehouse`: (sku_id, warehouse_id)
- `uk_sku_warehouse`: UNIQUE(sku_id, warehouse_id)

#### 2. inventory_reservations (库存预占表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| reservation_no | VARCHAR(50) | 预占单号 |
| sku_id | BIGINT | 商品SKU ID |
| warehouse_id | BIGINT | 仓库ID |
| quantity | INT | 预占数量 |
| reservation_type | VARCHAR(20) | 类型: cart/order |
| status | VARCHAR(20) | 状态: pending/confirmed/released/expired |
| reference_id | VARCHAR(100) | 关联业务单据ID |
| expires_at | DATETIME | 过期时间 |

**索引**:
- `idx_reservation_no`: UNIQUE(reservation_no)
- `idx_reference`: (reference_id, reservation_type)

#### 3. inventory_transactions (库存交易记录)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| transaction_no | VARCHAR(50) | 交易流水号 |
| stock_id | BIGINT | 库存ID |
| quantity_change | INT | 数量变化 (正数=入库, 负数=出库) |
| transaction_type | VARCHAR(20) | 类型: purchase/sale/adjust/reserve/release |
| reference_id | VARCHAR(100) | 关联业务单据ID |

---

## 🔗 依赖关系

### 外部依赖

```python
# 核心框架
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# 项目内部依赖
from app.core.database import get_db              # 数据库会话
from app.core.exceptions import (                  # 自定义异常
    InventoryError,
    InsufficientStockError,
    ReservationNotFoundError
)
from app.shared.permissions import RBACPermission  # 权限控制
```

### 被依赖模块

本模块被以下模块依赖:
- **shopping-cart**: 购物车预占库存
- **order-management**: 订单确认和库存扣减
- **product-catalog**: 商品库存状态查询

---

## 🧪 测试

### 运行单元测试

```bash
# 测试Repository层
pytest tests/modules/inventory_management/test_repository.py -v

# 测试Service层
pytest tests/modules/inventory_management/test_service.py -v

# 测试API层
pytest tests/modules/inventory_management/test_router.py -v

# 测试覆盖率
pytest tests/modules/inventory_management/ --cov=app.modules.inventory_management --cov-report=html
```

---

## 📚 相关文档

### 设计文档
- [模块概览](../../../docs/design/modules/inventory-management/overview.md)
- [详细设计](../../../docs/design/modules/inventory-management/design.md)
- [需求规格](../../../docs/design/modules/inventory-management/requirements.md)
- [API规范](../../../docs/design/modules/inventory-management/api-spec.md)
- [实现指南](../../../docs/design/modules/inventory-management/implementation.md)

### 标准规范
- [API设计标准](../../../docs/standards/api-standards.md)
- [数据库设计标准](../../../docs/standards/database-standards.md)
- [代码编写标准](../../../docs/standards/code-standards.md)
- [命名规范标准](../../../docs/standards/naming-conventions-standards.md)

---

**最后更新**: 2025-10-18  
**文档版本**: v1.1.0  
**代码版本**: v1.1.0  
**架构版本**: 四层架构 V2.0
