<!--
文档说明：
- 内容：第三方服务集成的架构规范和实施指南
- 使用方法：集成第三方服务时的标准化指导
- 更新方法：新增集成或集成方式变更时更新
- 引用关系：被各模块的第三方集成实现引用
- 更新频率：集成策略调整时
-->

# 第三方集成架构

## 集成设计原则

### 核心原则
1. **适配器模式** - 所有第三方集成通过适配器接口实现
2. **故障隔离** - 第三方服务故障不影响核心业务
3. **可替换性** - 支持第三方服务的热切换
4. **统一监控** - 集中监控所有第三方服务状态
5. **降级策略** - 第三方服务不可用时的备选方案

### 集成分类
- **支付服务** - 微信支付、支付宝、银联等
- **短信服务** - 腾讯云短信、阿里云短信等
- **对象存储** - 腾讯云COS、阿里云OSS等
- **推送服务** - 微信模板消息、APP推送等
- **物流服务** - 顺丰、圆通、中通等快递API
- **地图服务** - 高德地图、百度地图等

## 适配器架构设计

### 基础适配器接口
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class IntegrationResult:
    """集成调用结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None

class BaseAdapter(ABC):
    """第三方服务适配器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        pass
    
    def before_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """请求前置处理"""
        return params
    
    def after_request(self, result: IntegrationResult) -> IntegrationResult:
        """请求后置处理"""
        return result
    
    def handle_error(self, error: Exception) -> IntegrationResult:
        """统一错误处理"""
        return IntegrationResult(
            success=False,
            error_code="INTEGRATION_ERROR",
            error_message=str(error)
        )
```

### 支付服务适配器
```python
class PaymentAdapter(BaseAdapter):
    """支付服务适配器基类"""
    
    @abstractmethod
    def create_payment(self, order_data: Dict[str, Any]) -> IntegrationResult:
        """创建支付订单"""
        pass
    
    @abstractmethod
    def query_payment(self, payment_id: str) -> IntegrationResult:
        """查询支付状态"""
        pass
    
    @abstractmethod
    def refund_payment(self, refund_data: Dict[str, Any]) -> IntegrationResult:
        """申请退款"""
        pass
    
    @abstractmethod
    def verify_callback(self, callback_data: Dict[str, Any]) -> IntegrationResult:
        """验证支付回调"""
        pass

class WechatPayAdapter(PaymentAdapter):
    """微信支付适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get('app_id')
        self.mch_id = config.get('mch_id')
        self.api_key = config.get('api_key')
        self.cert_path = config.get('cert_path')
    
    def is_available(self) -> bool:
        try:
            # 调用微信支付健康检查接口
            response = self._make_request('/v3/merchant-service/complaints-v2')
            return response.status_code == 200
        except Exception:
            return False
    
    def create_payment(self, order_data: Dict[str, Any]) -> IntegrationResult:
        try:
            # 构建微信支付请求参数
            params = {
                'appid': self.app_id,
                'mchid': self.mch_id,
                'description': order_data['description'],
                'out_trade_no': order_data['order_no'],
                'amount': {
                    'total': int(order_data['amount'] * 100),  # 转换为分
                    'currency': 'CNY'
                },
                'notify_url': order_data['notify_url']
            }
            
            # 调用微信支付API
            response = self._make_request('/v3/pay/transactions/native', params)
            
            if response.get('code_url'):
                return IntegrationResult(
                    success=True,
                    data={
                        'payment_id': response.get('prepay_id'),
                        'code_url': response.get('code_url')
                    },
                    raw_response=response
                )
            else:
                return IntegrationResult(
                    success=False,
                    error_code='PAYMENT_CREATE_FAILED',
                    error_message='创建支付订单失败'
                )
        
        except Exception as e:
            return self.handle_error(e)

class AlipayAdapter(PaymentAdapter):
    """支付宝适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get('app_id')
        self.private_key = config.get('private_key')
        self.alipay_public_key = config.get('alipay_public_key')
    
    def create_payment(self, order_data: Dict[str, Any]) -> IntegrationResult:
        # 支付宝支付实现
        pass
