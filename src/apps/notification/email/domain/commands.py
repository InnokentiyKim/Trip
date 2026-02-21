from datetime import date
from typing import Any

from src.common.domain.commands import Command


class SendBookingConfirmationEmail(Command):
    email: str

    hotel_name: str
    date_from: date
    date_to: date
    total_price: float

    template_name: str = "booking_confirmation_en.html"
    subject: str = "Booking Confirmation"
    metadata: dict[str, Any] = {}

    room_numbers: list[str] = []


class SendWelcomeEmail(Command):
    email: str
    template_name: str = "welcome_email_en.html"
    subject: str = "User sign-up"
    metadata: dict[str, Any] = {}
