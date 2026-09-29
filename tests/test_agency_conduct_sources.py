"""Employment agency terms, introduction and record-keeping source tests (VIA-759)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

EXPECTED = {
    "conduct-regs-2003-reg-013": (
        "uksi/2003/3319/regulation/13/data.xht",
        "whether that service is a work-finding service for which the Act prohibits",
    ),
    "conduct-regs-2003-reg-016": (
        "uksi/2003/3319/regulation/16/data.xht",
        "for which it is permitted by regulation 26(1) to charge a fee",
    ),
    "conduct-regs-2003-reg-019": (
        "uksi/2003/3319/regulation/19/data.xht",
        "working with, caring for or attending a vulnerable person",
    ),
    "conduct-regs-2003-reg-020": (
        "uksi/2003/3319/regulation/20/data.xht",
        "would not be detrimental to the interests of the work-seeker or the hirer",
    ),
    "conduct-regs-2003-reg-022": (
        "uksi/2003/3319/regulation/22/data.xht",
        "obtained two references from persons who are not relatives",
    ),
    "conduct-regs-2003-reg-029": (
        "uksi/2003/3319/regulation/29/data.xht",
        "at least one year after the date on which the agency",
    ),
    "conduct-regs-2003-sch-004": (
        "uksi/2003/3319/schedule/4/data.xht",
        "Names of hirers to whom the work-seeker is introduced or supplied",
    ),
    "conduct-regs-2003-sch-005": (
        "uksi/2003/3319/schedule/5/data.xht",
        "Details of the position(s) the hirer seeks to fill",
    ),
}


class AgencyConductSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_agency_terms_and_records_sources(self):
        for source_id, (path, _) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertTrue(source["source_uri"].endswith(path))
                self.assertEqual("conduct-regs-2003", source["instrument"])
                self.assertEqual("in_force", source.get("enforcement_status", "in_force"))

    def test_sources_carry_controlling_text(self):
        for source_id, (_, phrase) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                body = (CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8")
                frontmatter, text = parse(body)
                self.assertEqual(source_id, frontmatter["id"])
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
