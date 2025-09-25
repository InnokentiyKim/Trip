from datetime import date
from typing import Any
from sqlalchemy import select, and_, or_, func
from src.apps.hotel.rooms.domain.model import Rooms
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.domain.model import Bookings
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency


class BookingAdapter(SQLAlchemyGateway, BookingGatewayProto):
    async def get_booking_by_id(self, booking_id: int, **filters: Any) -> Bookings | None:
        """Retrieve a booking by its ID."""
        booking = await self.get_one_item(SessionDependency, Bookings, id=booking_id, **filters)
        return booking

    async def get_bookings(self, **filters) -> list[Bookings]:
        """Retrieve a list of bookings."""
        bookings = await self.get_items_list(SessionDependency, Bookings, **filters)
        return bookings

    async def add_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> int | None:
        """Add a new booking."""
        booked_rooms = select(Bookings).where(
            and_(
                Bookings.room_id == 1,
                or_(
                    and_(
                        Bookings.date_from >= date_from,
                        Bookings.date_from < date_to
                    ),
                    and_(
                        Bookings.date_from <= date_from,
                        Bookings.date_to > date_from
                    ),
                )
            )
        ).cte("booked_rooms")

        rooms_left_query = select(
            (Rooms.quantity - func.count(booked_rooms.c.room_id)).label("room_left")
        ).select_from(Rooms).join(
            booked_rooms, booked_rooms.c.room_id == Rooms.id
        ).where(Rooms.id == room_id).group_by(
            Rooms.quantity, booked_rooms.c.room_id
        )

        rooms_left = await self.session.execute(rooms_left_query)
        rooms_left = rooms_left.scalar()

        if rooms_left is not None and rooms_left > 0:
            price_query = select(Rooms.price).filter_by(id=room_id)
            price = await self.session.execute(price_query)
            price = price.scalar()
            new_booking = Bookings(
                room_id=room_id,
                user_id=user_id,
                date_from=date_from,
                date_to=date_to,
                price=price
            )
            await self.add_item(SessionDependency, new_booking)
            return room_id

    async def delete_booking(self, booking_id: int) -> int:
        """Delete a booking by its ID."""
        booking = await self.get_item_by_id(SessionDependency, Bookings, booking_id)
        await self.delete_item(SessionDependency, booking)
        return booking_id
