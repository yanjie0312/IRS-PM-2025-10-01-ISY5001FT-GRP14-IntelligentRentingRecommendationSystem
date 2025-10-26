# app/dependencies.py
import openai
import redis.asyncio as redis
from typing import AsyncIterator
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

# ✅ 从数据库配置导入 engine（config.py 必须定义了 engine）
from app.database.config import engine
# ✅ 从缓存配置导入 redis 客户端（若你有 app/database/cache.py）
from app.database.cache import redis_client


# ------------------ OpenAI 客户端依赖 ------------------
def get_async_openai_client(request: Request) -> openai.AsyncOpenAI:
    """从 FastAPI app.state 取异步 OpenAI 客户端实例。"""
    return getattr(request.app.state, "async_openai_client", None)


# ------------------ 数据库 Session 依赖 ------------------
# 使用 SQLAlchemy 的 async_sessionmaker 创建会话工厂
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncIterator[AsyncSession]:
    """生成异步数据库会话（FastAPI 依赖注入用）"""
    async with async_session_maker() as session:
        yield session


# ------------------ Redis 依赖 ------------------
async def get_async_redis() -> redis.Redis:
    """返回 Redis 异步客户端实例"""
    return redis_client
