from enum import StrEnum


class PasswordResetTokenStatusEnum(StrEnum):
    CREATED = "created"  # Token created
    VERIFIED = "verified"  # Successfully used
    SUPERSEDED = "superseded"  # A newer token was requested


class OTPStatusEnum(StrEnum):
    CREATED = "created"  # OTP created
    VERIFIED = "verified"  # Successfully used
    SUPERSEDED = "superseded"  # A newer OTP was requested
    FAILED = "failed"  # Invalidated due to too many failed attempts
