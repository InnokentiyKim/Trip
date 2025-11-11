from uuid import UUID

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject
from src.common.utils.auth_scheme import auth_header

from src.apps.user.application.exceptions import UserNotFoundException
from src.common.exceptions.handlers import generate_responses
from src.apps.user.application.service import UserService
from src.apps.hotel.bookings.controllers.v1.dto.response import BookingResponseDTO
from src.apps.hotel.bookings.application.service import BookingService
from src.common.controllers.dto.base import BaseResponseDTO


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.get(
    "",
    responses=generate_responses(
        UserNotFoundException,
    )
)
@inject
async def get_bookings(
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header
) -> list[BookingResponseDTO]:
    user = await user_service.verify_user_by_token(token=token)
    bookings = await booking_service.get_bookings(user.id)
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get(
    "/{booking_id}",
    responses=generate_responses(
        UserNotFoundException,
    )
)
@inject
async def get_bookings(
    booking_id: UUID,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header
) -> BookingResponseDTO:
    user = await user_service.verify_user_by_token(token)
    booking = await booking_service.get_booking(user.id, booking_id)
    return BookingResponseDTO.from_model(booking)


@router.post(
    "/{booking_id}",
    responses=generate_responses(
        UserNotFoundException,
    )
)
@inject
async def cancel_active_booking(
    booking_id: UUID,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header
) -> BaseResponseDTO:
    user = await user_service.verify_user_by_token(token)
    await booking_service.cancel_active_booking(user.id, booking_id)
    return BaseResponseDTO(id=booking_id)


@router.delete(
    "/{booking_id}",
    responses=generate_responses(
        UserNotFoundException,
    )
)
@inject
async def delete_booking(
    booking_id: UUID,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header
) -> BaseResponseDTO:
    user = await user_service.verify_user_by_token(token)
    await booking_service.delete_booking(user.id, booking_id)
    return BaseResponseDTO(id=booking_id)
