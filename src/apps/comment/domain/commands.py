import uuid
from src.common.domain.commands import Command


class AddCommentCommand(Command):
    user_id: uuid.UUID
    hotel_id: int
    content: str
    rating: int | None = None


class ListUserCommentsCommand(Command):
    user_id: uuid.UUID


class ListHotelCommentsCommand(Command):
    hotel_id: int


class UpdateCommentInfoCommand(Command):
    comment_id: uuid.UUID
    content: str | None = None
    rating: int | None = None


class DeleteCommentCommand(Command):
    comment_id: uuid.UUID
