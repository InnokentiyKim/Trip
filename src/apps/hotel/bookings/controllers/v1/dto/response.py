import uuid
from datetime import date
from decimal import Decimal

from src.common.controllers.dto.base import BaseDTO


class BookingsResponseDTO(BaseDTO):
    id: uuid.UUID
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: Decimal
    total_cost: Decimal
    total_days: int
