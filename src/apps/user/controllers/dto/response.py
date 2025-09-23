from apps.user.domain.model import Users
from src.common.controllers.dto.base import BaseDTO
from pydantic import EmailStr


class RegisterUserResponseDTO(BaseDTO):
    id: int
    email: EmailStr
    is_active: bool

    @classmethod
    def from_model(cls, model: "Users") -> "RegisterUserResponseDTO":
        """Create a user response from the user model."""
        fields = {name: getattr(model, name, None) for name in cls.model_fields}
        return cls.model_validate(fields)
