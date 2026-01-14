from dishka import Provider, Scope, provide, provide_all, AsyncContainer

from src.apps.authentication.config import AuthGatewayEnum
from src.apps.authentication.session.adapters.adapter import AuthSessionAdapter, PasswordResetTokenAdapter, \
    OTPCodeAdapter, FakeAuthSessionAdapter, FakePasswordResetTokenAdapter, FakeOTPCodeAdapter
from src.apps.authentication.session.application.ensure import AuthenticationServiceEnsurance
from src.apps.authentication.session.application.interfaces.gateway import (
    AuthSessionGatewayProto, PasswordResetTokenGatewayProto, OTPCodeGatewayProto
)
from src.apps.authentication.session.application.service import AuthenticationService
from src.apps.authentication.user.adapters.adapter import UserAdapter, FakeUserAdapter
from src.apps.authentication.user.application.ensure import UserServiceEnsurance
from src.apps.authentication.user.application.interfaces.gateway import UserGatewayProto
from src.apps.authentication.user.application.service import UserService
from src.config import Configs


class AuthenticationServiceProviders(Provider):
    scope = Scope.REQUEST

    services = provide_all(
        UserService,
        UserServiceEnsurance,
        AuthenticationService,
        AuthenticationServiceEnsurance,
    )


class AuthenticationGatewayProviders(Provider):
    scope = Scope.REQUEST

    # Register user gateway implementations (not instantiated until requested)
    _alchemy_gateway = provide(UserAdapter)
    _memory_gateway = provide(FakeUserAdapter)

    # Register auth session gateway implementations (not instantiated until requested)
    _alchemy_auth_session_gateway = provide(AuthSessionAdapter)
    _memory_auth_session_gateway = provide(FakeAuthSessionAdapter)

    # Register password reset token gateway implementations (not instantiated until requested)
    _alchemy_password_reset_token_gateway = provide(PasswordResetTokenAdapter)
    _memory_password_reset_token_gateway = provide(FakePasswordResetTokenAdapter)

    # Register OTP code gateway implementations (not instantiated until requested)
    _alchemy_otp_code_gateway = provide(OTPCodeAdapter)
    _memory_otp_code_gateway = provide(FakeOTPCodeAdapter)

    @provide(provides=UserGatewayProto)
    async def provide_user_gateway(self, config: Configs, request_container: AsyncContainer,) -> UserGatewayProto:
        """
        Provide user gateway based on configuration.

        Args:
            config: Application configuration (auto-injected).
            request_container: Dependency injection container.

        Returns:
            UserGatewayProto: Selected gateway implementation.

        Raises:
            ValueError: If configured gateway type is not supported.
        """
        gateway_type = config.authentication.user.gateway

        if gateway_type == AuthGatewayEnum.ALCHEMY:
            return await request_container.get(UserAdapter)
        elif gateway_type == AuthGatewayEnum.MEMORY:
            return await request_container.get(FakeUserAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=AuthSessionGatewayProto)
    async def provide_auth_session_adapter(self, config: Configs, request_container: AsyncContainer) -> AuthSessionGatewayProto:
        gateway_type = config.authentication.auth_session.gateway

        if gateway_type == AuthGatewayEnum.ALCHEMY:
            return await request_container.get(AuthSessionAdapter)
        elif gateway_type == AuthGatewayEnum.MEMORY:
            return await request_container.get(FakeAuthSessionAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=PasswordResetTokenGatewayProto)
    async def provide_password_reset_token_adapter(self, config: Configs, request_container: AsyncContainer) -> PasswordResetTokenGatewayProto:
        gateway_type = config.authentication.password_reset_token.gateway

        if gateway_type == AuthGatewayEnum.ALCHEMY:
            return await request_container.get(PasswordResetTokenAdapter)
        elif gateway_type == AuthGatewayEnum.MEMORY:
            return await request_container.get(FakePasswordResetTokenAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")

    @provide(provides=OTPCodeGatewayProto)
    async def provide_otp_code_adapter(self, config: Configs, request_container: AsyncContainer) -> OTPCodeGatewayProto:
        gateway_type = config.authentication.otp.gateway

        if gateway_type == AuthGatewayEnum.ALCHEMY:
            return await request_container.get(OTPCodeAdapter)
        elif gateway_type == AuthGatewayEnum.MEMORY:
            return await request_container.get(FakeOTPCodeAdapter)
        else:
            raise ValueError(f"Unsupported user gateway: {gateway_type}")


def get_authentication_providers() -> list[Provider]:
    return [
        AuthenticationServiceProviders(),
        AuthenticationGatewayProviders()
    ]
