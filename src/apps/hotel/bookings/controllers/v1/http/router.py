from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query

from src.apps.authentication.user.application.exceptions import (
    Unauthorized,
    UserNotFoundError,
)
from src.apps.authorization.access.application.service import AccessService
from src.apps.authorization.access.domain import commands as access_commands
from src.apps.authorization.access.domain.commands import Authorize
from src.apps.authorization.access.domain.enums import (
    BookingPermissionEnum,
    ResourceTypeEnum,
)
from src.apps.authorization.access.domain.exceptions import Forbidden
from src.apps.hotel.bookings.application.exceptions import (
    BookingCannotBeCancelledError,
    BookingNotFoundError,
    InvalidBookingDatesError,
    RoomCannotBeBookedError,
)
from src.apps.hotel.bookings.application.service import BookingService
from src.apps.hotel.bookings.controllers.v1.dto.request import (
    CreateBookingRequestDTO,
    ListBookingsRequestDTO,
)
from src.apps.hotel.bookings.controllers.v1.dto.response import BookingResponseDTO
from src.apps.hotel.bookings.domain import commands as booking_commands
from src.apps.notification.email.application.service import EmailService
from src.common.controllers.dto.base import BaseResponseDTO
from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.get(
    "",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
    ),
)
@inject
async def get_bookings(
    filter_query: Annotated[ListBookingsRequestDTO, Query()],
    access_service: FromDishka[AccessService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> list[BookingResponseDTO]:
    """Get a list of bookings with optional filters."""
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=BookingPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.BOOKING,
        )
    )
    cmd = booking_commands.ListBookingsCommand(
        user_id=authorization_info.user_id,
        room_id=filter_query.room_id,
        date_from=filter_query.date_from,
        date_to=filter_query.date_to,
        status=filter_query.status,
    )

    bookings = await booking_service.list_bookings(cmd)
    return [BookingResponseDTO.from_model(booking) for booking in bookings]


@router.get(
    "/{booking_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        BookingNotFoundError,
    ),
)
@inject
async def get_booking(
    booking_id: UUID,
    access_service: FromDishka[AccessService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> BookingResponseDTO:
    """Get details of a specific booking by its ID."""
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=BookingPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.BOOKING,
        )
    )

    cmd = booking_commands.GetBookingCommand(user_id=authorization_info.user_id, booking_id=booking_id)

    booking = await booking_service.get_booking(cmd)
    return BookingResponseDTO.from_model(booking)


@router.post(
    "",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        InvalidBookingDatesError,
        RoomCannotBeBookedError,
    ),
)
@inject
async def add_booking(
    dto: CreateBookingRequestDTO,
    access_service: FromDishka[AccessService],
    booking_service: FromDishka[BookingService],
    email_service: FromDishka[EmailService],
    token: str = auth_header,
) -> BookingResponseDTO:
    """Create a new booking."""
    await access_service.verify_user_by_token(cmd=access_commands.VerifyUserByTokenCommand(access_token=token))
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=BookingPermissionEnum.CAN_CREATE,
            resource_type=ResourceTypeEnum.BOOKING,
        )
    )

    cmd = booking_commands.CreateBookingCommand(
        user_id=authorization_info.user_id,
        room_id=dto.room_id,
        date_from=dto.date_from,
        date_to=dto.date_to,
    )
    booking = await booking_service.create_booking(cmd)

    # await email_service.send_booking_confirmation_email(
    #     email_commands.SendBookingConfirmationEmail(
    #         email=user_info.email, metadata={"booking": booking}
    #     )
    # )
    return BookingResponseDTO.from_model(booking)


@router.post(
    "/{booking_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundError,
        BookingNotFoundError,
        BookingCannotBeCancelledError,
    ),
)
@inject
async def cancel_active_booking(
    booking_id: UUID,
    access_service: FromDishka[AccessService],
    booking_service: FromDishka[BookingService],
    token: str = auth_header,
) -> BaseResponseDTO:
    """Cancel an active booking."""
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=BookingPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.BOOKING,
            resource_id=booking_id,
        )
    )

    cmd = booking_commands.CancelActiveBookingCommand(user_id=authorization_info.user_id, booking_id=booking_id)

    await booking_service.cancel_active_booking(cmd)
    return BaseResponseDTO(id=booking_id)
