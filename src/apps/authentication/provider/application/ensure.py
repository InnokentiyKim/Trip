from uuid import UUID

from src.apps.authentication.provider.application.interfaces.gateway import ProviderGatewayProto
from src.apps.authentication.provider.domain.exceptions import ProviderNotFoundError, ProviderTokenNotFoundError
from src.apps.authentication.provider.domain.models import Provider, ProviderToken
from src.common.interfaces import CustomLoggerProto


class ProviderServiceEnsurance:
    """Ensurance helpers for ProviderService."""

    def __init__(self, gateway: ProviderGatewayProto, logger: CustomLoggerProto):
        self._gateway = gateway
        self._logger = logger

    async def provider_exists(self, provider_id: UUID) -> Provider:
        """
        Ensure that a provider exists for the given provider ID.

        Args:
            provider_id (UUID): The provider identifier to check.

        Returns:
            Provider: The provider instance.

        Raises:
            ProviderNotFoundError: If no provider is found with the given ID.
        """
        provider = await self._gateway.get_by_id(provider_id)
        if provider is None:
            raise ProviderNotFoundError

        return provider

    async def users_provider_exists(self, user_id: UUID, provider: str) -> Provider:
        """
        Ensure that a provider exists for the given user and provider.

        Args:
            user_id (UUID): The user identifier to check.
            provider (str): The provider name (e.g., 'vpic').

        Returns:
            Provider: The provider instance.

        Raises:
            ProviderNotFoundError: If no provider is found.
        """
        users_provider = await self._gateway.get_users_provider(
            user_id=user_id,
            provider=provider,
        )
        if users_provider is None:
            raise ProviderNotFoundError

        return users_provider

    def provider_has_token(self, provider: Provider) -> ProviderToken:
        """
        Ensure that a provider has an OAuth token.

        Args:
            provider (Provider): The provider instance to check.

        Returns:
            ProviderToken: The provider token.

        Raises:
            ProviderTokenNotFoundError: If the provider has no token.
        """
        token = provider.get_token()
        if token is None:
            raise ProviderTokenNotFoundError

        return token
