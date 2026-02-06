from dataclasses import dataclass

from src.apps.authentication.session.domain.enums import OAuthProviderEnum


@dataclass(frozen=True, slots=True)
class GetOAuthProviderUser:
    code: str
    provider: OAuthProviderEnum


@dataclass(frozen=True, slots=True)
class GetOAuthProviderUserByToken:
    token: str
    provider: OAuthProviderEnum


@dataclass(frozen=True, slots=True)
class GetOAuthProviderData:
    """
    Fetch OAuth provider data (user info + tokens) for connector creation.

    Similar to GetOAuthProviderUser but returns token data needed for connectors.
    """

    code: str
    provider: OAuthProviderEnum
