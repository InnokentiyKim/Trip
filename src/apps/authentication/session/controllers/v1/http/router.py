from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from pydantic import SecretStr

import src.apps.authentication.session.domain.commands
from src.apps.authentication.session.application.exceptions import InvalidRefreshSessionError
from src.apps.authentication.session.application.service import AuthenticationService
from src.apps.authentication.session.controllers.v1.dto.request import AuthRefreshSessionRequestDTO
from src.apps.authentication.session.controllers.v1.dto.response import AuthTokensResponseDTO
from src.apps.authentication.user.application.ensure import UserServiceEnsurance
from src.apps.authentication.user.application.exceptions import UserNotFoundException
from src.apps.authentication.user.application.service import UserService
from src.apps.authentication.user.controllers.dto.request import AuthUserRequestDTO, LoginUserRequestDTO, \
    LogoutUserRequestDTO
from src.apps.authentication.user.controllers.dto.response import RegisterUserResponseDTO, LoginUserResponseDTO, \
    LogoutUserResponseDTO
from src.apps.authentication.user.domain import commands as user_commands
from src.apps.authentication.session.domain import commands as auth_commands
from src.common.exceptions.handlers import generate_responses


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/signup",
)
@inject
async def signup(
    dto: AuthUserRequestDTO,
    user_service: FromDishka[UserService],
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

    user = await user_service.create_new_user(cmd)

    return RegisterUserResponseDTO.from_model(user)


@router.post(
    "/login",
    responses=generate_responses(
        UserNotFoundException,
    )
)
@inject
async def login_user(
    dto: LoginUserRequestDTO,
    user_service: FromDishka[UserService],
    user_ensure: FromDishka[UserServiceEnsurance],
    auth_service: FromDishka[AuthenticationService],
) -> LoginUserResponseDTO:
    cmd = src.apps.authentication.session.domain.commands.LoginUserCommand(email=dto.email, password=dto.password)
    user = await user_ensure.user_with_email_exists(cmd.email)

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
        InvalidRefreshSessionError
    )
)
@inject
async def refresh_token(
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
