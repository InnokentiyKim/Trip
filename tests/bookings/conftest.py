from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.apps.hotel.bookings.domain.enums import BookingStatusEnum
from src.apps.hotel.bookings.domain.models import Booking
from src.apps.hotel.hotels.domain.models import Hotel
from src.apps.hotel.rooms.domain.models import Room


@pytest.fixture
async def hotel(request_container, manager) -> Hotel:
    """Create a hotel."""
    hotel = Hotel(
        name="test_hotel",
        location="Test location",
        services={"wifi": True, "pool": False},
        rooms_quantity=10,
        owner=manager.id,
    )
    return hotel


@pytest.fixture
def sample_hotel(manager):
    return Hotel(
        name="Test Sample Hotel",
        location="Test City",
        services={"parking": True},
        rooms_quantity=10,
        owner=manager.id,
    )


@pytest.fixture
async def rooms(request_container, hotel, manager) -> list[Room]:
    """Create hotel rooms for testing."""
    rooms = []
    for i in range(3):
        rooms.append(
            Room(
                hotel_id=hotel.id,
                owner=manager.id,
                name=f"test_room_{i + 1}",
                price=Decimal("100.00") + Decimal(str(i * 10)),
                description="test_room",
                quantity=3,
                services={"wifi": True},
            )
        )
    return rooms


@pytest.fixture
def sample_room(sample_hotel):
    return Room(
        hotel_id=sample_hotel.id,
        owner=sample_hotel.owner,
        name="Deluxe Room",
        description="Luxury room",
        price=Decimal("100.0"),
        quantity=5,
        services={"wifi": True},
    )


@pytest.fixture
def existing_room(sample_room):
    return Room(
        hotel_id=sample_room.hotel_id,
        owner=sample_room.owner,
        name="Existing Room",
        price=Decimal("90.0"),
        quantity=3,
        description="Another room",
        services={"wifi": True},
    )


@pytest.fixture
def sample_booking(user, sample_room):
    """Create a sample booking."""
    today = date.today()
    return Booking(
        room_id=sample_room.id,
        user_id=user.id,
        date_from=today + timedelta(days=1),
        date_to=today + timedelta(days=5),
        price=sample_room.price,
        status=BookingStatusEnum.PENDING,
    )


@pytest.fixture
def confirmed_booking(user, existing_room):
    """Create a confirmed booking."""
    today = date.today()
    return Booking(
        room_id=existing_room.id,
        user_id=user.id,
        date_from=today + timedelta(days=10),
        date_to=today + timedelta(days=15),
        price=existing_room.price,
        status=BookingStatusEnum.CONFIRMED,
    )


@pytest.fixture
def cancelled_booking(user, sample_room):
    """Create a cancelled booking."""
    today = date.today()
    return Booking(
        room_id=sample_room.id,
        user_id=user.id,
        date_from=today - timedelta(days=10),
        date_to=today - timedelta(days=5),
        price=sample_room.price,
        status=BookingStatusEnum.CANCELLED,
    )


@pytest.fixture
def bookings(user, rooms):
    """Create multiple bookings for testing."""
    today = date.today()
    bookings_list = []

    for i, room in enumerate(rooms):
        bookings_list.append(
            Booking(
                room_id=room.id,
                user_id=user.id,
                date_from=today + timedelta(days=i * 7),
                date_to=today + timedelta(days=i * 7 + 3),
                price=room.price,
                status=BookingStatusEnum.PENDING,
            )
        )

    return bookings_list
