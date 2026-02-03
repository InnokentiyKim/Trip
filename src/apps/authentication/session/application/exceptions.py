from fastapi import status

from src.common.exceptions.common import BaseError


class OTPMaxAttemptsExceededError(BaseError):
    """Exception raised when the maximum number of attempts for an OTP code has been exceeded."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Maximum number of attempts for this OTP code has been reached. Please request a new code."
    loc = "otp_code"


class InvalidOTPCodeError(BaseError):
    """Exception raised when an invalid OTP code is provided."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid OTP code"
    loc = "otp_code"


class InvalidRefreshSessionError(BaseError):
    """Exception raised when an invalid refresh token is provided."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid refresh token"
    loc = "refresh_token"


class InvalidPasswordResetTokenError(BaseError):
    """Exception raised when an invalid password reset token is provided."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid password reset token"
    loc = "password_reset_token"


class ExchangeOAuthCodeError(BaseError):
    """Exception raised when failing to exchange an OAuth code."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Failed to exchange OAuth code"
    loc = "code"


class UserPhoneNotFoundError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "User phone number not found. Please add a phone number to enable SMS MFA."
    loc = "channel_type"
