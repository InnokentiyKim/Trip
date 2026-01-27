import hashlib
import secrets
import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from fastapi.concurrency import run_in_threadpool
from jose import JWTError, jwt

from src.apps.authentication.session.domain.enums import AuthTokenTypeEnum
from src.common.interfaces import CustomLoggerProto, SecurityGatewayProto
from src.config import Configs
from src.infrastructure.security.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
)


class SecurityAdapter(SecurityGatewayProto):
    def __init__(self, config: Configs, logger: CustomLoggerProto) -> None:
        self.config = config
        self.logger = logger

        self.hasher = PasswordHasher(
            time_cost=3,
            memory_cost=12288,
            parallelism=1,
        )

    async def hash_password(self, plain_password: str) -> str:
        """
        Get the hashed password.

        Args:
            plain_password (str): The plain text password to hash.

        Returns:
            str: The hashed password.
        """

        def _hash_password(password: str) -> str:
            return self.hasher.hash(password)

        return await run_in_threadpool(_hash_password, plain_password)

    async def verify_hashed_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if the password matches the hash, otherwise False.
        """

        def _verify_password(plain: str, hashed: str) -> bool:
            try:
                self.hasher.verify(hash=hashed, password=plain)
                return True
            except VerifyMismatchError:
                return False
            except (InvalidHashError, VerificationError):
                self.logger.error("[SecurityAdapter] Password hash verification error")
                return False

        return await run_in_threadpool(_verify_password, plain_password, hashed_password)

    async def create_jwt_token(
        self,
        token_type: AuthTokenTypeEnum,
        user_id: uuid.UUID,
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
        jwt_claims = {
            "sub": f"{user_id}",
            "token_type": token_type,
            "jti": f"{uuid.uuid4()}",
            "iat": created_at,
            "exp": expires_at,
        }

        def _generate_jwt() -> str:
            return jwt.encode(
                claims=jwt_claims,
                key=self.config.auth.jwt.secret_key.get_secret_value(),
                algorithm=self.config.auth.jwt.algorithm,
                headers={"kid": self.config.auth.jwt.jwt_key_id},
            )

        return await run_in_threadpool(_generate_jwt)

    async def decode_jwt_token(self, token: str) -> Any:
        """
        Decodes a JWT access_token.

        This method verifies and decodes a JSON Web Token (JWT) using the configured
        secret key and algorithm. If the access_token format is invalid, an exception is raised.

        Args:
            token (str): The JWT access_token to decode.

        Returns:
            Any: The decoded payload of the JWT access_token.

        Raises:
            JWTError: If the access_token is invalid or cannot be decoded.
        """

        def _decode_jwt() -> Any:
            try:
                return jwt.decode(
                    token=token,
                    key=self.config.auth.jwt.secret_key.get_secret_value(),
                    algorithms=[self.config.auth.jwt.algorithm],
                )
            except JWTError as err:
                self.logger.info(
                    "[Security Adapter] Invalid JWT access_token attempt while decoding",
                    error=f"{err}",
                )
                raise InvalidTokenError from None

        return await run_in_threadpool(_decode_jwt)

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
        payload = await self.decode_jwt_token(token)

        jwt_type = payload.get("token_type")
        expire = payload.get("exp")
        user_id = UUID(payload.get("sub"))

        if token_type != jwt_type:
            self.logger.info("[SecurityAdapter] Invalid token type attempt")
            raise InvalidTokenTypeError

        if not expire or not user_id:
            self.logger.info("[SecurityAdapter] Invalid token attempt")
            raise InvalidTokenError

        if int(expire) < int(datetime.now(UTC).timestamp()):
            self.logger.info("[SecurityAdapter] Expired token attempt")
            raise ExpiredTokenError

        return user_id

    def generate_urlsafe_token(self, nbytes: int = 32) -> str:
        """
        Generate a URL-safe access_token.

        This method creates a random URL-safe access_token using the specified number of bytes.

        Args:
            nbytes (int): The number of random bytes to use for the access_token generation. Default is 32.

        Returns:
            str: A URL-safe access_token string.
        """
        return secrets.token_urlsafe(nbytes)

    def generate_otp_code(self) -> str:
        """
        Generate a 6-digit OTP code.

        This method creates a random 6-digit one-time password (OTP) code.

        Returns:
            str: A 6-digit OTP code as a string.
        """
        return f"{secrets.randbelow(1_000_000):06d}"

    def hash_string(self, plain_string: str) -> str:
        """
        Hashes a string.

        Args:
            plain_string (str): The plain string to be hashed.

        Returns:
            str: The hashed string.
        """
        return hashlib.sha256(plain_string.encode()).hexdigest()

    def verify_hashed_string(self, plain_string: str, hashed_string: str) -> bool:
        """
        Verifies a string against its hashed counterpart.

        Args:
            plain_string (str): The plain string to verify.
            hashed_string (str): The hashed string to verify against.

        Returns:
            bool: True if the string matches the hash, otherwise False.
        """
        plain_hashed_string = hashlib.sha256(plain_string.encode()).hexdigest()
        return secrets.compare_digest(plain_hashed_string, hashed_string)
