from src.apps.user.controllers.dto.response import RegisterUserResponseDTO
from src.apps.user.controllers.dto.request import RegisterUserRequestDTO
from fastapi import APIRouter


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/register")
async def register_user(user_data: RegisterUserRequestDTO) -> RegisterUserResponseDTO:
    ...
