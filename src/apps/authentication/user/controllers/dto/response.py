from uuid import UUID
from src.common.controllers.dto.base import BaseDTO


class UserInfoResponseDTO(BaseDTO):
    id: UUID
    email: str
    is_mfa_enabled: bool
    user_type: str
    is_active: bool
