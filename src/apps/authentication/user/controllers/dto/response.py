from uuid import UUID
from src.common.controllers.dto.base import BaseResponseDTO
from src.common.controllers.dto.base import BaseDTO


class RegisterUserResponseDTO(BaseResponseDTO):
    email: str
    is_active: bool
    access_token: str
    refresh_token: str


    @classmethod
    def from_model(cls, model) -> "RegisterUserResponseDTO":
        return cls(
            id=model.id,
            email=model.email,
            is_active=model.is_active,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
        )


class LoginUserResponseDTO(BaseDTO):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutUserResponseDTO(BaseDTO):
    message: str = "Successfully logged out"


class UserInfoResponseDTO(BaseDTO):
    id: UUID
    email: str
    is_mfa_enabled: bool
    user_type: str
    is_active: bool
