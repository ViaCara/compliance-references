"""Data subject complaint sources: DPA 2018 s. 164A."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class DataSubjectComplaintSourceTests(unittest.TestCase):
    def setUp(self):
        sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        self.source = next(s for s in sources if s["id"] == "dpa-2018-s-164a")

    def test_manifest_points_at_section_164a(self):
        self.assertEqual(
            "https://www.legislation.gov.uk/ukpga/2018/12/section/164A/data.xht",
            self.source["source_uri"],
        )
        self.assertEqual("statute/uk/dpa-2018/section-164a.md", self.source["target"])

    def test_corpus_pins_the_operative_duties(self):
        fields, body = parse((CORPUS / self.source["target"]).read_text(encoding="utf-8"))

        self.assertEqual("in_force", fields["enforcement_status"])
        self.assertEqual("dpa-2018-s-164a", fields["id"])
        self.assertEqual("DPA 2018 s. 164A", fields["citation"])
        self.assertEqual(self.source["source_uri"], fields["source_uri"])
        self.assertEqual("legislation_section", fields["kind"])
        for phrase in (
            "(1) A data subject may make a complaint to the controller if the data subject considers that, "
            "in connection with personal data relating to the data subject, there is an infringement of the "
            "UK GDPR or Part 3 of this Act.",
            "providing a complaint form which can be completed electronically and by other means",
            "acknowledge receipt of the complaint within the period of 30 days beginning when the complaint is received",
            "(b) inform the complainant of the outcome of the complaint.",
            "(b) informing the complainant about progress on the complaint.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)


if __name__ == "__main__":
    unittest.main()
