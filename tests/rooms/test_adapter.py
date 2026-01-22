import uuid
from decimal import Decimal

import pytest

from src.apps.hotel.rooms.adapters.adapter import RoomAdapter
from src.apps.hotel.rooms.domain.models import Room
from tests.fixtures.mocks import MockHotel, MockRoom, MockUser


@pytest.fixture
async def room_adapter(request_container) -> RoomAdapter:
    """Create a room adapter for testing."""
    return await request_container.get(dependency_type=RoomAdapter)


@pytest.fixture(autouse=True)
async def mock_data(save_instances, user, manager, hotel, rooms, sample_hotel, sample_room, existing_room) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel]))
    await save_instances(MockRoom([*rooms, sample_room, existing_room]))


@pytest.mark.asyncio
class TestRoomAdapter:
    """Tests for RoomAdapter."""

    async def test_list_rooms_all(self, room_adapter, sample_hotel, sample_room, existing_room):
        """Test listing all rooms for a hotel."""
        result = await room_adapter.list_rooms(sample_hotel.id)

        assert isinstance(result, list)
        assert len(result) >= 2
        assert all(isinstance(room, Room) for room in result)
        assert all(room.hotel_id == sample_hotel.id for room in result)

    async def test_list_rooms_with_price_filter(self, room_adapter, sample_hotel):
        """Test listing rooms with price range filter."""
        result = await room_adapter.list_rooms(sample_hotel.id, price_from=Decimal("85.0"), price_to=Decimal("95.0"))

        assert len(result) >= 1
        assert all(Decimal("85.0") <= room.price <= Decimal("95.0") for room in result)

    async def test_list_rooms_with_services_filter(self, room_adapter, sample_hotel):
        """Test listing rooms with services filter."""
        result = await room_adapter.list_rooms(sample_hotel.id, services={"wifi": True})

        assert len(result) >= 1
        assert all(room.services and room.services.get("wifi") is True for room in result)

    async def test_get_room_success(self, room_adapter, existing_room):
        """Test getting room by ID."""
        result = await room_adapter.get_room(existing_room.id)

        assert result is not None
        assert result.id == existing_room.id
        assert result.name == existing_room.name
        assert result.hotel_id == existing_room.hotel_id

    async def test_get_room_not_found(self, room_adapter):
        """Test getting non-existent room."""
        non_existent_id = uuid.uuid4()
        result = await room_adapter.get_room(non_existent_id)

        assert result is None

    async def test_add_room_success(self, room_adapter, sample_hotel, manager):
        """Test adding a new room."""
        room_id = await room_adapter.add_room(
            hotel_id=sample_hotel.id,
            owner=manager.id,
            name="New Test Room",
            price=Decimal("150.0"),
            quantity=5,
            description="New room description",
            services={"wifi": True, "tv": True},
            image_id=1,
        )

        assert room_id is not None
        assert isinstance(room_id, uuid.UUID)

        created_room = await room_adapter.get_room(room_id)
        assert created_room is not None
        assert created_room.name == "New Test Room"
        assert created_room.price == Decimal("150.0")

    async def test_add_room_duplicate_name(self, room_adapter, sample_hotel, manager, existing_room):
        """Test adding room with duplicate name in same hotel."""
        room_id = await room_adapter.add_room(
            hotel_id=sample_hotel.id,
            owner=manager.id,
            name=existing_room.name,
            price=Decimal("100.0"),
            quantity=5,
        )

        assert room_id is None

    async def test_update_room_success(self, room_adapter, existing_room):
        """Test updating room."""
        updated_id = await room_adapter.update_room(
            room=existing_room,
            name="Updated Room Name",
            price=Decimal("200.0"),
        )

        assert updated_id is not None
        assert updated_id == existing_room.id

        updated_room = await room_adapter.get_room(existing_room.id)
        assert updated_room.name == "Updated Room Name"
        assert updated_room.price == Decimal("200.0")

    async def test_update_room_partial(self, room_adapter, existing_room):
        """Test partial update of room."""
        original_name = existing_room.name

        updated_id = await room_adapter.update_room(
            existing_room,
            price=Decimal("250.0"),
        )

        assert updated_id == existing_room.id

        updated_room = await room_adapter.get_room(existing_room.id)
        assert updated_room.name == original_name
        assert updated_room.price == Decimal("250.0")

    async def test_update_room_duplicate_name(self, room_adapter, existing_room, sample_room):
        """Test updating room with duplicate name."""
        updated_id = await room_adapter.update_room(existing_room, name=sample_room.name)

        assert updated_id is None

    async def test_delete_room_success(self, room_adapter, manager, sample_hotel):
        """Test deleting room."""
        new_room = Room(
            hotel_id=sample_hotel.id,
            owner=manager.id,
            name="Room to Delete",
            price=Decimal("100.0"),
            quantity=5,
        )
        room_id = await room_adapter.add_room(
            hotel_id=new_room.hotel_id,
            owner=new_room.owner,
            name=new_room.name,
            price=new_room.price,
            quantity=new_room.quantity,
        )

        created_room = await room_adapter.get_room(room_id)
        await room_adapter.delete_room(created_room)

        deleted_room = await room_adapter.get_room(room_id)
        assert deleted_room is None

    async def test_list_rooms_with_multiple_filters(self, room_adapter, sample_hotel):
        """Test listing rooms with multiple filters."""
        result = await room_adapter.list_rooms(
            sample_hotel.id, price_from=Decimal("50.0"), price_to=Decimal("150.0"), services={"wifi": True}
        )

        assert all(
            Decimal("50.0") <= room.price <= Decimal("150.0") and room.services and room.services.get("wifi") is True
            for room in result
        )

    async def test_list_rooms_different_hotels(self, room_adapter, hotel, sample_hotel, rooms):
        """Test listing rooms for different hotels."""
        hotel_rooms = await room_adapter.list_rooms(hotel.id)
        sample_hotel_rooms = await room_adapter.list_rooms(sample_hotel.id)

        assert all(room.hotel_id == hotel.id for room in hotel_rooms)
        assert all(room.hotel_id == sample_hotel.id for room in sample_hotel_rooms)
        assert len(hotel_rooms) >= 3
