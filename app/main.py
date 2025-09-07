from fastapi import FastAPI

app = FastAPI(title="定制化电商平台 - Sprint0", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "定制化电商平台 Sprint0 - FastAPI"}
from app.api import routes as api_routes

app.include_router(api_routes.router, prefix="/api", tags=["api"])
