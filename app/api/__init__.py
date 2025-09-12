"""
文件名：__init__.py
文件路径：app/api/__init__.py
功能描述：API包初始化文件，统一导出API模块和路由
主要功能：
- 导出模块化的API路由
- 导出数据模式定义
- 提供API包的统一接口
使用说明：
- 通过此文件可访问所有API相关功能
- 支持模块化的路由管理
依赖模块：
- app.api.routes: 模块化路由定义
- app.api.schemas: API数据模式
- app.api.main_routes: 主路由入口
"""

from .main_routes import router as main_router
from .routes import user_router, product_router, order_router, payment_router
from . import schemas

__all__ = [
    "main_router",
    "user_router",
    "product_router",
    "order_router", 
    "payment_router",
    "schemas"
]
