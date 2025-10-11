from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SendPasswordResetSMS:
    phone: str
    otp_code: str
    lifetime_minutes: int
