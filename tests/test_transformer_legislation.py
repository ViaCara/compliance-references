"""Legislation.gov.uk XHTML → GFM transformer tests."""

import unittest
from pathlib import Path

from lib.transformer_legislation import LegislationTransformer


FIXTURES = Path(__file__).parent / "fixtures"


class LegislationTransformerTests(unittest.TestCase):
    def test_transforms_synthetic_article(self):
        source = (FIXTURES / "synthetic_legislation_article.xhtml").read_text(
            encoding="utf-8"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(
            source,
            citation="UK GDPR Article 9",
        )

        # Heading carries the citation.
        self.assertIn("# UK GDPR Article 9", markdown)
        # Title text.
        self.assertIn("Processing of special categories of personal data", markdown)
        # Numbered paragraphs.
        self.assertIn("1. Processing of personal data revealing", markdown)
        self.assertIn(
            "2. Paragraph 1 shall not apply", markdown
        )
        # Sub-paragraph (a) and (h).
        self.assertIn("(a) the data subject has given explicit consent.", markdown)
        self.assertIn(
            "(h) processing is necessary for the purposes of preventive", markdown
        )

    def test_real_uk_gdpr_article_009_extraction(self):
        path = FIXTURES / "uk_gdpr_article_009.xhtml"
        if not path.exists():
            self.skipTest("real fixture not captured")
        source = path.read_text(encoding="utf-8")
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="UK GDPR Article 9")

        self.assertIn("# UK GDPR Article 9", markdown)
        self.assertIn("special categories", markdown.lower())
        self.assertIn("racial or ethnic origin", markdown)
        self.assertIn("explicit consent", markdown)

    def test_collapses_repealed_dot_only_paragraphs_into_marker(self):
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<h5 class="LegClearFix LegP1ContainerFirst">'
            '<span class="LegDS LegP1No">14</span>'
            '<span class="LegDS LegP1GroupTitleFirst">Automated decision-making</span>'
            "</h5>"
            '<p class="LegRHS LegP1Text">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</p>'
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="DPA 2018 s. 14")

        self.assertIn("# DPA 2018 s. 14", markdown)
        self.assertIn("_Provision repealed", markdown)
        # Run of dots must NOT appear in the output.
        self.assertNotIn(". . . . . . . . . .", markdown)

    def test_collapses_repealed_dot_only_numbered_paragraphs(self):
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<h5><span class="LegDS LegP1No">21</span><span class="LegDS LegP1GroupTitleFirst">Definitions</span></h5>'
            '<p class="LegClearFix LegP2Container"><span class="LegDS LegLHS LegP2No">(1)</span><span class="LegDS LegRHS LegP2Text">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</span></p>'
            '<p class="LegClearFix LegP2Container"><span class="LegDS LegLHS LegP2No">(2)</span><span class="LegDS LegRHS LegP2Text">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</span></p>'
            '<p class="LegClearFix LegP2Container"><span class="LegDS LegLHS LegP2No">(3)</span><span class="LegDS LegRHS LegP2Text">Active text here.</span></p>'
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="DPA 2018 s. 21")

        self.assertNotIn(". . . . . . . . . .", markdown)
        self.assertIn("(1) _(repealed)_", markdown)
        self.assertIn("(2) _(repealed)_", markdown)
        self.assertIn("(3) Active text here.", markdown)

    def test_strips_change_delimiters_but_keeps_additions(self):
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            "<h3><span class=\"LegP1No\">Section 1</span></h3>"
            "<p>Original text <span class=\"LegChangeDelimiter\">[</span>"
            "<span class=\"LegAddition\">added later</span>"
            "<span class=\"LegChangeDelimiter\">]</span>"
            " continued.</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="Test Section 1")

        self.assertIn("added later", markdown)
        self.assertNotIn("[", markdown)
        self.assertNotIn("]", markdown)


if __name__ == "__main__":
    unittest.main()
