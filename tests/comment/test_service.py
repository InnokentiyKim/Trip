import uuid

import pytest

from src.apps.comment.adapters.adapter import CommentAdapter
from src.apps.comment.application.service import CommentService
from src.apps.comment.domain import commands, fetches
from src.apps.comment.domain.excepitions import CommentNotFoundException, CommentAlreadyExistsException
from src.apps.comment.domain.results import CommentInfo
from tests.fixtures.mocks import MockComment, MockHotel, MockUser


@pytest.fixture
async def comment_service(request_container) -> CommentService:
    """Create a comment service for testing."""
    return await request_container.get(CommentService)


@pytest.fixture
async def comment_adapter(request_container) -> CommentAdapter:
    """Create a comment adapter for testing."""
    return await request_container.get(dependency_type=CommentAdapter)


@pytest.fixture(autouse=True)
async def mock_data(
    save_instances,
    user,
    manager,
    hotel,
    sample_hotel,
    another_hotel,
    comment,
    sample_comment,
) -> None:
    """Save required dependencies to database for tests."""
    await save_instances(MockUser([user, manager]))
    await save_instances(MockHotel([hotel, sample_hotel, another_hotel]))
    await save_instances(MockComment([sample_comment, comment]))


@pytest.mark.anyio
class TestCommentService:
    async def test_add_comment_success(self, comment_service, user, another_hotel):
        """Test adding a new comment."""
        cmd = commands.AddCommentCommand(
            user_id=user.id,
            hotel_id=another_hotel.id,
            content="Another comment content",
            rating=4,
        )

        result = await comment_service.add_comment(cmd)

        assert result is not None
        assert isinstance(result, uuid.UUID)

    async def test_add_comment_without_rating(self, comment_service, manager, hotel):
        """Test adding comment without rating."""
        cmd = commands.AddCommentCommand(
            user_id=manager.id,
            hotel_id=hotel.id,
            content="Comment without rating",
            rating=None,
        )

        result = await comment_service.add_comment(cmd)

        assert result is not None

    async def test_add_comment_already_exists(self, comment_service, user, hotel):
        """Test adding a new comment."""
        cmd = commands.AddCommentCommand(
            user_id=user.id,
            hotel_id=hotel.id,
            content="Existing comment content",
            rating=2,
        )

        with pytest.raises(CommentAlreadyExistsException):
            await comment_service.add_comment(cmd)

    async def test_get_comment_success(self, comment_service, sample_comment):
        """Test getting comment by ID."""
        fetch = fetches.GetCommentInfo(comment_id=sample_comment.id)

        result = await comment_service.get_comment(fetch)

        assert isinstance(result, CommentInfo)
        assert result.id == sample_comment.id
        assert result.content == sample_comment.content

    async def test_get_comment_not_found(self, comment_service):
        """Test getting non-existent comment."""
        fetch = fetches.GetCommentInfo(comment_id=uuid.uuid4())

        with pytest.raises(CommentNotFoundException):
            await comment_service.get_comment(fetch)

    async def test_list_user_comments(self, comment_service, user):
        """Test listing user's comments."""
        fetch = fetches.ListUserComments(user_id=user.id)

        result = await comment_service.list_user_comments(fetch)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(isinstance(comment, CommentInfo) for comment in result)

    async def test_list_hotel_comments(self, comment_service, hotel):
        """Test listing hotel's comments."""
        fetch = fetches.ListHotelComments(hotel_id=hotel.id)

        result = await comment_service.list_hotel_comments(fetch)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(isinstance(comment, CommentInfo) for comment in result)

    async def test_update_comment_info_success(
        self, comment_service, comment_adapter, sample_comment
    ):
        """Test updating comment info."""
        cmd = commands.UpdateCommentInfoCommand(
            comment_id=sample_comment.id,
            content="Updated comment content",
            rating=2,
        )

        await comment_service.update_comment_info(cmd)

        updated_comment = await comment_adapter.get_comment_by_id(sample_comment.id)
        assert updated_comment.content == "Updated comment content"
        assert updated_comment.rating == 2

    async def test_update_comment_info_partial(
        self, comment_service, comment_adapter, sample_comment
    ):
        """Test partial comment update."""
        cmd = commands.UpdateCommentInfoCommand(
            comment_id=sample_comment.id,
            content="Only content updated",
            rating=None,
        )

        await comment_service.update_comment_info(cmd)

        updated_comment = await comment_adapter.get_comment_by_id(sample_comment.id)
        assert updated_comment.content == "Only content updated"

    async def test_update_comment_not_found(self, comment_service):
        """Test updating non-existent comment."""
        cmd = commands.UpdateCommentInfoCommand(
            comment_id=uuid.uuid4(),
            content="Should fail",
            rating=1,
        )

        with pytest.raises(CommentNotFoundException):
            await comment_service.update_comment_info(cmd)

    async def test_delete_comment_success(self, comment_service, comment_adapter, comment):
        """Test deleting comment."""
        cmd = commands.DeleteCommentCommand(comment_id=comment.id)

        await comment_service.delete_comment(cmd)

        deleted_comment = await comment_adapter.get_comment_by_id(comment.id)
        assert deleted_comment is None

    async def test_delete_comment_not_found(self, comment_service):
        """Test deleting non-existent comment."""
        cmd = commands.DeleteCommentCommand(comment_id=uuid.uuid4())

        with pytest.raises(CommentNotFoundException):
            await comment_service.delete_comment(cmd)
