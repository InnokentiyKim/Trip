from typing import Any

from src.common.domain.commands import Command


class ListHotelsCommand(Command):
    location: str | None = None
    services: dict | None = None
    rooms_quantity: int | None = None


class GetHotelCommand(Command):
    hotel_id: int


class CreateHotelCommand(Command):
    name: str
    location: str
    rooms_quantity: int
    owner: int
    is_active: bool = True
    services: dict | None = None
    image_id: int | None = None

    @classmethod
    def from_model(cls, model: Any) -> "CreateHotelCommand":
        """Create command from model."""
        return cls(
            name=model.name,
            location=model.location,
            rooms_quantity=model.rooms_quantity,
            owner=model.owner,
            is_active=model.is_active,
            services=model.services,
            image_id=model.image_id
        )


class UpdateHotelCommand(Command):
    hotel_id: int
    name: str | None = None
    location: str | None = None
    services: dict | None = None
    rooms_quantity: int | None = None
    is_active: bool | None = None
    image_id: int | None = None


class DeleteHotelCommand(Command):
    hotel_id: int
