<!--
文档说明：
- 内容：数据架构设计，包括数据模型、存储策略、数据关系和性能优化
- 使用方法：数据库设计和数据模型开发的权威指导文档  
- 更新方法：数据架构调整或新增数据模型时更新
- 引用关系：被各模块models.py引用，引用business-architecture.md业务领域
- 更新频率：数据架构设计变更时
-->

# 数据架构设计

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-09-22  
👤 **负责人**: 数据架构师  
🔄 **最后更新**: 2025-09-22  
📋 **版本**: v1.0.0  

## 数据架构概览

### 数据存储技术栈

```
┌─────────────────────────────────────────────────────────────────┐
│                      数据架构技术栈                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  主数据库   │  │  缓存系统   │  │  搜索引擎   │  │  文件存储   │ │
│  │   MySQL     │  │   Redis     │  │Elasticsearch│  │   OSS/S3    │ │
│  │   8.0+      │  │   7.0+      │  │    8.0+     │  │   CDN       │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  消息队列   │  │  区块链存储  │  │  时序数据库  │  │  向量数据库  │ │
│  │  RabbitMQ   │  │  IPFS/链存证 │  │  InfluxDB   │  │  Pinecone   │ │
│  │  (后期)     │  │  (溯源)     │  │  (IoT)      │  │  (AI推荐)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 数据分布策略

| 数据类型 | 存储选型 | 访问模式 | 性能要求 |
|---------|---------|---------|---------|
| **核心业务数据** | MySQL主库 | 读写频繁 | ACID事务保证 |
| **热点数据** | Redis缓存 | 读多写少 | 毫秒级响应 |
| **搜索数据** | Elasticsearch | 复杂查询 | 秒级响应 |
| **媒体文件** | OSS+CDN | 读多写少 | 全球分发 |
| **溯源数据** | 区块链+IPFS | 防篡改 | 可信存证 |
| **IoT数据** | InfluxDB | 时序写入 | 高吞吐 |
| **AI模型数据** | 向量数据库 | 相似度查询 | 实时推荐 |

## 模块数据架构

### 按业务域划分数据表

基于[业务架构设计](business-architecture.md)的6大业务域，进行数据表分配：

#### 1. 用户域数据表

| 表名 | 主要职责 | 核心字段 | 索引策略 |
|------|---------|---------|---------|
| `users` | 用户基础信息 | id, username, email, phone, password_hash | 主键+唯一索引(email,phone) |
| `roles` | 角色权限管理 | id, role_name, permissions | 主键+唯一索引(role_name) |
| `user_roles` | 用户角色关联 | user_id, role_id, assigned_at | 复合主键(user_id,role_id) |
| `member_levels` | 会员等级体系 | id, level_name, min_points, discount_rate | 主键+索引(min_points) |
| `member_points` | 会员积分记录 | id, user_id, current_points, total_earned | 主键+索引(user_id) |
| `point_transactions` | 积分变动明细 | id, user_id, transaction_type, points_change | 主键+复合索引(user_id,created_at) |

#### 2. 商品域数据表

| 表名 | 主要职责 | 核心字段 | 索引策略 |
|------|---------|---------|---------|
| `categories` | 商品分类层次 | id, name, parent_id, level, path | 主键+索引(parent_id,level) |
| `brands` | 商品品牌 | id, name, slug, logo_url | 主键+唯一索引(slug) |
| `products` | 商品基础信息 | id, name, brand_id, category_id, status | 主键+复合索引(category_id,status) |
| `skus` | 商品规格定价 | id, product_id, sku_code, price, weight | 主键+唯一索引(sku_code) |
| `product_attributes` | 商品属性扩展 | id, product_id, attribute_name, attribute_value | 复合索引(product_id,attribute_name) |
| `sku_attributes` | SKU属性扩展 | id, sku_id, attribute_name, attribute_value | 复合索引(sku_id,attribute_name) |
| `product_images` | 商品图片 | id, product_id, image_url, sort_order | 复合索引(product_id,sort_order) |
| `inventory` | SKU库存数量 | id, sku_id, available_quantity, reserved_quantity | 主键+唯一索引(sku_id) |
| `inventory_transactions` | 库存变动记录 | id, sku_id, transaction_type, quantity_change | 复合索引(sku_id,created_at) |

#### 3. 交易域数据表

| 表名 | 主要职责 | 核心字段 | 索引策略 |
|------|---------|---------|---------|
| `shopping_carts` | 购物车主表 | id, user_id, status, expires_at | 主键+索引(user_id,status) |
| `cart_items` | 购物车商品项 | id, cart_id, sku_id, quantity, unit_price | 复合索引(cart_id,sku_id) |
| `orders` | 订单主表 | id, order_number, user_id, status, total_amount | 主键+复合索引(user_id,status) |
| `order_items` | 订单商品明细 | id, order_id, sku_id, quantity, unit_price | 复合索引(order_id,sku_id) |
| `order_status_history` | 订单状态历史 | id, order_id, old_status, new_status | 复合索引(order_id,created_at) |
| `payments` | 支付记录 | id, order_id, payment_method, amount, status | 复合索引(order_id,status) |
| `refunds` | 退款记录 | id, payment_id, refund_amount, status | 复合索引(payment_id,status) |

#### 4. 营销域数据表

| 表名 | 主要职责 | 核心字段 | 索引策略 |
|------|---------|---------|---------|
| `coupons` | 优惠券管理 | id, coupon_code, discount_type, discount_value | 主键+唯一索引(coupon_code) |
| `user_coupons` | 用户优惠券 | id, user_id, coupon_id, status, expires_at | 复合索引(user_id,status) |
| `group_buys` | 拼团活动 | id, product_id, required_count, current_count | 索引(product_id,status) |
| `group_buy_participants` | 拼团参与者 | id, group_buy_id, user_id, joined_at | 复合索引(group_buy_id,user_id) |
| `distributors` | 分销商管理 | id, user_id, level, commission_rate | 主键+索引(user_id) |
| `commissions` | 佣金记录 | id, distributor_id, order_id, commission_amount | 复合索引(distributor_id,order_id) |
| `social_shares` | 社交分享 | id, user_id, content_type, content_id, platform | 复合索引(user_id,content_type) |
| `referrals` | 邀请推荐 | id, referrer_id, referee_id, reward_amount | 复合索引(referrer_id,referee_id) |

#### 5. 农产品域数据表

| 表名 | 主要职责 | 核心字段 | 索引策略 |
|------|---------|---------|---------|
| `suppliers` | 供应商信息 | id, company_name, contact_person, status | 主键+索引(status) |
| `supplier_products` | 供应商商品 | id, supplier_id, product_id, supply_price | 复合索引(supplier_id,product_id) |
| `batches` | 生产批次 | id, batch_code, product_id, production_date | 主键+唯一索引(batch_code) |
| `trace_records` | 溯源记录 | id, batch_id, stage_type, operator, timestamp | 复合索引(batch_id,timestamp) |
| `certificates` | 质量认证 | id, batch_id, cert_type, cert_number | 复合索引(batch_id,cert_type) |
| `quality_reports` | 质检报告 | id, batch_id, test_type, test_result | 复合索引(batch_id,test_type) |
| `shipments` | 物流配送 | id, order_id, tracking_number, status | 复合索引(order_id,status) |
| `delivery_routes` | 配送路线 | id, shipment_id, location, temperature | 复合索引(shipment_id,timestamp) |

#### 6. 平台域数据表

| 表名 | 主要职责 | 核心字段 | 索引策略 |
|------|---------|---------|---------|
| `notifications` | 通知消息 | id, user_id, type, title, content, status | 复合索引(user_id,status) |
| `customer_tickets` | 客服工单 | id, user_id, category, status, priority | 复合索引(user_id,status) |
| `faq_articles` | FAQ知识库 | id, category, question, answer, view_count | 索引(category,view_count) |
| `risk_events` | 风控事件 | id, user_id, event_type, risk_score | 复合索引(user_id,event_type) |
| `analytics_events` | 用户行为事件 | id, user_id, event_type, event_data | 复合索引(user_id,created_at) |
| `recommendation_logs` | 推荐记录 | id, user_id, item_type, item_id, score | 复合索引(user_id,item_type) |

## 数据模型设计规范

### ORM基础架构

```python
# 统一Base类设计
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, comment="主键ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

