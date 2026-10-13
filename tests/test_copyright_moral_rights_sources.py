"""Copyright and moral rights sources: CDPA 1988 ss. 16, 77, 78, 80, 87,
90 and 296ZG."""

import json
import re
import unittest
from pathlib import Path

from lib.frontmatter import parse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CORPUS = ROOT / "corpus"
BASE_URI = "https://www.legislation.gov.uk/"

SUBSECTIONS = {
    "cdpa-1988-s-016": 4,
    "cdpa-1988-s-077": 9,
    "cdpa-1988-s-078": 5,
    "cdpa-1988-s-080": 8,
    "cdpa-1988-s-087": 4,
    "cdpa-1988-s-090": 4,
    "cdpa-1988-s-296zg": 9,
}

STATUTE = {
    "cdpa-1988-s-016": (
        "ukpga/1988/48/section/16/data.xht",
        (
            "the exclusive right to do the following acts in the United Kingdom",
            "(a) to copy the work (see section 17);",
            "(d) to communicate the work to the public (see section 20);",
            "(e) to make an adaptation of the work or do any of the above in relation to an adaptation",
            "Copyright in a work is infringed by a person who without the licence of the copyright owner does, "
            "or authorises another to do, any of the acts restricted by the copyright.",
            "in relation to the work as a whole or any substantial part of it",
        ),
    ),
    "cdpa-1988-s-077": (
        "ukpga/1988/48/section/77/data.xht",
        (
            "has the right to be identified as the author or director of the work",
            "the right is not infringed unless it has been asserted in accordance with section 78",
            "the work is published commercially or exhibited in public, or a visual image of it is communicated to the public",
            "the identification must in each case be clear and reasonably prominent",
            "If the author or director in asserting his right to be identified specifies a pseudonym",
        ),
    ),
    "cdpa-1988-s-078": (
        "ukpga/1988/48/section/78/data.xht",
        (
            "unless the right has been asserted in accordance with the following provisions",
            "by instrument in writing signed by the author or director",
            "anyone to whose notice the assertion is brought",
            "take into account any delay in asserting the right",
        ),
    ),
    "cdpa-1988-s-080": (
        "ukpga/1988/48/section/80/data.xht",
        (
            "not to have his work subjected to derogatory treatment",
            "any addition to, deletion from or alteration to or adaptation of the work",
            "if it amounts to distortion or mutilation of the work or is otherwise prejudicial to the honour "
            "or reputation of the author or director",
            "publishes commercially or exhibits in public a derogatory treatment of the work",
        ),
    ),
    "cdpa-1988-s-087": (
        "ukpga/1988/48/section/87/data.xht",
        (
            "to do any act to which the person entitled to the right has consented",
            "may be waived by instrument in writing signed by the person giving up the right",
            "may relate to existing or future works",
            "may be conditional or unconditional and may be expressed to be subject to revocation",
            "presumed to extend to his licensees and successors in title",
            "the general law of contract or estoppel in relation to an informal waiver",
        ),
    ),
    "cdpa-1988-s-090": (
        "ukpga/1988/48/section/90/data.xht",
        (
            "Copyright is transmissible by assignment",
            "to one or more, but not all, of the things the copyright owner has the exclusive right to do",
            "An assignment of copyright is not effective unless it is in writing signed by or on behalf of the assignor.",
            "A licence granted by a copyright owner is binding on every successor in title",
            "except a purchaser in good faith for valuable consideration and without notice",
        ),
    ),
    "cdpa-1988-s-296zg": (
        "ukpga/1988/48/section/296ZG/data.xht",
        (
            "knowingly and without authority, removes or alters electronic rights management information",
            "is inducing, enabling, facilitating or concealing an infringement of copyright",
            "distributes, imports for distribution or communicates to the public copies of a copyright work",
            "has the same rights against D and E as a copyright owner has in respect of an infringement of copyright",
            "which identifies the work, the author, the copyright owner or the holder of any intellectual property rights",
            "information about the terms and conditions of use of the work",
        ),
    ),
}


class CopyrightMoralRightsSourceTests(unittest.TestCase):
    def setUp(self):
        self.sources = {
            source["id"]: source
            for source in json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
        }

    def test_manifest_carries_statute_sources(self):
        for source_id, (path, _) in STATUTE.items():
            with self.subTest(source_id=source_id):
                source = self.sources[source_id]
                self.assertEqual(BASE_URI + path, source["source_uri"])
                self.assertEqual("cdpa-1988", source["instrument"])
                self.assertEqual("legislation_section", source["kind"])

    def test_statute_files_carry_source_identity(self):
        for source_id, (path, _) in STATUTE.items():
            source = self.sources[source_id]
            fields, _ = parse((CORPUS / source["target"]).read_text(encoding="utf-8"))
            with self.subTest(source_id=source_id):
                self.assertEqual(source_id, fields["id"])
                self.assertEqual(BASE_URI + path, fields["source_uri"])
                self.assertEqual("cdpa-1988", fields["instrument"])
                self.assertEqual("legislation_section", fields["kind"])
                self.assertEqual(source["citation"], fields["citation"])
                self.assertEqual("in_force", fields["enforcement_status"])

    def test_statute_files_keep_each_subsection_as_its_own_paragraph(self):
        for source_id, count in SUBSECTIONS.items():
            _, body = parse((CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8"))
            for number in range(1, count + 1):
                with self.subTest(source_id=source_id, subsection=number):
                    self.assertRegex(body, rf"(?m)^\({number}\) \S")

    def test_statute_files_carry_controlling_text(self):
        for source_id, (_, passages) in STATUTE.items():
            _, body = parse((CORPUS / self.sources[source_id]["target"]).read_text(encoding="utf-8"))
            paragraphs = [re.sub(r"\s+", " ", p) for p in re.split(r"\n\s*\n", body)]
            for passage in passages:
                with self.subTest(source_id=source_id, passage=passage):
                    self.assertTrue(
                        any(passage in paragraph for paragraph in paragraphs),
                        f"{passage!r} is not within one paragraph",
                    )


if __name__ == "__main__":
    unittest.main()
