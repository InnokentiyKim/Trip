import uuid
from src.common.domain.commands import Command


class AddCommentCommand(Command):
    user_id: uuid.UUID
    hotel_id: int
    content: str
    rating: int | None


class UpdateCommentInfoCommand(Command):
    comment_id: uuid.UUID
    content: str | None
    rating: int | None


class DeleteCommentCommand(Command):
    comment_id: uuid.UUID
