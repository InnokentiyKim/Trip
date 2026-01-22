from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_, select

from src.apps.hotel.bookings.application.interfaces.gateway import BookingGatewayProto
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.rooms.domain.models import Room
from src.common.adapters.adapter import FakeGateway, SQLAlchemyGateway
from src.infrastructure.database.memory.database import MemoryDatabase


class BookingAdapter(SQLAlchemyGateway, BookingGatewayProto):
    async def add(self, booking: Booking) -> None:
        """Add a new booking."""
        self.session.add(booking)
        await self.session.commit()

    async def get_booking_by_id(self, booking_id: UUID, **filters: Any) -> Booking | None:
        """
        Retrieve a booking by its ID.

        Args:
            booking_id (UUID): The ID of the booking to retrieve.
            **filters: Additional filters to apply.

        Returns:
            Booking | None: The booking if found, else None.
        """
        booking = await self.get_one_item(Booking, id=booking_id, **filters)
        return booking

    async def get_bookings(self, **filters: Any) -> list[Booking]:
        """
        Retrieve a list of bookings.

        Args:
            **filters: Filters to apply to the bookings query.

        Returns:
            list[Booking]: A list of bookings matching the filters.
        """
        criteria = []
        user_id = filters.get("user_id", None)
        status = filters.get("status", None)
        date_from = filters.get("date_from", None)
        date_to = filters.get("date_to", None)

        if user_id is not None:
            criteria.append(Booking.user_id == user_id)
        if status is not None:
            criteria.append(Booking.status == status)
        if date_from is not None:
            criteria.append(Booking.date_from >= date_from)
        if date_to is not None:
            criteria.append(Booking.date_to <= date_to)

        stmt = select(Booking).filter(*criteria)
        bookings = await self.session.execute(stmt)
        return list(bookings.scalars())

    async def get_active_bookings(self, **filters: Any) -> list[Booking]:
        """
        Retrieve a list of active bookings.

        Args:
            **filters: Filters to apply to the bookings query.

        Returns:
            list[Booking]: A list of active bookings matching the filters.
        """
        active_bookings = await self.session.execute(
            select(Booking)
            .where(
                or_(
                    Booking.status == BookingStatusEnum.PENDING,
                    Booking.status == BookingStatusEnum.CONFIRMED,
                )
            )
            .filter_by(**filters)
        )
        return list(active_bookings.scalars())

    async def get_free_rooms_left(self, room_id: UUID, date_from: date, date_to: date) -> int:
        """
        Retrieve the number of free rooms left for a given room and date range.

        Args:
            room_id (UUID): The ID of the room.
            date_from (date): The start date of the booking.
            date_to (date): The end date of the booking.

        Returns:
            int: The number of free rooms left.
        """
        booked_rooms = (
            select(Booking)
            .where(
                and_(
                    Booking.room_id == room_id,
                    or_(
                        and_(Booking.date_from >= date_from, Booking.date_from < date_to),
                        and_(Booking.date_from <= date_from, Booking.date_to > date_from),
                    ),
                )
            )
            .cte("booked_rooms")
        )

        rooms_left_query = (
            select((Room.quantity - func.coalesce(func.count(booked_rooms.c.room_id), 0)).label("room_left"))
            .select_from(Room)
            .outerjoin(booked_rooms, booked_rooms.c.room_id == Room.id)
            .where(Room.id == room_id)
            .group_by(Room.quantity, booked_rooms.c.room_id)
        )

        rooms_left = await self.session.scalar(rooms_left_query)
        return rooms_left or 0

    async def add_booking(self, user_id: UUID, room_id: UUID, date_from: date, date_to: date) -> Booking | None:
        """
        Add a new booking.

        Args:
            user_id (UUID): The ID of the user making the booking.
            room_id (UUID): The ID of the room to be booked.
            date_from (date): The start date of the booking.
            date_to (date): The end date of the booking.

        Returns:
            Booking | None: The newly created booking if successful, else None.
        """
        rooms_left = await self.get_free_rooms_left(room_id, date_from, date_to)

        if rooms_left > 0:
            price_query = select(Room.price).filter_by(id=room_id)
            price = await self.session.scalar(price_query)

            new_booking = Booking(
                room_id=room_id,
                user_id=user_id,
                date_from=date_from,
                date_to=date_to,
                price=price,  # type: ignore
            )

            await self.add(new_booking)
            return new_booking

        return None

    async def update_booking(self, booking: Booking, only_active: bool = False, **updating_params: Any) -> UUID | None:
        """
        Update a booking.

        Args:
            booking (Booking): The booking to update.
            only_active (bool): If True, only update if the booking is active.
            **updating_params: The parameters to update.

        Returns:
            UUID | None: The ID of the updated booking if successful, else None.
        """
        active_statuses = [BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED]
        if only_active and booking.status not in active_statuses:
            return None

        for key, value in updating_params.items():
            setattr(booking, key, value)

        await self.add(booking)
        return booking.id

    async def delete_booking(self, booking: Booking) -> None:
        """
        Delete a booking by its ID.

        Args:
            booking (Booking): The booking to delete.

        Returns:
            None
        """
        await self.delete_item(booking)


