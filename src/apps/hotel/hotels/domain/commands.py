from uuid import UUID

from src.common.domain.commands import Command


class ListHotelsCommand(Command):
    location: str | None
    services: dict | None
    rooms_quantity: int | None


class GetHotelCommand(Command):
    hotel_id: UUID


class CreateHotelCommand(Command):
    name: str
    location: str
    rooms_quantity: int
    owner: UUID
    is_active: bool
    services: dict | None
    image_id: int | None


class UpdateHotelCommand(Command):
    hotel_id: UUID
    owner: UUID
    name: str | None
    location: str | None
    services: dict | None
    rooms_quantity: int | None
    is_active: bool | None
    image_id: int | None


class DeleteHotelCommand(Command):
    hotel_id: UUID
