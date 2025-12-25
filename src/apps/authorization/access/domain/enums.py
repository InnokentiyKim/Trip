from enum import StrEnum


class ResourceTypeEnum(StrEnum):
    SYSTEM = "system"
    USER = "user"
    HOTEL = "hotel"
    ROOM = "room"
    BOOKING = "booking"


type PermissionEnum = (
    BasePermissionEnum
    | SystemPermissionEnum
    | UserPermissionEnum
    | HotelPermissionEnum
    | RoomPermissionEnum
    | BookingPermissionEnum
)


class BasePermissionEnum(StrEnum):
    CAN_MANAGE_ACCESS = "can_manage_access"
    CAN_CREATE = "can_create"
    CAN_EDIT = "can_edit"
    CAN_DELETE = "can_delete"
    CAN_VIEW = "can_view"


class SystemPermissionEnum(StrEnum):
    REMOVE_PERMISSION = "remove_permission"
    CREATE_ROLE = "create_role"
    GRANT_ACCESS = "GRANT_ACCESS"
    CAN_DELETE = BasePermissionEnum.CAN_DELETE
    CAN_VIEW = BasePermissionEnum.CAN_VIEW
    ADMIN_ACCESS = "admin_access"


class UserPermissionEnum(StrEnum):
    CAN_MANAGE_ACCESS = BasePermissionEnum.CAN_MANAGE_ACCESS
    CAN_CREATE = BasePermissionEnum.CAN_CREATE
    CAN_EDIT = BasePermissionEnum.CAN_EDIT
    CAN_DELETE = BasePermissionEnum.CAN_DELETE
    CAN_VIEW = BasePermissionEnum.CAN_VIEW


class HotelPermissionEnum(StrEnum):
    CAN_CREATE = BasePermissionEnum.CAN_CREATE
    CAN_EDIT = BasePermissionEnum.CAN_EDIT
    CAN_DELETE = BasePermissionEnum.CAN_DELETE
    CAN_VIEW = BasePermissionEnum.CAN_VIEW


class RoomPermissionEnum(StrEnum):
    CAN_CREATE = BasePermissionEnum.CAN_CREATE
    CAN_EDIT = BasePermissionEnum.CAN_EDIT
    CAN_DELETE = BasePermissionEnum.CAN_DELETE
    CAN_VIEW = BasePermissionEnum.CAN_VIEW


class BookingPermissionEnum(StrEnum):
    CAN_CREATE = BasePermissionEnum.CAN_CREATE
    CAN_EDIT = BasePermissionEnum.CAN_EDIT
    CAN_VIEW = BasePermissionEnum.CAN_VIEW
