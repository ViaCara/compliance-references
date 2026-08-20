"""Legislation.gov.uk XHTML → GFM transformer tests."""

import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

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
        self.assertIn("_Provision repealed.", markdown)
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

    def test_keeps_closing_words_that_follow_a_sub_paragraph_list(self):
        """The operative limb of a provision often sits after its (a)/(b) list,
        in a bare LegP2Text outside any container. Dropping it silently removes
        the duty the provision imposes, leaving a body that reads complete."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegClearFix LegP2Container">'
            '<span class="LegDS LegLHS LegP2No">1.</span>'
            '<span class="LegDS LegP2Text LegRHS">Where a decision is-</span>'
            "</p>"
            '<p class="LegClearFix LegP3Container">'
            '<span class="LegDS LegLHS LegP3No">(a)</span>'
            '<span class="LegDS LegP3Text LegRHS">based on personal data, and</span>'
            "</p>"
            '<p class="LegClearFix LegP3Container">'
            '<span class="LegDS LegLHS LegP3No">(b)</span>'
            '<span class="LegDS LegP3Text LegRHS">solely automated,</span>'
            "</p>"
            '<p class="LegP2Text LegRHS">the controller must ensure safeguards '
            "are in place.</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="Test Article 22C")

        self.assertIn("the controller must ensure safeguards are in place.", markdown)

    def test_closing_words_are_not_duplicated_into_their_container(self):
        """Closing words are emitted once, in source order, and a provision
        whose text sits inside a container is not emitted twice."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegClearFix LegP2Container">'
            '<span class="LegDS LegLHS LegP2No">1.</span>'
            '<span class="LegDS LegP2Text LegRHS">Only text.</span>'
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="Test Article 1")

        self.assertEqual(1, markdown.count("Only text."))

    def test_fallback_ignores_page_furniture_outside_the_snippet(self):
        """Documents whose provision text carries none of the LegP*Container
        classes fall back to emitting bare paragraphs. legislation.gov.uk wraps
        the provision in LegSnippet and the surrounding page in sibling markup,
        so the fallback must stay inside the snippet or it emits licence and
        navigation furniture as though it were statute."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml">'
            '<div class="LegSnippet">'
            '<p class="LegP1ParaText">5. The amendments do not apply to any '
            "decision taken before 5th February 2026.</p>"
            "</div>"
            "<p>All content is available under the Open Government Licence "
            "v3.0 except where otherwise stated.</p>"
            "<p>Back to top</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="S.I. 2026/82 regulation 5")

        self.assertIn("decision taken before 5th February 2026.", markdown)
        self.assertNotIn("Open Government Licence", markdown)
        self.assertNotIn("Back to top", markdown)

    def test_transforms_leg_sp_schedule_paragraph_classes(self):
        """Some schedules (e.g. Equality Act 2010 Sch. 2) typeset their
        numbered paragraphs under LegSP*Container/No/Text rather than the
        LegP* family every section uses. Without recognising both, only a
        stray LegP-classed amendment quotation survives extraction and the
        rest of the schedule silently disappears."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegClearFix LegSP2Container">'
            '<span class="LegDS LegLHS LegSP2No">(1)</span>'
            '<span class="LegDS LegSP2Text LegRHS">A must comply with the first requirement.</span>'
            "</p>"
            '<p class="LegClearFix LegSP3Container">'
            '<span class="LegDS LegLHS LegSP3No">(a)</span>'
            '<span class="LegDS LegSP3Text LegRHS">to avoid the disadvantage.</span>'
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="Equality Act 2010 Sch. 2")

        self.assertIn("(1) A must comply with the first requirement.", markdown)
        self.assertIn("(a) to avoid the disadvantage.", markdown)

    def test_transforms_top_level_schedule_paragraph_number(self):
        """A schedule paragraph with no sub-items (e.g. Equality Act 2010
        Sch. 2 para. 1) carries its own number and text directly on a
        LegSP1Container leaf -- there is no LegP2Container etc. beneath it
        at all. `LegP1Container` at this same level means a section heading
        (handled once by `_find_title`), so the two must not be conflated:
        emitting this paragraph's number+text must not also duplicate or
        suppress the document title."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<h3><span class="LegDS LegP1No">2</span>'
            '<span class="LegDS LegP1GroupTitleFirst">The duty</span></h3>'
            '<p class="LegClearFix LegSP1Container">'
            '<span class="LegDS LegP1No">1</span>'
            '<span class="LegDS LegRHS LegP1Text">'
            "This Schedule applies where a duty to make reasonable "
            "adjustments is imposed on A by this Part.</span>"
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="Equality Act 2010 Sch. 2")

        self.assertIn("_The duty_", markdown)
        self.assertIn(
            "1 This Schedule applies where a duty to make reasonable "
            "adjustments is imposed on A by this Part.",
            markdown,
        )
        self.assertEqual(1, markdown.count("The duty"))

    def test_falls_back_to_leg_sn_numbers_on_a_paragraph_fragment(self):
        """A schedule paragraph fetched at paragraph granularity (e.g.
        .../schedule/1/paragraph/18/data.xht) has no ancestor to carry its
        own number, so legislation.gov.uk folds it into sibling LegSN1No
        (the paragraph number), LegSN2No (the first sub-item number), ...
        spans on the same LegSP2Container leaf instead of a LegP2No/
        LegSP2No this transformer otherwise looks for."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegClearFix LegSP2Container">'
            '<span class="LegDS LegSN1No">18</span>'
            '<span class="LegDS LegSN2No">(1)</span>'
            '<span class="LegDS LegRHS LegP2Text">This condition is met if&#8212;</span>'
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="DPA 2018 Sch. 1 para. 18")

        self.assertIn("18(1) This condition is met if—", markdown)

    def test_leg_sn_fallback_concatenates_more_than_two_levels(self):
        """The fallback is not hard-coded to paragraph+sub-item -- it walks
        LegSN1No, LegSN2No, LegSN3No, ... until one is missing, so a
        fragment nested three deep still carries its full number."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegClearFix LegSP2Container">'
            '<span class="LegDS LegSN1No">18</span>'
            '<span class="LegDS LegSN2No">(1)</span>'
            '<span class="LegDS LegSN3No">(a)</span>'
            '<span class="LegDS LegRHS LegP2Text">the processing is necessary.</span>'
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="DPA 2018 Sch. 1 para. 18")

        self.assertIn("18(1)(a) the processing is necessary.", markdown)

    def test_leg_sn_fallback_stops_at_an_empty_span(self):
        """An empty LegSN{n}No span (no text) must stop the walk rather
        than being appended as a blank segment, and must not probe deeper
        levels past it -- a gap in the middle is not a gap to skip over."""
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegClearFix LegSP2Container">'
            '<span class="LegDS LegSN1No">18</span>'
            '<span class="LegDS LegSN2No"></span>'
            '<span class="LegDS LegSN3No">(a)</span>'
            '<span class="LegDS LegRHS LegP2Text">the processing is necessary.</span>'
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="DPA 2018 Sch. 1 para. 18")

        self.assertIn("18 the processing is necessary.", markdown)
        self.assertNotIn("(a)", markdown)

    def test_leg_sn_fallback_is_bounded(self):
        """A malformed or adversarial document cannot spin the LegSN walk
        forever -- it stops at _MAX_SCHEDULE_FRAGMENT_DEPTH levels even if
        every level up to and past it is actually present."""
        max_depth = LegislationTransformer._MAX_SCHEDULE_FRAGMENT_DEPTH
        spans = "".join(
            f'<span class="LegDS LegSN{n}No">{n}</span>' for n in range(1, max_depth + 3)
        )
        source = (
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            f'<p class="LegClearFix LegSP2Container">{spans}'
            '<span class="LegDS LegRHS LegP2Text">text.</span>'
            "</p>"
            "</div>"
        )
        transformer = LegislationTransformer()
        markdown = transformer.transform(source, citation="Test")

        expected_number = "".join(str(n) for n in range(1, max_depth + 1))
        self.assertIn(f"{expected_number} text.", markdown)
        self.assertNotIn(str(max_depth + 1), markdown)


class ContainedElementsTests(unittest.TestCase):
    """`_contained_elements` decides which text is already covered by a
    container walk. Get it wrong in one direction and closing words vanish; in
    the other, every provision is emitted twice."""

    SOURCE = (
        '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
        '<p class="LegClearFix LegP2Container">'
        '<span class="LegDS LegP2Text LegRHS">Inside a container.</span>'
        "</p>"
        '<p class="LegP2Text LegRHS">Outside every container.</p>'
        "</div>"
    )

    def setUp(self):
        self.root = ET.fromstring(self.SOURCE)
        self.contained = LegislationTransformer()._contained_elements(self.root)

    def _find(self, text):
        for element in self.root.iter():
            if (element.text or "").strip() == text:
                return element
        raise AssertionError(f"no element with text {text!r}")

    def test_span_within_a_container_is_contained(self):
        self.assertIn(id(self._find("Inside a container.")), self.contained)

    def test_container_itself_is_contained(self):
        container = self._find("Inside a container.")
        parent = next(e for e in self.root.iter() if container in list(e))

        self.assertIn(id(parent), self.contained)

    def test_paragraph_outside_every_container_is_not_contained(self):
        self.assertNotIn(id(self._find("Outside every container.")), self.contained)

    def test_root_without_containers_yields_nothing_contained(self):
        root = ET.fromstring(
            '<div xmlns="http://www.w3.org/1999/xhtml" class="LegSnippet">'
            '<p class="LegP1ParaText">Sole paragraph.</p>'
            "</div>"
        )

        self.assertEqual(set(), LegislationTransformer()._contained_elements(root))


if __name__ == "__main__":
    unittest.main()
