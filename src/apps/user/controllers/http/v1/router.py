from src.apps.authentication.adapters.adapter import AuthenticationAdapter
from src.apps.user.adapters.adapter import UserAdapter
from src.apps.user.controllers.dto.response import RegisterUserResponseDTO
from src.apps.user.controllers.dto.request import RegisterUserRequestDTO
from src.apps.user.application.service import UserService
from fastapi import APIRouter


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/register")
async def register_user(user_data: RegisterUserRequestDTO) -> RegisterUserResponseDTO:
    service = UserService(UserAdapter(), AuthenticationAdapter())
    user = await service.register_user(user_data.email, user_data.password)
    return RegisterUserResponseDTO.from_model(user)