class SoftDeleteMixin:
    """软删除混入类"""
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

class TimestampMixin:
    """时间戳混入类"""
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
```

### 外键约束策略

```python
# 外键约束设计原则
class Order(BaseModel):
    __tablename__ = 'orders'
    
    # 核心业务外键 - 使用SET NULL保护数据
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), comment="用户ID")
    
    # 从属关系外键 - 使用CASCADE保持一致性  
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(BaseModel):
    __tablename__ = 'order_items'
    
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), comment="订单ID")
    sku_id = Column(Integer, ForeignKey('skus.id', ondelete='SET NULL'), comment="SKU ID")
```

### 索引设计策略

```python
# 索引设计规范
from sqlalchemy import Index

class User(BaseModel):
    __tablename__ = 'users'
    
    username = Column(String(50), unique=True, comment="用户名")
    email = Column(String(100), unique=True, comment="邮箱")
    phone = Column(String(20), unique=True, comment="手机号")
    
    # 复合索引设计
    __table_args__ = (
        Index('idx_user_email_status', 'email', 'status'),  # 登录查询优化
        Index('idx_user_phone_status', 'phone', 'status'),  # 手机登录优化
        Index('idx_user_created_at', 'created_at'),         # 时间范围查询
    )
```

## 数据一致性设计

### 事务边界设计

```python
# 事务管理策略
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

