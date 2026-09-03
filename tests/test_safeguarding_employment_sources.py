"""Safeguarding and employment-agency source coverage tests (VIA-711)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

SVGA_SECTION_36_GROUNDS = (
    "svga-2006-sch-003-p-001",
    "svga-2006-sch-003-p-002",
    "svga-2006-sch-003-p-004",
    "svga-2006-sch-003-p-007",
    "svga-2006-sch-003-p-008",
    "svga-2006-sch-003-p-010",
)


class SafeguardingEmploymentSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_safeguarding_and_employment_agency_sources(self):
        expected_paths = {
            "svga-2006-s-006": "ukpga/2006/47/section/6/data.xht",
            "svga-2006-s-036": "ukpga/2006/47/section/36/data.xht",
            "svga-2006-s-060": "ukpga/2006/47/section/60/data.xht",
            "svga-2006-sch-003-p-001": "ukpga/2006/47/schedule/3/paragraph/1/data.xht",
            "svga-2006-sch-003-p-002": "ukpga/2006/47/schedule/3/paragraph/2/data.xht",
            "svga-2006-sch-003-p-004": "ukpga/2006/47/schedule/3/paragraph/4/data.xht",
            "svga-2006-sch-003-p-007": "ukpga/2006/47/schedule/3/paragraph/7/data.xht",
            "svga-2006-sch-003-p-008": "ukpga/2006/47/schedule/3/paragraph/8/data.xht",
            "svga-2006-sch-003-p-010": "ukpga/2006/47/schedule/3/paragraph/10/data.xht",
            "eaa-1973-s-006": "ukpga/1973/35/section/6/data.xht",
            "eaa-1973-s-013": "ukpga/1973/35/section/13/data.xht",
            "conduct-regs-2003-reg-026": "uksi/2003/3319/regulation/26/data.xht",
            "conduct-regs-2003-sch-003": "uksi/2003/3319/schedule/3/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(self.sources[source_id]["source_uri"].endswith(path))
                self.assertEqual("in_force", self.sources[source_id].get("enforcement_status", "in_force"))

    def test_sources_carry_controlling_text(self):
        expected = {
            "svga-2006-s-006": "he makes, or authorises the making of, arrangements",
            "svga-2006-s-036": "An employment agency acts for a person if it makes arrangements with him",
            "svga-2006-s-060": "“personnel supplier” means",
            "svga-2006-sch-003-p-004": "conduct which endangers a child or is likely to endanger a child",
            "eaa-1973-s-006": "shall not request or directly or indirectly receive any fee from any person",
            "eaa-1973-s-013": "“employment agency” means the business",
            "conduct-regs-2003-reg-026": "shall not apply in respect of a fee charged by an agency",
            "conduct-regs-2003-sch-003": "Professional sports person.",
        }

        for source_id, provision in expected.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                fields, body = parse(
                    (CORPUS / source["target"]).read_text(encoding="utf-8")
                )

                self.assertEqual(source_id, fields["id"])
                self.assertEqual(source["source_uri"], fields["source_uri"])
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertIn(provision, body)

    def test_every_schedule_3_ground_section_36_names_is_mirrored(self):
        # Section 36(4) makes the duty to refer turn on Schedule 3 paragraphs
        # 1, 2, 7 and 8 (automatic barring) and 4 and 10 (relevant conduct).
        # A consumer citing section 36 must be able to cite each ground.
        _, body = parse(
            (CORPUS / self.sources["svga-2006-s-036"]["target"]).read_text(encoding="utf-8")
        )
        self.assertIn("paragraph 1, 2, 7 or 8 of Schedule 3", body)
        self.assertIn("paragraph 4 or 10 of Schedule 3", body)
        for source_id in SVGA_SECTION_36_GROUNDS:
            with self.subTest(source_id=source_id):
                self.assertTrue((CORPUS / self.sources[source_id]["target"]).exists())
