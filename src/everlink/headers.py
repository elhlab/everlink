import logging

from starlette.datastructures import Headers
from multidict import CIMultiDict

logger = logging.getLogger(__name__)


def headers_as_multidict(headers: Headers | CIMultiDict) -> CIMultiDict:
    if isinstance(headers, CIMultiDict):
        return headers

    logger.debug("Parsing %d headers", len(headers))
    return CIMultiDict(
        (key.decode("latin-1"), value.decode("latin-1")) for key, value in headers.raw
    )


def parse_connection_header(value: str) -> list[str]:
    items = value.split(",")

    return [item.strip() for item in items]


HOP_BY_HOP_HEADERS = (
    "Connection",
    "Keep-Alive",
    "Proxy-Authenticate",
    "Proxy-Authorization",
    "TE",
    "Trailer",
    "Transfer-Encoding",
    "Upgrade",
)


def strip_hbp_headers(h: Headers | CIMultiDict) -> CIMultiDict:
    headers = headers_as_multidict(h)

    while "Connection" in headers:
        conn_headers = parse_connection_header(headers.pop("Connection"))

        for conn_header in conn_headers:
            headers.popall(conn_header, None)

    for conn_header in HOP_BY_HOP_HEADERS:
        headers.popall(conn_header, None)

    logger.debug("Filtered hop-by-hop headers: %d remaining", len(headers))
    return headers


def get_streaming_headers(h: Headers | CIMultiDict) -> CIMultiDict:
    headers = strip_hbp_headers(h)

    if "Host" in headers:
        headers.popall("Host")

    return headers


def get_navigate_headers() -> CIMultiDict[str]:
    return CIMultiDict(
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
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
