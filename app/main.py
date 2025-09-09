from fastapi import FastAPI
import os

# In development, allow auto-creating tables at startup to avoid missing-table errors.
# Set AUTO_CREATE_TABLES=1 in your environment when running locally if you want this behavior.
_auto_create_flag = os.environ.get("AUTO_CREATE_TABLES", "0") == "1"
# Detect common CI environment variables to avoid auto-creating tables in CI runners
_is_ci = os.environ.get("CI", "").lower() in ("1", "true", "yes") or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
AUTO_CREATE = _auto_create_flag and not _is_ci

app = FastAPI(title="定制化电商平台 - Sprint0", version="0.1.0")

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
