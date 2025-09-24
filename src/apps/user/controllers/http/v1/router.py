from apps.user.controllers.dto.response import LogoutUserResponseDTO
from src.apps.security.adapters.adapter import SecurityAdapter
from src.apps.user.adapters.adapter import UserAdapter
from src.apps.user.controllers.dto.response import RegisterUserResponseDTO, LoginUserResponseDTO
from src.apps.user.controllers.dto.request import AuthUserRequestDTO
from src.apps.user.application.service import UserService
from fastapi import APIRouter, Response


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/register")
async def register_user(user_data: AuthUserRequestDTO) -> RegisterUserResponseDTO:
    service = UserService(UserAdapter(), SecurityAdapter())
    user = await service.register_user(user_data.email, user_data.password)
    return RegisterUserResponseDTO.from_model(user)


@router.post("/login")
async def login_user(response: Response, user_data: AuthUserRequestDTO) -> LoginUserResponseDTO:
    service = UserService(UserAdapter(), SecurityAdapter())
    access_token = await service.login_user(user_data.email, user_data.password)
    response.set_cookie("access_token", access_token, expires=3600, httponly=True)
    return LoginUserResponseDTO(access_token=access_token)


@router.post("/logout")
async def logout_user(response: Response) -> LogoutUserResponseDTO:
    response.delete_cookie("access_token")
    return LogoutUserResponseDTO()


@router.get("/me")
async def get_user_info():
    ...
