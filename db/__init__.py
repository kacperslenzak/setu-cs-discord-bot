from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from config import BotConfig


DATABASE_URL = BotConfig.get("DATABASE_URL")


def create_engine() -> AsyncEngine:
    return create_async_engine(DATABASE_URL)


def create_async_session(engine):
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db(engine: AsyncEngine):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        return True
    except Exception as e:
        return False
