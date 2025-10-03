from abc import abstractmethod

from src.common.interfaces import GatewayProto


class SecurityGatewayProto(GatewayProto):
    @abstractmethod
    async def get_password_hash(self, password: str) -> str:
        """Get the hashed password."""
        ...

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        ...

    @abstractmethod
    async def create_access_token(self, data: dict, expires_minutes: int) -> str:
        """Create a JWT access token."""
        ...

    @abstractmethod
    async def verify_access_token(self, token: str) -> int:
        """Verify a JWT access token."""
        ...
