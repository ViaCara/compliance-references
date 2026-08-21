"""Financial-perimeter and AML source coverage tests (MLR 2017, FSMA, FPO, RAO)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class FinancialPerimeterSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_financial_perimeter_sources(self):
        expected_paths = {
            "mlr-2017-reg-018": "uksi/2017/692/regulation/18/data.xht",
            "mlr-2017-reg-018a": "uksi/2017/692/regulation/18A/data.xht",
            "mlr-2017-reg-028": "uksi/2017/692/regulation/28/data.xht",
            "mlr-2017-reg-040": "uksi/2017/692/regulation/40/data.xht",
            "mlr-2017-reg-056": "uksi/2017/692/regulation/56/data.xht",
            "fsma-2000-s-019": "ukpga/2000/8/section/19/data.xht",
            "fsma-2000-s-021": "ukpga/2000/8/section/21/data.xht",
            "fpo-2005-art-049": "uksi/2005/1529/article/49/data.xht",
            "fpo-2005-art-050a": "uksi/2005/1529/article/50A/data.xht",
            "rao-2001-art-060b": "uksi/2001/544/article/60B/data.xht",
            "rao-2001-art-061": "uksi/2001/544/article/61/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(self.sources[source_id]["source_uri"].endswith(path))

    def test_financial_perimeter_sources_carry_controlling_text(self):
        expected = {
            "mlr-2017-reg-018": (
                "(1) A relevant person must take appropriate steps to identify and "
                "assess the risks of money laundering and terrorist financing"
            ),
            "mlr-2017-reg-028": "(a) identify the customer unless the identity of that customer",
            "mlr-2017-reg-056": "(1) Unless a person in respect of whom the registering authorities",
            "fsma-2000-s-019": "(1) No person may carry on a regulated activity in the United Kingdom",
            "fsma-2000-s-021": "communicate an invitation or inducement to",
            "fpo-2005-art-049": "(1) The financial promotion restriction does not apply",
            "rao-2001-art-061": "(1) Entering into a regulated mortgage contract as lender",
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

    def test_statutory_instrument_lead_paragraphs_survive_extraction(self):
        """PECR regulation 22 lost its (1)-(3) lead paragraphs before the
        LegP{n}ParaText fix; guard the real corpus, not only the fixture."""
        source = self.sources["pecr-reg-022"]
        _fields, body = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))

        self.assertIn("(1) This regulation applies to the transmission", body)
        self.assertIn("(2) Except in the circumstances referred to in paragraph (3)", body)
