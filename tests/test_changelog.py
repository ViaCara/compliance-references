"""CHANGELOG append tests."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.changelog import Changelog, Entry


class ChangelogTests(unittest.TestCase):
    def test_append_creates_file_when_missing(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "CHANGELOG.md"
            log = Changelog(path)
            log.append(
                Entry(
                    date="2026-05-15",
                    target="statute/uk/gdpr/article-009.md",
                    source_uri="https://www.legislation.gov.uk/eur/2016/679/article/9",
                    prior_sha256="3a4f0000",
                    new_sha256="c0b10001",
                    summary="12 lines added, 3 removed",
                    revision="2026-04-01",
                )
            )
            text = path.read_text(encoding="utf-8")

            self.assertIn("## 2026-05-15", text)
            self.assertIn("article-009.md", text)
            self.assertIn("c0b10001", text)
            self.assertIn("12 lines added, 3 removed", text)

    def test_append_prepends_under_same_date_heading(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "CHANGELOG.md"
            log = Changelog(path)
            log.append(
                Entry(
                    date="2026-05-15",
                    target="a.md",
                    source_uri="https://x/a",
                    prior_sha256="00",
                    new_sha256="11",
                    summary="first",
                )
            )
            log.append(
                Entry(
                    date="2026-05-15",
                    target="b.md",
                    source_uri="https://x/b",
                    prior_sha256="22",
                    new_sha256="33",
                    summary="second",
                )
            )
            text = path.read_text(encoding="utf-8")

            self.assertEqual(text.count("## 2026-05-15"), 1)
            self.assertIn("a.md", text)
            self.assertIn("b.md", text)

    def test_new_date_heading_above_old_one(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "CHANGELOG.md"
            log = Changelog(path)
            log.append(
                Entry(
                    date="2026-04-01",
                    target="a.md",
                    source_uri="https://x/a",
                    prior_sha256="0",
                    new_sha256="1",
                    summary="april",
                )
            )
            log.append(
                Entry(
                    date="2026-05-15",
                    target="b.md",
                    source_uri="https://x/b",
                    prior_sha256="2",
                    new_sha256="3",
                    summary="may",
                )
            )
            text = path.read_text(encoding="utf-8")

            self.assertLess(text.index("2026-05-15"), text.index("2026-04-01"))

    def test_renders_status_change_without_claiming_content_drift(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "CHANGELOG.md"
            log = Changelog(path)
            log.append(
                Entry(
                    date="2026-07-24",
                    target="statute/uk/gdpr/article-022.md",
                    source_uri="https://www.legislation.gov.uk/eur/2016/679/article/22/data.xht",
                    prior_sha256="same",
                    new_sha256="same",
                    summary="enforcement status in_force -> repealed",
                )
            )
            text = path.read_text(encoding="utf-8")

            self.assertIn("enforcement status in_force -> repealed", text)

            self.assertNotIn("content changed", text)


if __name__ == "__main__":
    unittest.main()
