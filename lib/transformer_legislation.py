"""legislation.gov.uk XHTML → GFM markdown transformer (stdlib only).

Handles the `<div class="LegSnippet">` document body served at
`<uri>/data.xht`. The XHTML is well-formed so we parse it with
`xml.etree.ElementTree` and walk the tree, emitting markdown.

Class names used in selection (from the legislation.gov.uk DOM):

- `LegSnippet` — the root container we accept.
- `LegEUChapter`, `LegEUChapterNo`, `LegEUChapterTitle` — chapter heading.
- `LegP1ContainerFirst` / `LegP1Container` — article / regulation / section heading.
- `LegP1No`, `LegP1GroupTitleFirst`, `LegP1GroupTitle` — number + title spans.
- `LegP2Container` — top-level numbered paragraph.
- `LegP2No`, `LegP2Text` — number / text.
- `LegP3Container` — sub-paragraph (e.g. "(a)").
- `LegP3No`, `LegP3Text` — number / text.
- `LegP4Container` etc. — deeper nesting.
- `LegChangeDelimiter`, `LegAddition`, `LegRepealed`, `LegCommentaryLink` —
  amendment annotations. We strip delimiters and commentary links, keep
  additions inline.
"""

from __future__ import annotations

import re
from typing import Iterable
from xml.etree import ElementTree as ET


_NS = "{http://www.w3.org/1999/xhtml}"


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
    """Collect all visible text from `element`, skipping amendment chrome."""
    parts: list[str] = []
    _collect_inline(element, parts)
    text = "".join(parts)
    # Collapse runs of whitespace; preserve a single space.
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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

        # Trim trailing blank lines and ensure single trailing newline.
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

    def _iter_paragraphs(self, root: ET.Element) -> Iterable[str]:
        emitted_any = False
        for element in root.iter():
            cls = _classes(element)
            if "LegP2Container" in cls:
                number = self._number(element, level=2)
                text = self._text(element, level=2)
                if text:
                    emitted_any = True
                    yield f"{number} {text}".strip()
            elif "LegP3Container" in cls:
                number = self._number(element, level=3)
                text = self._text(element, level=3)
                if text:
                    emitted_any = True
                    yield f"    {number} {text}".strip()
            elif "LegP4Container" in cls:
                number = self._number(element, level=4)
                text = self._text(element, level=4)
                if text:
                    emitted_any = True
                    yield f"        {number} {text}".strip()

        if not emitted_any:
            # Fallback for snippets that use plain <p> elements rather than
            # the LegPN container vocabulary (e.g. small SI fragments).
            for element in root.iter():
                if _localname(element.tag) == "p":
                    text = _inline_text(element)
                    if text:
                        yield text

    def _number(self, element: ET.Element, *, level: int) -> str:
        for child in element.iter():
            cls = _classes(child)
            if f"LegP{level}No" in cls:
                return _inline_text(child)
        return ""

    def _text(self, element: ET.Element, *, level: int) -> str:
        for child in element.iter():
            cls = _classes(child)
            if f"LegP{level}Text" in cls:
                return _inline_text(child)
        # Fallback: full element text minus the number span.
        full = _inline_text(element)
        number = self._number(element, level=level)
        if number and full.startswith(number):
            return full[len(number) :].strip()
        return full


class TransformerError(ValueError):
    """Raised on malformed XHTML."""
