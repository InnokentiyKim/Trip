from decimal import Decimal
from typing import Any

from src.common.domain.commands import Command


class AddRoomCommand(Command):
    hotel_id: int
    name: str
    price: Decimal
    quantity: float
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None


class UpdateRoomCommand(Command):
    hotel_id: int
    room_id: int
    name: str | None = None
    price: Decimal | None = None
    quantity: float | None = None
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None



class DeleteRoomCommand(Command):
    hotel_id: int
    room_id: int
