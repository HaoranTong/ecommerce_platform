<!--
文档说明：
- 内容：模块实现记录文档模板
- 作用：记录开发过程、实现细节、技术问题和解决方案
- 使用方法：开发过程中实时记录，便于知识传承
-->

# 购物车模块 - 实现记录文档

📅 **创建日期**: 2025-09-16  
👤 **开发者**: 后端开发团队  
🔄 **最后更新**: 2025-09-16  
📊 **完成进度**: 0% (设计阶段完成，代码实现待开始)  

## 实施概述

### 实施状态
- **当前状态**: 设计完成，待开始开发
- **完成功能**: 技术文档设计、架构规划、API规范制定
- **待实施**: 数据模型实现、业务逻辑开发、API接口实现、缓存集成、测试用例
- **技术债务**: 无 (新模块开发)

### 关键里程碑
| 日期 | 里程碑 | 状态 | 备注 |
|------|--------|------|------|
| 2025-09-16 | 技术文档完成 | ✅ | 完成7个技术文档编写 |
| 预计第1周 | 数据模型实现 | ⏳ | Cart和CartItem模型 |
| 预计第1周 | 基础API实现 | ⏳ | CRUD接口开发 |
| 预计第2周 | 缓存集成完成 | ⏳ | Redis缓存策略 |
| 预计第3周 | 集成测试完成 | ⏳ | 与外部服务集成 |
| 预计第4周 | 性能优化完成 | ⏳ | 压测和优化 |

## 代码实现

### 目录结构
```
app/modules/shopping_cart/
├── __init__.py         # ⏳ 模块导出配置
├── router.py           # ⏳ API路由实现
├── service.py          # ⏳ 业务逻辑实现  
├── models.py           # ⏳ SQLAlchemy数据模型
├── schemas.py          # ⏳ Pydantic数据传输对象
├── dependencies.py     # ⏳ FastAPI依赖注入
└── README.md           # ⏳ 模块导航文档
```

### 核心组件实现规划

#### API路由层 (router.py)
```python
# 计划实现的API路由结构
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from .schemas import (
    AddItemRequest, 
    UpdateQuantityRequest, 
    BatchDeleteRequest,
    CartResponse
)
from .service import CartService
from .dependencies import get_cart_service

router = APIRouter(prefix="/api/v1/cart", tags=["购物车"])

@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    request: AddItemRequest,
    current_user: dict = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """添加商品到购物车"""
    # 具体实现将在开发阶段完成
    pass

@router.get("", response_model=CartResponse) 
async def get_cart(
    current_user: dict = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """获取购物车内容"""
    # 具体实现将在开发阶段完成
    pass

@router.put("/items/{item_id}", response_model=CartResponse)
async def update_item_quantity(
    item_id: int,
    request: UpdateQuantityRequest,
    current_user: dict = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """更新商品数量"""
    # 具体实现将在开发阶段完成
    pass

@router.delete("/items/{item_id}")
async def delete_cart_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """删除购物车商品项"""
    # 具体实现将在开发阶段完成
    pass

@router.delete("/items")
async def batch_delete_items(
    request: BatchDeleteRequest,
    current_user: dict = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """批量删除购物车商品"""
    # 具体实现将在开发阶段完成
    pass

@router.delete("")
async def clear_cart(
    current_user: dict = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """清空购物车"""
    # 具体实现将在开发阶段完成
    pass
```

