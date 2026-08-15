from dataclasses import dataclass
from typing import Awaitable, Callable, Protocol

from starlette.requests import Request
from starlette.responses import Response


class ServiceLike(Protocol):
    """Interface implemented by a download service.

    A service handles requests for a particular external download provider.
    Instances are created by the builder in :class:`ServiceDefinition` and
    may hold state or resources for the lifetime of the service.
    """

    id: str
    name: str

    async def handle_request(self, request: Request, slug: str) -> Response:
        """Handle a download request for this service.

        Args:
            request: The incoming HTTP request.
            slug: The service-specific download identifier extracted from
                the request URL.

        Returns:
            A Starlette response representing the download.

        Raises:
            HTTPException: If the request cannot be handled, such as when the
                slug is invalid or the requested resource is unavailable.
        """
        ...

    async def close(self) -> None:
        """Clean up resources held by the service."""
        ...


@dataclass(frozen=True)
class ServiceDefinition:
    """Metadata and factory used to register a service.

    Custom service modules must expose a module-level ``definition`` variable
    containing a ``ServiceDefinition`` instance.
    """

    id: str
    name: str
    builder: Callable[[], Awaitable[ServiceLike]]
