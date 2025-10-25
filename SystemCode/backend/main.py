import os
import openai
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.config import create_db_and_tables
from app.routes.property import router as property_router
from app.services.config import get_settings  # 新写法，见第2步


log = logging.getLogger("uvicorn.error")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ← 直接读 Cloud Run 环境变量

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # 不要因为连库失败就把服务“杀掉”，先让服务起来
        await create_db_and_tables()
        log.info("DB init done")
    except Exception as e:
        log.exception("DB init failed (continuing startup): %s", e)

    if OPENAI_API_KEY:
        # SDK v1 用法
        app.state.async_openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    else:
        app.state.async_openai_client = None
        log.warning("OPENAI_API_KEY not set; OpenAI features disabled")

    yield

    # Shutdown
    if app.state.async_openai_client:
        await app.state.async_openai_client.close()

app = FastAPI(
    title="IRRS API",
    description="API for IntelligentRentingREcommendatinoSystem",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # 把你的前端域名加进来（可精确到你的 run.app 域名）
        "https://irrsfrontend-234550193243.asia-southeast1.run.app",

        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(property_router)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Welcome to IRRS"}

# 注意：Cloud Run 用 Dockerfile 的 CMD 启动，这个 __main__ 块不会被用到
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
