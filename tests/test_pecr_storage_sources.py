"""PECR storage and access source coverage."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

        body = (ROOT / "corpus" / source["target"]).read_text(encoding="utf-8")
        self.assertIn("strictly necessary", body)
        self.assertIn("automatically authenticating the identity", body)


if __name__ == "__main__":
    unittest.main()
