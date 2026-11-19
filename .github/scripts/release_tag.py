"""Name the release tag for the current commit.

The first release of a day is `v<YYYY.MM.DD>`. Each later release on the same
day adds a counter: `v<YYYY.MM.DD>.1`, `v<YYYY.MM.DD>.2`. A commit that
already carries a release tag gets no second tag.

Usage: python3 .github/scripts/release_tag.py
Prints the tag to create, or nothing when the commit is already tagged.
"""

from __future__ import annotations

import re
import subprocess
from datetime import UTC, datetime

RELEASE_TAG = re.compile(r"^v\d{4}\.\d{2}\.\d{2}(\.\d+)?$")


def next_tag(date: str, existing: list[str], on_head: list[str]) -> str | None:
    if any(RELEASE_TAG.match(tag) for tag in on_head):
        return None
    base = f"v{date}"
    if base not in existing:
        return base
    counter = 1
    while f"{base}.{counter}" in existing:
        counter += 1
    return f"{base}.{counter}"


def _git_tags(*args: str) -> list[str]:
    return subprocess.run(["git", "tag", *args], check=True, capture_output=True, text=True).stdout.split()


def main() -> None:
    date = datetime.now(UTC).strftime("%Y.%m.%d")
    tag = next_tag(date, _git_tags("--list"), _git_tags("--points-at", "HEAD"))
    if tag:
        print(tag)


if __name__ == "__main__":
    main()
