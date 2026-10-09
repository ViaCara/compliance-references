"""Payment, charity and data-sharing source tests.

These tests pin the payment services perimeter, the charity law, the
data-sharing code and the controller guidance: the sources that decide when a
third party funding a service carries on a payment service, when a business
becomes a commercial participator and which data protection role each party
takes."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class PaymentCharityDataSharingSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def _read(self, source_id):
        source = self.sources[source_id]
        return parse((CORPUS / source["target"]).read_text(encoding="utf-8"))

    def test_in_force_statute_carries_controlling_text(self):
        expected = {
            "psr-2017-reg-002": "“money remittance” means a service for the transmission of money",
            "psr-2017-reg-038": "limited network exclusion",
            "psr-2017-sch-001": "commercial agent authorised in an agreement to negotiate or conclude",
            "emr-2011-reg-002": "is accepted by a person other than the electronic money issuer",
            "conduct-regs-2003-reg-025": "shall not request or directly or indirectly receive money on behalf of a work-seeker",
            "charities-act-2011-s-002": "is for the public benefit",
            "charities-act-2011-s-003": "the advancement of health or the saving of lives",
            "charities-act-2011-s-004": "it is not to be presumed that a purpose of a particular description is for the public benefit",
            "charities-act-2011-s-017": "must have regard to any such guidance",
            "charities-act-1992-s-058": "“commercial participator”, in relation to any charitable institution, means",
            "charities-act-1992-s-059": "unlawful for a commercial participator to represent that charitable contributions",
            "charities-act-1992-s-060": "commercial participator",
            "dpa-2018-s-121": "code of practice which contains",
            "dpa-2018-s-204": "“health professional” means any of the following",
            "uk-gdpr-art-029": "shall not process those data except on instructions from the controller",
        }

        for source_id, provision in expected.items():
            with self.subTest(source_id=source_id):
                fields, body = self._read(source_id)
                self.assertEqual(self.sources[source_id]["source_uri"], fields["source_uri"])
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertIn(provision, body)

    def test_payment_schedule_carries_both_parts(self):
        """The commercial agent, technical service provider and limited network
        exclusions sit in Part 2. A schedule mirror with Part 1 alone would
        make every platform look like a payment service."""
        _, body = self._read("psr-2017-sch-001")
        self.assertIn("are payment services", body)
        self.assertIn("technical service providers", body)
        self.assertIn("limited network of service providers", body)

    def test_curated_guidance_carries_the_controlling_passages(self):
        expected = {
            "fca-perg-15-5": [
                "only if you have the authority to affect the legal relations of your principal",
                "payment instruments that can be used on online marketplaces are unlikely to do so",
            ],
            "charity-commission-pb1": [
                "That ‘someone’ might be an individual or an organisation.",
                "‘the poor’ does not just mean the very poorest in society",
            ],
            "charity-commission-pb2": [
                "the level of provision that trustees make for the poor must be more than minimal or token",
            ],
            "charity-commission-cc3": [
                "in some cases trustees may have to reimburse the charity personally",
                "make balanced and adequately informed decisions, thinking about the long term as well as the short term",
            ],
            "charity-commission-cc20": [
                "Before the fundraising begins, you must enter into a written agreement which has all the details that the law requires.",
            ],
            "ico-data-sharing-code": [
                "data sharing does not include providing data access to employees or contractors, or with processors",
            ],
            "ico-joint-controllers": [
                "Controllers will not be joint controllers if they are processing the same data for different purposes",
            ],
            "ico-controllers-and-processors": [
                "it cannot take any of the overarching decisions, such as what types of personal data to collect",
            ],
            "edpb-guidelines-07-2020": [
                "Joint controllership may also be excluded in a situation where several entities use a shared database or a common infrastructure, if each entity independently determines its own purposes.",
            ],
            "cap-code-section-03-misleading-advertising": [
                "has been approved, endorsed or authorised by any public or private",
            ],
            "cma-unfair-commercial-practices-cma207": [
                "Displaying a trust mark, quality mark or equivalent without having",
            ],
        }

        for source_id, quotes in expected.items():
            source = self.sources[source_id]
            fields, body = self._read(source_id)
            with self.subTest(source_id=source_id):
                self.assertEqual("curated_quotes", source["kind"])
                self.assertEqual(fields["content_sha256"], body_sha256(body))
            for quote in quotes:
                with self.subTest(source_id=source_id, quote=quote[:40]):
                    self.assertIn(quote, body)


if __name__ == "__main__":
    unittest.main()
