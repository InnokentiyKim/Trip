from src.apps.user.domain.models import User
from src.common.controllers.dto.base import BaseDTO
from pydantic import EmailStr


class RegisterUserResponseDTO(BaseDTO):
    email: EmailStr
    is_active: bool

    @classmethod
    def from_model(cls, model: "User") -> "RegisterUserResponseDTO":
        """Create a user response from the user model."""
        fields = {name: getattr(model, name, None) for name in cls.model_fields}
        return cls.model_validate(fields)


class LoginUserResponseDTO(BaseDTO):
    access_token: str
    token_type: str = "bearer"


class LogoutUserResponseDTO(BaseDTO):
    message: str = "Successfully logged out"


class UserInfoResponseDTO(BaseDTO):
    id: int
    email: EmailStr
    is_active: bool

    @classmethod
    def from_model(cls, model: "User") -> "UserInfoResponseDTO":
        """Create a user info response from the user model."""
        fields = {name: getattr(model, name, None) for name in cls.model_fields}
        return cls.model_validate(fields)
