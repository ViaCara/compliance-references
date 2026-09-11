"""Medical device qualification source coverage.

Whether a software feature gives a product a medical purpose turns on the
Great Britain definition of "medical device" and on the purpose the
manufacturer states. The corpus previously held no medical devices material,
so a patient-specific suggestion feature had no controlling clause to cite.
These tests pin the statutory definition, the "intended purpose"
definition that ties qualification to the manufacturer's own labelling,
instructions and promotional materials, and the two MHRA guidance documents
that apply it to software and to digital mental health technology."""

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


if __name__ == "__main__":
    unittest.main()
