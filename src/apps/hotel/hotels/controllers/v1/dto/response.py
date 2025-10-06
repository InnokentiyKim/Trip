from common.controllers.dto.base import BaseResponseDTO
from src.common.controllers.dto.base import BaseDTO


class GetHotelsResponseDTO(BaseDTO):
    name: str
    location: str
    services: dict | None = None
    rooms_quantity: int
    is_active: bool
    image_id: int | None = None


class CreateHotelResponseDTO(BaseResponseDTO):
    ...
