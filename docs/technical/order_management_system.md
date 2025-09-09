# 订单管理系统技术文档

**版本**: 1.0.0  
**创建日期**: 2025-09-09  
**最后更新**: 2025-09-09  

## 概述

订单管理系统实现了完整的电商订单生命周期管理，包括订单创建、状态流转、库存管理、权限控制等核心功能，为Mini-MVP提供可靠的交易基础。

## 系统架构

### 核心模块
```
app/
├── api/
│   └── order_routes.py      # 订单API路由
├── models.py                # 数据模型(Order, OrderItem)
└── auth.py                  # 认证中间件集成
```

### 技术栈
- **后端框架**: FastAPI
- **数据库**: MySQL 8.0 + SQLAlchemy 2.x
- **认证**: JWT Bearer Token
- **数据验证**: Pydantic 2.x
- **API文档**: OpenAPI/Swagger

## 数据模型设计

### Order（订单表）
```python
class Order(Base):
    __tablename__ = 'orders'
    
    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 订单状态
    status = Column(String(20), nullable=False, default='pending')
    # 状态流转: pending → paid → shipped → delivered | cancelled
    
    # 金额信息
    subtotal = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    shipping_fee = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    discount_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    total_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    
    # 收货信息（JSON存储）
    shipping_address = Column(Text, nullable=True)
    remark = Column(Text, nullable=True)
    
    # 时间戳
    created_at, updated_at, paid_at, shipped_at, delivered_at
```

### OrderItem（订单项表）
```python
class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # 商品快照（防止商品信息变更影响历史订单）
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(100), nullable=False)
    
    # 交易信息
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
```

### 关系设计
```
User (1) ←→ (N) Order (1) ←→ (N) OrderItem (N) ←→ (1) Product
```

## API接口规范

### 1. 创建订单
```http
POST /api/orders
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "user_id": 31,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "shipping_address": "{\"name\":\"张三\",\"phone\":\"13800138000\",\"address\":\"北京市朝阳区测试地址123号\"}",
  "remark": "测试订单"
}
```

**响应示例**:
```json
{
  "id": 1,
  "order_no": "ORD202509091443258980F233",
  "user_id": 31,
  "status": "pending",
  "subtotal": "59.80",
  "shipping_fee": "0.00",
  "discount_amount": "0.00",
  "total_amount": "59.80",
  "shipping_address": null,
  "remark": "测试订单",
  "created_at": "2025-09-09T06:43:24",
  "updated_at": "2025-09-09T06:43:24",
  "paid_at": null,
  "shipped_at": null,
  "delivered_at": null,
  "order_items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "五常大米",
      "product_sku": "WC-RICE-001",
      "quantity": 2,
      "unit_price": "29.90",
      "total_price": "59.80"
    }
  ]
}
```

### 2. 获取订单列表
```http
GET /api/orders?status_filter=pending&limit=20&offset=0
Authorization: Bearer <jwt_token>
```

### 3. 获取订单详情
```http
GET /api/orders/{order_id}
Authorization: Bearer <jwt_token>
```

### 4. 更新订单状态
```http
PATCH /api/orders/{order_id}/status
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "status": "paid"
}
```

### 5. 取消订单
```http
DELETE /api/orders/{order_id}
Authorization: Bearer <jwt_token>
```

**响应**:
```json
{
  "message": "订单已取消",
  "order_id": 1
}
```

### 6. 获取订单商品列表
```http
GET /api/orders/{order_id}/items
Authorization: Bearer <jwt_token>
```

## 业务逻辑规则

### 订单创建流程
1. **权限验证**: 用户只能为自己创建订单（管理员例外）
2. **用户验证**: 验证目标用户存在且有效
3. **商品验证**: 验证所有商品存在、状态为active、库存充足
4. **金额计算**: 自动计算小计、运费、优惠、总金额
5. **订单生成**: 生成唯一订单号（ORD+时间戳+随机码）
6. **库存扣减**: 自动减少商品库存
7. **订单项创建**: 创建商品快照记录

### 订单状态流转
```
pending (待付款)
    ↓ 支付完成
paid (已付款)
    ↓ 商家发货
shipped (已发货)
    ↓ 用户确认收货
delivered (已完成)

pending → cancelled (取消订单，任何时候)
```

**状态转换规则**:
- `pending` → `paid`, `cancelled`
- `paid` → `shipped`, `cancelled`
- `shipped` → `delivered`
- `delivered` → 无法变更（终态）
- `cancelled` → 无法变更（终态）

### 库存管理机制
- **下单时**: 立即扣减商品库存 `Product.stock_quantity -= quantity`
- **取消时**: 恢复商品库存 `Product.stock_quantity += quantity`
- **校验规则**: 下单前检查 `product.stock_quantity >= item.quantity`
- **状态联动**: 库存为0时商品状态自动切换为 `out_of_stock`

