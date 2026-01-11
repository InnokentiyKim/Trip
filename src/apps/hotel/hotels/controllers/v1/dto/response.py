from uuid import UUID

from pydantic import ConfigDict

from src.common.controllers.dto.base import BaseResponseDTO
from src.common.controllers.dto.base import BaseDTO


class GetHotelsResponseDTO(BaseResponseDTO):

    name: str
    location: str
    services: dict | None = None
    rooms_quantity: int
    is_active: bool
    image_id: int | None = None


class CreateHotelResponseDTO(BaseResponseDTO): ...


class UploadHotelImageResponseDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True)

    url: str
    hotel_id: UUID
    content_type: str = "multipart/form-data"


class UpdateHotelResponseDTO(BaseResponseDTO): ...
