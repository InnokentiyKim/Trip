from uuid import UUID

from src.apps.comment.domain.models import Comment
from src.common.interfaces import GatewayProto


class CommentGatewayProto(GatewayProto):
    async def add(self, comment: Comment) -> None:
        """Add a new comment."""
        ...

    async def update_comment(self, comment: Comment, **params) -> UUID | None:
        """Update an existing comment."""
        ...

    async def delete_comment(self, comment: Comment) -> None:
        """Delete a comment by its ID."""
        ...
