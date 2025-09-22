# 库存管理模块实现文档

<!--
文件名：implementation.md
文件路径：docs/modules/inventory-management/implementation.md
文档类型：技术实现文档
模块名称：库存管理模块 (Inventory Management Module)
文档版本：v1.0.0
创建时间：2025-09-15
最后修改：2025-09-15
维护人员：开发工程师
文档状态：正式版本

文档用途：
- 详细描述库存管理模块的技术实现方案
- 提供代码结构和关键算法说明
- 指导开发团队进行具体实现

相关文档：
- 需求规格说明书：requirements.md
- 系统设计文档：design.md
- API规范：api-spec.md
-->

## 1. 技术栈选择

### 1.1 核心技术栈

| 技术组件 | 版本 | 用途 | 选择理由 |
|----------|------|------|----------|
| **FastAPI** | 0.104+ | Web框架 | 高性能、类型安全、自动API文档 |
| **SQLAlchemy** | 2.0+ | ORM框架 | 成熟的Python ORM，支持异步 |
| **PostgreSQL** | 15+ | 主数据库 | 强一致性、事务支持、JSON支持 |
| **Redis** | 7.0+ | 缓存/队列 | 高性能缓存、分布式锁、消息队列 |
| **Pydantic** | 2.0+ | 数据验证 | 类型验证、序列化、配置管理 |
| **Alembic** | 1.12+ | 数据库迁移 | SQLAlchemy官方迁移工具 |

### 1.2 开发工具链

| 工具 | 版本 | 用途 |
|------|------|------|
| **pytest** | 7.4+ | 测试框架 |
| **pytest-asyncio** | 0.21+ | 异步测试支持 |
| **black** | 23.0+ | 代码格式化 |
| **mypy** | 1.5+ | 静态类型检查 |
| **pre-commit** | 3.0+ | 代码质量检查 |

## 2. 项目结构实现

### 2.1 目录结构

```
app/modules/inventory_management/
├── __init__.py                 # 模块初始化
├── models.py                   # 数据模型定义
├── schemas.py                  # API数据结构
├── service.py                  # 业务逻辑服务
├── router.py                   # API路由定义
├── dependencies.py             # 依赖注入
└── exceptions.py               # 自定义异常

tests/
├── unit/
│   ├── test_models/
│   │   └── test_inventory_models.py
│   └── test_services/
│       └── test_inventory_service.py
├── integration/
│   └── test_api/
│       └── test_inventory_integration.py
└── conftest.py                 # 测试配置
```

### 2.2 模块依赖关系

```python
# 依赖层次结构
Router Layer    ->  Service Layer    ->  Model Layer
    │                    │                   │
    ├── schemas.py       ├── service.py     ├── models.py
    ├── router.py        └── exceptions.py  └── database.py
    └── dependencies.py
```

## 3. 数据模型实现

### 3.1 基础模型设计

