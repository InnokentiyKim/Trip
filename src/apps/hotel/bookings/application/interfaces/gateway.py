from abc import abstractmethod
from src.apps.hotel.bookings.domain.model import Bookings
from src.common.interfaces import GatewayProto


class BookingGatewayProto(GatewayProto):
    @abstractmethod
    async def get_bookings(self, **filters) -> list[Bookings]:
        """Retrieve a list of bookings."""
        ...

    @abstractmethod
    async def get_booking_by_id(self, booking_id: int) -> Bookings | None:
        """Retrieve a booking by its ID."""
        ...

    @abstractmethod
    async def add_booking(self, booking: Bookings) -> None:
        """Add a new booking."""
        ...

    @abstractmethod
    async def delete_booking(self, booking_id: int) -> None:
        """Delete a booking by its ID."""
        ...
