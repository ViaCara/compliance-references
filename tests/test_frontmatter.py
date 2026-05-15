"""Frontmatter round-trip + hash stability tests (stdlib unittest)."""

import unittest

from lib.frontmatter import (
    FrontmatterError,
    body_sha256,
    parse,
    render,
)


class FrontmatterTests(unittest.TestCase):
    def test_render_then_parse_round_trip(self):
        fields = {
            "id": "uk-gdpr-art-009",
            "title": "UK GDPR Article 9 - Processing of special categories of personal data",
            "instrument": "uk-gdpr",
            "kind": "legislation_article",
            "language": "en-GB",
        }
        body = "Body text.\n"
        rendered = render(fields, body)
        parsed_fields, parsed_body = parse(rendered)

        self.assertEqual(parsed_fields["id"], fields["id"])
        self.assertEqual(parsed_fields["title"], fields["title"])
        self.assertEqual(parsed_body, body)

    def test_render_preserves_field_order(self):
        fields = {"id": "a", "title": "t", "kind": "legislation_article"}
        rendered = render(fields, "body")

        self.assertTrue(rendered.startswith("---\n"))
        # Frontmatter keys should appear in insertion order.
        self.assertLess(rendered.index("id:"), rendered.index("title:"))
        self.assertLess(rendered.index("title:"), rendered.index("kind:"))

    def test_body_sha256_stable_across_frontmatter_changes(self):
        fields_a = {"id": "x", "kind": "legislation_article"}
        fields_b = {"id": "x", "kind": "legislation_article", "extra": "ignored"}
        body = "Same body\n"
        rendered_a = render(fields_a, body)
        rendered_b = render(fields_b, body)

        self.assertEqual(body_sha256(rendered_a), body_sha256(rendered_b))

    def test_body_sha256_differs_when_body_differs(self):
        fields = {"id": "x", "kind": "legislation_article"}
        rendered_a = render(fields, "body one\n")
        rendered_b = render(fields, "body two\n")

        self.assertNotEqual(body_sha256(rendered_a), body_sha256(rendered_b))

    def test_parse_raises_on_missing_frontmatter(self):
        with self.assertRaises(FrontmatterError):
            parse("no frontmatter here\n")

    def test_parse_raises_on_unterminated_frontmatter(self):
        with self.assertRaises(FrontmatterError):
            parse("---\nid: x\nbody without closing\n")

    def test_parse_handles_quoted_strings_and_dates(self):
        text = (
            "---\n"
            "id: uk-gdpr-art-009\n"
            'title: "UK GDPR Article 9 - special category"\n'
            "kind: legislation_article\n"
            "last_fetched: 2026-05-01\n"
            "---\n"
            "Body.\n"
        )
        fields, body = parse(text)

        self.assertEqual(fields["id"], "uk-gdpr-art-009")
        self.assertEqual(fields["title"], "UK GDPR Article 9 - special category")
        self.assertEqual(fields["last_fetched"], "2026-05-01")
        self.assertEqual(body, "Body.\n")


if __name__ == "__main__":
    unittest.main()