```python
# app/modules/inventory_management/models.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime, timezone

from app.shared.base_models import Base

class TransactionType(enum.Enum):
    """库存变动类型"""
    RESERVE = "reserve"      # 预占
    RELEASE = "release"      # 释放预占
    DEDUCT = "deduct"        # 扣减（实际出库）  
    ADJUST = "adjust"        # 手动调整
    RESTOCK = "restock"      # 入库

class ReservationType(enum.Enum):
    """预占类型"""
    CART = "cart"            # 购物车预占
    ORDER = "order"          # 订单预占

class InventoryStock(Base):
    """库存主表 - 基于SKU的库存管理"""
    __tablename__ = "inventory_stock"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String(100), unique=True, nullable=False, index=True)
    total_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    warning_threshold = Column(Integer, nullable=False, default=10)
    critical_threshold = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def available_quantity(self) -> int:
        """计算可用库存"""
        return max(0, self.total_quantity - self.reserved_quantity)
    
    @property
    def is_low_stock(self) -> bool:
        """判断是否低库存"""
        return self.available_quantity <= self.warning_threshold
    
    @property
    def is_critical_stock(self) -> bool:
        """判断是否紧急库存"""
        return self.available_quantity <= self.critical_threshold
    
    @property
    def is_out_of_stock(self) -> bool:
        """判断是否缺货"""
        return self.available_quantity == 0

    def can_reserve(self, quantity: int) -> bool:
        """检查是否可以预占指定数量"""
        return self.available_quantity >= quantity
    
    def reserve_quantity(self, quantity: int) -> bool:
        """预占库存"""
        if self.can_reserve(quantity):
            self.reserved_quantity += quantity
            return True
        return False
    
    def release_quantity(self, quantity: int) -> bool:
        """释放预占库存"""
        if self.reserved_quantity >= quantity:
            self.reserved_quantity -= quantity
            return True
        return False
    
    def deduct_quantity(self, quantity: int, from_reserved: bool = True) -> bool:
        """扣减库存"""
        if from_reserved:
            if self.reserved_quantity >= quantity:
                self.reserved_quantity -= quantity
                self.total_quantity -= quantity
                return True
        else:
            if self.available_quantity >= quantity:
                self.total_quantity -= quantity
                return True
        return False
```

### 3.2 关联模型实现

```python
class InventoryReservation(Base):
    """库存预占表"""
    __tablename__ = "inventory_reservation"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String(100), nullable=False, index=True)
    reservation_type = Column(SqlEnum(ReservationType), nullable=False)
    reference_id = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def is_expired(self) -> bool:
        """检查预占是否已过期"""
        return datetime.now(timezone.utc) > self.expires_at

class InventoryTransaction(Base):
    """库存事务表 - 记录所有库存变更"""
    __tablename__ = "inventory_transaction"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(String(100), nullable=False, index=True)
    transaction_type = Column(SqlEnum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(String(100))
    reason = Column(String(500))
    operator_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

## 4. 业务服务实现

### 4.1 服务层架构

```python
# app/modules/inventory_management/service.py

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import (
    InventoryStock, InventoryReservation, InventoryTransaction,
    TransactionType, ReservationType
)
from .exceptions import (
    InsufficientInventoryError, InventoryNotFoundError,
    ReservationExpiredError
)

class InventoryService:
    """库存管理服务类"""

    def __init__(self, db: Session):
        self.db = db

    async def get_sku_inventory(self, sku_id: str) -> Optional[Dict]:
        """获取SKU库存信息"""
        inventory = self.db.query(InventoryStock).filter(
            InventoryStock.sku_id == sku_id
        ).first()
        
        if not inventory:
            return None
            
        return {
            "id": inventory.id,
            "sku_id": inventory.sku_id,
            "total_quantity": inventory.total_quantity,
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "warning_threshold": inventory.warning_threshold,
            "critical_threshold": inventory.critical_threshold,
            "is_low_stock": inventory.is_low_stock,
            "is_critical_stock": inventory.is_critical_stock,
            "is_out_of_stock": inventory.is_out_of_stock,
            "is_active": inventory.is_active,
            "last_updated": inventory.updated_at
        }
