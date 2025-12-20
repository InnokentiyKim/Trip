from abc import abstractmethod, ABC
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from enum import StrEnum
from typing import Protocol, Any
from uuid import UUID
from src.common.domain.models import ORM_CLS, ORM_OBJ


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
        token_type: TokenTypeEnum,
        user_id: UUID,
        created_at: datetime,
        expires_at: datetime,
    ) -> str:
        """
        Generate a JSON Web Token (JWT).

        Args:
            token_type (TokenTypeEnum): The type of the token (e.g., access, refresh).
            user_id (UUID): The user ID for whom the token is generated.
            created_at (datetime): The creation time of the token.
            expires_at (datetime): The expiration time of the token.

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
            JWTDecodeError: If the token is invalid or cannot be decoded.
        """
        ...


class GatewayProto(ABC):
    def __call__(
        self, *args: Any, **kwargs: Any
    ) -> AbstractAsyncContextManager[UowProto]: #  noqa: E501
        """Return an async context manager for a unit of work."""
        ...


class SQLAlchemyGatewayProto(GatewayProto):
    # TODO: add __call__ method to return UoW instance

    @abstractmethod
    async def add_item(self, item: ORM_OBJ) -> None: ...

    @abstractmethod
    async def get_item_by_id(self, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ: ...

    @abstractmethod
    async def get_one_item(self, orm_cls: ORM_CLS, **filters: Any) -> ORM_OBJ: ...

    @abstractmethod
    async def get_items_list(
        self, orm_cls: ORM_CLS, **filters: Any
    ) -> list[ORM_OBJ]: ...

    @abstractmethod
    async def delete_item(self, orm_obj: ORM_OBJ) -> None: ...
