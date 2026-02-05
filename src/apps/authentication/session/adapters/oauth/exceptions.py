from fastapi import status

from src.common.exceptions.common import BaseError


class UnsupportedOAuthProviderError(BaseError):
    """
    Exception raised for unsupported OAuth adapters.

    This exception is raised when an OAuth adapter is used that
    is not supported by the system.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Unsupported OAuth provider."
    loc = "oauth"


class OAuthProviderLoginError(BaseError):
    """
    Exception raised when there is an issue during the login process with an OAuth provider.

    This exception can be used to signal errors specifically related to OAuth
    provider login failures, such as misconfiguration, invalid credentials,
    or unexpected response from the provider.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "OAuth login error."
    loc = "oauth"
