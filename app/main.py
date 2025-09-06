from fastapi import FastAPI

app = FastAPI(title="定制化电商平台 - Sprint0", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "定制化电商平台 Sprint0 - FastAPI"}
