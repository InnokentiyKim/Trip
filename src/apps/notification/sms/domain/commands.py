from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SendOTPPasswordResetSMS:
    phone: str
    otp_code: str
    lifetime_minutes: int
