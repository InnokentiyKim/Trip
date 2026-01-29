from datetime import datetime
from typing import Any
from uuid import UUID

from src.common.domain.commands import Command


class ConnectProvider(Command):
    """
    Connect user to an external service provider via OAuth.

    This command creates a new Provider aggregate with OAuth tokens.
    """

    user_id: UUID
    provider: str  # e.g., 'vpic', 'dropbox', 'google_drive'
    external_user_id: str
    external_account_email: str
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    scopes: list[str] | None = None
    provider_metadata: dict[str, Any] | None = None


class DisconnectProvider(Command):
    """
    Disconnect user from an external service provider.

    This command deactivates the connector (soft delete).
    """

    user_id: UUID
    provider: str


class UpdateProviderToken(Command):
    """
    Update OAuth tokens for an existing provider.

    This command is typically used after token refresh.
    """

    provider_id: UUID
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None


class UpdateProviderMetadata(Command):
    """
    Update provider-specific metadata.

    This command allows storing provider-specific data (e.g., VPic plan info).
    """

    provider_id: UUID
    metadata: dict[str, Any]
