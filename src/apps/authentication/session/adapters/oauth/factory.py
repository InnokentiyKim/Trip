from src.apps.authentication.session.adapters.oauth.exceptions import UnsupportedOAuthProviderError
from src.apps.authentication.session.adapters.oauth.google import GoogleOAuthAdapter
from src.apps.authentication.session.adapters.oauth.yandex import YandexOAuthAdapter
from src.apps.authentication.session.application.interfaces.oauth import OAuthAdapterFactoryProto, OAuthGatewayProto
from src.apps.authentication.session.domain.enums import OAuthProviderEnum
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class OAuthAdapterFactory(OAuthAdapterFactoryProto):
    """Factory for creating OAuth adapter instances."""

    def __init__(
        self,
        configs: Configs,
        logger: CustomLoggerProto,
    ) -> None:
        self.configs = configs
        self.logger = logger
        self._adapters: dict[str, OAuthGatewayProto] = {}

    def get_adapter(self, oauth_provider: OAuthProviderEnum) -> OAuthGatewayProto:
        """
        Get the appropriate OAuth adapter implementation based on the provider enum.

        Args:
            oauth_provider (OAuthProviderEnum): The OAuth provider enum.

        Returns:
            OAuthAdapterProto: The OAuth adapter implementation.

        Raises:
            UnsupportedOAuthProviderError: If the provider is not supported.
        """
        if oauth_provider not in self._adapters:
            # noinspection PyUnreachableCode
            match oauth_provider:
                case OAuthProviderEnum.GOOGLE:
                    self._adapters[oauth_provider] = GoogleOAuthAdapter(
                        self.configs,
                        self.logger,
                    )
                case OAuthProviderEnum.YANDEX:
                    self._adapters[oauth_provider] = YandexOAuthAdapter(
                        self.configs,
                        self.logger,
                    )
                case _:
                    self.logger.error("Unsupported OAuth provider", provider=oauth_provider)  # type: ignore[unreachable]
                    raise UnsupportedOAuthProviderError

        return self._adapters[oauth_provider]
