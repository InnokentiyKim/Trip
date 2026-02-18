from authlib.integrations.httpx_client import AsyncOAuth2Client

from src.apps.authentication.session.application.interfaces.oauth import OAuthGatewayProto
from src.apps.authentication.session.domain.results import OAuthProviderData, OAuthProviderUser
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class YandexOAuthAdapter(OAuthGatewayProto):
    def __init__(
        self,
        configs: Configs,
        logger: CustomLoggerProto,
    ) -> None:
        self.config = configs.auth
        self.logger = logger

        self.client_id = self.config.oauth.yandex_client_id
        self.client_secret = self.config.oauth.yandex_client_secret
        self.redirect_uri = self.config.oauth.yandex_redirect_uri
        self.token_url = self.config.oauth.yandex_token_url
        self.user_info_url = self.config.oauth.yandex_user_info_url

        self.oauth_client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret.get_secret_value(),
            redirect_uri=self.redirect_uri,
        )

    async def authorize(self, auth_code: str) -> None:
        """
        Exchange an authorization code for an access token and authorize the adapter.

        Args:
            auth_code (str): The authorization code received from the OAuth
            provider's redirect URL query parameters.
        """
        ...

    async def get_user_info(self) -> OAuthProviderUser:
        """
        Fetch the authenticated user's profile information from the provider.

        Returns:
            OAuthProviderUser: A data structure containing the user's profile
            information obtained from the provider.
        """
        ...

    async def get_token_data(self) -> OAuthProviderData:
        """
        Extract the token data from the provider.

        Returns:
            OAuthProviderData: A data structure containing the token data
        """
        ...
