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
- `LegTitleBlockTitle`, a schedule's own title, used as the title line
  only when the page has no `LegP1GroupTitle`.
- `LegSchedulePart` / `LegSchedulePartFirst` with `LegPartNo` and
  `LegPartTitle`, a Part heading inside a schedule, kept as a bold
  "PART n - Title" line because paragraphs refer to "this Part".
- `LegSP1GroupTitle` / `LegSP1GroupTitleFirst`, a schedule's cross-heading,
  kept as a bold line like `LegP2GroupTitle`.
- `LegP2GroupTitle`, a cross-heading inside a section ("All services",
  "Additional duties for Category 1 services"). It scopes the subsections
  under it, so it is kept as a bold line.
- `LegP2No`, `LegP2Text`, number / text.
- `LegP3Container`, sub-paragraph (e.g. "(a)").
- `LegP3No`, `LegP3Text`, number / text.
- `LegP4Container` etc., deeper nesting.
- `LegP{n}TextAmend`, `LegTextAmend`: the quoted words an amending
  provision inserts or substitutes, a paragraph of their own after the
  "insert—" or "substitute" line.
- `LegChangeDelimiter`, `LegAddition`, `LegRepealed`, `LegCommentaryLink`:
  amendment annotations. We strip delimiters and commentary links, keep
  additions inline.
- `LegConcurrent`, a heading's extent badge when a provision has one version
  per territorial extent. With two or more versions, each is labelled
  `**Extent:**` so the versions do not read as duplicates.
- `LegSP1Container` etc., the `LegSP`-prefixed twin of `LegP1Container` etc.
  Some schedules (e.g. Equality Act 2010 Sch. 2) typeset their numbered
  paragraphs under `LegSP*` rather than `LegP*`; treated identically at
  levels 2-4. At level 1 the two prefixes mean different things: `LegP1*`
  is a section/article heading (title only, handled once by `_find_title`),
  while `LegSP1*` is a schedule paragraph's own numbered content and must
  be walked like any other level.
- `LegP1ParaText`, `LegP2ParaText`, ... statutory instruments (and some
  Act sections) typeset each numbered paragraph as a flat `<p>` whose text
  carries its own "(1)" rather than as a `LegP{n}Container` with separate
  No/Text spans. The level-1 variant also carries the provision number in a
  `LegP1No` span ("4.—(1) ...") which is stripped because the heading
  already names the provision.
- `LegTabbedDef`, `LegListTextStandard`, `LegLevel{n}`, `LegListItem`,
  `LegListItemNo`: an interpretation subsection ("In this Chapter—") lists
  its defined terms as a `<ul class="LegTabbedDef">` whose items carry no
  `LegP{n}Text` class at all, and nests lettered limbs as `LegListItem`
  divs whose number sits in a sibling `LegListItemNo` div rather than in a
  `LegP{n}No` span. A `LegBlockText` block can also open such a list with a
  bare `<p class="LegLevel{n}">` ("Here "Act" means—") that carries no text
  class; it is emitted as a paragraph so the list keeps its lead-in.
- `LegSN1No`, `LegSN2No`, ... a schedule-paragraph fragment fetched at
  paragraph granularity (`.../schedule/N/paragraph/M/data.xht`) has no
  ancestor element to carry the outer paragraph number M, so
  legislation.gov.uk folds it into sibling `LegSN1No` (M), `LegSN2No`
  (the first sub-item's own number), ... on the same leaf that carries
  `LegP{n}Text`, instead of a `LegP{n}No`/`LegSP{n}No` this transformer
  otherwise looks for.
- `LegTabular`, `LegTable`: a provision that sets its wording in an XHTML
  `<table>` (Equality Act 2010 s. 20, UK GDPR Art. 17). The table is
  rendered whole as a GFM table at its place in the document, because
  printing some cells and not others reads as a complete table. A cell that
  spans rows repeats its text in each row it covers, so every row keeps its
  associations; a cell that spans columns fills the first and leaves the
  rest empty. Paragraphs within one cell are joined with `<br>`. Tables
  sit under `LegTabular`, outside any numbered container; a container
  never reads a cell as its own number or text.
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
    5: ("LegP", "LegSP"),
}

