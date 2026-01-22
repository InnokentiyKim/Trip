import uuid

import pytest

from src.apps.comment.adapters.adapter import CommentAdapter
from src.apps.comment.domain.excepitions import CommentAlreadyExistsError
from src.apps.comment.domain.models import Comment
from tests.fixtures.mocks import MockComment, MockHotel, MockUser


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
class TestCommentAdapter:
    """Tests for CommentAdapter."""

    async def test_get_comment_by_id_success(self, comment_adapter, sample_comment):
        """Test getting comment by ID."""
        result = await comment_adapter.get_comment_by_id(sample_comment.id)

        assert result is not None
        assert result.id == sample_comment.id
        assert result.content == sample_comment.content
        assert result.user_id == sample_comment.user_id

    async def test_get_comment_by_id_not_found(self, comment_adapter):
        """Test getting non-existent comment."""
        non_existent_id = uuid.uuid4()
        result = await comment_adapter.get_comment_by_id(non_existent_id)

        assert result is None

    async def test_get_comments_by_user_id(self, comment_adapter, user):
        """Test getting comments by user ID."""
        result = await comment_adapter.get_comments_by_user_id(user.id)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(comment.user_id == user.id for comment in result)

    async def test_get_comments_by_user_id_empty(self, comment_adapter):
        """Test getting comments for user with no comments."""
        non_existent_user_id = uuid.uuid4()
        result = await comment_adapter.get_comments_by_user_id(non_existent_user_id)

        assert result == []

    async def test_get_comments_by_hotel_id(self, comment_adapter, hotel):
        """Test getting comments by hotel ID."""
        result = await comment_adapter.get_comments_by_hotel_id(hotel.id)

        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(comment.hotel_id == hotel.id for comment in result)

    async def test_get_comments_by_hotel_id_empty(self, comment_adapter):
        """Test getting comments for hotel with no comments."""
        non_existent_hotel_id = uuid.uuid4()
        result = await comment_adapter.get_comments_by_hotel_id(non_existent_hotel_id)

        assert result == []

    async def test_add_comment_success(self, comment_adapter, user, another_hotel):
        """Test adding a new comment."""
        comment = Comment(
            hotel_id=another_hotel.id,
            user_id=user.id,
            content="New test comment",
            rating=5,
        )

        await comment_adapter.add(comment)

        saved_comment = await comment_adapter.get_comment_by_id(comment.id)
        assert saved_comment is not None
        assert saved_comment.content == "New test comment"
        assert saved_comment.rating == 5

    async def test_add_comment_already_exists(self, comment_adapter, user, another_hotel):
        """Test adding an existing comment."""
        comment = Comment(
            hotel_id=another_hotel.id,
            user_id=user.id,
            content="New test comment",
            rating=8,
        )

        await comment_adapter.add(comment)

        existing_comment = Comment(
            hotel_id=another_hotel.id,
            user_id=user.id,
            content="New existing comment",
            rating=5,
        )

        with pytest.raises(CommentAlreadyExistsError):
            await comment_adapter.add(existing_comment)

    async def test_update_comment_success(self, comment_adapter, sample_comment):
        """Test updating comment."""
        updated_id = await comment_adapter.update_comment(
            sample_comment,
            content="Updated content",
            rating=3,
        )

        assert updated_id == sample_comment.id

        updated_comment = await comment_adapter.get_comment_by_id(sample_comment.id)
        assert updated_comment.content == "Updated content"
        assert updated_comment.rating == 3

    async def test_delete_comment_success(self, comment_adapter, user, comment):
        """Test deleting comment."""
        await comment_adapter.delete_comment(comment)

        deleted_comment = await comment_adapter.get_comment_by_id(comment.id)
        assert deleted_comment is None
