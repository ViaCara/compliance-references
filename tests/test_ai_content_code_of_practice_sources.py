"""Commission Code of Practice on Transparency of AI-Generated Content tests."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

SOURCE_ID = "eu-commission-ai-content-cop-2026"
SOURCE_URI = "https://ec.europa.eu/newsroom/dae/redirection/document/129555"

PHRASES = (
    # Section 1: the two marking layers and the text exceptions.
    "will implement a multi-layered marking approach to ensure that the outputs of their "
    "generative AI systems are marked with at least two layers of machine-readable marking",
    "given that free-form text cannot transport metadata, a single-layer of marking as "
    "described in Sub-measure 1.1.2 is considered sufficient",
    "Signatories will record information in the metadata on whether the content is "
    "AI-generated or manipulated.",
    "is marked with an imperceptible watermark, with the exception of very short text.",
    "“very short text” should be understood as text shorter than 200 tokens.",
    "relying on fingerprinting or logging alone is not considered sufficient",
    "Signatories will make the detection solution available free of charge.",
    "will implement an interoperability solution for their detection mechanisms by "
    "2 February 2027",
    # Section 2: the icon or label for deployers.
    "the capitalised acronym “AI” in the English language",
    "a short audible disclaimer in plain and simple natural language",
    "in the top right corner of an image or video deep fake",
    "adherence to the Code does not constitute conclusive evidence of compliance",
)


class AiContentCodeOfPracticeSourceTests(unittest.TestCase):
    def setUp(self):
        sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }
        self.source = sources[SOURCE_ID]
        self.fields, self.body = parse(
            (CORPUS / self.source["target"]).read_text(encoding="utf-8")
        )

    def test_manifest_points_at_the_final_code(self):
        self.assertEqual(SOURCE_URI, self.source["source_uri"])
        self.assertEqual("curated_quotes", self.source["kind"])
        self.assertEqual(SOURCE_URI, self.fields["source_uri"])
        self.assertEqual("guidance", self.fields["enforcement_status"])
        self.assertEqual(body_sha256(self.body), self.fields["content_sha256"])

    def test_body_carries_the_marking_and_labelling_text(self):
        flat = " ".join(self.body.replace(">", " ").split())
        for phrase in PHRASES:
            with self.subTest(phrase=phrase[:40]):
                self.assertIn(phrase, flat)


if __name__ == "__main__":
    unittest.main()
