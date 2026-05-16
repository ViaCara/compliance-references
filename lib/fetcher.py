"""HTTP fetcher with rate limiting and conditional GET (stdlib only)."""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from urllib.error import HTTPError, URLError


class FetchError(RuntimeError):
    """Raised on any non-success HTTP response or transport failure."""


class TransportError(FetchError):
    """Raised on transport-level errors (SSL EOF, DNS, connection reset).

    These are retried by `Fetcher.fetch`; HTTP errors raise plain `FetchError`
    and are not retried.
    """


class NotModified(Exception):
    """Raised when the server returns 304 to a conditional GET."""


@dataclass
class FetchResult:
    body: bytes
    etag: str | None
    last_modified: str | None
    status: int = 200


_USER_AGENT = "compliance-references-sync/1.0 (+https://github.com/viacara/compliance-references)"


class Fetcher:
    """Rate-limited HTTP fetcher with `If-None-Match` support."""

    def __init__(self, sleep_seconds: float = 1.1, timeout_seconds: float = 30.0):
        self.sleep_seconds = sleep_seconds
        self.timeout_seconds = timeout_seconds
        self._last_request_at: float | None = None

    def fetch(
        self,
        url: str,
        *,
        if_none_match: str | None = None,
        max_retries: int = 3,
    ) -> FetchResult:
        last_error: Exception | None = None
        for attempt in range(max_retries):
            self._wait_for_quota()
            try:
                return self._fetch_once(url, if_none_match=if_none_match)
            except NotModified:
                raise
            except TransportError as exc:
                last_error = exc
                time.sleep(self.sleep_seconds * (2 ** attempt))
            except FetchError:
                raise
        assert last_error is not None
        raise last_error

    def _fetch_once(
        self,
        url: str,
        *,
        if_none_match: str | None = None,
    ) -> FetchResult:
        request = urllib.request.Request(url)
        request.add_header("User-Agent", _USER_AGENT)
        request.add_header("Accept-Language", "en-GB,en;q=0.8")
        if if_none_match:
            request.add_header("If-None-Match", if_none_match)

        try:
            response = urllib.request.urlopen(request, timeout=self.timeout_seconds)
        except HTTPError as exc:
            if exc.code == 304:
                raise NotModified(url) from exc
            raise FetchError(f"HTTP {exc.code} for {url}: {exc.reason}") from exc
        except (URLError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            raise TransportError(f"transport error for {url}: {reason}") from exc
        finally:
            self._last_request_at = time.monotonic()

        with response:
            body = response.read()
            etag = (
                response.getheader("ETag") if hasattr(response, "getheader") else None
            )
            last_modified = (
                response.getheader("Last-Modified")
                if hasattr(response, "getheader")
                else None
            )
            status = getattr(response, "status", 200)

        return FetchResult(
            body=body,
            etag=etag,
            last_modified=last_modified,
            status=status,
        )

    def _wait_for_quota(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.sleep_seconds:
            time.sleep(self.sleep_seconds - elapsed)
