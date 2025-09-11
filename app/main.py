from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

# Redis连接管理
from app.redis_client import close_redis_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化代码
    yield
    # 关闭时的清理代码
    await close_redis_connection()

# In development, allow auto-creating tables at startup to avoid missing-table errors.
# Set AUTO_CREATE_TABLES=1 in your environment when running locally if you want this behavior.
_auto_create_flag = os.environ.get("AUTO_CREATE_TABLES", "0") == "1"
# Detect common CI environment variables to avoid auto-creating tables in CI runners
_is_ci = os.environ.get("CI", "").lower() in ("1", "true", "yes") or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
AUTO_CREATE = _auto_create_flag and not _is_ci

app = FastAPI(
    title="定制化电商平台 - Sprint0", 
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "定制化电商平台 Sprint0 - FastAPI"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "服务运行正常"}

# 注册路由
from app.api import routes as api_routes
app.include_router(api_routes.router, prefix="/api", tags=["api"])

try:
    from app.api import product_routes
    app.include_router(product_routes.router, prefix="/api", tags=["products"])
except Exception:
    # product routes may be missing on some branches; ignore if not present
    pass

try:
    from app.api import category_routes
    app.include_router(category_routes.router, prefix="/api", tags=["categories"])
except Exception:
    # category routes may be missing on some branches; ignore if not present
    pass

try:
    from app.api import certificate_routes
    app.include_router(certificate_routes.router, prefix="/api", tags=["certificates"])
except Exception:
    pass

try:
    from app.api import user_routes
    app.include_router(user_routes.router, prefix="/api", tags=["users"])
except Exception:
    # user routes may be missing on some branches; ignore if not present
    pass

try:
    from app.api import order_routes
    app.include_router(order_routes.router, prefix="/api/orders", tags=["orders"])
except Exception:
    # order routes may be missing on some branches; ignore if not present
    pass

try:
    from app.api import cart_routes
    app.include_router(cart_routes.router, prefix="/api", tags=["shopping-cart"])
except Exception:
    # cart routes may be missing on some branches; ignore if not present
    pass

try:
    from app.api import payment_routes
    app.include_router(payment_routes.router, prefix="/api", tags=["payments"])
except Exception:
    # payment routes may be missing on some branches; ignore if not present
    pass

try:
    from app.api import test_routes
    app.include_router(test_routes.router, prefix="/api/test", tags=["test"])
except Exception:
    # test routes may be missing on some branches; ignore if not present
    pass
