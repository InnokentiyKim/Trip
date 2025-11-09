from decimal import Decimal

from src.common.controllers.dto.base import BaseResponseDTO


class GetRoomRequestDTO(BaseResponseDTO):
    hotel_id: int


class UpdateRoomRequestDTO(BaseResponseDTO):
    hotel_id: int
    name: str | None = None
    price: Decimal | None = None
    quantity: float | None = None
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None


class DeleteRoomRequestDTO(BaseResponseDTO):
    hotel_id: int
