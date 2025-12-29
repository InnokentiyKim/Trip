from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.apps.authentication.session.controllers.v1.http.router import router
from src.apps.authentication.user.controllers.dto.response import UserInfoResponseDTO
from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.role.application.service import RoleManagementService
from src.common.utils.auth_scheme import auth_header
from src.apps.authorization.access.domain import commands as access_commands
from src.apps.authorization.role.domain import fetches


@router.get(
    "/info",
)
@inject
async def get_info(
    access_service: FromDishka[AccessService],
    role_management: FromDishka[RoleManagementService],
    token: str = auth_header,
) -> UserInfoResponseDTO:
    user_info = await access_service.verify_user_by_token(
        cmd=access_commands.VerifyUserByTokenCommand(access_token=token)
    )

    role_info = await role_management.get_role_info(
        fetch=fetches.GetRoleInfo(role_id=user_info.role)
    )

    response = UserInfoResponseDTO(
        id=user_info.id, email=user_info.email, is_mfa_enabled=user_info.auth_info.is_mfa_enabled,
        user_type=role_info.name, is_active=user_info.is_active
    )
    return response
