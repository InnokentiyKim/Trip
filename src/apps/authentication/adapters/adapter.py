from src.apps.authentication.application.interfaces.gateway import AuthenticationGatewayProto
from passlib.context import CryptContext


class AuthenticationAdapter(AuthenticationGatewayProto):
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        """Get the hashed password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
