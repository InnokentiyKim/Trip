from datetime import datetime, UTC

from sqlalchemy.orm import MappedAsDataclass, Mapped, mapped_column
from src.common.domain.models import Base
from sqlalchemy import ForeignKey, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid


class CommentBase(MappedAsDataclass, Base):
    __abstract__ = True


class Comment(CommentBase):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    hotel_id: Mapped[int] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    content: Mapped[str] = mapped_column(String(512), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __init__(
        self,
        hotel_id: int,
        user_id: uuid.UUID,
        content: str,
        rating: int | None = None,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.hotel_id = hotel_id
        self.user_id = user_id
        self.content = content
        self.rating = rating
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now