#### 业务逻辑层 (service.py)
```python
# 计划实现的业务服务结构
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from .models import Cart, CartItem
from .schemas import AddItemRequest, CartResponse
from app.modules.product_catalog.service import ProductService
from app.modules.inventory_management.service import InventoryService

class CartService:
    def __init__(
        self, 
        db: Session,
        redis_client: Redis,
        product_service: ProductService,
        inventory_service: InventoryService
    ):
        self.db = db
        self.redis_client = redis_client
        self.product_service = product_service
        self.inventory_service = inventory_service
    
    async def add_item(self, user_id: int, request: AddItemRequest) -> CartResponse:
        """添加商品到购物车"""
        # 1. 验证商品存在性和状态
        # 2. 检查库存充足性
        # 3. 验证业务规则（数量限制等）
        # 4. 更新购物车数据
        # 5. 同步缓存
        # 具体实现将在开发阶段完成
        pass
    
    async def get_cart(self, user_id: int) -> CartResponse:
        """获取购物车内容"""
        # 1. 优先从Redis读取
        # 2. 缓存未命中时从数据库读取
        # 3. 聚合商品信息和库存状态
        # 4. 计算价格汇总
        # 具体实现将在开发阶段完成
        pass
    
    async def update_quantity(self, user_id: int, item_id: int, quantity: int) -> CartResponse:
        """更新商品数量"""
        # 1. 验证商品项归属
        # 2. 重新验证库存
        # 3. 更新数量
        # 4. 重新计算价格
        # 5. 同步缓存
        # 具体实现将在开发阶段完成
        pass
    
    async def delete_item(self, user_id: int, item_id: int) -> bool:
        """删除购物车商品项"""
        # 1. 验证商品项归属
        # 2. 执行删除操作
        # 3. 更新缓存
        # 具体实现将在开发阶段完成
        pass
    
    async def clear_cart(self, user_id: int) -> bool:
        """清空购物车"""
        # 1. 删除所有商品项
        # 2. 清理缓存
        # 具体实现将在开发阶段完成
        pass
    
    # 私有方法
    def _get_cart_cache_key(self, user_id: int) -> str:
        """获取购物车缓存key"""
        return f"cart:user:{user_id}"
    
    async def _validate_business_rules(self, cart: Cart, new_item: dict) -> bool:
        """验证业务规则"""
        # 1. 检查购物车商品种类限制
        # 2. 检查单商品数量限制
        # 具体实现将在开发阶段完成
        pass
    
    async def _calculate_totals(self, items: List[CartItem]) -> dict:
        """计算购物车汇总信息"""
        # 1. 计算总商品种类
        # 2. 计算总商品数量
        # 3. 计算总金额
        # 具体实现将在开发阶段完成
        pass
```

#### 数据模型层 (models.py)  
```python
# 计划实现的数据模型结构
from sqlalchemy import Column, Integer, String, DateTime, Decimal, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.shared.base_models import Base

class Cart(Base):
    """购物车主表"""
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id})>"

class CartItem(Base):
    """购物车商品项表"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Decimal(10, 2), nullable=False)  # 加入时的商品单价
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 唯一约束：同一购物车中，同一SKU只能有一条记录
    __table_args__ = (UniqueConstraint('cart_id', 'sku_id', name='uk_cart_sku'),)
    
    # 关联关系
    cart = relationship("Cart", back_populates="items")
    
    @property
    def subtotal(self) -> Decimal:
        """计算小计"""
        return self.unit_price * self.quantity
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, sku_id={self.sku_id}, quantity={self.quantity})>"
```

#### 数据传输对象 (schemas.py)
```python
# 计划实现的Pydantic模型结构
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class StockStatus(str, Enum):
    """库存状态枚举"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"

class AddItemRequest(BaseModel):
    """添加商品到购物车请求"""
    sku_id: int = Field(..., gt=0, description="商品SKU ID")
    quantity: int = Field(..., ge=1, le=999, description="商品数量")
    
    class Config:
        schema_extra = {
            "example": {
                "sku_id": 12345,
                "quantity": 2
            }
        }

class UpdateQuantityRequest(BaseModel):
    """更新商品数量请求"""
    quantity: int = Field(..., ge=1, le=999, description="新的商品数量")

class BatchDeleteRequest(BaseModel):
    """批量删除商品请求"""
    item_ids: List[int] = Field(..., min_items=1, max_items=50, description="商品项ID列表")

class CartItemResponse(BaseModel):
    """购物车商品项响应"""
    item_id: int
    sku_id: int
    product_name: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    stock_status: StockStatus
    available_stock: int
    added_at: datetime
    
    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    """购物车响应"""
    cart_id: int
    user_id: int
    total_items: int  # 商品种类数
    total_quantity: int  # 商品总数量
    total_amount: Decimal  # 总金额
    items: List[CartItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class SuccessResponse(BaseModel):
    """通用成功响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None
```

