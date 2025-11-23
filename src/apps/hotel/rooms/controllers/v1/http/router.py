from fastapi import APIRouter

from apps.hotel.rooms.controllers.v1.dto.response import UpdateRoomResponseDTO
from src.apps.hotel.rooms.application.service import RoomService
from src.apps.hotel.rooms.controllers.v1.dto.request import UpdateRoomRequestDTO, \
    DeleteRoomRequestDTO, ListRoomsRequestDTO
from src.apps.hotel.rooms.controllers.v1.dto.response import GetRoomResponseDTO, DeleteRoomResponseDTO
from src.apps.hotel.rooms.domain import commands as room_commands
from src.apps.user.domain import commands as user_commands
from src.apps.user.application.service import UserService
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.authentication.application.exceptions import Unauthorized

from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header


router = APIRouter(
    prefix="hotels/",
    tags=["rooms"],
)


@router.get(
    "{hotel_id}/rooms",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def list_rooms(
    hotel_id: int,
    dto: ListRoomsRequestDTO,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> list[GetRoomResponseDTO]:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = room_commands.ListRoomsCommand(
        hotel_id=hotel_id,
        price_from=dto.price_from,
        price_to=dto.price_to,
        services=dto.services,
    )
    rooms = await room_service.list_rooms(cmd)
    return [GetRoomResponseDTO.model_validate(room) for room in rooms]


@router.get(
    "{hotel_id}/rooms/{room_id}",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def get_room(
    hotel_id: int,
    room_id: int,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> GetRoomResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    room = await room_service.get_room(
        room_commands.GetRoomCommand(hotel_id=hotel_id, room_id=room_id)
    )
    return GetRoomResponseDTO.model_validate(room)


@router.post(
    "{hotel_id}/rooms/{room_id}",
    responses=generate_responses(
        Unauthorized,
    )
)
@inject
async def update_room(
    hotel_id: int,
    room_id: int,
    dto: UpdateRoomRequestDTO,
    user_service: FromDishka[UserService],
    room_service: FromDishka[RoomService],
    token: str = auth_header
) -> UpdateRoomResponseDTO:
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = room_commands.UpdateRoomCommand(
        hotel_id=hotel_id,
        room_id=room_id,
        user_id=user.id,
        name=dto.name,
        price=dto.price,
        quantity=dto.quantity,
        description=dto.description,
        services=dto.services,
        image_id=dto.image_id,
    )

    updated_id = await room_service.update_room(cmd)
    return UpdateRoomResponseDTO(id=updated_id)


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
    user = await user_service.verify_user_by_token(
        user_commands.VerifyUserByTokenCommand(token=token)
    )
    cmd = room_commands.DeleteRoomCommand(hotel_id=dto.hotel_id, room_id=room_id, user_id=user.id)
    await room_service.delete_room(cmd)
    return DeleteRoomResponseDTO()
