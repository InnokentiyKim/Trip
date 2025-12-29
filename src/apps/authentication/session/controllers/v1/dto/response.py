from src.common.controllers.dto.base import BaseDTO


class AuthTokensResponseDTO(BaseDTO):
    access_token: str
    refresh_token: str


class AuthInfoResponseDTO(BaseDTO):
    mfa_email_enabled: bool = False
    mfa_sms_enabled: bool = False
    is_mfa_enabled: bool = False
