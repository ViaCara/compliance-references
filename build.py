#!/usr/bin/env python3
"""compliance-references central sync orchestrator (Python 3.12 stdlib only).

Reads `manifest.json`, fetches each source URI, runs the appropriate
transformer, writes deterministic markdown under `corpus/` with frontmatter
recording source URI, revision id and content hash. Determinism contract:
re-running against an unchanged source set produces zero file diffs.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from dataclasses import dataclass
from pathlib import Path

from lib.changelog import Changelog, Entry
from lib.fetcher import FetchError, Fetcher, NotModified, TransportError
from lib.frontmatter import body_sha256, parse, render
from lib.index import write_index
from lib.manifest import EUR_LEX_KINDS, LEGISLATION_KINDS, load
from lib.transformer_eur_lex import EurLexTransformer
from lib.transformer_legislation import LegislationTransformer


ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
MANIFEST = ROOT / "manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"


class BuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class BuildContext:
    fetcher: Fetcher
    legislation: LegislationTransformer
    eur_lex: EurLexTransformer
    changelog: Changelog
    today: str


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync the compliance-references corpus")
    parser.add_argument("--only", help="Only process the entry with this id")
    parser.add_argument(
        "--skip-unreachable",
        action="store_true",
        help="Skip sources that can't be fetched instead of erroring out",
    )
    args = parser.parse_args(argv)

    manifest = load(MANIFEST)
    ctx = BuildContext(
        fetcher=Fetcher(),
        legislation=LegislationTransformer(),
        eur_lex=EurLexTransformer(),
        changelog=Changelog(CHANGELOG),
        today=_dt.date.today().isoformat(),
    )

    entries = list(manifest.sources)
    if args.only:
        entries = [entry for entry in entries if entry["id"] == args.only]
        if not entries:
            print(f"no manifest entry with id={args.only!r}", file=sys.stderr)
            return 2

    errors: list[str] = []
    written = 0
    unchanged = 0

    for entry in entries:
        target_path = CORPUS / entry["target"]
        try:
            outcome = _process_entry(entry, target_path, ctx)
        except FetchError as exc:
            if args.skip_unreachable:
                print(f"skip {entry['id']}: {exc}", file=sys.stderr)
                continue
            errors.append(f"{entry['id']}: {exc}")
            continue
        except BuildError as exc:
            errors.append(f"{entry['id']}: {exc}")
            continue

        if outcome == "written":
            written += 1
        else:
            unchanged += 1

    write_index(ROOT / "index.json", manifest.sources, CORPUS)

    print(f"summary: {written} written, {unchanged} unchanged, {len(errors)} errors")
    for err in errors:
        print(f"error: {err}", file=sys.stderr)
    return 1 if errors else 0


def _process_entry(entry, target_path: Path, ctx: BuildContext) -> str:
    prior_etag, prior_sha = _prior_metadata(target_path)
    try:
        result = ctx.fetcher.fetch(entry["source_uri"], if_none_match=prior_etag)
    except NotModified:
        return "no-op"

    transformer_kind = entry["kind"]
    citation = entry.get("citation") or entry.get("title") or entry["id"]
    if transformer_kind in LEGISLATION_KINDS:
        body = ctx.legislation.transform(result.body.decode("utf-8"), citation=citation)
    elif transformer_kind in EUR_LEX_KINDS:
        body = ctx.eur_lex.transform(result.body.decode("utf-8"), citation=citation)
    else:
        raise BuildError(f"no transformer for kind={transformer_kind!r}")

    new_hash = body_sha256(body)
    if prior_sha == new_hash:
        return "unchanged"

    fields = {
        "id": entry["id"],
        "title": entry.get("title") or citation,
        "instrument": entry.get("instrument", ""),
        "kind": transformer_kind,
        "citation": citation,
        "source_uri": entry["source_uri"],
        "source_format": entry.get("source_format", "xhtml"),
        "revision_id": result.last_modified or "",
        "content_sha256": new_hash,
        "last_fetched": ctx.today,
        "language": entry.get("language", "en-GB"),
        "enforcement_status": entry.get("enforcement_status", "in_force"),
    }
    if result.etag:
        fields["etag"] = result.etag

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(render(fields, body), encoding="utf-8")

    ctx.changelog.append(
        Entry(
            date=ctx.today,
            target=str(target_path.relative_to(ROOT)),
            source_uri=entry["source_uri"],
            prior_sha256=prior_sha or "(new file)",
            new_sha256=new_hash,
            summary=_summary(prior_sha, new_hash),
            revision=result.last_modified,
        )
    )
    return "written"


def _prior_metadata(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, None
    try:
        fields, _ = parse(path.read_text(encoding="utf-8"))
    except Exception:
        return None, None
    return fields.get("etag"), fields.get("content_sha256")


def _summary(prior_sha: str | None, new_sha: str) -> str:
    if not prior_sha:
        return "new file"
    return f"hash {prior_sha[:7]} -> {new_sha[:7]}"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
