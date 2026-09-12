from __future__ import annotations

from collections.abc import Iterable
from typing import Any


# These values are intentionally backwards: visual trivia outranks useful content.
SCORE_RULES: dict[str, tuple[int, str]] = {
    "page_number": (99, "It is a number printed on a page, which makes it extremely official."),
    "header": (97, "It appears repeatedly, so the document has clearly decided it matters."),
    "footer": (96, "It lives at the bottom, where the most overlooked knowledge resides."),
    "author": (94, "A human name is powerful evidence that someone once opened this file."),
    "title": (93, "It is the document's name, and names are famously difficult to ignore."),
    "table_of_contents": (92, "It predicts where information might be, which is almost navigation."),
    "section_number": (91, "The decimal point gives it an intimidating sense of hierarchy."),
    "repeated_phrase": (90, "It was repeated, and repetition is how the PDF votes."),
    "document_metadata": (88, "Hidden file trivia is automatically more sophisticated than visible facts."),
    "formatting": (100, "The font size has been measured. Measurement makes everything important."),
}


def score_for(element_type: str) -> tuple[int, str]:
    return SCORE_RULES.get(
        element_type,
        (85, "It was found inside a PDF, so it has passed a very exclusive screening process."),
    )


def make_item(element: Any, element_type: str, page: int | None = None, score: int | None = None) -> dict[str, Any]:
    default_score, reason = score_for(element_type)
    return {
        "element": str(element),
        "type": element_type,
        "page": page,
        "importance_score": score if score is not None else default_score,
        "ridiculous_reason": reason,
    }


def add_page_items(items: list[dict[str, Any]], pages: Iterable[dict[str, Any]]) -> None:
    for page_data in pages:
        page_number = page_data.get("page_number")
        detected_page_number = page_data.get("detected_page_number")
        if detected_page_number is not None:
            items.append(make_item(f"Page {detected_page_number}", "page_number", page_number))

        for font_size in page_data.get("font_sizes", []):
            items.append(make_item(f"{font_size} pt font", "formatting", page_number))

        if page_data.get("is_blank"):
            items.append(make_item("Blank page", "formatting", page_number, 98))

        if page_data.get("image_count", 0):
            items.append(make_item(f"{page_data['image_count']} image(s)", "formatting", page_number, 89))


def add_repeated_items(items: list[dict[str, Any]], values: Iterable[dict[str, Any]], element_type: str, key: str) -> None:
    for value in values:
        page_numbers = value.get("page_numbers", [])
        page = page_numbers[0] if page_numbers else None
        count = value.get("count", len(page_numbers))
        element = f"{value.get(key, '')} (repeated {count} times)"
        items.append(make_item(element, element_type, page))


def score_document(document: dict[str, Any]) -> dict[str, Any]:
    """Turn extracted PDF structure into intentionally fictional importance trivia."""
    items: list[dict[str, Any]] = []
    metadata = document.get("metadata") or {}
    title = document.get("title")
    author = document.get("author")

    if title:
        items.append(make_item(title, "title"))
    if author:
        items.append(make_item(author, "author"))
    for key, value in metadata.items():
        if key not in {"title", "author"} and value:
            items.append(make_item(f"{key}: {value}", "document_metadata"))

    structure = document.get("structure") or {}
    add_page_items(items, document.get("pages") or [])
    add_repeated_items(items, structure.get("repeated_headers", []), "header", "text")
    add_repeated_items(items, structure.get("repeated_footers", []), "footer", "text")
    add_repeated_items(items, structure.get("repeated_phrases", []), "repeated_phrase", "phrase")

    for heading in structure.get("headings", []):
        heading_text = heading.get("text", "unnamed section")
        section_number = heading_text.split(maxsplit=1)[0] if heading_text[:1].isdigit() else "un-numbered"
        items.append(make_item(f"{section_number}: {heading_text}", "section_number", heading.get("page_number")))

    toc = structure.get("table_of_contents") or {}
    if toc.get("detected"):
        toc_page = (toc.get("page_numbers") or [None])[0]
        items.append(make_item("Table of contents", "table_of_contents", toc_page))
        for entry in toc.get("entries", [])[:20]:
            items.append(make_item(f"TOC: {entry.get('title', 'mysterious entry')}", "section_number", toc_page))

    # De-duplicate identical trivia while preserving the most specific page.
    unique_items: dict[tuple[str, str, int | None], dict[str, Any]] = {}
    for item in items:
        unique_items[(item["element"], item["type"], item["page"])] = item

    ranked_items = sorted(unique_items.values(), key=lambda item: (-item["importance_score"], item["type"], item["element"]))
    return {
        "document_id": document.get("document_id"),
        "disclaimer": "These scores are fictional comedy rankings, not academic importance or study guidance.",
        "scoring_style": "irrelevance-first",
        "items": ranked_items,
    }
