import uuid

from src.common.controllers.dto.base import BaseDTO


class AddCommentResponseDTO(BaseDTO):
    id: uuid.UUID


class UpdateCommentResponseDTO(AddCommentResponseDTO):
    ...


class DeleteCommentResponseDTO(AddCommentResponseDTO):
    ...


class CommentInfoResponseDTO(BaseDTO):
    id: uuid.UUID
    user_id: uuid.UUID
    hotel_id: int
    content: str
    rating: int | None
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, model: "Comment") -> "CommentInfoResponseDTO":
        return cls(
            id=model.id,
            user_id=model.user_id,
            hotel_id=model.hotel_id,
            content=model.content,
            rating=model.rating,
            created_at=model.created_at.isoformat(),
            updated_at=model.updated_at.isoformat(),
        )
