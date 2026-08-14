from typing import Optional
import asyncio

from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException

from .interfaces import ServiceDefinition, ServiceLike
from .services import SERVICES


class Core:

    definitions: dict[str, ServiceDefinition]
    services: dict[str, ServiceLike]

    def __init__(
        self,
        services: Optional[list[ServiceDefinition]] = None,
        overwrite_services: bool = False,
    ) -> None:

        service_definitions = {}
        if not overwrite_services:
            service_definitions.update(SERVICES)

        if services:
            for service in services:
                service_definitions[service.id] = service

        self.definitions = service_definitions
        self.services = {}

    async def get_service(self, service_id: str) -> ServiceLike | None:
        if service_id in self.services:
            return self.services[service_id]

        definition = self.definitions.get(service_id)
        if definition is None:
            return None

        service = await definition.builder()
        self.services[service_id] = service
        return service

    async def route_request(
        self, request: Request, service_id: str, slug: str
    ) -> Response:
        service = await self.get_service(service_id)
        if service is None:
            raise HTTPException(
                status_code=404, detail=f"Service '{service_id}' does not exist."
            )

        return await service.handle_request(request, slug)

    async def close(self):
        await asyncio.gather(*(s.destroy() for s in self.services.values()))
