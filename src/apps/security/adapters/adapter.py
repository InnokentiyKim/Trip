from datetime import timedelta, datetime, UTC
from jose import jwt, JWTError
from src.apps.security.application.interfaces.gateway import SecurityGatewayProto
from passlib.context import CryptContext
from src.config import create_configs
from src.apps.security.application.exceptions import InvalidTokenException

config = create_configs()

class SecurityAdapter(SecurityGatewayProto):
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        """Get the hashed password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(self, data: dict, expires_minutes: int = 30) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expires = datetime.now(UTC) + timedelta(minutes=config.security.token_expire_minutes)
        to_encode.update({"exp": expires})
        encoded_jwt = jwt.encode(to_encode, config.security.secret_key, algorithm=config.security.algorithm)
        return encoded_jwt

    async def verify_access_token(self, token: str) -> int:
        """Verify a JWT access token."""
        try:
            payload = jwt.decode(token, config.security.secret_key, config.security.algorithm)
        except JWTError:
            raise InvalidTokenException
        expire = payload.get("exp")
        if (not expire) or (int(expire) < int(datetime.now(UTC).timestamp())):
            raise InvalidTokenException
        user_id = int(payload.get("sub"))
        if not user_id:
            raise InvalidTokenException
        return user_id
