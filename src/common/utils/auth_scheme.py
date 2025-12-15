from fastapi import Request, Security
from src.apps.authentication.user.application.exceptions import Unauthorized
from fastapi.security import HTTPBearer


class AuthHeaderToken(HTTPBearer):
    """Custom HTTP Bearer authentication scheme to extract token from Authorization header."""

    async def __call__(self, request: Request) -> str:
        auth = request.headers.get("Authorization") or request.cookies.get("token")
        if not auth:
            raise Unauthorized

        if not auth.startswith("Bearer"):
            auth = f"Bearer {auth.strip()}"
            request.headers.__dict__["_list"] = [
                (b"authorization", auth.encode())
                if key.lower() == b"authorization"
                else (key, value)
                for key, value in request.headers.raw
            ]

        credentials = await super().__call__(request)
        if credentials is None:
            raise Unauthorized

        return str(credentials.credentials)


bearer_scheme = AuthHeaderToken()
auth_header = Security(bearer_scheme)
