# Project instructions — compliance-references

## Merge gate: Mira

This repo requires the `mira-confidence` check before merge. The check passes
when every Mira finding on the pull request is answered. This is the same rule
as ViaCara (VIA-1727), adopted here on 8 October 2026 (VIA-2128). It is an
exception to the global rule. The global rule treats hosted reviewers as a
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

GitHub only runs an `issue_comment`-triggered workflow from the copy on the
default branch. It ignores the copy on the PR branch. This is a GitHub
platform rule, not a bug here.

`mira-confidence` reacts to Mira's comment through `issue_comment`. A PR that
adds or edits `mira-gate.yml` cannot trigger that reaction for itself. Its own
check stays on neutral, "Waiting for Mira review", no matter what Mira posts.
The `pull_request` half still runs. It resets the check to neutral on every
push.

To merge such a PR, check Mira's comment by eye. Do not wait for
`mira-confidence` to turn green on it. Every other PR is not affected. Once
the workflow file is on `main`, `issue_comment` runs for them as normal.
