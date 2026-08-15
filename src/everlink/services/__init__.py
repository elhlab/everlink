from ..interfaces import ServiceDefinition
from ..services import gdrive

_SERVICE_MODULES = (gdrive,)

SERVICES: dict[str, ServiceDefinition] = {
    module.definition.id: module.definition for module in _SERVICE_MODULES
}
