from dishka import AsyncContainer, Provider, Scope, provide, provide_all

from src.apps.authentication.provider.adapters.adapter import ProviderAdapter
from src.apps.authentication.provider.application.ensure import ProviderServiceEnsurance
from src.apps.authentication.provider.application.interfaces.gateway import ProviderGatewayProto
from src.apps.authentication.provider.application.service import ProviderService
from src.apps.authentication.session.adapters.adapter import (
    AuthSessionAdapter,
    OTPCodeAdapter,
    PasswordResetTokenAdapter,
)
from src.apps.authentication.session.application.ensure import (
    AuthenticationServiceEnsurance,
)
from src.apps.authentication.session.application.interfaces.gateway import (
    AuthSessionGatewayProto,
    OTPCodeGatewayProto,
    PasswordResetTokenGatewayProto,
)
from src.apps.authentication.session.application.service import AuthenticationService
from src.apps.authentication.user.adapters.adapter import UserAdapter
from src.apps.authentication.user.application.ensure import UserServiceEnsurance
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.application.service import UserService
from src.common.domain.enums import GatewayTypeEnum
from src.config import Configs


class AuthenticationServiceProviders(Provider):
    """Register authentication service providers."""

    scope = Scope.REQUEST

    services = provide_all(
        AuthenticationService,
        AuthenticationServiceEnsurance,
    )


class UserServiceProviders(Provider):
    """Register user service providers."""

    scope = Scope.REQUEST

    services = provide_all(
        UserService,
        UserServiceEnsurance,
    )


class OAuthServiceProviders(Provider):
    """Register user service providers."""

    scope = Scope.REQUEST

    services = provide_all(
        ProviderService,
        ProviderServiceEnsurance,
    )


class UserGatewayProviders(Provider):
    """Register user gateway providers."""

    scope = Scope.REQUEST

    # Register user gateway implementations (not instantiated until requested)
    _alchemy_user_gateway = provide(UserAdapter)

    @provide(provides=UserGatewayProto)
    async def provide_user_gateway(
        self,
        request_container: AsyncContainer,
    ) -> UserGatewayProto:
        """
        Provide user gateway based on configuration.

        Args:
            request_container: Dependency injection container.

        Returns:
            UserGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(UserAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")


class AuthenticationGatewayProviders(Provider):
    """Register authentication gateway providers."""

    scope = Scope.REQUEST

    # Register auth session gateway implementations (not instantiated until requested)
    _alchemy_auth_session_gateway = provide(AuthSessionAdapter)

    # Register password reset token gateway implementations (not instantiated until requested)
    _alchemy_password_reset_token_gateway = provide(PasswordResetTokenAdapter)

    # Register OTP code gateway implementations (not instantiated until requested)
    _alchemy_otp_code_gateway = provide(OTPCodeAdapter)

    @provide(provides=AuthSessionGatewayProto)
    async def provide_auth_session_adapter(self, request_container: AsyncContainer) -> AuthSessionGatewayProto:
        """
        Provide auth session gateway based on configuration.

        Args:
            request_container: Dependency injection container.

        Returns:
            AuthSessionGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(AuthSessionAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=PasswordResetTokenGatewayProto)
    async def provide_password_reset_token_adapter(
        self, request_container: AsyncContainer
    ) -> PasswordResetTokenGatewayProto:
        """
        Provide password reset token gateway based on configuration.

        Args:
            request_container: Dependency injection container.

        Returns:
            PasswordResetTokenGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(PasswordResetTokenAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=OTPCodeGatewayProto)
    async def provide_otp_code_adapter(self, request_container: AsyncContainer) -> OTPCodeGatewayProto:
        """
        Provide OTP code gateway based on configuration.

        Args:
            request_container: Dependency injection container.

        Returns:
            OTPCodeGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(OTPCodeAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")


class OAuthGatewayProviders(Provider):
    """OAuth Provider with container-based lazy instantiation."""

    scope = Scope.REQUEST

    # Register adapter implementation (not instantiated until requested)
    _alchemy_gateway = provide(ProviderAdapter)

    @provide(provides=ProviderGatewayProto)
    async def provide_provider_gateway(
        self,
        config: Configs,
        request_container: AsyncContainer,
    ) -> ProviderGatewayProto:
        """Provide provider gateway based on configuration.

        Uses container to retrieve only the selected implementation,
        which is instantiated on-demand with all dependencies auto-wired.

        Args:
            config: Application configuration (auto-injected).
            request_container: Dependency injection container.

        Returns:
            ProviderGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = GatewayTypeEnum.ALCHEMY

        if gateway_type == GatewayTypeEnum.ALCHEMY:
            return await request_container.get(ProviderAdapter)
        else:
            raise ValueError(f"Unsupported connector gateway: {gateway_type}")


def get_authentication_providers() -> list[Provider]:
    """Returns the list of authentication service and gateway providers."""
    return [
        AuthenticationServiceProviders(),
        AuthenticationGatewayProviders(),
        UserServiceProviders(),
        UserGatewayProviders(),
        OAuthServiceProviders(),
        OAuthGatewayProviders(),
    ]
