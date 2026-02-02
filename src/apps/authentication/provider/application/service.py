from src.apps.authentication.provider.application.ensure import ProviderServiceEnsurance
from src.apps.authentication.provider.application.interfaces.gateway import ProviderGatewayProto
from src.apps.authentication.provider.domain import commands, fetches, results
from src.apps.authentication.provider.domain.models import Provider
from src.common.application.service import ServiceBase
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class ProviderService(ServiceBase):
    """
    Service for managing user providers.

    Handles OAuth-based connections, token management, and provider metadata.
    """

    def __init__(
        self,
        config: Configs,
        adapter: ProviderGatewayProto,
        logger: CustomLoggerProto,
    ) -> None:
        self._config = config
        self._adapter = adapter
        self._logger = logger
        self._ensure = ProviderServiceEnsurance(self._adapter, self._logger)

    async def connect_provider(self, cmd: commands.ConnectProvider) -> results.ProviderInfo:
        """
        Connect a user to an external service provider via OAuth.

        Creates a new Provider aggregate with OAuth tokens.
        If a provider already exists for this user, returns the existing one.

        Args:
            cmd (commands.ConnectProvider): Connect provider command.

        Returns:
            ProviderInfo: Immutable provider information.
        """
        async with self._adapter():
            # Check if connector already exists
            existing_provider = await self._adapter.get_users_provider(
                user_id=cmd.user_id,
                provider=cmd.provider,
            )

            if existing_provider:
                # Update existing connector
                existing_provider.external_user_id = cmd.external_user_id
                existing_provider.external_account_email = cmd.external_account_email
                existing_provider.scopes = cmd.scopes or []
                if cmd.provider_metadata:
                    existing_provider.update_metadata(cmd.provider_metadata)

                # Update or add token
                existing_provider.add_token(
                    access_token=cmd.access_token,
                    refresh_token=cmd.refresh_token,
                    expires_at=cmd.token_expires_at,
                )

                # Reactivate if deactivated
                if not existing_provider.is_active:
                    existing_provider.activate()

                return results.ProviderInfo.from_model(existing_provider)

            # Create new connector
            provider = Provider(
                user_id=cmd.user_id,
                provider=cmd.provider,
                external_user_id=cmd.external_user_id,
                external_account_email=cmd.external_account_email,
                scopes=cmd.scopes,
                provider_metadata=cmd.provider_metadata,
            )

            # Add OAuth token
            provider.add_token(
                access_token=cmd.access_token,
                refresh_token=cmd.refresh_token,
                expires_at=cmd.token_expires_at,
            )

            await self._adapter.add(provider)

            return results.ProviderInfo.from_model(provider)

    async def disconnect_provider(self, cmd: commands.DisconnectProvider) -> results.ProviderInfo:
        """
        Disconnect a user from an external service provider.

        Deactivates the provider (soft delete) and removes OAuth tokens.

        Args:
            cmd (commands.DisconnectProvider): Disconnect provider command.

        Returns:
            ProviderInfo: Immutable provider information.

        Raises:
            ProviderNotFoundError: If provider doesn't exist.
        """
        async with self._adapter():
            provider = await self._ensure.users_provider_exists(
                user_id=cmd.user_id,
                provider=cmd.provider,
            )

            # Deactivate and remove token
            provider.deactivate()
            provider.remove_token()

            return results.ProviderInfo.from_model(provider)

    async def update_provider_token(self, cmd: commands.UpdateProviderToken) -> results.ProviderInfo:
        """
        Update OAuth tokens for an existing provider.

        Typically used after token refresh flow.

        Args:
            cmd (commands.UpdateProviderToken): Update provider token command.

        Returns:
            ProviderInfo: Immutable provider information.

        Raises:
            ProviderNotFoundError: If provider doesn't exist.
        """
        async with self._adapter():
            provider = await self._ensure.provider_exists(cmd.provider_id)

            # Update tokens
            provider.add_token(
                access_token=cmd.access_token,
                refresh_token=cmd.refresh_token,
                expires_at=cmd.token_expires_at,
            )

            return results.ProviderInfo.from_model(provider)

    async def update_provider_metadata(self, cmd: commands.UpdateProviderMetadata) -> results.ProviderInfo:
        """
        Update provider-specific metadata.

        Args:
            cmd (commands.UpdateProviderMetadata): Update provider metadata command.

        Returns:
            ProviderInfo: Immutable provider information.

        Raises:
            ProviderNotFoundError: If provider doesn't exist.
        """
        async with self._adapter():
            provider = await self._ensure.provider_exists(cmd.provider_id)

            provider.update_metadata(cmd.metadata)

            return results.ProviderInfo.from_model(provider)

    async def get_provider_info(self, fetch: fetches.GetProviderInfo) -> results.ProviderInfo:
        """
        Fetch provider information by ID.

        Args:
            fetch (fetches.GetProviderInfo): Get provider info fetch.

        Returns:
            ProviderInfo: Immutable provider information.

        Raises:
            ProviderNotFoundError: If provider doesn't exist.
        """
        async with self._adapter():
            provider = await self._ensure.provider_exists(fetch.provider_id)

            return results.ProviderInfo.from_model(provider)

    async def get_user_providers(self, fetch: fetches.GetUserProviders) -> list[results.ProviderInfo]:
        """
        Fetch all providers for a user.

        Args:
            fetch (fetches.GetUserProviders): Get user providers fetch.

        Returns:
            list[ProviderInfo]: List of immutable provider information.
        """
        async with self._adapter():
            connectors = await self._adapter.list_user_providers(fetch.user_id)

            return [results.ProviderInfo.from_model(provider) for provider in connectors]

    async def get_provider_token(self, fetch: fetches.GetProviderToken) -> results.ProviderTokenInfo:
        """
        Fetch OAuth token for a provider.

        This is used when making API calls to external services.

        Args:
            fetch (fetches.GetProviderToken): Get provider token fetch.

        Returns:
            ProviderTokenInfo: Immutable token information.

        Raises:
            ProviderNotFoundError: If provider doesn't exist.
            ProviderTokenNotFoundError: If provider has no token.
        """
        async with self._adapter():
            provider = await self._ensure.provider_exists(fetch.provider_id)
            token = self._ensure.provider_has_token(provider)

            return results.ProviderTokenInfo.from_model(token)
