# 订单管理模块 (Order Management Module)

## 模块概述

订单管理模块负责订单创建、状态流转、支付集成、履约跟踪和售后服务。支持多渠道订单、分布式事务、事件驱动状态同步。

### 主要功能

1. **订单创建与管理**
   - 订单生成（购物车结算、直接购买）
   - 订单状态流转（待支付、已支付、已发货、已完成、已取消、售后中）
   - 多渠道订单（PC、移动、API、第三方平台）
   - 订单拆分与合并

2. **支付集成**
   - 多支付方式（支付宝、微信、银联、PayPal）
   - 支付状态回调
   - 支付安全校验
   - 退款处理

3. **履约跟踪**
   - 发货管理
   - 物流跟踪
   - 配送状态同步
   - 异常处理（丢件、延迟、拒收）

4. **售后服务**
   - 退货/换货申请
   - 售后状态流转
   - 售后审核与处理
   - 售后退款

## 技术架构

### 核心组件

```
order-management/
├── controllers/
│   ├── order_controller.py      # 订单控制器
│   ├── payment_controller.py    # 支付控制器
│   └── fulfillment_controller.py # 履约控制器
├── services/
│   ├── order_service.py         # 订单业务逻辑
│   ├── payment_service.py       # 支付集成服务
│   ├── fulfillment_service.py   # 履约服务
│   └── aftersales_service.py    # 售后服务
├── models/
│   ├── order.py                 # 订单模型
│   ├── order_item.py            # 订单项模型
│   ├── payment.py               # 支付模型
│   ├── shipment.py              # 发货模型
│   └── aftersales.py            # 售后模型
├── events/
│   ├── order_events.py          # 订单事件
│   └── payment_events.py        # 支付事件
└── utils/
    ├── transaction_utils.py     # 分布式事务工具
    └── event_utils.py           # 事件工具
```

### 数据库设计

```sql
-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_fee DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE,
    shipped_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    aftersales_status VARCHAR(20) DEFAULT 'none'
);

-- 订单项表
CREATE TABLE order_items (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    sku_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    refund_status VARCHAR(20) DEFAULT 'none',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 支付表
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    payment_method VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100),
    paid_at TIMESTAMP WITH TIME ZONE,
    refunded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 发货表
CREATE TABLE shipments (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    carrier VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    shipped_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 售后表
CREATE TABLE aftersales (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL, -- 'refund', 'exchange', 'return'
    status VARCHAR(20) NOT NULL,
    reason TEXT,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);
```

## API 接口

### 订单操作

```yaml
/api/v1/orders:
  POST /:
    summary: 创建订单
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/OrderCreateRequest'
    responses:
      201:
        description: 订单创建成功
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Order'
      400:
        description: 请求参数错误
      409:
        description: 库存不足

  GET /{order_id}:
    summary: 获取订单详情
    security:
      - BearerAuth: []
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 订单详情
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Order'
      404:
        description: 订单不存在

  PUT /{order_id}/cancel:
    summary: 取消订单
    security:
      - BearerAuth: []
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 订单取消成功
      404:
        description: 订单不存在
      409:
        description: 订单不可取消

  POST /{order_id}/pay:
    summary: 订单支付
    security:
      - BearerAuth: []
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              payment_method:
                type: string
                enum: [alipay, wechat, unionpay, paypal]
    responses:
      200:
        description: 支付成功
      400:
        description: 支付参数错误
      409:
        description: 支付失败

  POST /{order_id}/refund:
    summary: 订单退款
    security:
      - BearerAuth: []
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              reason:
                type: string
    responses:
      200:
        description: 退款成功
      400:
        description: 退款参数错误
      409:
        description: 退款失败
```

## 订单状态流转

```mermaid
stateDiagram-v2
    [*] --> 待支付
    待支付 --> 已支付: 支付成功
    已支付 --> 已发货: 发货
    已发货 --> 已完成: 用户确认收货
    已发货 --> 售后中: 售后申请
    已支付 --> 已取消: 用户/系统取消
    已发货 --> 已取消: 拒收/丢件
    售后中 --> 已完成: 售后处理完成
    售后中 --> 已取消: 售后失败
```

## 分布式事务

- Saga模式：订单与库存、支付、物流等服务的分布式一致性
- 事件驱动：订单状态变更通过事件总线同步到各服务
- 补偿机制：失败时自动回滚相关操作

## 监控指标

### 业务指标

- 订单创建量
- 支付成功率
- 发货及时率
- 售后处理时长

### 技术指标

- API响应时间
- 分布式事务成功率
- 事件处理延迟
- 数据库慢查询

### 异常指标

- 订单取消率
- 支付失败率
- 售后失败率
- 物流异常率

## 部署配置

### 环境变量

```bash
# 数据库配置
ORDER_DB_URL=postgresql://user:pass@localhost/order_db

# 支付服务配置
PAYMENT_GATEWAY_URL=https://payment.example.com
PAYMENT_TIMEOUT=10

# 物流服务配置
FULFILLMENT_SERVICE_URL=http://fulfillment-service:8080
FULFILLMENT_TIMEOUT=5

# 消息队列配置
ORDER_EVENT_BROKER=redis://localhost:6379/3
ORDER_EVENT_TOPIC=order.events
```

### 依赖服务

- PostgreSQL (订单数据存储)
- Redis (事件队列)
- 支付网关 (支付集成)
- 物流服务 (履约跟踪)
- 用户服务 (用户信息)
- 商品服务 (商品信息)

## 相关文档

- [购物车模块](../shopping-cart/overview.md)
- [支付集成](../payment/overview.md)
- [事件架构](../../architecture/event-driven.md)
- [分布式事务](../../architecture/distributed-transactions.md)
