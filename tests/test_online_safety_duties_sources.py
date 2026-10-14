"""Online Safety Act 2023 risk assessment, illegal content and record-keeping source tests (VIA-742)."""

import html
import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"
FIXTURES = Path(__file__).parent / "fixtures"

S_I_2023_1420 = "in force at 10.1.2024 by S.I. 2023/1420"
CRIME_AND_POLICING_2026 = "(29.6.2026) by Crime and Policing Act 2026 (c. 20)"

COMMENCEMENT = {
    "osa_2023_section_009.xhtml": ["S. 9 " + S_I_2023_1420],
    "osa_2023_section_010.xhtml": [
        "S. 10 " + S_I_2023_1420,
        "S. 10(3A)(3B) inserted " + CRIME_AND_POLICING_2026,
        "S.I. 2026/689",
    ],
    "osa_2023_section_020a.xhtml": ["S. 20A inserted " + CRIME_AND_POLICING_2026, "S.I. 2026/689"],
    "osa_2023_section_022.xhtml": ["S. 22 " + S_I_2023_1420],
    "osa_2023_section_023.xhtml": [
        "S. 23(1)-(10) " + S_I_2023_1420,
        "S. 23(11) in force at 10.1.2024 for specified purposes by S.I. 2023/1420",
    ],
    "osa_2023_section_067.xhtml": ["S. 67 " + S_I_2023_1420],
    "osa_2023_schedule_003.xhtml": ["Sch. 3 para. 1 " + S_I_2023_1420],
}

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
                self.assertEqual("in_force", frontmatter["enforcement_status"])
                self.assertIn(phrase, text)

    def test_commencement_annotations_support_in_force_status(self):
        for fixture, notes in COMMENCEMENT.items():
            annotations = _annotation_text(FIXTURES / fixture)
            for note in notes:
                with self.subTest(fixture=fixture, note=note):
                    self.assertIn(note, annotations)


def _annotation_text(path):
    raw = path.read_text(encoding="utf-8").split('class="LegAnnotations"', 1)[1]
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s*,", ",", re.sub(r"\s+", " ", text))


if __name__ == "__main__":
    unittest.main()
