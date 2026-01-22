from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.apps.comment.domain.models import Comment


@dataclass(slots=True, frozen=True)
class CommentInfo:
    id: UUID
    user_id: UUID
    hotel_id: UUID
    content: str
    rating: int | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model: "Comment") -> "CommentInfo":
        """
        Converts `Comment` domain entity to the `CommentInfo` structure.

        Args:
            model: The `Comment` entity to convert from.

        Returns:
            CommentInfo: A `CommentInfo` structure representing the comment data.
        """
        return cls(
            id=model.id,
            user_id=model.user_id,
            hotel_id=model.hotel_id,
            content=model.content,
            rating=model.rating,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
