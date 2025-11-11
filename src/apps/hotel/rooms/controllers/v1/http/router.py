from fastapi import APIRouter
from src.apps.hotel.rooms.application.exceptions import RoomProcessingErrorException
from src.apps.hotel.rooms.application.service import RoomService
from src.apps.hotel.rooms.controllers.v1.dto.request import GetRoomRequestDTO, UpdateRoomRequestDTO, DeleteRoomRequestDTO
from src.apps.hotel.rooms.controllers.v1.dto.response import GetRoomResponseDTO, DeleteRoomResponseDTO
from src.apps.hotel.rooms.domain.commands import UpdateRoomCommand, DeleteRoomCommand
from src.apps.user.application.service import UserService
from src.common.controllers.dto.base import BaseResponseDTO
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.authentication.application.exceptions import Unauthorized

from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header


router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
)


@router.get(
    "",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def get_rooms(
    hotel_id: int,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> list[GetRoomResponseDTO]:
    user = await user_service.verify_user_by_token(token)
    rooms = await room_service.list_rooms(hotel_id=hotel_id)
    return [GetRoomResponseDTO.model_validate(room) for room in rooms]


@router.get(
    "/{room_id}",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def get_room(
    room_id: int,
    dto: GetRoomRequestDTO,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> GetRoomResponseDTO:
    user = await user_service.verify_user_by_token(token)
    room = await room_service.get_room(hotel_id=dto.hotel_id, room_id=room_id)
    return GetRoomResponseDTO.model_validate(room)


@router.post(
    "/{room_id}",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def update_room(
    room_id: int,
    dto: UpdateRoomRequestDTO,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> BaseResponseDTO:
    user = await user_service.verify_user_by_token(token)
    cmd = UpdateRoomCommand(
        room_id=room_id,
        hotel_id=dto.hotel_id,
        name=dto.name,
        price=dto.price,
        quantity=dto.quantity,
        description=dto.description,
        services=dto.services,
        image_id=dto.image_id,
    )

    is_updated = await room_service.update_room(cmd)
    if is_updated is None:
        raise RoomProcessingErrorException

    return BaseResponseDTO(id=cmd.room_id)


@router.delete(
    "/{room_id}",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def delete_room(
    room_id: int,
    dto: DeleteRoomRequestDTO,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> DeleteRoomResponseDTO:
    user = await user_service.verify_user_by_token(token)
    cmd = DeleteRoomCommand(hotel_id=dto.hotel_id, room_id=room_id)
    await room_service.delete_room(cmd)
    return DeleteRoomResponseDTO()
