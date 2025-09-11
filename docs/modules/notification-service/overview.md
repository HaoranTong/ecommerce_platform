# 通知服务模块 (Notification Service Module)

## 模块概述

通知服务模块负责多渠道消息推送、模板管理、发送策略、消息跟踪和用户偏好管理。支持邮件、短信、推送通知、站内信等多种通知方式。

### 主要功能

1. **多渠道通知**
   - 邮件通知 (SMTP、SendGrid、阿里云)
   - 短信通知 (阿里云、腾讯云、Twilio)
   - 推送通知 (APNs、FCM、个推)
   - 站内消息系统

2. **模板管理**
   - 可视化模板编辑
   - 多语言模板支持
   - 动态内容渲染
   - 模板版本管理

3. **智能发送**
   - 发送时机优化
   - 频率控制
   - 用户偏好尊重
   - 优先级管理

4. **效果跟踪**
   - 发送状态跟踪
   - 打开率统计
   - 点击率分析
   - 转化率监控

## 技术架构

### 核心组件

```
notification/
├── controllers/
│   ├── notification_controller.py  # 通知控制器
│   ├── template_controller.py      # 模板控制器
│   ├── preference_controller.py    # 偏好控制器
│   └── analytics_controller.py     # 分析控制器
├── services/
│   ├── notification_service.py     # 通知业务逻辑
│   ├── template_service.py         # 模板服务
│   ├── delivery_service.py         # 投递服务
│   ├── preference_service.py       # 偏好服务
│   └── analytics_service.py        # 分析服务
├── channels/
│   ├── base_channel.py             # 渠道基类
│   ├── email_channel.py            # 邮件渠道
│   ├── sms_channel.py              # 短信渠道
│   ├── push_channel.py             # 推送渠道
│   └── inapp_channel.py            # 站内信渠道
├── models/
│   ├── notification.py             # 通知模型
│   ├── template.py                 # 模板模型
│   ├── delivery_log.py             # 投递日志模型
│   └── user_preference.py          # 用户偏好模型
├── events/
│   ├── notification_events.py      # 通知事件
│   └── delivery_events.py          # 投递事件
└── utils/
    ├── template_engine.py          # 模板引擎
    ├── scheduler_utils.py          # 调度工具
    └── analytics_utils.py          # 分析工具
```

### 数据库设计

```sql
-- 通知模板表
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY,
    template_code VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    channel VARCHAR(20) NOT NULL, -- 'email', 'sms', 'push', 'inapp'
    language VARCHAR(10) DEFAULT 'zh-CN',
    subject VARCHAR(200),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text', -- 'text', 'html', 'markdown'
    variables JSONB, -- 模板变量定义
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

-- 通知记录表
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    template_code VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    priority VARCHAR(10) DEFAULT 'normal', -- 'low', 'normal', 'high', 'urgent'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed', 'cancelled'
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    recipient_address VARCHAR(200), -- 邮箱、手机号等
    subject VARCHAR(200),
    content TEXT,
    variables JSONB, -- 实际使用的变量值
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    external_id VARCHAR(100), -- 第三方服务返回的ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户通知偏好表
CREATE TABLE user_notification_preferences (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    channel VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'order', 'promotion', 'system', 'security'
    is_enabled BOOLEAN DEFAULT TRUE,
    frequency VARCHAR(20) DEFAULT 'immediate', -- 'immediate', 'daily', 'weekly', 'disabled'
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, channel, category)
);

-- 投递日志表
CREATE TABLE delivery_logs (
    id UUID PRIMARY KEY,
    notification_id UUID REFERENCES notifications(id),
    channel VARCHAR(20) NOT NULL,
    provider VARCHAR(50), -- 'sendgrid', 'aliyun_sms', 'fcm'
    status VARCHAR(20) NOT NULL,
    response_code VARCHAR(20),
    response_message TEXT,
    cost DECIMAL(8,4), -- 发送成本
    duration_ms INTEGER, -- 发送耗时(毫秒)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 通知统计表
CREATE TABLE notification_analytics (
    id UUID PRIMARY KEY,
    date DATE NOT NULL,
    template_code VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    bounced_count INTEGER DEFAULT 0,
    unsubscribed_count INTEGER DEFAULT 0,
    cost DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(date, template_code, channel)
);

-- 通知队列表
CREATE TABLE notification_queue (
    id UUID PRIMARY KEY,
    notification_id UUID REFERENCES notifications(id),
    priority INTEGER DEFAULT 100,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    max_retry INTEGER DEFAULT 3,
    retry_interval INTEGER DEFAULT 300, -- 重试间隔(秒)
    status VARCHAR(20) DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Redis 队列设计

```python
# 通知队列结构
notification_queue:{priority} = [
    {
        "notification_id": "notif_123",
        "channel": "email",
        "user_id": "user_456",
        "template_code": "order_confirmed",
        "variables": {...},
        "scheduled_at": "2024-01-01T10:00:00Z",
        "retry_count": 0
    }
]

