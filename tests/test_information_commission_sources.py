"""Information Commission sources.

The Data (Use and Access) Act 2025 abolished the office of Information
Commissioner and transferred its functions to the Information Commission on
30 September 2026. These tests pin the sections that made the change, the
regulation that commenced them and the UK GDPR definition that now names the
Commission."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
INDEX = ROOT / "index.json"
CORPUS = ROOT / "corpus"

EXPECTED = {
    "duaa-2025-s-118": {
        "source_uri": "https://www.legislation.gov.uk/ukpga/2025/18/section/118/data.xht",
        "target": "statute/uk/duaa-2025/section-118.md",
        "passages": [
            "(1) The office of Information Commissioner is abolished.",
            "(7) Omit Schedule 12 (the Information Commissioner).",
        ],
    },
    "duaa-2025-s-119": {
        "source_uri": "https://www.legislation.gov.uk/ukpga/2025/18/section/119/data.xht",
        "target": "statute/uk/duaa-2025/section-119.md",
        "passages": [
            "(1) The functions of the Information Commissioner are transferred to the Information Commission.",
            "is to be treated as a reference to the Information Commission.",
        ],
    },
    "duaa-2025-uksi-1015-reg-002": {
        "source_uri": "https://www.legislation.gov.uk/uksi/2026/1015/regulation/2/data.xht",
        "target": "statute/uk/duaa-2025/uksi-1015-regulation-002.md",
        "passages": [
            "come into force on 30th September 2026",
            "(a) section 117(4)(a) (the Information Commission: omission of section 205(2)(l) of the Data Protection Act 2018);",
            "(b) section 118 (abolition of the office of Information Commissioner);",
            "(c) section 119 (transfer of functions to the Information Commission).",
        ],
    },
    "uk-gdpr-art-004": {
        "source_uri": "https://www.legislation.gov.uk/eur/2016/679/article/4/data.xht",
        "target": "statute/uk/gdpr/article-004.md",
        "passages": [
            "(A2A) ‘the Commission’ means the Information Commission (see section 114A of the 2018 Act);",
            "(A3) _(repealed)_",
        ],
    },
}


class InformationCommissionSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }
        self.index = {
            record["id"]: record
            for record in json.loads(INDEX.read_text(encoding="utf-8"))
        }

    def test_sources_are_declared_with_canonical_uris(self):
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual(expected["source_uri"], source["source_uri"])
                self.assertEqual(expected["target"], source["target"])

    def test_sources_are_in_force_in_corpus_and_index(self):
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                fields, _body = parse((CORPUS / expected["target"]).read_text(encoding="utf-8"))
                self.assertEqual(source_id, fields["id"])
                self.assertEqual(expected["source_uri"], fields["source_uri"])
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertEqual("in_force", self.index[source_id]["enforcement_status"])

    def test_sources_carry_the_controlling_text(self):
        for source_id, expected in EXPECTED.items():
            _fields, body = parse((CORPUS / expected["target"]).read_text(encoding="utf-8"))
            for passage in expected["passages"]:
                with self.subTest(source_id=source_id, passage=passage[:40]):
                    self.assertIn(passage, body)

    def test_article_4_no_longer_defines_the_commissioner(self):
        _fields, body = parse((CORPUS / EXPECTED["uk-gdpr-art-004"]["target"]).read_text(encoding="utf-8"))
        self.assertNotIn("‘the Commissioner’ means the Information Commissioner", body)


if __name__ == "__main__":
    unittest.main()
