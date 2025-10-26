# app/database/config.py
import os
from typing import Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker,
    AsyncEngine, AsyncSession
)

_engine: Optional[AsyncEngine] = None
_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None

def _build_db_url() -> str:
    # 优先读取 DATABASE_URL（必须是异步驱动 asyncpg）
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # 兼容旧的分散变量（有则用）
    user = os.getenv("DB_USER")
    pwd  = os.getenv("DB_PASS")
    name = os.getenv("DB_NAME")
    host = os.getenv("DB_HOST")
    inst = os.getenv("INSTANCE_CONNECTION_NAME")
    if user and pwd and name and inst:
        # Cloud SQL Unix Socket
        return f"postgresql+asyncpg://{user}:{pwd}@/{name}?host=/cloudsql/{inst}"
    if user and pwd and name and host:
        # 直连 TCP
        return f"postgresql+asyncpg://{user}:{pwd}@{host}:5432/{name}"

    raise RuntimeError("DATABASE_URL not set (and no fallback env)")

def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _build_db_url(),
            pool_pre_ping=True,
            pool_recycle=1800,
        )
    return _engine

def get_async_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _sessionmaker

async def create_db_and_tables():
    from sqlmodel import SQLModel
    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
