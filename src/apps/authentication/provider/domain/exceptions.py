from fastapi import status

from src.common.exceptions.common import BaseError


class ProviderNotFoundError(BaseError):
    """Raised when a provider is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Provider not found."


class ProviderTokenNotFoundError(BaseError):
    """Raised when a provider has no OAuth token."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Provider token not found."


class ProviderAlreadyExistsError(BaseError):
    """Raised when attempting to create a provider that already exists."""

    status_code = status.HTTP_409_CONFLICT
    message = "Provider already exists."
