"""
文件名：__init__.py
文件路径：app/api/routes/__init__.py
功能描述：统一导出所有路由模块，便于主应用集成
主要功能：
- 导出用户管理路由 (user)
- 导出商品管理路由 (product)
- 导出订单管理路由 (order)
- 导出支付管理路由 (payment)
使用说明：
- 在主应用中通过 from app.api.routes import user_router, product_router 等方式导入
- 每个路由器都已配置好前缀和标签
- 支持统一的错误处理和认证机制
依赖模块：
- FastAPI APIRouter: 路由系统核心
- 各模块路由定义: user.py, product.py, order.py, payment.py
"""

from .user import router as user_router
from .product import router as product_router
from .order import router as order_router
from .payment import router as payment_router

__all__ = [
    "user_router",
    "product_router", 
    "order_router",
    "payment_router"
]