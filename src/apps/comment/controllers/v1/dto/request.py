from src.common.controllers.dto.base import BaseDTO


class AddCommentRequestDTO(BaseDTO):
    hotel_id: int
    content: str
    rating: int | None = None


class UpdateCommentRequestDTO(BaseDTO):
    content: str | None = None
    rating: int | None = None
