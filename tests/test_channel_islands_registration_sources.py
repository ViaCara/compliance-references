"""Channel Islands registration sources: Guernsey DPL 2017 s. 39 and the
Data Protection Authority (Jersey) Law 2018 Article 17."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


def _source(source_id):
    sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
    return next(s for s in sources if s["id"] == source_id)


def _flat(text):
    return " ".join(text.split())


class ChannelIslandsRegistrationSourceTests(unittest.TestCase):
    def test_guernsey_s39_gates_registration_on_establishment(self):
        source = _source("guernsey-dpl-2017-s-039")
        fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))

        self.assertEqual(source["source_uri"], fields["source_uri"])
        self.assertEqual(body_sha256(body), fields["content_sha256"])
        for phrase in (
            "39. (1) A controller or processor established in the Bailiwick must not cause or permit "
            "personal data to be processed unless the controller or (as the case may be) processor is -",
            "(a) registered in accordance with Schedule 4, or",
            "is guilty of an offence.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, _flat(body.replace("> ", "")))

    def test_jersey_art17_quotes_the_statute(self):
        source = _source("jersey-authority-law-2018-art-017")
        fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))

        self.assertEqual(
            "https://www.jerseylaw.je/laws/current/PDFs/L_4_2018.pdf", source["source_uri"]
        )
        self.assertEqual(source["source_uri"], fields["source_uri"])
        self.assertEqual("pdf", fields["source_format"])
        self.assertEqual("in_force", fields["enforcement_status"])
        self.assertEqual(body_sha256(body), fields["content_sha256"])
        for phrase in (
            "(1) A controller or processor established in Jersey must not cause or permit personal data "
            "to be processed without being registered as a controller or processor under this Article.",
            "(2) However, Regulations may make such exemptions from the requirements to register under "
            "this Article as the States think fit.",
            "(6) A person who contravenes paragraph (1) is guilty of an offence.",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, _flat(body.replace("> ", "")))


if __name__ == "__main__":
    unittest.main()