# 发送速率限制
rate_limit:{channel}:{provider} = {
    "count": 100,
    "window_start": "2024-01-01T10:00:00Z",
    "limit": 1000
}

# 用户通知频率控制
user_notification_frequency:{user_id}:{category} = {
    "last_sent": "2024-01-01T09:00:00Z",
    "count_today": 5,
    "count_hour": 2
}
```

## API 接口

### 通知发送

```yaml
/api/v1/notifications:
  POST /:
    summary: 发送通知
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              user_id:
                type: string
                format: uuid
              template_code:
                type: string
              channel:
                type: string
                enum: [email, sms, push, inapp]
              variables:
                type: object
              priority:
                type: string
                enum: [low, normal, high, urgent]
                default: normal
              scheduled_at:
                type: string
                format: date-time
    responses:
      201:
        description: 通知创建成功
        content:
          application/json:
            schema:
              type: object
              properties:
                notification_id:
                  type: string
                  format: uuid
                status:
                  type: string

  POST /batch:
    summary: 批量发送通知
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              notifications:
                type: array
                items:
                  type: object
                  properties:
                    user_id:
                      type: string
                      format: uuid
                    template_code:
                      type: string
                    channel:
                      type: string
                    variables:
                      type: object
    responses:
      201:
        description: 批量通知创建成功

  GET /{notification_id}:
    summary: 查询通知状态
    security:
      - BearerAuth: []
    parameters:
      - name: notification_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: 通知详情
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NotificationDetail'
```

### 模板管理

```yaml
/api/v1/notification-templates:
  GET /:
    summary: 获取模板列表
    security:
      - BearerAuth: []
    parameters:
      - name: channel
        in: query
        schema:
          type: string
      - name: language
        in: query
        schema:
          type: string
    responses:
      200:
        description: 模板列表
        content:
          application/json:
            schema:
              type: object
              properties:
                templates:
                  type: array
                  items:
                    $ref: '#/components/schemas/NotificationTemplate'

  POST /:
    summary: 创建模板
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/NotificationTemplateCreateRequest'
    responses:
      201:
        description: 模板创建成功

  PUT /{template_id}:
    summary: 更新模板
    security:
      - BearerAuth: []
    parameters:
      - name: template_id
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
            $ref: '#/components/schemas/NotificationTemplateUpdateRequest'
    responses:
      200:
        description: 更新成功
```

## 业务逻辑

### 通知发送服务

```python
class NotificationService:
    def __init__(self, db, queue_manager, template_service, preference_service):
        self.db = db
        self.queue_manager = queue_manager
        self.template_service = template_service
        self.preference_service = preference_service
    
    async def send_notification(self, notification_request: NotificationRequest) -> NotificationResult:
        """
        发送通知
        1. 检查用户偏好
        2. 渲染模板内容
        3. 入队等待发送
        """
        # 1. 检查用户通知偏好
        preference_check = await self.preference_service.check_user_preference(
            notification_request.user_id,
            notification_request.channel,
            notification_request.template_code
        )
        
        if not preference_check.allowed:
            return NotificationResult(
                status='skipped',
                reason=preference_check.reason
            )
        
        # 2. 获取模板并渲染内容
        template = await self.template_service.get_template(
            notification_request.template_code,
            notification_request.channel
        )
        
        rendered_content = await self.template_service.render_template(
            template,
            notification_request.variables
        )
        
        # 3. 创建通知记录
        notification = await self.db.create_notification(
            user_id=notification_request.user_id,
            template_code=notification_request.template_code,
            channel=notification_request.channel,
            priority=notification_request.priority,
            subject=rendered_content.subject,
            content=rendered_content.content,
            variables=notification_request.variables,
            scheduled_at=notification_request.scheduled_at
        )
        
        # 4. 添加到发送队列
        await self.queue_manager.enqueue_notification(
            notification_id=notification.id,
            priority=self._get_queue_priority(notification_request.priority),
            scheduled_at=notification_request.scheduled_at or datetime.utcnow()
        )
        
        return NotificationResult(
            notification_id=notification.id,
            status='queued'
        )
    
    async def send_batch_notifications(self, batch_request: BatchNotificationRequest) -> BatchNotificationResult:
        """批量发送通知"""
        results = []
        
        # 分批处理，避免数据库压力
        batch_size = 100
        for i in range(0, len(batch_request.notifications), batch_size):
            batch = batch_request.notifications[i:i+batch_size]
            
            # 并发处理单批次
            batch_results = await asyncio.gather(*[
                self.send_notification(notification_request)
                for notification_request in batch
            ], return_exceptions=True)
            
            results.extend(batch_results)
        
        success_count = sum(1 for result in results if isinstance(result, NotificationResult) and result.status != 'failed')
        
        return BatchNotificationResult(
            total_count=len(batch_request.notifications),
            success_count=success_count,
            failed_count=len(batch_request.notifications) - success_count,
            results=results
        )

