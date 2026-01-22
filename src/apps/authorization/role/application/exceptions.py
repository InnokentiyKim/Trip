from fastapi import status

from src.common.exceptions.common import BaseError


class RoleIsNotFoundError(BaseError):
    """Exception raised when role_id is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Role not found."


class RoleCouldNotBeDeletedError(BaseError):
    """Exception raised when trying to delete base role_id."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Base role_id can not be deleted."


class PermissionsNotFoundError(BaseError):
    """Exception raised when permission is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Permission not found."
