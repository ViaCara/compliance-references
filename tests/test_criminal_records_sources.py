"""Criminal-record vetting source coverage tests (VIA-716)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

CURATED_GUIDANCE = (
    "ico-criminal-offence-data",
    "ico-pre-employment-vetting",
    "dbs-code-of-practice",
    "dbs-handling-certificate-information",
    "dbs-update-service-employer-guide",
    "dbs-eligibility-enhanced-barred-list-children",
    "accessni-code-of-practice",
    "accessni-self-employed-viewing-guidance",
)


class CriminalRecordsSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_criminal_records_statute_sources(self):
        expected_paths = {
            "uk-gdpr-art-010": "eur/2016/679/article/10/data.xht",
            "dpa-2018-sch-001-pt-001-p-001": "ukpga/2018/12/schedule/1/paragraph/1/data.xht",
            "dpa-2018-sch-001-pt-002-p-006": "ukpga/2018/12/schedule/1/paragraph/6/data.xht",
            "dpa-2018-sch-001-pt-002-p-010": "ukpga/2018/12/schedule/1/paragraph/10/data.xht",
            "dpa-2018-sch-001-pt-002-p-011": "ukpga/2018/12/schedule/1/paragraph/11/data.xht",
            "dpa-2018-sch-001-pt-002-p-017": "ukpga/2018/12/schedule/1/paragraph/17/data.xht",
            "dpa-2018-sch-001-pt-003-p-029": "ukpga/2018/12/schedule/1/paragraph/29/data.xht",
            "dpa-2018-sch-001-pt-003-p-030": "ukpga/2018/12/schedule/1/paragraph/30/data.xht",
            "dpa-2018-sch-001-pt-003-p-032": "ukpga/2018/12/schedule/1/paragraph/32/data.xht",
            "dpa-2018-sch-001-pt-003-p-033": "ukpga/2018/12/schedule/1/paragraph/33/data.xht",
            "dpa-2018-sch-001-pt-003-p-036": "ukpga/2018/12/schedule/1/paragraph/36/data.xht",
            "dpa-2018-sch-001-pt-003-p-037": "ukpga/2018/12/schedule/1/paragraph/37/data.xht",
            "dpa-2018-sch-001-pt-004-p-038": "ukpga/2018/12/schedule/1/paragraph/38/data.xht",
            "dpa-2018-sch-001-pt-004-p-040": "ukpga/2018/12/schedule/1/paragraph/40/data.xht",
            "dpa-2018-sch-001-pt-004-p-041": "ukpga/2018/12/schedule/1/paragraph/41/data.xht",
            "police-act-1997-s-113a": "ukpga/1997/50/section/113A/data.xht",
            "police-act-1997-s-113b": "ukpga/1997/50/section/113B/data.xht",
            "police-act-1997-s-116a": "ukpga/1997/50/section/116A/data.xht",
            "police-act-1997-s-124": "ukpga/1997/50/section/124/data.xht",
            "criminal-records-regs-2002-reg-005a": "uksi/2002/233/regulation/5A/data.xht",
            "roa-exceptions-order-1975-art-003": "uksi/1975/1023/article/3/data.xht",
            "roa-exceptions-order-1975-sch-001": "uksi/1975/1023/schedule/1/data.xht",
            "svga-2006-s-007": "ukpga/2006/47/section/7/data.xht",
            "svga-2006-s-009": "ukpga/2006/47/section/9/data.xht",
            "svga-2006-sch-004-p-001": "ukpga/2006/47/schedule/4/paragraph/1/data.xht",
            "svga-2006-sch-004-p-002": "ukpga/2006/47/schedule/4/paragraph/2/data.xht",
            "svga-2006-sch-004-p-003": "ukpga/2006/47/schedule/4/paragraph/3/data.xht",
            "pvg-scotland-act-2007-s-045a": "asp/2007/14/section/45A/data.xht",
            "pvg-scotland-act-2007-s-045c": "asp/2007/14/section/45C/data.xht",
            "pvg-scotland-act-2007-s-045d": "asp/2007/14/section/45D/data.xht",
            "pvg-scotland-act-2007-s-045g": "asp/2007/14/section/45G/data.xht",
            "pvg-scotland-act-2007-s-046": "asp/2007/14/section/46/data.xht",
            "pvg-scotland-act-2007-s-054": "asp/2007/14/section/54/data.xht",
            "disclosure-scotland-act-2020-sch-003": "asp/2020/13/schedule/3/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(self.sources[source_id]["source_uri"].endswith(path))
                self.assertEqual(
                    "in_force",
                    self.sources[source_id].get("enforcement_status", "in_force"),
                )

    def test_sources_carry_controlling_text(self):
        expected = {
            "uk-gdpr-art-010": "only under the control of official authority",
            "dpa-2018-sch-001-pt-002-p-010": "detection of an unlawful act",
            "dpa-2018-sch-001-pt-002-p-017": "confidential counselling, advice or support",
            "dpa-2018-sch-001-pt-003-p-029": "the data subject has given consent to the processing",
            "dpa-2018-sch-001-pt-003-p-036": (
                "but for an express requirement for the processing to be necessary "
                "for reasons of substantial public interest"
            ),
            "dpa-2018-sch-001-pt-004-p-040": "period of 6 months beginning when the controller ceases",
            "dpa-2018-sch-001-pt-004-p-041": "which condition is relied on",
            "police-act-1997-s-113b": "enhanced criminal record certificate",
            "police-act-1997-s-116a": "relevant person",
            "police-act-1997-s-124": "commits an offence",
            "criminal-records-regs-2002-reg-005a": "section 113B",
            "roa-exceptions-order-1975-art-003": "section 4(2)",
            "roa-exceptions-order-1975-sch-001": "regulated activity relating to children",
            "svga-2006-s-007": "seeks to engage in regulated activity from which he is barred",
            "svga-2006-s-009": "personnel supplier commits an offence",
            "svga-2006-sch-004-p-001": "carried out frequently by the same person",
            "svga-2006-sch-004-p-002": "advice or guidance provided wholly or mainly for children",
            "pvg-scotland-act-2007-s-045a": "period of 5 years",
            "pvg-scotland-act-2007-s-045c": "offence for an individual to carry out",
            "pvg-scotland-act-2007-s-045d": "offence for an organisation",
            "pvg-scotland-act-2007-s-054": "third party",
            "disclosure-scotland-act-2020-sch-003": (
                "Providing counselling, therapy or advice or guidance in relation to "
                "health or wellbeing to children"
            ),
        }

        for source_id, provision in expected.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                fields, body = parse(
                    (CORPUS / source["target"]).read_text(encoding="utf-8")
                )

                self.assertEqual(source_id, fields["id"])
                self.assertEqual(source["source_uri"], fields["source_uri"])
                self.assertEqual("in_force", fields["enforcement_status"])
                self.assertIn(provision, body)

    def test_curated_guidance_is_declared_hashed_and_marked_guidance(self):
        for source_id in CURATED_GUIDANCE:
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual("curated_quotes", source["kind"])
                text = (CORPUS / source["target"]).read_text(encoding="utf-8")
                fields, body = parse(text)

                self.assertEqual(source_id, fields["id"])
                self.assertEqual("guidance", fields["enforcement_status"])
                self.assertEqual(body_sha256(text), fields["content_sha256"])
                self.assertIn("Reviewed 2026-09-03 by kylewelsby", " ".join(body.split()))
                self.assertGreaterEqual(body.count("\n> "), 10)
