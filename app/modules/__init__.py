"""
文件名：__init__.py
文件路径：app/modules/__init__.py
功能描述：业务模块包初始化文件

主要功能：
- 初始化业务模块包
- 定义模块访问接口
- 遵循模块化单体架构设计

使用说明：
- 通过此文件可访问各个业务模块
- 每个业务模块采用垂直切片架构
- 包含router、service、models、schemas等组件

架构说明：
- 核心交易模块：user_auth, product_catalog, shopping_cart, order_management, payment_service
- 农产品特色模块：batch_traceability, logistics_management  
- 营销会员模块：member_system, distributor_management, marketing_campaigns, social_features
- 基础服务模块：inventory_management, notification_service, supplier_management, 
  customer_service_system, risk_control_system, recommendation_system, data_analytics_platform

创建时间：2025-09-17
"""

__version__ = "1.0.0"
__title__ = "Business Modules Package"

# 模块注册信息（用于动态发现和管理）
AVAILABLE_MODULES = [
    # 核心交易模块 (P0 - 已完成)
    "user_auth",
    "product_catalog", 
    "shopping_cart",
    "order_management",
    "payment_service",
    
    # 基础服务模块 (P1-P2)
    "inventory_management",
    "notification_service",
    "supplier_management",
    "customer_service_system", 
    "risk_control_system",
    "recommendation_system",
    "data_analytics_platform",
    
    # 农产品特色模块 (P1)
    "batch_traceability",
    "logistics_management",
    
    # 营销会员模块 (P1-P2)
    "member_system",
    "distributor_management", 
    "marketing_campaigns",
    "social_features",
    
    # 质量控制模块 (P2)
    "quality_control",
]