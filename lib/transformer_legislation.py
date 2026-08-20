"""legislation.gov.uk XHTML → GFM markdown transformer (stdlib only).

Handles the `<div class="LegSnippet">` document body served at
`<uri>/data.xht`. The XHTML is well-formed so we parse it with
`xml.etree.ElementTree` and walk the tree, emitting markdown.

Class names used in selection (from the legislation.gov.uk DOM):

- `LegSnippet`, the root container we accept.
- `LegEUChapter`, `LegEUChapterNo`, `LegEUChapterTitle`, chapter heading.
- `LegP1ContainerFirst` / `LegP1Container`, article / regulation / section heading.
- `LegP1No`, `LegP1GroupTitleFirst`, `LegP1GroupTitle`, number + title spans.
- `LegP2Container`, top-level numbered paragraph.
- `LegP2No`, `LegP2Text`, number / text.
- `LegP3Container`, sub-paragraph (e.g. "(a)").
- `LegP3No`, `LegP3Text`, number / text.
- `LegP4Container` etc., deeper nesting.
- `LegChangeDelimiter`, `LegAddition`, `LegRepealed`, `LegCommentaryLink`:
  amendment annotations. We strip delimiters and commentary links, keep
  additions inline.
- `LegSP1Container` etc., the `LegSP`-prefixed twin of `LegP1Container` etc.
  Some schedules (e.g. Equality Act 2010 Sch. 2) typeset their numbered
  paragraphs under `LegSP*` rather than `LegP*`; treated identically at
  levels 2-4. At level 1 the two prefixes mean different things: `LegP1*`
  is a section/article heading (title only, handled once by `_find_title`),
  while `LegSP1*` is a schedule paragraph's own numbered content and must
  be walked like any other level.
- `LegSN1No`, `LegSN2No`, ... a schedule-paragraph fragment fetched at
  paragraph granularity (`.../schedule/N/paragraph/M/data.xht`) has no
  ancestor element to carry the outer paragraph number M, so
  legislation.gov.uk folds it into sibling `LegSN1No` (M), `LegSN2No`
  (the first sub-item's own number), ... on the same leaf that carries
  `LegP{n}Text`, instead of a `LegP{n}No`/`LegSP{n}No` this transformer
  otherwise looks for.
"""

from __future__ import annotations

import re
from typing import Iterable
from xml.etree import ElementTree as ET


_NS = "{http://www.w3.org/1999/xhtml}"

# legislation.gov.uk renders repealed/omitted provisions as a run of full stops
# separated by spaces in the body. Detect anything that's only dots, spaces and
# unicode whitespace after collapsing.
_REPEALED_DOTS_RE = re.compile(r"^[\s\.…]+$")
_DOT_COUNT_THRESHOLD = 6  # ".  . . . . ." → 6+ dots = treat as repealed marker

# No/Text spans use either prefix at any level; legislation.gov.uk does not
# mix them within one document, so checking both is safe and never ambiguous.
_NO_TEXT_PREFIXES = ("LegP", "LegSP")

# Container prefixes are level-restricted: a level-1 LegP1Container is a
# section/article heading that _find_title already owns, so only LegSP1
# (a schedule paragraph's own content) counts as a level-1 container here.
_CONTAINER_PREFIXES_BY_LEVEL = {
    1: ("LegSP",),
    2: ("LegP", "LegSP"),
    3: ("LegP", "LegSP"),
    4: ("LegP", "LegSP"),
}


def _has_class(cls: set[str], level: int, part: str) -> bool:
    return any(f"{prefix}{level}{part}" in cls for prefix in _NO_TEXT_PREFIXES)


def _is_container(cls: set[str], level: int) -> bool:
    return any(
        f"{prefix}{level}Container" in cls
        for prefix in _CONTAINER_PREFIXES_BY_LEVEL[level]
    )


def _localname(tag: str) -> str:
    if tag.startswith(_NS):
        return tag[len(_NS) :]
    return tag


def _classes(element: ET.Element) -> set[str]:
    raw = element.get("class")
    if not raw:
        return set()
    return set(raw.split())


def _is_skipped(element: ET.Element) -> bool:
    cls = _classes(element)
    if cls & {"LegChangeDelimiter", "LegCommentaryLink", "LegExtentRestriction"}:
        return True
    if _localname(element.tag) == "a" and not (element.text or "").strip():
        return True
    return False


def _inline_text(element: ET.Element) -> str:
    parts: list[str] = []
    _collect_inline(element, parts)
    return " ".join("".join(parts).split())


def _collect_inline(element: ET.Element, parts: list[str]) -> None:
    if _is_skipped(element):
        if element.tail:
            parts.append(element.tail)
        return
    if element.text:
        parts.append(element.text)
    for child in list(element):
        _collect_inline(child, parts)
    if element.tail:
        parts.append(element.tail)


