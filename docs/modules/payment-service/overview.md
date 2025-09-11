# 支付服务模块 (Payment Service Module)

## 模块概述

支付服务模块负责集成多种支付渠道、处理支付流程、管理支付状态、处理退款和对账。确保支付安全性、可靠性和合规性。

### 主要功能

1. **支付集成**
   - 多支付渠道集成 (支付宝、微信、银联、PayPal)
   - 统一支付接口封装
   - 支付路由策略
   - 支付降级处理

2. **支付流程管理**
   - 支付订单创建
   - 支付状态跟踪
   - 支付结果通知
   - 异步回调处理

3. **风控与安全**
   - 支付风险评估
   - 反欺诈检测
   - 支付限额控制
   - 敏感信息加密

4. **财务管理**
   - 退款处理
   - 对账管理
   - 清结算处理
   - 财务报表

## 技术架构

### 核心组件

```
payment/
├── controllers/
│   ├── payment_controller.py      # 支付控制器
│   ├── refund_controller.py       # 退款控制器
│   ├── webhook_controller.py      # 回调控制器
│   └── reconciliation_controller.py # 对账控制器
├── services/
│   ├── payment_service.py         # 支付业务逻辑
│   ├── gateway_service.py         # 网关服务
│   ├── risk_service.py            # 风控服务
│   ├── refund_service.py          # 退款服务
│   └── reconciliation_service.py  # 对账服务
├── gateways/
│   ├── base_gateway.py            # 网关基类
│   ├── alipay_gateway.py          # 支付宝网关
│   ├── wechat_gateway.py          # 微信支付网关
│   ├── unionpay_gateway.py        # 银联网关
│   └── paypal_gateway.py          # PayPal网关
├── models/
│   ├── payment.py                 # 支付模型
│   ├── refund.py                  # 退款模型
│   ├── transaction.py             # 交易模型
│   └── reconciliation.py          # 对账模型
├── events/
│   ├── payment_events.py          # 支付事件
│   └── refund_events.py           # 退款事件
└── utils/
    ├── crypto_utils.py            # 加密工具
    ├── signature_utils.py         # 签名工具
    └── currency_utils.py          # 货币工具
```

### 数据库设计

```sql
-- 支付订单表
CREATE TABLE payment_orders (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    user_id UUID NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'CNY',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    gateway VARCHAR(20) NOT NULL,
    gateway_order_id VARCHAR(100),
    gateway_transaction_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE,
    expired_at TIMESTAMP WITH TIME ZONE,
    callback_url VARCHAR(500),
    return_url VARCHAR(500),
    client_ip INET,
    user_agent TEXT,
    
    CONSTRAINT payment_amount_check CHECK (amount > 0)
);

-- 支付交易表
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY,
    payment_order_id UUID REFERENCES payment_orders(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'payment', 'refund', 'chargeback'
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    gateway VARCHAR(20) NOT NULL,
    gateway_transaction_id VARCHAR(100) UNIQUE,
    status VARCHAR(20) NOT NULL,
    raw_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 退款表
CREATE TABLE refunds (
    id UUID PRIMARY KEY,
    payment_order_id UUID REFERENCES payment_orders(id),
    refund_amount DECIMAL(12,2) NOT NULL,
    refund_reason VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    gateway_refund_id VARCHAR(100),
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT refund_amount_check CHECK (refund_amount > 0)
);

-- 支付方式配置表
CREATE TABLE payment_methods (
    id UUID PRIMARY KEY,
    method_code VARCHAR(20) UNIQUE NOT NULL,
    method_name VARCHAR(50) NOT NULL,
    gateway VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    min_amount DECIMAL(10,2) DEFAULT 0.01,
    max_amount DECIMAL(10,2),
    supported_currencies TEXT[] DEFAULT ARRAY['CNY'],
    config JSONB NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 对账记录表
CREATE TABLE reconciliation_records (
    id UUID PRIMARY KEY,
    reconciliation_date DATE NOT NULL,
    gateway VARCHAR(20) NOT NULL,
    total_count INTEGER NOT NULL DEFAULT 0,
    matched_count INTEGER NOT NULL DEFAULT 0,
    unmatched_count INTEGER NOT NULL DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    matched_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    unmatched_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(reconciliation_date, gateway)
);

-- 风控规则表
CREATE TABLE risk_rules (
    id UUID PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(20) NOT NULL, -- 'amount', 'frequency', 'location', 'device'
    conditions JSONB NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'allow', 'review', 'deny'
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 支付网关适配器

```python
# 支付网关基类
class BasePaymentGateway:
    def __init__(self, config: dict):
        self.config = config
    
    async def create_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """创建支付订单"""
        raise NotImplementedError
    
    async def query_payment(self, gateway_order_id: str) -> PaymentQueryResponse:
        """查询支付状态"""
        raise NotImplementedError
    
    async def create_refund(self, refund_request: RefundRequest) -> RefundResponse:
        """创建退款"""
        raise NotImplementedError
    
    async def verify_callback(self, callback_data: dict) -> bool:
        """验证回调签名"""
        raise NotImplementedError

