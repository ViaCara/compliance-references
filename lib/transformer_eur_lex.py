"""EUR-Lex HTML → GFM markdown transformer (stdlib only).

EUR-Lex serves HTML5 (not XHTML), so `html.parser.HTMLParser` is the right
tool. The relevant DOM containers we look for:

- `<div class="eli-container">` or `<div class="eli-main-title">`, main body.
- `<p class="oj-doc-ti">`, article / regulation title (e.g. "Article 6").
- `<p class="oj-sti-art">`, article subtitle.
- `<p class="oj-normal">`, main paragraph text.

We treat any descendant of the eli container that's a `<p>` as a paragraph
and strip inline tags (`<em>`, `<strong>`, `<span>`) to plain text.
"""

from __future__ import annotations

from html.parser import HTMLParser


class EurLexTransformerError(ValueError):
    """Raised when EUR-Lex HTML can't be parsed."""


class _EurLexExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._inside_main = False
        self._main_depth = 0
        self._current_p_classes: list[str] = []
        self._current_p_buffer: list[str] = []
        self._found_main = False
        self.paragraphs: list[tuple[str, str]] = []  # (class, text)

    def handle_starttag(self, tag: str, attrs):
        attrs_dict = dict(attrs)
        classes = set((attrs_dict.get("class") or "").split())

        if tag == "div" and (
            classes & {"eli-container", "eli-main-title", "eli-subdivision"}
        ):
            self._inside_main = True
            self._found_main = True

        if self._inside_main and tag == "div":
            self._main_depth += 1

        if self._inside_main and tag == "p":
            self._current_p_classes = list(classes)
            self._current_p_buffer = []

    def handle_endtag(self, tag: str):
        if self._inside_main and tag == "p":
            text = "".join(self._current_p_buffer).strip()
            text = " ".join(text.split())
            if text:
                cls = next(
                    (c for c in self._current_p_classes if c.startswith("oj-")),
                    "",
                )
                self.paragraphs.append((cls, text))
            self._current_p_classes = []
            self._current_p_buffer = []

        if self._inside_main and tag == "div":
            self._main_depth -= 1
            if self._main_depth <= 0:
                self._inside_main = False
                self._main_depth = 0

    def handle_data(self, data: str):
        if self._inside_main and self._current_p_classes is not None:
            if self._current_p_classes:
                self._current_p_buffer.append(data)


class EurLexTransformer:
    """EUR-Lex HTML → GFM."""

    def transform(self, html: str, *, citation: str) -> str:
        extractor = _EurLexExtractor()
        extractor.feed(html)
        if not extractor._found_main:
            raise EurLexTransformerError("no <div class='eli-container'> found")

        lines: list[str] = [f"# {citation}", ""]

        # Subtitle (oj-sti-art) becomes italic block after the heading.
        subtitle = next(
            (text for cls, text in extractor.paragraphs if cls == "oj-sti-art"),
            None,
        )
        if subtitle:
            lines.append(f"_{subtitle}_")
            lines.append("")

        for cls, text in extractor.paragraphs:
            if cls == "oj-sti-art":
                continue
            if cls == "oj-doc-ti":
                # The "Article 6" line is captured by the citation; skip.
                continue
            lines.append(text)
            lines.append("")

        while lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines) + "\n"