```

### 4.2 核心业务逻辑实现

```python
    async def reserve_inventory(
        self,
        reservation_type: ReservationType,
        reference_id: str,
        items: List[Dict],
        expires_minutes: int,
        user_id: int
    ) -> Dict:
        """预占库存"""
        reservation_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        reserved_items = []
        
        try:
            for item in items:
                sku_id = item["sku_id"]
                quantity = item["quantity"]
                
                # 使用悲观锁获取库存记录
                inventory = self.db.query(InventoryStock).filter(
                    InventoryStock.sku_id == sku_id,
                    InventoryStock.is_active == True
                ).with_for_update().first()
                
                if not inventory:
                    raise InventoryNotFoundError(f"SKU {sku_id} 不存在或未启用库存管理")
                
                # 检查库存是否足够
                if not inventory.can_reserve(quantity):
                    raise InsufficientInventoryError(
                        sku_id, quantity, inventory.available_quantity
                    )
                
                # 执行预占
                if not inventory.reserve_quantity(quantity):
                    raise InsufficientInventoryError(f"SKU {sku_id} 预占失败")
                
                # 创建预占记录
                reservation = InventoryReservation(
                    sku_id=sku_id,
                    reservation_type=reservation_type,
                    reference_id=reference_id,
                    quantity=quantity,
                    expires_at=expires_at
                )
                self.db.add(reservation)
                
                # 记录事务
                transaction = InventoryTransaction(
                    sku_id=sku_id,
                    transaction_type=TransactionType.RESERVE,
                    quantity_change=-quantity,
                    quantity_before=inventory.available_quantity + quantity,
                    quantity_after=inventory.available_quantity,
                    reference_type=reservation_type.value,
                    reference_id=reference_id,
                    operator_id=user_id
                )
                self.db.add(transaction)
                
                reserved_items.append({
                    "sku_id": sku_id,
                    "reserved_quantity": quantity,
                    "available_after_reserve": inventory.available_quantity
                })
            
            self.db.commit()
            
            return {
                "reservation_id": reservation_id,
                "expires_at": expires_at,
                "reserved_items": reserved_items
            }
            
        except Exception as e:
            self.db.rollback()
            raise
```

### 4.3 异常处理实现

```python
# app/modules/inventory_management/exceptions.py

class InventoryException(Exception):
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
    def __init__(self, message: str):
        super().__init__(message)

class ReservationExpiredError(InventoryException):
    """预占已过期异常"""
    def __init__(self, reservation_id: str):
        super().__init__(f"预占 {reservation_id} 已过期")

class InvalidOperationError(InventoryException):
    """无效操作异常"""
    def __init__(self, message: str):
        super().__init__(message)
```

## 5. API接口实现

### 5.1 数据Schema定义

```python
# app/modules/inventory_management/schemas.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ReservationType(str, Enum):
    CART = "cart"
    ORDER = "order"

class InventoryResponse(BaseModel):
    """库存信息响应模型"""
    sku_id: str
    total_quantity: int = Field(ge=0)
    available_quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)
    warning_threshold: int = Field(ge=0)
    critical_threshold: int = Field(ge=0)
    is_low_stock: bool
    is_critical_stock: bool
    is_out_of_stock: bool
    is_active: bool
    last_updated: datetime

class ReservationItem(BaseModel):
    """预占商品项"""
    sku_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)

class ReservationRequest(BaseModel):
    """库存预占请求"""
    reservation_type: ReservationType
    reference_id: str = Field(..., min_length=1, max_length=100)
    items: List[ReservationItem] = Field(..., min_items=1, max_items=100)
    expires_minutes: int = Field(default=120, gt=0, le=1440)

    @validator('items')
    def validate_unique_skus(cls, v):
        """验证SKU不重复"""
        sku_ids = [item.sku_id for item in v]
        if len(sku_ids) != len(set(sku_ids)):
            raise ValueError("SKU不能重复")
        return v

class ReservationResponse(BaseModel):
    """预占响应"""
    reservation_id: str
    expires_at: datetime
    reserved_items: List[Dict[str, Any]]
```

### 5.2 路由实现

```python
# app/modules/inventory_management/router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.modules.user_auth.dependencies import get_current_user
from .service import InventoryService
from .schemas import (
    InventoryResponse, ReservationRequest, ReservationResponse
)
from .exceptions import (
    InsufficientInventoryError, InventoryNotFoundError
)

router = APIRouter(prefix="/api/v1/inventory", tags=["库存管理"])

def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """获取库存服务实例"""
    return InventoryService(db)

