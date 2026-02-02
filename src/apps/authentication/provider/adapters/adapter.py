from uuid import UUID

from sqlalchemy import select

from src.apps.authentication.provider.application.interfaces.gateway import ProviderGatewayProto
from src.apps.authentication.provider.domain.models import Provider
from src.common.adapters.adapter import SQLAlchemyGateway


class ProviderAdapter(SQLAlchemyGateway, ProviderGatewayProto):
    """SQLAlchemy implementation of ProviderGatewayProto."""

    async def add(self, provider: Provider) -> None:
        """
        Add a new provider aggregate to the database.

        Args:
            provider (Provider): The provider aggregate.
        """
        self.session.add(provider)
        await self.session.commit()

    async def get_by_id(self, provider_id: UUID) -> Provider | None:
        """
        Retrieve a provider aggregate by ID.

        Args:
            provider_id (UUID): The unique identifier of the provider.

        Returns:
            Provider | None: The provider aggregate if found, otherwise None.
        """
        stmt = select(Provider).where(Provider.id == provider_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_users_provider(
        self,
        user_id: UUID,
        provider: str,
    ) -> Provider | None:
        """
        Retrieve a provider aggregate by user ID and provider name.

        Args:
            user_id (UUID): The user ID.
            provider (str): The provider name (e.g., 'vpic').

        Returns:
            Provider | None: The provider aggregate if found, otherwise None.
        """
        stmt = (
            select(Provider)
            .where(
                Provider.user_id == user_id,
                Provider.provider == provider,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_providers(self, user_id: UUID) -> list[Provider]:
        """
        List all providers for a user.

        Args:
            user_id (UUID): The user ID.

        Returns:
            list[Provider]: List of provider aggregates.
        """
        stmt = select(Provider).where(Provider.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
