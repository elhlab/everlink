import http
import logging
import contextlib

from typing import AsyncGenerator, TypedDict, cast
from urllib.parse import unquote


from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from .config import IS_DEV_ENV
from .core import Core

logger = logging.getLogger(__name__)


class ApplicationState(TypedDict):
    core: Core


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[ApplicationState, None]:
    async with Core() as core:
        yield {"core": core}


async def download_handler(request: Request[ApplicationState]):
    core = request.state["core"]

    service_id = request.path_params["service"]
    slug = unquote(request.path_params["slug"])
    logger.debug(
        '%s - "%s %s" [Range: %s]',
        request.client.host if request.client else "...",
        request.method,
        request.url.path,
        request.headers.get("Range", "none"),
    )

    response = await core.route_request(cast(Request, request), service_id, slug)
    logger.info(
        '%s - "%s %s" %s %s',
        request.client.host if request.client else "...",
        request.method,
        request.url.path,
        response.status_code,
        http.HTTPStatus(response.status_code).phrase,
    )

    return response


app = Starlette(
    debug=IS_DEV_ENV,
    lifespan=lifespan,
    routes=[
        Route(
            "/{service}/{slug}",
            download_handler,
            methods=["GET", "HEAD"],
        )
    ],
)
