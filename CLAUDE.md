# Project instructions — compliance-references

## Merge gate: Mira

The `mira-confidence` check merges a pull request. The check passes when
every Mira finding on the pull request is answered (since 8 October 2026),
and the gate then squash-merges it with no human step. It is an exception to the global rule. The global rule treats hosted reviewers as a
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
- When the check passes, the gate squash-merges the pull request and starts
  `tag-release`. It leaves the pull request for a human when it is a draft,
  carries `do-not-merge` (any case), comes from a fork, targets another
  branch or changes `.github/`. The reason is in the job log.
- To hold a pull request, open it as a draft or add `do-not-merge`. Releasing
  a hold starts no run: re-run the latest `mira-gate` run to merge it.
- A new push resets the check to neutral. The gate does not merge until Mira
  reviews the new commit.
- `main` has no branch protection. The gate is the only merge path that
  checks Mira; a maintainer can still merge by hand.

Keep this note in sync with `.github/scripts/mira_gate.py`. Update both
together.

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

The `.github/` hold does not bind such a PR either: its own copy of
`mira-gate.yml` runs on review comments and could merge it. Only a maintainer
with write access can open one.

## Public repository: keep the text neutral

This repository is public. Every file, commit message, branch name and pull
request describes the law, not a consumer's product.

- A summary, intro, `Application` note or test docstring states what the
  source means in law. It does not name a consumer, describe a consumer's
  feature, or say how a consumer relies on the source.
- Do not write an issue-tracker id (such as a Linear ticket number) or a link
  to a private tracker anywhere in the repository, a commit or a pull request.
- Name a test file after the sources it pins, not after the project that asked
  for them.
- A consumer keeps its own reasons for a source in its own repository.

Before you push, run:

```
git grep -nE "\b[A-Z]{2,5}-[0-9]+\b|linear\.app" -- . ':!CHANGELOG.md' ':!tests/fixtures'
```

and read each hit.
