from uuid import UUID

from src.apps.comment.application.interfaces.gateway import CommentGatewayProto
from src.apps.comment.domain.excepitions import CommentAlreadyExistsException
from src.apps.comment.domain.models import Comment
from src.common.adapters.adapter import SQLAlchemyGateway, FakeGateway
from sqlalchemy import select


class CommentAdapter(SQLAlchemyGateway, CommentGatewayProto):
    async def add(self, comment: Comment) -> None:
        """Add a new comment."""
        try:
            self.session.add(comment)
            await self.session.commit()
        except Exception:
            raise CommentAlreadyExistsException

    async def get_comment_by_id(self, comment_id: UUID) -> Comment:
        """Retrieve a comment by its ID."""
        comment = await self.get_item_by_id(Comment, comment_id)
        return comment

    async def get_comments_by_user_id(self, user_id: UUID) -> list[Comment]:
        """Retrieve a list of comments made by a specific user."""
        result = await self.session.execute(
            select(Comment).where(Comment.user_id == user_id)
        )

        return list(result.scalars())

    async def get_comments_by_hotel_id(self, hotel_id: int) -> list[Comment]:
        """Retrieve a list of comments for a specific hotel."""
        result = await self.session.execute(
            select(Comment).where(Comment.hotel_id == hotel_id)
        )

        return list(result.scalars())

    async def update_comment(self, comment: Comment, **params) -> UUID | None:
        """Update an existing comment."""
        for key, value in params.items():
            setattr(comment, key, value)
        await self.add(comment)
        return comment.id

    async def delete_comment(self, comment: Comment) -> None:
        """Delete a comment by its ID."""
        await self.delete_item(comment)


class FakeCommentAdapter(FakeGateway[Comment], CommentGatewayProto):
    async def add(self, comment: Comment) -> None:
        """Add a new comment."""
        self._collection.add(comment)

    async def get_comment_by_id(self, comment_id: UUID) -> Comment:
        """Retrieve a comment by its ID."""
        return next((comment for comment in self._collection if comment.id == comment_id), None)

    async def get_comments_by_user_id(self, user_id: UUID) -> list[Comment]:
        """Retrieve a list of comments made by a specific user."""
        return [comment for comment in self._collection if comment.user_id == user_id]

    async def get_comments_by_hotel_id(self, hotel_id: int) -> list[Comment]:
        """Retrieve a list of comments for a specific hotel."""
        return [comment for comment in self._collection if comment.hotel_id == hotel_id]

    async def update_comment(self, comment: Comment, **params) -> UUID | None:
        """Update an existing comment."""
        for key, value in params.items():
            setattr(comment, key, value)

        self._collection.discard(comment)
        self._collection.add(comment)

        return comment.id or None

    async def delete_comment(self, comment: Comment) -> None:
        """Delete a comment by its ID."""
        self._collection.discard(comment)