```

### 短信服务适配器
```python
class SMSAdapter(BaseAdapter):
    """短信服务适配器基类"""
    
    @abstractmethod
    def send_sms(self, phone: str, template_id: str, params: Dict[str, Any]) -> IntegrationResult:
        """发送短信"""
        pass
    
    @abstractmethod
    def query_sms_status(self, sms_id: str) -> IntegrationResult:
        """查询短信状态"""
        pass

class TencentSMSAdapter(SMSAdapter):
    """腾讯云短信适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secret_id = config.get('secret_id')
        self.secret_key = config.get('secret_key')
        self.sdk_app_id = config.get('sdk_app_id')
        self.region = config.get('region', 'ap-beijing')
    
    def send_sms(self, phone: str, template_id: str, params: Dict[str, Any]) -> IntegrationResult:
        try:
            from tencentcloud.sms.v20210111 import sms_client, models
            from tencentcloud.common import credential
            
            # 创建认证对象
            cred = credential.Credential(self.secret_id, self.secret_key)
            client = sms_client.SmsClient(cred, self.region)
            
            # 构建请求
            req = models.SendSmsRequest()
            req.PhoneNumberSet = [f"+86{phone}"]
            req.SmsSdkAppId = self.sdk_app_id
            req.TemplateId = template_id
            req.TemplateParamSet = list(params.values())
            
            # 发送短信
            resp = client.SendSms(req)
            
            if resp.SendStatusSet[0].Code == "Ok":
                return IntegrationResult(
                    success=True,
                    data={
                        'sms_id': resp.SendStatusSet[0].SerialNo,
                        'status': 'sent'
                    }
                )
            else:
                return IntegrationResult(
                    success=False,
                    error_code=resp.SendStatusSet[0].Code,
                    error_message=resp.SendStatusSet[0].Message
                )
        
        except Exception as e:
            return self.handle_error(e)
```

### 对象存储适配器
```python
class StorageAdapter(BaseAdapter):
    """对象存储适配器基类"""
    
    @abstractmethod
    def upload_file(self, file_path: str, content: bytes, content_type: str) -> IntegrationResult:
        """上传文件"""
        pass
    
    @abstractmethod
    def download_file(self, file_path: str) -> IntegrationResult:
        """下载文件"""
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> IntegrationResult:
        """删除文件"""
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str, expires: int = 3600) -> str:
        """获取文件访问URL"""
        pass

class TencentCOSAdapter(StorageAdapter):
    """腾讯云COS适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secret_id = config.get('secret_id')
        self.secret_key = config.get('secret_key')
        self.region = config.get('region')
        self.bucket = config.get('bucket')
        self.domain = config.get('domain')
    
    def upload_file(self, file_path: str, content: bytes, content_type: str) -> IntegrationResult:
        try:
            from qcloud_cos import CosConfig, CosS3Client
            
            # 创建COS客户端
            config = CosConfig(
                Region=self.region,
                SecretId=self.secret_id,
                SecretKey=self.secret_key
            )
            client = CosS3Client(config)
            
            # 上传文件
            response = client.put_object(
                Bucket=self.bucket,
                Body=content,
                Key=file_path,
                ContentType=content_type
            )
            
            return IntegrationResult(
                success=True,
                data={
                    'file_path': file_path,
                    'url': f"https://{self.domain}/{file_path}",
                    'etag': response['ETag']
                }
            )
        
        except Exception as e:
            return self.handle_error(e)
