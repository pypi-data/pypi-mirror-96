"""Define a client to interact with Flu Near You."""
import logging
from typing import Optional

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from .cdc import CdcReport
from .errors import RequestError
from .user import UserReport

_LOGGER: logging.Logger = logging.getLogger(__name__)

DEFAULT_CACHE_SECONDS: int = 60 * 60
DEFAULT_HOST: str = "api.v2.flunearyou.org"
DEFAULT_ORIGIN: str = "https://flunearyou.org"
DEFAULT_TIMEOUT: int = 10
DEFAULT_USER_AGENT: str = "Home Assistant (Macintosh; OS X/10.14.0) GCDHTTPRequest"

API_URL_SCAFFOLD: str = f"https://{DEFAULT_HOST}"


class Client:  # pylint: disable=too-few-public-methods
    """Define the client."""

    def __init__(
        self,
        *,
        cache_seconds: int = DEFAULT_CACHE_SECONDS,
        session: Optional[ClientSession] = None,
    ) -> None:
        """Initialize."""
        self._cache_seconds: int = cache_seconds
        self._session: ClientSession = session
        self.cdc_reports: CdcReport = CdcReport(self._request, cache_seconds)
        self.user_reports: UserReport = UserReport(self._request, cache_seconds)

    async def _request(
        self, method: str, endpoint: str, *, headers: Optional[dict] = None
    ) -> dict:
        """Make a request against Flu Near You."""
        _headers = headers or {}
        _headers.update(
            {
                "Host": DEFAULT_HOST,
                "Origin": DEFAULT_ORIGIN,
                "Referrer": DEFAULT_ORIGIN,
                "User-Agent": DEFAULT_USER_AGENT,
            }
        )

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(
                method, f"{API_URL_SCAFFOLD}/{endpoint}", headers=_headers
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except ClientError as err:
            raise RequestError(
                f"Error requesting data from {endpoint}: {err}"
            ) from None
        finally:
            if not use_running_session:
                await session.close()
