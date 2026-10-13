"""Mira gate decision tests."""

import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "mira_gate", Path(__file__).resolve().parents[1] / ".github" / "scripts" / "mira_gate.py"
)
mira_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mira_gate)

HEAD_SEEN = "2026-10-08T15:00:00Z"


def walkthrough(updated_at="2026-10-08T15:05:00Z", stats="2 files reviewed", score="4"):
    body = f"<!-- mira-walkthrough -->\nConfidence: {score}/5\n*{stats}*"
    return {"user": {"login": "viacara-mira[bot]"}, "body": body, "created_at": updated_at, "updated_at": updated_at}


def thread(*replies, resolved_by=None):
    nodes = [{"author": {"login": "viacara-mira"}, "body": "**Bug**", "url": "https://example.test/f"}]
    nodes += [{"author": {"login": login}, "body": body, "url": "u"} for login, body in replies]
    return {
        "isResolved": resolved_by is not None,
        "resolvedBy": {"login": resolved_by} if resolved_by else None,
        "path": "manifest.json",
        "line": 3,
        "comments": {"nodes": nodes},
    }


class MiraGateTests(unittest.TestCase):
    def decide(self, walkthroughs, threads=(), posted=0, permissions=None, head_seen_at=HEAD_SEEN):
        return mira_gate.decide(list(walkthroughs), head_seen_at, posted, list(threads), permissions or {})

    def test_no_walkthrough_leaves_the_check(self):
        self.assertIsNone(self.decide([]))

    def test_walkthrough_older_than_the_head_waits(self):
        verdict = self.decide([walkthrough(updated_at="2026-10-08T14:59:00Z")])
        self.assertEqual(("neutral", "Waiting for Mira review"), (verdict.conclusion, verdict.title))

    def test_head_never_seen_waits(self):
        verdict = self.decide([walkthrough()], head_seen_at=None)
        self.assertEqual("neutral", verdict.conclusion)

    def test_unfinished_walkthrough_waits(self):
        verdict = self.decide([walkthrough(stats="")])
        self.assertEqual("Mira review in progress", verdict.title)

    def test_waits_until_every_counted_finding_is_posted(self):
        verdict = self.decide([walkthrough(stats="2 files reviewed · 2 comments")], posted=1)
        self.assertEqual(("neutral", "Waiting for Mira findings"), (verdict.conclusion, verdict.title))

    def test_no_findings_passes_whatever_the_score(self):
        verdict = self.decide([walkthrough(score="4")])
        self.assertEqual("success", verdict.conclusion)
        self.assertIn("4/5 (information only)", verdict.summary)

    def test_unanswered_finding_fails(self):
        verdict = self.decide(
            [walkthrough(stats="2 files reviewed · 1 comment")], [thread()], posted=1
        )
        self.assertEqual("failure", verdict.conclusion)
        self.assertIn("manifest.json:3 https://example.test/f", verdict.summary)

    def test_maintainer_fixed_reply_answers(self):
        verdict = self.decide(
            [walkthrough()], [thread(("kylewelsby", "fixed in abcdef1"))], permissions={"kylewelsby": "admin"}
        )
        self.assertEqual("success", verdict.conclusion)

    def test_maintainer_reject_reply_answers(self):
        verdict = self.decide(
            [walkthrough()],
            [thread(("kylewelsby", "@viacara-mira reject not a defect"))],
            permissions={"kylewelsby": "write"},
        )
        self.assertEqual("success", verdict.conclusion)

    def test_reply_without_write_permission_does_not_answer(self):
        verdict = self.decide(
            [walkthrough()], [thread(("someone", "fixed in abcdef1"))], permissions={"someone": "read"}
        )
        self.assertEqual("failure", verdict.conclusion)

    def test_reply_in_another_form_does_not_answer(self):
        verdict = self.decide(
            [walkthrough()], [thread(("kylewelsby", "Thanks, will fix"))], permissions={"kylewelsby": "admin"}
        )
        self.assertEqual("failure", verdict.conclusion)

    def test_thread_mira_resolved_is_answered(self):
        verdict = self.decide([walkthrough()], [thread(resolved_by="viacara-mira[bot]")])
        self.assertEqual("success", verdict.conclusion)

    def test_thread_resolved_by_someone_else_still_needs_an_answer(self):
        verdict = self.decide([walkthrough()], [thread(resolved_by="kylewelsby")])
        self.assertEqual("failure", verdict.conclusion)

    def test_only_the_latest_walkthrough_counts(self):
        stale = walkthrough(updated_at="2026-10-08T14:00:00Z")
        stale["created_at"] = "2026-10-08T14:00:00Z"
        fresh = walkthrough(updated_at="2026-10-08T15:10:00Z")
        fresh["created_at"] = "2026-10-08T14:30:00Z"
        self.assertEqual("success", self.decide([fresh, stale]).conclusion)

    def test_reply_authors_lists_only_answer_shaped_replies_to_mira(self):
        threads = [thread(("kylewelsby", "fixed in abcdef1"), ("other", "looks fine"))]
        self.assertEqual({"kylewelsby"}, mira_gate.reply_authors(threads))


if __name__ == "__main__":
    unittest.main()
