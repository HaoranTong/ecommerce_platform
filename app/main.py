"""
文件名：main.py
文件路径：app/main.py
功能描述：FastAPI应用程序主入口，配置和启动电商平台后端服务
主要功能：
- 初始化FastAPI应用程序
- 配置应用生命周期管理
- 注册模块化API路由
- 配置中间件和错误处理
使用说明：
- 运行命令：uvicorn app.main:app --reload
- 访问文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health
依赖模块：
- app.api.main_routes: 主路由入口
- app.redis_client: Redis连接管理
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

# Redis连接管理
from app.core.redis_client import close_redis_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化代码
    print("🚀 电商平台服务启动中...")
    
    # 开发环境自动创建表
    if AUTO_CREATE:
        print("📋 自动创建数据库表...")
        from app.core.database import engine
        from app.shared.base_models import Base
        # 导入所有模型以确保表定义被注册
        from app.modules.user_auth.models import User
        from app.modules.product_catalog.models import Category, Brand, Product, SKU, ProductAttribute, SKUAttribute, ProductImage, ProductTag
        from app.modules.shopping_cart.models import Cart, CartItem
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建完成")
    
    yield
    # 关闭时的清理代码
    print("🛑 电商平台服务关闭中...")
    await close_redis_connection()

# 开发环境自动创建表设置
_auto_create_flag = os.environ.get("AUTO_CREATE_TABLES", "0") == "1"
_is_ci = os.environ.get("CI", "").lower() in ("1", "true", "yes") or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
AUTO_CREATE = _auto_create_flag and not _is_ci

# 创建FastAPI应用实例
app = FastAPI(
    title="电商平台后端服务", 
    version="1.0.0",
    description="基于FastAPI的模块化电商平台后端API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """根路径接口"""
    return {
        "message": "电商平台后端服务",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}

# 注册模块化路由 - 按照模块化单体架构直接注册各模块路由
from app.modules.user_auth.router import router as user_auth_router
from app.modules.quality_control.router import router as quality_control_router

# 注册模块路由，使用统一的API前缀
app.include_router(
    user_auth_router, 
    prefix="/api/v1", 
    tags=["用户认证"]
)

app.include_router(
    quality_control_router,
    prefix="/api/v1",
    tags=["质量控制"]
)

# 注册产品目录模块路由
from app.modules.product_catalog.router import router as product_router
app.include_router(product_router, prefix="/api/v1", tags=["商品管理"])

# 注册订单管理模块路由
from app.modules.order_management.router import router as order_router
app.include_router(order_router, prefix="/api/v1", tags=["订单管理"])

# 注册购物车模块路由
from app.modules.shopping_cart.router import router as cart_router
app.include_router(cart_router, prefix="/api/v1", tags=["购物车"])

# 注册库存管理模块路由
from app.modules.inventory_management.router import router as inventory_router
app.include_router(inventory_router, prefix="/api/v1", tags=["库存管理"])

# 注册支付服务模块路由
from app.modules.payment_service.router import router as payment_router
app.include_router(payment_router, prefix="/api/v1", tags=["支付服务"])

# 注册会员系统模块路由
from app.modules.member_system.router import router as member_system_router
app.include_router(member_system_router, prefix="/api/v1", tags=["会员系统"])

# TODO: 其他模块路由按需添加
