from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.apps.hotel.rooms.application import exceptions
from src.apps.hotel.rooms.application.service import RoomService
from src.apps.hotel.rooms.domain import commands
from tests.fixtures.mocks import MockHotel, MockRoom, MockUser


@pytest.fixture
async def room_service(request_container) -> RoomService:
    """Create a room service for testing."""
    return await request_container.get(RoomService)


@pytest.fixture(autouse=True)
async def mock_data(save_instances, user, manager, hotel, rooms, sample_hotel, sample_room, existing_room) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel]))
    await save_instances(MockRoom([*rooms, sample_room, existing_room]))


class TestRoomService:
    async def test_list_rooms_success(self, room_service, hotel, rooms):
        """Test listing all rooms for a hotel."""
        cmd = commands.ListRoomsCommand(hotel_id=hotel.id, services=None, price_from=None, price_to=None)
        result = await room_service.list_rooms(cmd)

        assert result == rooms

    async def test_get_room_success(self, room_service, sample_room):
        """Test getting an existing room."""
        cmd = commands.GetRoomCommand(room_id=sample_room.id)
        result = await room_service.get_room(cmd)

        assert result == sample_room
        assert result.id == sample_room.id

    async def test_get_room_not_found(self, room_service):
        """Test getting a non-existent room."""
        room_id = uuid4()
        cmd = commands.GetRoomCommand(room_id=room_id)

        with pytest.raises(exceptions.RoomNotFoundError):
            await room_service.get_room(cmd)

    async def test_add_room_success(self, room_service, sample_hotel):
        """Test adding a new room."""
        hotel_id = sample_hotel.id
        user_id = sample_hotel.owner

        cmd = commands.AddRoomCommand(
            user_id=user_id,
            hotel_id=hotel_id,
            name="Standard Room",
            price=Decimal("80.0"),
            quantity=10,
            description="Comfortable room",
            services={"wifi": True},
            image_id=None,
        )

        result = await room_service.add_room(cmd)

        assert result is not None
        assert isinstance(result, UUID)

    async def test_add_room_already_exists(self, room_service, sample_room):
        """Test adding a room that already exists in the hotel."""
        cmd = commands.AddRoomCommand(
            user_id=sample_room.owner,
            hotel_id=sample_room.hotel_id,
            name=sample_room.name,
            price=Decimal("100.0"),
            quantity=3,
            description="Existing room",
            services=None,
            image_id=None,
        )

        with pytest.raises(exceptions.RoomAlreadyExistsError):
            await room_service.add_room(cmd)

    async def test_update_room_success(self, room_service, sample_room):
        """Test updating an existing room."""
        cmd = commands.UpdateRoomCommand(
            room_id=sample_room.id,
            user_id=sample_room.owner,
            name="Updated Room",
            price=Decimal("120.0"),
            quantity=None,
            description=None,
            services=None,
            image_id=None,
        )

        result = await room_service.update_room(cmd)

        assert result is not None
        assert result == sample_room.id

    async def test_update_room_not_found(self, room_service, sample_room):
        """Test updating a non-existent room."""
        room_id = uuid4()

        cmd = commands.UpdateRoomCommand(
            user_id=sample_room.owner,
            room_id=room_id,
            name="Updated Room",
            price=None,
            quantity=None,
            description=None,
            services=None,
            image_id=None,
        )

        with pytest.raises(exceptions.RoomNotFoundError):
            await room_service.update_room(cmd)

    async def test_update_room_cannot_be_updated(self, room_service, sample_room, existing_room):
        """Test updating a room with a name that already exists in the same hotel."""
        cmd = commands.UpdateRoomCommand(
            user_id=sample_room.owner,
            room_id=sample_room.id,
            name=existing_room.name,  # This name already exists in the same hotel
            price=None,
            quantity=None,
            description=None,
            services=None,
            image_id=None,
        )

        with pytest.raises(exceptions.RoomCannotBeUpdatedError):
            await room_service.update_room(cmd)

    async def test_delete_room_success(self, room_service, sample_room):
        """Test deleting an existing room."""
        cmd = commands.DeleteRoomCommand(user_id=sample_room.owner, room_id=sample_room.id)
        result = await room_service.delete_room(cmd)

        assert result is None
        # Verify deletion
        cmd = commands.GetRoomCommand(room_id=sample_room.id)
        with pytest.raises(exceptions.RoomNotFoundError):
            await room_service.get_room(cmd)

    async def test_delete_room_not_found(self, room_service, sample_room):
        """Test deleting a non-existent room."""
        cmd = commands.DeleteRoomCommand(user_id=uuid4(), room_id=uuid4())

        with pytest.raises(exceptions.RoomNotFoundError):
            await room_service.delete_room(cmd)
