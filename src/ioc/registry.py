from dishka import Provider

from src.apps.authentication.ioc import get_authentication_providers
from src.apps.authorization.ioc import get_authorization_providers
from src.apps.comment.ioc import get_comment_providers
from src.apps.hotel.ioc import get_hotel_providers
from src.apps.notification.ioc import get_notification_providers
from src.infrastructure.ioc import get_infra_providers


def get_providers() -> list[Provider]:
    """
    Get the list of all providers.

    This function aggregates and returns a list of all provider instances,
    including infrastructure providers.

    Returns:
        list[Provider]: A list of provider instances.
    """
    return [
        *get_infra_providers(),
        *get_notification_providers(),
        *get_hotel_providers(),
        *get_authentication_providers(),
        *get_authorization_providers(),
        *get_comment_providers(),
    ]
