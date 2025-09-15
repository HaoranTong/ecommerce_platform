<!--
文档说明：
- 内容：订单管理模块的功能需求定义，包括业务规则、数据要求和接口需求
- 使用方法：开发订单模块时的需求规范，设计阶段的输入文档
- 更新方法：业务需求变更时更新，需要产品负责人确认
- 引用关系：被design.md和implementation.md引用，引用系统业务需求文档
- 更新频率：业务需求变化时
-->

# 订单管理模块需求规范

📝 **状态**: ✅ 已发布  
📅 **创建日期**: 2025-01-27  
👤 **负责人**: 产品架构师  
🔄 **最后更新**: 2025-01-27  
📋 **版本**: v1.0.0  

## 业务背景

### 模块定位
订单管理模块是电商平台的核心交易模块，负责管理从购物车到订单完成的完整业务流程。在农产品电商场景下，需要特别支持批次溯源、冷链物流等特殊需求。

### 业务价值
1. **交易闭环管理** - 完整的订单生命周期管理
2. **库存精准控制** - 实时库存扣减和恢复机制
3. **支付安全保障** - 多支付渠道和安全验证
4. **客户体验优化** - 订单状态实时跟踪和透明化

## 功能需求

### 核心功能模块

#### 1. 订单创建与管理
**优先级**: P0 (核心功能)

**功能描述**:
- 支持从购物车批量下单
- 支持单商品直接购买  
- 支持多SKU组合下单
- 订单信息完整记录和快照保存

**业务规则**:
- 下单时必须验证商品库存充足
- 下单时保存商品价格快照，避免价格变动影响
- 订单创建后自动生成唯一订单编号
- 支持订单备注信息记录

**数据要求**:
- 订单基础信息：订单号、用户ID、订单状态、金额明细
- 订单商品项：商品ID、SKU信息、数量、单价、小计
- 收货信息：收货地址、联系方式、配送要求
- 时间节点：创建时间、支付时间、发货时间、完成时间

#### 2. 订单状态流转
**优先级**: P0 (核心功能)

**功能描述**:
- 标准订单状态流转：待支付 → 已支付 → 已发货 → 已完成
- 异常流转支持：取消、退货、换货
- 状态变更历史完整记录
- 状态变更权限控制

**业务规则**:
```
状态流转规则：
- pending(待支付) → paid(已支付) | cancelled(已取消)
- paid(已支付) → shipped(已发货) | cancelled(已取消)  
- shipped(已发货) → delivered(已完成) | returned(退货中)
- delivered(已完成) → returned(退货中)
- cancelled(已取消) → [终态]
- returned(退货中) → [终态]
```

**权限要求**:
- 用户可取消待支付订单
- 管理员可操作所有状态流转
- 状态变更需记录操作人和操作原因

#### 3. 库存管理集成
**优先级**: P0 (核心功能)

**功能描述**:
- 下单时实时扣减库存
- 订单取消时自动恢复库存
- 库存不足时阻止下单
- 支持库存预占机制

**业务规则**:
- 下单成功后立即扣减库存，避免超卖
- 订单取消后30分钟内恢复库存
- 库存为0的商品不允许下单
- 库存扣减失败时整个订单创建失败

#### 4. 金额计算与管理
**优先级**: P0 (核心功能)

**功能描述**:
- 商品小计计算：数量 × 单价
- 订单总额计算：商品小计 + 运费 - 优惠金额
- 支持优惠券和促销活动
- 精确到分的金额计算

**业务规则**:
- 所有金额计算使用DECIMAL类型，精度到分
- 优惠金额不能超过商品小计
- 最终支付金额不能为负数
- 金额变更需要记录变更历史

#### 5. 收货地址管理
**优先级**: P1 (重要功能)

**功能描述**:
- 支持多收货地址管理
- 默认收货地址设置
- 地址信息验证和格式化
- 配送范围验证

**业务规则**:
- 收货地址必须包含：收货人、手机号、详细地址
- 支持地址簿功能，用户可保存常用地址
- 订单创建时地址信息快照保存
- 不在配送范围内的地址不允许下单

