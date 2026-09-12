from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

import fitz


PAGE_NUMBER_PATTERNS = (
    re.compile(r"\bpage\s+(?:no\.?\s*)?(\d{1,4})\b", re.IGNORECASE),
    re.compile(r"\b(\d{1,4})\s+of\s+\d{1,4}\b", re.IGNORECASE),
)
WORD_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")


@dataclass
class PageSnapshot:
    number: int
    text: str
    lines: list[str]
    words: list[tuple[Any, ...]]
    width: float
    height: float
    image_count: int
    font_sizes: list[float]


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def word_count(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def extract_page_number(text: str, page_number: int) -> int | None:
    for pattern in PAGE_NUMBER_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))

    standalone_numbers = [int(match.group(1)) for match in re.finditer(r"(?m)^\s*(\d{1,4})\s*$", text)]
    if len(standalone_numbers) == 1:
        return standalone_numbers[0]
    return page_number if str(page_number) in text.split()[:2] else None


def likely_heading(line: str, font_size: float, median_font_size: float, is_bold: bool) -> bool:
    if not 3 <= len(line) <= 120 or line.endswith(('.', ',', ';', ':', '?', '!')):
        return False
    words = line.split()
    if len(words) > 16:
        return False
    uppercase_ratio = sum(character.isupper() for character in line if character.isalpha()) / max(
        1, sum(character.isalpha() for character in line)
    )
    title_case = sum(word[:1].isupper() for word in words if word) >= max(1, len(words) // 2)
    return is_bold or uppercase_ratio > 0.72 or (title_case and font_size >= median_font_size * 1.12)


def collect_page_snapshots(document: fitz.Document) -> list[PageSnapshot]:
    snapshots: list[PageSnapshot] = []
    for index, page in enumerate(document, start=1):
        text = page.get_text("text")
        lines = [normalize_line(line) for line in text.splitlines() if normalize_line(line)]
        words = page.get_text("words")
        page_dict = page.get_text("dict")
        font_sizes = [
            float(span["size"])
            for block in page_dict.get("blocks", [])
            if block.get("type") == 0
            for line in block.get("lines", [])
            for span in line.get("spans", [])
            if span.get("size")
        ]
        snapshots.append(
            PageSnapshot(
                number=index,
                text=text.strip(),
                lines=lines,
                words=words,
                width=round(page.rect.width, 2),
                height=round(page.rect.height, 2),
                image_count=len(page.get_images(full=True)),
                font_sizes=font_sizes,
            )
        )
    return snapshots


def repeated_lines(snapshots: list[PageSnapshot], location: str) -> list[dict[str, Any]]:
    occurrences: defaultdict[str, list[int]] = defaultdict(list)
    for snapshot in snapshots:
        candidates = snapshot.lines[:3] if location == "header" else snapshot.lines[-3:]
        for line in candidates:
            if 3 <= len(line) <= 120:
                occurrences[line].append(snapshot.number)

    minimum_pages = max(2, math.ceil(len(snapshots) * 0.4))
    return [
        {"text": text, "page_numbers": pages, "count": len(pages)}
        for text, pages in sorted(occurrences.items(), key=lambda item: (-len(item[1]), item[0]))
        if len(pages) >= minimum_pages
    ][:20]


def repeated_phrases(snapshots: list[PageSnapshot]) -> list[dict[str, Any]]:
    phrase_pages: defaultdict[str, set[int]] = defaultdict(set)
    for snapshot in snapshots:
        tokens = [token.lower() for token in WORD_PATTERN.findall(snapshot.text)]
        seen_on_page: set[str] = set()
        for size in range(3, 6):
            for start in range(max(0, len(tokens) - size + 1)):
                phrase = " ".join(tokens[start : start + size])
                if phrase not in seen_on_page and sum(token.isalpha() for token in tokens[start : start + size]) >= 2:
                    seen_on_page.add(phrase)
                    phrase_pages[phrase].add(snapshot.number)

    repeated = [
        {"phrase": phrase, "page_numbers": sorted(pages), "count": len(pages)}
        for phrase, pages in phrase_pages.items()
        if len(pages) >= 2 and len(phrase) >= 12
    ]
    return sorted(repeated, key=lambda item: (-item["count"], -len(item["phrase"])))[:30]


def detect_table_of_contents(snapshots: list[PageSnapshot]) -> dict[str, Any]:
    toc_pages: list[int] = []
    entries: list[dict[str, Any]] = []
    for snapshot in snapshots[: min(8, len(snapshots))]:
        lower_text = snapshot.text.lower()
        if "table of contents" in lower_text or re.search(r"^contents$", lower_text, re.MULTILINE | re.IGNORECASE):
            toc_pages.append(snapshot.number)
        for line in snapshot.lines:
            match = re.match(r"^(.{3,100}?)(?:\.{2,}|\s{2,})(\d{1,4})$", line)
            if match:
                entries.append({"title": match.group(1).strip(" ."), "page_number": int(match.group(2))})
    return {"detected": bool(toc_pages or entries), "page_numbers": toc_pages, "entries": entries[:50]}


def build_headings(document: fitz.Document, snapshots: list[PageSnapshot]) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for snapshot in snapshots:
        page = document[snapshot.number - 1]
        page_dict = page.get_text("dict")
        median_size = sorted(snapshot.font_sizes)[len(snapshot.font_sizes) // 2] if snapshot.font_sizes else 12.0
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                text = normalize_line("".join(span.get("text", "") for span in spans))
                size = max((float(span.get("size", 0)) for span in spans), default=0)
                bold = any("bold" in span.get("font", "").lower() for span in spans)
                if text and likely_heading(text, size, median_size, bold):
                    headings.append({"text": text, "page_number": snapshot.number, "font_size": round(size, 2)})
    unique: dict[tuple[int, str], dict[str, Any]] = {(item["page_number"], item["text"]): item for item in headings}
    return list(unique.values())[:100]


def process_pdf(content: bytes, filename: str, document_id: str) -> dict[str, Any]:
    with fitz.open(stream=content, filetype="pdf") as document:
        snapshots = collect_page_snapshots(document)
        all_text = "\n".join(snapshot.text for snapshot in snapshots)
        total_characters = len(re.sub(r"\s+", "", all_text))
        scanned = total_characters < max(100, len(snapshots) * 30)
        metadata = {key: value for key, value in (document.metadata or {}).items() if value}
        page_records = []
        for snapshot in snapshots:
            page_records.append(
                {
                    "page_number": snapshot.number,
                    "text": snapshot.text,
                    "word_count": word_count(snapshot.text),
                    "detected_page_number": extract_page_number(snapshot.text, snapshot.number),
                    "width_points": snapshot.width,
                    "height_points": snapshot.height,
                    "image_count": snapshot.image_count,
                    "font_sizes": sorted({round(size, 2) for size in snapshot.font_sizes}),
                    "is_blank": not bool(snapshot.text),
                }
            )

        return {
            "document_id": document_id,
            "filename": filename,
            "page_count": len(snapshots),
            "title": metadata.get("title") or filename.rsplit(".", 1)[0],
            "author": metadata.get("author"),
            "metadata": metadata,
            "pages": page_records,
            "structure": {
                "detected_page_numbers": [
                    page["page_number"] for page in page_records if page["detected_page_number"] is not None
                ],
                "repeated_headers": repeated_lines(snapshots, "header"),
                "repeated_footers": repeated_lines(snapshots, "footer"),
                "repeated_phrases": repeated_phrases(snapshots),
                "headings": build_headings(document, snapshots),
                "table_of_contents": detect_table_of_contents(snapshots),
                "blank_page_numbers": [page["page_number"] for page in page_records if page["is_blank"]],
                "total_word_count": sum(page["word_count"] for page in page_records),
                "total_image_count": sum(page["image_count"] for page in page_records),
            },
            "ocr": {
                "recommended": scanned,
                "status": "not_configured" if scanned else "not_needed",
                "reason": "Very little extractable text was found; Tesseract OCR can be added here later." if scanned else None,
            },
        }
