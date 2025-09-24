from src.apps.authentication.adapters.adapter import AuthenticationAdapter
from src.apps.user.adapters.adapter import UserAdapter
from src.apps.user.controllers.dto.response import RegisterUserResponseDTO
from src.apps.user.controllers.dto.request import AuthUserRequestDTO
from src.apps.user.application.service import UserService
from fastapi import APIRouter, Response


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/register")
async def register_user(user_data: AuthUserRequestDTO) -> RegisterUserResponseDTO:
    service = UserService(UserAdapter(), AuthenticationAdapter())
    user = await service.register_user(user_data.email, user_data.password)
    return RegisterUserResponseDTO.from_model(user)


@router.post("/login")
async def login_user(response: Response, user_data: AuthUserRequestDTO) -> str:
    service = UserService(UserAdapter(), AuthenticationAdapter())
    access_token = await service.login_user(user_data.email, user_data.password)
    response.set_cookie("access_token", access_token, expires=3600, httponly=True)
    return access_token
