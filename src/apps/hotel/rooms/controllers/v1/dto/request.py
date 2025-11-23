from decimal import Decimal

from src.common.controllers.dto.base import BaseRequestDTO


class ListRoomsRequestDTO(BaseRequestDTO):
    price_from: Decimal | None = None
    price_to: Decimal | None = None
    services: dict | None = None


class UpdateRoomRequestDTO(BaseRequestDTO):
    name: str | None = None
    price: Decimal | None = None
    quantity: float | None = None
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None
