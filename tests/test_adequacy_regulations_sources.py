"""UK GDPR Article 45A adequacy regulation sources (VIA-941)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

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


if __name__ == "__main__":
    unittest.main()