#### 依赖注入 (dependencies.py)
```python
# 计划实现的依赖注入结构
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.modules.product_catalog.service import ProductService
from app.modules.inventory_management.service import InventoryService
from .service import CartService

def get_cart_service(
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis),
    product_service: ProductService = Depends(),
    inventory_service: InventoryService = Depends()
) -> CartService:
    """获取购物车服务实例"""
    return CartService(db, redis_client, product_service, inventory_service)
```
## 关键算法实现

### 购物车缓存策略
```python
# 缓存实现策略
class CartCacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 3600  # 1小时
    
    async def get_cart_from_cache(self, user_id: int) -> Optional[dict]:
        """从缓存获取购物车数据"""
        cache_key = f"cart:user:{user_id}"
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")
        return None
    
    async def set_cart_cache(self, user_id: int, cart_data: dict):
        """设置购物车缓存"""
        cache_key = f"cart:user:{user_id}"
        try:
            await self.redis.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(cart_data, cls=DecimalEncoder)
            )
        except Exception as e:
            logger.error(f"缓存写入失败: {e}")
    
    async def invalidate_cart_cache(self, user_id: int):
        """清除购物车缓存"""
        cache_key = f"cart:user:{user_id}"
        await self.redis.delete(cache_key)
```

### 库存验证算法
```python
# 分布式锁保护的库存验证
class InventoryValidator:
    def __init__(self, redis_client, inventory_service):
        self.redis = redis_client
        self.inventory_service = inventory_service
    
    async def validate_and_reserve_stock(self, sku_id: int, quantity: int) -> bool:
        """验证并预占库存"""
        lock_key = f"inventory:lock:sku:{sku_id}"
        
        # 获取分布式锁
        async with RedisLock(self.redis, lock_key, timeout=5):
            # 查询当前库存
            current_stock = await self.inventory_service.get_available_stock(sku_id)
            
            if current_stock >= quantity:
                # 库存充足，执行预占
                success = await self.inventory_service.reserve_stock(sku_id, quantity)
                return success
            else:
                # 库存不足
                return False
    
    async def release_reserved_stock(self, sku_id: int, quantity: int):
        """释放预占库存"""
        await self.inventory_service.release_stock(sku_id, quantity)
```

### 价格计算引擎
```python
# 购物车价格计算逻辑
class PriceCalculator:
    def __init__(self, product_service):
        self.product_service = product_service
    
    async def calculate_cart_totals(self, cart_items: List[CartItem]) -> dict:
        """计算购物车汇总信息"""
        total_items = len(cart_items)
        total_quantity = sum(item.quantity for item in cart_items)
        total_amount = Decimal('0.00')
        
        # 批量获取最新商品价格
        sku_ids = [item.sku_id for item in cart_items]
        current_prices = await self.product_service.get_prices_batch(sku_ids)
        
        # 计算每个商品的小计
        for item in cart_items:
            current_price = current_prices.get(item.sku_id, item.unit_price)
            item.current_unit_price = current_price
            item.subtotal = current_price * item.quantity
            total_amount += item.subtotal
        
        return {
            "total_items": total_items,
            "total_quantity": total_quantity,  
            "total_amount": total_amount
        }
    
    async def apply_promotions(self, cart_data: dict) -> dict:
        """应用促销规则（预留接口）"""
        # 未来扩展：优惠券、满减、折扣等
        return cart_data
```
```python
class {Module}Repository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def create_{entity}(self, entity_data: dict):
        """
        数据访问实现：
        - 表：{table_name}
        - 操作：{操作类型}
        - 索引使用：{索引信息}
        """
        # 实现代码
        pass
```

### 数据模型实现

#### SQLAlchemy模型
```python
from app.shared.base_models import BaseModel, TimestampMixin

class {Entity}(BaseModel, TimestampMixin):
    __tablename__ = '{table_name}'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    # 其他字段
    
    # 实现说明：
    # - 继承BaseModel提供基础功能
    # - 使用TimestampMixin自动处理时间戳
    # - 索引策略：{索引说明}
```

## 技术实现细节

### 关键算法实现
- **算法1**: {算法描述和实现}
- **算法2**: {算法描述和实现}

### 性能优化
- **数据库优化**: {具体优化措施}
- **缓存实现**: {缓存策略实现}
- **异步处理**: {异步实现方案}

