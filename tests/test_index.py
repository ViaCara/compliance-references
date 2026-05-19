"""Corpus index builder tests (stdlib unittest).

ADR-0023: build.py emits a per-source metadata index (no clause bodies) that
the consumer mirrors maximally for offline search. The index joins the
manifest entry with the rendered corpus file's frontmatter
(revision_id + content_sha256).
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.frontmatter import render
from lib.index import build_index, write_index


def _source(**overrides):
    src = {
        "id": "uk-gdpr-art-009",
        "citation": "UK GDPR Article 9",
        "title": "UK GDPR Article 9 - Processing of special categories",
        "instrument": "uk-gdpr",
        "source_uri": "https://www.legislation.gov.uk/eur/2016/679/article/9/data.xht",
        "target": "statute/uk/gdpr/article-009.md",
        "kind": "legislation_article",
        "frequency": "monthly",
    }
    src.update(overrides)
    return src


def _write_corpus_file(corpus_root: Path, target: str, *, revision_id: str, sha: str):
    path = corpus_root / target
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = {
        "id": "uk-gdpr-art-009",
        "revision_id": revision_id,
        "content_sha256": sha,
        "enforcement_status": "in_force",
    }
    path.write_text(render(fields, "# Body text that must NOT enter the index\n"), encoding="utf-8")


class BuildIndexTests(unittest.TestCase):
    def test_one_record_per_source_with_schema_keys_and_no_body(self):
        with TemporaryDirectory() as td:
            corpus_root = Path(td)
            _write_corpus_file(
                corpus_root,
                "statute/uk/gdpr/article-009.md",
                revision_id="Wed, 13 May 2026 15:07:58 GMT",
                sha="e5d8404dfedb6b11c375f27a8e5fae453b0881fe659e4f9be0bd8fad61a01dc1",
            )

            index = build_index([_source()], corpus_root)

            self.assertEqual(len(index), 1)
            record = index[0]
            self.assertEqual(record["id"], "uk-gdpr-art-009")
            self.assertEqual(record["title"], "UK GDPR Article 9 - Processing of special categories")
            self.assertEqual(
                record["source_uri"],
                "https://www.legislation.gov.uk/eur/2016/679/article/9/data.xht",
            )
            self.assertEqual(record["revision_id"], "Wed, 13 May 2026 15:07:58 GMT")
            self.assertEqual(
                record["sha"],
                "e5d8404dfedb6b11c375f27a8e5fae453b0881fe659e4f9be0bd8fad61a01dc1",
            )
            # The index is metadata only: no clause body may leak into it.
            self.assertNotIn("body", record)
            self.assertNotIn("content", record)
            for value in record.values():
                self.assertNotIn("Body text that must NOT enter the index", str(value))


    def test_jurisdiction_and_authority_are_derived(self):
        with TemporaryDirectory() as td:
            corpus_root = Path(td)
            _write_corpus_file(
                corpus_root,
                "statute/uk/gdpr/article-009.md",
                revision_id="r1",
                sha="abc",
            )
            eu_target = "statute/eu/ai-act/article-006.md"
            _write_corpus_file(corpus_root, eu_target, revision_id="r2", sha="def")

            index = build_index(
                [
                    _source(),
                    _source(
                        id="eu-ai-act-art-006",
                        target=eu_target,
                        kind="eur_lex_article",
                        instrument="eu-ai-act",
                    ),
                ],
                corpus_root,
            )

            by_id = {r["id"]: r for r in index}
            self.assertEqual(by_id["uk-gdpr-art-009"]["jurisdiction"], "uk")
            self.assertEqual(by_id["uk-gdpr-art-009"]["authority"], "statute")
            self.assertEqual(by_id["eu-ai-act-art-006"]["jurisdiction"], "eu")
            self.assertEqual(by_id["eu-ai-act-art-006"]["authority"], "statute")


    def test_domain_tags_and_summary_carry_from_manifest_with_empty_defaults(self):
        with TemporaryDirectory() as td:
            corpus_root = Path(td)
            _write_corpus_file(
                corpus_root,
                "statute/uk/gdpr/article-009.md",
                revision_id="r1",
                sha="abc",
            )
            tagged = "statute/uk/gdpr/article-022.md"
            _write_corpus_file(corpus_root, tagged, revision_id="r2", sha="def")

            index = build_index(
                [
                    _source(),  # no domain_tags / summary in manifest
                    _source(
                        id="uk-gdpr-art-022",
                        target=tagged,
                        domain_tags=["automated-decision", "profiling"],
                        summary="Right not to be subject to solely automated decisions.",
                    ),
                ],
                corpus_root,
            )

            by_id = {r["id"]: r for r in index}
            self.assertEqual(by_id["uk-gdpr-art-009"]["domain_tags"], [])
            self.assertEqual(by_id["uk-gdpr-art-009"]["summary"], "")
            self.assertEqual(
                by_id["uk-gdpr-art-022"]["domain_tags"],
                ["automated-decision", "profiling"],
            )
            self.assertEqual(
                by_id["uk-gdpr-art-022"]["summary"],
                "Right not to be subject to solely automated decisions.",
            )


    def test_write_index_is_sorted_by_id_and_byte_identical_on_rerun(self):
        with TemporaryDirectory() as td:
            corpus_root = Path(td)
            for tgt in ("statute/uk/gdpr/article-009.md", "statute/uk/gdpr/article-005.md"):
                _write_corpus_file(corpus_root, tgt, revision_id="r", sha="s")
            # Manifest order is 009 then 005; the index must not inherit it.
            sources = [
                _source(),
                _source(id="uk-gdpr-art-005", target="statute/uk/gdpr/article-005.md"),
            ]
            out = corpus_root / "index.json"

            write_index(out, sources, corpus_root)
            first = out.read_bytes()
            write_index(out, sources, corpus_root)
            second = out.read_bytes()

            self.assertEqual(first, second)  # determinism contract: zero diff on re-run
            ids = [r["id"] for r in json.loads(first.decode("utf-8"))]
            self.assertEqual(ids, sorted(ids))
            self.assertTrue(first.endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