### 扩展功能模块

#### 6. 订单搜索与筛选  
**优先级**: P1 (重要功能)

**功能描述**:
- 按订单号精确搜索
- 按订单状态筛选
- 按时间范围查询
- 按金额范围筛选

#### 7. 订单统计与分析
**优先级**: P2 (支撑功能)

**功能描述**:
- 订单数量统计
- 销售金额统计  
- 订单状态分布
- 热销商品分析

## 非功能需求

### 性能要求
基于 [性能标准](../../standards/performance-standards.md) 的具体要求：

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **响应时间** | < 500ms | 订单创建、查询、更新操作 |
| **并发处理** | 1000个/秒 | 同时处理的订单操作数 |
| **可用性** | 99.9% | 年停机时间不超过8.76小时 |
| **数据一致性** | 100% | 库存扣减和订单状态必须一致 |

### 安全要求
基于 [安全架构](../../architecture/security.md) 的具体要求：

1. **权限控制**
   - 用户只能操作自己的订单
   - 管理员可以操作所有订单
   - 敏感操作需要二次验证

2. **数据保护**  
   - 订单金额和地址信息加密存储
   - API接口防止SQL注入和XSS攻击
   - 订单数据传输使用HTTPS加密

3. **审计要求**
   - 所有订单操作记录操作日志
   - 重要状态变更记录操作人信息
   - 异常订单操作实时告警

### 可扩展性要求

1. **数据扩展**
   - 支持千万级订单数据存储
   - 支持分表分库扩展
   - 支持历史数据归档

2. **功能扩展**
   - 预留自定义字段扩展
   - 支持第三方支付集成
   - 支持多仓库发货模式

## 集成需求

### 模块依赖关系
基于 [依赖架构](../../architecture/dependency-architecture.md) 的设计：

| 依赖模块 | 依赖类型 | 集成方式 | 说明 |
|---------|---------|---------|------|
| **用户认证模块** | 强依赖 | 直接调用 | 获取用户信息、权限验证 |
| **商品管理模块** | 强依赖 | 直接调用 | 获取商品信息、价格信息 |
| **库存管理模块** | 强依赖 | 事务调用 | 库存扣减、恢复操作 |
| **购物车模块** | 中等依赖 | 接口调用 | 获取购物车商品信息 |
| **支付服务模块** | 弱依赖 | 事件通知 | 支付结果回调通知 |
| **物流管理模块** | 弱依赖 | 异步调用 | 发货信息同步 |

### 外部系统集成

1. **支付系统集成**
   - 支持微信支付、支付宝支付
   - 支付结果异步回调处理
   - 支付安全验证和对账

2. **物流系统集成**  
   - 支持多家快递公司API
   - 物流信息实时查询
   - 配送状态自动更新

## 数据规范

### 核心数据实体
基于 [表模块映射](../../architecture/table-module-mapping.md) 的设计：

#### 订单主表 (orders)
```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(32) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    shipping_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00, 
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    shipping_address TEXT,
    shipping_method VARCHAR(50) DEFAULT 'standard',
    notes TEXT,
    remark TEXT,
    paid_at DATETIME NULL,
    shipped_at DATETIME NULL, 
    delivered_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_status (user_id, status),
    INDEX idx_status_created (status, created_at),
    INDEX idx_order_number (order_number)
);
```

#### 订单商品表 (order_items)  
```sql
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    sku_id BIGINT NOT NULL,
    sku_code VARCHAR(100) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    sku_name VARCHAR(200) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_order_product (order_id, product_id),
    INDEX idx_order_sku (order_id, sku_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
```

#### 订单状态历史表 (order_status_history)
```sql  
CREATE TABLE order_status_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    remark TEXT,
    operator_id BIGINT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_order_status (order_id, created_at),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
```

### 数据约束规范

1. **必填字段约束**
   - 订单号、用户ID、商品ID必填
   - 数量必须大于0
   - 金额必须大于等于0

2. **数据格式约束**  
   - 订单号格式：ORD + 时间戳 + 随机数  
   - 手机号格式：11位数字
   - 金额精度：小数点后2位

