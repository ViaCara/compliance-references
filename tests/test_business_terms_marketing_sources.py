"""Business-to-business terms and marketing sources: UCTA 1977
ss. 3 and 11, BPMMR 2008 regs 3 and 4 and the CAP Code prices and "free"
rules 3.17 to 3.26."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

STATUTE = {
    "ucta-1977-s-003": (
        "ucta-1977",
        "ukpga/1977/50/section/3/data.xht",
        "on the other’s written standard terms of business",
    ),
    "ucta-1977-s-011": (
        "ucta-1977",
        "ukpga/1977/50/section/11/data.xht",
        "how far it was open to him to cover himself by insurance",
    ),
    "bpmmr-2008-reg-003": (
        "bpmmr-2008",
        "uksi/2008/1276/regulation/3/data.xht",
        "the price or manner in which the price is calculated",
    ),
    "bpmmr-2008-reg-004": (
        "bpmmr-2008",
        "uksi/2008/1276/regulation/4/data.xht",
        "Comparative advertising shall, as far as the comparison is concerned, be permitted only",
    ),
}

CAP_ID = "cap-code-section-03-misleading-advertising"
CAP_PASSAGES = [
    "Price statements must not mislead by omission, undue emphasis or distortion.",
    "Quoted prices must include non-optional taxes, duties, fees and charges",
    "make clear the extent of the commitment the consumer must make to obtain the advertised price",
    'Price claims such as "up to" and "from" must not mislead',
    "anything other than the unavoidable cost of responding",
    'the extent of the commitment the consumer must make to take advantage of a "free" offer',
    'Marketers must not describe an element of a package as "free"',
    'Marketers must not use the term "free trial"',
]


class BusinessTermsMarketingSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_statute_sources(self):
        for source_id, (instrument, path, _) in STATUTE.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertTrue(source["source_uri"].endswith(path))
                self.assertEqual(instrument, source["instrument"])

    def test_statute_files_carry_controlling_text(self):
        for source_id, (_, _, phrase) in STATUTE.items():
            with self.subTest(source_id=source_id):
                fields, text = parse((CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8"))
                self.assertEqual(source_id, fields["id"])
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertIn(phrase, re.sub(r"\s+", " ", text))

    def test_cap_section_three_carries_prices_and_free_rules(self):
        _, body = parse((CORPUS / self.sources[CAP_ID]["target"]).read_text(encoding="utf-8"))
        text = re.sub(r"\s+", " ", re.sub(r"^> ?", "", body, flags=re.M))
        for rule in range(17, 27):
            with self.subTest(rule=rule):
                self.assertIn(f"Rule 3.{rule}:", body)
        for passage in CAP_PASSAGES:
            with self.subTest(passage=passage):
                self.assertIn(passage, text)


if __name__ == "__main__":
    unittest.main()