# 支付宝网关实现
class AlipayGateway(BasePaymentGateway):
    def __init__(self, config: dict):
        super().__init__(config)
        self.app_id = config['app_id']
        self.private_key = config['private_key']
        self.alipay_public_key = config['alipay_public_key']
        self.gateway_url = config.get('gateway_url', 'https://openapi.alipay.com/gateway.do')
    
    async def create_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """创建支付宝支付订单"""
        biz_content = {
            "out_trade_no": payment_request.order_id,
            "total_amount": str(payment_request.amount),
            "subject": payment_request.subject,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            "notify_url": payment_request.notify_url,
            "return_url": payment_request.return_url
        }
        
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.page.pay",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "version": "1.0",
            "biz_content": json.dumps(biz_content, separators=(',', ':'))
        }
        
        # 生成签名
        sign = self._generate_sign(params)
        params['sign'] = sign
        
        # 生成支付URL
        payment_url = f"{self.gateway_url}?{self._build_query_string(params)}"
        
        return PaymentResponse(
            gateway_order_id=payment_request.order_id,
            payment_url=payment_url,
            status='created'
        )
    
    async def verify_callback(self, callback_data: dict) -> bool:
        """验证支付宝回调签名"""
        sign = callback_data.pop('sign', '')
        sign_type = callback_data.pop('sign_type', '')
        
        if sign_type != 'RSA2':
            return False
        
        # 参数排序并生成待签名字符串
        sorted_params = sorted(callback_data.items())
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params if v])
        
        # 验证签名
        return self._verify_sign(sign_string, sign)

# 微信支付网关实现
class WechatPayGateway(BasePaymentGateway):
    def __init__(self, config: dict):
        super().__init__(config)
        self.mch_id = config['mch_id']
        self.app_id = config['app_id']
        self.api_key = config['api_key']
        self.gateway_url = config.get('gateway_url', 'https://api.mch.weixin.qq.com')
    
    async def create_payment(self, payment_request: PaymentRequest) -> PaymentResponse:
        """创建微信支付订单"""
        params = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'body': payment_request.subject,
            'out_trade_no': payment_request.order_id,
            'total_fee': int(payment_request.amount * 100),  # 转为分
            'spbill_create_ip': payment_request.client_ip,
            'notify_url': payment_request.notify_url,
            'trade_type': 'NATIVE',  # 扫码支付
        }
        
        # 生成签名
        params['sign'] = self._generate_wechat_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        # 调用微信API
        response = await self._make_request(
            f"{self.gateway_url}/pay/unifiedorder", 
            xml_data
        )
        
        response_data = self._xml_to_dict(response)
        
        if response_data.get('return_code') == 'SUCCESS' and response_data.get('result_code') == 'SUCCESS':
            return PaymentResponse(
                gateway_order_id=response_data['prepay_id'],
                payment_url=response_data['code_url'],  # 二维码URL
                status='created'
            )
        else:
            raise PaymentError(response_data.get('err_code_des', 'Unknown error'))
