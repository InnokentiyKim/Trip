from typing import Iterable

from src.config import create_configs, Configs
from dishka import AsyncContainer, Provider, make_async_container


app_config: Configs = create_configs()


def create_async_container(providers: Iterable[Provider], config: Configs = app_config) -> AsyncContainer:
    """
    Creates an asynchronous container with the given providers and configuration.

    Note:
        Container is an object you use to get your dependency.

    Args:
        providers: An iterable of provider instances.
        config: The configuration settings. Defaults to app_config.

    Returns:
        AsyncContainer: The created asynchronous container.
    """
    return make_async_container(*providers, context={Configs: config})  # context={Configs: config}
