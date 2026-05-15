"""Markdown frontmatter helpers (stdlib only).

A tiny YAML subset is sufficient for the corpus:
- scalars (`key: value`)
- double-quoted strings (`key: "value with spaces"`)
- ISO dates (`key: 2026-05-01`)
- integers / booleans (not currently used; left for the future)

No nested maps or lists in frontmatter. Anything richer should live in the body.
"""

from __future__ import annotations

import hashlib
import re


class FrontmatterError(ValueError):
    """Raised on malformed frontmatter."""


_DELIMITER = "---"


def render(fields: dict, body: str) -> str:
    """Render a markdown file with frontmatter preserving field insertion order."""
    lines = [_DELIMITER]
    for key, value in fields.items():
        lines.append(f"{key}: {_emit_scalar(value)}")
    lines.append(_DELIMITER)
    head = "\n".join(lines) + "\n"
    return head + body


def parse(text: str) -> tuple[dict, str]:
    """Parse a markdown file with frontmatter, returning (fields, body)."""
    if not text.startswith(_DELIMITER + "\n"):
        raise FrontmatterError("missing opening --- delimiter")

    rest = text[len(_DELIMITER) + 1 :]
    end_match = re.search(r"^---\s*$", rest, flags=re.MULTILINE)
    if end_match is None:
        raise FrontmatterError("missing closing --- delimiter")

    head = rest[: end_match.start()]
    body = rest[end_match.end() :]
    if body.startswith("\n"):
        body = body[1:]

    fields: dict = {}
    for raw_line in head.splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise FrontmatterError(f"malformed frontmatter line: {raw_line!r}")
        key, _, value = line.partition(":")
        fields[key.strip()] = _parse_scalar(value.strip())

    return fields, body


def body_sha256(text: str) -> str:
    """Return the SHA-256 of the body, ignoring frontmatter.

    Stable across frontmatter changes so determinism gates work.
    """
    try:
        _, body = parse(text)
    except FrontmatterError:
        body = text
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _emit_scalar(value) -> str:
    if isinstance(value, str):
        if _needs_quoting(value):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _needs_quoting(value: str) -> bool:
    if not value:
        return True
    if value != value.strip():
        return True
    if any(ch in value for ch in (":", "#", "\n", '"', "'")):
        return True
    if value.startswith(("-", "*", "&", "!", "|", ">", "%", "@", "`")):
        return True
    return False


def _parse_scalar(raw: str) -> str:
    if not raw:
        return ""
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        inner = raw[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\")
    return raw
