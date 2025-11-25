from uuid import UUID

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

from src.apps.hotel.bookings.controllers.v1.dto.request import ListBookingsRequestDTO
from src.common.utils.auth_scheme import auth_header
from src.apps.user.domain import commands as user_commands
from src.apps.hotel.bookings.domain import commands as booking_commands

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
    ),
)
@inject
async def get_bookings(
    dto: ListBookingsRequestDTO,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> list[BookingResponseDTO]:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = booking_commands.ListBookingsCommand(
        user_id=user.id, room_id=dto.room_id, date_from=dto.date_from, status=dto.status
    )
    bookings = await booking_service.list_bookings(cmd)
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get(
    "/{booking_id}",
    responses=generate_responses(
        UserNotFoundException,
    ),
)
@inject
async def get_booking(
    booking_id: UUID,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> BookingResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = booking_commands.GetBookingCommand(user_id=user.id, booking_id=booking_id)
    booking = await booking_service.get_booking(cmd)
    return BookingResponseDTO.from_model(booking)


@router.post(
    "/{booking_id}",
    responses=generate_responses(
        UserNotFoundException,
    ),
)
@inject
async def cancel_active_booking(
    booking_id: UUID,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> BaseResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = booking_commands.CancelActiveBookingCommand(
        user_id=user.id, booking_id=booking_id
    )
    await booking_service.cancel_active_booking(cmd)
    return BaseResponseDTO(id=booking_id)


@router.delete(
    "/{booking_id}",
    responses=generate_responses(
        UserNotFoundException,
    ),
)
@inject
async def delete_booking(
    booking_id: UUID,
    user_service: FromDishka[UserService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> BaseResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = booking_commands.DeleteBookingCommand(user_id=user.id, booking_id=booking_id)
    await booking_service.delete_booking(cmd)
    return BaseResponseDTO(id=booking_id)
