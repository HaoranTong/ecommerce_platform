# 第三方集成实现设计

## 文档概述
**承接架构层**: [integration.md](../../architecture/integration.md) - 集成架构原则  
**设计职责**: 具体适配器实现、接口设计、数据流设计  
**边界约束**: 第三方集成技术方案，保持模块边界独立  

## 基础适配器实现

### 适配器接口定义
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

## 支付服务适配器实现

### 支付适配器基类
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
```

### 微信支付适配器实现
```python
import requests
import hashlib
from typing import Dict, Any

class WechatPayAdapter(PaymentAdapter):
    """微信支付适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get('app_id')
        self.mch_id = config.get('mch_id')
        self.api_key = config.get('api_key')
        self.cert_path = config.get('cert_path')
        self.base_url = "https://api.mch.weixin.qq.com"
    
    def is_available(self) -> bool:
        try:
            response = self._make_request('/v3/merchant-service/complaints-v2')
            return response.status_code == 200
        except Exception:
            return False
    
    def create_payment(self, order_data: Dict[str, Any]) -> IntegrationResult:
        try:
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
                    error_code="PAYMENT_CREATE_FAILED",
                    error_message="微信支付订单创建失败"
                )
        except Exception as e:
            return self.handle_error(e)
    
    def _make_request(self, endpoint: str, data: Dict = None):
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()
        
        if data:
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        return response.json()
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'ecommerce-platform/1.0.0'
        }
```

## 短信服务适配器实现

### 短信适配器接口
```python
class SMSAdapter(BaseAdapter):
    """短信服务适配器基类"""
    
    @abstractmethod
    def send_verification_code(self, phone: str, code: str) -> IntegrationResult:
        """发送验证码"""
        pass
    
    @abstractmethod
    def send_notification(self, phone: str, content: str) -> IntegrationResult:
        """发送通知短信"""
        pass
```

### 腾讯云短信适配器
```python
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.sms.v20210111 import sms_client, models

class TencentCloudSMSAdapter(SMSAdapter):
    """腾讯云短信适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secret_id = config.get('secret_id')
        self.secret_key = config.get('secret_key')
        self.region = config.get('region', 'ap-beijing')
        self.app_id = config.get('app_id')
        self.sign_name = config.get('sign_name')
        
        cred = credential.Credential(self.secret_id, self.secret_key)
        self.client = sms_client.SmsClient(cred, self.region)
    
    def send_verification_code(self, phone: str, code: str) -> IntegrationResult:
        try:
            req = models.SendSmsRequest()
            req.PhoneNumberSet = [phone]
            req.SmsSdkAppId = self.app_id
            req.SignName = self.sign_name
            req.TemplateId = self.config.get('verification_template_id')
            req.TemplateParamSet = [code, "5"]  # 验证码和有效期
            
            resp = self.client.SendSms(req)
            
            if resp.SendStatusSet[0].Code == "Ok":
                return IntegrationResult(
                    success=True,
                    data={
                        'message_id': resp.SendStatusSet[0].SerialNo,
                        'phone': phone
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

## 对象存储适配器实现

### 对象存储适配器接口
```python
class ObjectStorageAdapter(BaseAdapter):
    """对象存储适配器基类"""
    
    @abstractmethod
    def upload_file(self, file_path: str, object_key: str) -> IntegrationResult:
        """上传文件"""
        pass
    
    @abstractmethod
    def download_file(self, object_key: str, local_path: str) -> IntegrationResult:
        """下载文件"""
        pass
    
    @abstractmethod
    def delete_file(self, object_key: str) -> IntegrationResult:
        """删除文件"""
        pass
    
    @abstractmethod
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """获取文件访问URL"""
        pass
```

### 阿里云OSS适配器
```python
import oss2

class AliyunOSSAdapter(ObjectStorageAdapter):
    """阿里云OSS适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_key_id = config.get('access_key_id')
        self.access_key_secret = config.get('access_key_secret')
        self.endpoint = config.get('endpoint')
        self.bucket_name = config.get('bucket_name')
        
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
    
    def upload_file(self, file_path: str, object_key: str) -> IntegrationResult:
        try:
            result = self.bucket.put_object_from_file(object_key, file_path)
            return IntegrationResult(
                success=True,
                data={
                    'etag': result.etag,
                    'object_key': object_key,
                    'url': self.get_file_url(object_key)
                }
            )
        except Exception as e:
            return self.handle_error(e)
    
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """获取文件访问URL"""
        return self.bucket.sign_url('GET', object_key, expires)
```
- [性能设计方案](./performance-design.md)
- [各模块API规范](../modules/README.md)