```

## API 接口

### 支付操作

```yaml
/api/v1/payments:
  POST /:
    summary: 创建支付订单
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              order_id:
                type: string
                format: uuid
              payment_method:
                type: string
                enum: [alipay, wechat, unionpay, paypal]
              amount:
                type: number
                format: decimal
                minimum: 0.01
              currency:
                type: string
                default: CNY
              return_url:
                type: string
                format: uri
    responses:
      201:
        description: 支付订单创建成功
        content:
          application/json:
            schema:
              type: object
              properties:
                payment_id:
                  type: string
                  format: uuid
                payment_url:
                  type: string
                  format: uri
                qr_code:
                  type: string
                  description: 二维码内容（微信支付）

  GET /{payment_id}:
    summary: 查询支付状态
    security:
      - BearerAuth: []
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 支付状态
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PaymentStatus'

  POST /{payment_id}/cancel:
    summary: 取消支付
    security:
      - BearerAuth: []
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 取消成功

  POST /{payment_id}/refund:
    summary: 申请退款
    security:
      - BearerAuth: []
    parameters:
      - name: payment_id
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
              refund_amount:
                type: number
                format: decimal
                minimum: 0.01
              refund_reason:
                type: string
                maxLength: 200
    responses:
      201:
        description: 退款申请成功
        content:
          application/json:
            schema:
              type: object
              properties:
                refund_id:
                  type: string
                  format: uuid
                status:
                  type: string
```

### 支付回调

```yaml
/api/v1/payments/webhooks:
  POST /{gateway}/notify:
    summary: 支付网关回调通知
    parameters:
      - name: gateway
        in: path
        required: true
        schema:
          type: string
          enum: [alipay, wechat, unionpay, paypal]
    requestBody:
      required: true
      content:
        application/x-www-form-urlencoded:
          schema:
            type: object
        application/json:
          schema:
            type: object
        application/xml:
          schema:
            type: string
    responses:
      200:
        description: 回调处理成功
        content:
          text/plain:
            schema:
              type: string
              example: "success"
