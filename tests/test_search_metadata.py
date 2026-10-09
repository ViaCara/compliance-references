"""Search metadata coverage tests.

ADR-0023: consumer search and the undeclared-domain audit read each source's
domain_tags and summary from index.json. A source without them falls back to
"uncategorised" and is hard to find.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
INDEX = ROOT / "index.json"
TAG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class SearchMetadataTests(unittest.TestCase):
    def test_every_manifest_source_carries_domain_tags_and_summary(self):
        for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]:
            with self.subTest(source_id=source["id"]):
                tags = source.get("domain_tags", [])
                self.assertTrue(tags, "domain_tags is empty")
                for tag in tags:
                    self.assertRegex(tag, TAG)
                self.assertEqual(len(tags), len(set(tags)), "duplicate tag")
                self.assertTrue(source.get("summary", "").strip(), "summary is empty")

    def test_index_carries_the_manifest_metadata(self):
        sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }
        for record in json.loads(INDEX.read_text(encoding="utf-8")):
            with self.subTest(source_id=record["id"]):
                source = sources[record["id"]]
                self.assertEqual(source.get("domain_tags", []), record["domain_tags"])
                self.assertEqual(source.get("summary", ""), record["summary"])


if __name__ == "__main__":
    unittest.main()
