from uuid import UUID

from src.common.controllers.dto.base import BaseResponseDTO
from src.common.controllers.dto.base import BaseDTO


class GetHotelsResponseDTO(BaseDTO):
    name: str
    location: str
    services: dict | None = None
    rooms_quantity: int
    is_active: bool
    image_id: int | None = None


class CreateHotelResponseDTO(BaseResponseDTO): ...


class UploadHotelImageResponseDTO(BaseDTO):
    url: str
    hotel_id: UUID
    content_type: str = "multipart/form-data"


class UpdateHotelResponseDTO(BaseResponseDTO): ...
