from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import create_configs
from src.apps.hotel.bookings.domain.model import Bookings
from src.apps.hotel.hotels.domain.model import Hotels
from src.apps.hotel.rooms.domain.model import Rooms


config = create_configs()

DATABASE_URL = (f"postgresql+asyncpg://{config.database.user}:{config.database.password}@"
                f"{config.database.host}:{config.database.port}/{config.database.name}")

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

ORM_OBJ = Bookings | Hotels | Rooms
ORM_CLS = type[Bookings] | type[Hotels] | type[Rooms]


class Base(AsyncAttrs, DeclarativeBase):
    pass
