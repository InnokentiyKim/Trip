from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from src.apps.authentication.session.domain.enums import AuthTokenTypeEnum
from src.common.domain.models import ORM_CLS, ORM_OBJ


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
    def bind(self, *args: Any, **kwargs: Any) -> None:
        """Bind additional context variables to the logger."""
        ...

    def unbind(self, *keys: str) -> None:
        """Unbind (remove) previously bound keys from the logger's context."""
        ...

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


class SecurityGatewayProto(Protocol):
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
    async def verify_hashed_password(self, plain_password: str, hashed_password: str) -> bool:
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
    async def create_jwt_token(
        self,
        token_type: AuthTokenTypeEnum,
        user_id: UUID,
        created_at: datetime,
        expires_at: datetime,
    ) -> str:
        """
        Generate a JSON Web Token (JWT).

        Args:
            token_type (AuthTokenTypeEnum): The type of the access_token (e.g., access, refresh).
            user_id (UUID): The user ID for whom the access_token is generated.
            created_at (datetime): The creation time of the access_token.
            expires_at (datetime): The expiration time of the access_token.

        Returns:
            str: The generated JWT as a string.
        """
        ...

    @abstractmethod
    async def decode_jwt_token(self, token: str) -> Any:
        """
        Decode a JSON Web Token (JWT).

        Args:
            token (str): The JWT to decode.

        Returns:
            Any: The decoded payload of the JWT.

        Raises:
            JWTDecodeError: If the access_token is invalid or cannot be decoded.
        """
        ...

    @abstractmethod
    async def verify_token(self, token: str, token_type: AuthTokenTypeEnum) -> UUID:
        """
        Verify a JWT token.

        This method decodes the token and checks its expiration. If the token is valid, it returns the user ID.

        Args:
            token (str): The JWT token to verify.
            token_type (AuthTokenTypeEnum): The type of the access_token (e.g., access, refresh).

        Returns:
            UUID: The user ID extracted from the token if valid.
        """
        ...

    @abstractmethod
    def generate_urlsafe_token(self, nbytes: int = 32) -> str:
        """
        Generate a URL-safe access_token.

        This method creates a random URL-safe access_token using the specified number of bytes.

        Args:
            nbytes (int): The number of random bytes to use for the access_token generation. Default is 32.

        Returns:
            str: A URL-safe access_token string.
        """
        ...

    @abstractmethod
    def generate_otp_code(self) -> str:
        """
        Generate a 6-digit OTP code.

        This method creates a random 6-digit one-time password (OTP) code.

        Returns:
            str: A 6-digit OTP code as a string.
        """
        ...

    @abstractmethod
    def hash_string(self, plain_string: str) -> str:
        """
        Hashes a string.

        Args:
            plain_string (str): The plain string to be hashed.

        Returns:
            str: The hashed string.
        """
        ...

    @abstractmethod
    def verify_hashed_string(self, plain_string: str, hashed_string: str) -> bool:
        """
        Verifies a string against its hashed counterpart.

        Args:
            plain_string (str): The plain string to verify.
            hashed_string (str): The hashed string to verify against.

        Returns:
            bool: True if the string matches the hash, otherwise False.
        """
        ...


class GatewayProto(ABC):
    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> AbstractAsyncContextManager[UowProto]:  # noqa: E501
        """Return an async context manager for a unit of work."""
        ...

    @abstractmethod
    async def add(self, model: Any) -> Any | None:
        """Add a model instance to the gateway."""
        ...


class SQLAlchemyGatewayProto(GatewayProto):
    # TODO: add __call__ method to return UoW instance

    @abstractmethod
    async def add(self, item: ORM_OBJ) -> Any | None:
        """Add an ORM object to the database session."""
        ...

    @abstractmethod
    async def get_item_by_id(self, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ | None:
        """Retrieve an ORM object by its ID."""
        ...

    @abstractmethod
    async def get_one_item(self, orm_cls: ORM_CLS, **filters: Any) -> ORM_OBJ | None:
        """Retrieve a single ORM object matching the given filters."""
        ...

    @abstractmethod
    async def get_items_list(self, orm_cls: ORM_CLS, **filters: Any) -> list[ORM_OBJ]:
        """Retrieve a list of ORM objects matching the given filters."""
        ...

    @abstractmethod
    async def delete_item(self, orm_obj: ORM_OBJ) -> None:
        """Delete an ORM object from the database session."""
        ...
