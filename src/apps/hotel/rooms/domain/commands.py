from dataclasses import dataclass
from decimal import Decimal

from src.common.domain.commands import Command


@dataclass(frozen=True, slots=True)
class AddRoomCommand(Command):
    hotel_id: int
    name: str
    price: Decimal
    quantity: float
    description: str | None = None
    services: dict | None = None
    image_id: int | None = None