class NotificationDeliveryService:
    def __init__(self, db, channel_manager, analytics_service):
        self.db = db
        self.channel_manager = channel_manager
        self.analytics_service = analytics_service
    
    async def process_notification_queue(self):
        """
        处理通知队列 (后台任务)
        """
        while True:
            try:
                # 获取待发送的通知
                notifications = await self.queue_manager.dequeue_notifications(limit=50)
                
                if not notifications:
                    await asyncio.sleep(5)  # 无通知时等待5秒
                    continue
                
                # 并发处理通知
                await asyncio.gather(*[
                    self._deliver_notification(notification)
                    for notification in notifications
                ], return_exceptions=True)
                
            except Exception as e:
                logger.error(f"Error processing notification queue: {e}")
                await asyncio.sleep(10)
    
    async def _deliver_notification(self, notification: Notification):
        """投递单个通知"""
        try:
            # 1. 获取通知渠道
            channel = self.channel_manager.get_channel(notification.channel)
            
            # 2. 检查发送频率限制
            if not await self._check_rate_limit(notification.channel):
                await self._reschedule_notification(notification, delay_seconds=60)
                return
            
            # 3. 发送通知
            delivery_result = await channel.send(
                recipient=notification.recipient_address,
                subject=notification.subject,
                content=notification.content,
                metadata={
                    'notification_id': str(notification.id),
                    'user_id': str(notification.user_id),
                    'template_code': notification.template_code
                }
            )
            
            # 4. 更新通知状态
            await self.db.update_notification_status(
                notification.id,
                status='sent' if delivery_result.success else 'failed',
                sent_at=datetime.utcnow() if delivery_result.success else None,
                external_id=delivery_result.external_id,
                error_message=delivery_result.error_message
            )
            
            # 5. 记录投递日志
            await self.db.create_delivery_log(
                notification_id=notification.id,
                channel=notification.channel,
                provider=channel.provider_name,
                status='success' if delivery_result.success else 'failed',
                response_code=delivery_result.response_code,
                response_message=delivery_result.response_message,
                cost=delivery_result.cost,
                duration_ms=delivery_result.duration_ms
            )
            
            # 6. 更新分析数据
            await self.analytics_service.record_delivery(
                notification.template_code,
                notification.channel,
                'sent' if delivery_result.success else 'failed'
            )
            
        except Exception as e:
            # 处理发送失败
            await self._handle_delivery_failure(notification, str(e))
    
    async def _handle_delivery_failure(self, notification: Notification, error_message: str):
        """处理发送失败"""
        retry_count = notification.retry_count + 1
        max_retry = 3
        
        if retry_count <= max_retry:
            # 重试发送
            delay_seconds = min(300 * (2 ** retry_count), 3600)  # 指数退避，最大1小时
            
            await self.db.update_notification_retry(
                notification.id,
                retry_count=retry_count,
                error_message=error_message
            )
            
            await self._reschedule_notification(notification, delay_seconds)
        else:
            # 超过重试次数，标记为失败
            await self.db.update_notification_status(
                notification.id,
                status='failed',
                error_message=f"Max retry exceeded: {error_message}"
            )
```

### 模板引擎

```python
class TemplateEngine:
    def __init__(self):
        self.jinja_env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # 注册自定义过滤器
        self.jinja_env.filters['currency'] = self._currency_filter
        self.jinja_env.filters['datetime'] = self._datetime_filter
    
    async def render_template(self, template: NotificationTemplate, variables: dict) -> RenderedContent:
        """渲染模板"""
        try:
            # 验证必需变量
            self._validate_variables(template.variables, variables)
            
            # 渲染主题
            subject = None
            if template.subject:
                subject_template = self.jinja_env.from_string(template.subject)
                subject = subject_template.render(**variables)
            
            # 渲染内容
            content_template = self.jinja_env.from_string(template.content)
            content = content_template.render(**variables)
            
            return RenderedContent(
                subject=subject,
                content=content,
                content_type=template.content_type
            )
            
        except Exception as e:
            raise TemplateRenderError(f"Template render failed: {str(e)}")
    
    def _validate_variables(self, template_variables: dict, provided_variables: dict):
        """验证模板变量"""
        if not template_variables:
            return
        
        required_vars = [
            var_name for var_name, var_config in template_variables.items()
            if var_config.get('required', False)
        ]
        
        missing_vars = [var for var in required_vars if var not in provided_variables]
        if missing_vars:
            raise TemplateValidationError(f"Missing required variables: {missing_vars}")
    
    def _currency_filter(self, value, currency='CNY'):
        """货币格式化过滤器"""
        if currency == 'CNY':
            return f"¥{value:.2f}"
        elif currency == 'USD':
            return f"${value:.2f}"
        else:
            return f"{value:.2f} {currency}"
    
    def _datetime_filter(self, value, format='%Y-%m-%d %H:%M:%S'):
        """日期时间格式化过滤器"""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)
