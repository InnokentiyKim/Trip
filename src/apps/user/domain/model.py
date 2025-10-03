import uuid
from datetime import datetime, UTC

from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedAsDataclass
from sqlalchemy import Integer, String, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from apps.authentication.domain.results import OAuthProviderUser
from src.apps.authentication.domain.enums import OAuthProviderEnum
from src.apps.hotel.hotels.domain.model import Hotel
from src.apps.hotel.bookings.domain.model import Booking
from src.common.domain.models import Base


class UserBase(MappedAsDataclass, Base):
    """Base class for SQLAlchemy user ORM models."""

    __abstract__ = True


class AuthStatus(UserBase):
    __tablename__ = "auth_statuses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    mfa_email_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __init__(self, user_id: int) -> None:
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.last_login_at = None
        self.is_verified = True
        self.is_blocked = False
        self.failed_login_attempts = 0
        self.mfa_sms_enabled = False
        self.mfa_email_enabled = False
        super().__init__()


class OAuthAuth(UserBase):
    __tablename__ = "oauth_auths"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_account")
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider: Mapped[OAuthProviderEnum] = mapped_column(
        SAEnum(
            OAuthProviderEnum,
            name="oauth_provider_enum",
            validate_strings=True,
            values_callable=lambda enum_cls: [provider.value for provider in enum_cls],
        )
    )
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="oauth_auths")

    def __init__(self, user_id: int, provider: OAuthProviderEnum, provider_user_id: str) -> None:
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.provider = provider
        self.provider_user_id = provider_user_id
        self.created_at = datetime.now(UTC)
        super().__init__()

    def __eq__(self, other):
        if not isinstance(other, OAuthAuth):
            raise NotImplementedError
        return self.provider_user_id == other.provider_user_id and self.provider == other.provider


class User(UserBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="user", lazy="joined")
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="user", lazy="joined", uselist=True, cascade="all, delete-orphan"
    )

    auth_status: Mapped[AuthStatus] = relationship(
        "AuthStatus",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )
    oauth_auths: Mapped[list[OAuthAuth]] = relationship(
        "OAuthAuth", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __init__(
        self,
        user_id: int,
        email: str,
        phone: str | None = None,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        self.id = user_id
        self.email = email
        self.phone = phone
        self.name = name
        self.avatar_url = avatar_url
        self.hashed_password = ""
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now
        self.is_active = True

        self.auth_status = AuthStatus(user_id=user_id)

        super().__init__()


    def set_password(self, hashed_password: str) -> None:
        self.hashed_password = hashed_password
        self.updated_at = datetime.now(UTC)

    def bind_oauth(self, oauth_user: OAuthProviderUser, provider: OAuthProviderEnum) -> OAuthAuth:
        if user_oauth := self.get_oauth(oauth_user, provider):
            return user_oauth

        oauth = OAuthAuth(
            user_id=self.id,
            provider=provider,
            provider_user_id=oauth_user.id,
        )
        self.avatar_url = oauth_user.picture
        self.oauth_auths.append(oauth)
        return oauth

    def get_oauth(self, oauth_user: OAuthProviderUser, provider: OAuthProviderEnum) -> OAuthAuth | None:
        return next(
            (
                user_oauth
                for user_oauth in self.oauth_auths
                if user_oauth.provider == provider and user_oauth.provider_user_id == oauth_user.id
            ),
            None,
        )
