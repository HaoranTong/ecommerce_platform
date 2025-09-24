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

### 数据存储架构策略

```
┌─────────────────────────────────────────────────────────────────┐
│                      数据存储架构分层                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  主数据存储  │  │  缓存存储   │  │  搜索存储   │  │  文件存储   │ │
│  │ 关系型数据库 │  │ 内存数据库  │  │ 全文搜索引擎 │  │ 对象存储服务 │ │
│  │ ACID事务保证 │  │ 高速缓存    │  │ 复杂查询    │  │ CDN分发     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  消息存储   │  │  区块链存储  │  │  时序存储   │  │  向量存储   │ │
│  │ 异步消息队列 │  │ 防篡改存证  │  │ 时间序列数据 │  │ AI模型数据  │ │
│  │ 削峰填谷    │  │ 溯源记录    │  │ IoT传感器   │  │ 相似度搜索  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

> **具体技术选型和版本**: 详见 [系统技术栈设计](../design/system/technology-stack.md)

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

### ORM架构设计原则

#### 统一基础模型原则
- **基础类抽象**: 定义通用的基础模型类，包含标准字段和行为
- **混入类设计**: 通过混入类提供可复用的功能特性
- **时间戳标准**: 统一的创建时间和更新时间管理
- **软删除支持**: 支持逻辑删除以保护历史数据

#### 基础模型设计要求
- **主键策略**: 统一使用自增整型主键
- **注释规范**: 所有表和字段必须包含完整的中文注释
- **抽象基类**: 定义抽象基类避免重复代码
- **扩展性设计**: 预留扩展字段和扩展机制

### 外键约束设计原则

#### 约束策略分类
- **核心业务关系**: 使用SET NULL保护核心业务数据完整性
- **从属关系**: 使用CASCADE保持主从数据一致性
- **引用关系**: 使用RESTRICT防止意外删除被引用数据
- **历史关系**: 保留历史关联避免数据孤岛

#### 外键设计规范
- **删除策略**: 根据业务关系选择合适的ON DELETE策略
- **更新策略**: 合理设置ON UPDATE行为
- **性能考虑**: 平衡数据完整性和查询性能
- **微服务准备**: 考虑未来服务拆分对外键的影响

### 索引设计策略

#### 索引设计原则  
- **查询优化**: 基于实际查询模式设计索引
- **复合索引**: 合理使用复合索引提升查询效率
- **唯一约束**: 通过唯一索引保证数据唯一性
- **性能平衡**: 平衡查询性能和写入性能

#### 索引命名规范
- **前缀标识**: 使用统一的索引命名前缀
- **字段顺序**: 复合索引按查询频率排序字段
- **业务含义**: 索引名称体现业务查询场景

> **具体ORM实现和代码**: 详见 [系统技术栈设计](../design/system/technology-stack.md) 和各模块数据库设计文档
    )
```

## 数据一致性设计

### 事务边界设计原则

#### 事务范围划分
- **单一职责**: 每个事务专注于一个业务操作的完整性
- **最小化范围**: 尽量缩小事务涉及的数据范围和持有时间
- **嵌套避免**: 避免事务嵌套导致的死锁和性能问题
- **异常回滚**: 完善的异常处理和事务回滚机制

#### 业务事务策略
- **强一致性**: 关键业务操作使用ACID事务保证数据一致性
- **补偿机制**: 长事务通过补偿事务处理异常情况
- **超时控制**: 设置合理的事务超时时间避免长时间锁定
- **隔离级别**: 根据业务需求选择合适的事务隔离级别

> **具体事务实现**: 详见 [系统技术栈设计](../design/system/technology-stack.md) 和各模块数据库设计

### 跨模块数据一致性原则

#### 一致性策略选择
- **强一致性**: 关键业务数据使用同步事务保证强一致性
- **最终一致性**: 非关键业务数据通过事件机制保证最终一致性
- **补偿一致性**: 复杂业务流程通过补偿机制保证业务一致性
- **分布式事务**: 跨系统操作使用分布式事务模式

