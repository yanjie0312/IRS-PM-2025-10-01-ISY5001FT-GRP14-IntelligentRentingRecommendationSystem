# app/database/config.py
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# 读取 DATABASE_URL（Cloud Run 环境变量里已设置）
# 例：postgresql+asyncpg://USER:PASS@HOST:5432/DBNAME?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# 创建全局 Async Engine（导出名必须叫 engine，满足 dependencies.py 的 import）
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

# 创建异步 Session 工厂
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 供启动时（或首次访问时）建表
async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# 可选：提供一个通用的依赖（若你不在 dependencies.py 里写，也可以直接用这个）
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
