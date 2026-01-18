from decimal import Decimal

import pytest

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
                name=f"test_room_{i+1}",
                price=Decimal("100.00"+str(i*10)),
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
