from fastapi import FastAPI
import os

# In development, allow auto-creating tables at startup to avoid missing-table errors.
# Set AUTO_CREATE_TABLES=1 in your environment when running locally if you want this behavior.
AUTO_CREATE = os.environ.get("AUTO_CREATE_TABLES", "0") == "1"

app = FastAPI(title="定制化电商平台 - Sprint0", version="0.1.0")

if AUTO_CREATE:
    # Defer imports that touch DB until we know we want to create tables
    try:
        from app.db import engine, Base as _Base  # type: ignore

        @app.on_event("startup")
        async def _create_tables_on_startup():
            # Create all tables if they don't exist. Intended for local dev only.
            try:
                _Base.metadata.create_all(bind=engine)
                print("AUTO_CREATE_TABLES enabled: created missing tables (if any).")
            except Exception as _ex:
                # don't block startup; log the error
                import sys
                print("AUTO_CREATE_TABLES failed to create tables:", _ex, file=sys.stderr)
    except Exception:
        # If DB layer isn't available at import time, ignore - startup will surface errors later.
        pass

@app.get("/")
async def root():
    return {"message": "定制化电商平台 Sprint0 - FastAPI"}
from app.api import routes as api_routes

app.include_router(api_routes.router, prefix="/api", tags=["api"])
try:
    from app.api import product_routes as product_routes
    app.include_router(product_routes.router, prefix="/api", tags=["products"])
except Exception:
    # product routes may be missing on some branches; ignore if not present
    pass
try:
    from app.api import certificate_routes as certificate_routes
    app.include_router(certificate_routes.router, prefix="/api", tags=["certificates"])
except Exception:
    pass
