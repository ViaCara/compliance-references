"""Personal data breach source coverage tests."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class BreachIncidentSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_breach_definition_and_incident_guidance(self):
        expected_targets = {
            "uk-gdpr-art-004": "statute/uk/gdpr/article-004.md",
            "ico-personal-data-breaches-guide": "guidance/uk/ico/personal-data-breaches-guide.md",
        }

        for source_id, target in expected_targets.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(target, self.sources[source_id]["target"])

    def test_guidance_covers_incident_decision_points(self):
        source = self.sources["ico-personal-data-breaches-guide"]
        fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))

        self.assertEqual("curated_quotes", fields["kind"])

        for heading in (
            "## What is a personal data breach?",
            "## Risk-assessing data breaches",
            "## When do we need to tell individuals about a breach?",
            "## What breaches do we need to notify the ICO about?",
            "## How much time do we have to report a breach?",
            "## Does the UK GDPR require us to take any other steps in response to a breach?",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, body)


if __name__ == "__main__":
    unittest.main()
