"""Curated (Tier B/C) entries: the pipeline verifies, never fetches or rewrites."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import build
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


if __name__ == "__main__":
    unittest.main()
