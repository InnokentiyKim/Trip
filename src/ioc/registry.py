from dishka import Provider

from src.apps.authentication.user.ioc import get_user_providers
from src.apps.notification.ioc import get_notification_providers
from src.infrastructure.ioc import get_infra_providers
from src.apps.hotel.ioc import get_hotel_providers


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
        *get_user_providers(),
    ]
