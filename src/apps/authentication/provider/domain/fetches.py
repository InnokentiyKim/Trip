from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetProviderInfo:
    """Fetch provider information by  ID."""

    provider_id: UUID


@dataclass(frozen=True, slots=True)
class GetUserProviderInfo:
    """
    Fetch provider information by user ID and provider name.

    This is useful for checking if a user is connected to a specific provider.
    """

    user_id: UUID
    provider: str


@dataclass(frozen=True, slots=True)
class GetUserProviders:
    """
    Fetch all providers for a user.

    Returns a list of all active and inactive providers.
    """

    user_id: UUID


@dataclass(frozen=True, slots=True)
class GetProviderToken:
    """
    Fetch OAuth token for a provider.

    This is used when making API calls to external services.
    """

    provider_id: UUID
