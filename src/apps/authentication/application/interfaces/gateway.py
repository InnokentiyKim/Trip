from abc import abstractmethod

from src.common.interfaces import GatewayProto


class AuthenticationGatewayProto(GatewayProto):
    @abstractmethod
    async def get_password_hash(self, password: str) -> str:
        """Get the hashed password."""
        ...

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        ...
