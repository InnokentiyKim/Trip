from fastapi import APIRouter

from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.controllers.v1.dto.response import BookingResponseDTO
from src.apps.hotel.bookings.application.service import BookingService


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.get("")
async def get_bookings() -> list[BookingResponseDTO]:
    service = BookingService(BookingAdapter())
    bookings = await service.get_bookings()
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_bookings(booking_id: int) -> BookingResponseDTO:
    service = BookingService(BookingAdapter())
    booking = await service.get_booking(booking_id)
    return BookingResponseDTO.from_model(booking)
