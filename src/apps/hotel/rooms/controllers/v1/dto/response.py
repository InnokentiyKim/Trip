from decimal import Decimal
from pydantic import ConfigDict
from fastapi import status
from src.common.controllers.dto.base import BaseDTO, BaseResponseDTO


class GetRoomResponseDTO(BaseResponseDTO):
    hotel_id: int
    name: str
    description: str
    price: Decimal
    services: dict
    quantity: float
    image_id: int

    model_config = ConfigDict(from_attributes=True)


class UpdateRoomResponseDTO(BaseResponseDTO): ...


class AddRoomResponseDTO(BaseResponseDTO):
    hotel_id: int

class DeleteRoomResponseDTO(BaseDTO):
    status_code: int = status.HTTP_204_NO_CONTENT
