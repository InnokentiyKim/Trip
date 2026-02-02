from datetime import UTC, datetime

from asgi_correlation_id import correlation_id
from dishka import AsyncContainer, Provider, Scope, provide
from dishka.exceptions import NoFactoryError
from fastapi import Request

from src.infrastructure.context import RequestContext


class RequestContextProvider(Provider):
    """Provides request context for audit trails and logging.

    Extracts HTTP request metadata (IP address, user agent, request ID)
    from FastAPI Request when available. Falls back to empty context for
    non-HTTP contexts (tests, CLI, background jobs).
    """

    @provide(scope=Scope.REQUEST, provides=RequestContext)
    async def provide_request_context(self, container: AsyncContainer) -> RequestContext:
        """Extract request context from FastAPI Request or return empty context.

        Args:
            container: DI container to check for Request availability

        Returns:
            RequestContext: Extracted context from request, or empty context if no request

        Note:
            - For HTTP requests: Extracts IP, user agent, request ID from request
            - For non-HTTP contexts (tests, MessageBus, CLI): Returns empty context with 'system' IP
            - IP address extracted from request.client (handles proxy headers if configured)
            - Request ID from correlation_id (set by asgi-correlation-id middleware)
        """
        try:
            # Try to get Request from container context (only available in HTTP requests)
            request = await container.get(Request)
        except NoFactoryError:
            # Request not available in context (tests, MessageBus, CLI)
            return RequestContext.empty()

        # Extract client IP (with fallback for missing client info)
        client_host, _ = request.client or ("unknown", None)

        # Extract user agent from headers
        user_agent = request.headers.get("user-agent", "")

        # Get correlation ID (set by asgi-correlation-id middleware)
        request_id = correlation_id.get() or ""

        return RequestContext(
            ip_address=client_host,
            user_agent=user_agent,
            request_id=request_id,
            timestamp=datetime.now(UTC),
        )
