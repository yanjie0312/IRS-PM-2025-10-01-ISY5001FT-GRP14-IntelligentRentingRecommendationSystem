import logging, openai, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.config import get_settings

log = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 延迟导入数据库初始化，避免导入期崩
    try:
        from app.database.config import create_db_and_tables
        await create_db_and_tables()
        log.info("DB init done")
    except Exception as e:
        log.exception("DB init failed (continuing startup): %s", e)

    try:
        s = get_settings()
        if s.OPENAI_API_KEY:
            app.state.async_openai_client = openai.AsyncOpenAI(api_key=s.OPENAI_API_KEY)
        else:
            app.state.async_openai_client = None
            log.warning("OPENAI_API_KEY not set; OpenAI features disabled")
    except Exception as e:
        log.exception("OpenAI client init failed (continuing startup): %s", e)
        app.state.async_openai_client = None

    yield

    if getattr(app.state, "async_openai_client", None):
        await app.state.async_openai_client.close()

app = FastAPI(title="IRRS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://irrsfrontend-234550193243.asia-southeast1.run.app"  # 换成你的前端域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 延迟导入路由
try:
    from app.routes.property import router as property_router
    app.include_router(property_router)
except Exception as e:
    log.exception("Router import failed (continuing startup): %s", e)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Welcome to IRRS"}
