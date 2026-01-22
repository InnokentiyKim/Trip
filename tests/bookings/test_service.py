from datetime import date, timedelta
from uuid import uuid4

import pytest

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.application import exceptions
from src.apps.hotel.bookings.application.service import BookingService
from src.apps.hotel.bookings.domain import commands
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from tests.fixtures.mocks import (
    MockBooking,
    MockHotel,
    MockRoom,
    MockUser,
)


@pytest.fixture
async def booking_service(request_container) -> BookingService:
    """Create a booking service for testing."""
    return await request_container.get(BookingService)


@pytest.fixture
async def booking_adapter(request_container) -> BookingAdapter:
    """Create a booking adapter for testing."""
    return await request_container.get(dependency_type=BookingAdapter)


@pytest.fixture(autouse=True)
async def mock_data(
    save_instances,
    user,
    manager,
    hotel,
    rooms,
    sample_hotel,
    sample_room,
    existing_room,
    sample_booking,
    confirmed_booking,
    cancelled_booking,
    bookings,
) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel]))
    await save_instances(MockRoom([*rooms, sample_room, existing_room]))
    await save_instances(MockBooking([sample_booking, confirmed_booking, cancelled_booking, *bookings]))


@pytest.mark.anyio
class TestBookingService:
    async def test_get_booking_success(self, booking_service, user, sample_booking):
        """Test getting booking by ID."""
        cmd = commands.GetBookingCommand(user_id=user.id, booking_id=sample_booking.id)
        result = await booking_service.get_booking(cmd)

        assert result == sample_booking
        assert result.id == sample_booking.id

    async def test_get_booking_not_found(self, booking_service, user):
        """Test getting non-existent booking."""
        booking_id = uuid4()
        cmd = commands.GetBookingCommand(user_id=user.id, booking_id=booking_id)

        with pytest.raises(exceptions.BookingNotFoundError):
            await booking_service.get_booking(cmd)

    async def test_get_active_bookings(self, booking_service, user, sample_booking, confirmed_booking):
        """Test getting active bookings."""
        cmd = commands.GetActiveBookingsCommand(user_id=user.id)
        result = await booking_service.get_active_bookings(cmd)

        assert len(result) >= 2
        assert all(booking.status in [BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED] for booking in result)

    async def test_get_bookings_by_status(self, booking_service, user, sample_booking):
        """Test getting bookings by status."""
        cmd = commands.GetBookingsByStatusCommand(user_id=user.id, status=BookingStatusEnum.PENDING)
        result = await booking_service.get_bookings_by_status(cmd)

        assert len(result) >= 1
        assert all(booking.status == BookingStatusEnum.PENDING for booking in result)

    async def test_list_bookings(self, booking_service, user, bookings):
        """Test listing bookings."""
        cmd = commands.ListBookingsCommand(user_id=user.id, room_id=None, date_from=None, date_to=None, status=None)
        result = await booking_service.list_bookings(cmd)

        assert len(result) >= len(bookings)

    async def test_create_booking_success(self, booking_service, user, existing_room):
        """Test creating a new booking."""
        today = date.today()
        cmd = commands.CreateBookingCommand(
            user_id=user.id,
            room_id=existing_room.id,
            date_from=today + timedelta(days=20),
            date_to=today + timedelta(days=25),
        )

        result = await booking_service.create_booking(cmd)

        assert result is not None
        assert result.room_id == existing_room.id
        assert result.user_id == user.id

    async def test_create_booking_invalid_dates(self, booking_service, user, sample_room):
        """Test creating booking with invalid dates."""
        today = date.today()
        cmd = commands.CreateBookingCommand(
            user_id=user.id,
            room_id=sample_room.id,
            date_from=today + timedelta(days=10),
            date_to=today + timedelta(days=5),  # date_to before date_from
        )

        with pytest.raises(exceptions.InvalidBookingDatesError):
            await booking_service.create_booking(cmd)

    async def test_create_booking_room_not_available(self, booking_service, booking_adapter, user, sample_room):
        """Test creating booking when room is not available."""
        today = date.today()
        date_from = today + timedelta(days=1)
        date_to = today + timedelta(days=3)
        rooms_left = await booking_adapter.get_free_rooms_left(
            room_id=sample_room.id,
            date_from=date_from,
            date_to=date_to,
        )

        # Fill all rooms
        for _ in range(rooms_left):
            await booking_service.create_booking(
                commands.CreateBookingCommand(
                    user_id=user.id,
                    room_id=sample_room.id,
                    date_from=date_from,
                    date_to=date_to,
                )
            )

        # Try to book when full
        with pytest.raises(exceptions.RoomCannotBeBookedError):
            await booking_service.create_booking(
                commands.CreateBookingCommand(
                    user_id=user.id,
                    room_id=sample_room.id,
                    date_from=date_from,
                    date_to=date_to,
                )
            )

    async def test_cancel_active_booking_success(self, booking_service, user, sample_booking):
        """Test cancelling active booking."""
        cmd = commands.CancelActiveBookingCommand(user_id=user.id, booking_id=sample_booking.id)

        result = await booking_service.cancel_active_booking(cmd)

        assert result == sample_booking.id

    async def test_cancel_active_booking_not_pending(self, booking_service, user, confirmed_booking):
        """Test cancelling non-pending booking."""
        cmd = commands.CancelActiveBookingCommand(user_id=user.id, booking_id=confirmed_booking.id)

        with pytest.raises(exceptions.BookingCannotBeCancelledError):
            await booking_service.cancel_active_booking(cmd)

    async def test_cancel_active_booking_not_found(self, booking_service, user):
        """Test cancelling non-existent booking."""
        booking_id = uuid4()
        cmd = commands.CancelActiveBookingCommand(user_id=user.id, booking_id=booking_id)

        with pytest.raises(exceptions.BookingNotFoundError):
            await booking_service.cancel_active_booking(cmd)

    async def test_delete_booking_success(self, booking_service, user, cancelled_booking):
        """Test deleting cancelled booking."""
        cmd = commands.DeleteBookingCommand(user_id=user.id, booking_id=cancelled_booking.id)

        await booking_service.delete_booking(cmd)

        # Verify deletion
        get_cmd = commands.GetBookingCommand(user_id=user.id, booking_id=cancelled_booking.id)
        with pytest.raises(exceptions.BookingNotFoundError):
            await booking_service.get_booking(get_cmd)
