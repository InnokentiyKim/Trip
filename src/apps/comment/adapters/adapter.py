from uuid import UUID

from src.apps.comment.application.interfaces.gateway import CommentGatewayProto
from src.apps.comment.domain.excepitions import CommentAlreadyExistsException
from src.apps.comment.domain.models import Comment
from src.common.adapters.adapter import SQLAlchemyGateway


class CommentAdapter(SQLAlchemyGateway, CommentGatewayProto):
    async def add(self, comment: Comment) -> None:
        """Add a new comment."""
        try:
            self.session.add(comment)
            await self.session.commit()
        except Exception:
            raise CommentAlreadyExistsException

    async def update_comment(self, comment: Comment, **params) -> UUID | None:
        """Update an existing comment."""
        for key, value in params.items():
            setattr(comment, key, value)
        await self.add_item(comment)
        return comment.id

    async def delete_comment(self, comment: Comment) -> None:
        """Delete a comment by its ID."""
        await self.delete_item(comment)
