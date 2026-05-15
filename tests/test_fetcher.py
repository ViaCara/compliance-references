"""Fetcher tests (stdlib unittest with HTTPError stub)."""

from __future__ import annotations

import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from lib.fetcher import (
    FetchError,
    FetchResult,
    Fetcher,
    NotModified,
)


class _FakeResponse:
    def __init__(self, body: bytes, headers: dict | None = None, status: int = 200):
        self._body = body
        self.headers = headers or {}
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self):
        return self._body

    def getheader(self, name, default=None):
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default


class FetcherTests(unittest.TestCase):
    def test_returns_body_and_metadata_on_200(self):
        fetcher = Fetcher(sleep_seconds=0.0)
        fake = _FakeResponse(
            b"<html>hi</html>",
            headers={"ETag": '"abc"', "Last-Modified": "Mon, 01 Jan 2026 00:00:00 GMT"},
        )
        with patch("urllib.request.urlopen", return_value=fake):
            result = fetcher.fetch("https://example.gov.uk/x")
        self.assertIsInstance(result, FetchResult)
        self.assertEqual(result.body, b"<html>hi</html>")
        self.assertEqual(result.etag, '"abc"')

    def test_raises_not_modified_on_304(self):
        fetcher = Fetcher(sleep_seconds=0.0)

        def raise_304(*a, **k):
            raise HTTPError(
                url="https://example.gov.uk/x",
                code=304,
                msg="Not Modified",
                hdrs=None,
                fp=None,
            )

        with patch("urllib.request.urlopen", side_effect=raise_304):
            with self.assertRaises(NotModified):
                fetcher.fetch("https://example.gov.uk/x", if_none_match='"abc"')

    def test_raises_on_500(self):
        fetcher = Fetcher(sleep_seconds=0.0)

        def raise_500(*a, **k):
            raise HTTPError(
                url="https://example.gov.uk/x",
                code=500,
                msg="server error",
                hdrs=None,
                fp=None,
            )

        with patch("urllib.request.urlopen", side_effect=raise_500):
            with self.assertRaises(FetchError):
                fetcher.fetch("https://example.gov.uk/x")

    def test_raises_on_404(self):
        fetcher = Fetcher(sleep_seconds=0.0)

        def raise_404(*a, **k):
            raise HTTPError(
                url="https://example.gov.uk/x",
                code=404,
                msg="not found",
                hdrs=None,
                fp=None,
            )

        with patch("urllib.request.urlopen", side_effect=raise_404):
            with self.assertRaises(FetchError):
                fetcher.fetch("https://example.gov.uk/x")

    def test_enforces_minimum_sleep_between_requests(self):
        fetcher = Fetcher(sleep_seconds=0.1)
        fake = _FakeResponse(b"x")
        elapsed = []

        with patch("urllib.request.urlopen", return_value=fake):
            start = time.monotonic()
            fetcher.fetch("https://example.gov.uk/a")
            fetcher.fetch("https://example.gov.uk/b")
            elapsed.append(time.monotonic() - start)

        self.assertGreaterEqual(elapsed[0], 0.09)


if __name__ == "__main__":
    unittest.main()
