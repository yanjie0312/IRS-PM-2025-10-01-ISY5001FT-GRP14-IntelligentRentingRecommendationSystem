# app/dependencies.py
import openai
from typing import AsyncIterator, Optional
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database.config import engine

def get_async_openai_client(request: Request) -> openai.AsyncOpenAI:
    return getattr(request.app.state, "async_openai_client", None)

async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session

# 懒加载 Redis，避免导入期连带失败
async def get_async_redis():
    try:
        from app.database.cache import redis_client
        return redis_client  # 可能是 None
    except Exception:
        return None
