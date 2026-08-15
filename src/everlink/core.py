import asyncio
import logging

from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException

from .interfaces import ServiceDefinition, ServiceLike
from .config import IS_DEV_ENV
from .services import SERVICES

logger = logging.getLogger(__name__)


class Core:

    definitions: dict[str, ServiceDefinition]
    services: dict[str, ServiceLike]

    def __init__(self, custom_services: Path) -> None:

        service_definitions = dict(SERVICES)
        service_definitions.update(self.load_custom_definitions(custom_services))

        self.services = {}
        self.definitions = service_definitions

        logger.debug(
            "Loaded %d service definitions: %s",
            len(self.definitions),
            ", ".join(self.definitions.keys()),
        )

    def load_custom_definitions(self, path: Path) -> dict[str, ServiceDefinition]:
        """Loads user provided custom service definitions"""

        services = {}
        for file in path.glob("*.py"):
            if file.name.startswith("_") and not IS_DEV_ENV:
                continue

            spec = spec_from_file_location(file.stem, file)

            if spec is None or spec.loader is None:
                continue

            module = module_from_spec(spec)
            spec.loader.exec_module(module)

            definition = getattr(module, "definition", None)
            if not isinstance(definition, ServiceDefinition):
                continue

            if definition.id in services:
                raise ValueError(f"Duplicate custom service ID: {definition.id!r}")

            services[definition.id] = definition

        return services

    async def get_service(self, service_id: str) -> ServiceLike | None:
        if service_id in self.services:
            return self.services[service_id]

        definition = self.definitions.get(service_id)
        if definition is None:
            return None

        logger.info("Initializing service: %s", service_id)
        service = await definition.builder()
        self.services[service_id] = service
        return service

    async def route_request(
        self, request: Request, service_id: str, slug: str
    ) -> Response:
        service = await self.get_service(service_id)
        if service is None:
            logger.warning("Service not found: %s", service_id)
            raise HTTPException(
                status_code=404, detail=f"Service '{service_id}' does not exist."
            )

        return await service.handle_request(request, slug)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self.services:
            logger.info("Closing %d services", len(self.services))
        await asyncio.gather(*(s.destroy() for s in self.services.values()))