### 权限控制策略
- **普通用户**: 只能查看和管理自己的订单
- **管理员**: 可以查看和管理所有用户的订单
- **订单创建**: 只能为自己创建订单（管理员可为任何人创建）
- **状态更新**: 只有管理员可以更新订单状态

## 安全特性

### 数据完整性
- **商品快照**: 订单创建时保存商品名称、SKU、价格快照
- **外键约束**: 确保数据关系完整性
- **事务一致性**: 订单创建使用数据库事务保证原子性

### 业务安全
- **库存防超卖**: 下单前严格校验库存充足性
- **权限隔离**: 用户只能访问自己的订单数据
- **状态验证**: 严格的订单状态流转规则
- **金额校验**: 服务端重新计算所有金额，不信任客户端

### 输入验证
- **商品存在性**: 验证product_id有效且商品状态为active
- **数量合法性**: quantity > 0
- **订单项非空**: 至少包含一个商品
- **状态格式**: 状态值必须符合预定义枚举

## 数据库索引优化

### 核心索引
```sql
-- orders表
CREATE INDEX idx_user_status ON orders(user_id, status);
CREATE INDEX idx_status_created ON orders(status, created_at);
CREATE INDEX idx_order_no ON orders(order_no);

-- order_items表
CREATE INDEX idx_order_product ON order_items(order_id, product_id);
```

### 查询优化
- **用户订单列表**: `idx_user_status` 支持用户+状态过滤
- **订单时间排序**: `idx_status_created` 支持状态+时间排序
- **订单号查询**: `idx_order_no` 支持订单号快速查找
- **订单详情**: `idx_order_product` 支持订单项快速加载

## 错误处理

### 业务异常
```python
# 商品不存在
HTTP 404: "商品ID {product_id} 不存在"

# 商品已下架
HTTP 400: "商品 {product.name} 已下架"

# 库存不足
HTTP 400: "商品 {product.name} 库存不足，当前库存：{stock}"

# 权限不足
HTTP 403: "只能为自己创建订单"
HTTP 403: "无权访问此订单"

# 状态转换错误
HTTP 400: "订单状态不能从 {old_status} 变更为 {new_status}"
```

### 系统异常
- 数据库连接异常自动重试
- 事务回滚确保数据一致性
- 详细错误日志便于问题排查

## 测试用例

### 功能测试
```powershell
# 1. 创建订单
$orderBody = @{
  user_id = 31
  items = @(@{product_id = 1; quantity = 2})
  remark = "测试订单"
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8000/api/orders" -Method POST -Body $orderBody -ContentType "application/json" -Headers $headers

# 2. 查询订单
Invoke-RestMethod -Uri "http://localhost:8000/api/orders" -Method GET -Headers $headers

# 3. 取消订单
Invoke-RestMethod -Uri "http://localhost:8000/api/orders/1" -Method DELETE -Headers $headers
```

### 验证检查点
- ✅ 订单创建成功，自动生成订单号
- ✅ 金额计算正确 (2 * ¥29.90 = ¥59.80)
- ✅ 库存自动扣减 (100 → 98)
- ✅ 订单状态正确 (pending)
- ✅ 订单取消成功，库存恢复 (98 → 100)
- ✅ 权限控制有效

## 性能考虑

### 查询优化
- 订单列表默认限制20条，支持分页
- 使用索引优化常用查询路径
- 订单项使用延迟加载减少不必要的联表查询

### 并发处理
- 数据库行锁防止库存超卖
- 事务隔离级别确保数据一致性
- TODO: Redis分布式锁进一步增强并发安全

### 扩展性设计
- 金额字段预留运费和优惠计算
- 收货地址JSON存储支持灵活扩展
- 订单备注支持用户个性化需求
- 预留管理员权限扩展点

## 下一步开发计划

### 短期扩展（本期）
1. **购物车功能** - Redis临时存储
2. **库存预占机制** - Redis分布式锁防超卖
3. **幂等性支持** - idempotency_key机制
4. **支付集成** - 微信支付模拟接口

### 中期扩展
1. **订单批量操作** - 批量发货、批量取消
2. **订单搜索** - 按商品名、订单号、时间范围搜索
3. **订单导出** - CSV/Excel格式导出
4. **库存预警** - 低库存自动通知

### 长期扩展
1. **订单工作流** - 可配置的状态流转规则
2. **促销集成** - 优惠券、满减、折扣计算
3. **物流集成** - 快递单号、物流跟踪
4. **订单分析** - 销售报表、趋势分析

## 维护注意事项

1. **数据一致性**: 定期检查订单金额计算和库存同步
2. **性能监控**: 关注订单查询响应时间和数据库连接池
3. **安全审计**: 定期检查权限控制和数据访问日志
4. **备份策略**: 订单数据为核心业务数据，需要可靠备份
5. **版本兼容**: API变更需要考虑向后兼容性

---

**文档维护**: 此文档应随代码变更同步更新  
**审核周期**: 每次功能迭代后更新
