<!--
文档说明：
- 内容：应用架构设计，包括模块组织、分层架构、接口设计和技术实现
- 使用方法：应用开发和系统设计时的技术指导文档
- 更新方法：应用架构调整或新增模块时更新
- 引用关系：引用business-architecture.md业务架构，被技术实现引用
- 更新频率：应用架构变更时
-->

# 应用架构设计

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-22  
👤 **负责人**: 应用架构师  
🔄 **最后更新**: 2025-09-22  
📋 **版本**: v1.0.0  

## 应用架构概览

### 模块化单体架构
采用模块化单体架构(Modular Monolith)，为未来微服务演进奠定基础：

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI 应用入口层                          │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   用户域    │ │   商品域    │ │   交易域    │ │   营销域    │ │
│ │(2模块完成)   │ │(2模块完成)   │ │(3模块完成)   │ │(4模块规划)   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   农产品域   │ │   平台域    │ │   适配器层   │ │   共享层    │ │
│ │(6模块规划)   │ │(4模块规划)   │ │(第三方集成)  │ │(通用组件)    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      核心基础设施层                              │
│   Database(MySQL) + Cache(Redis) + Queue(Celery) + Auth(JWT)   │
└─────────────────────────────────────────────────────────────────┘
```

## 模块架构组织

### 目录结构设计

```
app/
├── main.py                     # FastAPI应用入口
├── core/                       # 核心基础设施
│   ├── database.py            # 数据库连接管理
│   ├── redis_client.py        # Redis缓存客户端
│   ├── auth.py                # JWT认证中间件
│   └── security_logger.py     # 安全日志记录
├── shared/                     # 共享组件层
│   ├── base_models.py         # 基础数据模型
│   ├── api_schemas.py         # API请求响应模型
│   └── models.py              # 跨模块共享模型
├── adapters/                   # 适配器层
│   └── payment/               # 支付适配器实现
└── modules/                    # 业务模块层
    ├── user_auth/             # 用户认证模块 ✅
    ├── product_catalog/       # 商品管理模块 ✅
    ├── shopping_cart/         # 购物车模块 ✅
    ├── order_management/      # 订单管理模块 ✅
    ├── payment_service/       # 支付服务模块 ✅
    ├── inventory_management/  # 库存管理模块 ✅
    ├── member_system/         # 会员系统模块 ✅
    ├── marketing_campaigns/   # 营销活动模块 ✅
    ├── batch_traceability/    # 批次溯源模块 (规划)
    ├── logistics_management/  # 物流管理模块 (规划)
    ├── quality_control/       # 质量控制模块 (规划)
    ├── distributor_management/ # 分销商管理模块 (规划)
    ├── social_features/       # 社交功能模块 (规划)
    ├── notification_service/  # 通知服务模块 (规划)
    ├── customer_service_system/ # 客服系统模块 (规划)
    ├── supplier_management/   # 供应商管理模块 (规划)
    ├── risk_control_system/   # 风控系统模块 (规划)
    ├── data_analytics_platform/ # 数据分析模块 (规划)
    ├── recommendation_system/ # 推荐系统模块 (规划)
    ├── live_streaming/        # 直播带货模块 (规划)
    ├── mini_program/          # 小程序原生模块 (规划)
    ├── b2b_procurement/       # B2B企业采购模块 (规划)
    ├── ai_customer_service/   # 智能客服模块 (规划)
    ├── agricultural_services/ # 农事服务模块 (规划)
    └── quality_certification/ # 检测认证模块 (规划)
```

### 标准模块结构

每个业务模块遵循统一结构：
```
modules/{module_name}/
├── __init__.py                # 模块初始化
├── router.py                  # FastAPI路由定义
├── service.py                 # 业务逻辑层
├── models.py                  # 数据模型定义
├── schemas.py                 # Pydantic请求响应模型
├── dependencies.py            # 依赖注入配置
└── README.md                  # 模块文档
```

## 分层架构设计

### 五层架构模型

| 层级 | 职责 | 技术选型 | 主要组件 |
|------|------|---------|---------|
| **表现层** | API接口、路由管理 | FastAPI + Pydantic | router.py, schemas.py |
| **业务层** | 业务逻辑、流程控制 | Python业务代码 | service.py, dependencies.py |
| **领域层** | 领域模型、业务规则 | SQLAlchemy ORM | models.py, 业务规则 |
| **基础设施层** | 数据访问、外部集成 | MySQL + Redis + 第三方API | database.py, adapters/ |
| **共享层** | 通用组件、工具类 | 跨模块共享代码 | shared/, core/ |

### 分层依赖规则

```
表现层 (router.py)
    ↓ 只能依赖
业务层 (service.py)
    ↓ 只能依赖
领域层 (models.py)
    ↓ 只能依赖
