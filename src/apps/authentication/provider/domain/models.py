import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from src.common.domain.models import Base


class ProviderBase(MappedAsDataclass, Base):
    """Base class for SQLAlchemy connector ORM models."""

    __abstract__ = True


class ProviderToken(ProviderBase):
    """
    OAuth tokens for external service API access.

    Stores access and refresh tokens for making authenticated API calls to
    external services. Tokens are stored in plain text (not hashed) because
    they need to be retrieved and used for API calls.
    """

    __tablename__ = "provider_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="OAuth access token (plain text)",
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="OAuth refresh token (plain text, if supported by provider)",
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Token expiration timestamp (None if no expiration)",
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    def __init__(
        self,
        provider_id: uuid.UUID,
        access_token: str,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = uuid.uuid4()
        self.provider_id = provider_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        now = created_at or datetime.now(UTC)
        self.created_at = now
        self.updated_at = now
        super().__init__()

    @property
    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) >= self.expires_at

    def update_tokens(
        self,
        access_token: str,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        """Update tokens (e.g., after refresh flow)."""
        self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.updated_at = datetime.now(UTC)

    def __hash__(self) -> int:
        """Hash of the connector token."""
        return hash(self.id)


class Provider(ProviderBase):
    """External service provider (e.g., Google, GitHub) for OAuth connections."""

    __tablename__ = "providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User ID (loose coupling - no foreign key constraint)",
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="External service provider (e.g., 'vpic', 'dropbox', 'google_drive')",
    )

    external_user_id: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="ID of the user in the external service",
    )

    external_account_email: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        comment="Email of the connected external account",
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Soft delete flag - can disable without deleting",
    )

    scopes: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        comment="OAuth scopes granted by the user",
    )

    provider_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Provider-specific metadata (JSON)",
    )

    token: Mapped[ProviderToken | None] = relationship(
        "ProviderToken",
        uselist=False,
        lazy="immediate",
        cascade="all, delete-orphan",
        init=False,
    )

    def __init__(
        self,
        user_id: uuid.UUID,
        provider: str,
        external_user_id: str,
        external_account_email: str,
        scopes: list[str] | None = None,
        provider_metadata: dict[str, Any] | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
    ) -> None:
        self.id = uuid.uuid4()
        self.user_id = user_id
        self.provider = provider
        self.external_user_id = external_user_id
        self.external_account_email = external_account_email
        self.scopes = scopes or []
        self.provider_metadata = provider_metadata or {}
        self.is_active = is_active
        self.token = None  # Initialize token as None

        now = created_at or datetime.now(UTC)
        self.created_at = now
        self.updated_at = now
        super().__init__()

    @property
    def has_token(self) -> bool:
        """Check if provider has an OAuth token."""
        return self.token is not None

    @property
    def is_token_expired(self) -> bool:
        """Check if the provider's OAuth token is expired."""
        if self.token is None:
            return True
        return self.token.is_expired

    def deactivate(self) -> None:
        """Soft delete the provider by marking it as inactive."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Reactivate a previously deactivated provider."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """Update provider-specific metadata (merges with existing)."""
        self.provider_metadata.update(metadata)
        self.updated_at = datetime.now(UTC)

    def add_token(
        self,
        access_token: str,
        refresh_token: str | None = None,
        expires_at: datetime | None = None,
    ) -> None:
        """
        Add or update OAuth token for this provider (aggregate root method).

        Args:
            access_token (str): OAuth access token.
            refresh_token (str | None): OAuth refresh token (if supported by provider).
            expires_at (datetime | None): Token expiration timestamp.
        """
        if self.token is None:
            # Create new token
            self.token = ProviderToken(
                provider_id=self.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
        else:
            # Update existing token
            self.token.update_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
        self.updated_at = datetime.now(UTC)

    def remove_token(self) -> None:
        """Remove OAuth token from this provider (aggregate root method)."""
        if self.token is not None:
            self.token = None
        self.updated_at = datetime.now(UTC)

    def get_token(self) -> ProviderToken | None:
        """
        Get the OAuth token for this provider.

        Returns:
            ProviderToken | None: The OAuth token.
        """
        return self.token

    def __hash__(self) -> int:
        """Hash of the provider."""
        return hash(self.id)