class LegislationTransformer:
    """XHTML → GFM."""

    def transform(self, xhtml: str, *, citation: str) -> str:
        try:
            root = ET.fromstring(xhtml)
        except ET.ParseError as exc:
            raise TransformerError(f"invalid XHTML: {exc}") from exc

        body_lines: list[str] = [f"# {citation}", ""]

        title = self._find_title(root)
        if title:
            body_lines.append(f"_{title}_")
            body_lines.append("")

        chapter = self._find_chapter(root)
        if chapter:
            body_lines.append(f"**Chapter:** {chapter}")
            body_lines.append("")

        for paragraph in self._iter_paragraphs(root):
            body_lines.append(paragraph)
            body_lines.append("")

        while body_lines and body_lines[-1] == "":
            body_lines.pop()
        return "\n".join(body_lines) + "\n"

    def _find_title(self, root: ET.Element) -> str | None:
        for element in root.iter():
            if "LegP1GroupTitleFirst" in _classes(element):
                return _inline_text(element)
            if "LegP1GroupTitle" in _classes(element):
                return _inline_text(element)
        return None

    def _find_chapter(self, root: ET.Element) -> str | None:
        for element in root.iter():
            if "LegEUChapter" in _classes(element):
                number = ""
                for child in element.iter():
                    if "LegEUChapterNo" in _classes(child):
                        number = _inline_text(child)
                    if "LegEUChapterTitle" in _classes(child):
                        title = _inline_text(child)
                        return f"{number} - {title}" if number else title
        return None

    _LEVELS = {1: "", 2: "", 3: "    ", 4: "        "}

    def _iter_paragraphs(self, root: ET.Element) -> Iterable[str]:
        emitted_any = False
        contained = self._contained_elements(root)
        for element in root.iter():
            cls = _classes(element)
            container_level = next(
                (lvl for lvl in self._LEVELS if _is_container(cls, lvl)), None
            )
            if container_level is not None:
                number = self._number(element, level=container_level)
                text = self._text(element, level=container_level)
                if text:
                    emitted_any = True
                    body = "_(repealed)_" if _is_repealed_marker(text) else text
                    yield f"{self._LEVELS[container_level]}{number} {body}".strip()
                continue
            if id(element) in contained or _localname(element.tag) != "p":
                continue
            if not any(_has_class(cls, level, "Text") for level in self._LEVELS):
                continue
            text = _inline_text(element)
            if text and not _is_repealed_marker(text):
                emitted_any = True
                yield text

        if not emitted_any:
            saw_repealed_only = True
            for element in self._snippet(root).iter():
                if _localname(element.tag) == "p":
                    text = _inline_text(element)
                    if not text:
                        continue
                    if _is_repealed_marker(text):
                        continue
                    saw_repealed_only = False
                    yield text
            if saw_repealed_only:
                yield "_Provision repealed. See source for amendment history._"

    def _snippet(self, root: ET.Element) -> ET.Element:
        """The provision body. legislation.gov.uk wraps it in LegSnippet and
        renders page furniture (licence text, navigation) as siblings, so the
        untagged fallback must not walk outside it."""
        for element in root.iter():
            if "LegSnippet" in _classes(element):
                return element
        return root

    def _contained_elements(self, root: ET.Element) -> set[int]:
        """Ids of every element inside a LegP*Container. Closing words sit in a
        bare LegP{n}Text outside any container; without this set they cannot be
        told apart from the text spans within one, and get emitted twice."""
        contained: set[int] = set()
        for element in root.iter():
            cls = _classes(element)
            if any(_is_container(cls, level) for level in self._LEVELS):
                for descendant in element.iter():
                    contained.add(id(descendant))
        return contained

    def _number(self, element: ET.Element, *, level: int) -> str:
        for child in element.iter():
            cls = _classes(child)
            if _has_class(cls, level, "No"):
                return _inline_text(child)
        return self._schedule_fragment_number(element)

    # Deepest real fragment seen carries 2 (paragraph + first sub-item); this
    # leaves headroom for a third level without letting a malformed or
    # adversarial document spin the loop unbounded.
    _MAX_SCHEDULE_FRAGMENT_DEPTH = 8

    def _schedule_fragment_number(self, element: ET.Element) -> str:
        numbers: list[str] = []
        for depth in range(1, self._MAX_SCHEDULE_FRAGMENT_DEPTH + 1):
            found = next(
                (
                    _inline_text(child)
                    for child in element.iter()
                    if f"LegSN{depth}No" in _classes(child)
                ),
                None,
            )
            if not found:
                break
            numbers.append(found)
        return "".join(numbers)

    def _text(self, element: ET.Element, *, level: int) -> str:
        for child in element.iter():
            cls = _classes(child)
            if _has_class(cls, level, "Text"):
                return _inline_text(child)
        full = _inline_text(element)
        number = self._number(element, level=level)
        if number and full.startswith(number):
            return full[len(number) :].strip()
        return full


def _is_repealed_marker(text: str) -> bool:
    """Detect legislation.gov.uk repealed-text markers.

    legislation.gov.uk renders omitted/repealed provisions as a run of full
    stops separated by spaces (e.g. `. . . . . . . . . . . . . . . . . . . .`).
    Returns True when the collapsed text is dots-and-whitespace only AND has
    at least `_DOT_COUNT_THRESHOLD` dots, avoids false positives on legitimate
    short text like "etc." or numeric ranges.
    """
    if not text:
        return False
    if not _REPEALED_DOTS_RE.fullmatch(text):
        return False
    return text.count(".") >= _DOT_COUNT_THRESHOLD


class TransformerError(ValueError):
    """Raised on malformed XHTML."""
