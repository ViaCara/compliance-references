"""Direct marketing definition and ICO guidance source coverage.

Every marketing verdict turns on whether a message is direct marketing at
all. The corpus previously held only PECR regulation 22, which says what may
not be sent but never defines the term. These tests pin the statutory
definition (PECR regulation 2, DPA 2018 section 122(5)) and the ICO guidance
that draws the service-message boundary and the mixed-message rule."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
INDEX = ROOT / "index.json"
CORPUS = ROOT / "corpus"

DEFINITION = (
    "the communication (by whatever means) of advertising or marketing material "
    "which is directed to particular individuals"
)


class DirectMarketingSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def _read(self, source_id):
        source = self.sources[source_id]
        fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
        self.assertEqual(source_id, fields["id"])
        self.assertEqual(source["source_uri"], fields["source_uri"])
        self.assertEqual(fields["content_sha256"], body_sha256(body))
        return fields, body

    def test_statute_sources_carry_the_definition(self):
        expected = {
            "pecr-reg-002": "uksi/2003/2426/regulation/2/data.xht",
            "dpa-2018-s-122": "ukpga/2018/12/section/122/data.xht",
        }

        for source_id, path in expected.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(self.sources[source_id]["source_uri"].endswith(path))
                fields, body = self._read(source_id)
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertIn(f"“direct marketing” means {DEFINITION}", body)

    def test_pecr_regulation_2_records_the_duaa_insertion(self):
        _fields, body = self._read("pecr-reg-002")

        self.assertIn("Data (Use and Access) Act 2025", self.sources["pecr-reg-002"]["summary"])
        self.assertIn("“electronic mail” means", body)

    def test_guidance_sources_draw_the_service_message_boundary(self):
        expected = {
            "ico-direct-marketing-guidance-identify": (
                "If your service message has elements that are direct marketing, even "
                "if that is not the main purpose of your message, then it will count "
                "as direct marketing."
            ),
            "ico-electronic-mail-marketing-key-concepts": (
                "However, if you add advertising or marketing material the message "
                "becomes direct marketing."
            ),
            "ico-guide-to-pecr-electronic-mail-marketing": (
                "you must not send electronic mail marketing to individuals, unless:"
            ),
        }

        for source_id, quote in expected.items():
            with self.subTest(source_id=source_id):
                fields, body = self._read(source_id)
                self.assertEqual("curated_quotes", fields["kind"])
                self.assertEqual("guidance", fields["enforcement_status"])
                self.assertIn(quote, body)

    def test_direct_marketing_search_finds_the_definition(self):
        records = json.loads(INDEX.read_text(encoding="utf-8"))
        hits = {
            record["id"]
            for record in records
            if "direct-marketing" in record.get("domain_tags", [])
        }

        self.assertEqual(
            {
                "pecr-reg-002",
                "dpa-2018-s-122",
                "ico-direct-marketing-guidance-identify",
                "ico-electronic-mail-marketing-key-concepts",
                "ico-guide-to-pecr-electronic-mail-marketing",
            },
            hits,
        )


if __name__ == "__main__":
    unittest.main()
