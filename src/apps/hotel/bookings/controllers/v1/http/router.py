from fastapi import HTTPException
from fastapi import APIRouter
from src.apps.hotel.bookings.controllers.v1.dto.response import BookingResponseDTO
from src.apps.hotel.bookings.application.service import BookingService


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.get("")
async def get_bookings() -> list[BookingResponseDTO]:
    bookings = await BookingService().get_bookings()
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_bookings(booking_id: int) -> BookingResponseDTO:
    booking = await BookingService().get_booking_by_id(booking_id)
    if booking:
        return BookingResponseDTO.from_model(booking)
    raise HTTPException(status_code=404, detail="Booking not found")
