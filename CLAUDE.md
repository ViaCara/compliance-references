# Project instructions — compliance-references

## Merge gate: Mira

This repo requires a Confidence score of 5/5 from `viacara-mira` before merge.
This is an exception to the global rule. The global rule treats hosted
reviewers as a bonus, never a gate.

The gate works like this:

- `viacara-mira[bot]` posts a PR walkthrough comment. The comment carries a
  `Confidence: n/5` score.
- `viacara-mira` cannot post a GitHub check. Its app permissions do not
  include `checks` or `statuses`.
- `.github/workflows/mira-gate.yml` reads the comment instead. It creates a
  `mira-confidence` check on the PR's head commit.
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
