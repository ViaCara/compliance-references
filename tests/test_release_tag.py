"""Release tag naming tests."""

import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "release_tag", Path(__file__).resolve().parents[1] / ".github" / "scripts" / "release_tag.py"
)
release_tag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_tag)

DATE = "2026.11.18"


class NextTagTests(unittest.TestCase):
    def test_first_release_of_the_day_uses_the_date(self):
        self.assertEqual(release_tag.next_tag(DATE, ["v2026.11.11"], []), "v2026.11.18")

    def test_second_release_of_the_day_adds_a_counter(self):
        self.assertEqual(release_tag.next_tag(DATE, ["v2026.11.18"], []), "v2026.11.18.1")

    def test_counter_takes_the_first_free_number(self):
        existing = ["v2026.11.18", "v2026.11.18.1", "v2026.11.18.2"]
        self.assertEqual(release_tag.next_tag(DATE, existing, []), "v2026.11.18.3")

    def test_commit_with_a_release_tag_gets_no_second_tag(self):
        self.assertIsNone(release_tag.next_tag(DATE, ["v2026.11.11.1"], ["v2026.11.11.1"]))

    def test_commit_with_a_major_prefix_tag_gets_no_date_tag(self):
        self.assertIsNone(release_tag.next_tag(DATE, ["v2.0.0-2026.11.18"], ["v2.0.0-2026.11.18"]))

    def test_other_tag_on_the_commit_does_not_stop_the_release(self):
        self.assertEqual(release_tag.next_tag(DATE, ["sync-base"], ["sync-base"]), "v2026.11.18")


if __name__ == "__main__":
    unittest.main()
