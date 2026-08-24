"""Processor-contract and restricted-transfer source coverage tests.

A live compliance question (the Mistral data processing addendum against
ViaCara's Article 9 triage data) found the corpus had no guidance on what an
Article 28(3) contract must set out, and no citable instrument at the end of
the Chapter V transfer route. These tests pin the sources that closed both
gaps."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
INDEX = ROOT / "index.json"
CORPUS = ROOT / "corpus"


class ProcessorContractSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_processor_contract_sources(self):
        expected_paths = {
            "uk-gdpr-art-024": "eur/2016/679/article/24/data.xht",
            "uk-gdpr-art-045": "eur/2016/679/article/45/data.xht",
            "uk-gdpr-art-045a": "eur/2016/679/article/45A/data.xht",
            "uk-gdpr-art-045b": "eur/2016/679/article/45B/data.xht",
            "uk-gdpr-art-046": "eur/2016/679/article/46/data.xht",
            "uk-gdpr-art-047": "eur/2016/679/article/47/data.xht",
            "uk-gdpr-art-047a": "eur/2016/679/article/47A/data.xht",
            "uk-gdpr-art-049": "eur/2016/679/article/49/data.xht",
            "uk-gdpr-art-049a": "eur/2016/679/article/49A/data.xht",
            "dpa-2018-s-119a": "ukpga/2018/12/section/119A/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(self.sources[source_id]["source_uri"].endswith(path))

    def test_statute_sources_carry_controlling_text(self):
        expected = {
            "uk-gdpr-art-024": (
                "the controller shall implement appropriate technical and organisational "
                "measures to ensure and to be able to demonstrate that processing is "
                "performed in accordance with this Regulation"
            ),
            "uk-gdpr-art-045a": (
                "the Secretary of State may by regulations approve transfers of personal "
                "data to—"
            ),
            "uk-gdpr-art-045b": "the data protection test is met",
            "uk-gdpr-art-046": (
                "standard data protection clauses specified in a document issued (and not "
                "withdrawn) by the Commissioner for the purposes of this Article under "
                "section 119A of the 2018 Act"
            ),
            "uk-gdpr-art-047": "binding corporate rules",
            "uk-gdpr-art-047a": (
                "The Secretary of State may by regulations specify standard data protection "
                "clauses"
            ),
            "uk-gdpr-art-049": "the data subject has explicitly consented to the proposed transfer",
            "uk-gdpr-art-049a": "important reasons of public interest",
            "dpa-2018-s-119a": (
                "The Commissioner may issue a document specifying standard data protection "
                "clauses"
            ),
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

    def test_superseded_adequacy_article_is_marked_repealed(self):
        """Article 45 is the phrase a reader reaches for first. It was omitted on
        5 February 2026 by the Data (Use and Access) Act 2025, so it is mirrored
        only to stop it being cited as live."""
        source = self.sources["uk-gdpr-art-045"]
        self.assertEqual("repealed", source["enforcement_status"])
        fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
        self.assertEqual("repealed", fields["enforcement_status"])
        self.assertIn("Data (Use and Access) Act 2025", body)

    def test_curated_guidance_carries_the_contract_content_requirements(self):
        expected = {
            "ico-controller-processor-contracts": [
                "the type of personal data and categories of data subject",
                "Processing only on the documented instructions of the controller.",
                "If a processor acts outside of the controller’s instructions in such a way "
                "that it decides the purpose and means of processing",
            ],
            "edpb-guidelines-07-2020": [
                "It would not be adequate merely to specify that it is “personal data "
                "pursuant to Article 4(1) GDPR” or “special categories of personal data "
                "pursuant to Article 9”",
                "The processor shall not go beyond what is instructed by the controller.",
                "In any event, all elements of Article 28(3) must be covered by the contract.",
            ],
        }

        for source_id, quotes in expected.items():
            source = self.sources[source_id]
            fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
            with self.subTest(source_id=source_id):
                self.assertEqual("curated_quotes", source["kind"])
                self.assertEqual("guidance", fields["enforcement_status"])
                self.assertEqual(fields["content_sha256"], body_sha256(body))
            for quote in quotes:
                with self.subTest(source_id=source_id, quote=quote[:40]):
                    self.assertIn(quote, body)

    def test_edpb_guidance_states_its_persuasive_uk_status(self):
        """The corpus is UK-first. EU guidance is mirrored because the Article 28
        text it interprets is materially identical, not because it binds here."""
        source = self.sources["edpb-guidelines-07-2020"]
        _fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
        self.assertIn("persuasive, not binding", body)
        self.assertIn("the UK source controls", body)

    def test_index_summaries_are_discoverable_by_documented_instructions(self):
        """The consumer searches titles, domain tags and summaries, never bodies.
        A processor-contract question starts from the phrase "documented
        instructions", so both guidance summaries must carry it."""
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        hits = {
            record["id"]
            for record in index
            if "documented instructions" in record.get("summary", "").lower()
        }
        self.assertIn("ico-controller-processor-contracts", hits)
        self.assertIn("edpb-guidelines-07-2020", hits)


if __name__ == "__main__":
    unittest.main()
