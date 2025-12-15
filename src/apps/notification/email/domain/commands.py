from typing import Any

from src.common.domain.commands import Command


class SendBookingConfirmationEmail(Command):
    email: str
    template_name: str = "booking_confirmation_en.html"
    subject: str = "Booking Confirmation"
    metadata: dict[str, Any] = {}
