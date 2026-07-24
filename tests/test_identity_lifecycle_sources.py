"""Identity-lifecycle source coverage tests."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class IdentityLifecycleSourceTests(unittest.TestCase):
    def test_manifest_carries_current_identity_lifecycle_sources(self):
        sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

        expected_paths = {
            "uk-gdpr-art-026": "article/26/data.xht",
            "uk-gdpr-art-022a": "article/22A/data.xht",
            "uk-gdpr-art-022b": "article/22B/data.xht",
            "uk-gdpr-art-022c": "article/22C/data.xht",
            "uk-gdpr-art-022d": "article/22D/data.xht",
            "uk-gdpr-art-044a": "article/44A/data.xht",
            "uk-gdpr-art-084b": "article/84B/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(sources[source_id]["source_uri"].endswith(path))

    def test_superseded_identity_sources_are_rebuilt_as_repealed(self):
        sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

        for source_id in (
            "uk-gdpr-art-022",
            "uk-gdpr-art-044",
            "dpa-2018-s-014",
        ):
            with self.subTest(source_id=source_id):
                source = sources[source_id]
                fields, _body = parse(
                    (CORPUS / source["target"]).read_text(encoding="utf-8")
                )

                self.assertEqual("repealed", source["enforcement_status"])

                self.assertEqual("repealed", fields["enforcement_status"])

                self.assertEqual("2026-07-24", fields["last_fetched"])

                self.assertEqual(source["source_uri"], fields["source_uri"])


if __name__ == "__main__":
    unittest.main()
