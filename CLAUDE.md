# Project instructions — compliance-references

## Merge gate: Mira

This repo requires the `mira-confidence` check before merge. The check passes
when every Mira finding on the pull request is answered (since 8 October
2026). It is an exception to the global rule. The global rule treats hosted reviewers as a
bonus, never a gate.

The gate works like this:

- `viacara-mira[bot]` posts a PR walkthrough comment, then one inline review
  comment per finding.
- `viacara-mira` cannot post a GitHub check. Its app permissions do not
  include `checks` or `statuses`.
- `.github/workflows/mira-gate.yml` reads the walkthrough and the review
  threads instead. It creates a `mira-confidence` check on the PR's head
  commit.
- A finding is answered when a maintainer (write, maintain or admin) replies
  `fixed in <sha>` or `@viacara-mira reject <reason>`, or when Mira resolves
  the thread itself. Each reply re-runs the check.
- The walkthrough's `Confidence: n/5` score is information only. Since 7
  October 2026 Mira scores statute mirrors 4/5 because it cannot check legal
  text against the live source, so a score rule blocked every PR.
- Branch protection on `main` requires the `mira-confidence` check.
- A new push resets the check to neutral. Merge stays blocked until Mira
  reviews the new commit.

Keep this note in sync with branch protection. Update both together.

## Known gap: the PR that changes the gate itself

GitHub runs an `issue_comment`-triggered workflow from the copy on the default
branch, but a `pull_request` or `pull_request_review_comment` run uses the
copy on the PR branch. This is a GitHub platform rule, not a bug here.

The decision step always checks out `.github/scripts/mira_gate.py` from the
default branch. A PR that edits only that script is graded by the old copy.
A PR that edits `mira-gate.yml` itself can change what its own review-comment
runs do, so its `mira-confidence` result proves nothing.

To merge a PR that edits `mira-gate.yml` or `mira_gate.py`, read the diff and
Mira's comments by eye. Do not rely on `mira-confidence` for it. Every other
PR is not affected.
