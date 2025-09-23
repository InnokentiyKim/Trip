import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from src.common.controllers.dto.base import BaseDTO


class BookingResponseDTO(BaseDTO):
    id: uuid.UUID
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: Decimal
    total_cost: Decimal
    total_days: int

    @classmethod
    def from_model(cls, model: Any) -> "BookingResponseDTO":
        """Create a booking response from the booking model."""
        return cls.model_validate(model)
