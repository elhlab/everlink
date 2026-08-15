import http
import logging

from typing import Optional
from urllib.parse import urlencode

import aiohttp

from bs4 import BeautifulSoup
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.exceptions import HTTPException


from ..interfaces import ServiceDefinition, ServiceLike
from ..headers import get_streaming_headers, get_navigate_headers
from ..streaming import stream_reader
from ..utils import truncate
from ..cache import cache

logger = logging.getLogger(__name__)

ID = "gdrive"
NAME = "Google Drive"

SLUG_CACHE_FMT = f"{ID}_download_url:{{slug}}"


def parse_download_url(html: str) -> str:
    soup = BeautifulSoup(html, features="lxml")

    form = soup.select_one("form#download-form")
    if form is None:
        logger.error("Download form not found for: %s", form)
        raise ValueError(
            "Unable to locate download-form. Did we receive an direct download?"
        )

    params = {}
    for input in form.select("input[name]"):
        params[input["name"]] = input["value"]

    return f"{form["action"]}?{urlencode(params)}"


class GdriveService(ServiceLike):

    id = ID
    name = NAME

    _session: Optional[aiohttp.ClientSession] = None

    def get_session(self) -> aiohttp.ClientSession:
        if self._session is not None:
            return self._session

        self._session = aiohttp.ClientSession()
        return self._session

    @cache(ttl=600, key=SLUG_CACHE_FMT, lock=True)
    async def fetch_download_url(self, slug: str) -> str:
        session = self.get_session()

        res = await session.get(
            "https://drive.usercontent.google.com/download",
            params={"id": slug, "export": "download"},
            headers=get_navigate_headers(),
        )

        res.raise_for_status()

        content_type = res.headers.get("Content-Type", "")
        if "text/html" in content_type:
            url = parse_download_url(await res.text())
            logger.info("Resolved download redirect: %s", slug)
            logger.debug("resolved url: '%s'", url)
            return url

        url = str(res.url)

        logger.warning("Direct download link: %s", slug)
        logger.debug("resolved url: '%s'", url)
        return url

    async def delete_cache_entry(self, slug: str):
        await cache.delete(SLUG_CACHE_FMT.format(slug))
        logger.debug("Cache cleared: %s", slug)

    async def handle_request(self, request: Request, slug: str) -> Response:
        url = await self.fetch_download_url(slug)

        headers = get_navigate_headers()
        streaming_headers = get_streaming_headers(request.headers)
        streaming_headers.pop("User-Agent", None)
        headers.update(streaming_headers)

        resp = await self.get_session().request(request.method, url, headers=headers)

        logger.debug(
            "%s - \"%s %s\" %s %s [Content-Type: '%s', Content-Length '%s']",
            request.client.host if request.client else "...",
            request.method,
            truncate(resp.url.path + "?" + resp.url.query_string, 27),
            resp.status,
            http.HTTPStatus(resp.status).phrase,
            resp.headers.get("Content-Type", "none"),
            resp.headers.get("Content-Length", "none"),
        )

        # TODO: actually figure out what google responds when the url expires. Dont assume.
        if resp.status == 401:
            logger.info("URL expired, refreshing: %s", slug)
            resp.release()

            await self.delete_cache_entry(slug)
            return await self.handle_request(request, slug)

        # Google Drive is gatekeeping this file due to popularity...
        if resp.status == 200 and "text/html" in resp.content_type.lower():
            raise HTTPException(
                status_code=429,
                headers={"Retry-After": "3600"},
            )

        if resp.status >= 400:
            body = await resp.text()
            logger.error(
                "Encountered an error from upstream server. error %d: %s",
                resp.status,
                body,
            )
            resp.release()
            raise HTTPException(status_code=resp.status, detail=body)

        return StreamingResponse(
            stream_reader(resp),
            status_code=resp.status,
            headers=get_streaming_headers(resp.headers.copy()),
        )

    async def close(self):
        if self._session:
            logger.info("Closing HTTP session")
            await self._session.close()


async def build():
    return GdriveService()


definition = ServiceDefinition(id=ID, name=NAME, builder=build)
