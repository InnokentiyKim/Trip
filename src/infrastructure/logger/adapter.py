from typing import Any

from src.common.interfaces import CustomLoggerProto
import structlog
import re


def _to_snake_case(name: str) -> str:
    """
    Convert a CamelCase class name to snake_case.

    Args:
        name: The original class name (CamelCase format).

    Returns:
        str: The name converted to snake_case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class CustomLoggerAdapter(CustomLoggerProto):
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger

    def bind(self, *args: Any, **kwargs: Any) -> None:
        """
        Bind additional context variables to the logger.

        This method iterates through all positional arguments. If an argument
        has an 'id' attribute, it will be converted into a snake-cased key and
        bound to the logger's context. Any keyword arguments (`kwargs`)
        are also bound as is.

        Args:
            *args (Any): Positional arguments to be examined for an 'id' attribute.
            **kwargs (Any): Arbitrary keyword arguments to bind directly.
        """
        for arg in args:
            if not hasattr(arg, 'id'):
                self.logger.error(
                    "Unsupported argument. Argument must have an 'id' attribute.",
                    argument_type=type(arg).__name__,
                )
                continue

            key = _to_snake_case(type(arg).__name__)
            structlog.contextvars.bind_contextvars(**{key: arg.id})

        structlog.contextvars.bind_contextvars(**kwargs)

    def unbind(self, *keys: str) -> None:
        """
        Unbind (remove) previously bound keys from the logger's context.
        Args:
            *keys (str): The keys to remove from the logger's current context.
        """
        structlog.contextvars.unbind_contextvars(*keys)

    def _log(self, level: str, *args: Any, **kwargs: Any) -> None:
        """
        Generic logging method that routes to the appropriate log level method.
        Args:
            level (str): The log level as a string (e.g., 'debug', 'info', 'error').
            *args (Any): Positional arguments to pass to the log method.
            **kwargs (Any): Keyword arguments to pass to the log method.
        """
        log_method = getattr(self.logger, level, None)
        if not log_method:
            raise AttributeError("Logger has no method for level: %s" % level)
        log_method(*args, **kwargs)

    def debug(self, *args: Any, **kwargs: Any) -> None:
        """
        Log a DEBUG-level message with optional additional context.
        Args:
            *args (Any): Positional arguments for the log method.
            **kwargs (Any): Keyword arguments for the log method.
        """
        self._log("debug", *args, **kwargs)

    def info(self, *args: Any, **kwargs: Any) -> None:
        """
        Log an INFO-level message with optional additional context.
        Args:
            *args (Any): Positional arguments for the log method.
            **kwargs (Any): Keyword arguments for the log method.
        """
        self._log("info", *args, **kwargs)

    def warning(self, *args: Any, **kwargs: Any) -> None:
        """
        Log a WARNING-level message with optional additional context.
        Args:
            *args (Any): Positional arguments for the log method.
            **kwargs (Any): Keyword arguments for the log method.
        """
        self._log("warning", *args, **kwargs)

    def error(self, *args: Any, **kwargs: Any) -> None:
        """
        Log an ERROR-level message with optional additional context.
        Args:
            *args (Any): Positional arguments for the log method.
            **kwargs (Any): Keyword arguments for the log method.
        """
        self._log("error", *args, **kwargs)

    def critical(self, *args: Any, **kwargs: Any) -> None:
        """
        Log a CRITICAL-level message with optional additional context.
        Args:
            *args (Any): Positional arguments for the log method.
            **kwargs (Any): Keyword arguments for the log method.
        """
        self._log("critical", *args, **kwargs)

    def exception(self, *args: Any, **kwargs: Any) -> None:
        """
        Log an ERROR-level message with exception information.

        This is typically used in `except` blocks to record stack traces along
        with the error message.

        Args:
            *args (Any): Positional arguments for the log method.
            **kwargs (Any): Keyword arguments for the log method.
        """
        self._log("exception", *args, **kwargs)
