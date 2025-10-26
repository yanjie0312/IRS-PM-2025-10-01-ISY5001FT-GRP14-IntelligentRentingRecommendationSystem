# main.py
import os
import logging
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

log = logging.getLogger("uvicorn.error")


async def _init_db_with_timeout():
    try:
        # 惰性导入，防止顶层导入时触发 DB 连接/配置副作用
        from app.database.config import create_db_and_tables
        # 给 DB 初始化加硬超时（建议 3~10 秒）
        await asyncio.wait_for(create_db_and_tables(), timeout=3)
        log.info("DB init done")
    except asyncio.TimeoutError:
        log.warning("DB init timeout; skipping at startup (will init lazily on first use)")
    except Exception as e:
        log.exception("DB init failed (continuing startup): %s", e)


def create_app() -> FastAPI:
    # 把一切“可能出事的东西”都放到函数体内
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 1) 启动后后台异步做 DB 初始化，避免阻塞监听端口
        db_task = asyncio.create_task(_init_db_with_timeout())

        # 2) OpenAI 客户端（仅创建对象，不应发网络请求）
        try:
            from app.config import get_settings
            from openai import AsyncOpenAI
            s = get_settings()
            if getattr(s, "OPENAI_API_KEY", None):
                app.state.async_openai_client = AsyncOpenAI(api_key=s.OPENAI_API_KEY)
            else:
                app.state.async_openai_client = None
                log.warning("OPENAI_API_KEY not set; OpenAI features disabled")
        except Exception as e:
            log.exception("OpenAI client init failed (continuing startup): %s", e)
            app.state.async_openai_client = None

        # ✅ 让 uvicorn 尽快开始监听端口
        yield

        # 优雅关闭
        if getattr(app.state, "async_openai_client", None):
            try:
                await app.state.async_openai_client.close()
            except Exception:
                pass

        if not db_task.done():
            db_task.cancel()

    app = FastAPI(title="IRRS API", version="0.1.0", lifespan=lifespan)

    # ------------------ CORS ------------------
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

    # ------------------ 路由注册 ------------------
    try:
        # ✅ 导入 property 路由模块
        from app.routes import property as property_routes

        # ✅ 挂载所有 /api/v1/properties/** 接口
        app.include_router(property_routes.router)
        log.info("✅ Property routes mounted successfully.")
    except Exception as e:
        log.exception("❌ Router import failed (continuing startup): %s", e)

    # ------------------ 基础探针 ------------------
    @app.get("/healthz")
    async def healthz():
        return {"ok": True}

    @app.get("/")
    async def root():
        return {"message": "Welcome to IRRS"}

    return app


# 兼容非 factory 运行方式（例如本地调试时 `uvicorn main:app` 也能起）
app = create_app()
