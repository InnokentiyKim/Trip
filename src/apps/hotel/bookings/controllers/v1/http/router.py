from fastapi import APIRouter, Request

from apps.authentication.adapters.adapter import AuthenticationAdapter
from apps.user.adapters.adapter import UserAdapter
from src.apps.user.application.service import UserService
from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.controllers.v1.dto.response import BookingResponseDTO
from src.apps.hotel.bookings.application.service import BookingService


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.get("")
async def get_bookings(request: Request) -> list[BookingResponseDTO]:
    user_service = UserService(UserAdapter(), AuthenticationAdapter())
    service = BookingService(BookingAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user_id = await user_service.verify_user_by_token(token)
    bookings = await service.get_bookings(user_id=user_id)
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_bookings(request: Request, booking_id: int) -> BookingResponseDTO:
    user_service = UserService(UserAdapter(), AuthenticationAdapter())
    service = BookingService(BookingAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user_id = await user_service.verify_user_by_token(token)
    booking = await service.get_booking(booking_id, user_id=user_id)
    return BookingResponseDTO.from_model(booking)
