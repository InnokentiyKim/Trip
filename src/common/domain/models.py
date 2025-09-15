from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import create_configs


config = create_configs()

DATABASE_URL = (f"postgresql+asyncpg://{config.database.user}:{config.database.password}@"
                f"{config.database.host}:{config.database.port}/{config.database.name}")

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass
