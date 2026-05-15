"""EUR-Lex HTML → GFM transformer tests."""

import unittest
from pathlib import Path

from lib.transformer_eur_lex import EurLexTransformer


FIXTURES = Path(__file__).parent / "fixtures"


class EurLexTransformerTests(unittest.TestCase):
    def test_transforms_synthetic_article(self):
        source = (FIXTURES / "synthetic_eur_lex_article.html").read_text(
            encoding="utf-8"
        )
        transformer = EurLexTransformer()
        markdown = transformer.transform(
            source,
            citation="EU AI Act Article 6",
        )

        self.assertIn("# EU AI Act Article 6", markdown)
        self.assertIn("Classification rules for high-risk AI systems", markdown)
        self.assertIn("Irrespective of whether an AI system", markdown)
        self.assertIn("(a) the AI system is intended", markdown)
        self.assertIn("Annex III", markdown)

    def test_strips_html_tags(self):
        source = (
            "<html><body><div class='eli-container'>"
            "<p class='oj-doc-ti'>Article 1</p>"
            "<p class='oj-normal'>Hello <em>world</em> with <strong>bold</strong>.</p>"
            "</div></body></html>"
        )
        transformer = EurLexTransformer()
        markdown = transformer.transform(source, citation="Test Article 1")

        self.assertIn("Hello world with bold.", markdown)
        self.assertNotIn("<em>", markdown)
        self.assertNotIn("<strong>", markdown)

    def test_raises_when_main_container_missing(self):
        source = "<html><body><p>nothing useful</p></body></html>"
        transformer = EurLexTransformer()
        with self.assertRaises(ValueError):
            transformer.transform(source, citation="EU GDPR Article 99")


if __name__ == "__main__":
    unittest.main()
