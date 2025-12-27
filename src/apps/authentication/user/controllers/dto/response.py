from src.apps.authorization.role.domain.enums import UserRoleEnum
from src.common.controllers.dto.base import BaseResponseDTO
from src.common.controllers.dto.base import BaseDTO


class RegisterUserResponseDTO(BaseResponseDTO):
    email: str
    is_active: bool

    @classmethod
    def from_model(cls, model) -> "RegisterUserResponseDTO":
        return cls(
            id=model.id,
            email=model.email,
            is_active=model.is_active,
        )


class LoginUserResponseDTO(BaseDTO):
    access_token: str
    token_type: str = "bearer"


class LogoutUserResponseDTO(BaseDTO):
    message: str = "Successfully logged out"


class UserInfoResponseDTO(BaseDTO):
    id: int
    email: str
    user_type: UserRoleEnum
    is_active: bool
