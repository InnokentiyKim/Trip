import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated
from unittest.mock import MagicMock

import pytest

from src.apps.authentication.session.domain.enums import AuthTokenTypeEnum
from src.common.interfaces import CustomLoggerProto
from src.infrastructure.security.adapter import SecurityAdapter
from src.infrastructure.security.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
)


@pytest.fixture
def mock_config():
    """Mock configuration for SecurityAdapter."""
    config = MagicMock()
    config.security.secret_key.get_secret_value.return_value = "test-secret-key-12345"
    config.security.algorithm = "HS256"
    config.security.jwt_key_id = "test-key-id"
    return config


@pytest.fixture
def mock_logger():
    """Mock logger for SecurityAdapter."""
    return MagicMock()


@pytest.fixture
def security_adapter(mock_config, mock_logger):
    """Create a SecurityAdapter instance for testing."""
    return SecurityAdapter(config=mock_config, logger=Annotated[mock_logger, CustomLoggerProto])


@pytest.mark.anyio
class TestSecurityAdapter:
    async def test_hash_password_returns_hashed_string(self, security_adapter):
        """Test that hashing a password returns a hashed string."""
        plain_password = "test_password_123"

        hashed = await security_adapter.hash_password(plain_password)

        assert hashed != plain_password
        assert len(hashed) > 0

    async def test_hash_password_different_hashes_for_same_password(self, security_adapter):
        """Test that hashing the same password twice produces different hashes."""
        plain_password = "test_password_123"

        hash1 = await security_adapter.hash_password(plain_password)
        hash2 = await security_adapter.hash_password(plain_password)

        assert hash1 != hash2  # Argon2 uses random salt

    async def test_verify_correct_password(self, security_adapter):
        """Test that verifying the correct password returns True."""
        plain_password = "test_password_123"
        hashed = await security_adapter.hash_password(plain_password)

        result = await security_adapter.verify_hashed_password(plain_password, hashed)

        assert result is True

    async def test_verify_incorrect_password(self, security_adapter):
        """Test that verifying an incorrect password returns False."""
        plain_password = "test_password_123"
        hashed = await security_adapter.hash_password(plain_password)

        result = await security_adapter.verify_hashed_password("wrong_password", hashed)

        assert result is False

    async def test_verify_invalid_hash(self, security_adapter):
        """Test that verifying with an invalid hash returns False."""
        result = await security_adapter.verify_hashed_password("password", "invalid_hash")

        assert result is False

    async def test_create_access_token(self, security_adapter):
        """Test creating an access token."""
        user_id = uuid.uuid4()
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(hours=1)

        token = await security_adapter.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )

        assert isinstance(token, str)
        assert len(token) > 0

    async def test_create_refresh_token(self, security_adapter):
        """Test creating a refresh token."""
        user_id = uuid.uuid4()
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(days=7)

        token = await security_adapter.create_jwt_token(
            token_type=AuthTokenTypeEnum.REFRESH,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )

        assert isinstance(token, str)
        assert len(token) > 0

    async def test_decode_valid_token(self, security_adapter):
        """Test decoding a valid token."""
        user_id = uuid.uuid4()
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(hours=1)

        token = await security_adapter.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )

        payload = await security_adapter.decode_jwt_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["token_type"] == AuthTokenTypeEnum.ACCESS

    async def test_decode_invalid_token(self, security_adapter):
        """Test decoding an invalid token."""
        with pytest.raises(InvalidTokenError):
            await security_adapter.decode_jwt_token("invalid.token.here")

    async def test_verify_valid_access_token(self, security_adapter):
        """Test verifying a valid access token."""
        user_id = uuid.uuid4()
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(hours=1)

        token = await security_adapter.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )

        result = await security_adapter.verify_token(token, AuthTokenTypeEnum.ACCESS)

        assert result == user_id

    async def test_verify_token_wrong_type(self, security_adapter):
        """Test verifying a token with the wrong type."""
        user_id = uuid.uuid4()
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(hours=1)

        token = await security_adapter.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )

        with pytest.raises(InvalidTokenTypeError):
            await security_adapter.verify_token(token, AuthTokenTypeEnum.REFRESH)

    async def test_verify_expired_token(self, security_adapter):
        """Test verifying an expired token."""
        user_id = uuid.uuid4()
        created_at = datetime.now(UTC) - timedelta(hours=2)
        expires_at = created_at + timedelta(hours=1)  # Already expired

        token = await security_adapter.create_jwt_token(
            token_type=AuthTokenTypeEnum.ACCESS,
            user_id=user_id,
            created_at=created_at,
            expires_at=expires_at,
        )

        with pytest.raises(tuple([InvalidTokenError, ExpiredTokenError])):
            await security_adapter.verify_token(token, AuthTokenTypeEnum.ACCESS)

    def test_generate_urlsafe_token_default_length(self, security_adapter):
        """Test generating a URL-safe token with default length."""
        token = security_adapter.generate_urlsafe_token()

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_urlsafe_token_custom_length(self, security_adapter):
        """Test generating a URL-safe token with custom length."""
        token = security_adapter.generate_urlsafe_token(nbytes=64)

        assert isinstance(token, str)
        assert len(token) > 43  # Base64 encoding increases length

    def test_generate_urlsafe_token_unique(self, security_adapter):
        """Test that multiple generated tokens are unique."""
        token1 = security_adapter.generate_urlsafe_token()
        token2 = security_adapter.generate_urlsafe_token()

        assert token1 != token2

    def test_generate_otp_code_format(self, security_adapter):
        """Test generating an OTP code with correct format."""
        otp = security_adapter.generate_otp_code()

        assert len(otp) == 6
        assert otp.isdigit()

    def test_generate_otp_code_unique(self, security_adapter):
        """Test that multiple generated OTP codes are unique."""
        codes = {security_adapter.generate_otp_code() for _ in range(100)}

        assert len(codes) > 90  # High probability of uniqueness

    def test_hash_string(self, security_adapter):
        """Test hashing a string."""
        plain_string = "test_string"

        hashed = security_adapter.hash_string(plain_string)

        assert hashed != plain_string
        assert len(hashed) == 64  # SHA256 hex digest

    def test_hash_string_deterministic(self, security_adapter):
        """Test that hashing the same string produces the same hash."""
        plain_string = "test_string"

        hash1 = security_adapter.hash_string(plain_string)
        hash2 = security_adapter.hash_string(plain_string)

        assert hash1 == hash2

    def test_verify_correct_string(self, security_adapter):
        """Test verifying the correct string against its hash."""
        plain_string = "test_string"
        hashed = security_adapter.hash_string(plain_string)

        result = security_adapter.verify_hashed_string(plain_string, hashed)

        assert result is True

    def test_verify_incorrect_string(self, security_adapter):
        """Test verifying an incorrect string against a hash."""
        hashed = security_adapter.hash_string("test_string")

        result = security_adapter.verify_hashed_string("wrong_string", hashed)

        assert result is False
