import uuid
from datetime import datetime, timedelta

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from src.apps.authentication.session.domain.enums import (
    OTPStatusEnum,
    PasswordResetTokenStatusEnum,
)
from src.apps.notification.enums import NotificationChannelEnum
from src.common.domain.models import Base


class AuthenticationBase(MappedAsDataclass, Base):
    """Base class for SQLAlchemy authentication ORM models."""

    __abstract__ = True


class AuthSession(AuthenticationBase):
    """Manages authentication sessions for users."""

    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    hashed_refresh_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __init__(
        self,
        user_id: uuid.UUID,
        hashed_refresh_token: str,
        duration: timedelta,
        created_at: datetime | None,
    ) -> None:
        super().__init__()
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.hashed_refresh_token = hashed_refresh_token
        now = datetime.now()
        self.created_at = created_at or now
        self.expires_at = now + duration

    def __hash__(self) -> int:
        """Returns the hash of the object's id."""
        return hash(self.id)


class PasswordResetToken(AuthenticationBase):
    """Manages password reset tokens for users."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    hashed_reset_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    status: Mapped[PasswordResetTokenStatusEnum] = mapped_column(
        SAEnum(
            PasswordResetTokenStatusEnum,
            name="password_reset_token_status_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [status.value for status in enum_cls],
        ),
        nullable=False,
    )

    def __hash__(self) -> int:
        """Returns the hash of the object's id."""
        return hash(self.id)


class OTPCode(AuthenticationBase):
    """Manages OTP codes for users."""

    __tablename__ = "otp_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    channel: Mapped[NotificationChannelEnum] = mapped_column(
        SAEnum(
            NotificationChannelEnum,
            name="notification_channel_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [channel.value for channel in enum_cls],
        ),
        nullable=False,
    )
    hashed_otp_code: Mapped[str] = mapped_column(String(64), nullable=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    status: Mapped[OTPStatusEnum] = mapped_column(
        SAEnum(
            OTPStatusEnum,
            name="otp_code_status_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [status.value for status in enum_cls],
        ),
        nullable=False,
    )

    def __hash__(self) -> int:
        """Returns the hash of the object's id."""
        return hash(self.id)
