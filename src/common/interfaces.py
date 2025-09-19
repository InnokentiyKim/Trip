from abc import abstractmethod, ABC
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from enum import StrEnum
from typing import Protocol, Any
from uuid import UUID


class TokenTypeEnum(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    MFA = "mfa"


class UowProto(Protocol, AbstractAsyncContextManager[Any]):
    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back the transaction."""
        ...


class CustomLoggerProto(Protocol):
    def debug(self, *args: Any, **kwargs: Any) -> None:
        """Log a DEBUG-level message."""
        ...

    def info(self, *args: Any, **kwargs: Any) -> None:
        """Log an INFO-level message."""
        ...

    def warning(self, *args: Any, **kwargs: Any) -> None:
        """Log a WARNING-level message."""
        ...

    def error(self, *args: Any, **kwargs: Any) -> None:
        """Log an ERROR-level message."""
        ...

    def critical(self, *args: Any, **kwargs: Any) -> None:
        """Log a CRITICAL-level message."""
        ...

    def exception(self, *args: Any, **kwargs: Any) -> None:
        """Log an exception with traceback information."""
        ...


class SecurityProto(Protocol):
    @abstractmethod
    async def hash_password(self, plain_password: str) -> str:
        """
        Hash a plain text password.

        Args:
            plain_password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """
        ...

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        ...

    @abstractmethod
    async def generate_jwt(
        self,
        token_type: TokenTypeEnum,
        user_id: str | UUID,
        created_at: datetime,
        expires_at: datetime,
    ) -> str:
        """
        Generate a JSON Web Token (JWT).

        Args:
            token_type (TokenTypeEnum): The type of token to generate (e.g., access, refresh).
            user_id (str | UUID): The unique identifier of the user.
            created_at (datetime): The timestamp when the token is created.
            expires_at (datetime): The timestamp when the token expires.

        Returns:
            str: The generated JWT as a string.
        """
        ...

    @abstractmethod
    async def decode_jwt(self, token: str) -> Any:
        """
        Decode a JSON Web Token (JWT).

        Args:
            token (str): The JWT to decode.

        Returns:
            Any: The decoded payload of the JWT.

        Raises:
            JWTDecodeError: If the token is invalid or cannot be decoded.
        """
        ...

    @abstractmethod
    async def generate_otp_code(self) -> str:
        """
        Generate a one-time password (OTP) code.

        Returns:
            str: The generated OTP code.
        """
        ...


class GatewayProto(ABC):

    def __call__(self, *args: Any, **kwargs: Any) -> AbstractAsyncContextManager[UowProto]:
        """Return an async context manager for a unit of work."""
        ...


class SQLAlchemyGatewayProto(GatewayProto):
    # TODO: add __call__ method to return UoW instance

    @abstractmethod
    async def find_all(self, **filters: Any) -> list[Any]:
        """Find all model instances matching the given filters."""
        ...

    @abstractmethod
    async def find_one(self, **filters: Any) -> Any | None:
        """Find a single model instance matching the given filters."""
        ...

    @abstractmethod
    async def find_by_id(self, instance_id: int) -> Any | None:
        """Find a single model instance by its unique identifier."""
        ...
