from fastapi import APIRouter, Query
from typing import Annotated
from src.apps.authorization.access.domain.commands import Authorize
from src.apps.authorization.access.domain.enums import RoomPermissionEnum, ResourceTypeEnum
from src.apps.authorization.access.domain.exceptions import Forbidden
from src.apps.hotel.hotels.application.exceptions import HotelNotFoundException
from src.apps.hotel.rooms.application.exceptions import RoomNotFoundException, RoomCannotBeUpdatedException, \
    RoomAlreadyExistsException
from src.apps.hotel.rooms.controllers.v1.dto.response import UpdateRoomResponseDTO, AddRoomResponseDTO
from src.apps.hotel.rooms.application.service import RoomService
from src.apps.hotel.rooms.controllers.v1.dto.request import (
    UpdateRoomRequestDTO,
    ListRoomsRequestDTO, AddRoomRequestDTO,
)
from src.apps.hotel.rooms.controllers.v1.dto.response import (
    GetRoomResponseDTO,
    DeleteRoomResponseDTO,
)
from src.apps.hotel.rooms.domain import commands as room_commands
from src.apps.authorization.access.application.service import AccessService
from dishka.integrations.fastapi import FromDishka, inject
from src.apps.authentication.user.application.exceptions import Unauthorized, UserNotFoundException

from src.common.exceptions.handlers import generate_responses
from src.common.utils.auth_scheme import auth_header


router = APIRouter(
    prefix="/hotels",
    tags=["rooms"],
)


@router.get(
    "/{hotel_id}/rooms",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
    ),
)
@inject
async def list_rooms(
    hotel_id: int,
    filter_query: Annotated[ListRoomsRequestDTO, Query()],
    access_service: FromDishka[AccessService],
    room_service: FromDishka[RoomService],
    token: str = auth_header,
) -> list[GetRoomResponseDTO]:
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=RoomPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.ROOM,
        )
    )

    cmd = room_commands.ListRoomsCommand(
        hotel_id=hotel_id,
        price_from=filter_query.price_from,
        price_to=filter_query.price_to,
        services=filter_query.services,
    )

    rooms = await room_service.list_rooms(cmd)
    return [GetRoomResponseDTO.model_validate(room) for room in rooms]


@router.get(
    "/{hotel_id}/rooms/{room_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
        RoomNotFoundException,
    ),
)
@inject
async def get_room(
    hotel_id: int,
    room_id: int,
    room_service: FromDishka[RoomService],
    access_service: FromDishka[AccessService],
    token: str = auth_header,
) -> GetRoomResponseDTO:
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=RoomPermissionEnum.CAN_VIEW,
            resource_type=ResourceTypeEnum.ROOM,
        )
    )

    room = await room_service.get_room(
        room_commands.GetRoomCommand(hotel_id=hotel_id, room_id=room_id)
    )

    return GetRoomResponseDTO.model_validate(room)


@router.post(
    "/{hotel_id}/rooms",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
        HotelNotFoundException,
        RoomAlreadyExistsException,
    ),
)
@inject
async def add_room(
    hotel_id: int,
    dto: AddRoomRequestDTO,
    access_service: FromDishka[AccessService],
    room_service: FromDishka[RoomService],
    token: str = auth_header,
) -> AddRoomResponseDTO:
    # Authorize user, only hotel owners can add rooms
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=RoomPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.HOTEL,
            resource_id=dto.hotel_id,
        )
    )

    cmd = room_commands.AddRoomCommand(
        hotel_id=hotel_id,
        user_id=authorization_info.user_id,
        name=dto.name,
        price=dto.price,
        quantity=dto.quantity,
        description=dto.description,
        services=dto.services,
        image_id=dto.image_id,
    )

    updated_id = await room_service.add_room(cmd=cmd)
    return AddRoomResponseDTO(id=updated_id, hotel_id=hotel_id)


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
        RoomNotFoundException,
        RoomCannotBeUpdatedException,
    ),
)
@inject
async def update_room(
    hotel_id: int,
    room_id: int,
    dto: UpdateRoomRequestDTO,
    access_service: FromDishka[AccessService],
    room_service: FromDishka[RoomService],
    token: str = auth_header,
) -> UpdateRoomResponseDTO:
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=RoomPermissionEnum.CAN_EDIT,
            resource_type=ResourceTypeEnum.ROOM,
            resource_id=room_id,
        )
    )

    cmd = room_commands.UpdateRoomCommand(
        hotel_id=hotel_id,
        room_id=room_id,
        user_id=authorization_info.user_id,
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
    "/{hotel_id}/rooms/{room_id}",
    responses=generate_responses(
        Unauthorized,
        Forbidden,
        UserNotFoundException,
        RoomNotFoundException,
    ),
)
@inject
async def delete_room(
    hotel_id: int,
    room_id: int,
    access_service: FromDishka[AccessService],
    room_service: FromDishka[RoomService],
    token: str = auth_header,
) -> DeleteRoomResponseDTO:
    # Authorize user
    authorization_info = await access_service.authorize(
        Authorize(
            access_token=token,
            permission=RoomPermissionEnum.CAN_DELETE,
            resource_type=ResourceTypeEnum.ROOM,
            resource_id=room_id,
        )
    )

    cmd = room_commands.DeleteRoomCommand(
        hotel_id=hotel_id, room_id=room_id, user_id=authorization_info.user_id
    )

    await room_service.delete_room(cmd)
    return DeleteRoomResponseDTO()
