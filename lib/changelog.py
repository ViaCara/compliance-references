"""CHANGELOG.md append-only writer (stdlib only)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Entry:
    date: str
    target: str
    source_uri: str
    prior_sha256: str
    new_sha256: str
    summary: str
    revision: str | None = None


_HEADER = "# CHANGELOG\n\nDrift log. Newer entries first.\n\n"


class Changelog:
    def __init__(self, path: Path):
        self.path = path

    def append(self, entry: Entry) -> None:
        existing = (
            self.path.read_text(encoding="utf-8") if self.path.exists() else _HEADER
        )
        if not existing.startswith(_HEADER):
            existing = _HEADER + existing

        date_heading = f"## {entry.date}"
        rendered = self._render(entry)

        # Find an existing date heading or insert a new one at the top of body.
        date_match = re.search(
            rf"^{re.escape(date_heading)}\s*$",
            existing,
            flags=re.MULTILINE,
        )
        if date_match is None:
            new_text = (
                _HEADER
                + date_heading
                + "\n"
                + rendered
                + "\n"
                + existing[len(_HEADER) :]
            )
        else:
            insertion_point = date_match.end() + 1
            new_text = (
                existing[:insertion_point]
                + rendered
                + "\n"
                + existing[insertion_point:]
            )

        self.path.write_text(new_text, encoding="utf-8")

    def _render(self, entry: Entry) -> str:
        lines = [
            f"- **{entry.target}** {entry.summary}",
            f"  - source: {entry.source_uri}",
            f"  - prior_sha256: {entry.prior_sha256}",
            f"  - new_sha256:   {entry.new_sha256}",
        ]
        if entry.revision:
            lines.append(f"  - revision: {entry.revision}")
        return "\n".join(lines) + "\n"
