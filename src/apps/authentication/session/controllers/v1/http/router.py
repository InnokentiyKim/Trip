from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from pydantic import SecretStr

from src.apps.authorization.access.domain import commands as access_commands
from src.apps.authentication.session.application.exceptions import InvalidRefreshSessionError
from src.apps.authentication.session.application.service import AuthenticationService
from src.apps.authentication.session.controllers.v1.dto.request import AuthRefreshSessionRequestDTO
from src.apps.authentication.session.controllers.v1.dto.response import AuthTokensResponseDTO, AuthInfoResponseDTO
from src.apps.authentication.user.application.exceptions import UserNotFoundException, Unauthorized, \
    UserAlreadyExistsException, InvalidCredentialsException
from src.apps.authentication.user.application.service import UserService
from src.apps.authentication.user.controllers.dto.request import AuthUserRequestDTO, LoginUserRequestDTO, \
    LogoutUserRequestDTO
from src.apps.authentication.user.controllers.dto.response import RegisterUserResponseDTO, LoginUserResponseDTO, \
    LogoutUserResponseDTO
from src.apps.authentication.user.domain import commands as user_commands
from src.apps.authentication.session.domain import commands as auth_commands
from src.apps.authorization.access.application.service import AccessService
from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/info",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def get_auth_info(
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> AuthInfoResponseDTO:
    user_info = await access_service.verify_user_by_token(
        cmd=access_commands.VerifyUserByTokenCommand(access_token=token)
    )
    auth_info = user_info.auth_info
    return AuthInfoResponseDTO(
        is_mfa_enabled=auth_info.is_mfa_enabled,
        mfa_email_enabled=auth_info.mfa_email_enabled,
        mfa_sms_enabled=auth_info.mfa_sms_enabled,
    )


@router.post(
    "/signup",
    responses=generate_responses(
        UserAlreadyExistsException,
    )
)
@inject
async def signup(
    dto: AuthUserRequestDTO,
    user_service: FromDishka[UserService],
    auth_service: FromDishka[AuthenticationService],
) -> RegisterUserResponseDTO:
    cmd = user_commands.CreateUserCommand(
        email=dto.email,
        password=dto.password,
        user_type=dto.user_type,
        name=dto.name,
        phone=dto.phone,
        avatar_url=dto.avatar_url,
        is_active=dto.is_active,
    )

    user_info = await user_service.create_new_user(cmd)
    auth_tokens = await auth_service.create_auth_session(
        cmd=auth_commands.CreateAuthSessionCommand(
            user_id=user_info.id
        )
    )

    return RegisterUserResponseDTO(
        id=user_info.id,
        email=user_info.email,
        is_active=user_info.is_active,
        access_token=auth_tokens.access_token.get_secret_value(),
        refresh_token=auth_tokens.refresh_token.get_secret_value(),
    )


@router.post(
    "/login",
    responses=generate_responses(
        UserNotFoundException,
        InvalidCredentialsException,
    )
)
@inject
async def login_user(
    dto: LoginUserRequestDTO,
    user_service: FromDishka[UserService],
    auth_service: FromDishka[AuthenticationService],
) -> LoginUserResponseDTO:
    cmd = auth_commands.LoginUserCommand(email=dto.email, password=dto.password)

    user_info = await user_service.verify_user_credentials(
        cmd=user_commands.VerifyUserCredentialsCommand(
            email=cmd.email,
            password=SecretStr(cmd.password),
        )
    )
    auth_info = user_info.auth_info

    # TODO: add logic if mfa is enabled

    # If MFA is not required, create a refresh session
    auth_tokens = await auth_service.create_auth_session(
        cmd=auth_commands.CreateAuthSessionCommand(
            user_id=user_info.id
        )
    )

    return LoginUserResponseDTO(
        access_token=auth_tokens.access_token.get_secret_value(),
        refresh_token=auth_tokens.refresh_token.get_secret_value()
    )


@router.post(
    "/logout",
    responses=generate_responses(
        InvalidRefreshSessionError,
    )
)
@inject
async def logout_user(
    dto: LogoutUserRequestDTO,
    auth_service: FromDishka[AuthenticationService],
) -> LogoutUserResponseDTO:
    await auth_service.invalidate_refresh_token(
        cmd=auth_commands.InvalidateRefreshTokenCommand(refresh_token=dto.refresh_token)
    )

    return LogoutUserResponseDTO()


@router.post(
    "/refresh",
    responses=generate_responses(
        InvalidRefreshSessionError,
    )
)
@inject
async def refresh_session(
    dto: AuthRefreshSessionRequestDTO,
    auth_service: FromDishka[AuthenticationService],
) -> AuthTokensResponseDTO:
    user_id_info = await auth_service.consume_refresh_token(
        cmd=auth_commands.ConsumeRefreshTokenCommand(refresh_token=dto.refresh_token)
    )

    auth_tokens = await auth_service.create_auth_session(
        cmd=auth_commands.CreateAuthSessionCommand(user_id=user_id_info.id)
    )

    return AuthTokensResponseDTO(
        access_token=auth_tokens.access_token.get_secret_value(),
        refresh_token=auth_tokens.refresh_token.get_secret_value(),
    )