_PARA_TEXT_RE = re.compile(r"^LegP(\d)ParaText$")
_AMEND_TEXT_RE = re.compile(r"^Leg(?:P\d)?TextAmend$")
_LIST_TEXT_CLASS = "LegListTextStandard"
_LIST_ITEM_CLASS = "LegListItem"
_LIST_ITEM_NO_CLASS = "LegListItemNo"
_LIST_LEVEL_RE = re.compile(r"^LegLevel(\d)$")
_EU_TEXT_CLASS = "LegText"
_DIVISION_CLASS = "LegDivision"
_DIVISION_TAGS = frozenset({"h2", "h3", "h4", "h5", "h6"})
_PARA_NUMBER_DASHES = "\u2014\u2013-"


def _para_text_level(cls: set[str]) -> int | None:
    for name in cls:
        match = _PARA_TEXT_RE.match(name)
        if match:
            return int(match.group(1))
    return None


def _list_level(cls: set[str]) -> int | None:
    for name in cls:
        match = _LIST_LEVEL_RE.match(name)
        if match:
            return int(match.group(1))
    return None


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
    if _localname(element.tag) == "a" and not "".join(element.itertext()).strip():
        return True
    return False


def _iter_outside_tables(element: ET.Element) -> Iterable[ET.Element]:
    """The element and its descendants, without anything inside a table:
    a table's cells belong to the table, never to the prose around it."""
    yield element
    for child in element:
        if _localname(child.tag) != "table":
            yield from _iter_outside_tables(child)


def _inline_text(element: ET.Element) -> str:
    parts: list[str] = []
    _collect_inline(element, parts)
    return " ".join("".join(parts).split())


