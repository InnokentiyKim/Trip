import uuid

from src.common.controllers.dto.base import BaseDTO


class AddCommentRequestDTO(BaseDTO):
    hotel_id: uuid.UUID
    content: str
    rating: int | None = None


class ListCommentsRequestDTO(BaseDTO):
    hotel_id: uuid.UUID
    rating: int | None = None


class UpdateCommentRequestDTO(BaseDTO):
    content: str | None = None
    rating: int | None = None
