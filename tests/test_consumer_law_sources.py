"""Consumer-law source coverage tests (DMCC 2024 Chapter 1, CRA 2015 Part 2,
the Consumer Contracts Regulations 2013 and the E-Commerce Regulations 2002)."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class ConsumerLawSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_consumer_law_sources(self):
        expected_paths = {
            "dmcc-2024-s-226": "ukpga/2024/13/section/226/data.xht",
            "dmcc-2024-s-227": "ukpga/2024/13/section/227/data.xht",
            "dmcc-2024-s-228": "ukpga/2024/13/section/228/data.xht",
            "dmcc-2024-s-229": "ukpga/2024/13/section/229/data.xht",
            "dmcc-2024-s-230": "ukpga/2024/13/section/230/data.xht",
            "dmcc-2024-s-245": "ukpga/2024/13/section/245/data.xht",
            "dmcc-2024-s-246": "ukpga/2024/13/section/246/data.xht",
            "dmcc-2024-s-248": "ukpga/2024/13/section/248/data.xht",
            "consumer-rights-act-2015-s-062": "ukpga/2015/15/section/62/data.xht",
            "consumer-rights-act-2015-s-064": "ukpga/2015/15/section/64/data.xht",
            "consumer-rights-act-2015-s-068": "ukpga/2015/15/section/68/data.xht",
            "consumer-rights-act-2015-sch-002": "ukpga/2015/15/schedule/2/data.xht",
            "consumer-contracts-regs-2013-reg-009": "uksi/2013/3134/regulation/9/data.xht",
            "consumer-contracts-regs-2013-reg-010": "uksi/2013/3134/regulation/10/data.xht",
            "consumer-contracts-regs-2013-reg-013": "uksi/2013/3134/regulation/13/data.xht",
            "consumer-contracts-regs-2013-reg-019": "uksi/2013/3134/regulation/19/data.xht",
            "consumer-contracts-regs-2013-sch-001": "uksi/2013/3134/schedule/1/data.xht",
            "consumer-contracts-regs-2013-sch-002": "uksi/2013/3134/schedule/2/data.xht",
            "ecommerce-regs-2002-reg-006": "uksi/2002/2013/regulation/6/data.xht",
            "ecommerce-regs-2002-reg-017": "uksi/2002/2013/regulation/17/data.xht",
            "ecommerce-regs-2002-reg-018": "uksi/2002/2013/regulation/18/data.xht",
            "ecommerce-regs-2002-reg-019": "uksi/2002/2013/regulation/19/data.xht",
        }

        for source_id, path in expected_paths.items():
            with self.subTest(source_id=source_id):
                self.assertTrue(self.sources[source_id]["source_uri"].endswith(path))

    def test_consumer_law_sources_carry_controlling_text(self):
        expected = {
            "dmcc-2024-s-226": (
                "(1) For the purposes of this Chapter, a commercial practice involves a "
                "misleading action if the practice involves—"
            ),
            "dmcc-2024-s-227": (
                "(2) In subsection (1)(a), “material information” means information that "
                "the average consumer needs to take an informed transactional decision."
            ),
            "dmcc-2024-s-230": "(b) the total price of the product",
            "dmcc-2024-s-245": "means any decision made by a consumer relating to",
            "dmcc-2024-s-246": "average consumer",
            "consumer-rights-act-2015-s-062": (
                "(4) A term is unfair if, contrary to the requirement of good faith"
            ),
            "consumer-rights-act-2015-s-068": (
                "(1) A trader must ensure that a written term of a consumer contract, or a "
                "consumer notice in writing, is transparent."
            ),
            "consumer-contracts-regs-2013-reg-013": (
                "must give or make available to the consumer the information listed in "
                "Schedule 2"
            ),
            "ecommerce-regs-2002-reg-006": (
                "shall make available to the recipient of the service"
            ),
            "ecommerce-regs-2002-reg-019": "actual knowledge of unlawful activity",
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

    def test_interpretation_subsections_keep_their_defined_terms(self):
        """A `LegTabbedDef` definition list rendered as nothing before the
        transformer fix, so DMCC 2024 s. 225(3) and MLR 2017 reg. 3(1) each
        published an empty interpretation subsection. Guard the real corpus."""
        cases = {
            "dmcc-2024-s-225": [
                "“commercial practice” means an act or omission by a trader",
                "“consumer” means an individual acting for purposes",
                "“trader” means—",
            ],
            "mlr-2017-reg-003": [
                "“Annex 1 financial institution” has the meaning given by regulation 55(2);"
            ],
        }

        for source_id, provisions in cases.items():
            source = self.sources[source_id]
            _fields, body = parse(
                (CORPUS / source["target"]).read_text(encoding="utf-8")
            )
            for provision in provisions:
                with self.subTest(source_id=source_id, provision=provision):
                    self.assertIn(provision, body)


if __name__ == "__main__":
    unittest.main()
