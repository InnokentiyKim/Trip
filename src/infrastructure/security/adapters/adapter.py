from datetime import timedelta, datetime, UTC
from uuid import UUID

from jose import jwt, JWTError
from src.infrastructure.security.application.interfaces.gateway import (
    SecurityGatewayProto,
)
from passlib.context import CryptContext
from src.config import Configs
from src.infrastructure.security.application.exceptions import InvalidTokenException


class SecurityAdapter(SecurityGatewayProto):
    def __init__(self, config: Configs) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.config = config

    def get_password_hash(self, password: str) -> str:
        """Get the hashed password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_minutes: int = 30) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expires = datetime.now(UTC) + timedelta(
            minutes=self.config.security.token_expire_minutes
        )
        to_encode.update({"exp": expires})
        encoded_jwt: str = jwt.encode(
            to_encode,
            self.config.security.secret_key,
            algorithm=self.config.security.algorithm,
        )
        return encoded_jwt

    def verify_access_token(self, token: str) -> UUID:
        """Verify a JWT access token."""
        try:
            payload = jwt.decode(
                token, self.config.security.secret_key, self.config.security.algorithm
            )
        except JWTError:
            raise InvalidTokenException
        expire = payload.get("exp")
        if (not expire) or (int(expire) < int(datetime.now(UTC).timestamp())):
            raise InvalidTokenException
        user_id = UUID(payload.get("sub"))
        if not user_id:
            raise InvalidTokenException
        return user_id
