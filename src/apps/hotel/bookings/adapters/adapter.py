from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.domain.model import Bookings
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency


class BookingAdapter(SQLAlchemyGateway, BookingGatewayProto):
    async def get_booking_by_id(self, booking_id: int) -> Bookings | None:
        """Retrieve a booking by its ID."""
        booking = await self.get_item_by_id(SessionDependency, Bookings, booking_id)
        return booking

    async def get_bookings(self, **filters) -> list[Bookings]:
        """Retrieve a list of bookings."""
        bookings = await self.get_items_list(SessionDependency, Bookings, **filters)
        return bookings

    async def add_booking(self, booking: Bookings) -> None:
        """Add a new booking."""
        await self.add_item(SessionDependency, booking)

    async def delete_booking(self, booking_id: int) -> None:
        """Delete a booking by its ID."""
        booking = await self.get_item_by_id(SessionDependency, Bookings, booking_id)
        await self.delete_item(SessionDependency, booking)
