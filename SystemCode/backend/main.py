# main.py
import os, logging, asyncio, openai
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.config import get_settings

log = logging.getLogger("uvicorn.error")

async def _init_db_with_timeout():
    try:
        from app.database.config import create_db_and_tables
        # 给 DB 初始化加硬超时（3 秒可自行调大到 5~10）
        await asyncio.wait_for(create_db_and_tables(), timeout=3)
        log.info("DB init done")
    except asyncio.TimeoutError:
        log.warning("DB init timeout; skipping for startup (will rely on lazy init at first use)")
    except Exception as e:
        log.exception("DB init failed (continuing startup): %s", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) **不要阻塞启动**：把 DB 初始化放到后台任务里跑
    db_task = asyncio.create_task(_init_db_with_timeout())

    # 2) OpenAI 客户端初始化（这一步不应该发起网络请求，不会阻塞）
    try:
        s = get_settings()
        if getattr(s, "OPENAI_API_KEY", None):
            app.state.async_openai_client = openai.AsyncOpenAI(api_key=s.OPENAI_API_KEY)
        else:
            app.state.async_openai_client = None
            log.warning("OPENAI_API_KEY not set; OpenAI features disabled")
    except Exception as e:
        log.exception("OpenAI client init failed (continuing startup): %s", e)
        app.state.async_openai_client = None

    # 让服务先开始监听端口
    yield

    # 关闭 OpenAI 客户端（若需要）
    if getattr(app.state, "async_openai_client", None):
        await app.state.async_openai_client.close()

    # 可选：若 DB 任务仍在运行，取消/忽略
    if not db_task.done():
        db_task.cancel()

app = FastAPI(title="IRRS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://irrsfrontend-234550193243.asia-southeast1.run.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ 确保“导入路由”不会在 import 顶层做数据库连接/测试连接
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
