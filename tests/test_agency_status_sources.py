"""Agency-status and price-claim sources: Conduct Regulations regs 6 and 32,
the FWA and GOV.UK guidance on agency scope and fees, and the CAP rules and
advice on "from" prices."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

STATUTE = {
    "conduct-regs-2003-reg-006": (
        "uksi/2003/3319/regulation/6/data.xht",
        ["identity of any future employer"],
    ),
    "conduct-regs-2003-reg-032": (
        "uksi/2003/3319/regulation/32/data.xht",
        [
            "conditional upon the work-seeker",
            "insert— “, or the person who is or would be supplied by the work-seeker to carry out the work”.",
            "substitute the following: “An employment business may not (whether by the inclusion of a term",
        ],
    ),
}

GUIDANCE = {
    "fwa-tutoring-services-guidance": "This is a criminal offence.",
    "fwa-conduct-regulations-overview": "online platforms and executive search consultants",
    "gov-uk-employment-agencies-and-businesses": "totally or mostly aimed at providing a work-finding service",
    "cap-advice-prices-general": "a significant proportion of sale items are discounted at the maximum saving",
    "cap-code-section-03-misleading-advertising": 'Price claims such as "up to" and "from" must not mislead',
}


def _flat(body: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"^> ?", "", body, flags=re.M))


class AgencyStatusSourceTests(unittest.TestCase):
    def setUp(self):
        sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        self.sources = {source["id"]: source for source in sources}

    def test_statute_entries_mirror_the_regulation(self):
        for source_id, (uri_tail, passages) in STATUTE.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual("legislation_regulation", source["kind"])
                self.assertTrue(source["source_uri"].endswith(uri_tail))
                fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
                self.assertEqual("in_force", fields["enforcement_status"])
                for passage in passages:
                    self.assertIn(passage, _flat(body))

    def test_guidance_entries_carry_the_relied_on_passage(self):
        for source_id, passage in GUIDANCE.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual("curated_quotes", source["kind"])
                fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
                self.assertEqual(source["source_uri"], fields["source_uri"])
                self.assertIn(passage, _flat(body))


if __name__ == "__main__":
    unittest.main()
