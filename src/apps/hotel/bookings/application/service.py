
from src.apps.hotel.bookings.domain.model import Bookings

from src.common.adapters.adapter import SQLAlchemyGateway
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto


class BookingService(SQLAlchemyGateway, BookingGatewayProto):
    def __init__(self) -> None:
        super().__init__()
        self.set_model(Bookings)

    async def get_bookings(self, **filters) -> list[Bookings]:
        """Retrieve a list of bookings."""
        return await self.find_all(**filters)

    async def get_booking_by_id(self, booking_id: int) -> Bookings | None:
        """Retrieve a booking by its ID."""
        return await self.find_by_id(booking_id)

    async def add_booking(self, booking: Bookings) -> None:
        """Add a new booking."""
        await self.add(booking)

    async def delete_booking(self, booking_id: int) -> None:
        """Delete a booking by its ID."""
        await self.delete_booking(booking_id)