```

### 通知渠道实现

```python
# 邮件渠道
class EmailChannel(BaseNotificationChannel):
    def __init__(self, config: dict):
        self.provider_name = config['provider']  # 'smtp', 'sendgrid', 'ses'
        self.config = config
        
        if self.provider_name == 'sendgrid':
            self.client = SendGridAPIClient(config['api_key'])
        elif self.provider_name == 'smtp':
            self.smtp_config = config['smtp']
    
    async def send(self, recipient: str, subject: str, content: str, metadata: dict) -> DeliveryResult:
        """发送邮件"""
        start_time = time.time()
        
        try:
            if self.provider_name == 'sendgrid':
                result = await self._send_via_sendgrid(recipient, subject, content, metadata)
            elif self.provider_name == 'smtp':
                result = await self._send_via_smtp(recipient, subject, content, metadata)
            else:
                raise NotImplementedError(f"Provider {self.provider_name} not implemented")
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return DeliveryResult(
                success=True,
                external_id=result.get('message_id'),
                response_code='200',
                duration_ms=duration_ms,
                cost=self._calculate_cost()
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            return DeliveryResult(
                success=False,
                error_message=str(e),
                response_code='500',
                duration_ms=duration_ms
            )
    
    async def _send_via_sendgrid(self, recipient: str, subject: str, content: str, metadata: dict):
        """通过SendGrid发送邮件"""
        message = Mail(
            from_email=self.config['from_email'],
            to_emails=recipient,
            subject=subject,
            html_content=content
        )
        
        # 添加跟踪参数
        message.tracking_settings = TrackingSettings()
        message.tracking_settings.click_tracking = ClickTracking(enable=True)
        message.tracking_settings.open_tracking = OpenTracking(enable=True)
        
        # 添加自定义参数
        message.custom_args = metadata
        
        response = await self.client.send(message)
        return {'message_id': response.headers.get('X-Message-Id')}

# 短信渠道
class SMSChannel(BaseNotificationChannel):
    def __init__(self, config: dict):
        self.provider_name = config['provider']  # 'aliyun', 'tencent', 'twilio'
        self.config = config
        
        if self.provider_name == 'aliyun':
            self.client = AlibabaCloudSMSClient(config)
        elif self.provider_name == 'twilio':
            self.client = TwilioSMSClient(config)
    
    async def send(self, recipient: str, subject: str, content: str, metadata: dict) -> DeliveryResult:
        """发送短信"""
        start_time = time.time()
        
        try:
            if self.provider_name == 'aliyun':
                result = await self._send_via_aliyun(recipient, content, metadata)
            elif self.provider_name == 'twilio':
                result = await self._send_via_twilio(recipient, content, metadata)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return DeliveryResult(
                success=result['success'],
                external_id=result.get('message_id'),
                response_code=result.get('code'),
                response_message=result.get('message'),
                duration_ms=duration_ms,
                cost=self._calculate_sms_cost(content)
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            return DeliveryResult(
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )
```

## 监控指标

### 业务指标

- 通知发送量
- 到达率
- 打开率
- 点击率

### 技术指标

- 队列处理延迟
- 发送成功率
- 重试率
- 渠道可用性

### 成本指标

- 单条通知成本
- 渠道成本对比
- ROI分析
- 预算控制

## 部署配置

### 环境变量

```bash
# 数据库配置
NOTIFICATION_DB_URL=postgresql://user:pass@localhost/notification_db

# 邮件配置
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_api_key
FROM_EMAIL=noreply@example.com

# 短信配置
SMS_PROVIDER=aliyun
ALIYUN_ACCESS_KEY=your_access_key
ALIYUN_SECRET_KEY=your_secret_key

# 推送配置
PUSH_PROVIDER=fcm
FCM_SERVER_KEY=your_server_key

# 队列配置
NOTIFICATION_QUEUE_URL=redis://localhost:6379/4
QUEUE_WORKER_COUNT=5
```

## 相关文档

- [用户模块](../user-auth/overview.md)
- [订单模块](../order-management/overview.md)
- [事件架构](../../architecture/event-driven.md)
- [模板系统](../../architecture/templates.md)
