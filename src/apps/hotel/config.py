from enum import StrEnum
from pydantic_settings import BaseSettings
from pydantic import Field

from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.file_object.domain.models import FileObject
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.domain.models import Room
from src.common.domain.enums import DataAccessEnum


class HotelGatewayEnum(StrEnum):
    ALCHEMY = DataAccessEnum.ALCHEMY
    MEMORY = DataAccessEnum.MEMORY


class HotelConfig(BaseSettings):
    gateway: HotelGatewayEnum = HotelGatewayEnum.ALCHEMY
    fake_data: list[Hotel] = []

class RoomConfig(BaseSettings):
    gateway: HotelGatewayEnum = HotelGatewayEnum.ALCHEMY
    fake_data: list[Room] = []

class BookingConfig(BaseSettings):
    gateway: HotelGatewayEnum = HotelGatewayEnum.ALCHEMY
    fake_data: list[Booking] = []

class FileObjectConfig(BaseSettings):
    gateway: HotelGatewayEnum = HotelGatewayEnum.ALCHEMY
    fake_data: list[FileObject] = []


class HotelsConfig(BaseSettings):
    hotel: HotelConfig = Field(default_factory=HotelConfig)
    room: RoomConfig = Field(default_factory=RoomConfig)
    booking: BookingConfig = Field(default_factory=BookingConfig)
    file_object: FileObjectConfig = Field(default_factory=FileObjectConfig)
