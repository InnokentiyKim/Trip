from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from src.apps.authentication.provider.application.service import ProviderService
from src.apps.authentication.provider.controllers.dto import request, response
from src.apps.authentication.provider.domain import commands as provider_commands
from src.apps.authentication.session.application import exceptions as session_exceptions
from src.apps.authentication.session.application.service import AuthenticationService
from src.apps.authentication.session.domain import fetches as session_fetches
from src.apps.authentication.session.domain.enums import OAuthProviderEnum
from src.apps.authentication.user.application.exceptions import Unauthorized
from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.access.domain import commands as authorization_commands
from src.apps.authorization.access.domain.enums import ResourceTypeEnum, UserPermissionEnum
from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header

router = APIRouter(prefix="/connectors", tags=["Connector API"])


@router.post(
    "/{provider}/callback",
    status_code=status.HTTP_200_OK,
    responses=generate_responses(
        Unauthorized,
        session_exceptions.ExchangeOAuthCodeError,
    ),
)
@inject
async def oauth_callback(
    provider: OAuthProviderEnum,
    dto: request.ProviderOAuthCallbackRequestDTO,
    authentication_service: FromDishka[AuthenticationService],
    provider_service: FromDishka[ProviderService],
    authorization_service: FromDishka[AccessService],
    token: str = auth_header,
) -> response.ProviderResponseDTO:
    """
    Handle OAuth provider callback and create connector.

    Generic endpoint for any OAuth provider (VPic, Dropbox, Google Drive, etc.).

    Orchestrates:
    1. Authorization check (workspace admin)
    2. OAuth token exchange via authentication service
    3. Connector creation via connector service
    4. Service query for response
    """
    # Step 1: Authorize user
    await authorization_service.authorize(
        authorization_commands.Authorize(
            access_token=token,
            permission=UserPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.USER,
        )
    )

    # Step 2: Exchange OAuth code for tokens and user info
    oauth_data = await authentication_service.get_oauth_provider_data(
        session_fetches.GetOAuthProviderData(
            code=dto.code,
            provider=provider,
        )
    )

    # Step 3: Create or update connector
    provider_info = await provider_service.connect_provider(
        provider_commands.ConnectProvider(
            user_id=dto.user_id,
            provider=provider,
            external_user_id=oauth_data.user_info.id,
            external_account_email=oauth_data.user_info.email,
            access_token=oauth_data.access_token.get_secret_value(),
            refresh_token=oauth_data.refresh_token.get_secret_value() if oauth_data.refresh_token else None,
            token_expires_at=oauth_data.expires_at,
            scopes=oauth_data.scopes,
            provider_metadata={"name": oauth_data.user_info.name},
        )
    )

    # Step 4: Return connector info
    provider_dto = response.ProviderResponseDTO.from_model(provider_info)

    return provider_dto