#### 事件驱动架构
- **事件发布**: 业务操作完成后发布相关业务事件
- **异步处理**: 通过事件总线异步处理跨模块业务逻辑
- **事件溯源**: 保留完整的事件历史支持业务审计
- **幂等性**: 确保事件处理的幂等性避免重复处理

> **具体事件机制实现**: 详见 [系统集成设计](../design/system/integration-design.md)

## 性能优化策略

### 缓存架构策略

#### 缓存分层设计
- **应用缓存**: 应用层内存缓存提升计算性能
- **分布式缓存**: 跨实例共享的分布式缓存系统
- **数据库缓存**: 数据库层查询结果缓存
- **CDN缓存**: 静态资源的全球分发缓存

#### 缓存策略原则
- **数据分类**: 根据数据特性选择不同的缓存策略
- **过期策略**: 设置合理的缓存过期时间和刷新策略
- **一致性保证**: 缓存与数据库的一致性维护机制
- **热点识别**: 识别热点数据优化缓存命中率

#### 缓存使用场景
- **用户信息**: 频繁访问的用户基础信息
- **商品数据**: 商品详情和库存信息
- **配置数据**: 系统配置和业务规则数据
- **计算结果**: 复杂计算和统计结果数据

> **具体缓存实现**: 详见 [系统性能设计](../design/system/performance-design.md)

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
### 数据安全架构

#### 数据加密策略
- **传输加密**: 数据传输过程中的端到端加密保护
- **存储加密**: 敏感数据的加密存储和访问控制
- **字段级加密**: 对特定敏感字段进行独立加密
- **密钥管理**: 安全的加密密钥生成、存储和轮换

#### 数据脱敏原则
- **分级脱敏**: 根据数据敏感级别采用不同脱敏策略
- **动态脱敏**: 运行时根据用户权限动态脱敏显示
- **测试环境**: 测试和开发环境使用脱敏数据
- **日志保护**: 确保日志中不包含敏感信息

### 审计追踪架构

#### 审计数据策略
- **操作记录**: 记录所有数据变更操作的完整信息
- **用户追踪**: 追踪操作用户、时间、IP等上下文信息
- **数据变更**: 记录变更前后的数据状态对比
- **业务审计**: 记录关键业务操作的审计轨迹

#### 审计日志管理
- **日志分类**: 按操作类型和重要程度分类存储
- **保留策略**: 设置合理的日志保留期限和归档策略
- **查询优化**: 优化审计日志的查询和分析性能
- **合规要求**: 满足行业合规和监管要求

> **具体数据安全实现**: 详见 [系统安全设计](../design/system/security-design.md)

## 农产品电商特色数据架构

### 区块链溯源数据架构

#### 溯源数据策略
- **链上存证**: 关键溯源信息上链确保数据不可篡改
- **链下存储**: 详细数据通过分布式存储保存并链上存证哈希
- **数据分类**: 按生产、检测、运输等环节分类存储溯源数据
- **实时同步**: 溯源数据实时同步到区块链网络

#### 区块链集成原则
- **混合架构**: 结合公有链和联盟链优势设计溯源系统
- **成本优化**: 平衡数据完整性和区块链交易成本
- **查询效率**: 设计高效的溯源数据查询和验证机制
- **标准兼容**: 遵循农产品溯源行业标准和规范

### IoT数据采集架构

#### 时序数据策略
- **实时采集**: 农业IoT设备实时采集环境和生产数据
- **数据分类**: 按传感器类型和数据重要性分级存储
- **压缩存储**: 使用时序数据库优化存储和查询性能
- **数据清洗**: 对IoT数据进行实时清洗和异常值过滤

#### IoT数据管理
- **设备管理**: 统一管理IoT设备注册、配置和状态监控
- **数据质量**: 确保IoT数据的准确性和完整性
- **边缘计算**: 在边缘节点进行数据预处理和分析
- **数据融合**: 将IoT数据与业务数据进行关联分析

> **具体区块链和IoT实现**: 详见相关模块设计文档

## 相关文档

- [业务架构设计](business-architecture.md) - 业务领域和数据边界
- [应用架构设计](application-architecture.md) - 应用层数据访问
- [基础设施架构](infrastructure-architecture.md) - 数据库部署架构
- [数据库设计规范](../standards/database-standards.md) - 具体实现规范