@contextmanager
def transaction_scope():
    """数据库事务上下文管理器"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 业务事务示例
async def create_order_with_payment(order_data, payment_data):
    """创建订单并处理支付 - 强一致性事务"""
    with transaction_scope() as session:
        # 1. 创建订单
        order = Order(**order_data)
        session.add(order)
        session.flush()  # 获取订单ID
        
        # 2. 减库存
        for item in order_data['items']:
            inventory = session.query(Inventory).filter_by(sku_id=item['sku_id']).first()
            inventory.available_quantity -= item['quantity']
        
        # 3. 创建支付记录
        payment = Payment(order_id=order.id, **payment_data)
        session.add(payment)
        
        return order, payment
```

### 跨模块数据一致性

```python
# 事件驱动的最终一致性
from typing import Dict, Any
import asyncio

class EventBus:
    """事件总线 - 处理模块间数据一致性"""
    
    async def publish_order_created(self, order_id: int, user_id: int):
        """订单创建事件 - 触发相关业务处理"""
        await asyncio.gather(
            self._update_user_points(user_id, order_id),      # 更新积分
            self._send_notification(user_id, order_id),       # 发送通知  
            self._update_analytics(user_id, order_id),        # 更新统计
        )
    
    async def _update_user_points(self, user_id: int, order_id: int):
        """异步更新用户积分"""
        # 会员系统处理积分增加
        pass
    
    async def _send_notification(self, user_id: int, order_id: int):
        """异步发送订单通知"""
        # 通知服务处理消息推送
        pass
```

## 性能优化策略

### 缓存架构设计

```python
# Redis缓存策略
import redis
import json
from typing import Optional, Any

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # 用户信息缓存 - 1小时过期
    async def get_user(self, user_id: int) -> Optional[Dict]:
        key = f"user:{user_id}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    # 商品信息缓存 - 24小时过期  
    async def get_product(self, product_id: int) -> Optional[Dict]:
        key = f"product:{product_id}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    # 库存缓存 - 实时更新
    async def get_inventory(self, sku_id: int) -> Optional[int]:
        key = f"inventory:{sku_id}"
        return self.redis_client.get(key)
```

### 分库分表策略

```python
# 数据分片策略 (为微服务演进准备)
class ShardingStrategy:
    """数据分片策略"""
    
    @staticmethod
    def get_user_shard(user_id: int) -> str:
        """用户数据分片 - 按用户ID哈希"""
        shard_index = user_id % 4  # 4个分片
        return f"user_shard_{shard_index}"
    
    @staticmethod  
    def get_order_shard(order_date: str) -> str:
        """订单数据分片 - 按日期分片"""
        return f"order_{order_date.replace('-', '')}"
```

## 数据安全与合规

### 数据加密存储

```python
# 敏感数据加密
from cryptography.fernet import Fernet
import hashlib

class DataEncryption:
    """数据加密工具"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希存储"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def encrypt_sensitive_data(data: str, key: bytes) -> str:
        """敏感信息加密存储"""
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()

# 数据模型应用
class User(BaseModel):
    __tablename__ = 'users'
    
    phone = Column(String(200), comment="手机号(加密存储)")  # 加密存储
    password_hash = Column(String(64), comment="密码哈希")   # 哈希存储
    id_card = Column(String(200), comment="身份证号(加密存储)")  # 加密存储
```

### 审计日志设计

```python
# 数据变更审计
class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    table_name = Column(String(50), comment="表名")
    record_id = Column(Integer, comment="记录ID")
    operation = Column(String(10), comment="操作类型(INSERT/UPDATE/DELETE)")
    old_values = Column(Text, comment="变更前数据(JSON)")
    new_values = Column(Text, comment="变更后数据(JSON)")
    user_id = Column(Integer, comment="操作用户ID")
    ip_address = Column(String(45), comment="操作IP")
    user_agent = Column(String(500), comment="用户代理")
```

## 农产品电商特色数据

### 区块链溯源数据

```python
# 区块链存证数据模型
class BlockchainRecord(BaseModel):
    __tablename__ = 'blockchain_records'
    
    batch_id = Column(Integer, ForeignKey('batches.id'), comment="批次ID")
    transaction_hash = Column(String(66), unique=True, comment="区块链交易哈希")
    block_number = Column(Integer, comment="区块号")
    ipfs_hash = Column(String(46), comment="IPFS存储哈希")
    data_type = Column(String(20), comment="数据类型(生产/检测/运输)")
    timestamp = Column(DateTime, comment="上链时间")
    
    __table_args__ = (
        Index('idx_blockchain_batch_type', 'batch_id', 'data_type'),
        Index('idx_blockchain_timestamp', 'timestamp'),
    )
```

### IoT数据采集

```python
# IoT传感器数据(时序数据库存储)
class IoTSensorData:
    """IoT传感器数据模型 - InfluxDB存储"""
    
    measurement = "sensor_data"
    tags = {
        'batch_id': 'string',      # 批次ID
        'sensor_type': 'string',   # 传感器类型
        'location': 'string',      # 位置信息
    }
    fields = {
        'temperature': 'float',    # 温度
        'humidity': 'float',       # 湿度  
        'ph_value': 'float',       # PH值
        'soil_moisture': 'float',  # 土壤湿度
    }
    timestamp = 'datetime'         # 时间戳
```

## 相关文档

- [业务架构设计](business-architecture.md) - 业务领域和数据边界
- [应用架构设计](application-architecture.md) - 应用层数据访问
- [基础设施架构](infrastructure-architecture.md) - 数据库部署架构
- [数据库设计规范](../standards/database-standards.md) - 具体实现规范