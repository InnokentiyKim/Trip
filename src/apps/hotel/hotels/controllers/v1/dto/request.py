from uuid import UUID

from src.common.controllers.dto.base import BaseRequestDTO


class CreateHotelRequestDTO(BaseRequestDTO):
    name: str
    location: str
    rooms_quantity: int
    is_active: bool = True
    services: dict | None = None
    image_id: int | None = None


class UpdateHotelRequestDTO(BaseRequestDTO):
    hotel_id: int
    name: str
    location: str
    rooms_quantity: int
    is_active: bool = True
    services: dict | None = None
    image_id: int | None = None


class ListHotelsRequestDTO(BaseRequestDTO):
    location: str | None = None
    services: dict | None = None
    rooms_quantity: int | None = None
