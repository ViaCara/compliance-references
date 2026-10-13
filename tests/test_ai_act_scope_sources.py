"""EU AI Act scope, classification and Digital Omnibus source tests."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

CELLAR = "https://publications.europa.eu/resource/cellar/"
AI_ACT = CELLAR + "dc8116a1-3fe6-11ef-865a-01aa75ed71a1.0006.03/DOC_1"
OMNIBUS = CELLAR + "b459c07f-86fb-11f1-bf5e-01aa75ed71a1.0006.03/DOC_1"

EXPECTED = {
    "eu-ai-act-2024-art-002": (AI_ACT, "where the output produced by the AI system is used in the Union"),
    "eu-ai-act-2024-art-004": (AI_ACT, "sufficient level of AI literacy"),
    "eu-ai-act-2024-art-006": (AI_ACT, "shall always be considered to be high-risk where the AI system performs profiling"),
    "eu-ai-act-2024-art-113": (AI_ACT, "It shall apply from 2 August 2026."),
    "eu-ai-act-2024-anx-003": (AI_ACT, "Employment, workers’ management and access to self-employment"),
    "eu-ai-omnibus-2026-art-001": (OMNIBUS, "Regulation (EU) 2024/1689 is amended as follows"),
    "eu-ai-omnibus-2026-art-004": (OMNIBUS, "This Regulation shall enter into force"),
}


class AiActScopeSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_scope_and_omnibus_sources_from_the_cellar(self):
        for source_id, (uri, _) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(uri, self.sources[source_id]["source_uri"])

    def test_sources_carry_controlling_text(self):
        for source_id, (_, phrase) in EXPECTED.items():
            with self.subTest(source_id=source_id):
                body = (CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8")
                frontmatter, text = parse(body)
                self.assertEqual(source_id, frontmatter["id"])
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