@router.get("/sku/{sku_id}", response_model=InventoryResponse)
async def get_sku_inventory(
    sku_id: str,
    service: InventoryService = Depends(get_inventory_service)
):
    """获取SKU库存信息"""
    try:
        inventory = await service.get_sku_inventory(sku_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SKU {sku_id} 的库存记录不存在"
            )
        return inventory
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/reserve", response_model=ReservationResponse)
async def reserve_inventory(
    request: ReservationRequest,
    service: InventoryService = Depends(get_inventory_service),
    current_user = Depends(get_current_user)
):
    """预占库存"""
    try:
        result = await service.reserve_inventory(
            reservation_type=request.reservation_type,
            reference_id=request.reference_id,
            items=[item.dict() for item in request.items],
            expires_minutes=request.expires_minutes,
            user_id=current_user.id
        )
        return result
    except InsufficientInventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INV_002",
                "message": str(e),
                "sku_id": e.sku_id,
                "requested": e.requested,
                "available": e.available
            }
        )
    except InventoryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "INV_001",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

## 6. 数据库迁移实现

### 6.1 Alembic配置

```python
# alembic/versions/001_create_inventory_tables.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 创建枚举类型
    transaction_type = postgresql.ENUM(
        'reserve', 'release', 'deduct', 'adjust', 'restock',
        name='transactiontype'
    )
    transaction_type.create(op.get_bind())
    
    reservation_type = postgresql.ENUM(
        'cart', 'order',
        name='reservationtype'
    )
    reservation_type.create(op.get_bind())

    # 创建库存主表
    op.create_table('inventory_stock',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku_id', sa.String(length=100), nullable=False),
        sa.Column('total_quantity', sa.Integer(), nullable=False),
        sa.Column('reserved_quantity', sa.Integer(), nullable=False),
        sa.Column('warning_threshold', sa.Integer(), nullable=False),
        sa.Column('critical_threshold', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku_id')
    )
    
    # 创建索引
    op.create_index('idx_inventory_sku_id', 'inventory_stock', ['sku_id'])
    op.create_index('idx_inventory_active', 'inventory_stock', ['is_active'])

def downgrade():
    op.drop_index('idx_inventory_active', table_name='inventory_stock')
    op.drop_index('idx_inventory_sku_id', table_name='inventory_stock')
    op.drop_table('inventory_stock')
    
    op.execute('DROP TYPE reservationtype')
    op.execute('DROP TYPE transactiontype')
```

### 6.2 数据库约束

```sql
-- 添加业务约束
ALTER TABLE inventory_stock 
ADD CONSTRAINT chk_inventory_quantities 
CHECK (total_quantity >= 0 AND reserved_quantity >= 0 AND reserved_quantity <= total_quantity);

ALTER TABLE inventory_stock 
ADD CONSTRAINT chk_inventory_thresholds 
CHECK (critical_threshold <= warning_threshold);

-- 添加复合索引优化查询
CREATE INDEX idx_inventory_low_stock 
ON inventory_stock (sku_id, is_active) 
WHERE (total_quantity - reserved_quantity) <= warning_threshold;

CREATE INDEX idx_reservation_active_sku 
ON inventory_reservation (sku_id, is_active, expires_at);
```

## 7. 缓存实现

### 7.1 Redis缓存策略

```python
# app/modules/inventory_management/cache.py

import json
import asyncio
from typing import Optional, Dict, List
from datetime import timedelta

from app.core.redis_client import get_redis_client

class InventoryCache:
    """库存缓存管理"""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.cache_prefix = "inventory"
        self.default_ttl = 300  # 5分钟

    async def get_inventory(self, sku_id: str) -> Optional[Dict]:
        """获取缓存的库存信息"""
        cache_key = f"{self.cache_prefix}:stock:{sku_id}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set_inventory(self, sku_id: str, inventory_data: Dict, ttl: int = None):
        """缓存库存信息"""
        cache_key = f"{self.cache_prefix}:stock:{sku_id}"
        ttl = ttl or self.default_ttl
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(inventory_data, default=str)
        )

    async def invalidate_inventory(self, sku_id: str):
        """清除库存缓存"""
        cache_key = f"{self.cache_prefix}:stock:{sku_id}"
        await self.redis.delete(cache_key)

    async def batch_invalidate(self, sku_ids: List[str]):
        """批量清除库存缓存"""
        cache_keys = [f"{self.cache_prefix}:stock:{sku_id}" for sku_id in sku_ids]
        if cache_keys:
            await self.redis.delete(*cache_keys)
```

