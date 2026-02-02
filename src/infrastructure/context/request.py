"""Request context for capturing HTTP request metadata."""

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class RequestContext:
    """Captures HTTP request metadata for audit trails and logging.

    This context is extracted from HTTP requests and can be passed through
    the application layers to provide audit trail information.

    Attributes:
        ip_address: Client IP address (from request.client or X-Forwarded-For header)
        user_agent: User agent string from request headers
        request_id: Unique request identifier (correlation ID)
        timestamp: Request timestamp (UTC)
    """

    ip_address: str
    user_agent: str
    request_id: str
    timestamp: datetime

    @classmethod
    def empty(cls) -> "RequestContext":
        """Create empty context for non-HTTP contexts (MessageBus, CLI, background jobs).

        Returns:
            RequestContext with default values
        """
        return cls(
            ip_address="system",
            user_agent="internal",
            request_id="",
            timestamp=datetime.now(UTC),
        )
