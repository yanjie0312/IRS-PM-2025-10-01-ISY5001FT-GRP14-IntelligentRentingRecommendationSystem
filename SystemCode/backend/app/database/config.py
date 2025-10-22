import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://yilin:qiyilin710@localhost:5432/irrs_dev"
)

ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True
)

async def create_db_and_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # if reset needed
        await conn.run_sync(SQLModel.metadata.create_all)
