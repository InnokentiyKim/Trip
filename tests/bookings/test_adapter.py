import uuid
from datetime import date, timedelta

import pytest

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.apps.hotel.bookings.domain.models import Booking
from tests.fixtures.mocks import MockBooking, MockHotel, MockRoom, MockUser


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
    bookings,
) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel]))
    await save_instances(MockRoom([*rooms, sample_room, existing_room]))
    await save_instances(MockBooking([sample_booking, confirmed_booking, *bookings]))


@pytest.mark.anyio
class TestBookingAdapter:
    """Tests for BookingAdapter."""

    async def test_get_booking_by_id_success(self, booking_adapter, sample_booking):
        """Test getting booking by ID."""
        result = await booking_adapter.get_booking_by_id(sample_booking.id)

        assert result is not None
        assert result.id == sample_booking.id
        assert result.room_id == sample_booking.room_id
        assert result.user_id == sample_booking.user_id

    async def test_get_booking_by_id_not_found(self, booking_adapter):
        """Test getting non-existent booking."""
        non_existent_id = uuid.uuid4()
        result = await booking_adapter.get_booking_by_id(non_existent_id)

        assert result is None

    async def test_get_bookings_all(self, booking_adapter, user, bookings):
        """Test getting all bookings for a user."""
        result = await booking_adapter.get_bookings(user_id=user.id)

        assert isinstance(result, list)
        assert len(result) >= len(bookings)
        assert all(isinstance(booking, Booking) for booking in result)

    async def test_get_bookings_by_status(self, booking_adapter, user, sample_booking):
        """Test getting bookings by status."""
        result = await booking_adapter.get_bookings(user_id=user.id, status=BookingStatusEnum.PENDING)

        assert len(result) >= 1
        assert all(booking.status == BookingStatusEnum.PENDING for booking in result)

    async def test_get_active_bookings(self, booking_adapter, user, sample_booking, confirmed_booking):
        """Test getting active bookings."""
        result = await booking_adapter.get_active_bookings(user_id=user.id)

        assert len(result) >= 2
        assert all(booking.status in [BookingStatusEnum.PENDING, BookingStatusEnum.CONFIRMED] for booking in result)

    async def test_get_free_rooms_left(self, booking_adapter, sample_room, sample_booking):
        """Test calculating free rooms left."""
        today = date.today()
        result = await booking_adapter.get_free_rooms_left(
            room_id=sample_room.id,
            date_from=today + timedelta(days=1),
            date_to=today + timedelta(days=3),
        )

        assert isinstance(result, int)
        assert result >= 0

    async def test_add_booking_success(self, booking_adapter, user, existing_room):
        """Test adding a new booking."""
        today = date.today()
        date_from = today + timedelta(days=20)
        date_to = today + timedelta(days=25)

        booking = await booking_adapter.add_booking(
            user_id=user.id,
            room_id=existing_room.id,
            date_from=date_from,
            date_to=date_to,
        )

        assert booking is not None
        assert isinstance(booking, Booking)
        assert booking.room_id == existing_room.id
        assert booking.user_id == user.id

    async def test_add_booking_no_rooms_available(self, booking_adapter, user, sample_room):
        """Test adding booking when no rooms available."""
        # Fill all rooms
        today = date.today()
        date_from = today + timedelta(days=1)
        date_to = today + timedelta(days=3)

        for _ in range(sample_room.quantity + 1):
            await booking_adapter.add_booking(
                user_id=user.id,
                room_id=sample_room.id,
                date_from=date_from,
                date_to=date_to,
            )

        # Try to book when full
        booking = await booking_adapter.add_booking(
            user_id=user.id,
            room_id=sample_room.id,
            date_from=date_from,
            date_to=date_to,
        )

        assert booking is None

    async def test_update_booking_success(self, booking_adapter, sample_booking):
        """Test updating booking."""
        updated_id = await booking_adapter.update_booking(
            sample_booking,
            status=BookingStatusEnum.CONFIRMED,
        )

        assert updated_id == sample_booking.id

        updated_booking = await booking_adapter.get_booking_by_id(sample_booking.id)
        assert updated_booking.status == BookingStatusEnum.CONFIRMED

    async def test_update_booking_only_active(self, booking_adapter, cancelled_booking):
        """Test updating non-active booking with only_active flag."""
        updated_id = await booking_adapter.update_booking(
            cancelled_booking,
            only_active=True,
            status=BookingStatusEnum.CONFIRMED,
        )

        assert updated_id is None

    async def test_delete_booking_success(self, booking_adapter, user, sample_room):
        """Test deleting booking."""
        today = date.today()
        booking = await booking_adapter.add_booking(
            user_id=user.id,
            room_id=sample_room.id,
            date_from=today + timedelta(days=30),
            date_to=today + timedelta(days=35),
        )

        await booking_adapter.delete_booking(booking)

        deleted_booking = await booking_adapter.get_booking_by_id(booking.id)
        assert deleted_booking is None

    async def test_get_bookings_with_date_filter(self, booking_adapter, user, bookings):
        """Test getting bookings with date filter."""
        today = date.today()
        result = await booking_adapter.get_bookings(user_id=user.id, date_from=today + timedelta(days=7))

        assert all(booking.date_from >= today + timedelta(days=7) for booking in result)
