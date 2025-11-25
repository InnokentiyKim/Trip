from src.apps.user.controllers.dto.response import LogoutUserResponseDTO
from src.apps.user.controllers.dto.response import (
    RegisterUserResponseDTO,
    LoginUserResponseDTO,
)
from src.apps.user.controllers.dto.request import (
    AuthUserRequestDTO,
    LoginUserRequestDTO,
)
from src.apps.user.application.service import UserService
from src.apps.user.domain import commands as user_commands
from src.common.utils.auth_scheme import auth_header
from fastapi import APIRouter, Response
from dishka.integrations.fastapi import inject, FromDishka


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/register",
)
@inject
async def register_user(
    dto: AuthUserRequestDTO,
    user_service: FromDishka[UserService],
) -> RegisterUserResponseDTO:
    cmd = user_commands.CreateUserCommand(
        email=dto.email,
        password=dto.password,
        name=dto.name,
        phone=dto.phone,
        avatar_url=dto.avatar_url,
        is_active=dto.is_active,
    )
    user = await user_service.register_user(cmd)
    return RegisterUserResponseDTO.from_model(user)


@router.post(
    "/login",
)
@inject
async def login_user(
    response: Response,
    dto: LoginUserRequestDTO,
    user_service: FromDishka[UserService],
) -> LoginUserResponseDTO:
    cmd = user_commands.LoginUserCommand(email=dto.email, password=dto.password)
    access_token = await user_service.login_user(cmd)
    response.set_cookie("access_token", access_token, expires=3600, httponly=True)
    return LoginUserResponseDTO(access_token=access_token)


@router.post(
    "/logout",
)
@inject
async def logout_user(
    response: Response, user_service: FromDishka[UserService], token: str = auth_header
) -> LogoutUserResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    response.delete_cookie("access_token")
    return LogoutUserResponseDTO()


# @router.get("/me")
# async def get_user_info():
#     ...
