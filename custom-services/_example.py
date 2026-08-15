from starlette.requests import Request
from starlette.responses import Response

from everlink.interfaces import ServiceDefinition, ServiceLike

ID = "example"
NAME = "Example Host"


class Example(ServiceLike):

    id = ID
    name = NAME

    async def handle_request(self, request: Request, slug: str) -> Response:
        return Response("Hello World")

    async def destroy(self):
        return


async def build():
    return Example()


definition = ServiceDefinition(id=ID, name=NAME, builder=build)
