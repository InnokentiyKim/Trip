import uuid
from datetime import date
from decimal import Decimal

from src.apps.hotel.bookings.domain.models import Booking
from src.common.controllers.dto.base import BaseDTO


class BookingResponseDTO(BaseDTO):
    id: uuid.UUID
    room_id: uuid.UUID
    user_id: uuid.UUID
    date_from: date
    date_to: date
    price: Decimal
    total_cost: Decimal
    total_days: int

    @classmethod
    def from_model(cls, model: "Booking") -> "BookingResponseDTO":
        """Create a booking response from the booking model."""
        return cls.model_validate(model, from_attributes=True)
