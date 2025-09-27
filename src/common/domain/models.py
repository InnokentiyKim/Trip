from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import create_configs
from src.apps.hotel.bookings.domain.model import Booking
from src.apps.hotel.hotels.domain.model import Hotel
from src.apps.hotel.rooms.domain.model import Room


config = create_configs()

DATABASE_URL = (f"postgresql+asyncpg://{config.database.user}:{config.database.password}@"
                f"{config.database.host}:{config.database.port}/{config.database.name}")

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

ORM_OBJ = Booking | Hotel | Room
ORM_CLS = type[Booking] | type[Hotel] | type[Room]


class Base(AsyncAttrs, DeclarativeBase):
    pass
