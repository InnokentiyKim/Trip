from decimal import Decimal
from pydantic import ConfigDict
from common.controllers.dto.base import BaseDTO, BaseResponseDTO


class GetRoomResponseDTO(BaseResponseDTO):
    hotel_id: int
    name: str
    description: str
    price: Decimal
    services: dict
    quantity: float
    image_id: int

    model_config = ConfigDict(from_attributes=True)


class DeleteRoomResponseDTO(BaseDTO):
    status_code: int = 204
    details: str = "Room deleted successfully"
