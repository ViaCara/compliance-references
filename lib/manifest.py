"""Manifest loader and validator (stdlib only)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse


class ManifestError(ValueError):
    """Raised when manifest.json is malformed or invalid."""


VALID_KINDS = {
    "legislation_article",
    "legislation_recital",
    "legislation_section",
    "legislation_regulation",
    "legislation_schedule",
    "legislation_part",
    "legislation_chapter",
    "eur_lex_article",
    "eur_lex_recital",
    "eur_lex_annex",
    "curated_quotes",
    "external_index",
    "contents",
}

VALID_FREQUENCIES = {"monthly", "quarterly", "yearly"}


@dataclass
class Manifest:
    sources: list = field(default_factory=list)
    contents_pages: list = field(default_factory=list)


def load(path: Path) -> Manifest:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON in {path}: {exc}") from exc
    return validate(data)


def validate(data) -> Manifest:
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be an object")
    sources = data.get("sources", [])
    contents = data.get("contents_pages", [])
    if not isinstance(sources, list) or not isinstance(contents, list):
        raise ManifestError("manifest sources / contents_pages must be lists")

    seen_ids: set[str] = set()
    seen_targets: set[str] = set()

    for entry in sources:
        _validate_entry(entry, require_kind=True)
        _check_unique(entry, seen_ids, seen_targets)

    for entry in contents:
        _validate_entry(entry, require_kind=False)
        _check_unique(entry, seen_ids, seen_targets)

    return Manifest(sources=sources, contents_pages=contents)


def _validate_entry(entry, *, require_kind: bool) -> None:
    if not isinstance(entry, dict):
        raise ManifestError(f"manifest entry must be an object: {entry!r}")
    for key in ("id", "source_uri", "target"):
        if key not in entry or not isinstance(entry[key], str) or not entry[key]:
            raise ManifestError(f"missing/invalid field {key!r} in entry {entry!r}")
    parsed = urlparse(entry["source_uri"])
    if parsed.scheme != "https":
        raise ManifestError(
            f"source_uri must use https scheme: {entry['source_uri']!r}"
        )
    target = entry["target"]
    normalised = Path(target)
    if normalised.is_absolute() or any(part == ".." for part in normalised.parts):
        raise ManifestError(f"target must stay under corpus/: {target!r}")
    if require_kind:
        kind = entry.get("kind")
        if kind not in VALID_KINDS:
            raise ManifestError(f"unknown kind {kind!r} in entry {entry['id']!r}")
        frequency = entry.get("frequency", "monthly")
        if frequency not in VALID_FREQUENCIES:
            raise ManifestError(
                f"unknown frequency {frequency!r} in entry {entry['id']!r}"
            )


def _check_unique(entry, seen_ids: set, seen_targets: set) -> None:
    entry_id = entry["id"]
    target = entry["target"]
    if entry_id in seen_ids:
        raise ManifestError(f"duplicate id {entry_id!r}")
    if target in seen_targets:
        raise ManifestError(f"duplicate target {target!r}")
    seen_ids.add(entry_id)
    seen_targets.add(target)
