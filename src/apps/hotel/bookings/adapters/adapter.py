from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import select, and_, or_, func

from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.apps.hotel.rooms.domain.model import Room
from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.domain.model import Booking
from src.common.adapters.adapter import SQLAlchemyGateway
from src.common.utils.dependency import SessionDependency


class BookingAdapter(SQLAlchemyGateway, BookingGatewayProto):
    async def get_booking_by_id(self, booking_id: UUID, **filters: Any) -> Booking | None:
        """Retrieve a booking by its ID."""
        booking = await self.get_one_item(SessionDependency, Booking, id=booking_id, **filters)
        return booking

    async def get_bookings(self, **filters) -> list[Booking]:
        """Retrieve a list of bookings."""
        if 'date_from' in filters:
            date_from = filters.pop('date_from')
            stmt = select(Booking).filter_by(**filters).where(Booking.date_from >= date_from)
            bookings = await self.session.execute(stmt)
            bookings = list(bookings.scalars())
        else:
            bookings = await self.get_items_list(SessionDependency, Booking, **filters)
        return bookings

    async def get_active_bookings(self, **filters) -> list[Booking]:
        """Retrieve a list of active bookings."""
        active_bookings = await self.session.execute(
            select(Booking).where(
                or_(Booking.status == BookingStatusEnum.PENDING, Booking.status == BookingStatusEnum.CONFIRMED)
            ).filter_by(**filters)
        )
        return list(active_bookings.scalars())

    async def add_booking(self, user_id: int, room_id: int, date_from: date, date_to: date) -> int | None:
        """Add a new booking."""
        booked_rooms = select(Booking).where(
            and_(
                Booking.room_id == room_id,
                or_(
                    and_(
                        Booking.date_from >= date_from,
                        Booking.date_from < date_to
                    ),
                    and_(
                        Booking.date_from <= date_from,
                        Booking.date_to > date_from
                    ),
                )
            )
        ).cte("booked_rooms")

        rooms_left_query = select(
            (Room.quantity - func.count(booked_rooms.c.room_id)).label("room_left")
        ).select_from(Room).join(
            booked_rooms, booked_rooms.c.room_id == Room.id
        ).where(Room.id == room_id).group_by(
            Room.quantity, booked_rooms.c.room_id
        )

        rooms_left = await self.session.execute(rooms_left_query)
        rooms_left = rooms_left.scalar()

        if rooms_left is not None and rooms_left > 0:
            price_query = select(Room.price).filter_by(id=room_id)
            price = await self.session.execute(price_query)
            price = price.scalar()
            new_booking = Booking(
                room_id=room_id,
                user_id=user_id,
                date_from=date_from,
                date_to=date_to,
                price=price
            )
            await self.add_item(SessionDependency, new_booking)
            return room_id

    async def update_booking(
        self, user_id: int, booking_id: UUID, only_active: bool=False, **updating_params: Any
    ) -> UUID | None:
        """Update a booking."""
        if only_active:
            booking = await self.get_one_item(
                SessionDependency,
                Booking,
                id=booking_id,
                user_id=user_id,
                status=or_(BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED)
            )
        else:
            booking = await self.get_one_item(SessionDependency, Booking, id=booking_id, user_id=user_id)
        if not booking:
            return None
        for key, value in updating_params.items():
            setattr(booking, key, value)
        await self.add_item(SessionDependency, booking)
        return booking_id

    async def delete_booking(self, user_id: int, booking_id: UUID) -> UUID | None:
        """Delete a booking by its ID."""
        booking = await self.get_one_item(SessionDependency, Booking, id=booking_id, user_id=user_id)
        if not booking:
            return None
        await self.delete_item(SessionDependency, booking)
        return booking_id