```

## 业务逻辑

### 支付流程服务

```python
class PaymentService:
    def __init__(self, db, gateway_manager, event_publisher, risk_service):
        self.db = db
        self.gateway_manager = gateway_manager
        self.event_publisher = event_publisher
        self.risk_service = risk_service
    
    async def create_payment(self, payment_request: PaymentCreateRequest) -> PaymentResult:
        """
        创建支付订单
        1. 风险评估
        2. 创建支付订单
        3. 调用支付网关
        4. 返回支付信息
        """
        # 1. 风险评估
        risk_result = await self.risk_service.assess_payment_risk(payment_request)
        
        if risk_result.action == 'deny':
            raise PaymentRiskError("支付被风控系统拒绝")
        elif risk_result.action == 'review':
            # 标记为需要人工审核
            payment_request.requires_review = True
        
        # 2. 创建支付订单
        payment_order = await self.db.create_payment_order(
            order_id=payment_request.order_id,
            user_id=payment_request.user_id,
            payment_method=payment_request.payment_method,
            amount=payment_request.amount,
            currency=payment_request.currency,
            gateway=self._select_gateway(payment_request.payment_method),
            callback_url=payment_request.callback_url,
            return_url=payment_request.return_url,
            client_ip=payment_request.client_ip,
            user_agent=payment_request.user_agent
        )
        
        # 3. 如果需要审核，暂停处理
        if payment_request.requires_review:
            await self.db.update_payment_status(payment_order.id, 'review')
            return PaymentResult(
                payment_id=payment_order.id,
                status='review',
                message="支付订单需要人工审核"
            )
        
        # 4. 调用支付网关
        gateway = self.gateway_manager.get_gateway(payment_order.gateway)
        
        try:
            gateway_response = await gateway.create_payment(PaymentRequest(
                order_id=str(payment_order.id),
                amount=payment_order.amount,
                subject=f"订单支付-{payment_request.order_id}",
                notify_url=f"{self.base_url}/api/v1/payments/webhooks/{payment_order.gateway}/notify",
                return_url=payment_request.return_url,
                client_ip=payment_request.client_ip
            ))
            
            # 5. 更新支付订单
            await self.db.update_payment_order(
                payment_order.id,
                gateway_order_id=gateway_response.gateway_order_id,
                status='created'
            )
            
            # 6. 发布事件
            await self.event_publisher.publish('payment.created', {
                'payment_id': str(payment_order.id),
                'order_id': payment_request.order_id,
                'amount': float(payment_order.amount),
                'payment_method': payment_order.payment_method
            })
            
            return PaymentResult(
                payment_id=payment_order.id,
                payment_url=gateway_response.payment_url,
                qr_code=gateway_response.qr_code,
                status='created'
            )
            
        except Exception as e:
            await self.db.update_payment_status(payment_order.id, 'failed')
            raise PaymentGatewayError(f"支付网关调用失败: {str(e)}")
    
    async def handle_payment_callback(self, gateway: str, callback_data: dict) -> bool:
        """
        处理支付回调
        1. 验证回调签名
        2. 更新支付状态
        3. 通知订单系统
        """
        gateway_instance = self.gateway_manager.get_gateway(gateway)
        
        # 1. 验证签名
        if not await gateway_instance.verify_callback(callback_data):
            logger.error(f"Invalid callback signature from {gateway}: {callback_data}")
            return False
        
        # 2. 解析回调数据
        payment_info = self._parse_callback_data(gateway, callback_data)
        
        # 3. 查找支付订单
        payment_order = await self.db.get_payment_order_by_gateway_id(
            payment_info.gateway_order_id
        )
        
        if not payment_order:
            logger.error(f"Payment order not found: {payment_info.gateway_order_id}")
            return False
        
        # 4. 防止重复处理
        if payment_order.status in ['paid', 'failed', 'cancelled']:
            return True
        
        # 5. 更新支付状态
        async with self.db.transaction():
            await self.db.update_payment_order(
                payment_order.id,
                status=payment_info.status,
                gateway_transaction_id=payment_info.transaction_id,
                paid_at=payment_info.paid_at if payment_info.status == 'paid' else None
            )
            
            # 6. 记录交易
            await self.db.create_payment_transaction(
                payment_order_id=payment_order.id,
                transaction_type='payment',
                amount=payment_info.amount,
                currency=payment_order.currency,
                gateway=gateway,
                gateway_transaction_id=payment_info.transaction_id,
                status=payment_info.status,
                raw_response=callback_data
            )
        
        # 7. 发布事件
        event_type = f"payment.{payment_info.status}"
        await self.event_publisher.publish(event_type, {
            'payment_id': str(payment_order.id),
            'order_id': str(payment_order.order_id),
            'amount': float(payment_order.amount),
            'gateway_transaction_id': payment_info.transaction_id,
            'paid_at': payment_info.paid_at.isoformat() if payment_info.paid_at else None
        })
        
        return True
