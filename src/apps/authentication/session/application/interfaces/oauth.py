from abc import ABC, abstractmethod

from typing import Protocol

from src.apps.authentication.session.domain.enums import OAuthProviderEnum
from src.apps.authentication.session.domain.results import OAuthProviderData, OAuthProviderUser


class OAuthGatewayProto(ABC):
    @abstractmethod
    async def authorize(self, auth_code: str) -> None:
        """
        Exchange an authorization code for an access token and authorize the adapter.

        Args:
            auth_code (str): The authorization code received from the OAuth
            provider's redirect URL query parameters.
        """
        ...

    @abstractmethod
    async def get_user_info(self) -> OAuthProviderUser:
        """
        Fetch the authenticated user's profile information from the provider.

        Returns:
            OAuthProviderUser: A data structure containing the user's profile
            information obtained from the provider.
        """
        ...

    @abstractmethod
    async def get_token_data(self) -> OAuthProviderData:
        """
        Extract the token data from the provider.

        Returns:
            OAuthProviderData: A data structure containing the token data
        """
        ...


class OAuthAdapterFactoryProto(Protocol):
    @abstractmethod
    def get_adapter(self, oauth_provider: OAuthProviderEnum) -> OAuthGatewayProto:
        """
        Get the appropriate OAuth adapter implementation based on the provider enum.

        Args:
            oauth_provider (OAuthProviderEnum): The OAuth provider enum.

        Returns:
            OAuthAdapterProto: The OAuth adapter implementation.
        """
        ...
