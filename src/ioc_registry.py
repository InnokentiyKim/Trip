from dishka import Provider

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
        *get_hotel_providers()
    ]