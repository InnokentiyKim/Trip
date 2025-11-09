from common.controllers.dto.base import BaseRequestDTO


class CreateHotelRequestDTO(BaseRequestDTO):
    name: str
    location: str
    rooms_quantity: int
    owner: int
    is_active: bool = True
    services: dict | None = None
    image_id: int | None = None
