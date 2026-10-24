from __future__ import annotations
import re
from pathlib import Path
from .models import Clause

def extract_pdf(data: bytes) -> tuple[str, list[tuple[int, str]]]:
    # Keep text-only analysis testable and usable even if the optional PDF wheel
    # was not installed correctly on a target platform.
    import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    pages = [(i + 1, page.get_text("text")) for i, page in enumerate(doc)]
    return "\n".join(t for _, t in pages), pages

def extract_document(filename: str, data: bytes) -> tuple[str, list[tuple[int, str]]]:
    if Path(filename).suffix.lower() == ".pdf":
        return extract_pdf(data)
    text = data.decode("utf-8", errors="replace")
    return text, [(1, text)]

HEADING = re.compile(r"(?m)^\s*((?:section|rule|clause|para(?:graph)?|article)\s+[\dA-Za-z][\dA-Za-z.()/-]*|\d+(?:\.\d+){0,3}[.)]?)\s+(.+)$", re.I)

def parse_clauses(pages: list[tuple[int, str]]) -> list[Clause]:
    """Retain stable legal identifiers where text has recognisable headings."""
    clauses: list[Clause] = []
    for page, text in pages:
        matches = list(HEADING.finditer(text))
        if not matches:
            cleaned = " ".join(text.split())
            if cleaned:
                clauses.append(Clause(identifier=f"Page {page}", text=cleaned, page=page))
            continue
        prefix = " ".join(text[:matches[0].start()].split())
        if prefix:
            clauses.append(Clause(identifier=f"Page {page} preamble", text=prefix, page=page))
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = " ".join(text[match.start():end].split())
            identifier = " ".join(match.group(1).split())
            clauses.append(Clause(identifier=identifier, text=content, page=page))
    return clauses
