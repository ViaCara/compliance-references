"""Decide the `mira-confidence` check for one pull request.

The check passes when Mira has reviewed the current head and every Mira
finding is answered: a maintainer replied `fixed in <sha>` or
`@viacara-mira reject <reason>`, or Mira resolved the thread itself. The
walkthrough's `Confidence: n/5` score is information only.

When the check passes, the script squash-merges the pull request and starts
tag-release, unless `merge_blocker` names a reason to leave it for a human.

Usage: python3 .github/scripts/mira_gate.py <owner/repo> <pr-number>
Reads GitHub through `gh api`, writes the check run and merges.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from typing import NamedTuple

CHECK_NAME = "mira-confidence"
MIRA = "viacara-mira"
MARKER = "mira-walkthrough"
CONFIDENCE = re.compile(r"Confidence:\s*([0-5])/5", re.IGNORECASE)
STATS = re.compile(r"(\d+) files? reviewed[^*\n]*", re.IGNORECASE)
COMMENT_COUNT = re.compile(r"(\d+) comments?", re.IGNORECASE)
FIXED = re.compile(r"\Afixed in [0-9a-f]{7,40}\b", re.IGNORECASE)
REJECT = re.compile(r"\A@viacara-mira reject\s+\S", re.IGNORECASE)
MAINTAINER = {"write", "maintain", "admin"}
HOLD = "do-not-merge"

THREADS_QUERY = """query($owner:String!,$repo:String!,$pr:Int!,$cursor:String){
  repository(owner:$owner,name:$repo){pullRequest(number:$pr){
    reviewThreads(first:100,after:$cursor){pageInfo{hasNextPage endCursor}
      nodes{isResolved resolvedBy{login} path line
        comments(first:100){nodes{author{login} body url}}}}}}}"""


class Verdict(NamedTuple):
    conclusion: str
    title: str
    summary: str


def bare(login: str | None) -> str:
    return re.sub(r"\[bot\]$", "", login or "")


def parse_time(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def is_reply(body: str) -> bool:
    body = body.strip()
    return bool(FIXED.search(body) or REJECT.search(body))


def reply_authors(threads: list[dict]) -> set[str]:
    """Logins whose permission decides whether a thread is answered."""
    authors = set()
    for thread in threads:
        root, *replies = thread["comments"]["nodes"] or [{}]
        if bare((root.get("author") or {}).get("login")) != MIRA:
            continue
        for reply in replies:
            login = (reply.get("author") or {}).get("login")
            if login and bare(login) != MIRA and is_reply(reply.get("body", "")):
                authors.add(login)
    return authors


def open_findings(threads: list[dict], permissions: dict[str, str]) -> list[str]:
    found = []
    for thread in threads:
        root, *replies = thread["comments"]["nodes"] or [{}]
        if bare((root.get("author") or {}).get("login")) != MIRA:
            continue
        if thread.get("isResolved") and bare((thread.get("resolvedBy") or {}).get("login")) == MIRA:
            continue
        answered = any(
            bare((reply.get("author") or {}).get("login")) != MIRA
            and permissions.get((reply.get("author") or {}).get("login", "")) in MAINTAINER
            and is_reply(reply.get("body", ""))
            for reply in replies
        )
        if not answered:
            found.append(f"- {thread.get('path')}:{thread.get('line') or '?'} {root.get('url', '')}")
    return found


def decide(
    walkthroughs: list[dict],
    head_seen_at: str | None,
    posted_findings: int,
    threads: list[dict],
    permissions: dict[str, str],
) -> Verdict | None:
    """Return the check verdict, or None when there is no walkthrough yet.

    `head_seen_at` is when GitHub first ran this check for the head commit,
    which happens on the push. It is server time, so a backdated commit
    cannot make an older walkthrough look like a review of a newer head.
    """
    waiting = Verdict("neutral", "Waiting for Mira review", "Mira has not reviewed this commit yet.")
    mine = sorted(
        (c for c in walkthroughs if bare(c["user"]["login"]) == MIRA and MARKER in (c.get("body") or "")),
        key=lambda c: c["created_at"],
    )
    if not mine:
        return None
    latest = mine[-1]
    if head_seen_at is None or parse_time(latest["updated_at"]) <= parse_time(head_seen_at):
        return waiting

    score = CONFIDENCE.search(latest["body"])
    stats = STATS.search(latest["body"])
    if not score or not stats:
        return Verdict("neutral", "Mira review in progress", "The walkthrough is not finished yet.")

    count = COMMENT_COUNT.search(stats.group(0))
    expected = int(count.group(1)) if count else 0
    if posted_findings < expected:
        return Verdict(
            "neutral",
            "Waiting for Mira findings",
            f"Mira has posted {posted_findings} of {expected} findings for this commit.",
        )

    note = f"Walkthrough score: {score.group(1)}/5 (information only)."
    found = open_findings(threads, permissions)
    if found:
        return Verdict(
            "failure",
            f"{len(found)} Mira finding(s) unanswered",
            "A maintainer must reply `fixed in <sha>` or `@viacara-mira reject <reason>` "
            "on each finding. A reply re-runs this check.\n\n" + "\n".join(found) + f"\n\n{note}",
        )
    return Verdict(
        "success",
        "Every Mira finding answered",
        f"Mira reviewed this commit ({stats.group(0).strip()}) and every finding is fixed or refuted. {note}",
    )


def gh(*arguments: str) -> object:
    result = subprocess.run(["gh", "api", *arguments], check=True, capture_output=True, text=True, timeout=60)
    return json.loads(result.stdout)


def gh_pages(path: str) -> list[dict]:
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", path], check=True, capture_output=True, text=True, timeout=120
    )
    return [item for page in json.loads(result.stdout) for item in page]


def fetch_threads(repository: str, number: int) -> list[dict]:
    owner, name = repository.split("/")
    threads, cursor = [], None
    while True:
        arguments = ["graphql", "-f", f"query={THREADS_QUERY}", "-f", f"owner={owner}", "-f", f"repo={name}", "-F", f"pr={number}"]
        if cursor:
            arguments += ["-f", f"cursor={cursor}"]
        payload = gh(*arguments)
        if payload.get("errors"):
            raise ValueError(f"GraphQL errors: {payload['errors']}")
        connection = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        threads.extend(connection["nodes"])
        if not connection["pageInfo"]["hasNextPage"]:
            return threads
        cursor = connection["pageInfo"]["endCursor"]


def changed_paths(files: list[dict]) -> list[str]:
    """Both names of every file, so a move out of .github/ still counts."""
    return [path for f in files for path in (f["filename"], f.get("previous_filename")) if path]


def merge_blocker(pull: dict, paths: list[str], listed_files: int) -> str | None:
    """Return why a passing pull request must wait for a human, or None to merge it."""
    if pull["state"] != "open":
        return "the pull request is not open"
    if pull["draft"]:
        return "the pull request is a draft"
    if any(label["name"].lower() == HOLD for label in pull["labels"]):
        return f"the pull request carries {HOLD}"
    if (pull["head"]["repo"] or {}).get("full_name") != pull["base"]["repo"]["full_name"]:
        return "the pull request comes from a fork"
    if pull["base"]["ref"] != pull["base"]["repo"]["default_branch"]:
        return "the pull request does not target the default branch"
    if pull["changed_files"] > listed_files:
        return "GitHub listed only part of the changed files"
    if any(path.startswith(".github/") for path in paths):
        return "the pull request changes .github/, which the gate cannot grade"
    return None


def merge(repository: str, number: int, graded_sha: str) -> None:
    files = gh_pages(f"repos/{repository}/pulls/{number}/files?per_page=100")
    pull = gh(f"repos/{repository}/pulls/{number}")
    if pull["head"]["sha"] != graded_sha:
        print(f"Not merging #{number}: the head moved after the check.")
        return
    blocker = merge_blocker(pull, changed_paths(files), len(files))
    if blocker:
        print(f"Not merging #{number}: {blocker}.")
        return
    try:
        gh("-X", "PUT", f"repos/{repository}/pulls/{number}/merge", "-f", "merge_method=squash", "-f", f"sha={graded_sha}")
    except subprocess.CalledProcessError as error:
        reason = (error.stderr or error.stdout or "").strip()
        print(f"::error::GitHub refused the merge of #{number}: {reason}")
        if "HTTP 409" in reason:
            return
        raise
    print(f"Merged #{number}.")
    try:
        subprocess.run(["gh", "workflow", "run", "tag-release.yml", "--repo", repository], check=True, timeout=60)
    except subprocess.CalledProcessError:
        print(f"::error::#{number} is merged, but tag-release did not start. Run it by hand.")
        raise


def main(repository: str, number: int) -> int:
    sha = gh(f"repos/{repository}/pulls/{number}")["head"]["sha"]
    walkthroughs = gh_pages(f"repos/{repository}/issues/{number}/comments?per_page=100")
    runs = gh(f"repos/{repository}/commits/{sha}/check-runs?check_name={CHECK_NAME}&filter=all&per_page=100")["check_runs"]
    head_seen_at = min((run["started_at"] for run in runs), default=None)
    inline = gh_pages(f"repos/{repository}/pulls/{number}/comments?per_page=100")
    posted = sum(
        1 for c in inline if bare(c["user"]["login"]) == MIRA and not c.get("in_reply_to_id") and c["commit_id"] == sha
    )
    threads = fetch_threads(repository, number)
    permissions = {
        login: gh(f"repos/{repository}/collaborators/{login}/permission")["permission"]
        for login in reply_authors(threads)
    }
    verdict = decide(walkthroughs, head_seen_at, posted, threads, permissions)
    if verdict is None:
        print("No Mira walkthrough yet; leaving the check unchanged.")
        return 0
    gh(
        "-X", "POST", f"repos/{repository}/check-runs",
        "-f", f"name={CHECK_NAME}", "-f", f"head_sha={sha}", "-f", "status=completed",
        "-f", f"conclusion={verdict.conclusion}",
        "-f", f"output[title]={verdict.title}", "-f", f"output[summary]={verdict.summary}",
    )
    print(f"{CHECK_NAME}: {verdict.conclusion} ({verdict.title}) on {sha}")
    if verdict.conclusion == "success":
        merge(repository, number, sha)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(sys.argv[2])))
