import pytest

from src.apps.comment.domain.models import Comment
from src.apps.hotel.hotels.domain.models import Hotel


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
    """Create a sample hotel."""
    return Hotel(
        name="Test Sample Hotel",
        location="Test City",
        services={"parking": True},
        rooms_quantity=10,
        owner=manager.id,
    )


@pytest.fixture
def another_hotel(manager):
    """Create another sample hotel."""
    return Hotel(
        name="Test Another Hotel",
        location="Test Another City",
        services={"parking": True},
        rooms_quantity=5,
        owner=manager.id,
    )


@pytest.fixture
def comment(user, hotel):
    """Create a comment."""
    return Comment(
        hotel_id=hotel.id,
        user_id=user.id,
        content="Great hotel, enjoyed my stay!",
        rating=None,
    )


@pytest.fixture
def sample_comment(user, sample_hotel):
    """Create a sample comment."""
    return Comment(
        hotel_id=sample_hotel.id,
        user_id=user.id,
        content="Great hotel, enjoyed my stay!",
        rating=5,
    )