### 错误处理
```python
class {Module}Exception(Exception):
    """模块自定义异常"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

# 使用示例
try:
    # 业务逻辑
    pass
except ValueError as e:
    raise {Module}Exception("业务错误", "MODULE_001")
```

## 集成实现

### 模块间集成
- **用户认证集成**: 通过依赖注入获取当前用户信息，验证用户身份
- **商品服务集成**: 调用ProductCatalogService获取商品信息和价格
- **库存服务集成**: 调用InventoryService进行实时库存验证
- **事件发布**: 发布购物车变更事件，供其他模块订阅

### 外部服务集成
```python
class ProductCatalogClient:
    """商品目录服务客户端"""
    
    def __init__(self):
        self.base_url = settings.PRODUCT_CATALOG_URL
        self.timeout = 5
        self.retry_times = 3
    
    async def get_product_info(self, sku_id: int) -> Optional[dict]:
        """
        获取商品信息：
        - 接口：GET /api/v1/products/{sku_id}
        - 重试：指数退避，最多3次
        - 降级：返回缓存的基础信息
        """
        for attempt in range(self.retry_times):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(f"{self.base_url}/api/v1/products/{sku_id}") as resp:
                        if resp.status == 200:
                            return await resp.json()
                        elif resp.status == 404:
                            return None
            except Exception as e:
                if attempt == self.retry_times - 1:
                    logger.error(f"商品信息获取失败: sku_id={sku_id}, error={e}")
                    # 降级：从本地缓存获取基础信息
                    return await self._get_cached_product_info(sku_id)
                await asyncio.sleep(2 ** attempt)  # 指数退避

class InventoryServiceClient:
    """库存服务客户端"""
    
    async def check_stock_availability(self, sku_id: int, quantity: int) -> bool:
        """
        库存可用性检查：
        - 接口：POST /api/v1/inventory/check
        - 重试：快速失败，不重试
        - 降级：返回False，拒绝操作保护系统
        """
        try:
            # 调用库存服务API
            result = await self._call_inventory_api(sku_id, quantity)
            return result.get('available', False)
        except Exception as e:
            logger.error(f"库存检查失败: sku_id={sku_id}, error={e}")
            return False  # 保守策略，拒绝操作
```

## 数据库实施

### 迁移脚本
```python
# alembic/versions/20250916_001_shopping_cart_init.py
"""创建购物车相关表

Revision ID: cart_001
Revises: base
Create Date: 2025-09-16 10:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = 'cart_001'
down_revision = 'base'
branch_labels = None
depends_on = None

def upgrade():
    # 创建购物车主表
    op.create_table('carts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uk_user_cart')
    )
    op.create_index('ix_carts_user_id', 'carts', ['user_id'])
    
    # 创建购物车商品项表
    op.create_table('cart_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('sku_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Decimal(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sku_id'], ['products.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('cart_id', 'sku_id', name='uk_cart_sku'),
        sa.CheckConstraint('quantity > 0 AND quantity <= 999', name='chk_quantity_range')
    )
    op.create_index('ix_cart_items_cart_id', 'cart_items', ['cart_id'])
    op.create_index('ix_cart_items_sku_id', 'cart_items', ['sku_id'])

def downgrade():
    op.drop_table('cart_items')
    op.drop_table('carts')
    )
    
    # 索引创建
    op.create_index('idx_{table}_{field}', '{table_name}', ['field'])

def downgrade():
    op.drop_table('{table_name}')
```

### 数据初始化
```python
# 初始化数据脚本
def init_{module}_data():
    """
    数据初始化：
    - 基础数据：{基础数据说明}
    - 测试数据：{测试数据说明}
    """
    # 实现代码
    pass
```

## 测试实施

### 单元测试实现
```python
import pytest
from app.modules.shopping_cart.service import {Module}Service

class Test{Module}Service:
    def setup_method(self):
        """测试设置"""
        self.service = {Module}Service()
    
    def test_create_{resource}(self):
        """
        测试用例：
        - 场景：{测试场景}
        - 输入：{输入数据}
        - 预期：{预期结果}
        """
        # 测试实现
        pass
```

