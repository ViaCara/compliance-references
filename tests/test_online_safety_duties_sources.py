"""Online Safety Act 2023 risk assessment, illegal content and record-keeping source tests (VIA-742)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

EXPECTED = {
    "osa-2023-s-009": (
        "ukpga/2023/50/section/9/data.xht",
        "A duty to carry out a suitable and sufficient illegal content risk assessment",
    ),
    "osa-2023-s-010": (
        "ukpga/2023/50/section/10/data.xht",
        "terms of service",
    ),
    "osa-2023-s-020a": (
        "ukpga/2023/50/section/20A/data.xht",
        "intimate image content report",
    ),
    "osa-2023-s-022": (
        "ukpga/2023/50/section/22/data.xht",
        "users’ right to freedom of expression within the law",
    ),
    "osa-2023-s-023": (
        "ukpga/2023/50/section/23/data.xht",
        "of all aspects of every risk assessment under section 9 or 11",
    ),
    "osa-2023-s-067": (
        "ukpga/2023/50/section/67/data.xht",
        "reports that are to be made to the NCA",
    ),
    "osa-2023-sch-003": (
        "ukpga/2023/50/schedule/3/data.xht",
        "The first illegal content risk assessment of the service must be completed within the period of three months",
    ),
}


class OnlineSafetyDutiesSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_online_safety_duty_sources(self):
        for source_id, (path, _) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertTrue(source["source_uri"].endswith(path))
                self.assertEqual("osa-2023", source["instrument"])
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
