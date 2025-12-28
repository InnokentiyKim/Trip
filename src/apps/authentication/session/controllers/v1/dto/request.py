from pydantic import SecretStr

from src.common.controllers.dto.base import BaseRequestDTO


class AuthRefreshSessionRequestDTO(BaseRequestDTO):
    refresh_token: SecretStr
