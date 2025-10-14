from src.common.domain.commands import Command


class CreateHotelCommand(Command):
    name: str
    location: str
    rooms_quantity: int
    owner: int
    is_active: bool = True
    services: dict | None = None
    image_id: int | None = None
