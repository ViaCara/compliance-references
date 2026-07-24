"""Curated (Tier B/C) entries: the pipeline verifies, never fetches or rewrites."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import build
from lib.fetcher import FetchResult
from lib.frontmatter import body_sha256, render


def _curated_entry() -> dict:
    return {
        "id": "cma-example",
        "kind": "curated_quotes",
        "source_uri": "https://www.gov.uk/example",
        "target": "guidance/uk/cma/example.md",
    }


def _write_curated(root: Path, body: str, sha: str | None = None) -> Path:
    path = root / "guidance" / "uk" / "cma" / "example.md"
    path.parent.mkdir(parents=True)
    fields = {
        "id": "cma-example",
        "kind": "curated_quotes",
        "content_sha256": sha if sha is not None else body_sha256(body),
    }
    path.write_text(render(fields, body), encoding="utf-8")
    return path


class VerifyCuratedTest(unittest.TestCase):
    def test_valid_curated_file_is_reported_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_curated(Path(tmp), "# Quotes\n\n> A quote.\n")

            self.assertEqual(build._verify_curated(_curated_entry(), path), "unchanged")

    def test_missing_curated_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "guidance" / "uk" / "cma" / "example.md"

            with self.assertRaises(build.BuildError):
                build._verify_curated(_curated_entry(), path)

    def test_stale_content_hash_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_curated(Path(tmp), "# Quotes\n\n> A quote.\n", sha="0" * 64)

            with self.assertRaises(build.BuildError):
                build._verify_curated(_curated_entry(), path)


class ProcessEntryTest(unittest.TestCase):
    def test_writes_when_enforcement_status_changes_without_body_drift(self):
        entry = {
            "id": "uk-gdpr-art-022",
            "citation": "UK GDPR Article 22",
            "instrument": "uk-gdpr",
            "kind": "legislation_article",
            "source_uri": "https://example.gov.uk/article-022",
            "enforcement_status": "repealed",
        }
        body = "# UK GDPR Article 22\n\n_(repealed)_\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "article-022.md"
            fields = {
                "id": entry["id"],
                "content_sha256": body_sha256(body),
                "enforcement_status": "in_force",
                "etag": '"prior"',
            }
            path.write_text(render(fields, body), encoding="utf-8")
            result = FetchResult(body=body.encode(), etag=None, last_modified=None)
            fetcher = _StaticFetcher(result)
            changelog = _StaticChangelog()
            context = build.BuildContext(
                fetcher=fetcher,
                legislation=_StaticTransformer(body),
                eur_lex=None,
                changelog=changelog,
                today="2026-07-24",
            )
            prior_root = build.ROOT
            build.ROOT = root
            try:
                self.assertEqual("written", build._process_entry(entry, path, context))
            finally:
                build.ROOT = prior_root

            actual, _body = build.parse(path.read_text(encoding="utf-8"))

            self.assertEqual("repealed", actual["enforcement_status"])

            self.assertEqual("enforcement status in_force -> repealed", changelog.entry.summary)

            self.assertEqual('"prior"', fetcher.if_none_match)


class _StaticFetcher:
    def __init__(self, result):
        self.result = result
        self.if_none_match = None

    def fetch(self, _url: str, *, if_none_match: str | None = None):
        self.if_none_match = if_none_match
        return self.result


class _StaticTransformer:
    def __init__(self, body: str):
        self.body = body

    def transform(self, _xhtml: str, *, citation: str) -> str:
        return self.body


class _StaticChangelog:
    def append(self, entry) -> None:
        self.entry = entry


if __name__ == "__main__":
    unittest.main()
