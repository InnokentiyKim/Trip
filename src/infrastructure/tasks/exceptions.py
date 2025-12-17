from src.common.exceptions.common import BaseError
from fastapi import status


class ImageProcessingError(BaseError):
    """Exception raised for errors during image processing."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An error occurred while processing the image"
    loc = "image_processing"
