from abc import abstractmethod
from uuid import UUID

from src.apps.authentication.provider.domain.models import Provider
from src.common.interfaces import GatewayProto


class ProviderGatewayProto(GatewayProto):
    """Gateway protocol for Provider aggregate operations."""

    @abstractmethod
    async def add(self, provider: Provider) -> None:
        """
        Add a new provider to the database.

        Args:
            provider (Provider): The provider aggregate.
        """
        ...

    @abstractmethod
    async def get_by_id(self, provider_id: UUID) -> Provider | None:
        """
        Retrieve a provider by ID.

        Args:
            provider_id (UUID): The unique identifier of the provider.

        Returns:
            Provider | None: The provider aggregate if found, otherwise None.
        """
        ...

    @abstractmethod
    async def get_users_provider(
        self,
        user_id: UUID,
        provider: str,
    ) -> Provider | None:
        """
        Retrieve a provider by user ID and provider name.

        Args:
            user_id (UUID): The user ID.
            provider (str): The provider name (e.g., 'vpic').

        Returns:
            Provider | None: The provider aggregate if found, otherwise None.
        """
        ...

    @abstractmethod
    async def list_user_providers(self, user_id: UUID) -> list[Provider]:
        """
        List all providers for a user.

        Args:
            user_id (UUID): The user ID.

        Returns:
            list[Provider]: List of provider aggregates.
        """
        ...
