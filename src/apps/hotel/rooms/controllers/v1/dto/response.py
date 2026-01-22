from decimal import Decimal
from uuid import UUID

from fastapi import status

from src.common.controllers.dto.base import BaseDTO, BaseResponseDTO


class GetRoomResponseDTO(BaseResponseDTO):
    hotel_id: UUID
    name: str
    description: str | None
    price: Decimal
    services: dict | None
    quantity: float
    image_id: int | None


class UpdateRoomResponseDTO(BaseResponseDTO): ...


class AddRoomResponseDTO(BaseResponseDTO):
    hotel_id: UUID


class DeleteRoomResponseDTO(BaseDTO):
    status_code: int = status.HTTP_204_NO_CONTENT
