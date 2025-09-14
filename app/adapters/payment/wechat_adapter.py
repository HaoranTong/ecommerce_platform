"""
微信支付适配器

提供微信支付服务的统一接口
"""
import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from decimal import Decimal

from .config import PaymentConfig


class WechatPayAdapter:
    """微信支付适配器 - V1.0 Mini-MVP实现"""
    
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