def _collect_inline(element: ET.Element, parts: list[str]) -> None:
    if _is_skipped(element) or _localname(element.tag) == "table":
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
        for element in root.iter():
            if "LegTitleBlockTitle" in _classes(element):
                return _inline_text(element)
        return None

    def _schedule_part_heading(self, element: ET.Element) -> str:
        number = title = ""
        for child in element.iter():
            if "LegPartNo" in _classes(child):
                number = _inline_text(child)
            if "LegPartTitle" in _classes(child):
                title = _inline_text(child)
        return " - ".join(part for part in (number, title) if part)

    def _table_descendants(self, root: ET.Element) -> set[int]:
        """Ids of every element inside a table, the table itself excluded.
        The table is rendered whole by `_table_markdown`, so no branch of the
        walk may emit a cell's text a second time."""
        return {
            id(descendant)
            for table in root.iter()
            if _localname(table.tag) == "table"
            for descendant in table.iter()
            if descendant is not table
        }

    def _division_heading(self, element: ET.Element) -> str:
        number = title = ""
        for child in element.iter():
            if "LegDivisionNo" in _classes(child):
                number = _inline_text(child)
            if "LegDivisionTitle" in _classes(child):
                title = _inline_text(child)
        if number or title:
            return " ".join(part for part in (number, title) if part)
        return _inline_text(element)

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

    _LEVELS = {1: "", 2: "", 3: "    ", 4: "        ", 5: "            "}

    def _iter_paragraphs(self, root: ET.Element) -> Iterable[str]:
        emitted_any = False
        # (is_table, text) in document order; tables do not count as emitted
        # text, so a page whose prose is untagged still reaches the fallback.
        out: list[tuple[int, bool, str]] = []
        position = {id(element): index for index, element in enumerate(root.iter())}
        headings: set[int] = set()
        # Tables beside the provision body (page furniture) are not the law.
        in_snippet = {id(element) for element in self._snippet(root).iter()}
        contained = self._contained_elements(root)
        list_numbers = self._list_item_numbers(root)
        in_tables = self._table_descendants(root)
        extents = self._concurrent_extents(root)
        for element in root.iter():
            if id(element) in in_tables:
                continue
            pos = position[id(element)]
            if _localname(element.tag) == "table":
                table = _table_markdown(element) if id(element) in in_snippet else ""
                if table:
                    out.append((pos, True, table))
                continue
            cls = _classes(element)
            if len(extents) > 1 and id(element) in extents:
                headings.add(id(element))
                out.append((pos, False, f"**Extent:** {extents[id(element)]}"))
                continue
            if cls & {"LegSchedulePart", "LegSchedulePartFirst"}:
                heading = self._schedule_part_heading(element)
                if heading:
                    headings.add(id(element))
                    out.append((pos, False, f"**{heading}**"))
                continue
            if cls & {"LegP2GroupTitle", "LegSP1GroupTitle", "LegSP1GroupTitleFirst"}:
                heading = _inline_text(element)
                if heading:
                    headings.add(id(element))
                    out.append((pos, False, f"**{heading}**"))
                continue
            if _DIVISION_CLASS in cls and _localname(element.tag) in _DIVISION_TAGS:
                heading = self._division_heading(element)
                if heading:
                    headings.add(id(element))
                    out.append((pos, False, f"**{heading}**"))
                continue
            container_level = next(
                (lvl for lvl in self._LEVELS if _is_container(cls, lvl)), None
            )
            if container_level is not None:
                number = self._number(element, level=container_level)
                text = self._text(element, level=container_level)
                if text:
                    emitted_any = True
                    body = "_(repealed)_" if _is_repealed_marker(text) else text
                    out.append((pos, False, f"{self._LEVELS[container_level]}{number} {body}".strip()))
                continue
            if id(element) in contained or _localname(element.tag) != "p":
                continue
            para_level = _para_text_level(cls)
            if para_level is not None:
                text = self._para_text(element, level=para_level)
                if text and not _is_repealed_marker(text):
                    emitted_any = True
                    out.append((pos, False, text))
                continue
            if any(_AMEND_TEXT_RE.match(name) for name in cls):
                text = _inline_text(element)
                if text:
                    emitted_any = True
                    out.append((pos, False, text))
                continue
            if _LIST_TEXT_CLASS in cls:
                text = _inline_text(element)
                if text and not _is_repealed_marker(text):
                    emitted_any = True
                    indent = self._LEVELS.get(_list_level(cls) or 0, "")
                    number = list_numbers.get(id(element), "")
                    out.append((pos, False, f"{indent}{number} {text}".strip()))
                continue
            if _EU_TEXT_CLASS in cls:
                text = _inline_text(element)
                if text and not _is_repealed_marker(text):
                    emitted_any = True
                    out.append((pos, False, text))
                continue
            if _list_level(cls) is not None:
                text = _inline_text(element)
                if text and not _is_repealed_marker(text):
                    emitted_any = True
                    out.append((pos, False, text))
                continue
            if not any(_has_class(cls, level, "Text") for level in self._LEVELS):
                continue
            text = _inline_text(element)
            if text and not _is_repealed_marker(text):
                emitted_any = True
                out.append((pos, False, text))

        if emitted_any:
            yield from (text for _, _, text in out)
            return
        # Untagged prose: headings stay, and the fallback adds each paragraph
        # and table, all in document order.
        merged: list[tuple[int, str]] = [(pos, text) for pos, is_table, text in out if not is_table]
        saw_repealed_only = True
        for element in self._snippet(root).iter():
            if id(element) in in_tables:
                continue
            if id(element) in headings:
                # Already emitted as a heading, but it is still words.
                heading_text = _inline_text(element) if _localname(element.tag) == "p" else ""
                if heading_text and not _is_repealed_marker(heading_text):
                    saw_repealed_only = False
                continue
            if _localname(element.tag) == "table":
                table = _table_markdown(element)
                if table:
                    saw_repealed_only = False
                    merged.append((position[id(element)], table))
                continue
            if _localname(element.tag) == "p":
                text = _inline_text(element)
                if not text:
                    continue
                if _is_repealed_marker(text):
                    continue
                saw_repealed_only = False
                merged.append((position[id(element)], text))
        yield from (text for _, text in sorted(merged, key=lambda item: item[0]))
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

    def _concurrent_extents(self, root: ET.Element) -> dict[int, str]:
        """Map each provision heading that opens a concurrent version to its
        territorial extent. legislation.gov.uk serves every extent's version
        of a provision back to back in one snippet, each under its own
        heading whose `LegConcurrent` span names the extent."""
        extents: dict[int, str] = {}
        for element in root.iter():
            if not _classes(element) & {"LegP1GroupTitleFirst", "LegP1GroupTitle"}:
                continue
            restriction = next(
                (
                    child
                    for concurrent in element.iter()
                    if "LegConcurrent" in _classes(concurrent)
                    for child in concurrent.iter()
                    if "LegExtentRestriction" in _classes(child)
                ),
                None,
            )
            if restriction is None:
                continue
            title = (restriction.get("title") or "").removeprefix("Applies to ").strip()
            extents[id(element)] = title or " ".join("".join(restriction.itertext()).split())
        return extents

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

    def _list_item_numbers(self, root: ET.Element) -> dict[int, str]:
        """Map each numbered list item's text paragraph to its number.

        A `LegListItem` holds its number in a sibling `LegListItemNo` div
        rather than in the `LegP{n}No` span `_number` looks for, and
        ElementTree has no parent pointers, so the pairing is resolved once
        up front. A nested item is walked in its own right, and its first
        text paragraph is its own, so the outer item never claims it."""
        numbers: dict[int, str] = {}
        for element in root.iter():
            if _LIST_ITEM_CLASS not in _classes(element):
                continue
            number = next(
                (
                    _inline_text(child)
                    for child in element.iter()
                    if _LIST_ITEM_NO_CLASS in _classes(child)
                ),
                "",
            )
            if not number:
                continue
            text_element = next(
                (
                    child
                    for child in element.iter()
                    if _localname(child.tag) == "p"
                    and _LIST_TEXT_CLASS in _classes(child)
                ),
                None,
            )
            if text_element is not None:
                numbers[id(text_element)] = number
        return numbers

    def _number(self, element: ET.Element, *, level: int) -> str:
        for child in _iter_outside_tables(element):
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
                    for child in _iter_outside_tables(element)
                    if f"LegSN{depth}No" in _classes(child)
                ),
                None,
            )
            if not found:
                break
            numbers.append(found)
        return "".join(numbers)

    def _para_text(self, element: ET.Element, *, level: int) -> str:
        """Text of a flat LegP{n}ParaText paragraph. At level 1 the paragraph
        opens with the provision number ("4.—(1) ..."); drop the number and
        the dash that joins it so the line starts at "(1)" like every other
        numbered paragraph."""
        full = _inline_text(element)
        if level != 1:
            return full
        number = next(
            (
                " ".join("".join(child.itertext()).split())
                for child in element.iter()
                if _has_class(_classes(child), 1, "No")
            ),
            "",
        )
        if number and full.startswith(number):
            full = full[len(number) :].lstrip(_PARA_NUMBER_DASHES + " ")
        return full

    def _text(self, element: ET.Element, *, level: int) -> str:
        for child in _iter_outside_tables(element):
            cls = _classes(child)
            if _has_class(cls, level, "Text"):
                return _inline_text(child)
        full = _inline_text(element)
        number = self._number(element, level=level)
        if number and full.startswith(number):
            return full[len(number) :].strip()
        return full


