from decimal import Decimal
from src.common.domain.commands import Command


class ListRoomsCommand(Command):
    hotel_id: int
    price_from: Decimal | None = None
    price_to: Decimal | None = None
    services: dict | None = None


class GetRoomCommand(Command):
    hotel_id: int
    room_id: int


class AddRoomCommand(Command):
    hotel_id: int
    name: str
    price: Decimal
    quantity: int | None = None
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None


class UpdateRoomCommand(Command):
    hotel_id: int
    room_id: int
    name: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None


class DeleteRoomCommand(Command):
    hotel_id: int
    room_id: int
