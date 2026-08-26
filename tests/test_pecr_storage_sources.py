"""PECR storage and access source coverage."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.json"


class PecrStorageSourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.sources = {source["id"]: source for source in manifest["sources"]}

    def test_strict_necessity_clause_is_pinned(self):
        source = self.sources["pecr-sch-a1-p-004"]

        self.assertTrue(
            source["source_uri"].endswith(
                "/uksi/2003/2426/schedule/A1/paragraph/4/data.xht"
            )
        )

        fields, provision = parse(
            (ROOT / "corpus" / source["target"]).read_text(encoding="utf-8")
        )

        self.assertEqual("pecr-sch-a1-p-004", fields["id"])
        self.assertEqual(source["source_uri"], fields["source_uri"])
        self.assertEqual("in_force", fields["enforcement_status"])
        self.assertEqual(fields["content_sha256"], body_sha256(provision))
        self.assertIn("Regulation 6(1) does not apply", provision)
        self.assertIn("strictly necessary", provision)
        self.assertIn("automatically authenticating the identity", provision)

    def test_authentication_search_finds_the_clause(self):
        records = json.loads(INDEX.read_text(encoding="utf-8"))
        hits = {
            record["id"]
            for record in records
            if "authentication"
            in " ".join(
                [
                    record["title"],
                    *record.get("domain_tags", []),
                    record.get("summary", ""),
                ]
            ).lower()
        }

        self.assertIn("pecr-sch-a1-p-004", hits)


if __name__ == "__main__":
    unittest.main()
