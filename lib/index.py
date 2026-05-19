"""Corpus index builder (stdlib only).

ADR-0023: the registry emits a per-source metadata index with no clause
bodies. The consumer mirrors it maximally and searches it offline. Each
record joins the manifest entry (id, title, source URI) with the rendered
corpus file's frontmatter (revision id, content hash).
"""

from __future__ import annotations

import json
from pathlib import Path

from lib.frontmatter import parse

# kind -> authority weight. Statute is binding; guidance is persuasive;
# standards are binding-on-members or technical. New kinds must be classified
# here so the index never emits an unweighted authority.
_AUTHORITY_BY_KIND = {
    "legislation_article": "statute",
    "legislation_section": "statute",
    "legislation_regulation": "statute",
    "eur_lex_article": "statute",
    "eur_lex_recital": "statute",
    "guidance": "guidance",
    "curated_quotes": "guidance",
    "standard": "standard",
    "external_index": "standard",
}


def _jurisdiction(target: str) -> str:
    """Derive jurisdiction from the corpus path: <layer>/<jurisdiction>/...."""
    parts = Path(target).parts
    return parts[1] if len(parts) >= 2 else ""


def _authority(kind: str) -> str:
    return _AUTHORITY_BY_KIND.get(kind, "")


def build_index(sources: list[dict], corpus_root: Path) -> list[dict]:
    """Build the metadata index for the given manifest sources.

    Pure over (sources, on-disk corpus). No network. No clause body is
    ever copied into a record.
    """
    records: list[dict] = []
    for source in sources:
        corpus_file = corpus_root / source["target"]
        fields, _body = parse(corpus_file.read_text(encoding="utf-8"))
        records.append(
            {
                "id": source["id"],
                "title": source.get("title", source.get("citation", source["id"])),
                "path": source["target"],
                "jurisdiction": _jurisdiction(source["target"]),
                "authority": _authority(source["kind"]),
                "source_uri": source["source_uri"],
                "domain_tags": list(source.get("domain_tags", [])),
                "summary": source.get("summary", ""),
                "revision_id": fields.get("revision_id", ""),
                "sha": fields.get("content_sha256", ""),
            }
        )
    return records


def write_index(path: Path, sources: list[dict], corpus_root: Path) -> None:
    """Emit the metadata index as deterministic JSON.

    Records are sorted by id and keys are sorted, so re-running against an
    unchanged corpus produces a byte-identical file (the determinism
    contract in PRD req 1 / ADR-0023).
    """
    records = sorted(build_index(sources, corpus_root), key=lambda r: r["id"])
    path.write_text(
        json.dumps(records, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
