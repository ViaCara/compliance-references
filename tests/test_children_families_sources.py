"""Children and families source coverage tests (VIA-686)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class ChildrenFamiliesSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_current_children_families_sources(self):
        sources = self.sources

        expected_paths = {
            "uk-gdpr-art-008": "article/8/data.xht",
            "uk-gdpr-art-008za": "article/8ZA/data.xht",
            "uk-gdpr-annex-001": "annex/1/data.xht",
            "dpa-2018-s-011": "section/11/data.xht",
            "dpa-2018-s-042": "section/42/data.xht",
            "dpa-2018-s-123": "section/123/data.xht",
            "dpa-2018-s-127": "section/127/data.xht",
            "dpa-2018-sch-001-p-002": "schedule/1/paragraph/2/data.xht",
            "dpa-2018-sch-001-pt-002-p-005": "schedule/1/paragraph/5/data.xht",
            "dpa-2018-sch-001-pt-004-p-039": "schedule/1/paragraph/39/data.xht",
            "osa-2023-s-003": "section/3/data.xht",
            "osa-2023-s-011": "section/11/data.xht",
            "osa-2023-s-012": "section/12/data.xht",
            "osa-2023-s-020": "section/20/data.xht",
            "osa-2023-s-021": "section/21/data.xht",
            "osa-2023-s-035": "section/35/data.xht",
            "osa-2023-s-036": "section/36/data.xht",
            "osa-2023-s-037": "section/37/data.xht",
            "osa-2023-s-055": "section/55/data.xht",
            "osa-2023-s-061": "section/61/data.xht",
            "osa-2023-s-066": "section/66/data.xht",
            "osa-2023-sch-001": "schedule/1/data.xht",
            "osa-2023-s-214a": "section/214A/data.xht",
            "children-act-1989-s-002": "section/2/data.xht",
            "children-act-1989-s-003": "section/3/data.xht",
            "children-act-2004-s-011": "section/11/data.xht",
            "family-law-reform-act-1969-s-008": "section/8/data.xht",
            "childrens-wellbeing-and-schools-act-2026-s-070": "section/70/data.xht",
            "childrens-wellbeing-and-schools-act-2026-s-072": "section/72/data.xht",
            "crime-and-policing-act-2026-s-085": "section/85/data.xht",
            "crime-and-policing-act-2026-s-092": "section/92/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(sources[source_id]["source_uri"].endswith(path))

    def test_new_children_families_sources_carry_controlling_text(self):
        expected = {
            "uk-gdpr-art-008": (
                "in_force",
                "the child is at least 13 years old",
            ),
            "uk-gdpr-art-008za": (
                "in_force",
                "at least the age for the time being specified in Article 8(1)",
            ),
            "uk-gdpr-annex-001": (
                "in_force",
                "safeguarding a vulnerable individual",
            ),
            "osa-2023-s-035": (
                "in_force",
                "age verification or age estimation is used on the service",
            ),
            "osa-2023-s-214a": (
                "in_force",
                "for the purpose of protecting relevant children from a risk of harm",
            ),
            "dpa-2018-s-123": (
                "in_force",
                "does not include preventive or counselling services",
            ),
            "children-act-1989-s-002": (
                "in_force",
                "More than one person may have parental responsibility for the same child",
            ),
            "crime-and-policing-act-2026-s-085": (
                "prospective",
                "reason to suspect that a child sex offence may have been committed",
            ),
        }

        for source_id, (status, provision) in expected.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                fields, body = parse(
                    (CORPUS / source["target"]).read_text(encoding="utf-8")
                )

                self.assertEqual(source_id, fields["id"])
                self.assertEqual(source["source_uri"], fields["source_uri"])
                self.assertEqual(status, fields["enforcement_status"])
                self.assertIn(provision, body)

    def test_prospective_crime_and_policing_sources_are_marked_prospective(self):
        # Crime and Policing Act 2026 ss.85/92 are real, Royal Assent 29.4.2026,
        # but not yet commenced (checked against both commencement SIs made so
        # far) -- getting this wrong would misclassify a future duty as a
        # current blocking violation.
        for source_id in ("crime-and-policing-act-2026-s-085", "crime-and-policing-act-2026-s-092"):
            with self.subTest(source_id=source_id):
                self.assertEqual("prospective", self.sources[source_id]["enforcement_status"])

    def test_ico_curated_guidance_sources_exist_with_matching_hash(self):
        for source_id in (
            "ico-age-appropriate-design-code",
            "ico-children-and-uk-gdpr",
            "ico-age-assurance-childrens-code",
        ):
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual("curated_quotes", source["kind"])

                path = CORPUS / source["target"]
                self.assertTrue(path.exists())

                fields, body = parse(path.read_text(encoding="utf-8"))
                import hashlib

                self.assertEqual(
                    fields["content_sha256"],
                    hashlib.sha256(body.encode("utf-8")).hexdigest(),
                )

    def test_age_appropriate_design_code_carries_all_15_standards(self):
        source = self.sources["ico-age-appropriate-design-code"]
        _fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))

        for n in range(1, 16):
            with self.subTest(standard=n):
                self.assertIn(f"**Standard {n}:", body)

    def test_age_assurance_guidance_states_self_declaration_is_insufficient_for_high_risk(self):
        source = self.sources["ico-age-assurance-childrens-code"]
        _fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
        normalised = " ".join(body.replace("\n> ", " ").split())

        self.assertIn(
            "self-declaration on its own is an appropriate method for services that are considered high risk",
            normalised,
        )


if __name__ == "__main__":
    unittest.main()
