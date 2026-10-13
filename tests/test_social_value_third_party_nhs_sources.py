"""Social Value Act 2012 s. 1, Contracts (Rights of Third Parties) Act 1999 ss. 1 and 2,
NHS England conflicts of interest guidance and the NHS Talking Therapies manual."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import body_sha256, parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"

STATUTE = {
    "psva-2012-s-001": (
        "https://www.legislation.gov.uk/ukpga/2012/3/section/1/data.xht",
        "statute/uk/psva-2012/section-001.md",
        (
            "it must comply with the requirements in subsections (3), (6) and (7) before starting the process of procurement.",
            "(a) how what is proposed to be procured might improve the economic, social and environmental well-being of the relevant area, and",
            "(b) how, in conducting the process of procurement, it might act with a view to securing that improvement.",
            "must consider the extent to which it is proportionate in all the circumstances to take those matters into account.",
            "(7) The authority must consider whether to undertake any consultation as to the matters that fall to be considered under subsection (3).",
            "“relevant authority” means a person or body that is a contracting authority within the meaning of the Procurement Act 2023",
        ),
    ),
    "crtpa-1999-s-001": (
        "https://www.legislation.gov.uk/ukpga/1999/31/section/1/data.xht",
        "statute/uk/crtpa-1999/section-001.md",
        (
            "a person who is not a party to a contract (a “third party”) may in his own right enforce a term of the contract if—",
            "(a) the contract expressly provides that he may, or",
            "(b) subject to subsection (2), the term purports to confer a benefit on him.",
            "it appears that the parties did not intend the term to be enforceable by the third party.",
            "(3) The third party must be expressly identified in the contract by name, as a member of a class or as answering a particular description",
            "otherwise than subject to and in accordance with any other relevant terms of the contract.",
        ),
    ),
    "crtpa-1999-s-002": (
        "https://www.legislation.gov.uk/ukpga/1999/31/section/2/data.xht",
        "statute/uk/crtpa-1999/section-002.md",
        (
            "may not, by agreement, rescind the contract, or vary it in such a way as to extinguish or alter his entitlement under that right, without his consent if—",
            "(a) the third party has communicated his assent to the term to the promisor,",
            "(b) the promisor is aware that the third party has relied on the term, or",
            "(a) the parties to the contract may by agreement rescind or vary the contract without the consent of the third party, or",
            "including a condition requiring the payment of compensation to the third party.",
        ),
    ),
}

GUIDANCE = {
    "nhs-england-managing-conflicts-of-interest": (
        "guidance/uk/nhs-england/managing-conflicts-of-interest.md",
        (
            "integrated care boards (ICBs)",
            "must have regard to this guidance through its incorporation into the NHS Standard Contract pursuant to general condition 27.",
            "This guidance does not apply to bodies not listed above (ie independent and private sector organisations, general practices,",
            "seek prior approval of their organisation before taking up private practice",
            "not accept direct or indirect financial incentives from private providers",
            "Hospital consultants should not initiate discussions about providing their private professional services for NHS patients, "
            "nor should they ask other staff to initiate such discussions on their behalf",
        ),
    ),
    "nhs-talking-therapies-manual": (
        "guidance/uk/nhs-england/talking-therapies-manual.md",
        (
            "Individuals who do not fully recover at this level should be stepped up to a course of high-intensity treatment.",
            "in which case patients are signposted to the relevant service.",
            "Developing a relapse prevention plan with patients before they are discharged.",
            "Patients should not be discharged during a course of treatment purely based on changes in geographical location",
            "Local discharge and onward referral policies need to be developed to support people as they recover.",
            "Copyright National Collaborating Centre for Mental Health, 2024",
        ),
    ),
}


def _flat(body):
    return re.sub(r"\s+", " ", re.sub(r"^> ?(\* )?", "", body, flags=re.M))


class SocialValueThirdPartyNhsSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_statute_sources_pin_their_operative_text(self):
        for source_id, (uri, target, phrases) in STATUTE.items():
            source = self.sources[source_id]
            fields, body = parse((CORPUS / target).read_text(encoding="utf-8"))
            with self.subTest(source_id=source_id):
                self.assertEqual(uri, source["source_uri"])
                self.assertEqual(target, source["target"])
                self.assertEqual(source_id, fields["id"])
                self.assertEqual(uri, fields["source_uri"])
                self.assertEqual("in_force", fields["enforcement_status"])
            for phrase in phrases:
                with self.subTest(source_id=source_id, phrase=phrase):
                    self.assertIn(phrase, body)

    def test_curated_guidance_carries_the_quoted_rules(self):
        for source_id, (target, phrases) in GUIDANCE.items():
            source = self.sources[source_id]
            fields, body = parse((CORPUS / target).read_text(encoding="utf-8"))
            with self.subTest(source_id=source_id):
                self.assertEqual(target, source["target"])
                self.assertEqual("curated_quotes", source["kind"])
                self.assertEqual("nhs-england-guidance", source["instrument"])
                self.assertEqual(source["source_uri"], fields["source_uri"])
                self.assertEqual(body_sha256(body), fields["content_sha256"])
            text = _flat(body)
            for phrase in phrases:
                with self.subTest(source_id=source_id, phrase=phrase):
                    self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
