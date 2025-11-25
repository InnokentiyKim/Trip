from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, JSON, UniqueConstraint

from src.common.domain.models import Base


class Hotel(Base):
    __tablename__ = "hotels"
    __table_args__ = (
        UniqueConstraint("name", "location", name="unq_hotel_name_location"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    services: Mapped[dict] = mapped_column(JSON, nullable=True)
    rooms_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    owner: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    image_id: Mapped[int] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="hotel", lazy="joined")
    rooms = relationship(
        "Room",
        back_populates="hotel",
        lazy="selectin",
        uselist=True,
        cascade="all, delete-orphan",
    )
