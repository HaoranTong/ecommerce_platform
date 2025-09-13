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

# 注册用户认证模块路由，使用正确的API路径标准
app.include_router(
    user_auth_router, 
    prefix="/api/v1/user-auth", 
    tags=["用户认证"]
)

# 注册质量控制模块路由
app.include_router(
    quality_control_router,
    prefix="/api/v1/quality-control",
    tags=["质量控制"]
)

# TODO: 其他模块路由按需添加
# from app.modules.product_catalog.router import router as product_router
# app.include_router(product_router, prefix="/api/v1/product-catalog", tags=["商品管理"])
