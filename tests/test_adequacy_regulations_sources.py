"""UK GDPR Article 45A adequacy regulation sources."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse
from lib.transformer_legislation import LegislationTransformer


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
INDEX = ROOT / "index.json"
CORPUS = ROOT / "corpus"
FIXTURES = Path(__file__).parent / "fixtures"

# Raw legislation.gov.uk XHTML captured 2026-10-07 (revision Wed, 30 Sep 2026 16:18:53 GMT).
SOURCE_FIXTURES = {
    "adequacy-usa-regs-2023-reg-003": "uksi_2023_1028_regulation_003.xhtml",
    "dpa-2018-sch-021-p-004": "dpa_2018_schedule_021_paragraph_004.xhtml",
}

EXPECTED = {
    "adequacy-usa-regs-2023-reg-002": (
        "adequacy-usa-regs-2023",
        "uksi/2023/1028/regulation/2/data.xht",
        "UK Extension to the EU-US Data Privacy Framework",
    ),
    "adequacy-usa-regs-2023-reg-003": (
        "adequacy-usa-regs-2023",
        "uksi/2023/1028/regulation/3/data.xht",
        "adequate level of protection",
    ),
    "adequacy-usa-regs-2023-reg-004": (
        "adequacy-usa-regs-2023",
        "uksi/2023/1028/regulation/4/data.xht",
        "Federal Trade Commission",
    ),
    "adequacy-korea-regs-2022-reg-002": (
        "adequacy-korea-regs-2022",
        "uksi/2022/1213/regulation/2/data.xht",
        "Republic of Korea",
    ),
    "adequacy-korea-regs-2022-reg-003": (
        "adequacy-korea-regs-2022",
        "uksi/2022/1213/regulation/3/data.xht",
        "Personal Information Protection Commission",
    ),
    "dpa-2018-sch-021-p-004": (
        "dpa-2018",
        "ukpga/2018/12/schedule/21/paragraph/4/data.xht",
        "treated as approved by regulations made under Article 45A",
    ),
    "dpa-2018-sch-021-p-005": (
        "dpa-2018",
        "ukpga/2018/12/schedule/21/paragraph/5/data.xht",
        "an EEA state",
    ),
}


class AdequacyRegulationSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_every_article_45a_route(self):
        for source_id, (instrument, path, _) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertTrue(source["source_uri"].endswith(path))
                self.assertEqual(instrument, source["instrument"])
                self.assertIn("cross-border-transfer", source["domain_tags"])
                self.assertEqual("in_force", source.get("enforcement_status", "in_force"))

    def test_sources_carry_controlling_text(self):
        for source_id, (_, _, phrase) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                body = (CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8")
                frontmatter, text = parse(body)
                self.assertEqual(source_id, frontmatter["id"])
                self.assertIn(phrase, " ".join(text.split()))

    def test_index_registers_each_source_with_its_body_hash(self):
        index = {entry["id"]: entry for entry in json.loads(INDEX.read_text(encoding="utf-8"))}
        for source_id in EXPECTED:
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                frontmatter, text = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
                self.assertEqual(source["target"], index[source_id]["path"])
                self.assertEqual(frontmatter["content_sha256"], index[source_id]["sha"])
                self.assertEqual(body_sha256(text), frontmatter["content_sha256"])

    def test_load_bearing_bodies_match_the_raw_source(self):
        transformer = LegislationTransformer()
        for source_id, fixture in SOURCE_FIXTURES.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                raw = (FIXTURES / fixture).read_text(encoding="utf-8")
                _, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
                self.assertEqual(transformer.transform(raw, citation=source["citation"]), body)


if __name__ == "__main__":
    unittest.main()
