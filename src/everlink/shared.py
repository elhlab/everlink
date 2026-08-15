import asyncio
import logging

import aiohttp
from multidict import CIMultiDict

logger = logging.getLogger(__name__)


def get_navigate_headers() -> CIMultiDict[str]:
    headers = CIMultiDict()
    headers.update(
        {
            "Accept": (
                "text/html,application/xhtml+xml," "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US;q=0.9,en;q=0.8",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) "
                "Gecko/20100101 Firefox/153.0"
            ),
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "sec-gpc": "1",
        }
    )

    return headers


async def stream_reader(response: aiohttp.ClientResponse):
    try:
        async for chunk in response.content.iter_chunked(64 * 1024):
            yield chunk
    except asyncio.CancelledError:
        logger.info("Client cancelled stream")
    finally:
        logger.debug("Closed upstream connection")
        response.release()
