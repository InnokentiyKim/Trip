from decimal import Decimal
from uuid import UUID

from src.common.domain.commands import Command


class ListRoomsCommand(Command):
    hotel_id: UUID
    price_from: Decimal | None
    price_to: Decimal | None
    services: dict | None


class GetRoomCommand(Command):
    hotel_id: UUID
    room_id: UUID


class AddRoomCommand(Command):
    hotel_id: UUID
    user_id: UUID
    name: str
    price: Decimal
    quantity: int | None
    description: str | None
    services: dict | None
    image_id: int | None


class UpdateRoomCommand(Command):
    hotel_id: UUID
    room_id: UUID
    user_id: UUID
    name: str | None
    price: Decimal | None
    quantity: int | None
    description: str | None
    services: dict | None
    image_id: int | None


class DeleteRoomCommand(Command):
    hotel_id: UUID
    room_id: UUID
    user_id: UUID
