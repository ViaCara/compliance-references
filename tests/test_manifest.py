"""Manifest validator tests (stdlib unittest)."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.manifest import ManifestError, load


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class ManifestLoaderTests(unittest.TestCase):
    def _valid_entry(self, **overrides):
        entry = {
            "id": "uk-gdpr-art-009",
            "source_uri": "https://www.legislation.gov.uk/eur/2016/679/article/9",
            "target": "statute/uk/gdpr/article-009.md",
            "kind": "legislation_article",
            "frequency": "monthly",
        }
        entry.update(overrides)
        return entry

    def test_load_valid_manifest(self):
        with TemporaryDirectory() as td:
            path = _write(
                Path(td) / "manifest.json",
                {"sources": [self._valid_entry()], "contents_pages": []},
            )
            manifest = load(path)
            self.assertEqual(len(manifest.sources), 1)
            self.assertEqual(manifest.sources[0]["id"], "uk-gdpr-art-009")

    def test_load_fails_on_invalid_json(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ManifestError):
                load(path)

    def test_load_fails_on_duplicate_id(self):
        with TemporaryDirectory() as td:
            path = _write(
                Path(td) / "manifest.json",
                {
                    "sources": [
                        self._valid_entry(),
                        self._valid_entry(target="statute/uk/gdpr/article-009-dup.md"),
                    ],
                    "contents_pages": [],
                },
            )
            with self.assertRaises(ManifestError):
                load(path)

    def test_load_fails_on_duplicate_target(self):
        with TemporaryDirectory() as td:
            path = _write(
                Path(td) / "manifest.json",
                {
                    "sources": [
                        self._valid_entry(),
                        self._valid_entry(id="uk-gdpr-art-009-alt"),
                    ],
                    "contents_pages": [],
                },
            )
            with self.assertRaises(ManifestError):
                load(path)

    def test_load_fails_on_http_scheme(self):
        with TemporaryDirectory() as td:
            path = _write(
                Path(td) / "manifest.json",
                {
                    "sources": [
                        self._valid_entry(source_uri="http://legislation.gov.uk/x"),
                    ],
                    "contents_pages": [],
                },
            )
            with self.assertRaises(ManifestError):
                load(path)

    def test_load_fails_on_unknown_kind(self):
        with TemporaryDirectory() as td:
            path = _write(
                Path(td) / "manifest.json",
                {
                    "sources": [self._valid_entry(kind="mystery")],
                    "contents_pages": [],
                },
            )
            with self.assertRaises(ManifestError):
                load(path)

    def test_load_fails_on_target_escaping_corpus(self):
        with TemporaryDirectory() as td:
            path = _write(
                Path(td) / "manifest.json",
                {
                    "sources": [self._valid_entry(target="../etc/passwd")],
                    "contents_pages": [],
                },
            )
            with self.assertRaises(ManifestError):
                load(path)


if __name__ == "__main__":
    unittest.main()
