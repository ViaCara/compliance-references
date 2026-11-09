"""Consumer Rights (Payment Surcharges) Regulations 2012 and Value Added Tax
Act 1994 Schedule 9 Group 7: the ban on fees for consumer card and similar
payments, the health-services exclusion that applies to regulation 4 only, and
the VAT exemption for medical care by registered health professionals."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"
SURCHARGES = "https://www.legislation.gov.uk/uksi/2012/3110/regulation/{}/data.xht"
SOURCES = {
    "payment-surcharges-regs-2012-reg-002": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("2")),
    "payment-surcharges-regs-2012-reg-003": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("3")),
    "payment-surcharges-regs-2012-reg-004": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("4")),
    "payment-surcharges-regs-2012-reg-005": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("5")),
    "payment-surcharges-regs-2012-reg-006a": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("6A")),
    "payment-surcharges-regs-2012-reg-006b": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("6B")),
    "payment-surcharges-regs-2012-reg-010": ("legislation_regulation", "payment-surcharges-regs-2012", SURCHARGES.format("10")),
    "vata-1994-sch-009-grp-007": (
        "legislation_schedule",
        "vata-1994",
        "https://www.legislation.gov.uk/ukpga/1994/23/schedule/9/part/II/chapter/7/data.xht",
    ),
}
PASSAGES = {
    "payment-surcharges-regs-2012-reg-002": [
        "means an individual acting for purposes which are wholly or mainly outside that individual's trade, business, craft or profession",
    ],
    "payment-surcharges-regs-2012-reg-003": [
        "have the meanings given in regulation 2(1) of the Payment Services Regulations 2017",
    ],
    "payment-surcharges-regs-2012-reg-004": [
        "fees that exceed the cost borne by the trader for the use of that means",
    ],
    "payment-surcharges-regs-2012-reg-005": [
        "by health professionals to patients to assess, maintain or restore their state of health",
    ],
    "payment-surcharges-regs-2012-reg-006a": [
        "A payee must not charge a payer any fee in respect of payment by means of",
        "is not a commercial card as defined in Article 2(6) of that Regulation",
        "a fee which exceeds the costs borne by the payee for the use of that specific payment instrument",
    ],
    "payment-surcharges-regs-2012-reg-006b": [
        "regulation 6A(2) applies but regulation 6A(1) does not apply",
    ],
    "payment-surcharges-regs-2012-reg-010": [
        "the contract for the purposes of which the payment is made is to be treated as providing for the",
    ],
    "vata-1994-sch-009-grp-007": [
        "The supply of services consisting in the provision of medical care by a person registered or enrolled in any of the following",
        "the register kept under the Health Professions Order 2001",
        "where the services are wholly performed or directly supervised by a person who is so registered or enrolled",
        "designed to promote the physical or mental welfare of elderly, sick, distressed or disabled persons",
    ],
}


class PaymentSurchargeVatHealthSourceTests(unittest.TestCase):
    def setUp(self):
        sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        self.sources = {source["id"]: source for source in sources}

    def test_manifest_declares_each_source(self):
        for source_id, (kind, instrument, uri) in SOURCES.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual(kind, source["kind"])
                self.assertEqual(instrument, source["instrument"])
                self.assertEqual(uri, source["source_uri"])

    def test_files_carry_the_operative_text(self):
        for source_id, passages in PASSAGES.items():
            fields, body = parse((CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8"))
            self.assertEqual(source_id, fields["id"])
            self.assertEqual(SOURCES[source_id][2], fields["source_uri"])
            self.assertEqual("in_force", fields["enforcement_status"])
            text = re.sub(r"\s+", " ", body).replace("’", "'")
            for passage in passages:
                with self.subTest(source_id=source_id, passage=passage):
                    self.assertIn(passage, text)


if __name__ == "__main__":
    unittest.main()
