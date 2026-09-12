"""Medical device qualification source coverage.

Whether a software feature gives a product a medical purpose turns on the
Great Britain definition of "medical device" and on the purpose the
manufacturer states. The corpus previously held no medical devices material,
so a patient-specific suggestion feature had no controlling clause to cite.
These tests pin the statutory definition, the "intended purpose"
definition that ties qualification to the manufacturer's own labelling,
instructions and promotional materials, and the two MHRA guidance documents
that apply it to software and to digital mental health technology. They
also pin the two sources that decide whether in-product copy is advertising
and whom it must not mislead: the CAP Code's own scope and the DMCC 2024
vulnerable-consumer benchmark."""

import json
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"


class MedicalDeviceSourceTests(unittest.TestCase):
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

    def test_regulation_2_carries_the_medical_device_definition(self):
        source = self.sources["mdr-2002-reg-002"]
        self.assertTrue(source["source_uri"].endswith("uksi/2002/618/regulation/2/data.xht"))

        fields, body = self._read("mdr-2002-reg-002")

        self.assertEqual("in_force", fields["enforcement_status"])
        self.assertIn("“medical device” means any instrument, apparatus, appliance, software", body)
        self.assertIn("diagnosis, prevention, monitoring, treatment or alleviation of disease", body)

    def test_regulation_2_labels_the_great_britain_and_northern_ireland_versions(self):
        _fields, body = self._read("mdr-2002-reg-002")

        great_britain = body.index("**Extent:** England, Wales and Scotland")
        northern_ireland = body.index("**Extent:** Northern Ireland")
        definition = body.index("“medical device” means any instrument")

        self.assertEqual(1, body.count("**Extent:** England, Wales and Scotland"))
        self.assertEqual(1, body.count("**Extent:** Northern Ireland"))
        self.assertLess(great_britain, definition)
        self.assertLess(definition, northern_ireland)

    def test_regulation_2_ties_intended_purpose_to_promotional_materials(self):
        _fields, body = self._read("mdr-2002-reg-002")

        self.assertIn(
            "the use to which the device is intended according to the data supplied by the "
            "manufacturer on the labelling, the instructions for use and/or the promotional materials",
            body,
        )

    def test_mhra_software_guidance_draws_the_decision_support_line(self):
        fields, body = self._read("mhra-standalone-software-apps")

        self.assertEqual("guidance", fields["enforcement_status"])
        self.assertIn("options may be explained but the health care\n> professional decides which path to take", body)
        self.assertIn("Software that provides treatment recommendations for listed conditions", body)

    def test_mhra_mental_health_guidance_names_recommending_therapeutic_options(self):
        fields, body = self._read("mhra-dmht-qualification-classification")

        self.assertEqual("guidance", fields["enforcement_status"])
        self.assertIn("Recommends therapeutic options, clinical decision support", body)
        self.assertIn("Processes data / information using AI", body)

    def test_dmcc_section_247_names_mental_health_vulnerability(self):
        source = self.sources["dmcc-2024-s-247"]
        self.assertTrue(source["source_uri"].endswith("ukpga/2024/13/section/247/data.xht"))

        fields, body = self._read("dmcc-2024-s-247")

        self.assertEqual("in_force", fields["enforcement_status"])
        self.assertIn(
            "a group of consumers is particularly vulnerable to a commercial practice in a way "
            "that the trader could reasonably be expected to foresee",
            body,
        )
        self.assertIn("are to be read as references to an average member of the group", body)
        self.assertIn("(b) their physical or mental health;", body)

    def test_cap_code_scope_covers_own_website_marketing_and_excludes_editorial(self):
        source = self.sources["cap-code-scope"]
        self.assertEqual("curated_quotes", source["kind"])

        fields, body = self._read("cap-code-scope")

        self.assertEqual("guidance", fields["enforcement_status"])
        self.assertIn("companies, organisations or sole traders on their own websites, or in\n> other non-paid-for space online under their control", body)
        self.assertIn("correspondence between\n> organisations and their customers about existing relationships", body)
        self.assertIn("> k. editorial content", body)


if __name__ == "__main__":
    unittest.main()