基础设施层 (database.py, adapters/)
    ↓ 可以依赖
共享层 (shared/, core/)
```

## 模块分类与优先级

### 按开发状态分类

| 状态 | 模块数量 | 模块列表 | 开发阶段 |
|------|---------|---------|---------|
| **✅ 已完成** | 8个 | user_auth, product_catalog, shopping_cart, order_management, payment_service, inventory_management, member_system, marketing_campaigns | 核心MVP |
| **🔄 开发中** | 0个 | - | - |
| **📝 规划中** | 22个 | batch_traceability, logistics_management 等 | 功能扩展期 |

### 按业务优先级分类

| 优先级 | 模块类型 | 开发阶段 | 业务价值 |
|-------|---------|---------|---------|
| **P0-核心** | 用户、商品、交易模块 | 已完成 | 电商基础能力 |
| **P1-特色** | 农产品溯源、质量控制 | 第二期 | 差异化竞争力 |
| **P2-营销** | 分销、社交、直播模块 | 第三期 | 业务增长引擎 |
| **P3-平台** | 数据分析、智能推荐 | 第四期 | 平台化能力 |

## 模块间集成方式

### 依赖注入模式

```python
# 标准依赖注入结构
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_order_service(
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> OrderService:
    return OrderService(db, user_service)
```

### 事件驱动通信

```python
# 模块间事件通信
class OrderCreatedEvent:
    order_id: int
    user_id: int
    total_amount: Decimal

# 事件发布
async def create_order(order_data: OrderCreate):
    order = await order_service.create(order_data)
    await event_publisher.publish(OrderCreatedEvent(
        order_id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount
    ))

# 事件订阅
@event_subscriber.subscribe(OrderCreatedEvent)
async def handle_order_created(event: OrderCreatedEvent):
    # 更新库存、发送通知等
    pass
```

### API标准化

所有模块API遵循统一规范：
```python
# 统一响应格式
class APIResponse[T]:
    success: bool
    data: Optional[T]
    message: str
    error_code: Optional[str]

# 统一错误处理
class BusinessException(Exception):
    error_code: str
    message: str
    status_code: int = 400
```

## 技术实现标准

### 数据模型规范

```python
# 基础模型继承
class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

# 软删除混入
class SoftDeleteMixin:
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False)
```

### 业务服务规范

```python
# 标准服务基类
class BaseService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, data: BaseSchema) -> BaseModel:
        pass
    
    async def get_by_id(self, id: int) -> Optional[BaseModel]:
        pass
    
    async def update(self, id: int, data: BaseSchema) -> BaseModel:
        pass
    
    async def delete(self, id: int) -> bool:
        pass
```

### 路由组织规范

```python
# 标准路由结构
router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

## 微服务演进准备

### 边界识别

基于业务域划分微服务边界：
```
用户域 → user-service
商品域 → product-service  
交易域 → order-service + payment-service
营销域 → marketing-service + social-service
农产品域 → traceability-service + logistics-service
平台域 → platform-service
```

### 数据隔离准备

```python
# 模块数据隔离
class UserModule:
    # 用户域数据表
    tables = ['users', 'roles', 'user_roles', 'member_levels', 'member_points']

class ProductModule:
    # 商品域数据表  
    tables = ['products', 'categories', 'brands', 'skus', 'inventory']
```

### 接口版本化

```python
# API版本管理
@router.get("/v1/users/{user_id}")  # 当前版本
@router.get("/v2/users/{user_id}")  # 新版本

# 向后兼容性
class UserResponseV1(BaseModel):
    id: int
    username: str

class UserResponseV2(UserResponseV1):
    email: Optional[str] = None  # 新增字段
```

## 架构治理原则

### 模块设计原则
1. **单一职责** - 每个模块专注特定业务领域
2. **松耦合** - 模块间通过标准接口交互
3. **高内聚** - 模块内部功能高度相关
4. **可替换** - 模块可独立升级不影响其他模块

### 依赖管理原则  
1. **分层依赖** - 严格按架构分层依赖，禁止逆向依赖
2. **接口依赖** - 依赖抽象而非具体实现
3. **版本兼容** - 接口变更保持向后兼容
4. **循环检测** - 定期检测消除循环依赖

### 质量保证原则
1. **代码规范** - 遵循Python PEP8和项目编码规范
2. **测试覆盖** - 单元测试覆盖率>80%，集成测试完整
3. **文档同步** - 代码变更同步更新文档
4. **性能监控** - 关键接口性能监控和优化

## 相关文档

- [业务架构设计](business-architecture.md) - 30模块业务域架构
- [数据架构设计](data-architecture.md) - 数据模型和存储架构  
- [基础设施架构](infrastructure-architecture.md) - 技术基础设施架构
- [架构演进路线](migration-roadmap.md) - 微服务演进规划