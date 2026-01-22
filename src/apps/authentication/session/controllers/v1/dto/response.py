from src.common.controllers.dto.base import BaseDTO, BaseResponseDTO


class AuthTokensResponseDTO(BaseDTO):
    access_token: str
    refresh_token: str


class AuthInfoResponseDTO(BaseDTO):
    mfa_email_enabled: bool = False
    mfa_sms_enabled: bool = False
    is_mfa_enabled: bool = False


class RegisterUserResponseDTO(BaseResponseDTO):
    email: str
    is_active: bool
    access_token: str
    refresh_token: str

    @classmethod
    def from_model(cls, model) -> "RegisterUserResponseDTO":
        """Create RegisterUserResponseDTO from model."""
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