_TABLE_SECTIONS = frozenset({"thead", "tbody", "tfoot"})
_TABLE_CELLS = frozenset({"td", "th"})
_BLOCK_IN_CELL = frozenset({"p", "div", "li", "tr", "td", "th", "br"})
# A malformed span must not make the grid grow without bound.
_MAX_TABLE_SPAN = 100


def _table_groups(table: ET.Element) -> list[list[list[ET.Element]]]:
    """Row groups in the order HTML renders them: thead, then body rows, then
    tfoot. A row span ends at the end of its own group. A nested table's rows
    belong to its own cell, not to this table."""
    thead: list[list[list[ET.Element]]] = []
    body: list[list[list[ET.Element]]] = []
    tfoot: list[list[list[ET.Element]]] = []

    def cells(row: ET.Element) -> list[ET.Element]:
        return [cell for cell in row if _localname(cell.tag) in _TABLE_CELLS]

    loose: list[list[ET.Element]] | None = None
    for child in table:
        name = _localname(child.tag)
        if name == "tr":
            # Rows directly under the table form a body group in place.
            if loose is None:
                loose = []
                body.append(loose)
            loose.append(cells(child))
            continue
        loose = None
        if name in _TABLE_SECTIONS:
            rows = [cells(row) for row in child if _localname(row.tag) == "tr"]
            {"thead": thead, "tbody": body, "tfoot": tfoot}[name].append(rows)
    return thead + body + tfoot


