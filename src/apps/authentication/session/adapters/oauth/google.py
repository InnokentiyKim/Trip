from datetime import UTC, datetime, timedelta

from authlib.integrations.base_client import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from pydantic import SecretStr

from src.apps.authentication.session.adapters.oauth.exceptions import OAuthProviderLoginError
from src.apps.authentication.session.application.interfaces.oauth import OAuthGatewayProto
from src.apps.authentication.session.domain.results import OAuthProviderData, OAuthProviderUser
from src.common.interfaces import CustomLoggerProto
from src.config import Configs


class GoogleOAuthAdapter(OAuthGatewayProto):
    def __init__(
        self,
        configs: Configs,
        logger: CustomLoggerProto,
    ) -> None:
        self.config = configs.auth
        self.logger = logger

        self.client_id = self.config.oauth.google_client_id
        self.client_secret = self.config.oauth.google_client_secret
        self.redirect_uri = self.config.oauth.google_redirect_uri
        self.token_url = self.config.oauth.google_token_url
        self.user_info_url = self.config.oauth.google_user_info_url

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
        try:
            self.oauth_client.token = await self.oauth_client.fetch_token(
                url=self.token_url,
                code=auth_code,
                grant_type="authorization_code",
            )
        except OAuthError as err:
            self.logger.error("Google user authorization failed", error=err.error)
            raise

    async def get_user_info(self) -> OAuthProviderUser:
        """
        Get user information using the access token.

        Returns:
            OAuthUserInfo: The user information from Google.

        Raises:
            OAuthProviderLoginError: If there's an error during the user info retrieval.
        """
        response = await self.oauth_client.get(self.user_info_url)
        if not response.is_success:
            self.logger.error("Google user info retrieval failed", response_text=response.text)
            raise OAuthProviderLoginError

        user_data = response.json()
        return OAuthProviderUser(
            id=f"{user_data['sub']}",
            name=user_data["name"],
            email=user_data["email"],
            picture=user_data.get("picture"),
        )

    async def get_token_data(self) -> OAuthProviderData:
        """
        Get the stored OAuth token data.

        Returns:
            OAuthConnectorData: Token data containing access_token, refresh_token, expires_in, scope, etc.
        """
        user_info = await self.get_user_info()
        token = self.oauth_client.token

        # Convert expires_in (seconds) to datetime
        expires_at = None
        if expires_in := token.get("expires_in"):
            expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))

        # Convert scope (space-separated string) to list
        scopes = None
        if scope_str := token.get("scope"):
            scopes = scope_str.split() if isinstance(scope_str, str) else scope_str

        return OAuthProviderData(
            user_info=user_info,
            access_token=SecretStr(token["access_token"]),
            refresh_token=SecretStr(token["refresh_token"]) if token.get("refresh_token") else None,
            expires_at=expires_at,
            scopes=scopes,
        )
