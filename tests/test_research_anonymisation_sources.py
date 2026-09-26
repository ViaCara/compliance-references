"""Purpose-compatibility, anonymisation and high-risk processing source tests.

A practitioner conversation-review feature needed to cite the further
processing test, the rules for data that no longer identifies anyone, the
research safeguards and the ICO's consent, anonymisation, special category,
AI and DPIA guidance. The corpus lacked all of them. These tests pin the
sources that closed the gap."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
INDEX = ROOT / "index.json"
CORPUS = ROOT / "corpus"


class ResearchAnonymisationSourceTests(unittest.TestCase):
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
            "uk-gdpr-art-008a": "the existence of appropriate safeguards (for example, encryption or pseudonymisation)",
            "uk-gdpr-art-011": "the controller shall not be obliged to maintain, acquire or process additional information",
            "uk-gdpr-art-084a": "Those purposes are referred to in this Chapter as “RAS purposes”.",
            "uk-gdpr-art-084c": "The requirement is not satisfied if the processing is likely to cause substantial damage or substantial distress",
            "uk-gdpr-art-084d": "The Secretary of State may by regulations",
        }

        for source_id, provision in expected.items():
            with self.subTest(source_id=source_id):
                fields, body = self._read(source_id)
                self.assertEqual(self.sources[source_id]["source_uri"], fields["source_uri"])
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertIn(provision, body)

    def test_omitted_research_article_is_marked_repealed(self):
        """ICO guidance still cites Article 89(1). The Data (Use and Access) Act
        2025 omitted it on 5 February 2026, so it is mirrored only to stop it
        being cited as live; Articles 84A to 84D carry the current law."""
        self.assertEqual("repealed", self.sources["uk-gdpr-art-089"]["enforcement_status"])
        fields, body = self._read("uk-gdpr-art-089")
        self.assertEqual("repealed", fields["enforcement_status"])
        self.assertIn("Art. 89 omitted (5.2.2026)", body)

    def test_curated_guidance_carries_the_controlling_passages(self):
        expected = {
            "ico-consent": [
                "Explicit consent must be expressly confirmed in words.",
                "It must also be as easy to withdraw consent as it was to give it.",
            ],
            "ico-anonymisation": [
                "This is known as the motivated intruder test.",
                "Pseudonymised data is personal data in the hands of someone who holds the additional information.",
            ],
            "ico-special-category-data": [
                "child psychotherapists; and",
                "you are processing special category data regardless of how confident you are that the inference is correct",
            ],
            "ico-ai-and-data-protection": [
                "In the vast majority of cases, the use of AI will involve a type of processing likely to result in a high risk",
            ],
            "ico-dpia-guidance": [
                "Individual professionals processing patient or client data are not processing on a large scale.",
                "In most cases, a combination of two of these factors indicates the need for a DPIA.",
            ],
        }

        for source_id, quotes in expected.items():
            source = self.sources[source_id]
            fields, body = self._read(source_id)
            with self.subTest(source_id=source_id):
                self.assertEqual("curated_quotes", source["kind"])
                self.assertEqual("guidance", fields["enforcement_status"])
                self.assertEqual(fields["content_sha256"], body_sha256(body))
                self.assertTrue(source["source_uri"].startswith("https://ico.org.uk/"))
            for quote in quotes:
                with self.subTest(source_id=source_id, quote=quote[:40]):
                    self.assertIn(quote, body)

    def test_index_finds_the_motivated_intruder_test(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        hits = {
            record["id"]
            for record in index
            if "motivated-intruder" in record.get("domain_tags", [])
        }
        self.assertEqual({"ico-anonymisation"}, hits)


if __name__ == "__main__":
    unittest.main()