### 7.2 缓存集成

```python
# 在service.py中集成缓存

class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = InventoryCache()

    async def get_sku_inventory_with_cache(self, sku_id: str) -> Optional[Dict]:
        """带缓存的库存查询"""
        # 尝试从缓存获取
        cached_inventory = await self.cache.get_inventory(sku_id)
        if cached_inventory:
            return cached_inventory
        
        # 缓存未命中，查询数据库
        inventory = await self.get_sku_inventory(sku_id)
        if inventory:
            # 缓存查询结果
            await self.cache.set_inventory(sku_id, inventory)
        
        return inventory

    async def _invalidate_cache_after_update(self, sku_ids: List[str]):
        """库存更新后清除相关缓存"""
        await self.cache.batch_invalidate(sku_ids)
```

## 8. 测试实现

### 8.1 单元测试

```python
# tests/unit/test_services/test_inventory_service.py

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from app.modules.inventory_management.service import InventoryService
from app.modules.inventory_management.models import ReservationType
from app.modules.inventory_management.exceptions import InsufficientInventoryError

class TestInventoryService:
    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def service(self, mock_db):
        return InventoryService(db=mock_db)

    @pytest.mark.asyncio
    async def test_get_sku_inventory_success(self, service, mock_db):
        """测试获取SKU库存 - 成功场景"""
        # Arrange
        sku_id = "TEST-SKU-001"
        mock_inventory = Mock()
        mock_inventory.id = 1
        mock_inventory.sku_id = sku_id
        mock_inventory.total_quantity = 100
        mock_inventory.available_quantity = 80
        mock_inventory.reserved_quantity = 20
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_inventory

        # Act
        result = await service.get_sku_inventory(sku_id)

        # Assert
        assert result is not None
        assert result["sku_id"] == sku_id
        assert result["total_quantity"] == 100
        assert result["available_quantity"] == 80

    @pytest.mark.asyncio
    async def test_reserve_inventory_insufficient_stock(self, service, mock_db):
        """测试库存预占 - 库存不足"""
        # Arrange
        items = [{"sku_id": "SKU-003", "quantity": 100}]
        mock_stock = Mock()
        mock_stock.available_quantity = 10
        mock_stock.can_reserve.return_value = False
        
        mock_db.query.return_value.filter.return_value.with_for_update.return_value.first.return_value = mock_stock
        
        # Act & Assert
        with pytest.raises(InsufficientInventoryError):
            await service.reserve_inventory(
                reservation_type=ReservationType.CART,
                reference_id="cart_456",
                items=items,
                expires_minutes=120,
                user_id=1
            )
```

### 8.2 集成测试

```python
# tests/integration/test_inventory_api.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_get_sku_inventory_not_found(client):
    """测试获取不存在的SKU库存"""
    response = client.get("/api/v1/inventory/sku/NONEXISTENT-SKU")
    assert response.status_code == 404

def test_create_and_get_inventory(client):
    """测试创建和查询库存的完整流程"""
    # 创建库存
    create_data = {
        "sku_id": "TEST-SKU-001",
        "initial_quantity": 100,
        "warning_threshold": 10,
        "critical_threshold": 5
    }
    
    create_response = client.post("/api/v1/inventory/create", json=create_data)
    assert create_response.status_code == 201
    
    # 查询库存
    get_response = client.get("/api/v1/inventory/sku/TEST-SKU-001")
    assert get_response.status_code == 200
    
    inventory_data = get_response.json()
    assert inventory_data["sku_id"] == "TEST-SKU-001"
    assert inventory_data["total_quantity"] == 100
```

