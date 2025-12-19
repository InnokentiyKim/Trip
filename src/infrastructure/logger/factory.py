from typing import Any
import logging
import structlog.processors
from structlog.typing import EventDict, Processor

from src.common.domain.enums import EnvironmentEnum
from src.config import Configs

_debug_additional_info =  structlog.processors.CallsiteParameterAdder(
    parameters=[
        structlog.processors.CallsiteParameter.FILENAME,
        structlog.processors.CallsiteParameter.FUNC_NAME,
        structlog.processors.CallsiteParameter.LINENO,
    ],
    additional_ignores=["src.infrastructure.logger"],
)

def add_debug_location(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    A structlog processor that adds the file name and line number of the caller
    to DEBUG-level log messages.

    Args:
        logger (Any): The logger instance.
        method_name (str): The log method name (e.g., 'debug', 'info').
        event_dict (EventDict): The log event dictionary.

    Returns:
        EventDict: The modified event dictionary with file and line info for DEBUG logs.
    """
    if method_name == "debug":
        return _debug_additional_info(logger, method_name, event_dict)
    return event_dict


def build_shared_processors(config: Configs) -> list[Processor]:
    """
    Build a list of shared structlog processors for logging.

    Args:
        config (Configs): The application configuration.

    Returns:
        list[Processor]: A list of structlog processors.
    """
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        structlog.processors.StackInfoRenderer(),
        add_debug_location,
    ]

    return processors


def setup_logging(config: Configs) -> None:
    shared_processors = build_shared_processors(config)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # The ProcessorFormatter allows us to:
    #  - run a chain of processors on log records from Python's logging
    #  - then run a final set of processors (including the final renderer)
    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within the structlog.
        foreign_pre_chain=shared_processors,
        processors=[
            # Remove internal structlog metadata so it doesn't show up in the final log.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            # Choose the final renderer based on config (JSON or console).
            (
                structlog.dev.ConsoleRenderer()
                if config.general.environment in (EnvironmentEnum.DEV, EnvironmentEnum.LOCAL)
                else structlog.processors.JSONRenderer()
            ),
        ],
    )

    # Create a default StreamHandler to output logs to sys.stderr (or stdout).
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Attach this handler to the root logger. This ensures all logs end up going through the structlog.
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    # Set the log level (e.g., INFO, DEBUG, etc.) based on user configs.
    root_logger.setLevel(config.logger.log_level.upper())

    # For Uvicorn's primary loggers, clear their default handlers and propagate to root.
    # This ensures that "uvicorn", "uvicorn.error" and FS logs go through structlog.
    for log_type in ("uvicorn", "uvicorn.error", ):
        logging.getLogger(log_type).handlers.clear()
        logging.getLogger(log_type).propagate = True

    # Avoid duplicate or redundant logs re-emitted by Uvicorn access logger.
    for log_type in (
        "uvicorn.access",
        "asyncio",
        "botocore",
        "aiobotocore",
        "urllib3",
        "httpcore",
    ):
        logging.getLogger(log_type).handlers.clear()
        logging.getLogger(log_type).propagate = False
