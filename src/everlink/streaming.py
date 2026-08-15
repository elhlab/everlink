import asyncio
import logging

import aiohttp

from .utils import format_bytes

logger = logging.getLogger(__name__)


async def stream_reader(response: aiohttp.ClientResponse):
    bytes_read = 0

    try:
        async for chunk in response.content.iter_chunked(64 * 1024):
            bytes_read += len(chunk)
            yield chunk
    except asyncio.CancelledError:
        logger.debug("Client cancelled stream after %s", format_bytes(bytes_read))
    finally:
        logger.debug(
            "Closing upstream connection; %s transferred", format_bytes(bytes_read)
        )
        response.release()
