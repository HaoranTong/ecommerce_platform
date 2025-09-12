"""
文件名：main_routes.py
文件路径：app/api/main_routes.py
功能描述：API路由主入口，整合所有业务模块路由
主要功能：
- 整合用户、商品、订单、支付等模块路由
- 提供统一的API版本控制
- 配置路由前缀和标签
- 健康检查和基础接口
使用说明：
- 所有API路由都通过此文件统一暴露
- 路由前缀：/api/v1
- 支持模块化的路由管理
依赖模块：
- app.api.routes: 各业务模块路由
- FastAPI APIRouter: 路由系统核心
"""

from fastapi import APIRouter
from app.api.routes import user_router, product_router, order_router, payment_router

# 创建主路由器
router = APIRouter(prefix="/api/v1")

# 健康检查路由
@router.get("/health", tags=["系统"])
async def health_check():
    """
    系统健康检查
    
    - 无需认证
    - 返回系统运行状态
    """
    return {"status": "ok", "message": "系统运行正常"}

# 注册各模块路由
router.include_router(user_router)
router.include_router(product_router)
router.include_router(order_router)
router.include_router(payment_router)