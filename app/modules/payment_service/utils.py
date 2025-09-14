"""
支付工具模块 - V1.0 Mini-MVP

提供支付相关的工具函数，包括：
- 支付验证工具
- 支付单号生成
- 金额验证
"""
import uuid
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal

from app.adapters.payment import PaymentConfig, WechatPayAdapter


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
wechat_pay_adapter = WechatPayAdapter()
payment_validator = PaymentValidator()
payment_number_generator = PaymentNumberGenerator()