## 9. 性能优化实现

### 9.1 数据库查询优化

```python
# 批量查询优化
async def get_batch_inventory_optimized(self, sku_ids: List[str]) -> List[Dict]:
    """优化的批量库存查询"""
    # 使用IN查询减少数据库访问次数
    inventories = self.db.query(InventoryStock).filter(
        InventoryStock.sku_id.in_(sku_ids),
        InventoryStock.is_active == True
    ).all()
    
    # 建立映射关系提高查找效率
    inventory_map = {inv.sku_id: inv for inv in inventories}
    
    results = []
    for sku_id in sku_ids:
        if sku_id in inventory_map:
            inv = inventory_map[sku_id]
            results.append({
                "sku_id": inv.sku_id,
                "available_quantity": inv.available_quantity,
                "reserved_quantity": inv.reserved_quantity,
                "total_quantity": inv.total_quantity,
                "is_low_stock": inv.is_low_stock
            })
    
    return results
```

### 9.2 连接池配置

```python
# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 数据库连接池优化配置
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 连接池大小
    max_overflow=30,       # 最大溢出连接
    pool_pre_ping=True,    # 连接验证
    pool_recycle=3600,     # 连接回收时间
    echo=False             # 生产环境关闭SQL日志
)
```

## 10. 监控和日志实现

### 10.1 业务监控指标

```python
# app/modules/inventory_management/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# 定义监控指标
inventory_operations_total = Counter(
    'inventory_operations_total',
    'Total inventory operations',
    ['operation_type', 'status']
)

inventory_operation_duration = Histogram(
    'inventory_operation_duration_seconds',
    'Inventory operation duration',
    ['operation_type']
)

current_low_stock_items = Gauge(
    'inventory_low_stock_items_current',
    'Current number of low stock items'
)

def monitor_operation(operation_type: str):
    """装饰器：监控操作指标"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                inventory_operations_total.labels(
                    operation_type=operation_type, 
                    status='success'
                ).inc()
                return result
            except Exception as e:
                inventory_operations_total.labels(
                    operation_type=operation_type, 
                    status='error'
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                inventory_operation_duration.labels(
                    operation_type=operation_type
                ).observe(duration)
                
        return wrapper
    return decorator

# 使用示例
class InventoryService:
    @monitor_operation('reserve_inventory')
    async def reserve_inventory(self, ...):
        # 业务逻辑
        pass
```

### 10.2 结构化日志

```python
# app/modules/inventory_management/logging.py

import structlog
from app.core.security_logger import get_security_logger

logger = structlog.get_logger(__name__)
security_logger = get_security_logger()

class InventoryAuditLogger:
    """库存操作审计日志"""
    
    @staticmethod
    async def log_inventory_change(
        operation: str,
        sku_id: str,
        user_id: int,
        old_quantity: int,
        new_quantity: int,
        reason: str = None,
        request_id: str = None
    ):
        """记录库存变更审计日志"""
        await security_logger.log_security_event(
            event_type="inventory_change",
            user_id=user_id,
            details={
                "operation": operation,
                "sku_id": sku_id,
                "quantity_change": new_quantity - old_quantity,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "reason": reason
            },
            request_id=request_id
        )
    
    @staticmethod
    async def log_reservation_event(
        event_type: str,
        reservation_id: str,
        sku_id: str,
        quantity: int,
        user_id: int,
        expires_at: datetime = None
    ):
        """记录预占事件日志"""
        logger.info(
            "inventory_reservation_event",
            event_type=event_type,
            reservation_id=reservation_id,
            sku_id=sku_id,
            quantity=quantity,
            user_id=user_id,
            expires_at=expires_at
        )
```

---

**文档版本**: v1.0  
**创建日期**: 2025-09-15  
**最后更新**: 2025-09-15  
**责任人**: 开发工程师  
**审核人**: 技术负责人