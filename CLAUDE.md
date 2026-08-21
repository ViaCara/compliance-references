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
