from abc import abstractmethod
from uuid import UUID

from src.apps.comment.domain.models import Comment
from src.common.interfaces import GatewayProto


class CommentGatewayProto(GatewayProto):
    @abstractmethod
    async def add(self, comment: Comment) -> None:
        """Add a new comment."""
        ...

    @abstractmethod
    async def get_comment_by_id(self, comment_id: UUID) -> Comment:
        """Retrieve a comment by its ID."""
        ...

    @abstractmethod
    async def get_comments_by_user_id(self, user_id: UUID) -> list[Comment]:
        """Retrieve a list of comments made by a specific user."""
        ...

    @abstractmethod
    async def get_comments_by_hotel_id(self, hotel_id: int) -> list[Comment]:
        """Retrieve a list of comments for a specific hotel."""
        ...

    @abstractmethod
    async def update_comment(self, comment: Comment, **params) -> UUID | None:
        """Update an existing comment."""
        ...

    @abstractmethod
    async def delete_comment(self, comment: Comment) -> None:
        """Delete a comment by its ID."""
        ...
