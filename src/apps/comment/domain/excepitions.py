from fastapi import status

from src.common.exceptions.common import BaseError


class CommentAlreadyExistsError(BaseError):
    """Exception raised when trying to create a comment that already exists."""

    status_code = status.HTTP_409_CONFLICT
    message = "Comment already exists."


class CommentNotFoundError(BaseError):
    """Exception raised when trying to retrieve a comment that does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Comment not found."