3. **业务逻辑约束**
   - 同一订单不能包含重复的SKU
   - 订单总金额必须等于各项金额之和
   - 订单状态变更必须符合状态流转规则

## 接口需求

### API接口规范
遵循 [API设计标准](../../standards/api-standards.md) 的统一规范：

#### 核心接口清单

| 接口路径 | HTTP方法 | 功能说明 | 权限要求 |
|---------|---------|---------|---------|
| `/api/v1/orders` | POST | 创建订单 | 用户认证 |
| `/api/v1/orders` | GET | 订单列表 | 用户认证 |
| `/api/v1/orders/{id}` | GET | 订单详情 | 用户认证+所有权 |
| `/api/v1/orders/{id}/status` | PATCH | 更新状态 | 管理员权限 |
| `/api/v1/orders/{id}` | DELETE | 取消订单 | 用户认证+所有权 |
| `/api/v1/orders/{id}/items` | GET | 订单商品 | 用户认证+所有权 |
| `/api/v1/orders/statistics` | GET | 订单统计 | 管理员权限 |

#### 请求响应格式
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功", 
  "data": {
    // 业务数据
  },
  "metadata": {
    "request_id": "req_123456789",
    "timestamp": "2025-01-27T10:00:00Z"
  }
}
```

### 事件接口规范
基于 [事件驱动架构](../../architecture/event-driven.md) 的设计：

#### 订单事件定义
```json
{
  "event_type": "Order.Created",
  "version": "1.0",
  "data": {
    "order_id": 123456,
    "order_number": "ORD202501271000001",
    "user_id": 1001,
    "total_amount": 99.99,
    "status": "pending",
    "items": [...],
    "created_at": "2025-01-27T10:00:00Z"
  }
}
```

#### 事件类型清单
- `Order.Created` - 订单创建成功
- `Order.Paid` - 订单支付完成
- `Order.Shipped` - 订单已发货
- `Order.Delivered` - 订单已完成
- `Order.Cancelled` - 订单已取消

## 验收标准

### 功能验收标准

1. **订单创建功能**
   - [ ] 支持单商品和多商品下单
   - [ ] 库存不足时正确阻止下单
   - [ ] 订单创建后库存正确扣减
   - [ ] 订单信息完整保存且格式正确

2. **订单查询功能**
   - [ ] 用户只能查看自己的订单
   - [ ] 管理员可以查看所有订单
   - [ ] 支持按多种条件筛选查询
   - [ ] 分页查询功能正常

3. **状态流转功能**
   - [ ] 状态流转规则严格执行
   - [ ] 状态变更历史完整记录
   - [ ] 权限控制正确执行
   - [ ] 异常状态正确处理

4. **集成功能**
   - [ ] 与库存模块集成正常
   - [ ] 与用户认证集成正常  
   - [ ] 与商品模块集成正常
   - [ ] 事件发布和处理正常

### 性能验收标准

1. **响应时间** - 所有接口响应时间 < 500ms
2. **并发能力** - 支持1000并发订单操作
3. **数据一致性** - 库存和订单状态100%一致
4. **可用性** - 服务可用性达到99.9%

### 安全验收标准

1. **权限控制** - 用户权限隔离100%有效
2. **数据安全** - 敏感数据加密存储
3. **接口安全** - 所有接口通过安全测试
4. **审计完整** - 重要操作100%记录日志

---

## 版本历史

| 版本 | 日期 | 变更说明 | 负责人 |
|------|------|----------|--------|
| v1.0.0 | 2025-01-27 | 初版需求规范，定义核心功能和接口 | 产品架构师 |

## 相关文档

- [系统业务需求](../../requirements/business.md) - 整体业务背景
- [功能需求规范](../../requirements/functional.md) - 系统功能需求  
- [架构设计总览](../../architecture/overview.md) - 技术架构设计
- [表模块映射](../../architecture/table-module-mapping.md) - 数据设计规范
- [API设计标准](../../standards/api-standards.md) - 接口设计规范