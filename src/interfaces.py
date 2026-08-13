from dataclasses import dataclass
from typing import Awaitable, Callable, Protocol

from starlette.requests import Request
from starlette.responses import Response


class ServiceLike(Protocol):

    id: str
    name: str

    async def handle_request(self, request: Request, slug: str) -> Response:
        """Handles a download request for this service. Returning a startlette response."""
        ...

    async def destroy(self):
        """Close service and cleanup"""
        ...


@dataclass(frozen=True)
class ServiceDefinition:
    id: str
    name: str
    builder: Callable[[], Awaitable[ServiceLike]]
