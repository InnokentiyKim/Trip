from src.common.controllers.dto.base import BaseDTO


class AuthTokensResponseDTO(BaseDTO):
    access_token: str
    refresh_token: str
