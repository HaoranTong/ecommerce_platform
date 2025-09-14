"""
支付配置管理

统一管理各种支付服务的配置信息
"""

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