_ZERO_RE = re.compile(r"\s*\+?0+\s*")


def _is_zero(value: str | None) -> bool:
    return value is not None and _ZERO_RE.fullmatch(value) is not None


def _span(cell: ET.Element, attribute: str) -> int:
    try:
        value = int(cell.get(attribute) or 1)
    except ValueError:
        return 1
    return max(1, min(value, _MAX_TABLE_SPAN))


_BLOCK_BREAK = "\x00"


def _collect_cell(element: ET.Element, parts: list[str]) -> None:
    """Like `_collect_inline`, but marks where each block starts and ends so
    loose text beside a paragraph stays its own segment."""
    if _is_skipped(element):
        if element.tail:
            parts.append(element.tail)
        return
    block = _localname(element.tag) in _BLOCK_IN_CELL
    if block:
        parts.append(_BLOCK_BREAK)
    if element.text:
        parts.append(element.text)
    for child in list(element):
        _collect_cell(child, parts)
    if block:
        parts.append(_BLOCK_BREAK)
    if element.tail:
        parts.append(element.tail)


def _cell_text(cell: ET.Element) -> str:
    """A cell's text with its paragraphs and loose runs kept apart in
    document order, pipes escaped so the text cannot end the cell early."""
    parts: list[str] = [cell.text or ""]
    for child in list(cell):
        _collect_cell(child, parts)
    segments = (" ".join(segment.split()) for segment in "".join(parts).split(_BLOCK_BREAK))
    # Literal angle brackets and ampersands in the source would read as HTML
    # beside the <br> joins, so they are escaped.
    escaped = (
        segment.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for segment in segments
        if segment
    )
    return "<br>".join(escaped).replace("|", "\\|")


def _group_grid(
    rows: list[list[ET.Element]], heading_columns: list[set[int]] | None = None
) -> list[list[str]]:
    """The group's rows as text, spans resolved. When `heading_columns` is
    given, it gains one set per row: the columns where a `th` cell starts."""
    grid: list[list[str]] = []
    # (row, column) -> (text, id of the spanning cell)
    pending: dict[tuple[int, int], tuple[str, int]] = {}
    for row_index, cells in enumerate(rows):
        line: list[str] = []
        starts: set[int] = set()
        column = 0
        queue = list(cells)
        while queue or any(key[0] == row_index for key in pending):
            if (row_index, column) in pending:
                line.append(pending.pop((row_index, column))[0])
                column += 1
                continue
            if not queue:
                line.append("")
                column += 1
                continue
            cell = queue.pop(0)
            text = _cell_text(cell)
            remaining = len(rows) - row_index
            # A zero rowspan spans the rest of the row group (HTML Standard).
            rowspan = remaining if _is_zero(cell.get("rowspan")) else _span(cell, "rowspan")
            rowspan = min(rowspan, remaining, _MAX_TABLE_SPAN)
            colspan = _span(cell, "colspan")
            # A heading scoped to its row labels the row, not a column.
            if _localname(cell.tag) == "th" and (cell.get("scope") or "").lower() != "row":
                starts.add(column)
            for offset in range(colspan):
                # A cell that lands on a column a row span holds wins it and
                # ends that span, so overlapping spans in malformed markup can
                # neither stall the row nor reappear below it.
                displaced = pending.pop((row_index, column + offset), None)
                if displaced is not None:
                    for key in [k for k, v in pending.items() if v[1] == displaced[1]]:
                        del pending[key]
                value = text if offset == 0 else ""
                line.append(value)
                for extra in range(1, rowspan):
                    pending[(row_index + extra, column + offset)] = (value, id(cell))
            column += colspan
        grid.append(line)
        if heading_columns is not None:
            heading_columns.append(starts)
    return grid