```

### 风控服务

```python
class RiskAssessmentService:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis = redis_client
    
    async def assess_payment_risk(self, payment_request: PaymentCreateRequest) -> RiskResult:
        """
        支付风险评估
        """
        risk_score = 0
        risk_factors = []
        
        # 1. 金额风险检查
        amount_risk = await self._check_amount_risk(payment_request)
        risk_score += amount_risk.score
        risk_factors.extend(amount_risk.factors)
        
        # 2. 频率风险检查
        frequency_risk = await self._check_frequency_risk(payment_request)
        risk_score += frequency_risk.score
        risk_factors.extend(frequency_risk.factors)
        
        # 3. 地理位置风险检查
        location_risk = await self._check_location_risk(payment_request)
        risk_score += location_risk.score
        risk_factors.extend(location_risk.factors)
        
        # 4. 设备风险检查
        device_risk = await self._check_device_risk(payment_request)
        risk_score += device_risk.score
        risk_factors.extend(device_risk.factors)
        
        # 5. 用户历史风险检查
        user_risk = await self._check_user_history_risk(payment_request)
        risk_score += user_risk.score
        risk_factors.extend(user_risk.factors)
        
        # 6. 确定风险等级和处理动作
        action = self._determine_risk_action(risk_score)
        
        return RiskResult(
            score=risk_score,
            action=action,
            factors=risk_factors
        )
    
    async def _check_amount_risk(self, payment_request: PaymentCreateRequest) -> RiskCheck:
        """检查金额风险"""
        risk_score = 0
        factors = []
        
        # 大额支付风险
        if payment_request.amount > 10000:
            risk_score += 30
            factors.append("大额支付")
        elif payment_request.amount > 5000:
            risk_score += 15
            factors.append("中额支付")
        
        # 用户历史支付金额对比
        user_payment_history = await self.db.get_user_payment_history(
            payment_request.user_id, 
            days=30
        )
        
        if user_payment_history:
            avg_amount = sum(p.amount for p in user_payment_history) / len(user_payment_history)
            if payment_request.amount > avg_amount * 5:
                risk_score += 25
                factors.append("支付金额异常（超过历史平均5倍）")
        
        return RiskCheck(score=risk_score, factors=factors)
    
    async def _check_frequency_risk(self, payment_request: PaymentCreateRequest) -> RiskCheck:
        """检查频率风险"""
        risk_score = 0
        factors = []
        
        # 检查用户短时间内支付频率
        recent_payments_key = f"payment_frequency:{payment_request.user_id}"
        recent_count = await self.redis.zcount(
            recent_payments_key,
            time.time() - 300,  # 5分钟内
            time.time()
        )
        
        if recent_count >= 5:
            risk_score += 40
            factors.append("5分钟内支付次数过多")
        elif recent_count >= 3:
            risk_score += 20
            factors.append("5分钟内支付次数较多")
        
        # 检查IP地址支付频率
        ip_payments_key = f"payment_ip:{payment_request.client_ip}"
        ip_count = await self.redis.zcount(
            ip_payments_key,
            time.time() - 3600,  # 1小时内
            time.time()
        )
        
        if ip_count >= 20:
            risk_score += 30
            factors.append("IP地址1小时内支付次数过多")
        
        return RiskCheck(score=risk_score, factors=factors)
    
    def _determine_risk_action(self, risk_score: int) -> str:
        """根据风险分数确定处理动作"""
        if risk_score >= 80:
            return 'deny'
        elif risk_score >= 50:
            return 'review'
        else:
            return 'allow'
```

## 监控指标

### 业务指标

- 支付成功率
- 支付转化率
- 平均支付时长
- 退款率

### 技术指标

- 支付网关响应时间
- 回调处理延迟
- API可用性
- 签名验证成功率

### 风控指标

- 风控拦截率
- 误报率
- 风险识别准确率
- 人工审核通过率

## 部署配置

### 环境变量

```bash
# 数据库配置
PAYMENT_DB_URL=postgresql://user:pass@localhost/payment_db

# 支付宝配置
ALIPAY_APP_ID=your_app_id
ALIPAY_PRIVATE_KEY=your_private_key
ALIPAY_PUBLIC_KEY=alipay_public_key

# 微信支付配置
WECHAT_MCH_ID=your_mch_id
WECHAT_APP_ID=your_app_id
WECHAT_API_KEY=your_api_key

# 风控配置
RISK_ASSESSMENT_ENABLED=true
HIGH_RISK_THRESHOLD=80
MEDIUM_RISK_THRESHOLD=50
```

## 相关文档

- [订单模块](../order-management/overview.md)
- [风控系统](../risk-management/overview.md)
- [安全架构](../../architecture/security.md)
- [事件架构](../../architecture/event-driven.md)
