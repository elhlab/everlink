import contextlib
import os

from typing import AsyncGenerator, TypedDict, cast
from urllib.parse import unquote


from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from .core import Core


class ApplicationState(TypedDict):
    core: Core


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[ApplicationState]:
    core = Core()

    try:
        yield {"core": core}
    finally:
        await core.close()


async def download_handler(request: Request[ApplicationState]):
    core = request.state["core"]

    service_id = request.path_params["service"]
    slug = unquote(request.path_params["slug"])

    return await core.route_request(cast(Request, request), service_id, slug)


app = Starlette(
    debug=os.environ.get("DEBUG", None) == "true",
    lifespan=lifespan,
    routes=[
        Route(
            "/{service}/{slug}",
            download_handler,
            methods=["GET", "HEAD"],
        )
    ],
)