### 集成测试实现
```python
def test_{module}_api_integration():
    """
    集成测试：
    - 测试范围：{测试范围}
    - 数据准备：{数据准备}
    - 验证点：{验证内容}
    """
    # 测试实现
    pass
```

## 配置实施

### 环境配置
```python
# app/core/config.py
class {Module}Settings:
    """模块配置"""
    {module}_feature_enabled: bool = True
    {module}_cache_ttl: int = 3600
    # 其他配置项
```

### 依赖注入配置
```python
# app/modules/shopping_cart/dependencies.py
def get_{module}_service() -> {Module}Service:
    """依赖注入工厂"""
    repository = get_{module}_repository()
    return {Module}Service(repository)
```

## 部署实施

### Docker配置
```dockerfile
# 如果需要特殊配置
FROM python:3.11-slim

# 模块特定依赖
RUN pip install {special_packages}

# 配置文件
COPY config/{module}.yaml /app/config/
```

### 环境变量
```bash
# 模块相关环境变量
{MODULE}_FEATURE_ENABLED=true
{MODULE}_CACHE_TTL=3600
{MODULE}_EXTERNAL_API_URL=https://api.example.com
```

## 问题和解决方案

### 技术问题记录
| 日期 | 问题描述 | 解决方案 | 状态 |
|------|----------|----------|------|
| 待开发 | Redis缓存与MySQL数据一致性 | 双写策略+最终一致性保证 | 🔄 待验证 |
| 待开发 | 高并发下库存超卖问题 | Redis分布式锁+乐观锁机制 | 🔄 待实现 |
| 待开发 | 缓存穿透和雪崩问题 | 空值缓存+布隆过滤器+缓存预热 | 🔄 待实现 |

### 性能问题预案
- **问题**: 购物车查询响应时间过长
- **原因**: 商品信息聚合查询量大，数据库压力
- **解决**: 1)Redis缓存预热 2)批量查询优化 3)商品信息本地缓存
- **效果**: 预期响应时间从800ms优化到200ms以内

### 集成问题预案  
- **问题**: 库存服务调用超时影响用户体验
- **影响**: 添加商品到购物车操作失败，用户操作受阻
- **解决**: 1)设置合理超时时间(5s) 2)快速失败策略 3)降级机制(禁止添加)

## 知识总结

### 经验教训
- **缓存一致性经验**: 购物车作为高频操作模块，缓存策略设计至关重要，双写+异步校验是较好的平衡方案
- **并发控制教训**: 分布式锁不是万能的，需要结合业务特点选择合适的锁粒度和超时时间
- **降级策略改进**: 外部服务调用必须设计降级方案，保护核心功能不受影响

### 最佳实践
- **分层架构实践**: Router→Service→Repository分层清晰，便于单元测试和维护
- **依赖注入实践**: 通过FastAPI的Depends机制管理依赖，提高代码可测试性
- **错误处理实践**: 统一异常处理机制，区分业务异常和系统异常
- **监控实践**: 关键业务指标和技术指标并重，及时发现和解决问题

### 技术债务
- **缓存预热机制**: 系统启动时需要实现购物车缓存预热，避免冷启动性能问题
- **批量操作优化**: 当前设计为单个操作，后续需要实现真正的批量添加/删除接口
- **事件系统完善**: 购物车变更事件发布机制需要与消息队列集成

## 后续计划

### 性能优化计划
- [ ] Redis缓存预热机制实现 - 第5周
- [ ] 数据库查询性能优化 - 第5周  
- [ ] 批量操作接口实现 - 第6周
- [ ] 缓存命中率监控和调优 - 第6周

### 功能扩展计划
- [ ] 购物车推荐商品功能 - 第7-8周
- [ ] 购物车优惠券集成 - 第8-9周
- [ ] 购物车分享功能 - 第9-10周
- [ ] 移动端购物车同步 - 第10-11周

### 技术升级计划  
- [ ] 事件驱动架构集成 - 第12周
- [ ] 微服务拆分准备 - 第13-14周
- [ ] GraphQL接口支持 - 第15周
- [ ] 实时推送功能 - 第16周

## 变更记录

| 日期 | 版本 | 变更内容 | 开发者 |
|------|------|----------|--------|
| 2025-09-16 | v1.0 | 购物车模块实现规划和技术方案设计 | 后端架构师 |
