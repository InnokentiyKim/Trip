from abc import abstractmethod
from uuid import UUID

from src.common.interfaces import GatewayProto


class SecurityGatewayProto(GatewayProto):
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        """Get the hashed password."""
        ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        ...

    @abstractmethod
    def create_access_token(self, data: dict, expires_minutes: int | None = None) -> str:
        """Create a JWT access token."""
        ...

    @abstractmethod
    def verify_access_token(self, token: str) -> UUID:
        """Verify a JWT access token."""
        ...
