from starlette import status

from src.common.exceptions.common import BaseError


class FileObjectDoesNotExistError(BaseError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "File object does not exist"
    loc = "storage_key"