```

## 服务管理器

### 集成服务管理
```python
class IntegrationManager:
    """第三方集成服务管理器"""
    
    def __init__(self):
        self.adapters: Dict[str, Dict[str, BaseAdapter]] = {}
        self.configs = self._load_configs()
        self._register_adapters()
    
    def _load_configs(self) -> Dict[str, Any]:
        """加载集成配置"""
        return {
            'payment': {
                'wechat': {
                    'app_id': os.getenv('WECHAT_APP_ID'),
                    'mch_id': os.getenv('WECHAT_MCH_ID'),
                    'api_key': os.getenv('WECHAT_API_KEY'),
                    'enabled': True,
                    'priority': 1
                },
                'alipay': {
                    'app_id': os.getenv('ALIPAY_APP_ID'),
                    'private_key': os.getenv('ALIPAY_PRIVATE_KEY'),
                    'enabled': True,
                    'priority': 2
                }
            },
            'sms': {
                'tencent': {
                    'secret_id': os.getenv('TENCENT_SECRET_ID'),
                    'secret_key': os.getenv('TENCENT_SECRET_KEY'),
                    'sdk_app_id': os.getenv('TENCENT_SMS_APP_ID'),
                    'enabled': True,
                    'priority': 1
                }
            }
        }
    
    def _register_adapters(self):
        """注册适配器"""
        # 注册支付适配器
        if 'payment' not in self.adapters:
            self.adapters['payment'] = {}
        
        for provider, config in self.configs.get('payment', {}).items():
            if config.get('enabled'):
                if provider == 'wechat':
                    self.adapters['payment'][provider] = WechatPayAdapter(config)
                elif provider == 'alipay':
                    self.adapters['payment'][provider] = AlipayAdapter(config)
        
        # 注册短信适配器
        if 'sms' not in self.adapters:
            self.adapters['sms'] = {}
        
        for provider, config in self.configs.get('sms', {}).items():
            if config.get('enabled'):
                if provider == 'tencent':
                    self.adapters['sms'][provider] = TencentSMSAdapter(config)
    
    def get_adapter(self, service_type: str, provider: str = None) -> Optional[BaseAdapter]:
        """获取适配器"""
        if service_type not in self.adapters:
            return None
        
        if provider:
            return self.adapters[service_type].get(provider)
        
        # 返回优先级最高的可用适配器
        available_adapters = [
            (adapter, self.configs[service_type][name].get('priority', 99))
            for name, adapter in self.adapters[service_type].items()
            if adapter.is_available()
        ]
        
        if available_adapters:
            return min(available_adapters, key=lambda x: x[1])[0]
        
        return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取所有集成服务健康状态"""
        status = {}
        for service_type, adapters in self.adapters.items():
            status[service_type] = {}
            for provider, adapter in adapters.items():
                try:
                    status[service_type][provider] = adapter.get_health_status()
                except Exception as e:
                    status[service_type][provider] = {
                        'available': False,
                        'error': str(e)
                    }
        return status

# 全局集成管理器实例
integration_manager = IntegrationManager()
```

## 服务降级策略

### 降级配置
```python
class FallbackStrategy:
    """降级策略"""
    
    def __init__(self):
        self.strategies = {
            'payment': self._payment_fallback,
            'sms': self._sms_fallback,
            'storage': self._storage_fallback
        }
    
    def _payment_fallback(self, error: Exception, params: Dict[str, Any]) -> IntegrationResult:
        """支付服务降级"""
        # 记录失败日志
        logger.error(f"Payment service failed: {error}")
        
        # 返回降级响应
        return IntegrationResult(
            success=False,
            error_code='PAYMENT_SERVICE_UNAVAILABLE',
            error_message='支付服务暂时不可用，请稍后重试'
        )
    
    def _sms_fallback(self, error: Exception, params: Dict[str, Any]) -> IntegrationResult:
        """短信服务降级"""
        # 可以尝试其他短信服务商
        # 或者将任务加入队列延迟处理
        
        logger.error(f"SMS service failed: {error}")
        
        # 将短信任务加入重试队列
        retry_queue.add_task('send_sms', params, delay=60)
        
        return IntegrationResult(
            success=True,  # 降级成功
            data={'status': 'queued'},
            error_message='短信发送已加入队列'
        )
    
    def execute_fallback(self, service_type: str, error: Exception, params: Dict[str, Any]) -> IntegrationResult:
        """执行降级策略"""
        strategy = self.strategies.get(service_type)
        if strategy:
            return strategy(error, params)
        
        return IntegrationResult(
            success=False,
            error_code='SERVICE_UNAVAILABLE',
            error_message=f'{service_type} 服务不可用'
        )

fallback_strategy = FallbackStrategy()
```

### 熔断器模式
```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # 正常状态
    OPEN = "open"         # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态

class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """执行函数调用，带熔断保护"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """调用成功处理"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """调用失败处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# 为每个第三方服务创建熔断器
circuit_breakers = {
    'wechat_pay': CircuitBreaker(failure_threshold=3, timeout=30),
    'alipay': CircuitBreaker(failure_threshold=3, timeout=30),
    'tencent_sms': CircuitBreaker(failure_threshold=5, timeout=60)
}
```

## 监控与告警

### 集成监控
```python
class IntegrationMonitor:
    """第三方集成监控"""
    
    def __init__(self):
        self.metrics = {}
        self.alert_rules = self._load_alert_rules()
    
    def record_request(self, service_type: str, provider: str, 
                      success: bool, response_time: float):
        """记录请求指标"""
        key = f"{service_type}_{provider}"
        if key not in self.metrics:
            self.metrics[key] = {
                'total_requests': 0,
                'success_requests': 0,
                'total_response_time': 0,
                'last_request_time': time.time()
            }
        
        self.metrics[key]['total_requests'] += 1
        self.metrics[key]['total_response_time'] += response_time
        self.metrics[key]['last_request_time'] = time.time()
        
        if success:
            self.metrics[key]['success_requests'] += 1
        
        # 检查告警规则
        self._check_alerts(key)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标"""
        result = {}
        for key, metrics in self.metrics.items():
            total = metrics['total_requests']
            success = metrics['success_requests']
            total_time = metrics['total_response_time']
            
            result[key] = {
                'total_requests': total,
                'success_rate': success / total if total > 0 else 0,
                'average_response_time': total_time / total if total > 0 else 0,
                'last_request_time': metrics['last_request_time']
            }
        
        return result
    
    def _check_alerts(self, service_key: str):
        """检查告警规则"""
        metrics = self.metrics[service_key]
        
        # 检查成功率
        if metrics['total_requests'] >= 10:
            success_rate = metrics['success_requests'] / metrics['total_requests']
            if success_rate < 0.9:  # 成功率低于90%
                self._send_alert(
                    service_key, 
                    f"Success rate is {success_rate:.2%}",
                    "HIGH"
                )
        
        # 检查响应时间
        avg_response_time = metrics['total_response_time'] / metrics['total_requests']
        if avg_response_time > 5.0:  # 平均响应时间超过5秒
            self._send_alert(
                service_key,
                f"Average response time is {avg_response_time:.2f}s",
                "MEDIUM"
            )
    
    def _send_alert(self, service: str, message: str, level: str):
        """发送告警"""
        logger.warning(f"ALERT [{level}] {service}: {message}")
        # 发送到告警系统（如企业微信、钉钉等）

# 全局监控实例
integration_monitor = IntegrationMonitor()
```

## 配置管理

### 动态配置
```python
class IntegrationConfig:
    """集成配置管理"""
    
    def __init__(self):
        self.config_file = "integrations.yaml"
        self.configs = self._load_from_file()
        self._watch_config_changes()
    
    def _load_from_file(self) -> Dict[str, Any]:
        """从文件加载配置"""
        import yaml
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def get_config(self, service_type: str, provider: str) -> Dict[str, Any]:
        """获取服务配置"""
        return self.configs.get(service_type, {}).get(provider, {})
    
    def update_config(self, service_type: str, provider: str, config: Dict[str, Any]):
        """更新服务配置"""
        if service_type not in self.configs:
            self.configs[service_type] = {}
        
        self.configs[service_type][provider] = config
        self._save_to_file()
        
        # 通知适配器重新加载配置
        adapter = integration_manager.get_adapter(service_type, provider)
        if adapter:
            adapter.config = config
    
    def _save_to_file(self):
        """保存配置到文件"""
        import yaml
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.configs, f, default_flow_style=False, allow_unicode=True)

# 配置示例文件 integrations.yaml
"""
payment:
  wechat:
    app_id: "${WECHAT_APP_ID}"
    mch_id: "${WECHAT_MCH_ID}"
    api_key: "${WECHAT_API_KEY}"
    enabled: true
    priority: 1
    timeout: 30
    retry_times: 3
  
  alipay:
    app_id: "${ALIPAY_APP_ID}"
    private_key: "${ALIPAY_PRIVATE_KEY}"
    enabled: true
    priority: 2
    timeout: 30
    retry_times: 3

sms:
  tencent:
    secret_id: "${TENCENT_SECRET_ID}"
    secret_key: "${TENCENT_SECRET_KEY}"
    sdk_app_id: "${TENCENT_SMS_APP_ID}"
    enabled: true
    priority: 1
    timeout: 10
    retry_times: 2
"""
```