class FakeBookingAdapter(FakeGateway[Booking], BookingGatewayProto):
    def __init__(self, memory_db: MemoryDatabase) -> None:
        super().__init__(memory_db)
        self._rooms_collection = memory_db.rooms

    async def add(self, booking: Booking) -> None:
        """Add a new booking."""
        self._collection.add(booking)

    async def get_booking_by_id(self, booking_id: UUID, **filters: Any) -> Booking | None:
        """Retrieve a booking by its ID."""
        return next(
            (
                booking
                for booking in self._collection
                if booking.id == booking_id and all(getattr(booking, k) == v for k, v in filters.items())
            ),
            None,
        )

    async def get_bookings(self, **filters: Any) -> list[Booking]:
        """Retrieve a list of bookings."""
        return [booking for booking in self._collection if all(getattr(booking, k) == v for k, v in filters.items())]

    async def get_active_bookings(self, **filters: Any) -> list[Booking]:
        """Retrieve a list of active bookings."""
        return [
            booking
            for booking in self._collection
            if booking.status in [BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED]
            and all(getattr(booking, k) == v for k, v in filters.items())
        ]

    async def get_free_rooms_left(self, room_id: UUID, date_from: date, date_to: date) -> int:
        """Retrieve the number of free rooms left for a given room and date range."""
        booked_rooms = [
            booking
            for booking in self._collection
            if booking.room_id == room_id
            and ((date_from <= booking.date_from < date_to) or (booking.date_from <= date_from < booking.date_to))
        ]

        rooms_count = len([room for room in self._rooms_collection if room.id == room_id])
        left_count = rooms_count - len(booked_rooms)

        return left_count

    async def add_booking(self, user_id: UUID, room_id: UUID, date_from: date, date_to: date) -> Booking | None:
        """Add a new booking."""
        days_count = (date_to - date_from).days
        rooms_left = await self.get_free_rooms_left(room_id, date_from, date_to)

        if rooms_left > 0:
            room = next((room for room in self._rooms_collection if room.id == room_id), None)

            if room is None:
                return None

            total_cost = room.price * days_count
            new_booking = Booking(
                room_id=room_id,
                user_id=user_id,
                date_from=date_from,
                date_to=date_to,
                price=total_cost,
            )

            self._collection.add(new_booking)
            return new_booking

        return None

    async def update_booking(self, booking: Booking, only_active: bool = False, **updating_params: Any) -> UUID | None:
        """Update a booking."""
        active_statuses = [BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED]

        if only_active and booking.status not in active_statuses:
            return None

        for key, value in updating_params.items():
            setattr(booking, key, value)

        self._collection.discard(booking)
        self._collection.add(booking)

        return booking.id

    async def delete_booking(self, booking: Booking) -> None:
        """Delete a booking by its ID."""
        self._collection.discard(booking)
