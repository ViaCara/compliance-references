"""Trade Marks Act 1994 sections 10 and 11: comparative advertising that
breaks the BPMMR 2008 conditions is trade mark use, and honest descriptive
use of a mark is not an infringement."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"
SOURCE_URIS = {
    "tma-1994-s-010": "https://www.legislation.gov.uk/ukpga/1994/26/section/10/data.xht",
    "tma-1994-s-011": "https://www.legislation.gov.uk/ukpga/1994/26/section/11/data.xht",
}
PASSAGES = {
    "tma-1994-s-010": [
        "uses the sign in comparative advertising in a manner that is contrary to the Business Protection from Misleading Marketing Regulations 2008",
        "takes unfair advantage of, or is detrimental to, the distinctive character or the repute of the trade mark",
    ],
    "tma-1994-s-011": [
        "the use of the trade mark for the purpose of identifying or referring to goods or services as those of the proprietor of that trade mark",
        "in particular where that use is necessary to indicate the intended purpose of a product or service",
        "provided the use is in accordance with honest practices in industrial or commercial matters",
    ],
}


class TradeMarkSourceTests(unittest.TestCase):
    def setUp(self):
        sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        self.sources = {source["id"]: source for source in sources}

    def test_manifest_declares_both_sections(self):
        for source_id in PASSAGES:
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual("legislation_section", source["kind"])
                self.assertEqual("tma-1994", source["instrument"])
                self.assertEqual(SOURCE_URIS[source_id], source["source_uri"])

    def test_files_carry_the_operative_text(self):
        for source_id, passages in PASSAGES.items():
            fields, body = parse((CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8"))
            self.assertEqual(source_id, fields["id"])
            self.assertEqual(SOURCE_URIS[source_id], fields["source_uri"])
            self.assertEqual("in_force", fields["enforcement_status"])
            text = re.sub(r"\s+", " ", body)
            for passage in passages:
                with self.subTest(source_id=source_id, passage=passage):
                    self.assertIn(passage, text)


if __name__ == "__main__":
    unittest.main()