def _table_markdown(table: ET.Element) -> str:
    """Render an XHTML table as a GFM table, or "" when it holds no text."""
    groups = _table_groups(table)
    heading_columns: list[set[int]] = []
    grid = [line for rows in groups for line in _group_grid(rows, heading_columns)]
    caption = next(
        (_inline_text(child) for child in table if _localname(child.tag) == "caption"),
        "",
    )
    if not any(text for line in grid for text in line):
        return f"**{caption}**" if caption else ""
    width = max(len(line) for line in grid)
    grid = [line + [""] * (width - len(line)) for line in grid]

    first_row = next((row for rows in groups for row in rows), [])
    has_thead = any(
        _localname(child.tag) == "thead"
        and any(_localname(row.tag) == "tr" for row in child)
        for child in table
    )
    first_all_th = bool(first_row) and all(_localname(cell.tag) == "th" for cell in first_row)
    if has_thead or first_all_th:
        header_rows = len(groups[0]) if has_thead else 1
        # Fold only under a single heading row: a second thead row names the
        # columns a statute may cite one by one.
        if header_rows == 1:
            grid = _merge_header_groups(grid, first_row, heading_columns[1:])
        width = len(grid[0])
        header, body = grid[0], grid[1:]
    else:
        header, body = [""] * width, grid

    def render(line: list[str]) -> str:
        return "| " + " | ".join(line) + " |"

    lines = [render(header), "| " + " | ".join(["---"] * width) + " |"]
    lines.extend(render(line) for line in body)
    table_text = "\n".join(lines)
    return f"**{caption}**\n\n{table_text}" if caption else table_text


def _merge_header_groups(
    grid: list[list[str]], header_cells: list[ET.Element], later_headings: list[set[int]]
) -> list[list[str]]:
    """Fold the physical columns under one spanning heading into one column.

    A statute that names "the first column" means the heading's column:
    ROA Exceptions Order art. 3 sets a Status heading over three cells
    (entry number, sub-paragraph letter, wording). Keeping them apart would
    push the second named column to the fourth place. Each row's texts under
    one heading are joined with a space.

    A group stays apart when heading cells in later rows start in two or
    more of its columns, in one row or across rows: those are sub-headings
    naming columns a statute may cite on their own. Heading cells that all
    start in one column are row labels, such as entry numbers, and do not
    split the group."""
    spans = [_span(cell, "colspan") for cell in header_cells]
    if all(span == 1 for span in spans) or sum(spans) != len(grid[0]):
        return grid
    ranges: list[range] = []
    start = 0
    for span in spans:
        ranges.append(range(start, start + span))
        start += span
    heading_starts = set().union(*later_headings) if later_headings else set()
    fold = [len(group) > 1 and len(heading_starts & set(group)) < 2 for group in ranges]
    merged: list[list[str]] = []
    for row_index, line in enumerate(grid):
        out: list[str] = []
        for group, folded in zip(ranges, fold):
            cells = line[group.start : group.stop]
            if not folded:
                out.extend(cells)
            elif row_index == 0:
                out.append(cells[0])
            else:
                out.append(" ".join(text for text in cells if text))
        merged.append(out)
    return merged


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
