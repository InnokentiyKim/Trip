from fastapi import status
from src.common.exceptions.common import BaseError, UniqueConstraintError


class OTPMaxAttemptsExceededError(BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Maximum number of attempts for this OTP code has been reached. Please request a new code."
    loc = "otp_code"


class InvalidOTPCodeError(BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid OTP code"
    loc = "otp_code"


class InvalidRefreshSessionError(BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid refresh session"
    loc = "refresh_token"


class InvalidPasswordResetTokenError(BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid password reset token"
    loc = "password_reset_token"
