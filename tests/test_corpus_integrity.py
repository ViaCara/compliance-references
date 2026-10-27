"""The committed corpus matches its own hashes, and index.json matches the corpus.

A hand edit of a mirrored body, or a corpus change without a rebuilt index,
fails here, so the Mira gate cannot merge it.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse
from lib.index import write_index
from lib.manifest import load

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"


class CorpusIntegrityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = load(ROOT / "manifest.json").sources

    def test_every_body_matches_its_recorded_hash(self) -> None:
        mismatches = []
        for source in self.sources:
            text = (CORPUS / source["target"]).read_text(encoding="utf-8")
            recorded = parse(text)[0].get("content_sha256")
            if recorded != body_sha256(text):
                mismatches.append(source["target"])
        self.assertEqual(mismatches, [], "corpus bodies changed without a rebuild")

    def test_index_matches_the_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            rebuilt = Path(scratch) / "index.json"
            write_index(rebuilt, self.sources, CORPUS)
            self.assertEqual(
                rebuilt.read_text(encoding="utf-8"),
                (ROOT / "index.json").read_text(encoding="utf-8"),
                "index.json is stale: run python3 build.py",
            )


if __name__ == "__main__":
    unittest.main()
