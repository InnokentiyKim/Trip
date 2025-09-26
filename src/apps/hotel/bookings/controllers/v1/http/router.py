from uuid import UUID

from fastapi import APIRouter, Request

from apps.security.adapters.adapter import SecurityAdapter
from apps.user.adapters.adapter import UserAdapter
from src.apps.user.application.service import UserService
from src.apps.hotel.bookings.adapters.adapter import BookingAdapter
from src.apps.hotel.bookings.controllers.v1.dto.response import BookingResponseDTO
from src.apps.hotel.bookings.application.service import BookingService
from src.common.controllers.dto.base import BaseResponseDTO


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.get("")
async def get_bookings(request: Request) -> list[BookingResponseDTO]:
    user_service = UserService(UserAdapter(), SecurityAdapter())
    service = BookingService(BookingAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user = await user_service.verify_user_by_token(token)
    bookings = await service.get_bookings(user_id=user.id)
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get("/{booking_id}")
async def get_bookings(request: Request, booking_id: UUID) -> BookingResponseDTO:
    user_service = UserService(UserAdapter(), SecurityAdapter())
    service = BookingService(BookingAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user = await user_service.verify_user_by_token(token)
    booking = await service.get_booking_by_id(booking_id, user_id=user.id)
    return BookingResponseDTO.from_model(booking)


@router.post("/{booking_id}")
async def cancel_active_booking(request: Request, booking_id: UUID) -> BaseResponseDTO:
    user_service = UserService(UserAdapter(), SecurityAdapter())
    service = BookingService(BookingAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user = await user_service.verify_user_by_token(token)
    await service.cancel_active_booking(user.id, booking_id)
    return BaseResponseDTO(id=booking_id)


@router.delete("/{booking_id}")
async def delete_booking(request: Request, booking_id: UUID) -> BaseResponseDTO:
    user_service = UserService(UserAdapter(), SecurityAdapter())
    service = BookingService(BookingAdapter())
    token = request.cookies.get("token") or request.headers.get("Authorization")
    user = await user_service.verify_user_by_token(token)
    await service.delete_booking(booking_id, user_id=user.id)
    return BaseResponseDTO(id=booking_id)
