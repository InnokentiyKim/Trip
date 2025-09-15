from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PASSWORD = "postgres"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass
