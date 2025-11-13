from abc import abstractmethod
from datetime import date
from typing import Any
from uuid import UUID

from src.apps.hotel.bookings.domain.models import Booking
from src.common.interfaces import GatewayProto


class BookingGatewayProto(GatewayProto):
    @abstractmethod
    async def get_booking_by_id(self, booking_id: int|UUID, **filters: dict | Any) -> Booking | None:
        """Retrieve a booking by its ID."""
        ...

    @abstractmethod
    async def get_bookings(self, **filters: dict | Any) -> list[Booking]:
        """Retrieve a list of bookings."""
        ...

    @abstractmethod
    async def get_active_bookings(self, **filters: dict | Any) -> list[Booking]:
        """Retrieve a list of active bookings."""
        ...

    @abstractmethod
    async def add_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> None:
        """Add a new booking."""
        ...

    @abstractmethod
    async def update_booking(
        self, booking: Booking, only_active: bool = False, **updating_params: Any
    ) -> UUID:
        """Update a booking."""
        ...

    @abstractmethod
    async def delete_booking(self, booking: Booking) -> None:
        """Delete a booking by its ID."""
        ...
