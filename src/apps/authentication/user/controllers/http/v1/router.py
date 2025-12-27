from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.apps.authentication.session.controllers.v1.http.router import router
from src.apps.authentication.user.application.service import UserService
from src.apps.authentication.user.controllers.dto.request import GetUserInfoRequestDTO
from src.apps.authentication.user.controllers.dto.response import UserInfoResponseDTO
from src.apps.authentication.user.domain import fetches


@router.get(
    "/info",
)
@inject
async def get_info(
    dto: GetUserInfoRequestDTO,
    user_service: FromDishka[UserService],
) -> UserInfoResponseDTO:
    user = await user_service.get_user_info(
        fetch=fetches.GetUserInfo(user_id=dto.user_id)
    )

    return UserInfoResponseDTO(id=user.id, email=user.email, user_type=user.role.name, is_active=user.is_active)
