"""Price-comparison guidance coverage: the CMA compliance advice on price
reduction claims, which a "below the usual rate" marker must satisfy."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"
SOURCE_ID = "cma-price-reduction-claims-online"


class PriceComparisonSourceTests(unittest.TestCase):
    def setUp(self):
        sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        self.source = {source["id"]: source for source in sources}[SOURCE_ID]

    def test_manifest_declares_curated_cma_guidance(self):
        self.assertEqual("curated_quotes", self.source["kind"])
        self.assertEqual("guidance/uk/cma/price-reduction-claims-online.md", self.source["target"])
        self.assertIn("price-comparison", self.source["domain_tags"])

    def test_file_carries_source_retrieval_and_status(self):
        fields, _ = parse((CORPUS / self.source["target"]).read_text(encoding="utf-8"))
        self.assertEqual(self.source["source_uri"], fields["source_uri"])
        self.assertTrue(fields["last_fetched"])
        self.assertEqual("guidance", fields["enforcement_status"])

    def test_file_carries_the_usual_selling_price_test(self):
        _, body = parse((CORPUS / self.source["target"]).read_text(encoding="utf-8"))
        text = re.sub(r"\s+", " ", re.sub(r"^> ?", "", body, flags=re.M))
        for passage in [
            "we mean any discount or special offer price that refers to a higher comparison price",
            "The higher price is not now the product’s usual selling price",
            "The higher price in a price reduction claim must be a genuine and realistic selling price",
            "keep adequate records to show that these claims genuinely reflect selling conditions",
        ]:
            with self.subTest(passage=passage):
                self.assertIn(passage, text)


if __name__ == "__main__":
    unittest.main()
