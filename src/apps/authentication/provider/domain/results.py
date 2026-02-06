from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from src.apps.authentication.provider.domain.models import Provider, ProviderToken


@dataclass(slots=True, frozen=True)
class ProviderInfo:
    """
    Immutable result representing a Provider aggregate.

    This is returned by service methods instead of the domain model.
    """

    id: UUID
    user_id: UUID
    provider: str
    external_user_id: str
    external_account_email: str
    scopes: list[str]
    provider_metadata: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    has_token: bool
    is_token_expired: bool

    @classmethod
    def from_model(cls, model: Provider) -> "ProviderInfo":
        """
        Create ProviderInfo from Provider domain model.

        Args:
            model (Provider): The Provider aggregate.

        Returns:
            ProviderInfo: Immutable provider information.
        """
        return cls(
            id=model.id,
            user_id=model.user_id,
            provider=model.provider,
            external_user_id=model.external_user_id,
            external_account_email=model.external_account_email,  # type: ignore
            scopes=model.scopes.copy(),  # Defensive copy
            provider_metadata=model.provider_metadata.copy(),  # Defensive copy
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            has_token=model.has_token,
            is_token_expired=model.is_token_expired,
        )


@dataclass(slots=True, frozen=True)
class ProviderTokenInfo:
    """
    Immutable result representing provider OAuth tokens.

    This is used when tokens need to be returned separately
    (e.g., for making API calls to external service).
    """

    provider_id: UUID
    access_token: str
    refresh_token: str | None
    expires_at: datetime | None
    is_expired: bool

    @classmethod
    def from_model(cls, model: ProviderToken) -> "ProviderTokenInfo":
        """
        Create ProviderTokenInfo from ProviderToken domain model.

        Args:
            model (ProviderToken): The ProviderToken entity.

        Returns:
            ProviderTokenInfo: Immutable token information.
        """
        return cls(
            provider_id=model.provider_id,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            expires_at=model.expires_at,
            is_expired=model.is_expired,
        )
