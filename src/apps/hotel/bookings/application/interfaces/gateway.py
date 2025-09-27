from abc import abstractmethod
from datetime import date
from uuid import UUID

from src.apps.hotel.bookings.domain.model import Booking
from src.common.interfaces import GatewayProto


class BookingGatewayProto(GatewayProto):
    @abstractmethod
    async def get_bookings(self, **filters) -> list[Booking]:
        """Retrieve a list of bookings."""
        ...

    @abstractmethod
    async def get_booking_by_id(self, booking_id: int|UUID) -> Booking | None:
        """Retrieve a booking by its ID."""
        ...

    @abstractmethod
    async def add_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> None:
        """Add a new booking."""
        ...

    @abstractmethod
    async def delete_booking(self, user_id: int, booking_id: int|UUID) -> None:
        """Delete a booking by its ID."""
        ...
