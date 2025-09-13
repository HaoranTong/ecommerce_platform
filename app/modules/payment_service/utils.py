"""
支付工具模块 - V1.0 Mini-MVP

提供支付相关的工具函数，包括：
- 微信支付SDK集成
- 支付单号生成
- 金额验证
- 签名验证
"""
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

import requests
from fastapi import HTTPException, status


class PaymentConfig:
    """支付配置 - V1.0 Mini-MVP版本"""
    
    # 微信支付配置（从环境变量获取）
    WECHAT_APPID = "your_wechat_appid"
    WECHAT_MCH_ID = "your_mch_id"
    WECHAT_API_KEY = "your_api_key"
    WECHAT_NOTIFY_URL = "https://your-domain.com/api/payments/callback/wechat"
    
    # 支付宝配置（预留）
    ALIPAY_APP_ID = "your_alipay_app_id"
    ALIPAY_PRIVATE_KEY = "your_alipay_private_key"
    ALIPAY_PUBLIC_KEY = "your_alipay_public_key"
    
    # 支付超时时间（分钟）
    PAYMENT_TIMEOUT = 30


class WechatPayService:
    """微信支付服务 - V1.0 Mini-MVP实现"""
    
    def __init__(self):
        self.app_id = PaymentConfig.WECHAT_APPID
        self.mch_id = PaymentConfig.WECHAT_MCH_ID
        self.api_key = PaymentConfig.WECHAT_API_KEY
        self.notify_url = PaymentConfig.WECHAT_NOTIFY_URL
    
    def create_unified_order(
        self, 
        payment_no: str, 
        amount: Decimal, 
        description: str,
        user_openid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建微信统一下单
        
        Args:
            payment_no: 商户订单号
            amount: 支付金额（元）
            description: 商品描述
            user_openid: 用户微信openid（小程序支付需要）
            
        Returns:
            微信支付参数字典
        """
        # 转换金额为分
        total_fee = int(amount * 100)
        
        # 构建请求参数
        params = {
            'appid': self.app_id,
            'mch_id': self.mch_id,
            'nonce_str': self._generate_nonce_str(),
            'body': description,
            'out_trade_no': payment_no,
            'total_fee': total_fee,
            'spbill_create_ip': '127.0.0.1',  # 实际环境需要获取真实IP
            'notify_url': self.notify_url,
            'trade_type': 'JSAPI' if user_openid else 'NATIVE',
        }
        
        if user_openid:
            params['openid'] = user_openid
        
        # 生成签名
        params['sign'] = self._generate_sign(params)
        
        # 发送请求到微信
        xml_data = self._dict_to_xml(params)
        
        # TODO: 实现真实的微信API调用
        # response = requests.post(
        #     'https://api.mch.weixin.qq.com/pay/unifiedorder',
        #     data=xml_data,
        #     headers={'Content-Type': 'application/xml'}
        # )
        
        # V1.0 Mock响应用于开发测试
        mock_response = {
            'return_code': 'SUCCESS',
            'result_code': 'SUCCESS',
            'prepay_id': f'wx{int(time.time())}{payment_no[-8:]}',
            'trade_type': params['trade_type'],
            'code_url': f'weixin://wxpay/bizpayurl?pr={payment_no}' if params['trade_type'] == 'NATIVE' else None
        }
        
        return mock_response
    
    def verify_callback_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        验证微信支付回调签名
        
        Args:
            data: 回调数据
            signature: 微信签名
            
        Returns:
            bool: 签名是否有效
        """
        # 生成本地签名
        local_sign = self._generate_sign(data)
        return local_sign == signature
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        return str(uuid.uuid4()).replace('-', '')[:32]
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """
        生成微信支付签名
        
        Args:
            params: 参数字典
            
        Returns:
            str: MD5签名
        """
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 拼接参数
        param_str = '&'.join([f'{k}={v}' for k, v in sorted_params if v])
        
        # 添加API密钥
        param_str += f'&key={self.api_key}'
        
        # MD5加密
        return hashlib.md5(param_str.encode('utf-8')).hexdigest().upper()
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """字典转XML格式"""
        xml = '<xml>'
        for k, v in data.items():
            xml += f'<{k}>{v}</{k}>'
        xml += '</xml>'
        return xml


class PaymentValidator:
    """支付验证工具"""
    
    @staticmethod
    def validate_amount(order_amount: Decimal, payment_amount: Decimal) -> bool:
        """
        验证支付金额与订单金额一致性
        
        Args:
            order_amount: 订单金额
            payment_amount: 支付金额
            
        Returns:
            bool: 金额是否一致
        """
        return abs(order_amount - payment_amount) < Decimal('0.01')
    
    @staticmethod
    def validate_payment_method(method: str) -> bool:
        """
        验证支付方式是否支持
        
        Args:
            method: 支付方式
            
        Returns:
            bool: 是否支持
        """
        supported_methods = ['wechat', 'alipay']
        return method in supported_methods
    
    @staticmethod
    def validate_payment_timeout(created_at: datetime) -> bool:
        """
        验证支付是否超时
        
        Args:
            created_at: 创建时间
            
        Returns:
            bool: 是否超时
        """
        timeout_minutes = PaymentConfig.PAYMENT_TIMEOUT
        time_diff = datetime.utcnow() - created_at
        return time_diff.total_seconds() > (timeout_minutes * 60)


class PaymentNumberGenerator:
    """支付单号生成器"""
    
    @staticmethod
    def generate_payment_no() -> str:
        """
        生成支付单号
        
        格式: PAY + 时间戳 + 随机字符
        例如: PAY202509111430001234ABCD
        
        Returns:
            str: 支付单号
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4()).replace('-', '')[:8].upper()
        return f"PAY{timestamp}{random_suffix}"
    
    @staticmethod
    def generate_refund_no() -> str:
        """
        生成退款单号
        
        格式: REF + 时间戳 + 随机字符
        
        Returns:
            str: 退款单号
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4()).replace('-', '')[:8].upper()
        return f"REF{timestamp}{random_suffix}"


def create_payment_response(payment, wechat_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建标准的支付响应
    
    Args:
        payment: 支付单对象
        wechat_response: 微信支付响应
        
    Returns:
        Dict: 标准支付响应
    """
    response = {
        'payment_id': payment.id,
        'payment_no': payment.payment_no,
        'amount': float(payment.amount),
        'currency': payment.currency,
        'payment_method': payment.payment_method,
        'status': payment.status,
        'created_at': payment.created_at.isoformat()
    }
    
    # 添加支付方式特定的信息
    if payment.payment_method == 'wechat':
        if wechat_response.get('trade_type') == 'NATIVE':
            response['qr_code'] = wechat_response.get('code_url')
        elif wechat_response.get('trade_type') == 'JSAPI':
            response['prepay_id'] = wechat_response.get('prepay_id')
    
    return response


# 全局服务实例
wechat_pay_service = WechatPayService()
payment_validator = PaymentValidator()
payment_number_generator = PaymentNumberGenerator()
